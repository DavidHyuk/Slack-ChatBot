#!/usr/bin/env python3
"""
Resize an image to exactly 512×512 pixels (default: assets/chatbot_image.png).

  python3 scripts/resize_chatbot_image.py
  python3 scripts/resize_chatbot_image.py --input other.png --output out.png
  python3 scripts/resize_chatbot_image.py --mode stretch   # ignore aspect ratio
  python3 scripts/resize_chatbot_image.py --mode contain # letterbox / pillarbox on transparent canvas

Requires: pip install Pillow (see requirements.txt).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Missing Pillow. Run: pip install Pillow", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PATH = REPO_ROOT / "assets" / "chatbot_image.png"


def _resize_cover(im: Image.Image, size: tuple[int, int]) -> Image.Image:
    w, h = im.size
    tw, th = size
    scale = max(tw / w, th / h)
    nw, nh = int(round(w * scale)), int(round(h * scale))
    resized = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return resized.crop((left, top, left + tw, top + th))


def _resize_contain(im: Image.Image, size: tuple[int, int]) -> Image.Image:
    w, h = im.size
    tw, th = size
    scale = min(tw / w, th / h)
    nw, nh = int(round(w * scale)), int(round(h * scale))
    resized = im.resize((nw, nh), Image.Resampling.LANCZOS)
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        canvas = Image.new("RGBA", size, (0, 0, 0, 0))
        paste_im = resized.convert("RGBA")
    else:
        canvas = Image.new("RGB", size, (255, 255, 255))
        paste_im = resized.convert("RGB")
    left = (tw - nw) // 2
    top = (th - nh) // 2
    canvas.paste(paste_im, (left, top))
    return canvas


def _resize_stretch(im: Image.Image, size: tuple[int, int]) -> Image.Image:
    return im.resize(size, Image.Resampling.LANCZOS)


def resize_to_square(im: Image.Image, size: tuple[int, int], mode: str) -> Image.Image:
    if mode == "cover":
        return _resize_cover(im, size)
    if mode == "contain":
        return _resize_contain(im, size)
    if mode == "stretch":
        return _resize_stretch(im, size)
    raise ValueError(f"unknown mode: {mode}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument(
        "--input",
        "-i",
        type=Path,
        default=DEFAULT_PATH,
        help=f"Source image (default: {DEFAULT_PATH.relative_to(REPO_ROOT)})",
    )
    p.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Destination path (default: overwrite --input)",
    )
    p.add_argument(
        "--mode",
        choices=("cover", "contain", "stretch"),
        default="cover",
        help="cover: center-crop to fill square (default). contain: fit inside square with padding. stretch: distort to square.",
    )
    p.add_argument("--width", type=int, default=512, help="Output width (default: 512)")
    p.add_argument("--height", type=int, default=512, help="Output height (default: 512)")
    args = p.parse_args()

    src = args.input if args.input.is_absolute() else REPO_ROOT / args.input
    out = args.output
    if out is None:
        out = src
    else:
        out = out if out.is_absolute() else REPO_ROOT / out

    if not src.is_file():
        print(f"Input not found: {src}", file=sys.stderr)
        sys.exit(1)

    size = (args.width, args.height)
    im = Image.open(src)
    result = resize_to_square(im, size, args.mode)

    out.parent.mkdir(parents=True, exist_ok=True)
    # Preserve PNG; use original format when saving to same extension
    ext = out.suffix.lower()
    if ext == ".png":
        result.save(out, format="PNG", optimize=True)
    elif ext in (".jpg", ".jpeg"):
        rgb = result.convert("RGB")
        rgb.save(out, format="JPEG", quality=95, optimize=True)
    else:
        result.save(out)

    print(f"Wrote {size[0]}×{size[1]} ({args.mode}) → {out}")


if __name__ == "__main__":
    main()
