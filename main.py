#!/usr/bin/env python3
"""Entry program for make.fun's news-image-20261117 competition.

Writes the entry image to /output/entry.png. The image (entry.png, drawn
by draw.py and committed beside this file) is copied byte-for-byte, so
repeated runs always produce identical output. Standard library only.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")
OUTPUT_DIR = "/output"
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "entry.png")


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
JPEG_SIGNATURE = b"\xff\xd8\xff"
MAX_BYTES = 1024 * 1024  # competition cap: 1 MiB


def verify(path):
    """Check the written image: size within the cap and a real PNG/JPEG
    signature. Returns (size, kind) or raises ValueError."""
    size = os.path.getsize(path)
    if size == 0 or size > MAX_BYTES:
        raise ValueError(f"image size {size} outside 1..{MAX_BYTES} bytes")
    with open(path, "rb") as fh:
        head = fh.read(8)
    if head.startswith(PNG_SIGNATURE):
        return size, "PNG"
    if head.startswith(JPEG_SIGNATURE):
        return size, "JPEG"
    raise ValueError("image has neither a PNG nor a JPEG signature")


def main():
    if not os.path.isfile(SOURCE):
        print(f"error: committed image not found at {SOURCE}", file=sys.stderr)
        return 1
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    shutil.copyfile(SOURCE, OUTPUT_PATH)
    try:
        size, kind = verify(OUTPUT_PATH)
    except ValueError as exc:
        print(f"error: verification failed: {exc}", file=sys.stderr)
        return 1
    print(f"entry.png written: {size} bytes, {kind}, verified OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
