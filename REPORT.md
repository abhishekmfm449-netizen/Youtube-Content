# India HFT / Options Short — Production Report

**Deliverable:** `india_hft_options_short.mp4`

| | |
|---|---|
| Duration | **77.83 s** (1 min 18 s) |
| Resolution | 1080 × 1920 (9:16 vertical) |
| Frame rate | 30 fps (constant, 2 335 frames) |
| Video | H.264 High profile, yuv420p, ~7.84 Mbps |
| Audio | AAC-LC, 48 kHz stereo, 178 kbps |
| Loudness | −14.4 LUFS integrated, −4.3 dBTP |
| File size | 74.4 MB |

---

## 1. What was actually in the repository

This is the most important finding, so it is first.

**The repository does not contain a voiceover file.** There is no `.mp3`, `.wav`,
`.m4a`, `.aac`, `.ogg` or `.flac` anywhere in the working tree or anywhere in the
git history. Two of the three `.mp4` clips carry ~10 s of ambient sound from a
video generator; the third is silent. None of them contains narration.

**None of the 15 images or 3 video clips relate to this topic.** Every asset in
the repository belongs to a *different* project — a Flipkart "Big Billion Days"
festive e-commerce video:

| Asset | Content |
|---|---|
| 15 × `WhatsApp Image 2026-09-21 …jpeg` (768×1376) | Flipkart / "Utsav Sale" app screens, Diwali decor, phones in hand, bank-card offers, smartwatch deal pages |
| 3 × `WhatsApp Video 2026-09-21 …mp4` (1024×576, 10 s) | Flipkart Big Billion Days app promos, a phone on a rotating podium with "−90%" |

There is no trader, no NIFTY/BANK NIFTY, no option chain, no server or data-centre
footage, no `$33 BILLION` visual and no `$7 BILLION` visual in the repository.

Per the brief's instruction not to stop for assets, **the entire short was built
from scratch.** No repository asset was used, because using festive e-commerce
footage under narration about SEBI derivative losses would have been actively
misleading.

## 2. Audio check (transcription vs. script)

Because no voiceover existed, the narration was **synthesised from the script
verbatim** using a neural TTS voice (Piper, `en-US-ryan-high`), then mastered
(85 Hz high-pass → light compression → EBU R128 normalisation to −14 LUFS /
−1.5 dBTP → 48 kHz stereo).

The spoken audio therefore matches the script word for word by construction, and
this was verified programmatically against the original text. **No word of the
script was changed, shortened, rewritten or rearranged.** The only differences
are pronunciation forms and caption capitalisation:

| Script | Spoken as | Caption shows | Why |
|---|---|---|---|
| `$33 billion` | "thirty three billion dollars" | `$33 BILLION` | numeral → speech |
| `$7 billion` | "seven billion dollars" | `$7 BILLION` | numeral → speech |
| `March 2025` | "March twenty twenty five" | `March 2025` | numeral → speech |
| `algorithm-driven`, `ultra-fast`, `High-frequency` | hyphens dropped | hyphens kept | hyphens confuse the TTS front-end |
| `microseconds or even faster —` | comma in place of the dash | em dash kept | dash → natural pause |
| `options market`, `algorithms`, `technology gap`, `Speed.` | unchanged | `OPTIONS MARKET`, `ALGORITHMS`, `TECHNOLOGY GAP`, `SPEED` | requested keyword highlighting |

Captions were then aligned to the **actual rendered audio**, not to an estimate:
each of the 59 caption phrases is paired with its exact spoken fragment, weighted
by syllable count, and each boundary is snapped to the nearest real low-energy
point (pause) in the waveform within ±160 ms.

## 3. Assets used

**From the repository: none** (see §1).

**Created for this video:** every frame. 2 335 frames were rendered
programmatically at 1080×1920 — a custom compositor (NumPy + Pillow + a hand-built
perspective/lighting/bloom/grain pipeline), driven by the narration timeline.

Reusable components written for it: back-lit human silhouette with rim lighting,
server-rack wall with live status LEDs, one-point-perspective data-centre
corridor, candlestick engine, NIFTY/BANK NIFTY option chain, market-depth ladder,
fibre-optic bundle with travelling pulses, digit rain, packet streams, radial
speed streaks, animated count-up stat cards, phone mock-up with live chart.

Typography: Montserrat (captions, stat numbers) and Inter (UI/labels), fetched as
variable fonts.

## 4. Scene map — every line has a matched visual

| # | Time (s) | Visual |
|---|---|---|
| 1 | 00.00–03.61 | Opening — back-lit retail trader with glowing phone, wall of trading servers behind |
| 2 | 03.61–08.18 | NIFTY · BANK NIFTY option chain, CALL/STRIKE/PUT, live-flickering premiums |
| 3 | 08.18–12.58 | Algorithms — the human dissolves into a data-centre corridor + data streams |
| 4 | 12.58–14.18 | "The numbers are crazy" — accelerating numeric storm |
| 5 | 14.18–24.21 | **$33 BILLION** stat card, count-up, held visible, descending loss bars, sourced |
| 6 | 24.21–32.85 | **$7 BILLION** stat card — different colour, rising bars, "A SEPARATE FIGURE" chip |
| 7 | 32.85–35.34 | "How do firms get the advantage?" — question beat inside the corridor |
| 8 | 35.34–36.27 | **SPEED** — radial light-speed burst, hardest cut in the video |
| 9 | 36.27–44.05 | Microseconds — live µs latency readout vs. the retail phone chart ("YOU") |
| 10 | 44.05–51.08 | Technology investment — deep data-centre corridor, fibre bundles, infra labels |
| 11 | 51.08–53.02 | "But here's the important part" — pace slows, calm concentric pulse |
| 12 | 53.02–57.44 | Not stealing — two equal, neutral order-flow panels, no theft imagery |
| 13 | 57.44–61.96 | Liquidity — balanced two-sided market-depth ladder |
| 14 | 61.96–67.91 | **TECHNOLOGY GAP** — split screen: one trader + one chart ⟷ racks of servers |
| 15 | 67.91–70.48 | Sudden stock move — candlestick chart spikes |
| 16 | 70.48–71.43 | "Remember:" — dark pulse beat |
| 17 | 71.43–77.85 | Final — trader on the phone, infrastructure operating behind, slow push-in |

Transitions: hard cuts on the beat for pace, dissolves (0.18–0.34 s) on the calm
sections, and white flashes into `$33 BILLION`, `SPEED` and `MICROSECONDS`.
All still elements carry continuous camera movement (push-ins, parallax drifts,
layered depth-of-field), so nothing reads as a slideshow.

## 5. Captions

59 phrase captions, Montserrat Bold/ExtraBold, 64 px body / 78 px highlighted,
heavy dark stroke plus a soft gradient scrim, pop-in on each cue. Positioned at
66.5 % height — clear of the YouTube Shorts bottom UI and the right-hand action
rail.

Highlighted as requested: `OPTIONS MARKET`, `ALGORITHMS`, `$33 BILLION`,
`$7 BILLION`, `SPEED`, `MICROSECONDS`, `TECHNOLOGY GAP` (amber for the money
figures and the gap, cyan for the technology terms).

`india_hft_options_short.srt` is included as a sidecar if you want to edit the
captions or upload them separately.

## 6. Factual presentation

- The two figures are **never** connected. They appear in separate scenes with
  different colour languages (amber vs. cyan), different chart directions and no
  arrow, flow or morph between them.
- The `$7 BILLION` card carries an explicit **"A SEPARATE FIGURE"** chip on screen.
- Both cards are captioned `SEBI study, reported by Bloomberg`.
- Scene 12 deliberately avoids any theft imagery and slows the pace, as briefed.
- Scene 13 shows a balanced two-sided book, so HFT is not framed as purely negative.
- **No statistic, company, dollar amount or claim was invented.** The only
  on-screen numbers beyond the script are illustrative UI texture (option-chain
  premiums, depth quantities, a ticking latency readout), which are low-contrast,
  unattributed and never presented as findings.

## 7. Quality checks run

- **Black-frame detection:** only 0.000–0.133 s — the intended fade-in. No blank
  frames anywhere in the body of the video.
- **Silence detection:** only 75.80–77.82 s — the intended tail under the final
  held shot. No dead air mid-narration.
- **Loudness:** −14.4 LUFS / −4.3 dBTP, on YouTube's delivery target.
- **Visual review:** all 17 scenes inspected at full resolution, plus a 24-point
  contact sheet sampled across the finished file — captions in sync, no awkward
  transitions, no mismatched visuals.

## 8. Skipped / not done, and why

| Item | Status | Reason |
|---|---|---|
| Use the uploaded voiceover | **Not possible** | No voiceover file exists in the repo or its history. Narration was synthesised from your exact script instead. |
| Use the uploaded images and clips | **Deliberately not used** | All 18 assets are Flipkart e-commerce material from an unrelated project. Using them would have contradicted the narration. |
| Background music | **Not added** | The brief said to add music only if suitable music already existed in the repo. None does — the only audio present is ~10 s of ambient sound inside two off-topic promo clips. |

## 9. If you have the real voiceover

Drop the file in and the video can be rebuilt against it: the timeline, the
caption alignment and every scene duration are derived automatically from the
narration waveform, so only the audio needs to change. The same applies if you
upload on-topic imagery — any scene can take a real photo or clip in place of the
generated background.
