"""Marble/node sync re-measurement for v5 (after the text changes).

Same method as measure_sync4.py, applied to render_gitvisual5 alone:
screen-space distance (px at 2560x1440) between marble centroid and
node center at the continuous event time and at the nearest 30 fps
frame, using v5's own camera and marble model (a pure function of
head_x / cursor_rank, unchanged from v4). Also asserts the event
RANKS / node positions / gate ranks are identical to v4 - the text
revision moved wall times only (marbles wait), never events.
Writes sync_measurements5.json.
"""
import json, math
from pathlib import Path
import render_gitvisual4 as V4
import render_gitvisual5 as V5

HERE = Path(__file__).resolve().parent
R, FPS = V5, 30

def dist_px(t, p_marble, p_node):
    cam = R.master_cam(t)
    (ax, ay), da, _ = cam.one(p_marble)
    (bx, by), db, _ = cam.one(p_node)
    if da <= 40 or db <= 40:
        return None
    return round(math.hypot(ax - bx, ay - by), 3)

def t_of_cursor(target):
    lo, hi = R.T_REPLAY, R.T_BOX
    prev_t, prev_v = lo, R.cursor_rank(lo) - target
    t = lo
    while t < hi:
        t += 0.02
        v = R.cursor_rank(t) - target
        if prev_v <= 0 <= v and not (prev_v == 0 == v):
            a, b = prev_t, t
            for _ in range(60):
                m = (a + b) / 2
                if R.cursor_rank(m) < target:
                    a = m
                else:
                    b = m
            return (a + b) / 2
        prev_t, prev_v = t, v
    return None

def ev(t, marble_fn, node_p):
    tf = round(t * FPS) / FPS
    return {"t_event": round(t, 4),
            "dist_at_event_px": dist_px(t, marble_fn(t), node_p),
            "dist_nearest_frame_px": dist_px(tf, marble_fn(tf), node_p)}

rows = []
for i in range(len(R.NODES)):
    t_first = next(k / FPS for k in range(int(R.T_BRIDGE * FPS) + 1)
                   if R.head_x(k / FPS) >= R.NODE_X[i])
    rows.append({"kind": "chase_node_lighting", "event": f"node {i} {R.NODES[i]['system']}",
                 **ev(t_first,
                      lambda t, i=i: (R.clip_branch(R.branch_pts3(i, t), R.head_x(t)) or
                                      [R.branch_pts3(i, t)[0]])[-1],
                      R.branch_pts3(i, R.node_arrival(i))[-1])})

R.assign_lanes()
lanes = R.all_lane_pts()
for m in R.MERGES:
    if m["target"] != "main":
        continue
    short, base, mrank = m["short"], float(m["merge_base_rank"]), float(m["rank"])
    pts = lanes[short]
    rows.append({"kind": "merge_split", "event": f"{short} base rank {base:.0f}",
                 **ev(t_of_cursor(base),
                      lambda t, pts=pts: R.R3(R.cursor_rank(t), R.slot_at(pts, R.cursor_rank(t))),
                      R.R3(base, 0.0))})
    rows.append({"kind": "merge_absorb", "event": f"{short} merge rank {mrank:.0f}",
                 **ev(t_of_cursor(mrank),
                      lambda t, pts=pts: R.R3(R.cursor_rank(t), R.slot_at(pts, R.cursor_rank(t))),
                      R.R3(mrank, 0.0))})

sample = []
for m in R.MERGES:
    if m["target"] == "main":
        sample += [(m["short"], float(r)) for r in m["exclusive_ranks"]]
for short, r in sample[::3]:
    pts = lanes[short]
    rows.append({"kind": "exclusive_node_sample", "event": f"{short} exclusive rank {r:.0f}",
                 **ev(t_of_cursor(r),
                      lambda t, pts=pts: R.R3(R.cursor_rank(t), R.slot_at(pts, R.cursor_rank(t))),
                      R.R3(r, R.slot_at(pts, r)))})

def loop_marble(sb, t):
    ph = R.sb_phase(sb, R.cursor_rank(t))
    if ph is None:
        return R.R3(R.cursor_rank(t), R.sb_slot(sb))
    return R.interp_poly(R.loop_pts3(sb), ph)

for sb in R.SENDBACKS:
    Rr, sl = sb["rank"], R.sb_slot(sb)
    apex = Rr - 1.0 + R.sb_apex_frac(sb) * R.LOOP_SPAN
    rows.append({"kind": "sendback_entry", "event": f"rank {Rr:.0f} loop entry",
                 **ev(t_of_cursor(Rr - 1.0), lambda t, sb=sb: loop_marble(sb, t), R.R3(Rr - 1.0, sl))})
    rows.append({"kind": "sendback_apex_stamp", "event": f"rank {Rr:.0f} stamp vs apex",
                 **ev(t_of_cursor(apex), lambda t, sb=sb: loop_marble(sb, t), R.loop_pts3(sb)[2])})
    rows.append({"kind": "sendback_exit", "event": f"rank {Rr:.0f} loop exit",
                 **ev(t_of_cursor(Rr + 3.0), lambda t, sb=sb: loop_marble(sb, t), R.R3(Rr + 3.0, sl))})

for g in R.GATES:
    rows.append({"kind": "gate_arrival", "event": f"{g['id']} gate rank {g['rank']:.0f}",
                 **ev(g["t0"], lambda t: R.R3(R.cursor_rank(t), 0.0), R.R3(g["rank"], 0.0))})

g0 = R.GATES[0]
cam = R.master_cam(g0["t0"] + 2.0)
cents = []
for dt in (0.0, 0.25, 0.5):
    t = g0["t0"] + 2.0 + dt
    (sx, sy), _, _ = cam.one(R.R3(R.cursor_rank(t), 0.0))
    cents.append((sx, sy))
pulse_drift = round(max(math.hypot(a[0] - b[0], a[1] - b[1]) for a in cents for b in cents), 3)

def agg(kr, key):
    vals = [r[key] for r in kr if r.get(key) is not None]
    return {"n": len(vals), "max": max(vals), "mean": round(sum(vals) / len(vals), 3)} if vals else None

summary = {}
for kind in sorted(set(r["kind"] for r in rows)):
    kr = [r for r in rows if r["kind"] == kind]
    summary[kind] = {"at_event": agg(kr, "dist_at_event_px"),
                     "nearest_frame": agg(kr, "dist_nearest_frame_px")}

# events never moved: ranks / node X / gate ranks identical to v4
identity = {
    "NODE_X_equal": list(R.NODE_X) == list(V4.NODE_X),
    "gate_ranks_equal": [g["rank"] for g in R.GATES] == [g["rank"] for g in V4.GATES],
    "gate_durations_s": [g["t1"] - g["t0"] for g in R.GATES],
    "leg_rank_spans_equal": [(l[2], l[3]) for l in R.LEGS] == [(l[2], l[3]) for l in V4.LEGS],
    "leg_durations_s": [round(l[1] - l[0], 3) for l in R.LEGS],
    "v4_leg_durations_s": [round(l[1] - l[0], 3) for l in V4.LEGS],
    "sendback_ranks_equal": [s["rank"] for s in R.SENDBACKS] == [s["rank"] for s in V4.SENDBACKS],
    "head_x_at_arrivals": [R.head_x(R.node_arrival(i)) for i in range(7)],
    "cursor_at_gate_t0": [R.cursor_rank(g["t0"]) for g in R.GATES],
}
out = {"resolution": "2560x1440", "fps": FPS, "summary": summary,
       "pulse_hold_drift_px": pulse_drift, "event_identity_vs_v4": identity, "rows": rows}
(HERE / "sync_measurements5.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
for kind, s in summary.items():
    print(f"{kind:26s} at-event max {s['at_event']['max']:.3f}px mean {s['at_event']['mean']:.3f}  "
          f"nearest-frame max {s['nearest_frame']['max']:.2f}px  n={s['at_event']['n']}")
print("pulse hold drift px:", pulse_drift)
print("identity:", json.dumps(identity))
print("-> sync_measurements5.json")
