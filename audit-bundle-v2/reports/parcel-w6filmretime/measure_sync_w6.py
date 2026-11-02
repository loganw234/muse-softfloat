"""Marble/node sync measurement for v7 (analytic; v6 measure_sync6
adapted): screen-space distance (px at 2560x1440) between marble
centroid and node center at the continuous event time and at the
nearest 30 fps frame, using v7's own camera and marble model.
v7 adds EPISODE at-event checks for all 93 lane episodes: spawn
(marble exactly on the spine node at draw_start) and endpoint
(authors/fixers exactly on the merge node at draw_end; verifiers/
surveyors exactly on their verdict/doc node at draw_end) - episode
activity is a pure function of the same cursor_rank, no second
clock. Plus process-graph accounting cross-checks (counts by role,
slot/concurrency recompute, DEEP colour map). All r2 checks kept.
Writes sync_measurements7.json.

Run: $MSF_PYTHON measure_sync7.py
"""
import json, math, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEG = Path(r"C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w6-filmretime\video\segments")
sys.path.insert(0, str(SEG))
import gitvisual as R

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

# ---- v7: episode spawn / endpoint at-event checks (all 93) ----
# Pre-root episodes spawn before the cursor exists (cursor starts at
# rank 0), so their spawn event has no wall time; they are checked
# geometrically: ep_marble_pos at draw_start IS the spine point.
pre_root_spawn = []
for ep in R.LANE_EPS:
    s, e = ep["draw_start"], ep["draw_end"]
    if s >= 0:
        rows.append({"kind": "episode_spawn",
                     "event": f"{ep['id']} {ep['agent']} spawn rank {s:.2f}",
                     **ev(t_of_cursor(s), lambda t, ep=ep: R.ep_marble_pos(ep, R.cursor_rank(t)),
                          R.R3(s, 0.0))})
    else:
        p = R.ep_marble_pos(ep, s)
        pre_root_spawn.append({"id": ep["id"], "agent": ep["agent"],
                               "spawn_rank": s, "on_spine": p == R.R3(s, 0.0)})
    if ep["endpoint"] == "merge":
        node = R.R3(e, 0.0)
    else:
        node = R.R3(e, float(ep["slot"]))
    if e >= 0:
        rows.append({"kind": "episode_endpoint",
                     "event": f"{ep['id']} {ep['agent']} {ep['endpoint']} rank {e:.2f}",
                     **ev(t_of_cursor(e), lambda t, ep=ep: R.ep_marble_pos(ep, R.cursor_rank(t)),
                          node)})
    else:  # ends before the root commit: no cursor wall time exists
        p = R.ep_marble_pos(ep, e)
        pre_root_spawn.append({"id": ep["id"], "agent": ep["agent"],
                               "endpoint_rank": e, "endpoint_on_node": p == node})


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
    for t in (55.0, 75.0, 90.0)}
# item 2: every inset text-quad corner strictly inside plate quad
_cam = R.master_cam(R.T_BOX + 7.8)
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

# ---- v7 process-graph cross-checks (independent recompute) ----
from collections import Counter
acc = R.PG["accounting"]
_slots = {}
_slot_clash = []
for ep in R.LANE_EPS:
    for other in _slots.get(ep["slot"], []):
        if not (ep["draw_end"] + 0.2 < other["draw_start"] or other["draw_end"] + 0.2 < ep["draw_start"]):
            _slot_clash.append((ep["id"], other["id"], ep["slot"]))
    _slots.setdefault(ep["slot"], []).append(ep)
_git_clash = []
for ep in R.LANE_EPS:
    if ep.get("git_lane"):
        continue
    for short, gs in R.PG["git_slots"].items():
        if gs != ep["slot"]:
            continue
        m = next(m for m in R.MERGES if m["short"] == short)
        if not (ep["draw_end"] + 0.2 < m["merge_base_rank"] - 0.5
                or m["rank"] + 0.5 < ep["draw_start"] - 0.2):
            _git_clash.append((ep["id"], short))
_maxconc = max(sum(1 for e in R.LANE_EPS if e["draw_start"] <= r / 10 <= e["draw_end"])
               for r in range(-15, 1401))
checks["v7_process_graph"] = {
    "accounting": acc,
    "episodes_loaded": len(R.EPISODES), "lane_episodes_loaded": len(R.LANE_EPS),
    "role_counts_recomputed": dict(Counter(e["role"] for e in R.EPISODES)),
    "role_colours": {k: list(v) for k, v in R.ROLE_COL.items()},
    "deep_colours_match_legend": all(R.ROLE_COL[k] == R.DEEP[v] for k, v in
                                     R.PG["role_colors_deep"].items()),
    "slot_clashes_episode_episode": _slot_clash,
    "slot_clashes_episode_git": _git_clash,
    "max_concurrency_recomputed_sampled": _maxconc,
    "pre_root_spawn_geometric": pre_root_spawn,
    "pre_root_all_on_spine": all(p.get("on_spine", True) for p in pre_root_spawn),
    "pre_root_all_on_endpoint_node": all(p.get("endpoint_on_node", True) for p in pre_root_spawn),
    "episode_nearest_frame_over_100px": sum(
        1 for r in rows if r["kind"] in ("episode_spawn", "episode_endpoint")
        and (r.get("dist_nearest_frame_px") or 0) > 100),
    "plants_ticks_total_on_episodes": sum(len(e["plants"]) for e in R.LANE_EPS),
    "study_label_ids": sorted(R.STUDY_LABELS),
    "agents_counter_denominator": R.N_AGENTS,
    "agents_lit_at_head": sum(1 for e in R.LANE_EPS if e["draw_start"] <= R.LAST_RANK),
}

out = {"resolution": "2560x1440", "fps": FPS, "summary": summary,
       "v6_checks": checks, "rows": rows}
(HERE / "sync_measurements_w6.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
for kind, s in summary.items():
    print(f"{kind:26s} at-event max {s['at_event']['max']:.3f}px mean {s['at_event']['mean']:.3f}  "
          f"nearest-frame max {s['nearest_frame']['max']:.2f}px  n={s['at_event']['n']}")
print(json.dumps(checks, indent=1))
print("-> sync_measurements_w6.json")
