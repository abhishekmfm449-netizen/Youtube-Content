# -*- coding: utf-8 -*-
"""Synthesised, deliberately subtle score + transition SFX for the Short."""
import numpy as np, soundfile as sf, json, os
SP  = "/tmp/claude-0/-home-user-Youtube-Content/f48c739a-f44b-53f4-b1f5-20e1481d2735/scratchpad"
OUT = os.path.join(SP, "build")
SR  = 48000
DUR = float(os.environ.get("VID_DUR", "79.4"))
N   = int(DUR * SR)
rng = np.random.default_rng(7)
t   = np.arange(N) / SR

def env_adsr(n, a, d, s, r, peak=1.0, sus=None):
    sus = s if sus is None else sus
    e = np.zeros(n)
    ai, di, ri = int(a*SR), int(d*SR), int(r*SR)
    ai = min(ai, n); e[:ai] = np.linspace(0, peak, ai)
    di = min(di, n-ai); e[ai:ai+di] = np.linspace(peak, sus, di)
    body = n - ai - di - ri
    if body > 0: e[ai+di:ai+di+body] = sus
    if ri > 0: e[max(0,n-ri):] = np.linspace(e[max(0,n-ri-1)], 0, min(ri, n))
    return e

def onepole_lp(x, cutoff):
    a = np.exp(-2*np.pi*cutoff/SR); y = np.empty_like(x); acc = 0.0
    for i in range(len(x)):
        acc = a*acc + (1-a)*x[i]; y[i] = acc
    return y

def biquad_lp(x, fc, q=0.707):
    w0 = 2*np.pi*fc/SR; al = np.sin(w0)/(2*q); c = np.cos(w0)
    b0,b1,b2 = (1-c)/2, 1-c, (1-c)/2
    a0,a1,a2 = 1+al, -2*c, 1-al
    b0,b1,b2,a1,a2 = b0/a0,b1/a0,b2/a0,a1/a0,a2/a0
    y = np.zeros_like(x); x1=x2=y1=y2=0.0
    for i in range(len(x)):
        v = b0*x[i]+b1*x1+b2*x2-a1*y1-a2*y2
        x2,x1 = x1,x[i]; y2,y1 = y1,v; y[i]=v
    return y

def note(freq, dur, kind="pad", amp=0.2, detune=0.0):
    n = int(dur*SR); tt = np.arange(n)/SR
    if kind == "pad":
        sig = np.zeros(n)
        for k, (mul, a) in enumerate([(1,1.0),(2,0.34),(3,0.16),(4,0.09),(5,0.05)]):
            det = 1 + detune*((-1)**k)*0.0016
            sig += a*np.sin(2*np.pi*freq*mul*det*tt + k)
        sig /= 1.65
        e = env_adsr(n, 0.9, 0.5, 0.75, 1.1)
        return sig*e*amp
    if kind == "pluck":
        sig = (np.sin(2*np.pi*freq*tt) + 0.25*np.sin(2*np.pi*freq*2*tt)
               + 0.1*np.sin(2*np.pi*freq*3*tt))
        e = np.exp(-tt*5.5)
        return sig*e*amp
    if kind == "sub":
        f = freq*np.exp(-tt*2.2)*0.06 + freq
        sig = np.sin(2*np.pi*np.cumsum(f)/SR)
        e = np.exp(-tt*4.0)
        return sig*e*amp
    raise ValueError(kind)

def place(buf, sig, at):
    i = int(at*SR); j = min(len(buf), i+len(sig))
    if i >= len(buf) or j <= i: return
    buf[i:j] += sig[:j-i]

# ---------------- harmony -------------------------------------------------
def hz(semi): return 440.0*2**(semi/12.0)
# A minor family, voiced low and wide.  (root, third, fifth) in semitones from A4
PROG = [
    [-24,-12,-5, 0],   # Am
    [-24,-12,-5, 3],   # Am add-b3
    [-22,-10,-3, 2],   # Bdim-ish / F
    [-27,-15,-8,-3],   # F
    [-25,-13,-6,-1],   # G
]
BPM = 84.0
BEAT = 60.0/BPM
BAR  = 4*BEAT            # 2.857 s

pad   = np.zeros(N)
pluck = np.zeros(N)
sub   = np.zeros(N)

bar = 0; tt = 0.0
while tt < DUR:
    ch = PROG[bar % len(PROG)]
    for k, s in enumerate(ch):
        place(pad, note(hz(s), BAR*1.12, "pad", amp=0.085 if k else 0.10, detune=1.0), tt)
    # sparse pluck motif, only on alternate bars -> keeps it from becoming a loop
    if bar % 2 == 0:
        for bi, s in [(0, ch[3]+12), (1.5, ch[2]+12), (2.5, ch[3]+12), (3.5, ch[1]+24)]:
            place(pluck, note(hz(s), 1.0, "pluck", amp=0.042), tt+bi*BEAT)
    # heartbeat sub on 1 and 3
    place(sub, note(hz(ch[0])/2, 0.55, "sub", amp=0.16), tt)
    place(sub, note(hz(ch[0])/2, 0.45, "sub", amp=0.10), tt+2*BEAT)
    tt += BAR; bar += 1

pad   = biquad_lp(pad[:N],  1800)
pluck = biquad_lp(pluck[:N], 4200)
sub   = biquad_lp(sub[:N],   150)

# gentle air layer so the bed is not purely tonal
air = rng.normal(0, 1, N)
air = biquad_lp(air, 900) * 0.010
air *= (0.6 + 0.4*np.sin(2*np.pi*t/17.0))

music = 0.95*pad + 1.0*pluck + 1.0*sub + air

# slow arrangement dynamics: lift into the three motion peaks, pull back elsewhere
peaks = json.load(open(os.path.join(OUT, "music_curve.json")))
curve = np.interp(t, [p[0] for p in peaks], [p[1] for p in peaks])
music *= curve

# ---------------- transition SFX -----------------------------------------
def whoosh(dur=0.55, up=True, amp=0.22):
    n = int(dur*SR); tt2 = np.arange(n)/SR
    nz = rng.normal(0, 1, n)
    f = np.linspace(400, 3000, n) if up else np.linspace(2600, 500, n)
    y = biquad_lp(nz, 2500) * (np.sin(np.pi*tt2/dur)**1.6)
    y *= np.interp(f, [400, 3000], [0.8, 1.0])
    return y*amp

def tick(amp=0.12):
    n = int(0.09*SR); tt2 = np.arange(n)/SR
    y = (np.sin(2*np.pi*1450*tt2) + 0.5*np.sin(2*np.pi*2900*tt2))*np.exp(-tt2*48)
    return y*amp

sfx = np.zeros(N)
cues = json.load(open(os.path.join(OUT, "sfx_cues.json")))
W_UP, W_DN, TICK = whoosh(0.55, True), whoosh(0.60, False), tick()
for c in cues:
    if   c["k"] == "wu": place(sfx, W_UP*c.get("g",1.0),  c["t"]-0.22)
    elif c["k"] == "wd": place(sfx, W_DN*c.get("g",1.0),  c["t"]-0.26)
    elif c["k"] == "tk": place(sfx, TICK*c.get("g",1.0),  c["t"])

bed = music + sfx
bed = np.tanh(bed*1.2)/1.2
# stereo, slightly widened pad
L = bed.copy(); R = bed.copy()
d = int(0.008*SR)
R[d:] += 0.16*pad[:-d]*curve[:-d]; L += 0.16*pad*curve*0.0
st = np.stack([L, R], axis=1)
st /= max(1.0, np.abs(st).max()/0.82)
sf.write(os.path.join(OUT, "music_bed.wav"), st, SR)
print("music bed:", round(len(st)/SR, 2), "s  peak", round(float(np.abs(st).max()), 3))
