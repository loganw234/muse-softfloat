"""Probe-verify all four v3 clips + handoff pixel measurements.

Uses video/probe.py (bundled ffmpeg decode). Writes verify3.json and
MP4-grab stills (stills3/, stills-idea2/, why stills3/).
Run: $MSF_PYTHON verify3.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "video"))
import probe as P  # noqa: E402

IDEA = HERE.parent / "study-video-idea"
WHY = HERE.parent / "study-video-why"

JOBS = [
    (HERE / "intro3.mp4", HERE / "stills3" / "intro",
     [0.2, 1.2, 4.4, 5.4, 6.8], [6.8], 210),
    (HERE / "outro3.mp4", HERE / "stills3" / "outro",
     [0.0, 1.0, 2.8, 4.2, 8.3], [], 255),
    (IDEA / "idea2-1440p.mp4", IDEA / "stills-idea2",
     [0.2, 4.4, 9.4, 14.4, 18.4, 21.4, 22.3], [0.2, 22.3], 675),
    (WHY / "why3-1440p.mp4", WHY / "stills3",
     [0.2, 3.4, 7.9, 13.4, 18.4, 23.9, 27.9, 32.4, 33.3], [0.2, 33.3], 1005),
]
PRIORS = {
    "intro2.mp4": (HERE / "intro2.mp4", 643997),
    "outro2.mp4": (HERE / "outro2.mp4", 536110),
    "idea-1440p.mp4": (IDEA / "idea-1440p.mp4", 1051203),
    "why2-1440p.mp4": (WHY / "why2-1440p.mp4", 2453116),
}

out: dict = {"clips": {}, "priors": {}}
for mp4, sdir, times, whites, expect in JOBS:
    info = P.probe(mp4)
    info["expected_frames"] = expect
    made = P.stills(mp4, sdir, times)
    by_t = dict(zip(times, made))
    checks = {}
    for t in whites:
        a = np.asarray(Image.open(by_t[t]).convert("RGB"))
        checks[f"white_{t}s"] = dict(
            nonwhite_px=int((a != 255).any(axis=2).sum()),
            total_px=int(a.shape[0] * a.shape[1]))
    if mp4.name == "outro3.mp4":
        a = np.asarray(Image.open(by_t[0.0]).convert("RGB"))
        flat = a.reshape(-1, 3)
        dom = Counter(map(tuple, flat[::37].tolist())).most_common(3)
        checks["first_frame"] = dict(
            min=int(a.min()), max=int(a.max()),
            dominant_sampled=[[list(k), v] for k, v in dom])
    info["handoff"] = checks
    info["stills"] = [str(s.relative_to(ROOT)) for s in made]
    out["clips"][mp4.name] = info
    print(mp4.name, {k: info[k] for k in ("bytes", "duration_s", "codec",
          "width", "height", "fps", "decoded_frames", "decode_rc")}, checks)

for name, (p, expect_bytes) in PRIORS.items():
    got = p.stat().st_size
    out["priors"][name] = dict(bytes=got, expected=expect_bytes,
                               unchanged=got == expect_bytes)
    print("prior", name, got, "unchanged" if got == expect_bytes else "CHANGED!")

(HERE / "verify3.json").write_text(json.dumps(out, indent=1))
print("wrote verify3.json")
