from pathlib import Path
import hashlib


def generate_sigil(text: str, sigil_dir: Path = Path("sigils")) -> Path:
    from PIL import Image, ImageDraw

    sigil_dir.mkdir(exist_ok=True)
    hash_val = hashlib.sha256(text.encode()).hexdigest()
    filename = f"sigil_{hash_val[:8]}.png"
    filepath = sigil_dir / filename

    size = 128
    img = Image.new("RGB", (size, size), color="white")
    draw = ImageDraw.Draw(img)

    for i in range(0, len(hash_val), 4):
        x = int(hash_val[i], 16) % size
        y = int(hash_val[i + 1], 16) % size
        r = (int(hash_val[i + 2], 16) % 10) + 2
        draw.ellipse((x, y, x + r, y + r), fill="black")

    img.save(filepath)
    print(f"[Glypha] Sigil forged: {filename}")
    return filepath
