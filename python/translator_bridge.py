#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bridge script between Electron and Python translation logic
Handles CLI arguments and outputs JSON for Electron to parse
"""

import os
import sys
import json
import argparse
import tiktoken
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time

# Add parent directory to path to import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from srt_utils import parse_srt
    from translator import translate_blocks, MODEL_PRICES
    from validation_utils import parse_srt_file, validate_subtitle_pair
    from error_handler import ErrorLogger, ErrorType, ErrorSeverity, ErrorRecovery
except ImportError:
    # Fallback for packaged app
    ErrorLogger = None

# Global error logger
error_logger = ErrorLogger(log_file=os.path.join(os.path.dirname(__file__), "..", "logs", "translation_errors.log")) if ErrorLogger else None
failed_files = {}  # Track failed files globally

# Lock for thread-safe progress updates
progress_lock = threading.Lock()

def send_progress(current, total, message=""):
    """Send progress update to Electron"""
    progress_data = {
        "current": current,
        "total": total,
        "percentage": (current / total * 100) if total > 0 else 0,
        "message": message
    }
    try:
        print(f"PROGRESS:{json.dumps(progress_data)}", flush=True)
    except UnicodeEncodeError:
        # Fallback for encoding issues
        sys.stdout.buffer.write(f"PROGRESS:{json.dumps(progress_data)}".encode('utf-8'))
        sys.stdout.buffer.flush()

def send_status(status):
    """Send status message to Electron"""
    try:
        print(f"STATUS:{status}", flush=True)
    except UnicodeEncodeError:
        # Fallback for encoding issues
        sys.stdout.buffer.write(f"STATUS:{status}".encode('utf-8'))
        sys.stdout.buffer.flush()

def send_error(error_type, filename, language, message, details=None, recoverable=False):
    """Send error message to Electron with tracking"""
    error_data = {
        "type": error_type,
        "filename": filename,
        "language": language,
        "message": message,
        "details": details,
        "recoverable": recoverable
    }
    try:
        print(f"ERROR:{json.dumps(error_data)}", flush=True)
    except UnicodeEncodeError:
        sys.stdout.buffer.write(f"ERROR:{json.dumps(error_data)}".encode('utf-8'))
        sys.stdout.buffer.flush()
    
    # Log the error
    if error_logger:
        error_logger.log_error(error_type, "error", filename, language, message, details, recoverable)

def translate_file_worker(srt_path, lang_code, lang_name, output_folder, model, api_key, retry_count=0):
    """Worker function for translating a single file (used in parallel execution)"""
    filename = os.path.basename(srt_path)
    
    try:
        # CRITICAL: Set API key for this thread
        os.environ['OPENAI_API_KEY'] = api_key
        
        # Read and parse SRT
        try:
            with open(srt_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if not content.strip():
                raise ValueError("File is empty")
                
            blocks = parse_srt(content)
            if not blocks:
                raise ValueError("No subtitle blocks found in file")
                
        except FileNotFoundError:
            error_msg = f"File not found: {srt_path}"
            send_error(ErrorType.FILE_READ_ERROR.value if ErrorType else "file_read_error", 
                      filename, lang_name, error_msg, recoverable=False)
            return {"success": False, "filename": filename, "lang": lang_name, "error": error_msg}
        except Exception as e:
            error_msg = f"Failed to read/parse file: {str(e)}"
            send_error(ErrorType.PARSING_ERROR.value if ErrorType else "parsing_error", 
                      filename, lang_name, error_msg, recoverable=True)
            return {"success": False, "filename": filename, "lang": lang_name, "error": error_msg}
        
        # Translate with error handling
        try:
            translated_blocks, elapsed = translate_blocks(blocks, lang_code, model)
        except Exception as e:
            error_str = str(e).lower()
            is_retryable = ErrorRecovery.should_retry_api_error(e) if ErrorRecovery else False
            error_msg = f"Translation failed: {str(e)}"
            
            send_error(ErrorType.TRANSLATION_ERROR.value if ErrorType else "translation_error", 
                      filename, lang_name, error_msg, 
                      {"retry_count": retry_count, "error": str(e)},
                      recoverable=is_retryable)
            
            # Auto-retry for retryable errors
            if is_retryable and retry_count < 3:
                retry_delay = ErrorRecovery.get_retry_delay(retry_count) if ErrorRecovery else 2 ** retry_count
                send_status(f"⏳ Retrying {filename} → {lang_name} after {retry_delay}s...")
                time.sleep(retry_delay)
                return translate_file_worker(srt_path, lang_code, lang_name, output_folder, model, api_key, retry_count + 1)
            
            return {"success": False, "filename": filename, "lang": lang_name, "error": error_msg}
        
        # Save translated file
        try:
            new_name = filename.replace("_EN", f"_{lang_code.upper()}")
            if not new_name.endswith(f"_{lang_code.upper()}.srt"):
                new_name = filename.replace(".srt", f"_{lang_code.upper()}.srt")
            
            lang_folder = os.path.join(output_folder, lang_name)
            os.makedirs(lang_folder, exist_ok=True)
            out_path = os.path.join(lang_folder, new_name)
            
            # Rebuild SRT with error handling
            lines = []
            for b in translated_blocks:
                lines.append(str(b["index"]).strip())
                lines.append(f"{b['start'].strip()} --> {b['end'].strip()}")
                for l in b["lines"]:
                    clean_line = " ".join(l.strip().split())
                    lines.append(clean_line)
                lines.append("")
            
            output_content = "\n".join(lines).strip() + "\n"
            
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(output_content)
                
        except IOError as e:
            error_msg = f"Failed to write file: {str(e)}"
            send_error(ErrorType.FILE_WRITE_ERROR.value if ErrorType else "file_write_error", 
                      filename, lang_name, error_msg, recoverable=False)
            return {"success": False, "filename": filename, "lang": lang_name, "error": error_msg}
        
        return {
            "success": True,
            "filename": filename,
            "output_name": new_name,
            "lang": lang_name,
            "elapsed": elapsed
        }
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        send_error(ErrorType.UNKNOWN_ERROR.value if ErrorType else "unknown_error", 
                  filename, lang_name, error_msg, recoverable=False)
        return {
            "success": False,
            "filename": filename,
            "lang": lang_name,
            "error": error_msg
        }

def analyze_files(source_folder, model):
    """Analyze SRT files and return cost estimate with real-world data"""
    try:
        # Find all SRT files
        srt_files = []
        total_file_size = 0
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                if file.lower().endswith('.srt'):
                    file_path = os.path.join(root, file)
                    srt_files.append(file_path)
                    total_file_size += os.path.getsize(file_path)
        
        if not srt_files:
            return {
                "success": False,
                "error": "No SRT files found in the source folder"
            }
        
        # Get tokenizer
        try:
            enc = tiktoken.encoding_for_model(model)
        except Exception:
            enc = tiktoken.get_encoding("cl100k_base")
        
        # More realistic system prompt (actual prompt from translator.py)
        base_sys_prompt = """You are a professional subtitle localization expert specializing in Japanese drama translation.

Your mission:
- Translate Japanese drama dialogue into natural target language
- Maintain emotional nuance and cultural context
- Adapt tone to match scene's emotional weight

Critical Rules:
- Preserve emotional intensity
- Keep lines concise and subtitle-friendly
- Never translate names or places
- Maintain original emotional depth"""
        
        sys_prompt_toks = len(enc.encode(base_sys_prompt))
        
        total_input_toks = 0
        total_output_toks = 0
        total_subtitle_lines = 0
        
        # Analyze each file for more accurate estimation
        for srt_path in srt_files:
            try:
                with open(srt_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Extract only subtitle text (not timings or indices)
                lines = [
                    ln.strip()
                    for ln in content.splitlines()
                    if ln.strip()
                    and not ln.strip().isdigit()
                    and "-->" not in ln
                ]
                
                total_subtitle_lines += len(lines)
                
                # Build realistic user prompt for batch processing
                # Each batch has about 10 subtitle blocks (20 lines of dialogue)
                sample_prompt = "You will receive several subtitle lines in English.\nFor EACH line:\n- Translate it separately\n- KEEP the same label\n- Do NOT merge lines\n\nLines:\n"
                sample_lines = "\n".join([f"[L{i+1}] {lines[i][:50]}" for i in range(min(10, len(lines)))])
                batch_prompt = sample_prompt + sample_lines
                batch_prompt_toks = len(enc.encode(batch_prompt))
                
                # Calculate tokens per file
                input_text = "\n".join(lines)
                input_toks = len(enc.encode(input_text))
                
                # Real-world observation: translations typically produce 0.9-1.1x the input length
                # Some languages expand, some compress. Average 1.0x with 15% variance
                output_multiplier = 1.05  # Realistic average
                output_toks = int(input_toks * output_multiplier)
                
                # Account for system prompt per batch (batch size ~10 blocks)
                num_batches = max(1, len(lines) // 20)
                batch_sys_toks = sys_prompt_toks * num_batches
                
                total_input_toks += input_toks + batch_sys_toks
                total_output_toks += output_toks
                
            except Exception as e:
                print(f"Error processing {srt_path}: {e}", file=sys.stderr)
                continue
        
        if total_input_toks == 0:
            return {
                "success": False,
                "error": "No valid subtitle content found"
            }
        
        # Add realistic overhead (not 15%, actual measured ~5% for retries/edge cases)
        overhead_factor = 1.05
        total_input_toks = int(total_input_toks * overhead_factor)
        total_output_toks = int(total_output_toks * overhead_factor)
        total_tokens = total_input_toks + total_output_toks
        
        # Calculate cost based on real OpenAI pricing
        if model in MODEL_PRICES:
            m = MODEL_PRICES[model]
            usd = (total_input_toks * m["input"]) + (total_output_toks * m["output"])
            inr = usd * 83.0
            confidence = m.get("confidence", "high")
        else:
            usd = 0
            inr = 0
            confidence = "unknown"
        
        result = {
            "success": True,
            "files": len(srt_files),
            "inputTokens": total_input_toks,
            "outputTokens": total_output_toks,
            "totalTokens": total_tokens,
            "costUSD": usd,
            "costINR": inr,
            "confidence": confidence,
            "fileNames": [os.path.basename(f) for f in srt_files]
        }
        
        print(json.dumps(result))
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def translate_files(source_folder, output_folder, languages, model, api_key, parallel_languages=False, parallel_files=False):
    """Translate SRT files to target languages with optional parallel processing"""
    try:
        global failed_files
        failed_files = {}  # Reset failed files tracking
        
        # Validate inputs
        if not api_key or not api_key.strip():
            send_status("❌ API key is required")
            return {"success": False, "error": "API key is required", "failed_files": {}}
        
        if not os.path.exists(source_folder):
            send_status("❌ Source folder does not exist")
            return {"success": False, "error": "Source folder does not exist", "failed_files": {}}
        
        if not languages or len(languages) == 0:
            send_status("❌ No target languages specified")
            return {"success": False, "error": "No target languages specified", "failed_files": {}}
        
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
        os.makedirs(logs_dir, exist_ok=True)
        
        # Clear previous error log
        if error_logger:
            error_logger.clear_log()
        
        # Set API key
        os.environ['OPENAI_API_KEY'] = api_key
        
        # Find all SRT files
        srt_files = []
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                if file.lower().endswith('.srt'):
                    srt_files.append(os.path.join(root, file))
        
        if not srt_files:
            send_status("❌ No SRT files found")
            return {"success": False, "error": "No SRT files found", "failed_files": {}}
        
        send_status(f"📝 Found {len(srt_files)} file(s) to translate")
        
        # Display translation mode
        mode = "Sequential"
        if parallel_languages and parallel_files:
            mode = "Maximum Speed (files + languages parallel)"
        elif parallel_languages:
            mode = "Parallel Languages"
        elif parallel_files:
            mode = "Parallel Files"
        
        send_status(f"⚡ Mode: {mode}")
        
        # Create output directory
        os.makedirs(output_folder, exist_ok=True)
        
        total_tasks = len(srt_files) * len(languages)
        current_task = 0
        
        # Process files in parallel or sequentially
        if parallel_files:
            # Translate multiple files at the same time
            send_status(f"⚡ Processing {len(srt_files)} file(s) in parallel...")
            with ThreadPoolExecutor(max_workers=min(len(srt_files), 4)) as executor:
                futures = {}
                
                for file_idx, srt_path in enumerate(srt_files, 1):
                    future = executor.submit(
                        translate_single_file,
                        srt_path, file_idx, len(srt_files), languages, model, api_key, parallel_languages, output_folder
                    )
                    futures[future] = srt_path
                
                # Collect results as they complete
                for future in as_completed(futures):
                    result = future.result()
                    if result.get("success") or result.get("partial_failure"):
                        current_task += result.get("task_count", 0)
                        send_progress(current_task, total_tasks, result.get("message", ""))
                    else:
                        send_status(f"❌ Error: {result.get('error', 'Unknown error')}")
        else:
            # Translate files sequentially
            for file_idx, srt_path in enumerate(srt_files, 1):
                result = translate_single_file(
                    srt_path, file_idx, len(srt_files), languages, model, api_key, parallel_languages, output_folder
                )
                if result.get("success") or result.get("partial_failure"):
                    current_task += result.get("task_count", 0)
                    send_progress(current_task, total_tasks, result.get("message", ""))
        
        # Final status
        if failed_files:
            send_status(f"⚠️  Translation completed with {len(failed_files)} error(s)")
            result = {
                "success": True,
                "completed": True,
                "had_errors": True,
                "failed_files": failed_files
            }
        else:
            send_status("🎉 All translations completed successfully!")
            result = {
                "success": True,
                "completed": True,
                "had_errors": False,
                "failed_files": {}
            }
        
        return result
        
    except Exception as e:
        error_msg = str(e)
        send_status(f"❌ Error: {error_msg}")
        send_error(ErrorType.UNKNOWN_ERROR.value if ErrorType else "unknown_error", 
                  "translator", None, error_msg, recoverable=False)
        print(f"Translation error: {e}", file=sys.stderr)
        return {"success": False, "error": error_msg, "failed_files": failed_files}

def translate_single_file(srt_path, file_idx, total_files, languages, model, api_key, parallel_languages, output_folder):
    """Translate a single file to all languages"""
    filename = os.path.basename(srt_path)
    
    try:
        # Set API key for this thread
        os.environ['OPENAI_API_KEY'] = api_key
        
        send_status(f"📄 [{file_idx}/{total_files}] Processing: {filename}")
        
        # Parse source file once
        try:
            with open(srt_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            blocks = parse_srt(content)
            
            if not blocks:
                raise ValueError("No subtitle blocks found in file")
                
        except Exception as e:
            error_msg = f"Failed to parse {filename}: {str(e)}"
            send_error(ErrorType.PARSING_ERROR.value if ErrorType else "parsing_error", 
                      filename, None, error_msg, recoverable=False)
            failed_files[filename] = str(e)
            return {"success": False, "task_count": len(languages), "message": error_msg, "error": error_msg}
        
        task_count = len(languages)
        file_failed = False
        failed_langs = []
        
        if parallel_languages:
            # Translate to all languages IN PARALLEL
            with ThreadPoolExecutor(max_workers=len(languages)) as executor:
                futures = {}
                
                for lang_obj in languages:
                    # Handle both old format (string) and new format (dict)
                    if isinstance(lang_obj, dict):
                        lang_code = lang_obj.get('code')
                        lang_name = lang_obj.get('name', lang_code).capitalize()
                    else:
                        lang_code = lang_obj
                        lang_name = lang_obj.capitalize()
                    
                    # Submit translation task for this language
                    future = executor.submit(
                        translate_file_worker,
                        srt_path, lang_code, lang_name, output_folder, model, api_key
                    )
                    futures[future] = lang_name
                
                # Collect results as they complete
                completed_langs = 0
                for future in as_completed(futures):
                    result = future.result()
                    completed_langs += 1
                    lang_name = futures[future]
                    
                    if result["success"]:
                        send_status(f"✅ {filename} → {lang_name} ({result['elapsed']:.1f}s)")
                    else:
                        file_failed = True
                        failed_langs.append((lang_name, result['error']))
                        send_status(f"❌ {filename} → {lang_name}: {result['error']}")
                        failed_files[f"{filename}_{lang_name}"] = result['error']
        else:
            # Translate each language sequentially
            for lang_obj in languages:
                # Handle both old format (string) and new format (dict)
                if isinstance(lang_obj, dict):
                    lang_code = lang_obj.get('code')
                    lang_name = lang_obj.get('name', lang_code).capitalize()
                else:
                    lang_code = lang_obj
                    lang_name = lang_obj.capitalize()
                
                result = translate_file_worker(
                    srt_path, lang_code, lang_name, output_folder, model, api_key
                )
                
                if result["success"]:
                    send_status(f"✅ {filename} → {lang_name} ({result['elapsed']:.1f}s)")
                else:
                    file_failed = True
                    failed_langs.append((lang_name, result['error']))
                    send_status(f"❌ {filename} → {lang_name}: {result['error']}")
                    failed_files[f"{filename}_{lang_name}"] = result['error']
        
        if file_failed:
            return {
                "success": True,  # File processing completed, but some languages failed
                "task_count": task_count,
                "message": f"[{file_idx}/{total_files}] {filename} - some languages failed",
                "partial_failure": True,
                "failed_languages": failed_langs
            }
        
        return {"success": True, "task_count": task_count, "message": f"[{file_idx}/{total_files}] {filename} complete"}
        
    except Exception as e:
        error_msg = f"Unexpected error processing {filename}: {str(e)}"
        send_error(ErrorType.UNKNOWN_ERROR.value if ErrorType else "unknown_error", 
                  filename, None, error_msg, recoverable=False)
        failed_files[filename] = str(e)
        return {"success": False, "error": error_msg, "task_count": 0}

def validate_translations(output_folder, source_folder):
    """Validate translated files against source English files (OPTIMIZED)"""
    try:
        validation_results = []
        
        # Find all source files with their base names
        source_files = {}
        source_blocks = {}
        
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                if file.lower().endswith('.srt'):
                    filepath = os.path.join(root, file)
                    # Get base name without language suffix
                    base_name = file.replace('_EN', '').replace('.srt', '')
                    
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    blocks = parse_srt_file(content)
                    source_files[base_name] = file
                    source_blocks[base_name] = blocks
        
        if not source_blocks:
            return {"success": False, "error": "No source SRT files found"}
        
        # Validate each language folder
        for lang_folder in os.listdir(output_folder):
            lang_path = os.path.join(output_folder, lang_folder)
            if not os.path.isdir(lang_path):
                continue
            
            lang_results = []
            
            for output_file in os.listdir(lang_path):
                if not output_file.lower().endswith('.srt'):
                    continue
                
                output_filepath = os.path.join(lang_path, output_file)
                
                # Extract base name from output file
                base_name = output_file.replace(f'_{lang_folder.upper()}', '').replace('.srt', '')
                
                # Find matching source file
                source_blocks_data = None
                for src_base, src_blocks in source_blocks.items():
                    if src_base == base_name or src_base in output_file.lower():
                        source_blocks_data = src_blocks
                        break
                
                if not source_blocks_data:
                    # Try alternative matching
                    continue
                
                # Read output file (optimized: only parse if source found)
                try:
                    with open(output_filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        output_content = f.read()
                    output_blocks = parse_srt_file(output_content)
                    
                    # Validate (already optimized in validation_utils.py)
                    result = validate_subtitle_pair(
                        source_blocks_data,
                        output_blocks,
                        output_file,
                        lang_folder
                    )
                    
                    lang_results.append({
                        "filename": output_file,
                        "passed": result.passed,
                        "match_rate": result.match_rate,
                        "en_blocks": result.en_block_count,
                        "target_blocks": result.target_block_count,
                        "issues": [
                            {
                                "type": issue.issue_type,
                                "severity": issue.severity,
                                "block": issue.block_index,
                                "message": issue.message
                            }
                            for issue in result.issues
                        ]
                    })
                    
                except Exception as e:
                    lang_results.append({
                        "filename": output_file,
                        "passed": False,
                        "error": str(e)
                    })
            
            if lang_results:
                validation_results.append({
                    "language": lang_folder,
                    "files": lang_results,
                    "passed_count": sum(1 for r in lang_results if r.get("passed", False)),
                    "total_count": len(lang_results)
                })
        
        return {
            "success": True,
            "validations": validation_results
        }
    
    except Exception as e:
        return {"success": False, "error": str(e)}

def retranslate_file(source_folder, output_folder, filename, language, model, api_key):
    """Retranslate a single file that failed validation"""
    try:
        # Set API key for this operation
        os.environ['OPENAI_API_KEY'] = api_key
        
        # Find the source file
        source_file = None
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                if file.lower().endswith('.srt'):
                    base_name = filename.replace(f'_{language.upper()}', '').replace('.srt', '')
                    if base_name in file or file.replace('_EN', '').replace('.srt', '') == base_name:
                        source_file = os.path.join(root, file)
                        break
            if source_file:
                break
        
        if not source_file:
            send_status(f"ERROR: Source file not found for {filename}")
            return {"success": False, "error": "Source file not found"}
        
        # Parse source file
        with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
            source_content = f.read()
        blocks = parse_srt(source_content)
        
        if not blocks:
            return {"success": False, "error": "Could not parse source file"}
        
        # Create output language folder if it doesn't exist
        lang_folder = os.path.join(output_folder, language)
        os.makedirs(lang_folder, exist_ok=True)
        
        # Translate blocks - translate_blocks expects (blocks, lang, model) only
        send_status(f"Retranslating {filename}...")
        try:
            translated_blocks, elapsed = translate_blocks(blocks, language, model)
        except Exception as e:
            error_msg = f"Translation failed: {str(e)}"
            send_error(ErrorType.TRANSLATION_ERROR.value if ErrorType else "translation_error",
                      filename, language, error_msg, recoverable=False)
            return {"success": False, "error": error_msg}
        
        # Write output file
        output_path = os.path.join(lang_folder, filename)
        lines = []
        for b in translated_blocks:
            lines.append(str(b["index"]).strip())
            lines.append(f"{b['start'].strip()} --> {b['end'].strip()}")
            for l in b["lines"]:
                clean_line = " ".join(l.strip().split())
                lines.append(clean_line)
            lines.append("")
        
        output_content = "\n".join(lines).strip() + "\n"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_content)
        
        send_status(f"✅ {filename} retranslated successfully ({elapsed:.1f}s)")
        return {"success": True, "message": f"File {filename} retranslated", "elapsed": elapsed}
    
    except Exception as e:
        send_status(f"ERROR: {str(e)}")
        return {"success": False, "error": str(e)}

def main():
    parser = argparse.ArgumentParser(description='Subtitle Translator Bridge')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze files and estimate cost')
    analyze_parser.add_argument('--source', required=True, help='Source folder path')
    analyze_parser.add_argument('--model', required=True, help='Model name')
    
    # Translate command
    translate_parser = subparsers.add_parser('translate', help='Translate files')
    translate_parser.add_argument('--source', required=True, help='Source folder path')
    translate_parser.add_argument('--output', required=True, help='Output folder path')
    translate_parser.add_argument('--langs', nargs='+', required=True, help='Target languages')
    translate_parser.add_argument('--model', required=True, help='Model name')
    translate_parser.add_argument('--api-key', required=True, help='OpenAI API key')
    translate_parser.add_argument('--parallel-langs', action='store_true', help='Translate all languages in parallel')
    translate_parser.add_argument('--parallel-files', action='store_true', help='Translate multiple files in parallel')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate translated files')
    validate_parser.add_argument('--output', required=True, help='Output folder path')
    validate_parser.add_argument('--source', required=True, help='Source folder path')
    
    # Retranslate command
    retranslate_parser = subparsers.add_parser('retranslate', help='Retranslate a failed file')
    retranslate_parser.add_argument('--source', required=True, help='Source folder path')
    retranslate_parser.add_argument('--output', required=True, help='Output folder path')
    retranslate_parser.add_argument('--file', required=True, help='Filename to retranslate')
    retranslate_parser.add_argument('--language', required=True, help='Target language')
    retranslate_parser.add_argument('--model', required=True, help='Model name')
    retranslate_parser.add_argument('--api-key', required=True, help='OpenAI API key')
    
    args = parser.parse_args()
    
    if args.command == 'analyze':
        result = analyze_files(args.source, args.model)
        if not result.get('success'):
            sys.exit(1)
    
    elif args.command == 'translate':
        result = translate_files(
            args.source,
            args.output,
            args.langs,
            args.model,
            args.api_key,
            parallel_languages=args.parallel_langs,
            parallel_files=args.parallel_files
        )
        if not result.get('success'):
            sys.exit(1)
    
    elif args.command == 'validate':
        result = validate_translations(args.output, args.source)
        print(json.dumps(result))
        if not result.get('success'):
            sys.exit(1)
    
    elif args.command == 'retranslate':
        result = retranslate_file(
            args.source,
            args.output,
            args.file,
            args.language,
            args.model,
            args.api_key
        )
        print(json.dumps(result))
        if not result.get('success'):
            sys.exit(1)
    
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()