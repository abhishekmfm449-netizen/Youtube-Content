# -*- coding: utf-8 -*-
"""Frame renderer: writes raw RGB24 1080x1920@30 to stdout for ffmpeg."""
import os, sys, math, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from design import *
import graphics, captions
from timeline import SHOTS, IMG, VID, REPO, VIDEO_DUR, MARKS, _m, SOFTEN

FPS   = 30
SP    = "/tmp/claude-0/-home-user-Youtube-Content/f48c739a-f44b-53f4-b1f5-20e1481d2735/scratchpad"
VFDIR = os.path.join(SP, "vframes")
NF    = int(round(VIDEO_DUR*FPS))

CARD  = (90, 672, 990, 1178)           # 16:9 inset card for video sources
AR    = W/H

# ---------------------------------------------------------------- sources --
_img = {}
def img(key):
    """Loads a repository still.  Regions listed in SOFTEN carry prices for
    products this story makes no claim about, so they are blurred at source."""
    if key not in _img:
        im = Image.open(os.path.join(REPO, IMG[key])).convert("RGB")
        for (x0, y0, x1, y1) in SOFTEN.get(key, []):
            bx = (int(x0*im.width), int(y0*im.height), int(x1*im.width), int(y1*im.height))
            reg = im.crop(bx).filter(ImageFilter.GaussianBlur(im.width*0.015))
            fm = Image.new("L", (bx[2]-bx[0], bx[3]-bx[1]), 0)
            pad = 14
            ImageDraw.Draw(fm).rectangle((pad, pad, fm.width-pad, fm.height-pad), fill=255)
            im.paste(reg, bx[:2], fm.filter(ImageFilter.GaussianBlur(pad*0.7)))
        _img[key] = im
    return _img[key]

_vf = {}
def vframe(key, idx):
    idx = max(1, min(300, int(idx)+1))
    k = (key, idx)
    if k not in _vf:
        if len(_vf) > 240: _vf.clear()
        _vf[k] = Image.open(os.path.join(VFDIR, key, f"{idx:04d}.jpg")).convert("RGB")
    return _vf[k]

# ---------------------------------------------------------------- camera ---
def cover_crop(im, z, cx, cy, out=(W, H)):
    """Crop a `out`-aspect window at zoom z centred on (cx,cy) in 0..1, then scale up."""
    sw, sh = im.size
    sc = max(out[0]/sw, out[1]/sh) * z
    cw, ch = out[0]/sc, out[1]/sc
    x = clamp(cx*sw - cw/2, 0, max(0, sw-cw))
    y = clamp(cy*sh - ch/2, 0, max(0, sh-ch))
    if cw > sw: x, cw = 0, sw
    if ch > sh: y, ch = 0, sh
    return im.resize(out, Image.LANCZOS, box=(x, y, x+cw, y+ch))

def blur_plate(im, z, cx, cy, radius=34, dim=0.42, tint=(9, 18, 40), tint_a=0.30):
    small = (W//8, H//8)
    p = cover_crop(im, z, cx, cy, small).filter(ImageFilter.GaussianBlur(radius/8.0))
    p = p.resize((W, H), Image.BICUBIC)
    p = ImageEnhance.Brightness(p).enhance(dim)
    if tint_a > 0:
        p = Image.blend(p, Image.new("RGB", (W, H), tint), tint_a)
    return p

def grade(im, sat=1.04, con=1.05, bri=1.0):
    im = ImageEnhance.Color(im).enhance(sat)
    im = ImageEnhance.Contrast(im).enhance(con)
    if bri != 1.0: im = ImageEnhance.Brightness(im).enhance(bri)
    return im

def vignette_mask():
    m = Image.new("L", (W//4, H//4), 0)
    d = ImageDraw.Draw(m)
    d.ellipse((-W//10, H//20, W//4+W//10, H//4-H//20), fill=255)
    return m.filter(ImageFilter.GaussianBlur(34)).resize((W, H), Image.BICUBIC)
_VIG = None
def vignette(im, strength=0.30):
    global _VIG
    if _VIG is None: _VIG = vignette_mask()
    dark = ImageEnhance.Brightness(im).enhance(1-strength)
    return Image.composite(im, dark, _VIG)

# ---------------------------------------------------------------- shots ----
def shot_base(s, t):
    """Render one shot's picture (no graphics, no captions) at absolute time t."""
    dur = s["t1"] - s["t0"]
    u   = min(max((t - s["t0"]) / dur, 0.0), 1.18)   # slight overshoot so the
    mv  = s["move"]                                   # outgoing shot keeps moving
    uc  = min(u, 1.0)
    e   = u + 0.30*(smooth(uc) - uc)

    if s["src"][0] == "vid":
        key, st = s["src"][1], s["src"][2]
        fr = vframe(key, (st + (t - s["t0"]))*FPS)
        pz0, pz1 = mv.get("plate_z", (1.35, 1.45))
        plate = blur_plate(fr, lerp(pz0, pz1, e), 0.5, 0.5, radius=34, dim=0.54)
        z  = lerp(mv["z0"], mv["z1"], e)
        cx = mv.get("cx", 0.5) + mv.get("dx", 0.0)*e
        cy = mv.get("cy", 0.5) + mv.get("dy", 0.0)*e
        cw, ch = CARD[2]-CARD[0], CARD[3]-CARD[1]
        card = cover_crop(fr, z, cx, cy, (cw, ch))
        card = grade(card, 1.06, 1.06)
        base = plate
        sh = Image.new("L", (W, H), 0)
        ImageDraw.Draw(sh).rounded_rectangle((CARD[0], CARD[1]+18, CARD[2], CARD[3]+18),
                                             radius=26, fill=175)
        sh = sh.filter(ImageFilter.GaussianBlur(26))
        base = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), base, sh)
        mask = Image.new("L", (W, H), 0)
        ImageDraw.Draw(mask).rounded_rectangle(CARD, radius=26, fill=255)
        full = Image.new("RGB", (W, H)); full.paste(card, (CARD[0], CARD[1]))
        base = Image.composite(full, base, mask)
        ed = ImageDraw.Draw(base)
        ed.rounded_rectangle(CARD, radius=26, outline=(172, 192, 224), width=2)
        return vignette(base, 0.26)

    im = img(s["src"][1])
    k  = mv["k"]
    if k == "push":
        z  = lerp(mv["z0"], mv["z1"], e)
        out = cover_crop(im, z, mv["cx"], mv["cy"])
    elif k == "pan":
        z  = lerp(mv["z0"], mv["z1"], e)
        out = cover_crop(im, z, lerp(mv["cx0"], mv["cx1"], e), lerp(mv["cy0"], mv["cy1"], e))
    elif k == "parallax":
        z   = lerp(mv["z0"], mv["z1"], e)
        cx  = lerp(mv["cx0"], mv["cx1"], e); cy = lerp(mv["cy0"], mv["cy1"], e)
        bcx = lerp(mv["cx0"], mv["cx1"], e*0.55); bcy = lerp(mv["cy0"], mv["cy1"], e*0.55)
        back  = cover_crop(im, z*0.955, bcx, bcy).filter(ImageFilter.GaussianBlur(4.5))
        back  = ImageEnhance.Brightness(back).enhance(0.84)
        front = cover_crop(im, z, cx, cy)
        fm = Image.new("L", (W//4, H//4), 0)
        ImageDraw.Draw(fm).ellipse((-W//14, H//16, W//4+W//14, H//4-H//12), fill=255)
        fm = fm.filter(ImageFilter.GaussianBlur(30)).resize((W, H), Image.BICUBIC)
        out = Image.composite(front, back, fm)
    else:
        raise ValueError(k)

    if mv.get("blur"): out = out.filter(ImageFilter.GaussianBlur(mv["blur"]))
    out = grade(out, 1.05, 1.05, mv.get("dim", 1.0))
    if mv.get("dim", 1.0) < 1.0:
        out = Image.blend(out, Image.new("RGB", (W, H), (7, 15, 34)), 0.22)
    return vignette(out, 0.30)

def shot_full(s, t):
    """Picture + that shot's motion graphics."""
    base = shot_base(s, t).convert("RGBA")
    g = s.get("gfx")
    if g:
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d  = ImageDraw.Draw(ov)
        dur = s["t1"] - s["t0"]
        graphics.REG[g](ov, d, clamp((t-s["t0"])/dur), dur)
        base.alpha_composite(ov)
    return base

# ------------------------------------------------------------ transitions --
TRANS_DUR = {"cut":0.0, "dissolve":0.38, "push_l":0.30, "push_u":0.32,
             "whip":0.24, "pushin_cut":0.16}

def hblur(im, px):
    """Smooth directional blur for the whip cuts (running-sum box blur)."""
    k = int(px)
    if k < 1: return im
    a = np.asarray(im.convert("RGB")).astype(np.float32)
    pad = np.pad(a, ((0, 0), (k+1, k), (0, 0)), mode="edge")
    c = np.cumsum(pad, axis=1)
    c = np.concatenate([np.zeros((c.shape[0], 1, 3), np.float32), c], axis=1)
    out = (c[:, 2*k+1:2*k+1+a.shape[1]] - c[:, :a.shape[1]]) / (2*k+1)
    return Image.fromarray(out.astype(np.uint8)).convert("RGBA")

def compose(t):
    i = 0
    while i < len(SHOTS)-1 and t >= SHOTS[i]["t1"]: i += 1
    s = SHOTS[i]
    cur = shot_full(s, t)
    td  = TRANS_DUR.get(s["trans"], 0.0)
    if i > 0 and td > 0 and (t - s["t0"]) < td:
        p  = SHOTS[i-1]
        u  = clamp((t - s["t0"]) / td)
        prev = shot_full(p, t)               # keeps the outgoing shot alive, no freeze
        kind = s["trans"]
        if kind == "dissolve":
            cur = Image.blend(prev, cur, smooth(u))
        elif kind in ("push_l", "push_u", "whip"):
            e = out_q(u) if kind != "whip" else out_c(u)
            if kind == "push_u":
                off = int(H*(1-e)); a = (0, off); b = (0, off-int(H*0.22))
            else:
                amt = W if kind == "push_l" else int(W*1.02)
                off = int(amt*(1-e)); a = (off, 0); b = (off-int(W*0.28), 0)
            if kind == "whip":
                bl = int(26*(1-abs(u*2-1)))
                cur, prev = hblur(cur, bl), hblur(prev, bl)
            out = Image.new("RGBA", (W, H), (0, 0, 0, 255))
            out.paste(prev, b, prev)
            out.paste(cur, a, cur)
            cur = out
        elif kind == "pushin_cut":
            f = 1.0 + 0.06*(1-out_q(u))
            if f > 1.001:
                nw, nh = int(W*f), int(H*f)
                cur = cur.resize((nw, nh), Image.BILINEAR).crop(
                    ((nw-W)//2, (nh-H)//2, (nw-W)//2+W, (nh-H)//2+H))
            fl = int(46*(1-out_q(u/0.55)) ) if u < 0.55 else 0
            if fl > 0: cur.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, fl)))
    return cur

# ------------------------------------------------------------------ grain --
_rng = np.random.default_rng(3)
GRAIN = [(_rng.normal(0, 3.1, (H, W, 1))).astype(np.float32) for _ in range(6)]

# ------------------------------------------------------------------- main --
def main():
    ev = captions.build(_m["marks"], VIDEO_DUR)
    captions.to_srt(ev, os.path.join(SP, "build", "captions.srt"))
    out = sys.stdout.buffer
    probe = os.environ.get("PROBE")          # comma-separated seconds -> PNG stills
    if probe:
        os.makedirs(os.path.join(SP, "probe"), exist_ok=True)
        for x in probe.split(","):
            t = float(x)
            fr = compose(t)
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            for e in ev: captions.render(ov, d, e, t)
            fr.alpha_composite(ov)
            fr.convert("RGB").save(os.path.join(SP, "probe", f"t{t:06.2f}.png"))
        return
    for n in range(NF):
        t = n/FPS
        fr = compose(t)
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        for e in ev: captions.render(ov, d, e, t)
        fr.alpha_composite(ov)
        a = np.asarray(fr.convert("RGB")).astype(np.float32) + GRAIN[n % 6]
        np.clip(a, 0, 255, out=a)
        out.write(a.astype(np.uint8).tobytes())
        if n % 150 == 0:
            print(f"  frame {n}/{NF}  t={t:5.2f}", file=sys.stderr, flush=True)
    out.flush()

if __name__ == "__main__":
    main()
