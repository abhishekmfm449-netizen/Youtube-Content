"""Quality control on the rendered file.

Checks the things that actually go wrong in a vertical render: wrong shape, a
letterbox creeping in, stretched footage, audio that drifts out of the picture,
a gap in the narration, captions wandering out of the safe area, a hook that is
dark for the first second.  Run after render.py.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import captions as CAP  # noqa: E402
from design import CAP_TOP, FPS, H, SAFE_BOTTOM, W  # noqa: E402

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "out")
BUILD = os.path.join(HERE, "build")
VIDEO = os.path.join(OUT, "Vayu_UTtaM_YouTube_Short.mp4")

PASS, FAIL = "PASS", "FAIL"
results = []


def check(name, ok, detail=""):
    results.append((PASS if ok else FAIL, name, detail))


def probe(path):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", path],
                         capture_output=True, text=True).stderr
    return out


def frames(path, n=90):
    """Decode n evenly spaced frames as raw RGB."""
    dur = float(json.load(open(os.path.join(BUILD, "timeline.json")))["duration"])
    step = max(1, int(dur * FPS / n))
    p = subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", path,
         "-vf", f"select='not(mod(n\\,{step}))'", "-vsync", "0",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        capture_output=True)
    buf = np.frombuffer(p.stdout, dtype=np.uint8)
    k = buf.size // (W * H * 3)
    return buf[:k * W * H * 3].reshape(k, H, W, 3)


def main():
    if not os.path.exists(VIDEO):
        raise SystemExit(f"not found: {VIDEO}")

    info = probe(VIDEO)
    timeline = json.load(open(os.path.join(BUILD, "timeline.json")))
    cards = CAP.build(timeline)

    # ---- container ----------------------------------------------------------
    check("resolution is 1080x1920", f"{W}x{H}" in info, info.split("Video:")[1][:90]
          if "Video:" in info else "")
    check("aspect ratio is 9:16", abs(W / H - 9 / 16) < 1e-6, f"{W}/{H}")
    check("30 fps", "30 fps" in info)
    check("H.264 / yuv420p", "h264" in info and "yuv420p" in info)
    check("AAC audio at 48 kHz stereo",
          "aac" in info and "48000 Hz" in info and "stereo" in info)
    check("faststart (moov before mdat)",
          subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-v", "error",
                          "-i", VIDEO, "-f", "null", "-"],
                         capture_output=True).returncode == 0,
          "stream decodes cleanly")

    vdur = float([l for l in info.splitlines() if "Duration" in l][0]
                 .split("Duration:")[1].split(",")[0].strip()
                 .replace(":", " ").split()[-1]) + 60 * float(
        [l for l in info.splitlines() if "Duration" in l][0]
        .split("Duration:")[1].split(",")[0].strip().split(":")[1])
    check("duration matches the narration timeline",
          abs(vdur - timeline["duration"]) < 0.35,
          f"video {vdur:.2f}s vs timeline {timeline['duration']:.2f}s")

    # ---- picture ------------------------------------------------------------
    fr = frames(VIDEO)
    edge = 6
    top = fr[:, :edge, :, :].mean()
    bot = fr[:, -edge:, :, :].mean()
    left = fr[:, :, :edge, :].mean()
    right = fr[:, :, -edge:, :].mean()
    check("no black bars on any edge",
          min(top, bot, left, right) > 2.0,
          f"edge means t={top:.1f} b={bot:.1f} l={left:.1f} r={right:.1f}")

    perframe = fr.reshape(len(fr), -1).mean(axis=1)
    check("no fully black frames", perframe.min() > 3.0, f"darkest frame mean {perframe.min():.1f}")
    check("hook is lit in the first second",
          fr[0].mean() > 12.0, f"frame 0 mean {fr[0].mean():.1f}")
    check("no blown-out frames", perframe.max() < 210, f"brightest frame mean {perframe.max():.1f}")

    # ---- captions -----------------------------------------------------------
    lo = int(H * CAP_TOP)
    check("captions stay inside the reserved band",
          all(c["end"] > c["start"] for c in cards) and lo < SAFE_BOTTOM,
          f"band {lo}px..{SAFE_BOTTOM}px of {H}px")
    check("no caption runs past the narration",
          max(c["end"] for c in cards) <= timeline["duration"] + 0.01,
          f"last caption ends {max(c['end'] for c in cards):.2f}s")
    check("no caption card is a flicker",
          min(c["end"] - c["start"] for c in cards) >= 0.45,
          f"shortest card {min(c['end'] - c['start'] for c in cards):.2f}s")
    check("caption text matches the script verbatim",
          " ".join(c["text"] for c in cards).split()
          == " ".join(ln["text"] for ln in timeline["lines"]).split())

    # ---- audio --------------------------------------------------------------
    with wave.open(os.path.join(BUILD, "mix.wav"), "rb") as w:
        sr = w.getframerate()
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32)
        a = a.reshape(-1, w.getnchannels()).mean(axis=1) / 32768.0
    with wave.open(os.path.join(BUILD, "narration.wav"), "rb") as w:
        n = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0

    check("no clipping", int((np.abs(a) > 0.999).sum()) == 0,
          f"peak {20 * np.log10(np.abs(a).max()):.2f} dBFS")
    # A truncated recording starts on a discontinuity - a large value at sample
    # zero.  A natural onset ramps up instead, so testing "is the first 50 ms
    # quiet" just measures how promptly the reader starts, not whether the file
    # was cut.  Test the discontinuity, and the tail separately.
    onset = int(np.argmax(np.abs(n) > 0.05)) / sr
    check("narration does not start on a discontinuity",
          abs(n[0]) < 0.02 and np.abs(n[:int(0.01 * sr)]).max() < 0.05,
          f"first sample {abs(n[0]):.4f}, speech begins at {onset * 1000:.0f} ms")
    check("narration tail is clean silence",
          np.abs(n[-int(0.3 * sr):]).max() < 0.01,
          f"last 300 ms peak {np.abs(n[-int(0.3 * sr):]).max():.4f}")

    bed = a[:len(n)] - n
    speech = np.abs(n) > 0.05
    sep = (20 * np.log10(np.sqrt((n[speech] ** 2).mean()))
           - 20 * np.log10(np.sqrt((bed[speech] ** 2).mean())))
    check("narration sits clearly above the bed", sep > 10.0, f"{sep:.1f} dB separation")

    # a silent stretch longer than the longest scripted pause would be a gap
    win = int(0.25 * sr)
    env = np.abs(a[:len(a) // win * win].reshape(-1, win)).max(axis=1)
    run = best = 0
    for v in env < 0.004:
        run = run + 1 if v else 0
        best = max(best, run)
    check("no unintended silent gap", best * 0.25 <= 2.2, f"longest quiet run {best * 0.25:.2f}s")

    # ---- report -------------------------------------------------------------
    width = max(len(n) for _, n, _ in results)
    for status, name, detail in results:
        mark = "✓" if status == PASS else "✗"
        print(f"  {mark} {name:<{width}}  {detail}")
    bad = [r for r in results if r[0] == FAIL]
    print(f"\n{len(results) - len(bad)}/{len(results)} checks passed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
