"""Pixel proofs for the r2 fixes (items 3, 4, 5) on rendered frames.

- bridge: consecutive-frame mean |diff| across 44.5-45.6 s - the seam
  frame (45.0) must not spike above its neighbours (r1 switched
  worlds there in one frame).
- spine: at 50/65/80 s, sample pixels along the projected lit spine
  (cursor-12..cursor) and ghost spine (cursor+2..+14); count
  blue-dominant hits within 3 px.
- red: at 62.0 s (after the IAS15 gate), sample along the completed
  rank-38 loop; count red-dominant hits within 4 px.

Writes verify_r2.json. Run: $MSF_PYTHON verify_r2.py
"""
import json, sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gitvisual6 as R

R.assign_lanes(); R.all_lane_pts()
out = {}

# ---- item 3: bridge frame differences ----
ts = [44.5 + k / R.FPS for k in range(34)]  # 44.500 .. 45.600
frames = [np.asarray(R.frame_at(t), dtype=np.int16) for t in ts]
diffs = [round(float(np.abs(frames[i + 1] - frames[i]).mean()), 4)
         for i in range(len(frames) - 1)]
seam_i = next(i for i, t in enumerate(ts) if abs(t - 45.0) < 1e-9)
# world-only diffs: mask the HUD title box, whose text legitimately
# swaps at the seam beat ("1 > 2" -> "2 - AS IT HAPPENED", r1 copy)
mask = np.ones((R.H, R.W), bool); mask[:200, :1200] = False
wdiffs = [round(float(np.abs(frames[i + 1] - frames[i]).mean(axis=2)[mask].mean()), 4)
          for i in range(len(frames) - 1)]
out["bridge_frame_diff"] = {
    "window_s": [ts[0], ts[-1]],
    "seam_diff_44.967_to_45.000": diffs[seam_i - 1],
    "seam_diff_45.000_to_45.033": diffs[seam_i],
    "max_diff_in_window": max(diffs),
    "median_diff_in_window": round(float(np.median(diffs)), 4),
    "world_only_seam_diff_44.967_to_45.000": wdiffs[seam_i - 1],
    "world_only_seam_diff_45.000_to_45.033": wdiffs[seam_i],
    "world_only_max_diff_in_window": max(wdiffs),
    "world_only_median_diff_in_window": round(float(np.median(wdiffs)), 4),
    "diffs": diffs, "world_only_diffs": wdiffs,
}

def sample_hits(img, cam, pts3, pred, rad=3):
    arr = np.asarray(img).astype(int)
    hits = tot = 0
    for p in pts3:
        (sx, sy), dep, _ = cam.one(p)
        if dep <= 40:
            continue
        x, y = int(round(sx)), int(round(sy))
        if not (rad <= x < R.W - rad and rad <= y < R.H - rad):
            continue
        tot += 1
        patch = arr[y - rad:y + rad + 1, x - rad:x + rad + 1].reshape(-1, 3)
        if any(pred(px) for px in patch):
            hits += 1
    return {"hits": hits, "samples": tot,
            "frac": round(hits / tot, 3) if tot else None}

blue = lambda px: px[2] > 110 and px[2] > px[0] + 25
red = lambda px: px[0] > 130 and px[0] > px[1] + 35

out["spine"] = {}
for t in (50.0, 65.0, 80.0):
    img = R.frame_at(t); cam = R.master_cam(t); cur = R.cursor_rank(t)
    lit = [R.R3(cur - 12.0 + k, 0.0) for k in range(13)]
    ghost = [R.R3(cur + 2.0 + k, 0.0) for k in range(13)]
    out["spine"][str(t)] = {"cursor": round(cur, 2),
                            "lit": sample_hits(img, cam, lit, blue),
                            "ghost": sample_hits(img, cam, ghost, blue)}

t = 62.0
img = R.frame_at(t); cam = R.master_cam(t)
sb38 = next(s for s in R.SENDBACKS if s["rank"] == 38.0)
loop = [R.interp_poly(R.loop_pts3(sb38), f / 40.0) for f in range(41)]
out["red_loop_rank38_at_62s"] = sample_hits(img, cam, loop, red, rad=4)

(HERE / "verify_r2.json").write_text(json.dumps(out, indent=1))
print(json.dumps({k: (v if k != "bridge_frame_diff" else
                       {kk: vv for kk, vv in v.items() if kk != "diffs"})
                  for k, v in out.items()}, indent=1))
print("-> verify_r2.json")
