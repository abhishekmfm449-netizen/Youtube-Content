# -*- coding: utf-8 -*-
"""Motion-graphics recipes.  Each takes (ov, d, u, dur) and draws onto an RGBA overlay.
   u = 0..1 progress through the shot, dur = shot length in seconds."""
import math
from PIL import Image, ImageDraw, ImageFilter
from design import *

def _t(u, dur): return u*dur          # seconds into the shot

def _fade_tail(t, dur, tail=0.30):
    """1.0 through the shot, easing off just before the cut so nothing pops."""
    return clamp((dur - t)/tail) if t > dur-tail else 1.0

def _A(base, k):  return int(clamp(k)*base)

_SCRIM = {}
def _topscrim(ov, a=1.0, h=560, alpha=132):
    """Soft top-down darkening so headline type never fights a bright still."""
    key = (h, alpha)
    if key not in _SCRIM:
        g = Image.new("L", (1, h))
        px = g.load()
        for y in range(h):
            px[0, y] = int(alpha*(1 - (y/(h-1))**1.55))
        _SCRIM[key] = g.resize((W, h), Image.BILINEAR)
    m = _SCRIM[key]
    if a < 1.0: m = m.point(lambda v: int(v*a))
    lay = Image.new("RGBA", (W, h), (4, 9, 22, 255)); lay.putalpha(m)
    ov.alpha_composite(lay, (0, 0))

# ---------------------------------------------------------------- opening --
def open_title(ov, d, u, dur):
    t = _t(u, dur); a = _fade_tail(t, dur)
    _topscrim(ov, a)
    k = out_c(clamp(t/0.55))
    y = 268 + (1-k)*26
    rule(d, MARGIN, MARGIN+170, int(y-26), GOLD+(_A(255, k*a),), clamp((t-0.10)/0.40))
    draw_text(d, (MARGIN, y+16), "FLIPKART", font("sb", 44), SOFT+(_A(255, k*a),), tracking=9.0)
    k2 = out_q(clamp((t-0.18)/0.70))
    lay = Image.new("RGBA", ov.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    draw_text(ld, (MARGIN, 366), "BIG BILLION", font("xb", 100), WHITE+(_A(255, a),), halo=7)
    draw_text(ld, (MARGIN, 474), "DAYS",        font("xb", 100), GOLD+(_A(255, a),), halo=7)
    m = Image.new("L", ov.size, 0)
    ImageDraw.Draw(m).rectangle((0, 344, W, 344 + 254*k2), fill=255)
    ov.alpha_composite(Image.composite(lay, Image.new("RGBA", ov.size, (0,0,0,0)), m))
    k3 = out_c(clamp((t-0.75)/0.45))
    if k3 > 0:
        chip(ov, d, (MARGIN, 592), "SMARTPHONE SALE  ·  WHAT CHANGED",
             fsize=30, bg=(255,255,255), fg=INK, reveal=k3, alpha=_A(238, a))

def open_sub(ov, d, u, dur):
    t = _t(u, dur); a = _fade_tail(t, dur)
    k = out_c(clamp(t/0.45))
    chip(ov, d, (W/2, 224), "BIGGEST SALE OF THE YEAR", fsize=34, bg=GOLD, fg=INK,
         anchor="m", reveal=k, alpha=_A(245, a))
    rule(d, MARGIN, W-MARGIN, 326, (255,255,255,_A(70, a)), clamp((t-0.25)/0.6), thick=3, from_="c")

# ------------------------------------------------- originally: october -----
def orig_october(ov, d, u, dur):
    t = _t(u, dur); a = _fade_tail(t, dur, 0.35)
    k  = out_c(clamp((t-0.12)/0.55))
    bx = (MARGIN, 470, W-MARGIN, 1046)
    sh = shadow_layer(ov.size, bx, 34, blur=30, alpha=_A(150, k*a))
    ov.alpha_composite(Image.merge("RGBA", (Image.new("L", ov.size, 0),)*3 + (sh,)))
    off = int((1-k)*40)
    lay = Image.new("RGBA", ov.size, (0,0,0,0)); ld = ImageDraw.Draw(lay)
    rrect(ld, (bx[0], bx[1]+off, bx[2], bx[3]+off), 34,
          fill=(11, 24, 54, _A(249, a)), outline=(126, 156, 214, _A(110, a)), width=2)
    draw_text(ld, (bx[0]+46, bx[1]+54+off), "ORIGINAL PLAN", font("sb", 32), SOFT+(_A(255, a),), tracking=6.0)
    draw_text(ld, (bx[0]+46, bx[1]+110+off), "OCTOBER", font("xb", 104), WHITE+(_A(255, a),))
    ld.rectangle((bx[0]+46, bx[1]+244+off, bx[0]+46+430*out_c(clamp((t-0.9)/0.5)), bx[1]+248+off),
                 fill=GOLD+(_A(255, a),))
    # month grid
    g0x, g0y, cw, ch = bx[0]+50, bx[1]+300+off, 132, 62
    kg = clamp((t-0.75)/1.5)
    for i in range(20):
        col, row = i % 7, i // 7
        if row > 2: break
        if i/20.0 > kg: break
        x, y = g0x+col*cw, g0y+row*ch
        ld.rounded_rectangle((x, y, x+cw-14, y+ch-14), radius=9,
                             fill=(255, 255, 255, _A(34, a)))
    ov.alpha_composite(lay)
    ov.alpha_composite(cal_glyph(78, WHITE, _A(200, k*a)), (int(W-MARGIN-110), int(bx[1]+48+off)))

# ------------------------------------------------------ september 24 -------
def sept24_badge(ov, d, u, dur):
    t = _t(u, dur); a = _fade_tail(t, dur, 0.35)
    k = out_c(clamp(t/0.5))
    bh = 92
    lay = Image.new("RGBA", ov.size, (0,0,0,0)); ld = ImageDraw.Draw(lay)
    ld.rectangle((0, 168, W, 168+bh), fill=(7, 14, 30, _A(206, a)))
    ld.rectangle((0, 168+bh-4, W*out_c(clamp((t-0.2)/0.7)), 168+bh), fill=GOLD+(_A(255, a),))
    draw_text(ld, (MARGIN, 168+bh/2), "EARLY BIRD DEALS", font("b", 36), GOLD+(_A(255, a),),
              tracking=4.0, anchor="lm")
    draw_text(ld, (W-MARGIN, 168+bh/2), "FROM SEPTEMBER 24", font("sb", 34), WHITE+(_A(255, a),),
              tracking=2.0, anchor="rm")
    m = Image.new("L", ov.size, 0)
    ImageDraw.Draw(m).rectangle((0, 168, W*k, 168+bh+6), fill=255)
    ov.alpha_composite(Image.composite(lay, Image.new("RGBA", ov.size, (0,0,0,0)), m))

# ------------------------------------------------------------ wait ---------
def hold_on(ov, d, u, dur):
    t = _t(u, dur); a = _fade_tail(t, dur, 0.28)
    k = back_out(clamp(t/0.5))
    s = int(126*clamp(k, 0.1, 1.2))
    g = pause_glyph(max(8, s), WHITE, _A(225, a))
    ov.alpha_composite(g, (int(W/2-s/2), int(430-s/2)))
    pr = 0.5+0.5*math.sin(t*3.0)
    d.ellipse((W/2-s*0.78, 430-s*0.78, W/2+s*0.78, 430+s*0.78),
              outline=(255,255,255,_A(46*(1-pr*0.6), a)), width=3)

# ---------------------------------------------------------- iPhone 17 ------
def iphone_title(ov, d, u, dur):
    t = _t(u, dur); a = _fade_tail(t, dur, 0.30)
    _topscrim(ov, a)
    k  = out_q(clamp(t/0.55))
    x  = W-MARGIN + (1-k)*180
    fb = font("xb", 92)
    bw = max(text_w(d, "iPhone 17", fb), text_w(d, "EXPECTED DEAL", font("sb", 32), 6.0))
    d.rectangle((x-bw-34, 318, x-bw-26, 318+188), fill=GOLD+(_A(255, k*a),))
    draw_text(d, (x, 336), "EXPECTED DEAL", font("sb", 32), SOFT+(_A(255, k*a),), tracking=6.0, anchor="ra", halo=4)
    draw_text(d, (x, 386), "iPhone 17",     fb, WHITE+(_A(255, k*a),), anchor="ra", halo=7)

def iphone_title2(ov, d, u, dur):
    t = _t(u, dur); a = _fade_tail(t, dur, 0.26)
    _topscrim(ov, a)
    draw_text(d, (MARGIN, 250), "iPhone 17", font("xb", 62), WHITE+(_A(255, a),), halo=6)
    rule(d, MARGIN, MARGIN+300, 330, GOLD+(_A(255, a),), out_c(clamp(t/0.5)))
    k = clamp((t-0.25)/0.5)
    draw_text(d, (MARGIN, 358), "MAJOR DISCOUNT EXPECTED", font("sb", 30),
              SOFT+(_A(255, k*a),), tracking=5.0)

def iphone_price(ov, d, u, dur):
    t = _t(u, dur); a = _fade_tail(t, dur, 0.35)
    _topscrim(ov, a)
    draw_text(d, (MARGIN, 300), "iPhone 17", font("b", 54), WHITE+(_A(255, a),), tracking=1.5, halo=5)
    rule(d, MARGIN, MARGIN+240, 380, GOLD+(_A(255, a),), out_c(clamp(t/0.45)))
    k1 = clamp((t-0.35)/0.45)
    draw_text(d, (MARGIN, 424), "EXPECTED SALE PRICE", font("sb", 32),
              SOFT+(_A(255, k1*a),), tracking=6.0)
    # big reveal, masked upward
    k2 = out_q(clamp((t-0.62)/0.75))
    lay = Image.new("RGBA", ov.size, (0,0,0,0)); ld = ImageDraw.Draw(lay)
    draw_text(ld, (MARGIN, 486), "UNDER", font("xb", 76), GOLD+(_A(255, a),), tracking=4.0, halo=6)
    draw_text(ld, (MARGIN, 574), "₹80,000", font("xb", 158), WHITE+(_A(255, a),), halo=9)
    m = Image.new("L", ov.size, 0)
    ImageDraw.Draw(m).rectangle((0, 470, W, 470 + 320*k2), fill=255)
    ov.alpha_composite(Image.composite(lay, Image.new("RGBA", ov.size, (0,0,0,0)), m))
    k3 = out_c(clamp((t-1.35)/0.5))
    if k3 > 0:
        chip(ov, d, (MARGIN, 784), "EXPECTED  ·  NOT A CONFIRMED PRICE", fsize=28,
             bg=(255,255,255), fg=INK, reveal=k3, alpha=_A(210, a))

# ------------------------------------------------------------ Samsung ------
def samsung_title(ov, d, u, dur):
    t = _t(u, dur); a = _fade_tail(t, dur, 0.28)
    _topscrim(ov, a)
    k = out_q(clamp(t/0.5))
    x = MARGIN - (1-k)*160
    draw_text(d, (x, 330), "SAMSUNG", font("xb", 88), WHITE+(_A(255, k*a),), tracking=2.0, halo=7)
    rule(d, MARGIN, MARGIN+420, 452, GOLD+(_A(255, a),), out_c(clamp((t-0.25)/0.5)))
    draw_text(d, (MARGIN, 486), "IS ALSO IN THE GAME", font("sb", 32),
              SOFT+(_A(255, clamp((t-0.4)/0.5)*a),), tracking=6.0)

def _samsung_callout(ov, d, t, dur, model, price):
    a  = _fade_tail(t, dur, 0.35)
    k  = out_q(clamp(t/0.55))
    y, bh = 168, 96
    lay = Image.new("RGBA", ov.size, (0,0,0,0)); ld = ImageDraw.Draw(lay)
    ld.rectangle((0, y, W, y+bh), fill=(7, 14, 30, _A(214, a)))
    ld.rectangle((0, y+bh-4, W*out_c(clamp((t-0.2)/0.7)), y+bh), fill=GOLD+(_A(255, a),))
    draw_text(ld, (MARGIN, y+bh/2), model, font("b", 40), WHITE+(_A(255, a),),
              tracking=1.0, anchor="lm")
    pw = text_w(ld, price, font("xb", 42))
    draw_text(ld, (W-MARGIN-pw-18, y+bh/2), "TEASED AT", font("sb", 24),
              SOFT+(_A(235, a),), tracking=3.0, anchor="rm")
    draw_text(ld, (W-MARGIN, y+bh/2), price, font("xb", 42), GOLD+(_A(255, a),), anchor="rm")
    m = Image.new("L", ov.size, 0)
    ImageDraw.Draw(m).rectangle((0, y-6, W*k, y+bh+8), fill=255)
    ov.alpha_composite(Image.composite(lay, Image.new("RGBA", ov.size, (0,0,0,0)), m))

def s25(ov, d, u, dur):   _samsung_callout(ov, d, _t(u,dur), dur, "GALAXY S25",    "UNDER ₹60,000")
def s25fe(ov, d, u, dur): _samsung_callout(ov, d, _t(u,dur), dur, "GALAXY S25 FE", "UNDER ₹50,000")

# -------------------------------------------------------- bank offers ------
TERMS = "Offers subject to terms"
def _terms(ov, d, t, dur, a=1.0):
    k = clamp((t-0.30)/0.5)
    if k <= 0: return
    chip(ov, d, (W-MARGIN, 1128), TERMS, fsize=25, style="m", bg=(7, 14, 30),
         fg=(216, 228, 246), pad=(20, 11), tracking=0.6, anchor="r",
         reveal=1.0, alpha=_A(196, k*a))

def more_card(ov, d, u, dur):
    t = _t(u, dur); a = _fade_tail(t, dur, 0.22)
    k = out_q(clamp(t/0.55))
    c = card_shape((336, 212))
    c = c.rotate(-9+(1-k)*16, resample=Image.BICUBIC, expand=True)
    if a < 1.0 or k < 1.0:
        al = c.getchannel("A").point(lambda v: int(v*clamp(k)*a)); c.putalpha(al)
    ov.alpha_composite(c, (int(W/2-c.width/2+(1-k)*300), int(392-c.height/2)))


def banks_intro(ov, d, u, dur):
    t = _t(u, dur); a = _fade_tail(t, dur, 0.30)
    _topscrim(ov, a)
    k = out_c(clamp(t/0.5))
    chip(ov, d, (MARGIN, 236), "BANK OFFERS", fsize=36, bg=GOLD, fg=INK, reveal=k, alpha=_A(245, a))
    _terms(ov, d, t, dur, a)

def banks_10(ov, d, u, dur):
    t = _t(u, dur); a = _fade_tail(t, dur, 0.32)
    for i, (name, off) in enumerate([("AXIS BANK", 0.0), ("ICICI BANK", 0.30)]):
        k = out_q(clamp((t-off)/0.55))
        if k <= 0: continue
        y  = 300 + i*186
        bx = (MARGIN - (1-k)*220, y, MARGIN + 700 - (1-k)*220, y+150)
        lay = Image.new("RGBA", ov.size, (0,0,0,0)); ld = ImageDraw.Draw(lay)
        rrect(ld, bx, 24, fill=(7,14,30,_A(216, a)), outline=(132,158,214,_A(80,a)), width=2)
        ld.rectangle((bx[0], bx[1], bx[0]+8, bx[3]), fill=BLUE+(_A(255, a),))
        draw_text(ld, (bx[0]+36, bx[1]+30), name, font("sb", 34), SOFT+(_A(255, a),), tracking=3.0)
        draw_text(ld, (bx[0]+36, bx[1]+74), "10% OFF", font("xb", 58), GOLD+(_A(255, a),))
        ov.alpha_composite(lay)
    k3 = clamp((t-0.75)/0.5)
    if k3 > 0:
        chip(ov, d, (MARGIN, 676), "ADDITIONAL DISCOUNT  ·  ELIGIBLE CARDS", fsize=26,
             style="sb", bg=(7, 14, 30), fg=(226, 235, 250), reveal=k3, alpha=_A(210, a))
    _terms(ov, d, t, dur, a)

def instant10(ov, d, u, dur):
    t = _t(u, dur); a = _fade_tail(t, dur, 0.32)
    _topscrim(ov, a)
    k = out_q(clamp(t/0.6))
    lay = Image.new("RGBA", ov.size, (0,0,0,0)); ld = ImageDraw.Draw(lay)
    draw_text(ld, (MARGIN, 300), "FLIPKART AXIS BANK", font("sb", 32), SOFT+(_A(255, a),), tracking=5.0)
    draw_text(ld, (MARGIN, 348), "CREDIT CARD",        font("sb", 32), SOFT+(_A(255, a),), tracking=5.0)
    draw_text(ld, (MARGIN, 416), "INSTANT",            font("xb", 74), WHITE+(_A(255, a),), tracking=2.0, halo=6)
    draw_text(ld, (MARGIN, 500), "10% OFF",            font("xb", 118), GOLD+(_A(255, a),), halo=8)
    m = Image.new("L", ov.size, 0)
    ImageDraw.Draw(m).rectangle((0, 286, W*out_c(k), 640), fill=255)
    ov.alpha_composite(Image.composite(lay, Image.new("RGBA", ov.size, (0,0,0,0)), m))
    _terms(ov, d, t, dur, a)

def cashback10(ov, d, u, dur):
    t = _t(u, dur); a = _fade_tail(t, dur, 0.32)
    _topscrim(ov, a)
    k = out_q(clamp(t/0.55))
    y = 228 - (1-k)*50
    draw_text(d, (W/2, y), "super.money", font("b", 46), WHITE+(_A(255, k*a),), tracking=1.0, anchor="ma", halo=5)
    k2 = out_q(clamp((t-0.28)/0.6))
    lay = Image.new("RGBA", ov.size, (0,0,0,0)); ld = ImageDraw.Draw(lay)
    draw_text(ld, (W/2, 296), "10% CASHBACK", font("xb", 58), GOLD+(_A(255, a),),
              tracking=1.0, anchor="ma", halo=6)
    m = Image.new("L", ov.size, 0)
    ImageDraw.Draw(m).rectangle((0, 286, W, 286+90*k2), fill=255)
    ov.alpha_composite(Image.composite(lay, Image.new("RGBA", ov.size, (0,0,0,0)), m))
    _terms(ov, d, t, dur, a)

# -------------------------------------------------------- price caution ----
def remember(ov, d, u, dur):
    t = _t(u, dur); a = _fade_tail(t, dur, 0.25)
    ov.alpha_composite(Image.new("RGBA", ov.size, (5, 9, 20, _A(56, clamp(t/0.4)*a))))
    rule(d, MARGIN, W-MARGIN, 262, AMBER+(_A(255, a),), out_c(clamp(t/0.5)), thick=4)
    draw_text(d, (MARGIN, 288), "A QUICK NOTE", font("sb", 32),
              AMBER+(_A(255, clamp((t-0.2)/0.4)*a),), tracking=7.0)

def not_final(ov, d, u, dur):
    t = _t(u, dur); a = _fade_tail(t, dur, 0.35)
    ov.alpha_composite(Image.new("RGBA", ov.size, (5, 9, 20, _A(52, a))))
    rule(d, MARGIN, W-MARGIN, 262, AMBER+(_A(255, a),), 1.0, thick=4)
    draw_text(d, (MARGIN, 288), "A QUICK NOTE", font("sb", 32), AMBER+(_A(255, a),), tracking=7.0)
    k = out_q(clamp((t-0.15)/0.6))
    lay = Image.new("RGBA", ov.size, (0,0,0,0)); ld = ImageDraw.Draw(lay)
    draw_text(ld, (MARGIN, 366), "TEASED PRICES",  font("xb", 68), WHITE+(_A(255, a),), halo=6)
    draw_text(ld, (MARGIN, 452), "ARE NOT FINAL",  font("xb", 68), AMBER+(_A(255, a),), halo=6)
    m = Image.new("L", ov.size, 0)
    ImageDraw.Draw(m).rectangle((0, 352, W, 352+200*k), fill=255)
    ov.alpha_composite(Image.composite(lay, Image.new("RGBA", ov.size, (0,0,0,0)), m))

# ------------------------------------------------------------ october 9 ----
def oct9(ov, d, u, dur):
    t = _t(u, dur); a = _fade_tail(t, dur, 0.35)
    # recess the still first, so the title and the timeline both stay crisp
    k3 = out_c(clamp((t-1.85)/0.55))
    if k3 > 0:
        ov.alpha_composite(Image.new("RGBA", ov.size, (5, 10, 24, _A(168, k3*a))))
    _topscrim(ov, a)
    k = out_c(clamp(t/0.5))
    chip(ov, d, (MARGIN, 226), "MAIN SALE", fsize=34, bg=GOLD, fg=INK, reveal=k, alpha=_A(245, a))
    k2 = out_q(clamp((t-0.3)/0.7))
    lay = Image.new("RGBA", ov.size, (0,0,0,0)); ld = ImageDraw.Draw(lay)
    draw_text(ld, (MARGIN, 318), "OCTOBER 9", font("xb", 128), WHITE+(_A(255, a),), halo=9)
    m = Image.new("L", ov.size, 0)
    ImageDraw.Draw(m).rectangle((0, 300, W, 300+180*k2), fill=255)
    ov.alpha_composite(Image.composite(lay, Image.new("RGBA", ov.size, (0,0,0,0)), m))
    # two-stop timeline keeps the early-bird date and the main sale date apart
    if k3 <= 0: return
    py0, py1 = 742, 934
    lay = Image.new("RGBA", ov.size, (0,0,0,0)); ld = ImageDraw.Draw(lay)
    rrect(ld, (MARGIN, py0, W-MARGIN, py1), 26,
          fill=(9, 18, 42, _A(242, a)), outline=(126, 156, 214, _A(104, a)), width=2)
    y  = py0 + 66
    x0, x1 = MARGIN+112, W-MARGIN-112
    ld.rectangle((x0, y-2, x0+(x1-x0)*k3, y+2), fill=(150, 174, 212, _A(155, a)))
    for (px, lab, sub, hot) in [(x0, "SEP 24", "EARLY BIRD", False),
                                (x1, "OCT 9",  "MAIN SALE",  True)]:
        if (px-x0)/(x1-x0) > k3 + 0.02: continue
        col = GOLD if hot else (176, 196, 228)
        ld.ellipse((px-12, y-12, px+12, y+12), fill=col+(_A(255, a),))
        if hot: ld.ellipse((px-23, y-23, px+23, y+23), outline=col+(_A(110, a),), width=3)
        draw_text(ld, (px, y+32), lab, font("b", 36), col+(_A(255, a),), anchor="ma")
        draw_text(ld, (px, y+78), sub, font("sb", 24), (192, 208, 234)+(_A(220, a),),
                  tracking=2.5, anchor="ma")
    ov.alpha_composite(lay)

# ---------------------------------------------------------------- close ----
def flagships(ov, d, u, dur):
    t = _t(u, dur); a = _fade_tail(t, dur, 0.30)
    _topscrim(ov, a)
    k = out_c(clamp(t/0.5))
    rule(d, MARGIN, W-MARGIN, 250, GOLD+(_A(255, a),), k, thick=4)
    draw_text(d, (MARGIN, 282), "iPhone", font("b", 44), WHITE+(_A(255, k*a),), tracking=1.0, halo=5)
    draw_text(d, (W-MARGIN, 282), "SAMSUNG FLAGSHIP", font("b", 44), WHITE+(_A(255, k*a),),
              tracking=1.0, anchor="ra", halo=5)

def sept24_onwards(ov, d, u, dur):
    t = _t(u, dur); a = _fade_tail(t, dur, 0.26)
    _topscrim(ov, a)
    k = out_q(clamp(t/0.5))
    ov.alpha_composite(cal_glyph(74, WHITE, _A(235, k*a)), (int(W/2-37), int(292)))
    draw_text(d, (W/2, 396), "SEPTEMBER 24", font("xb", 64),
              GOLD+(_A(255, k*a),), tracking=1.0, anchor="ma", halo=7)

def app_ready(ov, d, u, dur):
    t = _t(u, dur); a = _fade_tail(t, dur, 0.26)
    # soft attention pulse over the app screen, no added copy
    for i in range(3):
        p = ((t*0.75) + i/3.0) % 1.0
        r = 70 + 190*p
        al = _A(120*(1-p)**1.4, a)
        if al <= 2: continue
        d.ellipse((W/2-r, 980-r, W/2+r, 980+r), outline=(255, 255, 255, al), width=3)

def closing(ov, d, u, dur):
    t = _t(u, dur); a = 1.0
    _topscrim(ov, a)
    k = out_c(clamp(t/0.7))
    rule(d, MARGIN, W-MARGIN, 236, GOLD+(_A(255, a),), k, thick=4, from_="c")
    draw_text(d, (W/2, 270), "BIG BILLION DAYS  ·  FESTIVE SMARTPHONE DEALS", font("sb", 30),
              SOFT+(_A(235, k),), tracking=3.0, anchor="ma", halo=4)

REG = {n: g for n, g in list(globals().items()) if callable(g) and not n.startswith("_")
       and n not in ("clamp","smooth","smoother","out_c","out_q","cine","back_out","lerp",
                     "text_w","draw_text","wrap","rrect","shadow_layer","vgrad","chip","rule",
                     "wipe_up","card_shape","pause_glyph","cal_glyph","font","Image","ImageDraw",
                     "ImageFilter","TERMS")}
