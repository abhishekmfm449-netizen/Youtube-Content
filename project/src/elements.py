"""Reusable visual elements.

Every element here is generic, illustrative motion graphics.  Nothing imitates a
real interface, insignia, document or aircraft type, which is deliberate: the
subject is factual and the visuals must not read as operational footage.
"""
from __future__ import annotations

import math

import numpy as np

from design import INK, INK_FAINT, RH, RW, SS, f_mono, lerp, text

# Re-exported so scenes can reach every drawing helper through one namespace.
from design import corner_box, crosshair

__all__ = ["corner_box", "crosshair", "haze_band", "quadcopter", "drone_dot", "Track",
           "draw_track", "make_tracks", "illustration_mark", "stat_chip", "skyline_band",
           "pylon", "runway"]


# ----------------------------------------------------------------- airspace
def haze_band(arr, y0, y1, color, strength):
    """Soft atmospheric band - cheap depth."""
    h, w = arr.shape[:2]
    y = np.arange(h, dtype=np.float32)[:, None]
    m = np.clip(1.0 - np.abs((y - (y0 + y1) / 2) / max(1.0, (y1 - y0) / 2)), 0, 1) ** 1.6
    return arr + m[:, :, None] * np.array(color, dtype=np.float32) * strength


# -------------------------------------------------------------------- icons
def quadcopter(d, x, y, s, color, alpha=255, spin=0.0, width=None):
    """Civilian / commercial quadcopter, plan view."""
    w = width or max(1, int(1.7 * SS * s / 30))
    c = color + (alpha,)
    arm = s * 0.72
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        ax, ay = x + arm * math.cos(a), y + arm * math.sin(a) * 0.86
        d.line([x, y, ax, ay], fill=c, width=w)
        r = s * 0.34
        d.ellipse([ax - r, ay - r * 0.86, ax + r, ay + r * 0.86],
                  outline=color + (int(alpha * 0.55),), width=max(1, w - int(0.4 * SS)))
        # rotor blur streak
        b = spin + k * 1.1
        d.arc([ax - r, ay - r * 0.86, ax + r, ay + r * 0.86],
              math.degrees(b), math.degrees(b) + 130, fill=color + (alpha,), width=w)
    d.rounded_rectangle([x - s * 0.24, y - s * 0.17, x + s * 0.24, y + s * 0.17],
                        radius=s * 0.09, fill=c)


def drone_dot(d, x, y, r, color, alpha=255, ring=True):
    d.ellipse([x - r, y - r, x + r, y + r], fill=color + (alpha,))
    if ring:
        rr = r * 2.5
        d.ellipse([x - rr, y - rr, x + rr, y + rr],
                  outline=color + (int(alpha * 0.45),), width=max(1, int(1.2 * SS)))


# ------------------------------------------------------------------- tracks
class Track:
    """A drone track: a path, a moving head, a fading trail, an optional label."""

    def __init__(self, pts, speed, phase, color, label=None, kind="auth", seed=0):
        self.pts = pts
        self.speed = speed
        self.phase = phase
        self.color = color
        self.label = label
        self.kind = kind
        self.seed = seed

    def pos(self, t):
        u = (self.phase + t * self.speed) % 1.0
        n = len(self.pts) - 1
        i = min(int(u * n), n - 1)
        f = u * n - i
        (x0, y0), (x1, y1) = self.pts[i], self.pts[i + 1]
        return lerp(x0, x1, f), lerp(y0, y1, f)

    def trail(self, t, span=0.16, steps=16):
        out = []
        for k in range(steps):
            tt = t - span * (k / steps) / max(self.speed, 1e-6) * self.speed
            u = (self.phase + tt * self.speed) % 1.0
            n = len(self.pts) - 1
            i = min(int(u * n), n - 1)
            f = u * n - i
            (x0, y0), (x1, y1) = self.pts[i], self.pts[i + 1]
            out.append((lerp(x0, x1, f), lerp(y0, y1, f)))
        return out


def draw_track(d, tr, t, alpha=255, head_r=None, show_label=False, label_alpha=255,
               trail_width=None, fnt=None):
    head_r = head_r or 4.2 * SS
    trail_width = trail_width or int(2.0 * SS)
    pts = tr.trail(t)
    for k in range(len(pts) - 1):
        a = int(alpha * (1.0 - k / len(pts)) ** 1.8 * 0.72)
        if a < 3:
            continue
        d.line([pts[k], pts[k + 1]], fill=tr.color + (a,), width=trail_width)
    x, y = pts[0]
    d.ellipse([x - head_r, y - head_r, x + head_r, y + head_r], fill=tr.color + (alpha,))
    d.ellipse([x - head_r * 2.4, y - head_r * 2.4, x + head_r * 2.4, y + head_r * 2.4],
              outline=tr.color + (int(alpha * 0.5),), width=max(1, int(1.3 * SS)))
    if show_label and tr.label and fnt is not None:
        lx, ly = x + head_r * 3.4, y - head_r * 3.0
        d.line([x + head_r * 1.8, y - head_r * 1.4, lx - 6 * SS, ly + 9 * SS],
               fill=tr.color + (int(label_alpha * 0.6),), width=max(1, int(1.2 * SS)))
        text(d, (lx, ly), tr.label, fnt, tr.color, alpha=label_alpha, track=1.0 * SS)


def make_tracks(n, seed, x0, y0, x1, y1, color, speed=(0.05, 0.13), segs=5):
    rng = np.random.default_rng(seed)
    out = []
    for i in range(n):
        ax, ay = rng.uniform(x0, x1), rng.uniform(y0, y1)
        ang = rng.uniform(0, 2 * math.pi)
        length = rng.uniform(0.35, 0.95) * (x1 - x0)
        pts = [(ax, ay)]
        for s in range(segs):
            ang += rng.uniform(-0.55, 0.55)
            ax += math.cos(ang) * length / segs
            ay += math.sin(ang) * length / segs * 0.55
            pts.append((ax, ay))
        out.append(Track(pts, float(rng.uniform(*speed)), float(rng.random()), color,
                         label=f"UA-{rng.integers(1000, 9999)}", seed=int(rng.integers(1e6))))
    return out


# ------------------------------------------------------------- HUD / chrome
def illustration_mark(d, alpha=200, y=None):
    """Standing notice that the graphics are illustrative, not a real system
    display.  Small, low-contrast, always present on interface-like scenes."""
    fnt = f_mono(19 * SS, 500)
    y = y or RH * 0.646
    text(d, (RW / 2, y), "ILLUSTRATIVE VISUALISATION — NOT AN ACTUAL SYSTEM DISPLAY",
         fnt, INK_FAINT, anchor="ma", alpha=alpha, track=1.6 * SS)


def stat_chip(d, x, y, w, h, title, value, color, alpha=255, fnt_t=None, fnt_v=None):
    d.rounded_rectangle([x, y, x + w, y + h], radius=8 * SS,
                        fill=(color[0], color[1], color[2], int(alpha * 0.10)),
                        outline=color + (int(alpha * 0.55),), width=int(1.5 * SS))
    text(d, (x + 18 * SS, y + h * 0.26), title, fnt_t, color, anchor="lm",
         alpha=int(alpha * 0.85), track=2.0 * SS)
    text(d, (x + 18 * SS, y + h * 0.68), value, fnt_v, INK, anchor="lm", alpha=alpha)


def skyline_band(d, ybase, height, color, alpha, seed, width=RW, density=26, phase=0.0):
    rng = np.random.default_rng(seed)
    x = -rng.random() * 120 * SS + phase
    while x < width:
        bw = rng.uniform(26, 92) * SS
        bh = rng.uniform(0.25, 1.0) ** 1.5 * height
        d.rectangle([x, ybase - bh, x + bw, RH + 10], fill=color + (alpha,))
        # a few lit windows
        if rng.random() < 0.65:
            for _ in range(int(rng.integers(1, 6))):
                wx = x + rng.uniform(0.15, 0.8) * bw
                wy = ybase - rng.uniform(0.1, 0.9) * bh
                ws = rng.uniform(2.0, 4.0) * SS
                d.rectangle([wx, wy, wx + ws, wy + ws * 1.6],
                            fill=(226, 190, 140, int(alpha * rng.uniform(0.35, 0.9))))
        x += bw + rng.uniform(8, 46) * SS


def pylon(d, x, ybase, h, color, alpha, width=None):
    """Transmission tower - the 'critical infrastructure' read."""
    w = width or int(2.0 * SS)
    c = color + (alpha,)
    halfb, halft = h * 0.20, h * 0.055
    d.line([x - halfb, ybase, x - halft, ybase - h], fill=c, width=w)
    d.line([x + halfb, ybase, x + halft, ybase - h], fill=c, width=w)
    for k, fy in enumerate((0.52, 0.72, 0.9)):
        y = ybase - h * fy
        arm = lerp(halfb, halft, fy) + h * (0.17 - k * 0.028)
        d.line([x - arm, y, x + arm, y], fill=c, width=w)
    # cross bracing
    for k in range(5):
        y0 = ybase - h * k / 5
        y1 = ybase - h * (k + 1) / 5
        s0 = lerp(halfb, halft, k / 5)
        s1 = lerp(halfb, halft, (k + 1) / 5)
        d.line([x - s0, y0, x + s1, y1], fill=color + (int(alpha * 0.7),), width=max(1, w - SS))
        d.line([x + s0, y0, x - s1, y1], fill=color + (int(alpha * 0.7),), width=max(1, w - SS))


def runway(d, cx, ytop, ybot, halfw_top, halfw_bot, color, alpha, dashes=9, phase=0.0):
    d.polygon([(cx - halfw_top, ytop), (cx + halfw_top, ytop),
               (cx + halfw_bot, ybot), (cx - halfw_bot, ybot)],
              fill=color + (int(alpha * 0.30),))
    d.line([cx - halfw_top, ytop, cx - halfw_bot, ybot], fill=color + (alpha,), width=int(2 * SS))
    d.line([cx + halfw_top, ytop, cx + halfw_bot, ybot], fill=color + (alpha,), width=int(2 * SS))
    for i in range(dashes):
        f0 = (i + phase % 1.0) / dashes
        f1 = f0 + 0.055
        if f1 > 1:
            continue
        y0, y1 = lerp(ytop, ybot, f0), lerp(ytop, ybot, f1)
        w0 = lerp(halfw_top, halfw_bot, f0) * 0.05
        w1 = lerp(halfw_top, halfw_bot, f1) * 0.05
        d.polygon([(cx - w0, y0), (cx + w0, y0), (cx + w1, y1), (cx - w1, y1)],
                  fill=color + (int(alpha * 0.9),))


