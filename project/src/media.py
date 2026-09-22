"""Loading, cropping and grading the supplied footage.

Two things happen here.

First, crop windows.  Several of the supplied stills carry regions that the
brief rules out - the prompt text that leaked into the render, a fabricated
Indian Air Force crest, a Government of India branded interface, a tricolour
emblem.  Rather than discard whole images, each one declares the rectangle that
is actually usable, and only that rectangle ever reaches the screen.  See
ASSETS below: every entry says what was excluded and why.

Second, a common grade.  The stills come from two different generators and the
clips from a third source, so they arrive with clashing colour.  One grade over
all of them, tuned to the same palette as the motion graphics, is what makes the
cuts feel like one film instead of a slideshow.
"""
from __future__ import annotations

import os

import numpy as np
from PIL import Image

from design import H, W, ease_in_out, lerp

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(HERE)
CACHE = os.path.join(HERE, "build", "cache")

IMG_DIR = os.path.join(REPO, "Image")
VID_DIR = os.path.join(REPO, "Video")


# --------------------------------------------------------------- the catalogue
# crop is (x0, y0, x1, y1) in normalised source coordinates.
ASSETS = {
    # ---- stills, used in full ------------------------------------------------
    "tracks_sky": dict(
        file="ChatGPT Image Sep 22, 2026, 08_23_52 PM.png",
        crop=(0.0, 0.0, 1.0, 0.42),
        note="Night sky dense with drone tracks over a skyline. Generic counters, "
             "no official branding - used as-is.",
    ),
    "classify": dict(
        file="ChatGPT Image Sep 22, 2026, 08_23_52 PM.png",
        crop=(0.33, 0.44, 0.99, 0.605),
        note="The threat-alert cell of a three-stage classification panel. "
             "Generic illustrative UI, no official branding. Used as an inset, "
             "never full frame - the source cell is 3:1 and filling 9:16 from "
             "it would magnify the baked label past legibility.",
    ),
    "operator_wall": dict(
        file="ChatGPT Image Sep 22, 2026, 08_23_52 PM.png",
        crop=(0.0, 0.60, 1.0, 1.0),
        note="Operator silhouette at a console wall.",
    ),
    "airliner": dict(
        file="ChatGPT Image Sep 22, 2026, 08_25_42 PM.png",
        crop=(0.17, 0.045, 0.93, 0.335),
        note="Airliner on approach. Cropped in from the flight-data column.",
    ),
    "infrastructure": dict(
        file="ChatGPT Image Sep 22, 2026, 08_25_42 PM.png",
        crop=(0.14, 0.395, 0.98, 0.655),
        note="Refinery and grid at night. Cropped past the left icon rail.",
    ),
    "response": dict(
        file="ChatGPT Image Sep 22, 2026, 08_25_42 PM.png",
        crop=(0.06, 0.695, 0.86, 0.905),
        note="Emergency response on a city street. Cropped past the right icon "
             "rail and the inset map.",
    ),
    "desert_range": dict(
        file="Gemini_Generated_Image_ib64u2ib64u2ib64.png",
        crop=(0.0, 0.10, 1.0, 0.88),
        note="Desert test range with radar vehicles and shelters. Clean plate, "
             "no text anywhere. Bottom edge trimmed to drop the generator "
             "watermark.",
    ),

    # ---- stills used only in part -------------------------------------------
    "rotor": dict(
        file="ChatGPT Image Sep 22, 2026, 08_22_17 PM.png",
        crop=(0.34, 0.0, 1.0, 0.30),
        note="EXCLUDES the lower half and the left of the frame. The airframe "
             "carries a fabricated 'INDIAN ARMED FORCES' marking and a flag "
             "decal, and the lower half is a system graphic with 'VAYU UTTAM' "
             "baked into it. Only the bare rotor is used.",
    ),
    "city_drones": dict(
        file="Gemini_Generated_Image_laxnivlaxnivlaxn.png",
        crop=(0.0, 0.135, 1.0, 0.545),
        note="EXCLUDES the top of the frame, where the image generator printed "
             "the prompt text into the render.",
    ),
    "mountain_uav": dict(
        file="Gemini_Generated_Image_laxnivlaxnivlaxn.png",
        crop=(0.0, 0.585, 1.0, 0.985),
        note="Fixed-wing UAV over mountains. Same image, lower frame.",
    ),
    "field_tablet": dict(
        file="Gemini_Generated_Image_1ugihz1ugihz1ugi.png",
        crop=(0.0, 0.30, 1.0, 0.97),
        note="EXCLUDES the top of the frame, where the generator printed the "
             "prompt text.",
    ),
    "jet_high": dict(
        file="Gemini_Generated_Image_22a72622a72622a7.png",
        crop=(0.0, 0.128, 1.0, 0.298),
        note="EXCLUDES the printed prompt text above, and the tricolour shield "
             "emblem below.",
    ),
    "drone_formation": dict(
        file="Gemini_Generated_Image_22a72622a72622a7.png",
        crop=(0.0, 0.625, 1.0, 0.965),
        note="Formation of craft. Same image, below the emblem; bottom trimmed "
             "to drop the generator watermark.",
    ),
}

# Supplied images deliberately NOT used anywhere, and why.
EXCLUDED = {
    "ChatGPT Image Sep 22, 2026, 08_33_08 PM.png":
        "Fabricates an Indian Air Force crest and banner and an official-looking "
        "'Vayu UTtaM' system display. The brief rules out fake insignia and fake "
        "official interfaces, so this one is unusable rather than croppable.",
    "Gemini_Generated_Image_1ugihz1ugihz1ugi.png (upper frame)":
        "A 'Government of India / National Airspace Monitoring' branded interface. "
        "Fabricated government branding - excluded by crop.",
    "ChatGPT Image Sep 22, 2026, 08_26_47 PM.png":
        "Tricolour shield emblem, 'Indian Defence Ecosystem' lockup and a soldier "
        "silhouetted against a flag. Quasi-official emblem plus a propaganda "
        "register the brief asks to avoid.",
    "ChatGPT Image Sep 22, 2026, 08_28_28 PM.png":
        "Large fabricated tricolour shield emblem over an India map. Same reason.",
}

CLIPS = {
    "city_fpv": dict(
        file="Fast_forward_FPV_drone_shot_sw.mp4", start=0.2, end=4.6,
        crop=(0.18, 0.0, 0.82, 1.0),
        note="FPV run over a city at dusk. Source is 16:9, so a centre column is "
             "taken for 9:16 rather than letterboxing.",
    ),
    "city_hud": dict(
        file="Fast_forward_FPV_drone_shot_sw.mp4", start=5.4, end=9.8,
        crop=(0.20, 0.0, 0.80, 1.0),
        note="The same run resolving into a wireframe tracking view.",
    ),
    "city_dusk": dict(
        file="make_this_clip_without_any_sou.mp4", start=0.3, end=5.0,
        crop=(0.0, 0.0, 1.0, 0.93),
        note="City at dusk, already 9:16. Bottom trimmed to drop the watermark.",
    ),
    "city_night": dict(
        file="make_this_clip_without_any_sou.mp4", start=5.4, end=9.9,
        crop=(0.0, 0.0, 1.0, 0.93),
        note="Same clip, later - city at night.",
    ),
    "console": dict(
        file="make_this_clip_without_any_sou.mp4", start=10.4, end=14.9,
        crop=(0.0, 0.0, 1.0, 0.93),
        note="Operator at radar consoles.",
    ),
    "crew": dict(
        file="make_this_clip_without_any_sou.mp4", start=15.3, end=19.9,
        crop=(0.0, 0.0, 1.0, 0.93),
        note="Crew at stations.",
    ),
}


# ------------------------------------------------------------------- grading
def grade(arr, strength=1.0, cool=1.0, lift=1.0):
    """One documentary grade for every source, so the cuts match.

    Slight desaturation, a soft S-curve, cool shadows and a touch of warmth in
    the highlights - the same teal/amber relationship the graphics use.
    """
    x = arr / 255.0

    lum = (x[:, :, 0] * 0.299 + x[:, :, 1] * 0.587 + x[:, :, 2] * 0.114)[:, :, None]
    x = lerp(x, lum, 0.26 * strength)

    x = np.clip(x, 0.0, 1.0)
    x = x * x * (3 - 2 * x) * 0.55 + x * 0.45          # gentle S-curve

    shadow = np.clip(1.0 - lum * 2.1, 0, 1)
    high = np.clip(lum * 1.7 - 0.55, 0, 1)
    x[:, :, 0] += (-0.020 * shadow[:, :, 0] + 0.016 * high[:, :, 0]) * cool
    x[:, :, 1] += (0.004 * shadow[:, :, 0] + 0.006 * high[:, :, 0]) * cool
    x[:, :, 2] += (0.034 * shadow[:, :, 0] - 0.012 * high[:, :, 0]) * cool

    x = x * 0.955 + np.array([0.016, 0.022, 0.030], dtype=np.float32) * lift
    return np.clip(x, 0, 1) * 255.0


# ------------------------------------------------------------- stills / clips
_IMG_CACHE: dict = {}


def _load_still(key):
    if key in _IMG_CACHE:
        return _IMG_CACHE[key]
    spec = ASSETS[key]
    im = Image.open(os.path.join(IMG_DIR, spec["file"])).convert("RGB")
    x0, y0, x1, y1 = spec["crop"]
    w, h = im.size
    im = im.crop((int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h)))
    _IMG_CACHE[key] = im
    return im


def _cover(im, f, cx=0.5, cy=0.5, zoom=1.0):
    """Fill 1080x1920 from a source of any shape - crop, never letterbox.

    `f` is the extra headroom left for the Ken Burns move; zoom rides on top.
    """
    sw, sh = im.size
    scale = max(W / sw, H / sh) * f * zoom
    nw, nh = max(W, int(round(sw * scale))), max(H, int(round(sh * scale)))
    im = im.resize((nw, nh), Image.LANCZOS)
    ox = int(round((nw - W) * cx))
    oy = int(round((nh - H) * cy))
    ox = max(0, min(ox, nw - W))
    oy = max(0, min(oy, nh - H))
    return im.crop((ox, oy, ox + W, oy + H))


def still(key, t, dur, zoom=(1.06, 1.14), pan=((0.5, 0.5), (0.5, 0.5)), grade_kw=None):
    """A still with a Ken Burns move, filled to frame and graded."""
    im = _load_still(key)
    f = ease_in_out(t / max(dur, 1e-6))
    z = lerp(zoom[0], zoom[1], f)
    cx = lerp(pan[0][0], pan[1][0], f)
    cy = lerp(pan[0][1], pan[1][1], f)
    out = _cover(im, 1.0, cx, cy, z)
    return grade(np.asarray(out, dtype=np.float32), **(grade_kw or {}))


_CLIP_INDEX: dict = {}


def clip_frames(key):
    if key in _CLIP_INDEX:
        return _CLIP_INDEX[key]
    d = os.path.join(CACHE, key)
    frames = sorted(os.listdir(d)) if os.path.isdir(d) else []
    if not frames:
        raise SystemExit(f"clip cache missing for {key!r} - run: python3 src/prep_media.py")
    _CLIP_INDEX[key] = (d, frames)
    return _CLIP_INDEX[key]


def clip(key, t, dur, zoom=(1.0, 1.06), pan=((0.5, 0.5), (0.5, 0.5)), grade_kw=None,
         loop=True):
    """A cached clip frame at scene-local time t, with an optional slow push."""
    d, frames = clip_frames(key)
    src_fps = 24.0
    i = int(t * src_fps)
    i = i % len(frames) if loop else min(i, len(frames) - 1)
    im = Image.open(os.path.join(d, frames[i])).convert("RGB")

    f = ease_in_out(t / max(dur, 1e-6))
    z = lerp(zoom[0], zoom[1], f)
    cx = lerp(pan[0][0], pan[1][0], f)
    cy = lerp(pan[0][1], pan[1][1], f)
    out = _cover(im, 1.0, cx, cy, z)
    return grade(np.asarray(out, dtype=np.float32), **(grade_kw or {}))


def manifest():
    """What was used, what was cropped out, what was dropped - for the README."""
    return dict(stills=ASSETS, clips=CLIPS, excluded=EXCLUDED)
