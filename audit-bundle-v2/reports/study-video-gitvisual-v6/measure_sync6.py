"""Marble/node sync measurement for v6 (analytic, adapted from the
v5 approach in scratch/study-video-gitvisual/measure_sync5.py):
screen-space distance (px at 2560x1440) between marble centroid and
node center at the continuous event time and at the nearest 30 fps
frame, using v6's own camera and marble model - now exercised under
the NEW chase-language replay camera (events must still land at
0.0 px at-event: marbles are pure functions of head_x/cursor_rank,
the camera only looks). Plus v6-specific checks: tokens gate gone,
augint gate parked exactly on LAST_RANK through its window and the
settle leg, cursor monotonicity, bridge/dolly camera continuity,
camera-to-head distance in chase language, and the opening's
gravity law. Writes sync_measurements6.json.

Run: $MSF_PYTHON measure_sync6.py
"""
import json, math, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gitvisual6 as R

FPS = R.FPS
R.assign_lanes()
lanes = R.all_lane_pts()


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
    return R.T_BOX  # target == LAST_RANK plateau


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


def agg(kr, key):
    vals = [r[key] for r in kr if r.get(key) is not None]
    return {"n": len(vals), "max": max(vals), "mean": round(sum(vals) / len(vals), 3)} if vals else None


summary = {}
for kind in sorted(set(r["kind"] for r in rows)):
    kr = [r for r in rows if r["kind"] == kind]
    summary[kind] = {"at_event": agg(kr, "dist_at_event_px"),
                     "nearest_frame": agg(kr, "dist_nearest_frame_px")}

# ---- v6-specific checks ----
aug = next(g for g in R.GATES if g["id"] == "augint")
checks = {
    "gate_ids": [g["id"] for g in R.GATES],
    "gate_ranks": [g["rank"] for g in R.GATES],
    "augint_rank_is_last": aug["rank"] == float(R.LAST_RANK),
    "augint_window_s": [aug["t0"], aug["t1"]],
    "cursor_at_gate_t0": [R.cursor_rank(g["t0"]) for g in R.GATES],
    "cursor_during_augint_and_settle": sorted({
        round(R.cursor_rank(aug["t0"] + 0.37 * k), 9) for k in range(33)}),
    "leg_wall_times_s": [[l[0], l[1], l[2], l[3]] for l in R.LEGS],
}
# cursor monotonic nondecreasing on a fine grid over the whole replay
prev, mono = -1.0, True
for k in range(int((R.TOTAL - R.T_REPLAY) * 20) + 1):
    c = R.cursor_rank(R.T_REPLAY + k / 20.0)
    mono = mono and c >= prev - 1e-12
    prev = c
checks["cursor_monotonic"] = mono

# bridge + opening-dolly camera continuity across the seams (1 frame step)
def cam_step(t_seam):
    a = R.master_cam(t_seam - 1 / FPS)
    b = R.master_cam(t_seam)
    return {"pos_step": round(float(abs(b.pos - a.pos).max()), 2),
            "tgt_step": round(float(abs(b.tgt - a.tgt).max()), 2),
            "focal_a": a.focal, "focal_b": b.focal}

checks["cam_step_at_bridge_start"] = cam_step(R.T_BRIDGE + 1 / FPS)
checks["cam_step_at_replay_start"] = cam_step(R.T_REPLAY + 1 / FPS)
checks["cam_step_at_opening_start"] = cam_step(R.T_BOX + 1 / FPS)

# chase-language distance: camera to head marble over the replay legs
dists = []
for k in range(400):
    t = R.T_REPLAY + (R.T_BOX - R.T_REPLAY) * k / 399.0
    cam = R.master_cam(t)
    _, dep, _ = cam.one(R.R3(R.cursor_rank(t), 0.0))
    dists.append(dep)
checks["cam_head_depth_replay"] = {"min": round(min(dists), 1), "max": round(max(dists), 1)}
chase_d = []
for k in range(50):
    t = 10.0 + 0.6 * k
    cam = R.master_cam(t)
    _, dep, _ = cam.one((R.head_x(t), 0.0, R.trail_z(R.head_x(t), t)))
    chase_d.append(dep)
checks["cam_head_depth_chase"] = {"min": round(min(chase_d), 1), "max": round(max(chase_d), 1)}

# opening gravity: second difference of z_off in free fall == -FALL_G*dt^2
lt0 = R.PACK_TRAVEL + R.TIP_T
zs = [R.pack_state(lt0 + 0.05 * k)[0][2] for k in range(6)]
second = [round(zs[i + 2] - 2 * zs[i + 1] + zs[i], 6) for i in range(4)]
checks["fall_second_difference"] = second
checks["fall_expected"] = round(-R.FALL_G * 0.05 ** 2, 6)
checks["pack_order"] = R.PACK_ORDER
checks["all_inside_by_lt"] = {str(lt): sum(1 for p in R.pack_state(lt) if p[3])
                              for lt in (4.0, 5.0, 6.0, 6.5, 7.0)}

# ---- r2 checks ----
aug_end = aug["t1"]
checks["r2_end_beats_s"] = {
    "interval_gate_close": aug_end,
    "opening_scene_start_T_BOX": R.T_BOX,
    "first_rim": R.T_BOX + R.PACK_TRAVEL,
    "first_fall": R.T_BOX + R.PACK_TRAVEL + R.TIP_T,
    "last_rim": R.T_BOX + R.PACK_STAGGER * 6 + R.PACK_TRAVEL,
    "dim_start": R.T_BOX + R.PACK_DIM_LT,
    "fade_start": R.T_FADE, "total": R.TOTAL,
    "gate_close_to_first_fall": round(R.T_BOX + R.PACK_TRAVEL + R.TIP_T - aug_end, 2),
}
# item 4 root-cause exhibit: depth of the old two-point lit spine's
# start vertex R3(cur-30,0) - behind the near plane at chase
# distance, which is why the old vertex-drop filter culled it whole
checks["r2_old_spine_start_depth"] = {
    str(t): round(R.master_cam(t).one(R.R3(R.cursor_rank(t) - 30.0, 0.0))[1], 1)
    for t in (50.0, 65.0, 80.0)}
# item 2: every inset text-quad corner strictly inside plate quad
_cam = R.master_cam(98.3)
_lx = R.X0R + R.BOX_RANK * R.DX + 650.0
_pq, _tq = R.plate_quads(_cam, _lx)
def _inside(p, q):
    cr = []
    for i in range(4):
        a, b = q[i], q[(i + 1) % 4]
        cr.append((b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]))
    return all(v > 0 for v in cr) or all(v < 0 for v in cr)
checks["r2_plate_text_quad_inside_plate"] = all(_inside(p, _pq) for p in _tq)
_tex = R.plate_texture(7, 0.0)
checks["r2_plate_texture_ink_bbox"] = _tex.getchannel("A").getbbox()
checks["r2_plate_texture_size"] = list(_tex.size)
rim_r = R.BOX_RANK - R.OPEN_HX / R.DX
checks["falling_rank_inside_hole"] = all(
    rim_r < p[1] < R.BOX_RANK + R.OPEN_HX / R.DX
    for lt in (3.2, 4.2, 5.2) for p in R.pack_state(lt) if p[2] < -8.0)

out = {"resolution": "2560x1440", "fps": FPS, "summary": summary,
       "v6_checks": checks, "rows": rows}
(HERE / "sync_measurements6.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
for kind, s in summary.items():
    print(f"{kind:26s} at-event max {s['at_event']['max']:.3f}px mean {s['at_event']['mean']:.3f}  "
          f"nearest-frame max {s['nearest_frame']['max']:.2f}px  n={s['at_event']['n']}")
print(json.dumps(checks, indent=1))
print("-> sync_measurements6.json")
