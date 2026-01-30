import hashlib
from pathlib import Path
from collections import Counter
import re
from config import EDENISH_EXTS, CODE_EXTS, DOC_EXTS, IMG_EXTS, AUDIO_EXTS, ARCHIVE_EXTS, SAFE_MAX_BYTES_TO_PEEK, PKG_HINT_PATTERNS, PFX_SPLIT
from collections import defaultdict

def decide_category(p: Path) -> str:
    ext = p.suffix.lower()
    if ext in EDENISH_EXTS:
        return "Eden"
    if ext in CODE_EXTS:
        return "Code"
    if ext in DOC_EXTS:
        return "Docs"
    if ext in IMG_EXTS:
        return "MediaImages"
    if ext in AUDIO_EXTS:
        return "MediaAudio"
    if ext in ARCHIVE_EXTS:
        return "Archives"
    return "Other"

def smarter_decide_category(p: Path) -> str:
    """Context-aware categorization that looks inside small text files."""
    ext = p.suffix.lower()
    base = decide_category(p)
    try:
        if p.stat().st_size < SAFE_MAX_BYTES_TO_PEEK and ext in {".txt", ".md", ".json", ".yaml", ".yml"}:
            text = peek_text(p).lower()
            if "def " in text or "class " in text or "import " in text or "function " in text:
                return "Code"
            if "docker" in text or "services:" in text or "compose" in text:
                return "DevOps"
            if "dependencies" in text or "require(" in text:
                return "NodeProject"
    except Exception:
        pass
    return base

def peek_text(p: Path) -> str:
    try:
        with p.open("rb") as f:
            data = f.read(SAFE_MAX_BYTES_TO_PEEK)
        return data.decode("utf-8", errors="ignore")
    except Exception:
        return ""

def project_signals(file_paths):
    sigs = Counter()
    for p in file_paths:
        s = str(p).replace("\\", "/")
        for name, rx in PKG_HINT_PATTERNS:
            if rx.search(s):
                sigs[name] += 1
        if p.suffix.lower() == ".py" and "kivy" in peek_text(p).lower():
            sigs["kivy"] += 1
    return sigs

def group_candidates(files):
    buckets = defaultdict(list)
    for p in files:
        stem = p.stem
        token = PFX_SPLIT.split(stem)[0].lower() if stem else "_"
        key = (token, p.parent)
        buckets[key].append(p)
    merged = defaultdict(list)
    for (token, parent), lst in buckets.items():
        merged[token].extend(lst)
    groups = {}
    for token, lst in merged.items():
        uniq = sorted(set(lst))
        if len(uniq) < 2:
            continue
        if len({p.suffix.lower() for p in uniq}) >= 2 or len(uniq) >= 3:
            groups[token] = uniq
    return groups

def _hash(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def _same_file(a: Path, b: Path) -> bool:
    try:
        return _hash(a) == _hash(b)
    except Exception:
        return False

def _disambig(p: Path) -> Path:
    base = p.with_suffix("")
    ext = p.suffix
    i = 1
    while p.exists():
        p = base.with_name(base.name + f"_{i}").with_suffix(ext)
        i += 1
    return p
