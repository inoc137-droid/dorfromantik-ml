from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "processed"
DST_DIR = BASE_DIR / "processed_render"

TARGET_SIZE = (256, 256)

DST_DIR.mkdir(parents=True, exist_ok=True)

files = sorted(SRC_DIR.glob("*.png"))

print(f"Found {len(files)} files")

for src_path in sorted(SRC_DIR.glob("*.png")):
    img = Image.open(src_path).convert("RGBA")
    img = img.resize(TARGET_SIZE, Image.Resampling.LANCZOS)

    dst_path = DST_DIR / src_path.name
    img.save(dst_path, format="PNG", optimize=True, compress_level=9)

    print(f"{src_path.name} -> {dst_path.name}")

print("Fertig.")