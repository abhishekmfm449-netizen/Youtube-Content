"""Render the thumbnail frame.

Taken from the Vayu UTtaM title beat in scene 2 - the one moment carrying the
subject, the name and a lit foreground at once.

The frame is rendered from the scene directly rather than grabbed out of the
finished MP4, so it comes out without a caption across it and without the
encoder's compression on top.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from design import to_image  # noqa: E402
from scenes import SCENES  # noqa: E402

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "out")
BUILD = os.path.join(HERE, "build")


def main():
    spans = json.load(open(os.path.join(BUILD, "scenes.json")))["scenes"]
    s2 = next(s for s in spans if s["scene"] == 2)
    dur = s2["end"] - s2["start"]
    local = dur * 0.62                       # title and subtitle both fully up

    dst = os.path.join(OUT, "thumbnail.jpg")
    to_image(SCENES[2](local, dur)).save(dst, quality=94, subsampling=0)
    print(f"thumbnail from scene 2 at +{local:.2f}s -> {dst} "
          f"({os.path.getsize(dst) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
