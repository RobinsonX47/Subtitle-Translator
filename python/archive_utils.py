import os
import zipfile
import rarfile
import shutil
from shutil import make_archive, which

def _has_unrar():
    """Check if unrar or WinRAR is available."""
    candidates = ["unrar", "unrar.exe", "winrar", "winrar.exe", "bsdtar"]
    return any(which(cmd) is not None for cmd in candidates)

def extract_archive(input_path, extract_to):
    """Extracts .zip or .rar archive to a target folder."""
    os.makedirs(extract_to, exist_ok=True)
    lower = input_path.lower()

    if lower.endswith(".zip"):
        with zipfile.ZipFile(input_path, "r") as zf:
            zf.extractall(extract_to)
    elif lower.endswith(".rar"):
        if not _has_unrar():
            raise RuntimeError("WinRAR or unrar not found on PATH.")
        with rarfile.RarFile(input_path) as rf:
            rf.extractall(path=extract_to)
    else:
        raise RuntimeError("Unsupported file format. Use .zip or .rar")

def make_zip(folder_path, output_zip_path):
    """Zips a folder into a .zip file."""
    os.makedirs(os.path.dirname(output_zip_path), exist_ok=True)
    base, _ = os.path.splitext(output_zip_path)
    make_archive(base, "zip", folder_path)
