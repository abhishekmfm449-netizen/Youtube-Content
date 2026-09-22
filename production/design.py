# -*- coding: utf-8 -*-
"""Design system: colours, type, and reusable motion-graphic primitives."""
import os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SP    = "/tmp/claude-0/-home-user-Youtube-Content/f48c739a-f44b-53f4-b1f5-20e1481d2735/scratchpad"
FONTS = os.path.join(SP, "fonts")
W, H  = 1080, 1920

NAVY_D  = (5, 11, 26)
NAVY    = (10, 24, 54)
BLUE    = (43, 118, 240)
BLUE_D  = (22, 62, 140)
GOLD    = (255, 206, 84)
GOLD_D  = (196, 143, 24)
AMBER   = (255, 178, 44)
WHITE   = (255, 255, 255)
SOFT    = (206, 218, 238)
INK     = (7, 14, 30)

MARGIN     = 72
CAP_Y      = 1332          # caption block centre
CAP_MAXW   = 862           # keeps captions clear of the Shorts action rail

_fc = {}
def font(style, size):
    key = (style, size)
    if key not in _fc:
        f = {"xb":"Poppins-ExtraBold.ttf","b":"Poppins-Bold.ttf",
             "sb":"Poppins-SemiBold.ttf","m":"Poppins-Medium.ttf"}[style]
        _fc[key] = ImageFont.truetype(os.path.join(FONTS, f), size)
    return _fc[key]

# ---------- easing ---------------------------------------------------------
def clamp(x, a=0.0, b=1.0): return a if x < a else (b if x > b else x)
def smooth(u):  u = clamp(u); return u*u*(3-2*u)
def smoother(u):u = clamp(u); return u*u*u*(u*(u*6-15)+10)
def out_c(u):   u = clamp(u); return 1-(1-u)**3
def out_q(u):   u = clamp(u); return 1-(1-u)**5
def cine(u):    u = clamp(u); return u + 0.30*(smooth(u)-u)     # near-linear, soft ends
def back_out(u):
    u = clamp(u); c = 1.70158
    return 1 + (c+1)*(u-1)**3 + c*(u-1)**2
def lerp(a, b, u): return a + (b-a)*u

# ---------- text -----------------------------------------------------------
def text_w(d, s, f, tracking=0.0):
    if not s: return 0
    if tracking == 0: return d.textlength(s, font=f)
    return sum(d.textlength(c, font=f) for c in s) + tracking*(len(s)-1)

def draw_text(d, xy, s, f, fill, tracking=0.0, anchor="la", halo=0):
    """anchor: first char h in (l,m,r), second v in (a=ascender top, m=middle).
       halo>0 rings the glyphs with a soft dark edge so headline type stays
       readable over a bright still."""
    if halo:
        ha = int((fill[3] if len(fill) > 3 else 255) * 0.42)
        if ha > 3:
            for r in (halo, halo*0.55):
                for k in range(8):
                    an = k*math.pi/4
                    draw_text(d, (xy[0]+math.cos(an)*r, xy[1]+math.sin(an)*r),
                              s, f, (3, 7, 18, ha), tracking, anchor)
    x, y = xy
    tw = text_w(d, s, f, tracking)
    if   anchor[0] == "m": x -= tw/2
    elif anchor[0] == "r": x -= tw
    va = "a" if anchor[1] == "a" else ("m" if anchor[1] == "m" else "s")
    if tracking == 0:
        d.text((x, y), s, font=f, fill=fill, anchor="l"+va)
    else:
        for c in s:
            d.text((x, y), c, font=f, fill=fill, anchor="l"+va)
            x += d.textlength(c, font=f) + tracking
    return tw

def wrap(d, s, f, maxw, tracking=0.0):
    words, lines, cur = s.split(" "), [], ""
    for wd in words:
        t = (cur+" "+wd).strip()
        if text_w(d, t, f, tracking) <= maxw or not cur: cur = t
        else: lines.append(cur); cur = wd
    if cur: lines.append(cur)
    return lines

# ---------- primitives -----------------------------------------------------
def rrect(d, box, r, fill=None, outline=None, width=2):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)

def shadow_layer(size, box, r, blur=26, alpha=140, offset=(0, 14)):
    s = Image.new("L", size, 0)
    ImageDraw.Draw(s).rounded_rectangle(
        (box[0]+offset[0], box[1]+offset[1], box[2]+offset[0], box[3]+offset[1]),
        radius=r, fill=alpha)
    return s.filter(ImageFilter.GaussianBlur(blur))

def vgrad(size, top, bottom):
    w, h = size
    g = Image.new("RGB", (1, h))
    px = g.load()
    for y in range(h):
        u = y/(h-1)
        px[0, y] = (int(lerp(top[0], bottom[0], u)),
                    int(lerp(top[1], bottom[1], u)),
                    int(lerp(top[2], bottom[2], u)))
    return g.resize(size, Image.BILINEAR)

def chip(ov, d, xy, label, *, fsize=38, style="sb", fg=INK, bg=GOLD,
         pad=(26, 14), r=None, tracking=1.5, anchor="l", reveal=1.0, alpha=255):
    """Rounded pill.  reveal 0..1 wipes the pill in from the left."""
    f = font(style, fsize)
    tw = text_w(d, label, f, tracking)
    bw, bh = tw + pad[0]*2, fsize + pad[1]*2
    x, y = xy
    if   anchor == "m": x -= bw/2
    elif anchor == "r": x -= bw
    rr = bh/2 if r is None else r
    vis = max(2.0, bw*out_c(reveal))
    tmp  = Image.new("RGBA", (int(bw)+4, int(bh)+4), (0, 0, 0, 0))
    td   = ImageDraw.Draw(tmp)
    td.rounded_rectangle((0, 0, bw, bh), radius=rr, fill=bg+(alpha,))
    draw_text(td, (pad[0], bh/2), label, f, fg+(alpha,), tracking, anchor="lm")
    tmp = tmp.crop((0, 0, int(vis), int(bh)+4))
    ov.alpha_composite(tmp, (int(x), int(y)))
    return bw, bh

def rule(d, x0, x1, y, color, u, thick=4, from_="l"):
    u = clamp(u)
    if u <= 0: return
    if from_ == "l": d.rectangle((x0, y, x0+(x1-x0)*u, y+thick), fill=color)
    elif from_ == "r": d.rectangle((x1-(x1-x0)*u, y, x1, y+thick), fill=color)
    else:
        c = (x0+x1)/2; hw = (x1-x0)/2*u
        d.rectangle((c-hw, y, c+hw, y+thick), fill=color)

def wipe_up(ov, layer, u, height):
    """Reveal `layer` (RGBA, same size as ov) with a bottom-up mask."""
    u = clamp(u)
    if u <= 0: return
    m = Image.new("L", ov.size, 0)
    ImageDraw.Draw(m).rectangle((0, 0, ov.size[0], height*u), fill=255)
    ov.alpha_composite(Image.composite(layer, Image.new("RGBA", ov.size, (0,0,0,0)), m))

def card_shape(size=(300, 190), c1=(28, 58, 124), c2=(14, 30, 70)):
    """Generic payment-card illustration (no brand marks)."""
    w, h = size
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    g = vgrad((w, h), c1, c2).convert("RGBA")
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0,0,w-1,h-1), radius=20, fill=255)
    im.paste(g, (0, 0), m)
    d.rectangle((0, int(h*0.30), w, int(h*0.30)+int(h*0.16)), fill=(9, 18, 40, 255))
    d.rounded_rectangle((int(w*0.08), int(h*0.56), int(w*0.08)+int(w*0.16), int(h*0.56)+int(h*0.16)),
                        radius=6, fill=GOLD+(255,))
    for i in range(4):
        d.rounded_rectangle((int(w*0.30)+i*int(w*0.155), int(h*0.66),
                             int(w*0.30)+i*int(w*0.155)+int(w*0.11), int(h*0.70)),
                            radius=3, fill=(178, 198, 232, 210))
    d.rounded_rectangle((0, 0, w-1, h-1), radius=20, outline=(150, 178, 224, 120), width=2)
    return im

def pause_glyph(size=118, color=WHITE, alpha=235, ring=True):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if ring:
        d.ellipse((2, 2, size-3, size-3), outline=color+(alpha,), width=5)
    bw, bh = size*0.115, size*0.40
    cx, cy = size/2, size/2
    d.rounded_rectangle((cx-bw*1.9, cy-bh/2, cx-bw*0.6, cy+bh/2), radius=4, fill=color+(alpha,))
    d.rounded_rectangle((cx+bw*0.6, cy-bh/2, cx+bw*1.9, cy+bh/2), radius=4, fill=color+(alpha,))
    return im

def cal_glyph(size=96, color=WHITE, alpha=235):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((4, 14, size-5, size-6), radius=12, outline=color+(alpha,), width=5)
    d.rectangle((4, 30, size-5, 36), fill=color+(alpha,))
    d.rounded_rectangle((size*0.24, 4, size*0.24+7, 22), radius=3, fill=color+(alpha,))
    d.rounded_rectangle((size*0.70, 4, size*0.70+7, 22), radius=3, fill=color+(alpha,))
    return im
