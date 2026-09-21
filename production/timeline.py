# -*- coding: utf-8 -*-
"""Shot list for the Short, anchored to the generated voiceover's chunk marks."""
import json, os
SP   = "/tmp/claude-0/-home-user-Youtube-Content/f48c739a-f44b-53f4-b1f5-20e1481d2735/scratchpad"
REPO = "/home/user/Youtube-Content"
OUT  = os.path.join(SP, "build")

_m = json.load(open(os.path.join(OUT, "vo_marks.json")))
MARKS = {m["id"]: m for m in _m["marks"]}
VO_DUR = _m["duration"]
VIDEO_DUR = round(VO_DUR + 0.80, 2)          # short clean tail after the last word

def S(cid): return MARKS[cid]["start"]
def E(cid): return MARKS[cid]["end"]

# ---- repository assets, named by what they actually show ------------------
IMG = {
 "sept24_festive" : "WhatsApp Image 2026-09-21 at 8.15.00 PM.jpeg",   # SEPTEMBER 24 early-bird calendar, diya/festive
 "woman_phone"    : "WhatsApp Image 2026-09-21 at 8.15.01 PM (1).jpeg",
 "app_browse"     : "WhatsApp Image 2026-09-21 at 8.15.01 PM.jpeg",   # festive app, "Early Bird Offer" chips
 "s23_banner"     : "WhatsApp Image 2026-09-21 at 8.15.02 PM (1).jpeg",# UNUSED - carries an unrelated exact price
 "samsung_duo"    : "WhatsApp Image 2026-09-21 at 8.15.02 PM (2).jpeg",# S25 UNDER 60k / S25 FE UNDER 50k
 "two_women"      : "WhatsApp Image 2026-09-21 at 8.15.02 PM.jpeg",
 "bank_cards"     : "WhatsApp Image 2026-09-21 at 8.15.03 PM (1).jpeg",# Axis + ICICI, 10% badges
 "offer_cloud"    : "WhatsApp Image 2026-09-21 at 8.15.03 PM.jpeg",   # floating offer cards, "DEALS LIVE NOW"
 "cashback"       : "WhatsApp Image 2026-09-21 at 8.15.04 PM (1).jpeg",# 10% CASHBACK + Super Money
 "axis_instant"   : "WhatsApp Image 2026-09-21 at 8.15.04 PM.jpeg",   # Flipkart Axis Bank CC, INSTANT 10% OFF
 "teaser_price"   : "WhatsApp Image 2026-09-21 at 8.15.05 PM (1).jpeg",# TEASER PRICE -> FINAL PRICE hidden
 "check_final"    : "WhatsApp Image 2026-09-21 at 8.15.05 PM.jpeg",   # "Check Final Price before Buying"
 "flagship_duo"   : "WhatsApp Image 2026-09-21 at 8.15.06 PM (1).jpeg",# iPhone + Samsung at a BBD store
 "oct9_countdown" : "WhatsApp Image 2026-09-21 at 8.15.06 PM.jpeg",   # STARTS ON OCTOBER 9
 "sept24_app"     : "WhatsApp Image 2026-09-21 at 8.15.07 PM.jpeg",   # EARLY BIRD / SEPTEMBER 24 in-app
}
VID = {
 "app_marble"  : "WhatsApp Video 2026-09-21 at 8.14.45 PM.mp4",
 "phone_rise"  : "WhatsApp Video 2026-09-21 at 8.14.52 PM.mp4",
 "rotate_mall" : "WhatsApp Video 2026-09-21 at 8.14.58 PM.mp4",
}
for k, v in IMG.items(): assert os.path.exists(os.path.join(REPO, v)), v
for k, v in VID.items(): assert os.path.exists(os.path.join(REPO, v)), v


# Regions (normalised x0,y0,x1,y1 in the source still) holding prices for
# products this story makes no claim about.  Blurred so nothing on screen reads
# as a price we did not state.
SOFTEN = {
 "offer_cloud"  : [(0.00, 0.000, 1.000, 0.440),                       # floating offer cards
                   (0.00, 0.430, 0.345, 1.000),                        # left coupons / % badge
                   (0.685, 0.430, 1.00, 1.000),                        # right coupons / % badge
                   (0.335, 0.830, 0.700, 1.000)],                       # coupons on the floor
 "app_browse"   : [(0.48, 0.395, 0.97, 0.500)],                      # generic listing price + % badge
 "axis_instant" : [(0.26, 0.310, 0.79, 0.412),                        # unrelated handset + price
                   (0.26, 0.506, 0.79, 0.660)],                       # order summary / order total
 "cashback"     : [(0.26, 0.318, 0.78, 0.362),                        # item + price
                   (0.28, 0.652, 0.76, 0.694)],                       # "PAY" amount
 "check_final"  : [(0.30, 0.520, 0.76, 0.568)],                       # unrelated smartwatch price
 "teaser_price" : [(0.30, 0.612, 0.74, 0.672)],                       # masked "final price" figure
}

# ---------------------------------------------------------------------------
# Shot dict keys
#   t0,t1   : absolute seconds
#   src     : ("img", key) | ("vid", key, src_start_seconds)
#   frame   : "full" (image fills 1080x1920) | "card" (16:9 inset over blurred plate)
#   move    : motion recipe, see renderer
#   trans   : incoming transition ("push_l","push_u","dissolve","whip","cut","pushin_cut")
#   gfx     : motion-graphics recipe id (or None)
# ---------------------------------------------------------------------------
SHOTS = [
 # ---------- MOTION PEAK 1 : OPENING -------------------------------------
 dict(t0=0.00, t1=2.16, src=("vid","phone_rise",5.60), frame="card",
      move=dict(k="push", z0=1.52, z1=1.72, cy=0.42, dy=-0.02, plate_z=(1.30,1.42)),
      trans="cut", gfx="open_title"),
 dict(t0=2.16, t1=4.19, src=("img","offer_cloud"), frame="full",
      move=dict(k="push", z0=1.50, z1=1.36, cx=0.55, cy=0.555),
      trans="whip", gfx="open_sub"),

 # ---------- ORIGINAL OCTOBER SCHEDULE ------------------------------------
 dict(t0=4.19, t1=8.72, src=("img","app_browse"), frame="full",
      move=dict(k="pan", z0=1.18, z1=1.24, cx0=0.44, cy0=0.34, cx1=0.56, cy1=0.42, blur=6.5, dim=0.48),
      trans="push_u", gfx="orig_october"),

 # ---------- SEPTEMBER 24 : EARLY BIRD ------------------------------------
 dict(t0=8.72, t1=10.65, src=("img","sept24_app"), frame="full",
      move=dict(k="push", z0=1.08, z1=1.22, cx=0.52, cy=0.46),
      trans="push_l", gfx=None),
 dict(t0=10.65, t1=13.81, src=("img","sept24_festive"), frame="full",
      move=dict(k="parallax", z0=1.24, z1=1.16, cx0=0.60, cy0=0.60, cx1=0.46, cy1=0.56),
      trans="push_l", gfx="sept24_badge"),

 # ---------- IF YOU'RE BUYING A PHONE ... WAIT -----------------------------
 dict(t0=13.81, t1=16.62, src=("img","two_women"), frame="full",
      move=dict(k="push", z0=1.30, z1=1.14, cx=0.54, cy=0.46),
      trans="dissolve", gfx=None),
 dict(t0=16.62, t1=18.31, src=("img","woman_phone"), frame="full",
      move=dict(k="pan", z0=1.20, z1=1.28, cx0=0.52, cy0=0.44, cx1=0.42, cy1=0.48),
      trans="push_l", gfx="hold_on"),

 # ---------- MOTION PEAK 2 : iPHONE 17 -------------------------------------
 dict(t0=18.31, t1=20.60, src=("img","flagship_duo"), frame="full",
      move=dict(k="parallax", z0=1.48, z1=1.66, cx0=0.30, cy0=0.60, cx1=0.36, cy1=0.56),
      trans="whip", gfx="iphone_title"),
 dict(t0=20.60, t1=22.30, src=("img","flagship_duo"), frame="full",
      move=dict(k="push", z0=1.88, z1=2.06, cx=0.345, cy=0.545),
      trans="pushin_cut", gfx="iphone_title2"),
 dict(t0=22.30, t1=26.43, src=("img","flagship_duo"), frame="full",
      move=dict(k="push", z0=1.62, z1=1.50, cx=0.35, cy=0.53, blur=2.6, dim=0.50),
      trans="push_u", gfx="iphone_price"),

 # ---------- SAMSUNG --------------------------------------------------------
 dict(t0=26.43, t1=28.43, src=("vid","rotate_mall",2.05), frame="card",
      move=dict(k="push", z0=1.02, z1=1.16, cy=0.46, plate_z=(1.34,1.46)),
      trans="whip", gfx="samsung_title"),
 dict(t0=28.43, t1=33.08, src=("img","samsung_duo"), frame="full",
      move=dict(k="pan", z0=1.64, z1=1.58, cx0=0.30, cy0=0.575, cx1=0.34, cy1=0.555),
      trans="push_l", gfx="s25"),
 dict(t0=33.08, t1=38.20, src=("img","samsung_duo"), frame="full",
      move=dict(k="pan", z0=1.58, z1=1.64, cx0=0.68, cy0=0.555, cx1=0.72, cy1=0.575),
      trans="push_l", gfx="s25fe"),

 # ---------- BANK / super.money OFFERS -------------------------------------
 dict(t0=38.20, t1=39.36, src=("vid","app_marble",0.02), frame="card",
      move=dict(k="push", z0=1.30, z1=1.16, cy=0.50, plate_z=(1.44,1.36)),
      trans="whip", gfx="more_card"),
 dict(t0=39.36, t1=43.17, src=("img","bank_cards"), frame="full",
      move=dict(k="push", z0=1.04, z1=1.18, cx=0.50, cy=0.48),
      trans="push_u", gfx="banks_intro"),
 dict(t0=43.17, t1=45.82, src=("img","bank_cards"), frame="full",
      move=dict(k="pan", z0=1.44, z1=1.54, cx0=0.42, cy0=0.470, cx1=0.58, cy1=0.470, dim=0.56, blur=2.2),
      trans="pushin_cut", gfx="banks_10"),
 dict(t0=45.82, t1=48.61, src=("img","axis_instant"), frame="full",
      move=dict(k="push", z0=1.36, z1=1.26, cx=0.50, cy=0.445),
      trans="push_l", gfx=None),
 dict(t0=48.61, t1=51.56, src=("img","axis_instant"), frame="full",
      move=dict(k="push", z0=1.54, z1=1.68, cx=0.52, cy=0.455, dim=0.54, blur=2.6),
      trans="pushin_cut", gfx="instant10"),
 dict(t0=51.56, t1=54.64, src=("img","cashback"), frame="full",
      move=dict(k="push", z0=1.34, z1=1.22, cx=0.50, cy=0.470),
      trans="push_l", gfx="cashback10"),

 # ---------- PRICE CAUTION (pace change) -----------------------------------
 dict(t0=54.64, t1=55.95, src=("img","teaser_price"), frame="full",
      move=dict(k="push", z0=1.06, z1=1.12, cx=0.50, cy=0.46),
      trans="dissolve", gfx="remember"),
 dict(t0=55.95, t1=59.88, src=("img","teaser_price"), frame="full",
      move=dict(k="parallax", z0=1.24, z1=1.34, cx0=0.52, cy0=0.505, cx1=0.48, cy1=0.525),
      trans="dissolve", gfx="not_final"),

 # ---------- OCTOBER 9 : MAIN SALE ------------------------------------------
 dict(t0=59.88, t1=61.68, src=("img","check_final"), frame="full",
      move=dict(k="pan", z0=1.34, z1=1.40, cx0=0.56, cy0=0.44, cx1=0.46, cy1=0.46, dim=0.66),
      trans="push_u", gfx=None),
 dict(t0=61.68, t1=65.29, src=("img","oct9_countdown"), frame="full",
      move=dict(k="push", z0=1.19, z1=1.07, cx=0.50, cy=0.495),
      trans="push_u", gfx="oct9"),

 # ---------- MOTION PEAK 3 : CLOSE -----------------------------------------
 dict(t0=65.29, t1=69.06, src=("vid","rotate_mall",5.70), frame="card",
      move=dict(k="push", z0=1.08, z1=1.22, plate_z=(1.32,1.44)),
      trans="whip", gfx="flagships"),
 dict(t0=69.06, t1=71.10, src=("vid","phone_rise",7.55), frame="card",
      move=dict(k="push", z0=1.44, z1=1.32, cy=0.40, plate_z=(1.42,1.34)),
      trans="push_l", gfx="sept24_onwards"),
 dict(t0=71.10, t1=73.19, src=("img","app_browse"), frame="full",
      move=dict(k="push", z0=1.46, z1=1.64, cx=0.50, cy=0.235),
      trans="push_l", gfx="app_ready"),
 dict(t0=73.19, t1=VIDEO_DUR, src=("img","flagship_duo"), frame="full",
      move=dict(k="push", z0=1.28, z1=1.10, cx=0.50, cy=0.535),
      trans="dissolve", gfx="closing"),
]

# ---- score dynamics: (time, gain).  Lifts under the three motion peaks. ----
MUSIC_CURVE = [
 (0.00,0.30),(0.35,0.95),(2.10,1.00),(4.19,0.62),(8.60,0.62),(8.90,0.86),
 (13.60,0.72),(16.50,0.60),(18.20,0.70),(20.50,0.95),(22.30,1.00),(26.30,0.90),
 (26.50,0.92),(28.40,0.74),(38.10,0.70),(38.40,0.84),(39.40,0.66),(54.30,0.66),
 (54.70,0.42),(59.70,0.46),(59.95,0.70),(65.10,0.74),(65.40,1.00),(73.10,1.00),
 (76.50,0.88),(78.30,0.52),(VIDEO_DUR,0.0),
]

# ---- SFX cues: "wu"/"wd" whoosh, "tk" tick ---------------------------------
SFX = (
 [dict(k="wu", t=s["t0"], g=0.9 if s["trans"] in ("whip","push_l","push_u") else 0.0)
  for s in SHOTS if s["trans"] in ("whip","push_l","push_u")] +
 [dict(k="wd", t=s["t0"], g=0.55) for s in SHOTS if s["trans"] == "pushin_cut"] +
 [dict(k="tk", t=x, g=g) for x, g in
   [(11.35,1.0),(11.62,0.7),(23.30,1.0),(23.62,0.7),(29.55,0.9),(34.20,0.9),
    (40.40,0.8),(43.95,0.9),(44.35,0.9),(49.45,0.9),(52.45,0.9),(62.60,1.0),
    (62.95,0.7),(69.70,0.8)]]
)

if __name__ == "__main__":
    json.dump(MUSIC_CURVE, open(os.path.join(OUT,"music_curve.json"),"w"))
    json.dump(SFX,         open(os.path.join(OUT,"sfx_cues.json"),"w"))
    gaps = []
    prev = 0.0
    for s in SHOTS:
        assert abs(s["t0"]-prev) < 1e-6, (s["t0"], prev)
        assert s["t1"] > s["t0"]
        prev = s["t1"]
    assert abs(prev-VIDEO_DUR) < 1e-6, (prev, VIDEO_DUR)
    print("shots:", len(SHOTS), " video dur:", VIDEO_DUR, " no gaps/overlaps OK")
