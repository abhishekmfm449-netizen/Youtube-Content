"""Build the master timeline from the narration.

Two modes, decided automatically:

  1. A real voiceover exists at assets/voiceover/voiceover.(wav|mp3|m4a).
     It is used verbatim as the master track.  Per-line boundaries are recovered
     by aligning the speech energy envelope to the script's line lengths, so the
     edit still cuts on the narration.

  2. No voiceover supplied.  A scratch narration is synthesised per line with
     Kokoro (Apache-2.0), which hands us exact per-line boundaries for free.

Either way the output is the same: narration.wav plus timeline.json holding the
start/end of every line.  Nothing downstream knows or cares which mode ran.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from script import LINES, TAIL  # noqa: E402

_VOWELS = __import__("re").compile(r"[aeiouy]+", __import__("re").I)


def _syllables(s: str) -> float:
    """Rough syllable count - a far better duration predictor than characters."""
    n = 0
    for w in s.split():
        core = __import__("re").sub(r"[^a-z]", "", w.lower())
        k = len(_VOWELS.findall(core))
        if core.endswith("e") and k > 1:
            k -= 1
        n += max(1, k)
    return float(max(1, n))

SR = 48000
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(HERE)
# The supplied voiceover lives in the repo's own Voiceover/ folder; the project
# folder is only a fallback for dropping in a replacement read.
VO_DIRS = [os.path.join(REPO, "Voiceover"), os.path.join(HERE, "assets", "voiceover")]
BUILD = os.path.join(HERE, "build")
ALIGN_FILE = os.path.join(HERE, "assets", "voiceover", "alignment.json")

KOKORO_MODEL = os.environ.get("KOKORO_MODEL", "/tmp/kok/kokoro-v1.0.onnx")
KOKORO_VOICES = os.environ.get("KOKORO_VOICES", "/tmp/kok/voices-v1.0.bin")
KOKORO_VOICE = os.environ.get("KOKORO_VOICE", "am_michael")
KOKORO_SPEED = float(os.environ.get("KOKORO_SPEED", "0.96"))


def find_supplied() -> str | None:
    for vo_dir in VO_DIRS:
        if not os.path.isdir(vo_dir):
            continue
        for name in sorted(os.listdir(vo_dir)):
            if name.startswith("."):
                continue
            if os.path.splitext(name)[1].lower() in (".wav", ".mp3", ".m4a", ".aac",
                                                     ".flac", ".ogg"):
                return os.path.join(vo_dir, name)
    return None


def read_wav_mono(path: str) -> np.ndarray:
    with wave.open(path, "rb") as w:
        assert w.getsampwidth() == 2, "expected 16-bit wav"
        data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
        if w.getnchannels() == 2:
            data = data.reshape(-1, 2).mean(axis=1)
        return data.astype(np.float32) / 32768.0


def write_wav_mono(path: str, x: np.ndarray, sr: int = SR) -> None:
    x = np.clip(x, -1.0, 1.0)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((x * 32767.0).astype("<i2").tobytes())


def decode_to_wav(src: str, dst: str) -> None:
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", src,
         "-ac", "1", "-ar", str(SR), "-c:a", "pcm_s16le", dst],
        check=True,
    )


def trim_silence(x: np.ndarray, thresh: float = 0.012, pad: int = int(0.04 * SR)) -> np.ndarray:
    """Trim leading/trailing near-silence so our designed pauses are the real ones."""
    if x.size == 0:
        return x
    loud = np.abs(x) > thresh
    if not loud.any():
        return x
    a, b = int(np.argmax(loud)), int(len(loud) - np.argmax(loud[::-1]))
    return x[max(0, a - pad):min(len(x), b + pad)]


# ---------------------------------------------------------------- mode 2: TTS

def synth_lines() -> list[np.ndarray]:
    from kokoro_onnx import Kokoro

    if not (os.path.exists(KOKORO_MODEL) and os.path.exists(KOKORO_VOICES)):
        raise SystemExit(
            "Kokoro model files not found.  Either drop a real voiceover into\n"
            f"  {VO_DIRS[1]}\n"
            "or fetch the scratch-narration model:\n"
            "  bash project/fetch_tts_model.sh"
        )

    kok = Kokoro(KOKORO_MODEL, KOKORO_VOICES)
    out = []
    for i, ln in enumerate(LINES, 1):
        samples, sr = kok.create(ln["speak"], voice=KOKORO_VOICE, speed=KOKORO_SPEED, lang="en-us")
        samples = np.asarray(samples, dtype=np.float32)
        if sr != SR:  # kokoro is 24k; linear resample is plenty for speech
            n = int(round(len(samples) * SR / sr))
            samples = np.interp(
                np.linspace(0, len(samples) - 1, n), np.arange(len(samples)), samples
            ).astype(np.float32)
        out.append(trim_silence(samples))
        print(f"  line {i:2d}  {len(out[-1]) / SR:5.2f}s  {ln['text'][:52]}...")
    return out


# ------------------------------------------- mode 1: align a supplied recording

def speech_segments(x, thresh_rel=0.030, min_gap=0.12):
    """Split the recording into runs of speech separated by real pauses."""
    win = int(0.02 * SR)
    frames = len(x) // win
    env = np.abs(x[: frames * win].reshape(frames, win)).max(axis=1)
    env = np.convolve(env, np.ones(3) / 3, mode="same")
    thr = max(0.015, float(np.percentile(env, 95)) * thresh_rel)

    segs, run = [], None
    for i, v in enumerate(env > thr):
        if v and run is None:
            run = i
        elif not v and run is not None:
            segs.append([run * win / SR, i * win / SR])
            run = None
    if run is not None:
        segs.append([run * win / SR, frames * win / SR])

    merged = []
    for a, b in segs:
        if merged and a - merged[-1][1] < min_gap:
            merged[-1][1] = b
        else:
            merged.append([a, b])
    return [(a, b) for a, b in merged if b - a > 0.08]


def align_supplied(x):
    """Assign speech segments to script lines.

    A narration line is one or more consecutive speech segments - a read breaks
    mid-sentence for breath, and an ellipsis in the script becomes a real pause.
    So the job is to cut the segment list into N consecutive groups, one per
    line.  This is a shortest-path problem over group boundaries, solved exactly
    by dynamic programming, scoring each group on how close its duration is to
    what the line's syllable count predicts, with a bonus for cutting at a long
    pause.  That beats picking the N-1 longest gaps, which happily puts a line
    break in the middle of "So... what does it actually do?".
    """
    segs = speech_segments(x)
    n_lines = len(LINES)
    if len(segs) < n_lines:
        # Not enough pauses to work with - fall back to a proportional split.
        total = len(x) / SR
        w = np.array([_syllables(ln["text"]) for ln in LINES], dtype=float)
        edges = np.concatenate([[0.0], np.cumsum(w / w.sum()) * total])
        return [(float(edges[i]), float(edges[i + 1])) for i in range(n_lines)]

    m = len(segs)
    speak = np.array([b - a for a, b in segs])
    total_speech = speak.sum()
    weights = np.array([_syllables(ln["text"]) for ln in LINES], dtype=float)
    expect = weights / weights.sum() * total_speech

    gap_before = [0.0] + [segs[i][0] - segs[i - 1][1] for i in range(1, m)]
    max_gap = max(gap_before) or 1.0

    INF = float("inf")
    cost = np.full((n_lines + 1, m + 1), INF)
    back = np.zeros((n_lines + 1, m + 1), dtype=int)
    cost[0, 0] = 0.0
    for li in range(1, n_lines + 1):
        for j in range(li, m - (n_lines - li) + 1):
            best, arg = INF, j - 1
            for i in range(li - 1, j):
                if cost[li - 1, i] == INF:
                    continue
                spoken = speak[i:j].sum()
                # duration error, relative to what this line should take
                c = cost[li - 1, i] + abs(spoken - expect[li - 1]) / max(expect[li - 1], 0.4)
                # prefer starting a line after a long pause
                c -= 0.55 * (gap_before[i] / max_gap)
                # and mildly discourage splitting on a very short gap
                if i > 0 and gap_before[i] < 0.20:
                    c += 0.45
                if c < best:
                    best, arg = c, i
            cost[li, j] = best
            back[li, j] = arg

    j, bounds = m, []
    for li in range(n_lines, 0, -1):
        i = back[li, j]
        bounds.append((segs[i][0], segs[j - 1][1]))
        j = i
    return list(reversed(bounds))


def load_pinned(vo_path: str):
    """Return a hand-checked line alignment if one exists for this recording.

    The automatic aligner is good but not perfect, and the line boundaries drive
    every cut in the edit, so the alignment actually shipped is verified by ear
    against the pause map and pinned here.  It is keyed on the audio content,
    not the filename: re-export the voiceover and the pin stops applying, which
    is the safe direction to fail in.
    """
    path = os.path.join(os.path.dirname(ALIGN_FILE), os.path.basename(ALIGN_FILE))
    if not os.path.exists(path):
        return None
    with open(vo_path, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    data = json.load(open(path))
    entry = data.get(digest)
    if not entry:
        return None
    if len(entry["bounds"]) != len(LINES):
        return None
    return [(float(a), float(b)) for a, b in entry["bounds"]]


def main() -> None:
    os.makedirs(BUILD, exist_ok=True)
    supplied = find_supplied()

    if supplied:
        print(f"Using supplied voiceover: {os.path.basename(supplied)}")
        tmp = os.path.join(BUILD, "_supplied.wav")
        decode_to_wav(supplied, tmp)
        narration = read_wav_mono(tmp)

        pinned = load_pinned(supplied)
        if pinned:
            bounds = pinned
            print("  using the pinned, hand-checked alignment for this recording")
        else:
            bounds = align_supplied(narration)
            print("  alignment derived automatically - check build/timeline.json")
        source = os.path.basename(supplied)
    else:
        print("No voiceover supplied - synthesising a scratch narration.")
        clips = synth_lines()
        pieces, bounds, t = [], [], 0.0
        for ln, clip in zip(LINES, clips):
            pieces.append(np.zeros(int(ln["lead_in"] * SR), dtype=np.float32))
            t += ln["lead_in"]
            start = t
            pieces.append(clip)
            t += len(clip) / SR
            bounds.append((start, t))
        narration = np.concatenate(pieces)
        source = f"scratch TTS (Kokoro, voice={KOKORO_VOICE})"

    narration = np.concatenate([narration, np.zeros(int(TAIL * SR), dtype=np.float32)])

    peak = float(np.abs(narration).max()) or 1.0
    narration = narration * (0.89 / peak)

    write_wav_mono(os.path.join(BUILD, "narration.wav"), narration)

    duration = len(narration) / SR
    timeline = dict(
        source=source,
        supplied=bool(supplied),
        sample_rate=SR,
        duration=round(duration, 3),
        lines=[
            dict(
                index=i + 1,
                scene=LINES[i]["scene"],
                start=round(a, 3),
                end=round(b, 3),
                text=LINES[i]["text"],
            )
            for i, (a, b) in enumerate(bounds)
        ],
    )
    with open(os.path.join(BUILD, "timeline.json"), "w") as f:
        json.dump(timeline, f, indent=2)

    print(f"\nnarration.wav  {duration:.2f}s   ({source})")
    for ln in timeline["lines"]:
        print(f"  {ln['index']:2d}  {ln['start']:6.2f} -> {ln['end']:6.2f}  scene {ln['scene']}")


if __name__ == "__main__":
    main()
