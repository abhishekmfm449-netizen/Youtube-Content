"""Render the Short.

    python3 src/render.py [--preview] [--jobs N] [--range A:B]

Reads build/timeline.json, renders every frame, burns in the captions, mixes the
audio and encodes the final MP4.  Frames are handed to ffmpeg over a pipe, so no
PNG sequence ever touches the disk.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import wave
from concurrent.futures import ProcessPoolExecutor

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import captions as CAP  # noqa: E402
import media as MEDIA  # noqa: E402
import sound as SND  # noqa: E402
from design import FPS, H, W, composite, new_layer, resolve, to_image  # noqa: E402
from scenes import SCENES  # noqa: E402

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(HERE, "build")
OUT = os.path.join(HERE, "out")

# Scene cuts land part-way into the pause before each line, so the picture
# changes just ahead of the words - the way a documentary cut actually sits.
CUT_LEAD = 0.55


def scene_spans(timeline):
    lines = timeline["lines"]
    total = timeline["duration"]
    spans = []
    for i, ln in enumerate(lines):
        if i == 0:
            start = 0.0
        else:
            gap = ln["start"] - lines[i - 1]["end"]
            start = ln["start"] - gap * CUT_LEAD
        if i + 1 < len(lines):
            nxt = lines[i + 1]
            gap = nxt["start"] - ln["end"]
            end = nxt["start"] - gap * CUT_LEAD
        else:
            end = total
        spans.append(dict(scene=ln["scene"], start=round(start, 3), end=round(end, 3),
                          line=ln["index"], text=ln["text"]))
    return spans


_STATE = {}


def _init(spans, cards):
    _STATE["spans"] = spans
    _STATE["cards"] = cards


def render_frame(idx):
    t = idx / FPS
    spans = _STATE["spans"]
    sp = spans[-1]
    for s in spans:
        if s["start"] <= t < s["end"]:
            sp = s
            break
    local = t - sp["start"]
    dur = sp["end"] - sp["start"]
    arr = SCENES[sp["scene"]](local, dur)

    # cross-dissolve into the next scene over the last 0.22 s
    XF = 0.22
    i = spans.index(sp)
    if i + 1 < len(spans) and local > dur - XF:
        nxt = spans[i + 1]
        f = (local - (dur - XF)) / XF
        b = SCENES[nxt["scene"]](t - nxt["start"], nxt["end"] - nxt["start"])
        arr = arr * (1 - f) + b * f

    lay, ld = new_layer()
    CAP.draw(ld, _STATE["cards"], t)
    arr = composite(arr, resolve(lay, bloom=2.5, gain=1.05))
    return idx, to_image(arr).tobytes()


def build_audio(timeline, spans, path):
    narr_path = os.path.join(BUILD, "narration.wav")
    with wave.open(narr_path, "rb") as w:
        narration = (np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
                     .astype(np.float32) / 32768.0)
    n = len(narration)
    dur = n / SND.SR

    cuts = [s["start"] for s in spans]
    bed = SND.music_bed(dur, cuts[1:]) * 0.115          # sits ~13 dB under the read
    bed = SND.duck(bed, narration, amount=0.62)

    sfx = np.zeros(n, dtype=np.float32)
    # one soft hit on each act change, quieter on the small beats
    big = {1, 2, 3, 5, 9, 10, 13, 14}
    for s in spans:
        g = 0.30 if s["scene"] in big else 0.17
        SND.place(sfx, SND.impact(), s["start"] - 0.10, g)
    # radar pings under the scope and map scenes
    for s in spans:
        if s["scene"] in (1, 4, 7, 9, 14):
            for k in range(int((s["end"] - s["start"]) / 2.1)):
                SND.place(sfx, SND.radar_ping(), s["start"] + 0.5 + k * 2.1, 0.12)
    # airspace scan on the two question beats
    for s in spans:
        if s["scene"] in (4, 6):
            SND.place(sfx, SND.sweep_air(0.9), s["start"] - 0.25, 0.30)
    # interface blips where the graphics acknowledge something
    for s in spans:
        if s["scene"] in (5, 8, 11):
            for k in range(3):
                SND.place(sfx, SND.ui_blip(), s["start"] + 0.9 + k * 0.85, 0.22)
    # rotor hum wherever a drone is the subject
    for s in spans:
        if s["scene"] in (1, 3, 6, 12, 13):
            SND.place(sfx, SND.drone_hum(min(3.0, s["end"] - s["start"]), seed=s["scene"]),
                      s["start"] + 0.2, 0.10)

    mix = narration + bed + sfx * 0.24
    peak = float(np.abs(mix).max()) or 1.0
    if peak > 0.97:
        mix *= 0.97 / peak

    stereo = np.stack([mix, mix], axis=1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SND.SR)
        w.writeframes((np.clip(stereo, -1, 1) * 32767).astype("<i2").tobytes())
    return dur


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true", help="half resolution, faster")
    ap.add_argument("--jobs", type=int, default=max(1, os.cpu_count() or 2))
    ap.add_argument("--range", default=None, help="seconds A:B, for checking one scene")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    timeline = json.load(open(os.path.join(BUILD, "timeline.json")))
    spans = scene_spans(timeline)
    cards = CAP.build(timeline)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(BUILD, "scenes.json"), "w") as f:
        json.dump(dict(fps=FPS, size=[W, H], duration=timeline["duration"],
                       voiceover=timeline["source"], scenes=spans), f, indent=2)
    with open(os.path.join(OUT, "Vayu_UTtaM_YouTube_Short.srt"), "w") as f:
        f.write(CAP.to_srt(cards))
    # what was used, what was cropped out of it, and what was dropped - written
    # every build so the record cannot drift from the code
    with open(os.path.join(OUT, "asset_manifest.json"), "w") as f:
        json.dump(MEDIA.manifest(), f, indent=2)

    t0, t1 = 0.0, timeline["duration"]
    if args.range:
        a, b = args.range.split(":")
        t0, t1 = float(a), float(b)
    f0, f1 = int(t0 * FPS), int(round(t1 * FPS))
    total = f1 - f0

    audio = os.path.join(BUILD, "mix.wav")
    build_audio(timeline, spans, audio)
    print(f"audio mixed -> {audio}")

    out_path = args.out or os.path.join(OUT, "Vayu_UTtaM_YouTube_Short.mp4")
    ow, oh = (W // 2, H // 2) if args.preview else (W, H)

    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-ss", str(t0), "-i", audio,
        "-map", "0:v", "-map", "1:a", "-shortest",
        "-c:v", "libx264", "-preset", "slow" if not args.preview else "veryfast",
        # CRF 20 rather than a lower number: the film grain is expensive to
        # encode and CRF 17 tripled the file for no visible gain once YouTube
        # re-encodes it. This lands ~4.4 Mbit/s, a clean master to upload.
        "-crf", "20" if not args.preview else "26",
        "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.1",
        "-x264-params", "keyint=60:min-keyint=30:scenecut=0",
        "-movflags", "+faststart",
        "-vf", f"scale={ow}:{oh}:flags=lanczos" if args.preview else "null",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        out_path,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    print(f"rendering {total} frames ({t1 - t0:.1f}s) on {args.jobs} workers...")
    done = 0
    with ProcessPoolExecutor(max_workers=args.jobs, initializer=_init,
                             initargs=(spans, cards)) as ex:
        CHUNK = args.jobs * 6
        for base in range(f0, f1, CHUNK):
            idxs = list(range(base, min(base + CHUNK, f1)))
            for _, buf in sorted(ex.map(render_frame, idxs), key=lambda r: r[0]):
                proc.stdin.write(buf)
            done += len(idxs)
            pct = done / total * 100
            print(f"\r  {done}/{total} frames  {pct:5.1f}%", end="", flush=True)
    print()
    proc.stdin.close()
    rc = proc.wait()
    if rc != 0:
        raise SystemExit(f"ffmpeg exited {rc}")
    print(f"wrote {out_path}  ({os.path.getsize(out_path)/1e6:.1f} MB)")


if __name__ == "__main__":
    main()
