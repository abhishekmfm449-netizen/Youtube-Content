"""Palette, type ramp and low-level drawing primitives.

Everything renders into RGB numpy arrays at RENDER scale and is downsampled once
per frame, which is what keeps the vector art clean without a real 2D engine.
"""
from __future__ import annotations

import json
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
FPS = 30
SS = 2                      # supersample factor for vector layers
RW, RH = W * SS, H * SS

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(HERE, "assets", "fonts")
GEO = os.path.join(HERE, "assets", "geo", "india_outline.json")

# Shorts safe area.  YouTube's own chrome (title, channel, action rail) eats the
# bottom of the frame, so nothing that carries meaning goes below SAFE_BOTTOM.
SAFE_TOP = int(H * 0.055)
SAFE_BOTTOM = int(H * 0.835)
SAFE_X = 84

# The caption band is reserved: scene furniture must stay above CAP_TOP so
# burned-in subtitles never cover a label, a counter or the subject of a shot.
CAP_TOP = 0.655
CAP_MID = 0.735

# ------------------------------------------------------------------- palette
# Restrained, desaturated, documentary.  One cool system accent, one warm
# caution accent, no neon.
BG_TOP = (7, 11, 17)
BG_BOT = (13, 20, 29)
INK = (233, 240, 247)
INK_DIM = (139, 156, 173)
INK_FAINT = (74, 90, 106)

SYS = (86, 190, 204)        # system / authorised - muted teal-cyan
SYS_DEEP = (36, 96, 112)
CAUTION = (226, 160, 62)    # unidentified - amber, deliberately not red
GRID = (36, 52, 68)
HORIZON_WARM = (168, 118, 72)
SAND_DARK = (46, 37, 31)


def font(name: str, size: int, wght: float | None = None) -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    if wght is not None:
        try:
            axes = f.get_variation_axes()
            vals = []
            for ax in axes:
                nm = (ax["name"] or b"").decode(errors="ignore").lower()
                vals.append(wght if "weight" in nm else ax["default"])
            f.set_variation_by_axes(vals)
        except Exception:
            pass
    return f


# Type ramp, in render-space pixels (i.e. already multiplied by SS at call time).
def f_title(sz: int):    return font("BarlowCondensed-Bold.ttf", sz)
def f_sub(sz: int):      return font("BarlowCondensed-SemiBold.ttf", sz)
def f_mono(sz: int, w=500): return font("JetBrainsMono.ttf", sz, w)
def f_caption(sz: int, w=800): return font("Montserrat.ttf", sz, w)


# ------------------------------------------------------------------- helpers
def ease_out(t: float, p: float = 3.0) -> float:
    t = min(max(t, 0.0), 1.0)
    return 1.0 - (1.0 - t) ** p


def ease_in_out(t: float) -> float:
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def smooth01(x: float, a: float, b: float) -> float:
    """Ramp 0->1 as x travels a->b, clamped."""
    if b <= a:
        return 1.0 if x >= b else 0.0
    return ease_in_out((x - a) / (b - a))


def lerp(a, b, t):
    return a + (b - a) * t


def mix(c1, c2, t: float):
    t = min(max(t, 0.0), 1.0)
    return tuple(int(round(lerp(c1[i], c2[i], t))) for i in range(3))


def new_layer(size=None) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    im = Image.new("RGBA", size or (RW, RH), (0, 0, 0, 0))
    d = ImageDraw.Draw(im, "RGBA")
    d._image = im          # so helpers can composite onto the layer, not just draw
    return im, d


_GRAD_CACHE: dict = {}


def vgradient(top, bot, size=None) -> np.ndarray:
    key = (tuple(top), tuple(bot), tuple(size) if size else None)
    hit = _GRAD_CACHE.get(key)
    if hit is not None:
        return hit.copy()
    w, h = size or (W, H)
    t = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None]
    g = np.zeros((h, w, 3), dtype=np.float32)
    for i in range(3):
        g[:, :, i] = lerp(float(top[i]), float(bot[i]), t)
    _GRAD_CACHE[key] = g
    return g.copy()


_VIG_CACHE: dict = {}


def vignette(img: np.ndarray, strength: float = 0.55, power: float = 1.7) -> np.ndarray:
    h, w = img.shape[:2]
    key = (h, w, round(strength, 4), round(power, 4))
    v = _VIG_CACHE.get(key)
    if v is None:
        y, x = np.mgrid[0:h, 0:w].astype(np.float32)
        dx = (x - w / 2) / (w / 2)
        dy = (y - h / 2) / (h / 2)
        r = np.sqrt(dx * dx + dy * dy * 0.62)
        v = (1.0 - strength * np.clip(r, 0, 1.6) ** power)[:, :, None]
        _VIG_CACHE[key] = v
    return img * v


_GRAIN_BANK: dict = {}
_GRAIN_N = 12


def grain(img: np.ndarray, amount: float, seed: int) -> np.ndarray:
    """Film grain from a small pre-rolled bank, cycled by frame.

    Generating fresh gaussian noise per frame cost more than the rest of the
    composite put together; a 12-frame bank is indistinguishable in motion.
    """
    h, w = img.shape[:2]
    key = (h, w)
    bank = _GRAIN_BANK.get(key)
    if bank is None:
        rng = np.random.default_rng(20260922)
        bank = []
        for _ in range(_GRAIN_N):
            n = rng.normal(0.0, 1.0, (h // 2, w // 2, 1)).astype(np.float32)
            bank.append(np.repeat(np.repeat(n, 2, axis=0), 2, axis=1)[:h, :w])
        _GRAIN_BANK[key] = bank
    img += bank[seed % _GRAIN_N] * (amount * 255.0)
    return img


def composite(base: np.ndarray, layer, downsample: bool = True) -> np.ndarray:
    """Alpha-composite an RGBA layer onto a 1080x1920 float array, in place.

    `layer` is either a full-frame RGBA image or the (image, offset) pair that
    `resolve` returns, in which case only that sub-rectangle is touched.  Most
    overlays cover a small slice of the frame, so blending just their bounding
    box is a large saving over blending 2 megapixels every time.
    """
    off = (0, 0)
    if isinstance(layer, tuple):
        layer, off = layer
    if layer is None:
        return base
    if downsample and layer.size != (W, H) and off == (0, 0):
        layer = layer.resize((W, H), Image.LANCZOS)

    ox, oy = off
    lw, lh = layer.size
    la = np.asarray(layer, dtype=np.float32)
    a = la[:, :, 3:4] * (1.0 / 255.0)
    view = base[oy:oy + lh, ox:ox + lw]
    view *= (1.0 - a)
    view += la[:, :, :3] * a
    return base


def to_image(arr: np.ndarray) -> Image.Image:
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


# --------------------------------------------------------------- primitives
def dashed_circle(d: ImageDraw.ImageDraw, cx, cy, r, color, width, dashes=48, phase=0.0,
                  duty=0.55):
    step = 2 * math.pi / dashes
    for i in range(dashes):
        a0 = i * step + phase
        a1 = a0 + step * duty
        d.arc([cx - r, cy - r, cx + r, cy + r],
              math.degrees(a0), math.degrees(a1), fill=color, width=width)


def crosshair(d, x, y, s, color, width, gap=None):
    gap = gap or s * 0.42
    d.line([x - s, y, x - gap, y], fill=color, width=width)
    d.line([x + gap, y, x + s, y], fill=color, width=width)
    d.line([x, y - s, x, y - gap], fill=color, width=width)
    d.line([x, y + gap, x, y + s], fill=color, width=width)


def corner_box(d, x0, y0, x1, y1, color, width, arm=None):
    """HUD-style bracket - four corners, no full rectangle."""
    arm = arm or min(x1 - x0, y1 - y0) * 0.28
    for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        d.line([cx, cy, cx + arm * sx, cy], fill=color, width=width)
        d.line([cx, cy, cx, cy + arm * sy], fill=color, width=width)


def text(d, xy, s, fnt, color, anchor="la", alpha=255, track=0.0):
    """Draw text, optionally with letter tracking (PIL has no native tracking)."""
    col = color + (alpha,) if len(color) == 3 else color
    if not track:
        d.text(xy, s, font=fnt, fill=col, anchor=anchor)
        return
    widths = [d.textlength(ch, font=fnt) for ch in s]
    total = sum(widths) + track * (len(s) - 1)
    x, y = xy
    if anchor[0] == "m":
        x -= total / 2
    elif anchor[0] == "r":
        x -= total
    va = anchor[1]
    for ch, w in zip(s, widths):
        d.text((x, y), ch, font=fnt, fill=col, anchor="l" + va)
        x += w + track


def text_size(d, s, fnt, track=0.0):
    w = sum(d.textlength(ch, font=fnt) for ch in s) + track * max(0, len(s) - 1)
    bb = fnt.getbbox(s)
    return w, bb[3] - bb[1]


# ------------------------------------------------------------------ the map
_GEO_CACHE = None


def india_rings():
    global _GEO_CACHE
    if _GEO_CACHE is None:
        _GEO_CACHE = json.load(open(GEO))
    return _GEO_CACHE


def map_projector(cx, cy, scale):
    """Equirectangular with a cos(lat) correction at India's mid-latitude, so the
    outline keeps its true proportions instead of being stretched."""
    g = india_rings()
    lon0 = (g["bounds"]["lon"][0] + g["bounds"]["lon"][1]) / 2
    lat0 = (g["bounds"]["lat"][0] + g["bounds"]["lat"][1]) / 2
    k = math.cos(math.radians(lat0))

    def proj(lon, lat):
        return (cx + (lon - lon0) * k * scale, cy - (lat - lat0) * scale)

    return proj


def map_scale_for_height(px_height: float) -> float:
    g = india_rings()
    span = g["bounds"]["lat"][1] - g["bounds"]["lat"][0]
    return px_height / span


def draw_india(d, proj, outline=None, width=2, fill=None, rings=None, dash=0):
    """Draw the India outline, optionally filled.

    The fill goes onto a scratch layer and is alpha-composited back.  Drawing it
    straight onto `d` looks right but is not: ImageDraw writes a polygon's RGBA
    verbatim rather than blending it, so a translucent fill over a panel
    *replaces* the panel's alpha there and punches a hole through to whatever is
    underneath.  Lines and text do blend, which is why only the fill needs this.
    """
    g = india_rings()
    sel = g["rings"] if rings is None else [g["rings"][i] for i in rings]

    if fill:
        scratch = Image.new("RGBA", d.im.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(scratch, "RGBA")
        for ring in sel:
            pts = [proj(lon, lat) for lon, lat in ring]
            if len(pts) >= 3:
                sd.polygon(pts, fill=fill)
        d._image.alpha_composite(scratch)

    for ring in sel:
        pts = [proj(lon, lat) for lon, lat in ring]
        if len(pts) < 3:
            continue
        if outline:
            if dash:
                for i in range(0, len(pts) - 1, dash):
                    seg = pts[i:i + max(2, dash - 1)]
                    if len(seg) >= 2:
                        d.line(seg, fill=outline, width=width, joint="curve")
            else:
                d.line(pts + [pts[0]], fill=outline, width=width, joint="curve")


# A handful of real Indian cities, used only as neutral map anchors.
CITIES = [
    ("DELHI", 77.21, 28.61),
    ("MUMBAI", 72.88, 19.08),
    ("KOLKATA", 88.36, 22.57),
    ("CHENNAI", 80.27, 13.08),
    ("BENGALURU", 77.59, 12.97),
    ("JAISALMER", 70.91, 26.91),
    ("HYDERABAD", 78.49, 17.39),
    ("AHMEDABAD", 72.57, 23.02),
    ("LUCKNOW", 80.95, 26.85),
    ("GUWAHATI", 91.74, 26.14),
    ("NAGPUR", 79.09, 21.15),
    ("KOCHI", 76.27, 9.93),
    ("BHOPAL", 77.41, 23.26),
    ("PATNA", 85.14, 25.59),
    ("JAIPUR", 75.79, 26.91),
    ("SRINAGAR", 74.80, 34.08),
    ("VISAKHAPATNAM", 83.30, 17.69),
    ("PUNE", 73.86, 18.52),
]

POKHRAN = (71.92, 26.92)


def resolve(layer: Image.Image, bloom: float = 0.0, gain: float = 1.0):
    """Crop a render-scale layer to what it actually draws, downsample, bloom.

    Returns an (image, offset) pair for `composite`.  Three things matter here
    for speed: `reduce` is a true box downsample and far cheaper than LANCZOS at
    an exact integer factor; cropping to the ink means an overlay that is 95%
    empty costs 5% of a full frame; and the bloom then runs on the crop only.
    """
    bb = layer.getbbox()
    if bb is None:
        return None, (0, 0)

    pad = int(max(2, bloom * 2.5) * SS)
    x0 = max(0, (bb[0] - pad) // SS * SS)
    y0 = max(0, (bb[1] - pad) // SS * SS)
    x1 = min(layer.size[0], -(-(bb[2] + pad) // SS) * SS)
    y1 = min(layer.size[1], -(-(bb[3] + pad) // SS) * SS)

    crop = layer.crop((x0, y0, x1, y1))
    small = crop.reduce(SS) if SS > 1 else crop

    if bloom > 0:
        b = small.filter(ImageFilter.GaussianBlur(bloom))
        if gain != 1.0:
            b.putalpha(b.split()[3].point(lambda v: min(255, int(v * gain))))
        small = Image.alpha_composite(b, small)
    return small, (x0 // SS, y0 // SS)


def sweep_out(cx, cy, r, angle, color, span=1.05, steps=44, alpha=110, bloom=6.0):
    """Radar sweep rendered straight at output resolution.

    The sweep is a soft gradient wedge with no hard edges, so supersampling it
    buys nothing - and at render scale it was the single most expensive draw in
    the frame.  Coordinates come in render-space and are scaled down here.
    """
    # Drawn at half output resolution and scaled up: the sweep is a soft
    # gradient with no hard edges, so the detail is not there to lose, and the
    # two blur passes then cost a quarter as much.
    q = 2
    cx, cy, r = cx / SS / q, cy / SS / q, r / SS / q
    im = Image.new("RGBA", (W // q, H // q), (0, 0, 0, 0))
    d = ImageDraw.Draw(im, "RGBA")
    for i in range(steps):
        f = i / (steps - 1)
        a1 = angle - span * f
        a0 = a1 - span / steps * 1.6
        a = int(alpha * (1.0 - f) ** 2.1)
        if a <= 1:
            continue
        d.pieslice([cx - r, cy - r, cx + r, cy + r],
                   math.degrees(a0), math.degrees(a1), fill=color + (a,))
    d.line([cx, cy, cx + r * math.cos(angle), cy + r * math.sin(angle)],
           fill=color + (200,), width=1)
    if bloom:
        im = im.filter(ImageFilter.GaussianBlur(bloom / q / 2))
    return im.resize((W, H), Image.BILINEAR)
