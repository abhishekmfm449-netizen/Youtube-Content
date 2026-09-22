# -*- coding: utf-8 -*-
import sys, os, json, numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from script_data import CHUNKS
from kokoro_onnx import Kokoro

SP   = "/tmp/claude-0/-home-user-Youtube-Content/f48c739a-f44b-53f4-b1f5-20e1481d2735/scratchpad"
TTS  = os.path.join(SP, "tts")
OUT  = os.path.join(SP, "build")
VOICE = os.environ.get("VO_VOICE","hm_omega")
SPEED = float(os.environ.get("VO_SPEED","1.10"))
LEAD  = 0.45            # silence before first word

k = Kokoro(os.path.join(TTS,"kokoro-v1.0.onnx"), os.path.join(TTS,"voices-v1.0.bin"))

def trim(x, sr, thr=0.004, pad=0.02):
    e = np.abs(x)
    # moving max over 5 ms
    w = max(1,int(0.005*sr))
    k2 = np.convolve(e, np.ones(w)/w, mode="same")
    idx = np.where(k2 > thr)[0]
    if len(idx)==0: return x
    a = max(0, idx[0]-int(pad*sr)); b = min(len(x), idx[-1]+int(pad*sr))
    return x[a:b]

sr = 24000
pieces = []
marks  = []
t = LEAD
pieces.append(np.zeros(int(LEAD*sr), dtype=np.float32))

GAPSCALE = float(os.environ.get("VO_GAP","0.75"))
for cid, cap, tts, gap in CHUNKS:
    gap = gap * GAPSCALE
    s, _sr = k.create(tts, voice=VOICE, speed=SPEED, lang="en-us")
    assert _sr == sr, _sr
    s = trim(np.asarray(s, dtype=np.float32), sr)
    dur = len(s)/sr
    marks.append({"id": cid, "caption": cap, "start": round(t,4), "end": round(t+dur,4), "gap": gap})
    pieces.append(s)
    t += dur
    if gap > 0:
        pieces.append(np.zeros(int(gap*sr), dtype=np.float32))
        t += gap
    print(f"{cid}  {dur:5.2f}s  -> {t:6.2f}s   {cap[:48]}")

vo = np.concatenate(pieces)
sf.write(os.path.join(OUT,"vo_raw.wav"), vo, sr)
json.dump({"sr":sr, "duration":len(vo)/sr, "marks":marks},
          open(os.path.join(OUT,"vo_marks.json"),"w"), indent=1)
print("TOTAL RAW VO:", round(len(vo)/sr,2), "s")
