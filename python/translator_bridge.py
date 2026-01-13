#!/usr/bin/env python3
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

# Add parent directory to path to import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from srt_utils import parse_srt
    from translator import translate_blocks, MODEL_PRICES
except ImportError:
    # Fallback for packaged app
    pass

def send_progress(current, total, message=""):
    """Send progress update to Electron"""
    progress_data = {
        "current": current,
        "total": total,
        "percentage": (current / total * 100) if total > 0 else 0,
        "message": message
    }
    print(f"PROGRESS:{json.dumps(progress_data)}", flush=True)

def send_status(status):
    """Send status message to Electron"""
    print(f"STATUS:{status}", flush=True)

def analyze_files(source_folder, model):
    """Analyze SRT files and return cost estimate"""
    try:
        # Find all SRT files
        srt_files = []
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                if file.lower().endswith('.srt'):
                    srt_files.append(os.path.join(root, file))
        
        if not srt_files:
            return {
                "success": False,
                "error": "No SRT files found in the source folder"
            }
        
        # Calculate tokens
        try:
            enc = tiktoken.encoding_for_model(model)
        except Exception:
            enc = tiktoken.get_encoding("cl100k_base")
        
        total_input_toks = 0
        total_output_toks = 0
        sys_prompt_toks = len(enc.encode("You are a professional subtitle translator."))
        
        for srt_path in srt_files:
            try:
                with open(srt_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                lines = [
                    ln.strip()
                    for ln in content.splitlines()
                    if ln.strip()
                    and not ln.strip().isdigit()
                    and "-->" not in ln
                ]
                
                input_text = "\n".join(lines)
                input_toks = len(enc.encode(input_text))
                output_toks = int(input_toks * 1.2)
                
                total_input_toks += input_toks + sys_prompt_toks
                total_output_toks += output_toks
            except Exception as e:
                print(f"Error processing {srt_path}: {e}", file=sys.stderr)
                continue
        
        # Add safety buffer
        total_input_toks = int(total_input_toks * 1.15)
        total_output_toks = int(total_output_toks * 1.15)
        total_tokens = total_input_toks + total_output_toks
        
        # Calculate cost
        if model in MODEL_PRICES:
            m = MODEL_PRICES[model]
            usd = (total_input_toks * m["input"]) + (total_output_toks * m["output"])
            inr = usd * 83.0
            confidence = m.get("confidence", "unknown")
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

def translate_files(source_folder, output_folder, languages, model, api_key):
    """Translate SRT files to target languages"""
    try:
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
            return {"success": False, "error": "No SRT files found"}
        
        send_status(f"📝 Found {len(srt_files)} file(s)")
        
        total_tasks = len(srt_files) * len(languages)
        current_task = 0
        
        # Create output directory
        os.makedirs(output_folder, exist_ok=True)
        
        for lang in languages:
            send_status(f"🌍 Translating to {lang}...")
            
            lang_folder = os.path.join(output_folder, lang)
            os.makedirs(lang_folder, exist_ok=True)
            
            for srt_path in srt_files:
                filename = os.path.basename(srt_path)
                
                send_progress(current_task, total_tasks, f"Translating {filename} to {lang}")
                
                try:
                    # Read and parse SRT
                    with open(srt_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    blocks = parse_srt(content)
                    
                    # Translate
                    translated_blocks, elapsed = translate_blocks(blocks, lang, model)
                    
                    # Save translated file
                    new_name = filename.replace("_EN", f"_{lang.upper()}")
                    if not new_name.endswith(f"_{lang.upper()}.srt"):
                        new_name = filename.replace(".srt", f"_{lang.upper()}.srt")
                    
                    out_path = os.path.join(lang_folder, new_name)
                    
                    # Rebuild SRT
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
                    
                    send_status(f"✅ {filename} → {new_name} ({elapsed:.1f}s)")
                    
                except Exception as e:
                    send_status(f"❌ Failed: {filename} - {str(e)}")
                    print(f"Error translating {filename}: {e}", file=sys.stderr)
                
                current_task += 1
                send_progress(current_task, total_tasks, f"Completed {filename}")
            
            send_status(f"🎯 Completed: {lang}")
        
        send_status("🎉 All translations completed!")
        return {"success": True}
        
    except Exception as e:
        send_status(f"❌ Error: {str(e)}")
        print(f"Translation error: {e}", file=sys.stderr)
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
            args.api_key
        )
        if not result.get('success'):
            sys.exit(1)
    
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()