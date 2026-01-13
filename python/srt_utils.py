import re

def parse_srt(content):
    """Parse SRT content into structured blocks."""
    pattern = re.compile(r"(\d+)\s+(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\s+(.*?)\s*(?=\n\d+\n|\Z)", re.S)
    matches = pattern.findall(content)

    blocks = []
    for m in matches:
        blocks.append({
            "index": m[0],
            "start": m[1],
            "end": m[2],
            "lines": [line.strip() for line in m[3].split("\n") if line.strip()]
        })
    return blocks

def rebuild_srt(blocks):
    """Rebuild structured SRT blocks into text."""
    parts = []
    for b in blocks:
        lines = "\n".join(b["lines"])
        parts.append(f"{b['index']}\n{b['start']} --> {b['end']}\n{lines}\n")
    return "\n".join(parts)
