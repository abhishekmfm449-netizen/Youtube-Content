# Flipkart Big Billion Days 2026 — YouTube Short

**Deliverable:** `flipkart_bbd_2026_short.mp4`
**Caption track (separate, editable):** `flipkart_bbd_2026_short.srt`

---

## 1. Final specification

| | |
|---|---|
| Duration | **79.43 s** (2383 frames) |
| Resolution | 1080 × 1920 (9:16) |
| Frame rate | 30 fps, constant |
| Video | H.264 High @ L4.1, yuv420p, ~7.6 Mbps, `faststart` |
| Audio | AAC-LC 192 kbps, 48 kHz, stereo |
| Loudness | −14.0 LUFS integrated, true peak −2.8 dBFS, **0 clipped samples** |
| File size | 72 MB |

QC sweep on the finished file: no black frames, no frozen frames, no dropped
frames, no silence gap over 1.5 s, no clipping.

## 2. Voiceover

**There is no previous or reference voiceover anywhere in this repository.** The
three `.mp4` files carry only ambient sound design (verified by spectrogram — no
speech), and no audio file exists in the current tree or anywhere in the git
history. So the new voiceover could not be matched to a reference; it was built
to the written brief instead.

* **Tool:** Kokoro-82M (ONNX, running locally) via `kokoro-onnx`, espeak-ng
  phonemiser. Microsoft Edge TTS — which has purpose-built Indian English voices
  — is blocked by this environment's egress policy, as is Hugging Face.
* **Voice:** `hm_omega`, the deepest male voice in the Indian voice pack,
  reading English phonemes. Measured median pitch 124 Hz against 132 Hz for the
  alternative (`hm_psi`), so it is the lower of the two available.
* **Delivery:** speed 1.12 of the model's natural rate ≈ **168 words/minute** —
  a measured tech-news pace, not rushed. Every line was generated as its own
  clip so the pauses are placed deliberately rather than inherited from the
  model: longer holds after "September 24", "₹60,000", "10% cashback",
  "But remember…" and "you might want to wait."
* **Pitch:** shifted down a further **−0.67 semitone** (Rubber Band), taking the
  median from 129 Hz to 125 Hz — audibly deeper without sounding processed.
* **Pronunciation pass** (audio only — on-screen text keeps the numerals):
  "eighty thousand rupees", "sixty thousand rupees", "fifty thousand rupees",
  "ten percent", "iPhone seventeen", "Galaxy S twenty five",
  "S twenty five F E", "September twenty four", "October nine", and
  "I C I C I" spelled out (espeak mispronounces "ICICI" as a word).
* **Processing:** high-pass 75 Hz → light FFT denoise → corrective EQ (−2 dB at
  260 Hz, +1.2 dB at 1.9 kHz, +2.2 dB presence at 3.4 kHz, gentle air shelf) →
  de-esser → two-stage compression (3:1 then 6:1 peak catch) → loudness
  normalisation → limiter.

**Honest assessment of voice match:** this is a good, natural Indian-English
male read at the requested pace and depth, but with no reference file in the
repository there is nothing to claim a likeness to. If you have the previous
voiceover, send it and the voice can be re-matched.

## 3. Music and mix

No external audio sources are reachable from this environment, so the score is
synthesised from scratch (`production/make_music.py`): a filtered A-minor pad at
84 BPM, a sparse pluck motif on alternate bars, a soft sub pulse, and a slow air
layer. Arrangement gain follows the edit, lifting under the three motion peaks
and pulling right back for the price-caution section. Transition whooshes and
reveal ticks are synthesised the same way.

The bed is side-chained to the voice: measured at **21.8 dB below the narration
while it speaks** and 15 dB below in the pauses. It is present, never competing.

## 4. Repository assets used

All fifteen stills and all three clips were inspected. Thirteen stills and all
three clips are in the cut:

| Asset | Used for |
|---|---|
| `…8.15.00 PM.jpeg` | SEPTEMBER 24 festive calendar — early-bird reveal |
| `…8.15.01 PM.jpeg` | October backdrop; "keep your Flipkart app ready" |
| `…8.15.01 PM (1).jpeg` | "you might want to wait" |
| `…8.15.02 PM (2).jpeg` | Galaxy S25 / S25 FE with their UNDER ₹60,000 / ₹50,000 badges |
| `…8.15.02 PM.jpeg` | "if you're planning to buy a new smartphone" |
| `…8.15.03 PM.jpeg` | Opening — festive Flipkart sale atmosphere |
| `…8.15.03 PM (1).jpeg` | Axis Bank + ICICI Bank 10% offer |
| `…8.15.04 PM.jpeg` | Flipkart Axis Bank Credit Card — instant 10% |
| `…8.15.04 PM (1).jpeg` | super.money 10% cashback |
| `…8.15.05 PM (1).jpeg` | Teaser price → final price hidden (caution beat) |
| `…8.15.05 PM.jpeg` | "check final price" support shot |
| `…8.15.06 PM (1).jpeg` | iPhone 17 hero **and** the closing flagship shot |
| `…8.15.06 PM.jpeg` | STARTS ON OCTOBER 9 countdown |
| `…8.15.07 PM.jpeg` | Big Billion Days Early Bird in-app |
| `…8.14.45 PM.mp4` | "And there's more" — inset card |
| `…8.14.52 PM.mp4` | Opening hero; "September 24 onwards" |
| `…8.14.58 PM.mp4` | Samsung product rotation; closing flagship rotation |

**Not used:** `…8.15.02 PM (1).jpeg` (Galaxy S23 Ultra at ₹74,999 with a
"FLAT ₹60,000 OFF" banner). It shows a different handset at a hard price that
this story makes no claim about, and it would have read as a contradiction of
the S25 messaging.

All Flipkart, Samsung, Apple, Axis Bank, ICICI Bank, Visa, Mastercard and
super.money marks on screen come from these supplied stills. No logo was
redrawn, recreated or traced; every brand reference the motion graphics add is
plain type.

## 5. Visuals generated

AI video generation is blocked in this environment, so everything supplementary
is built as motion graphics over the supplied footage (`production/graphics.py`):

* Opening title build (masked wipe-up), festive sale chip.
* "ORIGINAL PLAN — OCTOBER" calendar card with a progressive month grid.
* Early-bird top bar with an animated gold underline.
* Pause glyph with a breathing ring for "you might want to wait".
* iPhone 17 title build, then the **UNDER ₹80,000** reveal with an
  "EXPECTED · NOT A CONFIRMED PRICE" tag.
* SAMSUNG title build; per-model bars reading "GALAXY S25 — TEASED AT
  UNDER ₹60,000" and "GALAXY S25 FE — TEASED AT UNDER ₹50,000".
* Payment-card illustration that flies in for "And there's more" (generic — no
  brand marks on it).
* AXIS BANK 10% OFF / ICICI BANK 10% OFF cards, INSTANT 10% OFF build,
  super.money 10% CASHBACK, each carrying **"Offers subject to terms"**.
* Amber "TEASED PRICES ARE NOT FINAL" caution treatment.
* OCTOBER 9 build plus a two-stop timeline — **SEP 24 · EARLY BIRD →
  OCT 9 · MAIN SALE** — so the two dates can never be read as one.
* Closing kicker over a slow push-in.

**Camera work** is varied per shot rather than one repeated Ken Burns: push-ins,
pull-outs, lateral pans, and a real 2.5D parallax (a blurred background plate
tracking at 55 % of the sharp foreground, composited through a soft mask).
Video clips appear as sharp 16:9 inset cards over their own blurred, graded
plate, which both avoids upscaling a 1024×576 source to full frame and gives the
edit a second visual register. Transitions are pushes, dissolves, whip cuts with
true directional blur, and snap cuts — matched to the beat, never templated.

## 6. Factual and accuracy guards

* No exact iPhone 17 price anywhere. The only figure shown is **UNDER ₹80,000**,
  tagged "EXPECTED · NOT A CONFIRMED PRICE".
* September 24 is labelled **EARLY BIRD** every time it appears; October 9 is
  labelled **MAIN SALE**. The timeline graphic states the relationship
  explicitly.
* Samsung figures carry "TEASED AT".
* Several supplied stills have unrelated products and prices baked into their
  mock app screens — a Pixel 8 Pro at ₹1,09,999, a smartwatch at ₹9,999, a
  "FLAT 40% OFF" card, an "EXTRA ₹5,000 OFF" card, a masked "$15.90". Those
  regions are blurred at source (`SOFTEN` in `production/timeline.py`) with
  feathered masks, so nothing on screen reads as a price or an offer the script
  does not state. The blur is shallow-depth-of-field in character, not a patch.
* Script wording is verbatim. The single on-screen deviation is "Super Money"
  rendered as **super.money** as instructed; the narration still says
  "Super Money".

## 7. Captions

Built as a separate layer (`production/captions.py`), never baked into a still
or a generated graphic, and driven by the voiceover's own per-line timings —
so they are frame-accurate by construction rather than eyeballed. The same
timings are exported to `flipkart_bbd_2026_short.srt` (28 cues, no overlaps) if
you want to restyle or re-time them elsewhere.

Style: Poppins SemiBold 54 px on a translucent panel, max two lines, held inside
a 862 px column centred at y = 1332 — clear of the Shorts bottom UI and mostly
clear of the right action rail. Gold highlighting is reserved for the items the
brief listed: September 24, ₹80,000, ₹60,000, ₹50,000, 10%, October 9.
Shot framings were adjusted per scene so captions do not sit on product names,
prices, logos or phone screens.

## 8. Things I could not do as specified

1. **Match the reference voice.** There is no voiceover in the repository —
   see §2. Reported rather than guessed at.
2. **"Slightly slower / lower than the previous voiceover."** Same reason: with
   no previous take to measure, I could only deliver an objectively unrushed
   168 wpm read and pitch it down 0.67 semitone from the model's own baseline.
3. **Duration.** The brief allowed "roughly 65–70 seconds". The final is 79.4 s.
   At 180 spoken words (≈ 205 once numbers are spoken in full) plus the
   deliberate pauses the brief asked for, 65–70 s would need ~200 wpm, which
   contradicts "prioritise clarity over speed" and "do not compress the
   narration unnaturally". I followed the clarity instruction and let the
   voiceover set the length. Say the word and I can re-cut at a faster read.
4. **AI-generated supplementary video.** Blocked in this environment, as the
   brief anticipated; all gaps are filled with motion graphics instead.
5. **Minor:** the AI-generated clips contain some garbled micro-text on the
   phone screens (an artifact of the source footage). Framings were chosen to
   keep it small and peripheral, but it cannot be removed entirely without
   dropping the clips.

## 9. Reproducing the edit

`production/` holds the whole pipeline: `script_data.py` (script + caption
chunks), `make_vo.py` (voiceover), `make_music.py` (score), `timeline.py` (shot
list, framings, blur regions), `design.py` / `graphics.py` (design system and
motion graphics), `captions.py` (caption layer), `render.py` (frame renderer).
`voiceover.wav` is the processed narration stem on its own.
