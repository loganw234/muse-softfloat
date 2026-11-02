"""Measure v3 camera curves at 30 fps: master cam (pos/target) across the
whole film + cursor-rank velocity at every leg/gate join. Writes
camera_measurements3.json. A velocity STEP would show as a one-frame
spike in |v[i+1]-v[i]| far above the smooth trend. Also records the
parametric-scale facts behind the no-crop-upscale claim."""
import json
from pathlib import Path
import numpy as np
import render_gitvisual3 as R

dt = 1 / 30
ts = np.arange(1.0, 88.0, dt)
pos = np.array([R.master_cam(float(t)).pos for t in ts])
tgt = np.array([R.master_cam(float(t)).tgt for t in ts])
cur = np.array([R.cursor_rank(float(t)) for t in ts])
head = np.array([R.head_x(float(t)) for t in ts])

def stats(name, x):
    v = np.linalg.norm(np.diff(x, axis=0), axis=1) / dt if x.ndim == 2 else np.abs(np.diff(x)) / dt
    dv = np.abs(np.diff(v))
    nz = dv[dv > 1e-6]
    return {"name": name, "speed_first": round(float(v[0]), 2), "speed_last": round(float(v[-1]), 2),
            "speed_peak": round(float(v.max()), 1), "max_frame_dv": round(float(dv.max()), 3),
            "mean_frame_dv": round(float(dv.mean()), 4),
            "peak_dv_over_median_nonzero": round(float(dv.max() / max(1e-9, np.median(nz))), 1)}

out = [stats("master_cam_pos", pos), stats("master_cam_target", tgt),
       stats("cursor_rank", cur), stats("head_x", head)]
joins = []
for kt in [6.5, 28.6, 31.0, 39.0, 47.0, 52.0, 60.0, 67.0, 75.0, 79.0]:
    vb = (R.cursor_rank(kt) - R.cursor_rank(kt - dt)) / dt if kt >= 31.0 else (R.head_x(kt) - R.head_x(kt - dt)) / dt
    va = (R.cursor_rank(kt + dt) - R.cursor_rank(kt)) / dt if kt >= 31.0 else (R.head_x(kt + dt) - R.head_x(kt)) / dt
    joins.append({"t": kt, "v_before": round(float(vb), 3), "v_after": round(float(va), 3)})
res = {"curves": out, "timeline_joins": joins,
       "resolution": f"{R.W}x{R.H}",
       "upscale_note": ("All geometry is projected and all text rasterised at output "
                        "scale every frame (Cam.proj + PIL fonts sized in output px); "
                        "no bitmap is ever resized up. Max crop-upscale factor: 1.0. "
                        "Line widths scale by median focal/depth clamped to [0.25, 1.15]."),
       "note": "smootherstep legs: analytic 0 velocity+accel at joins; sampled joins below."}
Path(__file__).with_name("camera_measurements3.json").write_text(json.dumps(res, indent=1))
print(json.dumps(res, indent=1))
