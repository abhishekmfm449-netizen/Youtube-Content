"""The fourteen scenes.

Each renderer takes local time `t` and the scene's duration, and returns a
1080x1920 float32 RGB array.  Camera moves, reveals and counters are functions
of `t`, so the edit re-times itself if the narration changes.

The construction is the same everywhere: supplied footage underneath, rendered
motion graphics and typography on top.  Footage carries the reality, graphics
carry the argument.  Nothing is generated here that the supplied assets already
provide.

House rules enforced in this file and in media.py:
  * nothing imitates a real system display, document, logo or insignia
  * no fabricated official interfaces reach the screen - see media.EXCLUDED
  * the India outline is the official boundary, drawn undistorted
  * typography is always rendered in post, never baked into an image
  * no explosions, no weapons, no attack imagery
"""
from __future__ import annotations

import math

import numpy as np
from PIL import Image

import elements as E
import media as M
from design import (CAUTION, CITIES, H, INK, INK_DIM, INK_FAINT, RH, RW, SS, SYS, SYS_DEEP,
                    W, composite, dashed_circle, draw_india, ease_in_out, ease_out, f_mono,
                    f_sub, f_title, grain, lerp, map_projector, map_scale_for_height, mix,
                    new_layer, resolve, smooth01, sweep_out, text, text_size, vgradient,
                    vignette)


# --------------------------------------------------------------- scene utils
def finish(arr, t, seed, vig=0.42, gr=0.0038):
    arr = vignette(arr, vig)
    return grain(arr, gr, seed + int(t * 30))


def dissolve(a, b, f):
    f = ease_in_out(f)
    return a * (1 - f) + b * f


def title_block(d, cx, y, main, sub=None, t=0.0, t0=0.0, size=126, sub_size=40,
                color=INK, sub_color=SYS, rule=True):
    """Post-production typography: a rule wipes, then the words rise in."""
    a = smooth01(t, t0, t0 + 0.45)
    if a <= 0.001:
        return
    slide = (1 - ease_out(a, 2.4)) * 26 * SS
    fnt = f_title(size * SS)
    if rule:
        w = text_size(d, main, fnt, track=3 * SS)[0]
        rw = w * smooth01(t, t0, t0 + 0.55)
        d.line([cx - rw / 2, y - 26 * SS, cx + rw / 2, y - 26 * SS],
               fill=SYS + (int(190 * a),), width=int(3 * SS))
    text(d, (cx, y + slide), main, fnt, color, anchor="ma", alpha=int(255 * a), track=3 * SS)
    if sub:
        a2 = smooth01(t, t0 + 0.30, t0 + 0.80)
        text(d, (cx, y + size * SS * 1.02), sub, f_sub(sub_size * SS), sub_color,
             anchor="ma", alpha=int(230 * a2), track=7 * SS)


def scrim(d, y0f, y1f, alpha=150, fade=0.18):
    """A soft dark gradient behind type that sits over busy footage.

    Cheaper and less heavy-handed than a box, and it keeps the caption and title
    contrast predictable no matter what the shot underneath is doing.
    """
    y0, y1 = RH * y0f, RH * y1f
    span = y1 - y0
    steps = 26
    for i in range(steps):
        f = i / (steps - 1)
        edge = min(f / fade, (1 - f) / fade, 1.0)
        d.rectangle([0, y0 + span * f, RW, y0 + span * (f + 1 / steps) + 1],
                    fill=(4, 7, 11, int(alpha * max(0.0, edge))))


def tag(d, y, s, alpha=255, color=INK_DIM, size=32):
    text(d, (RW / 2, RH * y), s, f_sub(size * SS), color, anchor="ma", alpha=alpha,
         track=8 * SS)


# ------------------------------------------------------------------ SCENE 1
def scene1(t, dur):
    """HOOK - the city below, then the air picture switches on above it."""
    arr = M.clip("city_dusk", t, dur, zoom=(1.02, 1.12), pan=((0.5, 0.55), (0.5, 0.42)))

    im, d = new_layer()
    cx, cy = RW * 0.5, RH * 0.40
    ring_a = smooth01(t, 0.10, 0.95)
    for k, r in enumerate((0.22, 0.37, 0.52)):
        dashed_circle(d, cx, cy, RW * r, SYS + (int(70 * ring_a),), int(1.6 * SS),
                      dashes=60, phase=t * 0.12 * (1 + k * 0.3))

    ang = -math.pi / 2 + t * 2.1
    proj = map_projector(cx, cy, map_scale_for_height(RH * 0.30))
    reveal = smooth01(t, 0.35, 1.7)
    draw_india(d, proj, outline=SYS + (int(150 * reveal),), width=int(2.0 * SS))

    # contacts light up behind the beam
    rng = np.random.default_rng(7)
    lit = 0
    for _name, lon, lat in CITIES:
        x, y = proj(lon, lat)
        x += rng.uniform(-26, 26) * SS
        y += rng.uniform(-26, 26) * SS
        delta = (ang - math.atan2(y - cy, x - cx)) % (2 * math.pi)
        if delta < 3.4 and t > 0.30:
            a = int(225 * max(0.0, 1.0 - delta / 3.4) * reveal)
            if a > 4:
                lit += 1
                E.drone_dot(d, x, y, 3.6 * SS, SYS, a)

    arr = composite(arr, sweep_out(cx, cy, RW * 0.55, ang, SYS, alpha=int(52 * ring_a)),
                    downsample=False)
    arr = composite(arr, resolve(im, bloom=6, gain=1.45))

    ov, od = new_layer()
    scrim(od, 0.0, 0.20, 170)
    tag(od, 0.072, "INDIAN AIRSPACE", int(225 * smooth01(t, 0.45, 1.0)))
    text(od, (RW / 2, RH * 0.072 + 52 * SS), f"CONTACTS  {lit:02d}", f_mono(26 * SS, 600),
         SYS, anchor="ma", alpha=int(200 * smooth01(t, 0.8, 1.3)), track=2 * SS)
    arr = composite(arr, resolve(ov, bloom=3, gain=1.1))
    return finish(arr, t, 101)


# ------------------------------------------------------------------ SCENE 2
def scene2(t, dur):
    """REVEAL - an operator at the consoles, and the name of the system."""
    arr = M.clip("console", t, dur, zoom=(1.04, 1.13), pan=((0.46, 0.5), (0.54, 0.46)))

    im, d = new_layer()
    scrim(d, 0.0, 0.34, 195)
    scrim(d, 0.57, 0.67, 115)
    E.illustration_mark(d, alpha=int(150 * smooth01(t, 1.0, 1.8)))
    arr = composite(arr, resolve(im, bloom=0))

    ov, od = new_layer()
    tag(od, 0.052, "INDIAN AIR FORCE  •  INDIGENOUS SYSTEM",
        int(215 * smooth01(t, 0.25, 0.8)), size=27)
    title_block(od, RW / 2, RH * 0.135, "VAYU UTtaM", "UNMANNED TRAFFIC MANAGEMENT",
                t=t, t0=1.05, size=118, sub_size=33)
    text(od, (RW / 2, RH * 0.612), "DEMONSTRATED — NOT YET IN SERVICE",
         f_mono(21 * SS, 600), INK_FAINT, anchor="ma",
         alpha=int(185 * smooth01(t, 2.2, 2.8)), track=2.4 * SS)
    arr = composite(arr, resolve(ov, bloom=4, gain=1.2))
    return finish(arr, t, 202)


# ------------------------------------------------------------------ SCENE 3
def scene3(t, dur):
    """DRONATHON 2026 - the desert range."""
    arr = M.still("desert_range", t, dur, zoom=(1.05, 1.16),
                  pan=((0.50, 0.62), (0.50, 0.44)))

    im, d = new_layer()
    scrim(d, 0.0, 0.30, 180)
    scrim(d, 0.55, 0.66, 125)
    for i, (fx, fy) in enumerate(((0.30, 0.495), (0.56, 0.540), (0.72, 0.470))):
        a = int(165 * smooth01(t, 0.7 + i * 0.22, 1.2 + i * 0.22))
        if a < 3:
            continue
        x, y = RW * fx, RH * fy
        E.corner_box(d, x - 54 * SS, y - 40 * SS, x + 54 * SS, y + 40 * SS,
                     SYS + (a,), int(2 * SS), arm=17 * SS)
    arr = composite(arr, resolve(im, bloom=4, gain=1.15))

    ov, od = new_layer()
    title_block(od, RW / 2, RH * 0.115, "DRONATHON 2026", "POKHRAN  •  RAJASTHAN",
                t=t, t0=0.35, size=100, sub_size=34)
    text(od, (RW / 2, RH * 0.605), "TECHNOLOGY DEMONSTRATION", f_mono(23 * SS, 600),
         INK_DIM, anchor="ma", alpha=int(195 * smooth01(t, 1.5, 2.1)), track=3 * SS)
    arr = composite(arr, resolve(ov, bloom=4, gain=1.2))
    return finish(arr, t, 303)


# ------------------------------------------------------------------ SCENE 4
def scene4(t, dur):
    """QUESTION - the city resolves into a tracking view.  Deliberately spare."""
    arr = M.clip("city_hud", t, dur, zoom=(1.02, 1.10))

    im, d = new_layer()
    scrim(d, 0.50, 0.66, 170)
    E.crosshair(d, RW * 0.5, RH * 0.33, 58 * SS,
                SYS + (int(190 * smooth01(t, 0.2, 0.7)),), int(2.2 * SS))
    arr = composite(arr, resolve(im, bloom=5, gain=1.25))

    ov, od = new_layer()
    text(od, (RW / 2, RH * 0.565), "WHAT IT DOES", f_title(92 * SS), INK,
         anchor="ma", alpha=int(255 * smooth01(t, 0.10, 0.5)), track=6 * SS)
    arr = composite(arr, resolve(ov, bloom=4, gain=1.2))
    return finish(arr, t, 404)


# ------------------------------------------------------------------ SCENE 5
def scene5(t, dur):
    """EXPLANATION - a military craft, then a civilian one, then both on a single
    air picture, then DETECT -> TRACK -> MANAGE."""
    a_mil = M.still("mountain_uav", t, dur, zoom=(1.06, 1.16), pan=((0.45, 0.5), (0.58, 0.5)))
    f1 = smooth01(t, 2.5, 3.3)
    if f1 > 0.001:
        a_civ = M.still("city_drones", t - 2.5, dur, zoom=(1.05, 1.15),
                        pan=((0.5, 0.42), (0.5, 0.56)))
        arr = dissolve(a_mil, a_civ, f1)
    else:
        arr = a_mil

    im, d = new_layer()
    scrim(d, 0.0, 0.205, 150)         # the city plate has a bright sky to sit on
    lab_a = smooth01(t, 0.5, 1.0) * (1 - smooth01(t, 2.4, 2.9))
    lab_b = smooth01(t, 3.2, 3.7) * (1 - smooth01(t, 5.0, 5.5))
    if lab_a > 0.01 or lab_b > 0.01:
        scrim(d, 0.045, 0.185, int(180 * max(lab_a, lab_b)))
    if lab_a > 0.01:
        tag(d, 0.088, "MILITARY", int(245 * lab_a), INK, size=44)
    if lab_b > 0.01:
        tag(d, 0.088, "CIVILIAN", int(245 * lab_b), INK, size=44)

    merge = smooth01(t, 5.2, 6.2)
    if merge > 0.01:
        py0, py1 = RH * 0.195, RH * 0.525
        d.rounded_rectangle([RW * 0.08, py0, RW * 0.92, py1], radius=14 * SS,
                            fill=(7, 14, 21, int(214 * merge)),
                            outline=SYS + (int(72 * merge),), width=int(1.7 * SS))
        E.corner_box(d, RW * 0.08, py0, RW * 0.92, py1, SYS + (int(170 * merge),),
                     int(2.2 * SS), arm=36 * SS)
        proj = map_projector(RW * 0.5, (py0 + py1) / 2,
                             map_scale_for_height((py1 - py0) * 0.80))
        draw_india(d, proj, outline=SYS + (int(170 * merge),), width=int(2 * SS),
                   fill=SYS_DEEP + (int(30 * merge),))
        for i, tr in enumerate(E.make_tracks(8, 55, RW * 0.15, py0 + 44 * SS,
                                             RW * 0.85, py1 - 44 * SS, SYS,
                                             speed=(0.05, 0.11))):
            E.draw_track(d, tr, t, alpha=int(215 * merge), head_r=3.6 * SS,
                         show_label=(i == 0 and t > 6.6),
                         label_alpha=int(210 * smooth01(t, 6.6, 7.1)),
                         fnt=f_mono(19 * SS, 500))
        tag(d, 0.165, "ONE AIR PICTURE", int(200 * merge), INK_DIM, size=26)

    if smooth01(t, 6.5, 7.0) > 0.01:
        scrim(d, 0.540, 0.632, int(200 * smooth01(t, 6.5, 7.0)))
    for i, s in enumerate(("DETECT", "TRACK", "MANAGE")):
        a = smooth01(t, 6.6 + i * 0.78, 7.0 + i * 0.78)
        if a < 0.01:
            continue
        cxs, y = RW * (0.22 + i * 0.28), RH * 0.567
        text(d, (cxs, y), s, f_sub(38 * SS), mix(INK_DIM, SYS, a), anchor="ma",
             alpha=int(255 * a), track=4 * SS)
        d.line([cxs - 52 * SS, y + 48 * SS, cxs + 52 * SS, y + 48 * SS],
               fill=SYS + (int(170 * a),), width=int(2.4 * SS))
        if i < 2:
            # drawn as a mark: the condensed face carries no arrow glyph
            aa = smooth01(t, 7.0 + i * 0.78, 7.35 + i * 0.78)
            ax, ay, hh = cxs + RW * 0.14, y + 22 * SS, 11 * SS
            d.polygon([(ax - hh, ay - hh), (ax + hh, ay), (ax - hh, ay + hh)],
                      fill=SYS + (int(195 * aa),))

    E.illustration_mark(d, alpha=int(150 * merge))
    arr = composite(arr, resolve(im, bloom=5, gain=1.3))
    return finish(arr, t, 505)


# ------------------------------------------------------------------ SCENE 6
def scene6(t, dur):
    """TENSION - a fast run across the city, one contact bracketed."""
    arr = M.clip("city_fpv", t, dur, zoom=(1.03, 1.22))

    im, d = new_layer()
    f = t / max(dur, 1e-6)
    qx, qy = RW * (0.40 + 0.16 * f), RH * (0.34 - 0.05 * f)
    a = smooth01(t, 0.25, 0.75)
    E.crosshair(d, qx, qy, 112 * SS, SYS + (int(190 * a),), int(2.2 * SS))
    E.corner_box(d, qx - 88 * SS, qy - 80 * SS, qx + 88 * SS, qy + 80 * SS,
                 SYS + (int(160 * a),), int(2 * SS), arm=24 * SS)
    text(d, (qx + 102 * SS, qy - 92 * SS), "CONTACT", f_mono(20 * SS, 600), SYS,
         alpha=int(215 * a), track=2 * SS)
    arr = composite(arr, resolve(im, bloom=5, gain=1.25))
    return finish(arr, t, 606, vig=0.5)


# ------------------------------------------------------------------ SCENE 7
def scene7(t, dur):
    """CROWDED AIRSPACE - the sky fills up and the count climbs with it."""
    arr = M.still("tracks_sky", t, dur, zoom=(1.04, 1.15), pan=((0.5, 0.40), (0.5, 0.58)))

    im, d = new_layer()
    f = t / max(dur, 1e-6)
    total = 46
    active = int(round(lerp(4, total, ease_out(f, 1.5))))
    tracks = E.make_tracks(total, 77, RW * 0.06, RH * 0.16, RW * 0.94, RH * 0.50,
                           SYS, speed=(0.05, 0.15))
    for i, tr in enumerate(tracks[:active]):
        born = i / total * dur * 0.78
        E.draw_track(d, tr, t, alpha=int(200 * smooth01(t, born, born + 0.40)),
                     head_r=3.0 * SS, trail_width=int(1.7 * SS))

    scrim(d, 0.0, 0.155, 190)
    scrim(d, 0.545, 0.655, 135)
    arr = composite(arr, resolve(im, bloom=6, gain=1.4))

    ov, od = new_layer()
    tag(od, 0.046, "AIRSPACE DENSITY", 205, size=30)
    text(od, (RW / 2, RH * 0.046 + 50 * SS), f"{active:02d}", f_title(104 * SS), SYS,
         anchor="ma", alpha=245)
    text(od, (RW / 2, RH * 0.046 + 172 * SS), "ACTIVE TRACKS", f_mono(21 * SS, 600),
         INK_FAINT, anchor="ma", alpha=190, track=3 * SS)
    text(od, (RW / 2, RH * 0.592), "WHICH ONE IS AUTHORISED?", f_sub(40 * SS), INK,
         anchor="ma", alpha=int(240 * smooth01(t, dur - 2.6, dur - 1.8)), track=3 * SS)
    E.illustration_mark(od, alpha=140)
    arr = composite(arr, resolve(ov, bloom=4, gain=1.2))
    return finish(arr, t, 707)


# ------------------------------------------------------------------ SCENE 8
def scene8(t, dur):
    """POTENTIAL THREAT - one track stops matching the rest.

    Identification, not engagement: no weapon, no intercept, no explosion.
    """
    arr = M.still("field_tablet", t, dur, zoom=(1.06, 1.15), pan=((0.5, 0.46), (0.5, 0.56)))

    im, d = new_layer()
    a = smooth01(t, 0.15, 0.7)
    pulse = 0.74 + 0.26 * math.sin(t * 7.0)
    # The supplied plate already carries its own lock box.  Drawing a second
    # bracket over it just made two boxes fight, so the overlay here is a single
    # pulsing marker off to the side and nothing on top of the screen itself.
    mx, my = RW * 0.845, RH * 0.118
    d.ellipse([mx - 13 * SS, my - 13 * SS, mx + 13 * SS, my + 13 * SS],
              fill=CAUTION + (int(235 * a * pulse),))
    dashed_circle(d, mx, my, 30 * SS, CAUTION + (int(150 * a),), int(1.8 * SS),
                  dashes=12, phase=t * 1.1)

    scrim(d, 0.0, 0.115, 185)
    scrim(d, 0.505, 0.655, 205)
    arr = composite(arr, resolve(im, bloom=6, gain=1.4))

    ov, od = new_layer()
    tag(od, 0.042, "TRACK CLASSIFICATION", 205, size=28)
    E.stat_chip(od, RW * 0.10, RH * 0.532, RW * 0.38, 96 * SS, "AUTHORISED", "45",
                SYS, int(240 * a), f_mono(18 * SS, 600), f_title(44 * SS))
    E.stat_chip(od, RW * 0.52, RH * 0.532, RW * 0.38, 96 * SS, "UNIDENTIFIED", "01",
                CAUTION, int(240 * a), f_mono(18 * SS, 600), f_title(44 * SS))
    E.illustration_mark(od, alpha=150)
    arr = composite(arr, resolve(ov, bloom=4, gain=1.2))
    return finish(arr, t, 808)


# ------------------------------------------------------------------ SCENE 9
def scene9(t, dur):
    """ROGUE DRONES - the crew, and the air picture they are working."""
    arr = M.clip("crew", t, dur, zoom=(1.05, 1.14), pan=((0.56, 0.5), (0.44, 0.5)))

    im, d = new_layer()
    px0, px1 = RW * 0.07, RW * 0.93
    py0, py1 = RH * 0.105, RH * 0.435
    pa = smooth01(t, 0.3, 1.1)
    d.rounded_rectangle([px0, py0, px1, py1], radius=16 * SS,
                        fill=(6, 13, 20, int(218 * pa)),
                        outline=SYS + (int(80 * pa),), width=int(1.8 * SS))
    proj = map_projector((px0 + px1) / 2, (py0 + py1) / 2,
                         map_scale_for_height((py1 - py0) * 0.84))
    draw_india(d, proj, outline=SYS + (int(185 * pa),), width=int(2 * SS),
               fill=SYS_DEEP + (int(38 * pa),))

    tracks = E.make_tracks(22, 91, px0 + 56 * SS, py0 + 42 * SS, px1 - 56 * SS,
                           py1 - 42 * SS, SYS, speed=(0.05, 0.12))
    for i, tr in enumerate(tracks):
        if i == 5:
            continue
        E.draw_track(d, tr, t, alpha=int(195 * pa), head_r=3.0 * SS, trail_width=int(1.7 * SS))
    rt = tracks[5]
    rt.color = CAUTION
    E.draw_track(d, rt, t, alpha=int(248 * pa), head_r=4.6 * SS, trail_width=int(2.4 * SS))
    rx, ry = rt.pos(t)
    E.corner_box(d, rx - 58 * SS, ry - 58 * SS, rx + 58 * SS, ry + 58 * SS,
                 CAUTION + (int(215 * pa * (0.72 + 0.28 * math.sin(t * 6))),),
                 int(2.2 * SS), arm=19 * SS)

    sweep = sweep_out((px0 + px1) / 2, (py0 + py1) / 2, (px1 - px0) * 0.50,
                      -math.pi / 2 + t * 1.0, SYS, alpha=int(40 * pa))

    fm = f_mono(21 * SS, 600)
    for i, (lbl, val, col) in enumerate((("AUTHORISED", "21", SYS),
                                         ("UNIDENTIFIED", "01", CAUTION))):
        a = int(235 * smooth01(t, 1.5 + i * 0.4, 2.1 + i * 0.4))
        y = py1 + 42 * SS + i * 46 * SS
        d.rectangle([px0, y - 4 * SS, px0 + 6 * SS, y + 25 * SS], fill=col + (a,))
        text(d, (px0 + 22 * SS, y), lbl, fm, col, alpha=a, track=2.2 * SS)
        text(d, (px1, y), val, fm, INK, anchor="ra", alpha=a, track=2.2 * SS)

    E.illustration_mark(d, alpha=int(160 * pa))
    arr = composite(arr, sweep, downsample=False)
    arr = composite(arr, resolve(im, bloom=6, gain=1.35))

    ov, od = new_layer()
    text(od, (RW / 2, RH * 0.612), "MANAGING A CROWDED SKY", f_sub(36 * SS), INK_DIM,
         anchor="ma", alpha=int(215 * smooth01(t, 3.0, 3.7)), track=7 * SS)
    arr = composite(arr, resolve(ov, bloom=3, gain=1.1))
    return finish(arr, t, 909)


# ----------------------------------------------------------------- SCENE 10
def scene10(t, dur):
    """BEYOND MILITARY - one continuous lateral move past a range, an airport, a
    city and an infrastructure site.

    Rendered rather than cut together on purpose: the line is about one system
    reaching four places, and a single unbroken camera move says that where four
    cross-dissolves would just look like four shots.
    """
    horizon = H * 0.44
    f = t / max(dur, 1e-6)
    arr = vgradient((16, 20, 28), (34, 38, 46))
    arr[:int(horizon)] = vgradient((18, 26, 42), (132, 104, 86), (W, int(horizon)))
    arr = E.haze_band(arr, horizon - 230, horizon + 30, (150, 118, 94), 0.55)
    arr = E.haze_band(arr, horizon - 60, horizon + 120, (96, 86, 90), 0.30)

    im, d = new_layer()
    hy = horizon * SS
    pan = ease_in_out(f) * RW * 2.55
    d.rectangle([0, hy, RW, RH], fill=(14, 18, 25, 255))
    d.line([0, hy, RW, hy], fill=(196, 158, 126, 130), width=int(2.0 * SS))

    def sx(wx):
        return wx - pan

    ink = (11, 14, 20)
    # 1 range
    d.rectangle([sx(RW * 0.18), hy - 50 * SS, sx(RW * 0.52), hy], fill=ink + (255,))
    d.rectangle([sx(RW * 0.58), hy - 36 * SS, sx(RW * 0.80), hy], fill=ink + (255,))
    d.line([sx(RW * 0.88), hy, sx(RW * 0.88), hy - 186 * SS], fill=ink + (255,),
           width=int(4 * SS))
    # 2 airport
    E.runway(d, sx(RW * 1.35), hy - 4 * SS, RH, 28 * SS, 290 * SS, (150, 162, 178), 118,
             phase=t * 0.5)
    d.rectangle([sx(RW * 1.05), hy - 42 * SS, sx(RW * 1.30), hy], fill=ink + (255,))
    d.rectangle([sx(RW * 1.585), hy - 168 * SS, sx(RW * 1.625), hy], fill=ink + (255,))
    d.rounded_rectangle([sx(RW * 1.53), hy - 204 * SS, sx(RW * 1.67), hy - 156 * SS],
                        radius=8 * SS, fill=ink + (255,))
    # 3 city
    E.skyline_band(d, hy, 246 * SS, ink, 255, seed=44, phase=sx(RW * 1.95))
    # 4 infrastructure
    for k in range(4):
        E.pylon(d, sx(RW * (2.72 + k * 0.30)), hy, (206 - k * 12) * SS, ink, 255)

    # one drone holds frame throughout - the thread through the move
    qx = RW * 0.5 + math.sin(t * 0.9) * 38 * SS
    qy = RH * 0.245 + math.sin(t * 1.4) * 9 * SS
    E.quadcopter(d, qx, qy, 44 * SS, INK, 235, spin=t * 14)
    E.crosshair(d, qx, qy, 86 * SS, SYS + (150,), int(1.8 * SS))

    arr = composite(arr, resolve(im, bloom=5, gain=1.2))

    ov, od = new_layer()
    scrim(od, 0.0, 0.14, 150)
    scrim(od, 0.545, 0.645, 165)
    tag(od, 0.055, "BEYOND THE MILITARY", int(205 * smooth01(t, 0.2, 0.8)), size=30)
    for name, a0, a1 in (("MILITARY", 0.02, 0.24), ("AIRPORT", 0.28, 0.52),
                         ("CITY", 0.54, 0.76), ("INFRASTRUCTURE", 0.78, 1.01)):
        a = smooth01(f, a0, a0 + 0.07) * (1 - smooth01(f, a1 - 0.07, a1))
        if a > 0.01:
            text(od, (RW / 2, RH * 0.578), name, f_sub(40 * SS), INK,
                 anchor="ma", alpha=int(240 * a), track=7 * SS)
    arr = composite(arr, resolve(ov, bloom=3, gain=1.1))
    return finish(arr, t, 1010, vig=0.5)


# ----------------------------------------------------------------- SCENE 11
def scene11(t, dur):
    """CIVIL AVIATION / CRITICAL INFRASTRUCTURE / PUBLIC SAFETY.

    Three real shots in one frame, arriving in turn on the three nouns, so the
    line lands as a montage rather than three separate cuts.
    """
    arr = vgradient((6, 10, 16), (11, 17, 25))
    bands = (("airliner", 0.055, 0.238, "CIVIL AVIATION"),
             ("infrastructure", 0.248, 0.431, "CRITICAL INFRASTRUCTURE"),
             ("response", 0.441, 0.624, "PUBLIC SAFETY"))

    for i, (key, y0f, y1f, _label) in enumerate(bands):
        t0 = 0.15 + i * 0.62
        a = smooth01(t, t0, t0 + 0.70)
        if a < 0.01:
            continue
        y0 = int(H * y0f)
        bw, bh = int(W * 0.86), int(H * y1f) - y0
        src = M._load_still(key)
        sw, sh = src.size
        zz = max(bw / sw, bh / sh) * 1.06 * (1.0 + 0.05 * ease_in_out(
            min(1.0, max(0.0, (t - t0) / max(dur - t0, 1e-6)))))
        nw, nh = max(bw, int(sw * zz)), max(bh, int(sh * zz))
        tile = src.resize((nw, nh), Image.LANCZOS)
        tile = tile.crop(((nw - bw) // 2, (nh - bh) // 2,
                          (nw - bw) // 2 + bw, (nh - bh) // 2 + bh))
        block = M.grade(np.asarray(tile, dtype=np.float32))
        x0 = int(W * 0.07)
        sl = arr[y0:y0 + bh, x0:x0 + bw]
        arr[y0:y0 + bh, x0:x0 + bw] = sl * (1 - a) + block * a

    im, d = new_layer()
    for i, (_key, y0f, y1f, label) in enumerate(bands):
        a = smooth01(t, 0.15 + i * 0.62, 0.85 + i * 0.62)
        if a < 0.01:
            continue
        y0, y1 = RH * y0f, RH * y1f
        d.rounded_rectangle([RW * 0.07, y0, RW * 0.93, y1], radius=13 * SS,
                            outline=SYS + (int(80 * a),), width=int(1.7 * SS))
        d.rectangle([RW * 0.07, y1 - 54 * SS, RW * 0.93, y1], fill=(4, 8, 13, int(168 * a)))
        text(d, (RW * 0.10, y1 - 40 * SS), label, f_mono(23 * SS, 700), SYS,
             alpha=int(240 * a), track=2.4 * SS)
        qx = RW * (0.16 + ((t * 0.13 + i * 0.4) % 1.0) * 0.68)
        E.crosshair(d, qx, y0 + (y1 - y0) * 0.34, 40 * SS, SYS + (int(140 * a),),
                    int(1.5 * SS))
    E.illustration_mark(d, alpha=150)
    arr = composite(arr, resolve(im, bloom=4, gain=1.2))
    return finish(arr, t, 1111)


# ----------------------------------------------------------------- SCENE 12
def scene12(t, dur):
    """DRONATHON, WIDE.

    Opens tight on a rotor and pulls out to the range.  Scene 3 already played
    this location; starting somewhere else and arriving here keeps the callback
    without repeating the shot.
    """
    a_rotor = M.still("rotor", t, dur, zoom=(1.10, 1.30), pan=((0.44, 0.5), (0.58, 0.5)))
    f1 = smooth01(t, 1.5, 2.6)
    if f1 > 0.001:
        a_range = M.still("desert_range", t - 1.5, dur, zoom=(1.34, 1.02),
                          pan=((0.42, 0.30), (0.56, 0.62)))
        arr = dissolve(a_rotor, a_range, f1)
    else:
        arr = a_rotor

    im, d = new_layer()
    scrim(d, 0.0, 0.26, 185)
    scrim(d, 0.545, 0.655, 150)
    if f1 > 0.3:
        aa = int(150 * smooth01(t, 2.4, 3.2))
        E.crosshair(d, RW * 0.5, RH * 0.40, 44 * SS, SYS + (aa,), int(1.8 * SS))
        dashed_circle(d, RW * 0.5, RH * 0.40, 112 * SS, SYS + (int(aa * 0.7),),
                      int(1.5 * SS), dashes=30, phase=t * 0.5)
    arr = composite(arr, resolve(im, bloom=4, gain=1.18))

    ov, od = new_layer()
    a = smooth01(t, 0.4, 1.1)
    text(od, (RW / 2, RH * 0.082), "DRONATHON 2026", f_title(86 * SS), INK,
         anchor="ma", alpha=int(250 * a), track=5 * SS)
    text(od, (RW / 2, RH * 0.082 + 100 * SS), "ONE OF MANY TECHNOLOGIES SHOWCASED",
         f_mono(21 * SS, 600), INK_DIM, anchor="ma",
         alpha=int(205 * smooth01(t, 0.9, 1.6)), track=2.6 * SS)
    arr = composite(arr, resolve(ov, bloom=4, gain=1.2))
    return finish(arr, t, 1212)


# ----------------------------------------------------------------- SCENE 13
def scene13(t, dur):
    """FUTURE OF AIRSPACE - fast jets, then the drones alongside them."""
    a_jet = M.still("jet_high", t, dur, zoom=(1.05, 1.14), pan=((0.42, 0.5), (0.56, 0.5)))
    f1 = smooth01(t, 1.5, 2.4)
    if f1 > 0.001:
        a_swarm = M.still("drone_formation", t - 1.5, dur, zoom=(1.04, 1.13),
                          pan=((0.5, 0.42), (0.5, 0.58)))
        arr = dissolve(a_jet, a_swarm, f1)
    else:
        arr = a_jet

    im, d = new_layer()
    na = smooth01(t, 2.2, 3.0)
    if na > 0.01:
        rng = np.random.default_rng(202)
        pts = [(RW * rng.uniform(0.16, 0.84), RH * rng.uniform(0.20, 0.52)) for _ in range(9)]
        for i in range(len(pts) - 1):
            d.line([pts[i], pts[i + 1]], fill=SYS + (int(52 * na),), width=int(1.3 * SS))
        for p in pts:
            E.drone_dot(d, p[0], p[1], 3.4 * SS, SYS, int(180 * na))

    scrim(d, 0.0, 0.115, 190)
    scrim(d, 0.520, 0.655, 210)
    arr = composite(arr, resolve(im, bloom=5, gain=1.3))

    ov, od = new_layer()
    tag(od, 0.045, "THE NEXT AIRSPACE", int(200 * smooth01(t, 0.3, 0.9)), size=28)
    text(od, (RW / 2, RH * 0.578), "FIGHTER JETS  +  DRONES  +  NETWORK", f_sub(34 * SS),
         SYS, anchor="ma", alpha=int(240 * smooth01(t, 2.3, 2.9)), track=4 * SS)
    arr = composite(arr, resolve(ov, bloom=4, gain=1.2))
    return finish(arr, t, 1313)


# ----------------------------------------------------------------- SCENE 14
def scene14(t, dur):
    """HERO / END CARD - the crew, the full air picture, and the name."""
    arr = M.clip("console", t + 1.2, dur, zoom=(1.10, 1.02), pan=((0.5, 0.46), (0.5, 0.52)))

    im, d = new_layer()
    cx, cy = RW * 0.5, RH * 0.275
    pa = smooth01(t, 0.1, 0.9)
    for _k, r in enumerate((0.20, 0.33, 0.46)):
        dashed_circle(d, cx, cy, RW * r, SYS + (int(64 * pa),), int(1.4 * SS),
                      dashes=70, phase=t * 0.08)
    proj = map_projector(cx, cy, map_scale_for_height(RH * 0.26))
    draw_india(d, proj, outline=SYS + (int(215 * pa),), width=int(2.4 * SS),
               fill=SYS_DEEP + (int(40 * pa),))
    for tr in E.make_tracks(26, 303, cx - RW * 0.30, cy - RH * 0.12,
                            cx + RW * 0.30, cy + RH * 0.12, SYS, speed=(0.04, 0.11)):
        E.draw_track(d, tr, t, alpha=int(200 * pa), head_r=3.0 * SS, trail_width=int(1.7 * SS))
    sweep = sweep_out(cx, cy, RW * 0.50, -math.pi / 2 + t * 0.9, SYS, alpha=int(44 * pa))
    E.illustration_mark(d, alpha=int(140 * pa))

    arr = composite(arr, sweep, downsample=False)
    arr = composite(arr, resolve(im, bloom=7, gain=1.45))

    ov, od = new_layer()
    a = smooth01(t, dur - 3.2, dur - 2.3)
    if a > 0.01:
        od.rectangle([0, 0, RW, RH], fill=(4, 8, 13, int(196 * a)))
    title_block(od, RW / 2, RH * 0.425, "VAYU UTtaM", "UNMANNED TRAFFIC MANAGEMENT",
                t=t, t0=dur - 3.0, size=128, sub_size=33)
    text(od, (RW / 2, RH * 0.545), "DEMONSTRATED AT DRONATHON 2026", f_mono(22 * SS, 600),
         INK_DIM, anchor="ma", alpha=int(205 * smooth01(t, dur - 2.1, dur - 1.4)),
         track=2.6 * SS)
    arr = composite(arr, resolve(ov, bloom=4, gain=1.2))
    return finish(arr, t, 1414)


SCENES = {
    1: scene1, 2: scene2, 3: scene3, 4: scene4, 5: scene5, 6: scene6, 7: scene7,
    8: scene8, 9: scene9, 10: scene10, 11: scene11, 12: scene12, 13: scene13, 14: scene14,
}
