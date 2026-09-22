"""Extract the clip segments named in media.CLIPS into a frame cache.

Decoding a 20 s H.264 file at a random timestamp, thousands of times, from four
worker processes, is not something to do inside the render loop.  This runs once
and leaves a JPEG per source frame, already cropped and scaled, which the render
then reads by index.
"""
from __future__ import annotations

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from media import CACHE, CLIPS, VID_DIR  # noqa: E402

SRC_FPS = 24
LONG_EDGE = 1440          # room for a push-in before the 1080x1920 fill


def main():
    os.makedirs(CACHE, exist_ok=True)
    for key, spec in CLIPS.items():
        out = os.path.join(CACHE, key)
        if os.path.isdir(out) and os.listdir(out):
            print(f"  {key:16s} cached")
            continue
        os.makedirs(out, exist_ok=True)
        x0, y0, x1, y1 = spec["crop"]
        vf = (f"crop=iw*{x1 - x0:.4f}:ih*{y1 - y0:.4f}:iw*{x0:.4f}:ih*{y0:.4f},"
              f"scale=-2:{LONG_EDGE}:flags=lanczos")
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
               "-ss", str(spec["start"]), "-to", str(spec["end"]),
               "-i", os.path.join(VID_DIR, spec["file"]),
               "-vf", vf, "-r", str(SRC_FPS), "-q:v", "2",
               os.path.join(out, "%05d.jpg")]
        subprocess.run(cmd, check=True)
        n = len(os.listdir(out))
        print(f"  {key:16s} {n:4d} frames  ({spec['end'] - spec['start']:.1f}s)")


if __name__ == "__main__":
    main()
