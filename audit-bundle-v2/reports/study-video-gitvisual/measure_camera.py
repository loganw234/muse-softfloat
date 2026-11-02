"""Measure v2 camera curves at 30 fps: chase cam (pos/target) + axis-switch
rotation. Writes camera_measurements.json. A velocity STEP would show as a
one-frame spike in |v[i+1]-v[i]| far above the smooth trend."""
import json, math
from pathlib import Path
import numpy as np
import render_gitvisual2 as R

dt = 1 / 30
ts = np.arange(1.0, 30.0, dt)
pos = np.array([R.chase_cam(float(t)).pos for t in ts])
tgt = np.array([R.chase_cam(float(t)).tgt for t in ts])
head = np.array([R.head_x(float(t)) for t in ts])
def stats(name, x):
    v = np.linalg.norm(np.diff(x, axis=0), axis=1) / dt if x.ndim == 2 else np.abs(np.diff(x)) / dt
    dv = np.abs(np.diff(v))
    a = dv / dt
    return {"name": name, "speed_first": round(float(v[0]), 2), "speed_last": round(float(v[-1]), 2),
            "speed_peak": round(float(v.max()), 1), "max_frame_dv": round(float(dv.max()), 3),
            "mean_frame_dv": round(float(dv.mean()), 4), "max_accel_step_per_s2": round(float(a.max()), 1),
            "peak_dv_over_median_nonzero": round(float(dv.max() / max(1e-9, np.median(dv[dv > 1e-6]))), 1)}
out = [stats("chase_cam_pos", pos), stats("chase_cam_target", tgt), stats("head_x", head)]
# axis switch: theta(t) 30..34
ts2 = np.arange(30.0, 34.0, dt)
theta = np.array([R.ss(((float(t) - 30.0) - 0.7) / 2.7) * math.pi / 2 for t in ts2])
out.append(stats("axis_theta_rad", theta))
# joins: speed just before/after each head keyframe (should both be ~0 via ss)
joins = []
for kt, _ in R.KEYS[1:-1]:
    vb = (R.head_x(kt) - R.head_x(kt - dt)) / dt
    va = (R.head_x(kt + dt) - R.head_x(kt)) / dt
    joins.append({"t": kt, "v_before": round(vb, 3), "v_after": round(va, 3)})
res = {"curves": out, "head_keyframe_joins": joins,
       "note": "smootherstep legs: analytic 0 velocity+accel at joins; sampled joins below."}
Path(__file__).with_name("camera_measurements.json").write_text(json.dumps(res, indent=1))
print(json.dumps(res, indent=1))
