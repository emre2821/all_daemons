import re

PALETTES = {
    "DreambearerLight": ["#F6F3EE", "#E6D9C9", "#CFAF91", "#8B6B5A", "#3B2F2A"],
    "EdenSky": ["#DFF0FF", "#B8E1FF", "#7BC6FF", "#368DFF", "#1D4ED8"],
    "VelvetDivision": ["#1A1A1A", "#3A2E39", "#6A365D", "#A33EA1", "#EAD7EF"],
}
BG = PALETTES["DreambearerLight"][0]
FG = "#1A1A1A"
ACCENT = PALETTES["EdenSky"][3]

EDENISH_EXTS = {".chaos", ".chaosincarnet", ".chaos-ception", ".vas", ".mirror.json",
                ".shalfredlayer.chaos", ".chaosmeta", ".chaosscript", ".chaoscript"}
CODE_EXTS = {".py", ".ipynb", ".js", ".ts", ".tsx", ".jsx", ".json", ".yaml", ".yml",
            ".toml", ".ini", ".cfg", ".md", ".html", ".css", ".scss", ".less", ".java",
            ".kt", ".cs", ".cpp", ".c", ".go", ".rs"}
DOC_EXTS = {".txt", ".rtf", ".pdf", ".doc", ".docx", ".odt"}
IMG_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg"}
AUDIO_EXTS = {".mp3", ".wav", ".flac", ".m4a", ".ogg"}
ARCHIVE_EXTS = {".zip", ".tar", ".gz", ".bz2", ".7z"}
SAFE_MAX_BYTES_TO_PEEK = 96 * 1024
CATEGORY_FOLDERS = {
    "Eden": "Eden",
    "Code": "Code",
    "Docs": "Docs",
    "MediaImages": "Media/Images",
    "MediaAudio": "Media/Audio",
    "Archives": "Archives",
    "DevOps": "DevOps",
    "NodeProject": "Node",
    "Other": "Other"
}
PKG_HINT_PATTERNS = [
    ("python", re.compile(r"(^|/)setup\.py$|(^|/)pyproject\.toml$|(^|/)requirements\.txt$", re.I)),
    ("node", re.compile(r"(^|/)package\.json$|(^|/)vite\.config|webpack\.config", re.I)),
    ("kivy", re.compile(r"from\s+kivy|\[Kivy\]|buildozer\.spec", re.I)),
]
PFX_SPLIT = re.compile(r"[-_. ]+")
MAX_FILES = 10000
