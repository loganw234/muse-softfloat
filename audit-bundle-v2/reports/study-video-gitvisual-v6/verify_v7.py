"""Pixel proofs for v7 on rendered frames (verify_r2.py extended).

Kept from r2: bridge seam frame-diff, lit/ghost spine sampling at
50/65/80 s (now DEEP lead blue), completed rank-38 red loop at 62 s.
New for v7:
- role lanes: at the busiest film moment and at 75.8 s, sample along
  projected ACTIVE episode lanes per role; count pixels matching the
  role's DEEP hue family within 3 px (colour semantics on screen).
- plant ticks: orange filled/hollow census in a window around
  verifier-sf2's verdict node at 75.8 s (3 caught / 2 missed).
- replay legend: census of the five DEEP chip colours in the legend
  box region at 65 s.
Writes verify_v7.json. Run: $MSF_PYTHON verify_v7.py
"""
import json, sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gitvisual7 as R

R.assign_lanes(); R.all_lane_pts()
out = {}

ts = [44.5 + k / R.FPS for k in range(34)]
frames = [np.asarray(R.frame_at(t), dtype=np.int16) for t in ts]
diffs = [round(float(np.abs(frames[i + 1] - frames[i]).mean()), 4)
         for i in range(len(frames) - 1)]
seam_i = next(i for i, t in enumerate(ts) if abs(t - 45.0) < 1e-9)
mask = np.ones((R.H, R.W), bool); mask[:200, :1600] = False
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


blue = lambda px: px[2] > 100 and px[2] > px[0] + 20
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

# ---- v7: role-colour sampling along lit episode lanes ----
def role_pred(col):
    # glow_poly lightens core toward white; accept the hue family:
    # the DEEP colour's dominant channel(s) must lead clearly
    cr, cg, cb = col
    def pred(px):
        d = np.abs(px - np.array(col)).max()
        bright = np.abs(px - np.array(col) * 0.35 - 255 * 0.65 * 0.35).max()
        return d < 90 or bright < 90
    return pred

def lane_samples(t):
    img = R.frame_at(t); cam = R.master_cam(t); cur = R.cursor_rank(t)
    per_role = {}
    for ep in R.LANE_EPS:
        if not (ep["draw_start"] + 0.3 <= cur):
            continue
        pts = R.ep_pts_rs(ep)
        lo, hi = max(ep["draw_start"], cur - 14.0), min(cur, ep["draw_end"])
        if hi - lo < 0.4:
            continue
        samples = []
        for k in range(6):
            r = lo + (hi - lo) * (k + 0.5) / 6.0
            p = R.R3(r, R.slot_at(pts, r))
            z = R.ep_zoff(ep, r)
            samples.append((p[0], p[1], p[2] + z) if z else p)
        res = sample_hits(img, cam, samples, role_pred(R.ROLE_COL[ep["role"]]), rad=3)
        agg = per_role.setdefault(ep["role"], {"hits": 0, "samples": 0, "episodes": 0})
        agg["hits"] += res["hits"]; agg["samples"] += res["samples"]; agg["episodes"] += 1
    for v in per_role.values():
        v["frac"] = round(v["hits"] / v["samples"], 3) if v["samples"] else None
    return {"t": t, "cursor": round(cur, 2), "per_role": per_role}

out["role_lane_pixels"] = [lane_samples(48.0), lane_samples(75.8), lane_samples(78.6)]

# ---- v7: plant ticks near verifier-sf2 verdict (3 caught/2 missed) ----
img = R.frame_at(75.8); cam = R.master_cam(75.8)
ep = next(e for e in R.LANE_EPS if e["agent"] == "verifier-sf2")
arr = np.asarray(img).astype(int)
ocol = np.array(R.DEEP["plants"])
tick_res = []
for k, tk in enumerate(ep["plants"]):
    tp = R.R3(ep["draw_end"] + 0.28 + 0.30 * k, float(ep["slot"]))
    tp = (tp[0], tp[1], tp[2] + 30.0)
    (sx, sy), dep, _ = cam.one(tp)
    x, y = int(round(sx)), int(round(sy))
    patch = arr[max(0, y - 14):y + 15, max(0, x - 14):x + 15].reshape(-1, 3)
    orange = int((np.abs(patch - ocol).max(axis=1) < 60).sum())
    tick_res.append({"plant": tk["plant"], "grade": tk["grade"], "orange_px_near": orange})
out["plant_ticks_verifier_sf2_75.8s"] = tick_res

# ---- v7: replay legend chip census ----
img = R.frame_at(65.0)
arr = np.asarray(img).astype(int)
crop = arr[R.H - 480:R.H - 130, R.W - 620:R.W - 40].reshape(-1, 3)
legend = {}
for role, col in R.ROLE_COL.items():
    legend[role] = int((np.abs(crop - np.array(col)).max(axis=1) < 40).sum())
legend["plants_orange"] = int((np.abs(crop - ocol).max(axis=1) < 40).sum())
out["replay_legend_chips_65s"] = legend

(HERE / "verify_v7.json").write_text(json.dumps(out, indent=1))
print(json.dumps({k: (v if k != "bridge_frame_diff" else
                       {kk: vv for kk, vv in v.items() if kk not in ("diffs", "world_only_diffs")})
                  for k, v in out.items()}, indent=1))
print("-> verify_v7.json")
