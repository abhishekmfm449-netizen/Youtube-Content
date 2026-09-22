#!/usr/bin/env bash
# One-shot rebuild of the Short from the supplied assets.
set -euo pipefail
cd "$(dirname "$0")"

python3 src/prep_media.py      # clip frame cache (skips if already built)
python3 src/voiceover.py       # narration.wav + timeline.json (the master timeline)
python3 src/render.py "$@"     # frames + audio mix + encode
python3 src/thumbnail.py
python3 src/qc.py
