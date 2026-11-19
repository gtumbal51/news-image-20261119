#!/usr/bin/env python3
"""Copy the news-image entry to the make.fun output directory.

Reads the MAKEFUN_OUTPUT_DIR environment variable and copies the
entry.png sitting next to this script into it as entry.png, then
verifies the copy: it must be a valid PNG, exactly 1024x1024, and
byte-identical in size to the source.
"""

import os
import shutil
import struct
import sys
from pathlib import Path

EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def verify_png(path: Path) -> str | None:
    """Return an error message if path is not a valid 1024x1024 PNG."""
    try:
        data = path.read_bytes()
    except OSError as exc:
        return f"cannot read {path}: {exc}"
    if len(data) < 33 or data[:8] != PNG_MAGIC:
        return f"{path} is not a PNG file (bad magic bytes)"
    # IHDR chunk: length (4) + "IHDR" (4) + width (4) + height (4).
    if data[12:16] != b"IHDR":
        return f"{path} is not a PNG file (missing IHDR chunk)"
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        return (
            f"{path} is {width}x{height}, "
            f"expected {EXPECTED_WIDTH}x{EXPECTED_HEIGHT}"
        )
    return None


def main() -> int:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        print("error: MAKEFUN_OUTPUT_DIR is not set", file=sys.stderr)
        return 1

    src = Path(__file__).resolve().parent / "entry.png"
    if not src.is_file():
        print(f"error: entry image not found: {src}", file=sys.stderr)
        return 1

    dest_dir = Path(out_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "entry.png"
    shutil.copyfile(src, dest)

    # Verify the copy: same size as the source, and a valid 1024x1024 PNG.
    if dest.stat().st_size != src.stat().st_size:
        print(
            f"error: copy size mismatch: {dest} is "
            f"{dest.stat().st_size} bytes, source is {src.stat().st_size}",
            file=sys.stderr,
        )
        return 1
    error = verify_png(dest)
    if error:
        print(f"error: verification failed: {error}", file=sys.stderr)
        return 1

    print(f"copied {src} -> {dest} (verified PNG {EXPECTED_WIDTH}x{EXPECTED_HEIGHT})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
