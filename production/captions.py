# -*- coding: utf-8 -*-
"""Caption layer - a separate, editable track driven by the voiceover marks.
   Nothing is burned into the source images or the generated graphics."""
import re, json, os
from PIL import Image, ImageDraw, ImageFilter
from design import *

# Only the items the brief calls out get the gold treatment.
HI = [
    r"SEPTEMBER\s+24", r"September\s+24", r"October\s+9", r"OCTOBER\s+9",
    r"₹80,000", r"₹60,000", r"₹50,000", r"10%",
]
HI_RE = re.compile("(" + "|".join(HI) + ")")

FS   = 54
LEAD = 1.24
FADE = 0.12

def build(marks, video_dur):
    """-> list of caption events with hold-until-next-start timing."""
    ev = []
    for i, m in enumerate(marks):
        nxt = marks[i+1]["start"] if i+1 < len(marks) else None
        t0  = m["start"] - 0.10
        t1  = (nxt - 0.13) if nxt is not None else min(m["end"] + 0.85, video_dur)
        ev.append(dict(text=m["caption"], t0=max(0.0, t0), t1=t1, id=m["id"]))
    return ev

def _tokens(line):
    out, last = [], 0
    for mt in HI_RE.finditer(line):
        if mt.start() > last: out.append((line[last:mt.start()], False))
        out.append((mt.group(0), True)); last = mt.end()
    if last < len(line): out.append((line[last:], False))
    return out or [(line, False)]

_cache = {}
def render(ov, d, ev, t):
    """Draw the active caption (pill + text) onto the overlay."""
    if t < ev["t0"] or t >= ev["t1"]: return
    local = t - ev["t0"]
    span  = ev["t1"] - ev["t0"]
    a = clamp(local/FADE) * clamp((span-local)/FADE)
    if a <= 0.01: return
    pop  = out_c(clamp(local/0.20))
    dy   = (1-pop)*12

    key = ev["id"]
    if key not in _cache:
        f = font("sb", FS)
        lines = wrap(d, ev["text"], f, CAP_MAXW)
        _cache[key] = (lines, [text_w(d, l, f) for l in lines])
    lines, widths = _cache[key]
    f  = font("sb", FS)
    lh = int(FS*LEAD)
    blockh = lh*len(lines)
    top    = CAP_Y - blockh/2 + dy
    maxw   = max(widths)

    padx, pady = 30, 18
    bx = (W/2 - maxw/2 - padx, top - pady, W/2 + maxw/2 + padx, top + blockh + pady - 8)
    lay = Image.new("RGBA", ov.size, (0, 0, 0, 0))
    ld  = ImageDraw.Draw(lay)
    ld.rounded_rectangle(bx, radius=22, fill=(6, 12, 26, int(150*a)))
    ld.rounded_rectangle(bx, radius=22, outline=(255, 255, 255, int(26*a)), width=2)

    for i, line in enumerate(lines):
        y = top + i*lh + lh/2 - 2
        x = W/2 - widths[i]/2
        for tok, hot in _tokens(line):
            if not tok: continue
            col = GOLD if hot else WHITE
            ld.text((x+2, y+3), tok, font=f, fill=(0, 0, 0, int(150*a)), anchor="lm")
            ld.text((x, y), tok, font=f, fill=col+(int(255*a),), anchor="lm")
            x += ld.textlength(tok, font=f)
    ov.alpha_composite(lay)

def to_srt(events, path):
    """Writes the caption track as a standalone, editable .srt."""
    def ts(x):
        h = int(x//3600); m = int(x % 3600//60); s = x % 60
        return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")
    with open(path, "w") as fh:
        for i, e in enumerate(events, 1):
            end = e["t1"]
            if i < len(events):
                end = min(end, events[i]["t0"] - 0.001)   # never overlap the next cue
            fh.write(f"{i}\n{ts(e['t0'])} --> {ts(end)}\n{e['text']}\n\n")
