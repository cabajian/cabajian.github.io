"""Make web-sized copies of gallery photos and print the HTML to paste.

Drop full-size photos into images/engagement/ (or pass other folders), then:

    pip install pillow
    python tools/build_gallery.py

For each photo this writes two files to images/web/gallery/:
    <name>-800.jpg   thumbnail shown in the grid (800px wide)
    <name>-2000.jpg  enlarged view in the lightbox (2000px on the long side)
Photos that are already up to date are skipped. Paste the printed <li> for any
new photo into the gallery list in index.html and fill in its alt text.
"""

import sys
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "images" / "web" / "gallery"
EXTS = {".jpg", ".jpeg", ".png"}


def save(im, path, size):
    copy = im.copy()
    copy.thumbnail(size, Image.LANCZOS)
    copy.save(path, quality=80, optimize=True, progressive=True)
    return copy.size


def main():
    sources = [Path(p) for p in sys.argv[1:]] or [ROOT / "images" / "engagement"]
    OUT.mkdir(parents=True, exist_ok=True)
    photos = sorted(p for d in sources for p in d.iterdir() if p.suffix.lower() in EXTS)

    for src in photos:
        thumb = OUT / f"{src.stem}-800.jpg"
        large = OUT / f"{src.stem}-2000.jpg"
        im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
        if not thumb.exists() or thumb.stat().st_mtime < src.stat().st_mtime:
            save(im, thumb, (800, 10_000))
            save(im, large, (2000, 2000))
            print(f"built {src.name}", file=sys.stderr)
        w, h = Image.open(thumb).size
        rel = lambda p: p.relative_to(ROOT).as_posix()
        print(
            f'<li><a href="{rel(large)}"><img src="{rel(thumb)}" '
            f'width="{w}" height="{h}" alt="" loading="lazy" /></a></li>'
        )


if __name__ == "__main__":
    main()
