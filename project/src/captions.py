"""Burned-in captions, Shorts-tuned.

Rules this enforces:
  * never more than a few words on screen at once
  * large, heavy, high contrast, inside the reserved caption band
  * key phrases pick up the system accent colour rather than a highlight box
  * a word appears when it is spoken, derived from the line's own timing

Timings come from the line boundaries in timeline.json.  Within a line, words
are distributed by syllable weight rather than character count, which tracks a
real read far better than an even split.
"""
from __future__ import annotations

import re

from design import CAP_MID, INK, RH, RW, SS, SYS, f_caption, text_size
from script import EMPHASIS

MAX_CHARS = 26          # per caption card; keeps cards to ~3-5 words
MIN_CARD = 0.45         # seconds; anything shorter reads as a flicker
FONT_PX = 62            # output pixels
LINE_GAP = 1.16

_VOWELS = re.compile(r"[aeiouy]+", re.I)


def syllables(word: str) -> float:
    core = re.sub(r"[^a-z]", "", word.lower())
    if not core:
        return 1.0
    n = len(_VOWELS.findall(core))
    if core.endswith("e") and n > 1:
        n -= 1
    return float(max(1, n))


def _emphasis_spans(textline: str) -> list[tuple[int, int]]:
    low = textline.lower()
    spans = []
    for phrase in EMPHASIS:
        start = 0
        p = phrase.lower()
        while True:
            i = low.find(p, start)
            if i < 0:
                break
            spans.append((i, i + len(p)))
            start = i + 1
    return spans


def split_cards(line_text: str) -> list[list[str]]:
    """Break a narration line into caption cards of a few words each."""
    words = line_text.split()
    cards, cur, n = [], [], 0
    for w in words:
        add = len(w) + (1 if cur else 0)
        if cur and n + add > MAX_CHARS:
            cards.append(cur)
            cur, n = [w], len(w)
        else:
            cur.append(w)
            n += add
    if cur:
        cards.append(cur)
    return cards


def build(timeline: dict) -> list[dict]:
    """Expand the line timeline into per-word caption events."""
    out = []
    for ln in timeline["lines"]:
        spans = _emphasis_spans(ln["text"])
        # character offset of every word, so emphasis can be matched by position
        offsets, pos = [], 0
        for w in ln["text"].split():
            i = ln["text"].find(w, pos)
            offsets.append(i)
            pos = i + len(w)

        cards = split_cards(ln["text"])
        weights = [sum(syllables(w) for w in c) for c in cards]
        total = sum(weights) or 1.0
        span = ln["end"] - ln["start"]

        wi, t = 0, ln["start"]
        for card, wgt in zip(cards, weights):
            cdur = span * wgt / total
            wwts = [syllables(w) for w in card]
            wtot = sum(wwts) or 1.0
            wt = t
            words = []
            for w, ww in zip(card, wwts):
                off = offsets[wi]
                em = any(a <= off < b for a, b in spans)
                words.append(dict(word=w, at=round(wt, 3), emphasis=em))
                wt += cdur * ww / wtot
                wi += 1
            out.append(dict(start=round(t, 3), end=round(t + cdur, 3),
                            text=" ".join(card), words=words))
            t += cdur

    # A card shorter than MIN_CARD flashes rather than reads; fold it back into
    # the one before it (within the same narration line only).
    merged = []
    for c in out:
        if (merged and c["end"] - c["start"] < MIN_CARD
                and abs(merged[-1]["end"] - c["start"]) < 1e-3
                and len(merged[-1]["words"]) + len(c["words"]) <= 7):
            merged[-1]["end"] = c["end"]
            merged[-1]["words"] += c["words"]
            merged[-1]["text"] += " " + c["text"]
        else:
            merged.append(c)
    return merged


def _wrap(d, words, fnt, max_w):
    lines, cur = [], []
    for w in words:
        trial = cur + [w]
        if cur and text_size(d, " ".join(x["word"] for x in trial), fnt)[0] > max_w:
            lines.append(cur)
            cur = [w]
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def draw(layer_draw, cards, t):
    """Draw the active caption card at time t onto a render-scale layer."""
    card = None
    for c in cards:
        if c["start"] - 0.05 <= t < c["end"] + 0.10:
            card = c
            break
    if card is None:
        return

    fnt = f_caption(FONT_PX * SS, 800)
    d = layer_draw
    max_w = RW * 0.84
    lines = _wrap(d, card["words"], fnt, max_w)

    lh = FONT_PX * SS * LINE_GAP
    total_h = lh * len(lines)
    y = RH * CAP_MID - total_h / 2

    # a short pop as the card lands, then hold
    age = t - card["start"]
    pop = 1.0 if age > 0.16 else 0.90 + 0.10 * (age / 0.16)
    fade = min(1.0, max(0.0, (t - card["start"] + 0.05) / 0.12))
    fade *= min(1.0, max(0.0, (card["end"] + 0.10 - t) / 0.10))
    if fade <= 0.01:
        return

    # A soft, wide gradient under the band.  Nearly invisible on the dark
    # scenes, and the difference between readable and not over the bright city
    # plates - which is what a Short gets watched on, on a phone, in daylight.
    band_h = total_h + 76 * SS
    by = y - 38 * SS
    steps = 20
    for i in range(steps):
        fr = i / (steps - 1)
        edge = min(fr / 0.32, (1 - fr) / 0.32, 1.0)
        d.rectangle([0, by + band_h * fr, RW, by + band_h * (fr + 1 / steps) + 1],
                    fill=(3, 6, 10, int(96 * fade * max(0.0, edge))))

    for ln_words in lines:
        s = " ".join(x["word"] for x in ln_words)
        lw = text_size(d, s, fnt)[0] * pop
        x = RW / 2 - lw / 2
        f2 = f_caption(int(FONT_PX * SS * pop), 800)
        for wd in ln_words:
            spoken = t >= wd["at"] - 0.02
            if wd["emphasis"]:
                col = SYS if spoken else (60, 96, 104)
            else:
                col = INK if spoken else (104, 118, 132)
            a = int(255 * fade)
            # readability plate: a soft dark halo, not a hard box
            for ox, oy in ((-3, 0), (3, 0), (0, -3), (0, 3), (-2, -2), (2, 2), (-2, 2), (2, -2)):
                d.text((x + ox * SS, y + oy * SS), wd["word"], font=f2,
                       fill=(3, 6, 10, int(a * 0.80)), anchor="la")
            d.text((x, y), wd["word"], font=f2, fill=col + (a,), anchor="la")
            x += d.textlength(wd["word"] + " ", font=f2)
        y += lh * pop


def to_srt(cards) -> str:
    def ts(v):
        h = int(v // 3600)
        m = int(v % 3600 // 60)
        s = v % 60
        return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")

    out = []
    for i, c in enumerate(cards, 1):
        out.append(f"{i}\n{ts(c['start'])} --> {ts(c['end'])}\n{c['text']}\n")
    return "\n".join(out)
