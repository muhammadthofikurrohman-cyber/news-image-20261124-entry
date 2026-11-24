#!/usr/bin/env python3
"""Entry point for 'THE WORLD IN ONE DAY — Tuesday 24 November 2026'.

Copies the pre-rendered broadsheet (entry.png, drawn by draw.py in this
repository with PIL) to $MAKEFUN_OUTPUT_DIR/entry.png.

Standard library only: the grader runs `python3 -P -s main.py` inside a
python:3.13-slim sandbox with no network and no third-party packages, so
this file imports nothing beyond the stdlib, reads no environment value as
code, and performs no randomness or clock reads. The copy is byte-identical
on every run.
"""
import hashlib
import os
import shutil
import struct
import sys

EXPECTED_W, EXPECTED_H = 1024, 1024
MAX_BYTES = 1048576


def _png_size(path):
    with open(path, "rb") as fh:
        head = fh.read(33)
    if len(head) < 33 or head[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("entry.png is not a PNG file")
    if head[12:16] != b"IHDR":
        raise ValueError("entry.png has no IHDR chunk")
    w, h = struct.unpack(">II", head[16:24])
    return w, h


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")

    w, h = _png_size(src)
    if (w, h) != (EXPECTED_W, EXPECTED_H):
        raise ValueError("entry.png is %dx%d, expected %dx%d"
                         % (w, h, EXPECTED_W, EXPECTED_H))
    if os.path.getsize(src) > MAX_BYTES:
        raise ValueError("entry.png exceeds 1 MiB")

    shutil.copyfile(src, dst)
    os.chmod(dst, 0o644)

    # Read-back check: the output must be byte-identical to the source.
    # Any difference (a short write, a stray byte) fails the run loudly
    # instead of shipping a corrupt image to the grader.
    src_digest = hashlib.sha256(open(src, "rb").read()).hexdigest()
    dst_digest = hashlib.sha256(open(dst, "rb").read()).hexdigest()
    if src_digest != dst_digest:
        raise ValueError("copy mismatch: %s != %s" % (dst_digest, src_digest))
    print("wrote %s (%dx%d, sha256 %s)" % (dst, w, h, dst_digest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
