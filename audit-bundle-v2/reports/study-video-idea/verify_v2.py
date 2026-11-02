"""Probe + stills + pure-white bookend measurement for idea & why2.

Run: $MSF_PYTHON verify_v2.py   (from this directory or anywhere)
Uses video/probe.py for decode-verification; measures exact-white
pixel counts on grabbed stills (first/second-half-second and tail).
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "video"))
import probe as P  # noqa: E402

JOBS = [
    (HERE / "idea-1440p.mp4", HERE / "stills",
     [0.2, 2.8, 6.2, 9.5, 11.8, 13.0, 14.3], [(0.2,), (14.3,)]),
    (HERE.parent / "study-video-why" / "why2-1440p.mp4",
     HERE.parent / "study-video-why" / "stills2",
     [0.2, 2.2, 8.2, 12.2, 18.7, 24.2, 26.3, 27.7, 30.8, 31.8],
     [(0.2,), (31.8,)]),
]

for mp4, sdir, times, whites in JOBS:
    info = P.probe(mp4)
    print("==", mp4.name, {k: info[k] for k in
          ("bytes", "duration_s", "codec", "width", "height", "fps",
           "decoded_frames", "decode_rc")})
    made = P.stills(mp4, sdir, times)
    for s in made:
        print("still:", s)
    by_t = dict(zip(times, made))
    for (t,) in whites:
        im = Image.open(by_t[t]).convert("RGB")
        px = im.getdata()
        nonwhite = sum(1 for p in px if p != (255, 255, 255))
        print(f"white-check t={t}s nonwhite_px = {nonwhite} of {len(px)}")
