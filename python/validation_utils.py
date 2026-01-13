#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SRT Subtitle Validator - Lightweight version for translator app
Checks for common issues in translated subtitle files
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

TIMESTAMP_RE = re.compile(
    r"^(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})$"
)

@dataclass
class SubtitleBlock:
    index: Optional[int]
    start_time: str
    end_time: str
    text_lines: List[str]
    line_number: int

    @property
    def has_text(self) -> bool:
        for line in self.text_lines:
            if line.strip():
                return True
        return False

    @property
    def text_preview(self) -> str:
        if self.text_lines:
            return self.text_lines[0].strip()[:80]
        return ""

@dataclass
class ValidationIssue:
    issue_type: str
    severity: str  # "error", "warning"
    block_index: Optional[int]
    message: str
    details: Optional[Dict] = None

@dataclass
class ValidationResult:
    filename: str
    target_language: str
    passed: bool
    issues: List[ValidationIssue]
    en_block_count: int
    target_block_count: int
    match_rate: float

def parse_timestamp_line(line: str) -> Optional[Tuple[str, str]]:
    """Parse timestamp line and return (start_time, end_time)"""
    m = TIMESTAMP_RE.match(line.strip())
    if not m:
        return None
    start = f"{m.group(1)}:{m.group(2)}:{m.group(3)},{m.group(4)}"
    end = f"{m.group(5)}:{m.group(6)}:{m.group(7)},{m.group(8)}"
    return start, end

def parse_srt_file(text: str) -> List[SubtitleBlock]:
    """Parse SRT file content into subtitle blocks"""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")
    blocks = []
    i = 0
    
    while i < len(lines):
        # Skip empty lines
        while i < len(lines) and not lines[i].strip():
            i += 1
        if i >= len(lines):
            break

        line_number = i + 1
        index = None
        current = lines[i].strip()

        # Try to parse index
        if current.isdigit():
            try:
                index = int(current)
                i += 1
                if i >= len(lines):
                    break
                current = lines[i].strip()
            except ValueError:
                pass

        # Parse timestamp
        ts = parse_timestamp_line(current)
        if not ts:
            i += 1
            continue

        start_time, end_time = ts
        i += 1

        # Collect text lines
        text_lines = []
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            if not stripped:
                break
            if stripped.isdigit():
                if i + 1 < len(lines) and parse_timestamp_line(lines[i + 1].strip()):
                    break
            if parse_timestamp_line(stripped):
                break
            text_lines.append(line.rstrip())
            i += 1

        blocks.append(
            SubtitleBlock(
                index=index,
                start_time=start_time,
                end_time=end_time,
                text_lines=text_lines,
                line_number=line_number,
            )
        )

    return blocks

def validate_timestamps_match(en_block: SubtitleBlock, target_block: SubtitleBlock) -> bool:
    """Check if timestamps match between English and target blocks"""
    return (
        en_block.start_time == target_block.start_time
        and en_block.end_time == target_block.end_time
    )

def calculate_match_rate(issues: List[ValidationIssue], total_blocks: int) -> float:
    """Calculate percentage of valid blocks"""
    if total_blocks == 0:
        return 0.0
    error_count = sum(1 for i in issues if i.severity == "error")
    return ((total_blocks - error_count) / total_blocks) * 100

def validate_subtitle_pair(
    en_blocks: List[SubtitleBlock],
    target_blocks: List[SubtitleBlock],
    filename: str,
    target_lang: str,
) -> ValidationResult:
    """Validate target subtitles against English reference (OPTIMIZED)"""
    issues: List[ValidationIssue] = []

    # Quick check: if target file is empty
    if len(target_blocks) == 0:
        issues.append(
            ValidationIssue(
                issue_type="empty_file",
                severity="error",
                block_index=None,
                message="Target subtitle file is empty",
            )
        )
        return ValidationResult(
            filename=filename,
            target_language=target_lang,
            passed=False,
            issues=issues,
            en_block_count=len(en_blocks),
            target_block_count=0,
            match_rate=0.0,
        )

    # Quick check: block count must match
    if len(en_blocks) != len(target_blocks):
        issues.append(
            ValidationIssue(
                issue_type="block_count_mismatch",
                severity="error",
                block_index=None,
                message=f"Block count mismatch: {len(en_blocks)} vs {len(target_blocks)}",
                details={
                    "en_count": len(en_blocks),
                    "target_count": len(target_blocks),
                    "difference": abs(len(en_blocks) - len(target_blocks)),
                },
            )
        )
        # Don't bother checking further if block counts don't match
        match_rate = 0.0
        passed = False
        return ValidationResult(
            filename=filename,
            target_language=target_lang,
            passed=passed,
            issues=issues,
            en_block_count=len(en_blocks),
            target_block_count=len(target_blocks),
            match_rate=match_rate,
        )

    # Fast validation: only check critical blocks
    error_count = 0
    checked_blocks = 0
    
    for i in range(len(en_blocks)):
        en_b = en_blocks[i]
        tg_b = target_blocks[i]

        # Skip silent blocks
        if not en_b.has_text:
            continue
        
        checked_blocks += 1

        # Quick timestamp check
        if en_b.start_time != tg_b.start_time or en_b.end_time != tg_b.end_time:
            issues.append(
                ValidationIssue(
                    issue_type="timestamp_mismatch",
                    severity="error",
                    block_index=i + 1,
                    message=f"Timestamp mismatch at block {i + 1}",
                    details={
                        "en_start": en_b.start_time,
                        "target_start": tg_b.start_time,
                    },
                )
            )
            error_count += 1
            continue

        # Quick check: does target have content?
        if not tg_b.has_text:
            issues.append(
                ValidationIssue(
                    issue_type="missing_dialogue",
                    severity="error",
                    block_index=i + 1,
                    message=f"Missing translation in block {i + 1}",
                    details={"en_text": en_b.text_preview},
                )
            )
            error_count += 1

    # Calculate match rate only for checked blocks
    if checked_blocks > 0:
        match_rate = ((checked_blocks - error_count) / checked_blocks) * 100
    else:
        match_rate = 100.0
    
    passed = error_count == 0 and len(issues) == 0

    return ValidationResult(
        filename=filename,
        target_language=target_lang,
        passed=passed,
        issues=issues,
        en_block_count=len(en_blocks),
        target_block_count=len(target_blocks),
        match_rate=match_rate,
    )
