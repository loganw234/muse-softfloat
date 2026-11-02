"""Marble/node sync measurement: v3 (before) vs v4 (after).

For every track event frame we compute the screen-space distance
(px at 2560x1440) between the marble centroid and the node center
it is meant to sit on, using each module's own camera and its own
marble model, replicated exactly:
  v3: replay marbles ride at R3 + 26 world units (+ a 4-unit
      sinusoidal gate bob), gates hold the cursor at gate_rank-0.5,
      chase nodes light on wall time (arrival-0.1 s) while the head
      stops 14 units past each node, sendback stamps fire on a
      6-rank phase window while the marble rides a 4-rank window.
  v4: marble_pos is a pure function of (rank, slot); chase lighting
      is gated on head_x itself; gates hold ON the gate rank;
      sendback stamp lands at the loop-apex rank.

Events: all 7 chase node lightings, all 25 merge splits (cursor at
merge-base) + merge absorbs (cursor at merge rank), a sample of
exclusive-commit nodes, all 5 sendback loop entries / apex stamps /
exits, all 3 gate arrivals, and the BPM-pulse/gate-bob centroid
drift during a gate hold. Distances are reported at the continuous
event time (cursor == event rank exactly) and at the nearest
rendered 30 fps frame. Writes sync_measurements4.json.
"""
import json, math
from pathlib import Path
import render_gitvisual3 as V3
import render_gitvisual4 as V4

HERE = Path(__file__).resolve().parent
FPS = 30

def dist_px(R, t, p_marble, p_node):
    cam = R.master_cam(t)
    (ax, ay), da, _ = cam.one(p_marble)
    (bx, by), db, _ = cam.one(p_node)
    if da <= 40 or db <= 40:
        return None
    return round(math.hypot(ax - bx, ay - by), 3)

def t_of_cursor(R, target):
    """Continuous t in [31, 79) with cursor_rank(t) == target."""
    lo, hi = 31.0, 79.0
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

def marble_world(R, t, rank, slot, v3):
    p = R.R3(rank, slot)
    if not v3:
        return p
    gate, _ = R.gate_at(t)
    lift = 26.0 + (4.0 * math.sin(t * 5.0 + rank) if gate is not None else 0.0)
    return (p[0], p[1], p[2] + lift)

def loop_marble(R, sb, cur, v3):
    pts = R.loop_pts3(sb)
    if v3:
        f = R.clamp((cur - (sb["rank"] - 1.0)) / 4.0)
        p = R.interp_poly(pts, f)
        return (p[0], p[1], p[2] + 26.0)
    ph = R.sb_phase(sb, cur)
    if ph is None:  # renderer falls back to the straight ride
        return R.R3(cur, R.sb_slot(sb))
    return R.interp_poly(pts, ph)

def both(t_ev_fn, marble_fn, node_fn):
    """Run one event against v3 and v4; return distances dict."""
    out = {}
    for tag, R, v3 in (("v3", V3, True), ("v4", V4, False)):
        t = t_ev_fn(R, v3)
        if t is None:
            out[tag] = None
            continue
        tf = round(t * FPS) / FPS
        out[tag] = {
            "t_event": round(t, 4),
            "dist_at_event_px": dist_px(R, t, marble_fn(R, t, v3), node_fn(R)),
            "dist_nearest_frame_px": dist_px(R, tf, marble_fn(R, tf, v3), node_fn(R)),
        }
    return out

rows = []

# ---- chase node lightings (7) ----
for i in range(len(V4.NODES)):
    def t_fn(R, v3, i=i):
        if v3:  # first rendered frame with t >= arrival-0.1
            return math.ceil((R.node_arrival(i) - 0.1) * FPS) / FPS
        # first rendered frame with head_x >= NODE_X (lighting clock)
        for k in range(int(31 * FPS)):
            if R.head_x(k / FPS) >= R.NODE_X[i]:
                return k / FPS
        return None
    def m_fn(R, t, v3, i=i):
        clipped = R.clip_branch(R.branch_pts3(i, t), R.head_x(t))
        return clipped[-1] if clipped else R.branch_pts3(i, t)[0]
    def n_fn(R, i=i):
        return R.branch_pts3(i, R.node_arrival(i))[-1]
    d = both(t_fn, m_fn, lambda R: R.branch_pts3(i, R.node_arrival(i))[-1])
    rows.append({"kind": "chase_node_lighting", "event": f"node {i} {V4.NODES[i]['system']}", **d})

# ---- merges: split at merge-base, absorb at merge rank (25 each) ----
V4.assign_lanes(); V3.assign_lanes()
lanes4 = V4.all_lane_pts()
for m in V4.MERGES:
    if m["target"] != "main":
        continue
    short, base, mrank = m["short"], float(m["merge_base_rank"]), float(m["rank"])
    pts = lanes4[short]
    rows.append({"kind": "merge_split", "event": f"{short} base rank {base:.0f}",
                 **both(lambda R, v3: t_of_cursor(R, base),
                        lambda R, t, v3: marble_world(R, t, R.cursor_rank(t),
                                                       R.slot_at(pts, R.cursor_rank(t)), v3),
                        lambda R: R.R3(base, 0.0))})
    rows.append({"kind": "merge_absorb", "event": f"{short} merge rank {mrank:.0f}",
                 **both(lambda R, v3: t_of_cursor(R, mrank),
                        lambda R, t, v3: marble_world(R, t, R.cursor_rank(t),
                                                       R.slot_at(pts, R.cursor_rank(t)), v3),
                        lambda R: R.R3(mrank, 0.0))})

# ---- sample of exclusive-commit nodes (every 3rd, lane marble) ----
sample = []
for m in V4.MERGES:
    if m["target"] == "main":
        sample += [(m["short"], float(r)) for r in m["exclusive_ranks"]]
for short, r in sample[::3]:
    pts = lanes4[short]
    rows.append({"kind": "exclusive_node_sample", "event": f"{short} exclusive rank {r:.0f}",
                 **both(lambda R, v3: t_of_cursor(R, r),
                        lambda R, t, v3: marble_world(R, t, R.cursor_rank(t),
                                                       R.slot_at(pts, R.cursor_rank(t)), v3),
                        lambda R: R.R3(r, R.slot_at(pts, r)))})

# ---- sendback loops: entry / apex stamp / exit (5 each) ----
for sb in V4.SENDBACKS:
    Rr, sl = sb["rank"], V4.sb_slot(sb)
    rows.append({"kind": "sendback_entry", "event": f"rank {Rr:.0f} loop entry",
                 **both(lambda R, v3: t_of_cursor(R, Rr - 1.0),
                        lambda R, t, v3: loop_marble(R, sb, R.cursor_rank(t), v3),
                        lambda R: R.R3(Rr - 1.0, sl))})
    apex4 = Rr - 1.0 + V4.sb_apex_frac(sb) * V4.LOOP_SPAN
    def t_apex(R, v3, Rr=Rr, apex4=apex4):
        return t_of_cursor(R, (Rr + 0.5) if v3 else apex4)  # v3 stamp: phase 0.25 of 6
    rows.append({"kind": "sendback_apex_stamp", "event": f"rank {Rr:.0f} stamp vs apex",
                 **both(t_apex,
                        lambda R, t, v3: loop_marble(R, sb, R.cursor_rank(t), v3),
                        lambda R: R.loop_pts3(sb)[2])})
    rows.append({"kind": "sendback_exit", "event": f"rank {Rr:.0f} loop exit",
                 **both(lambda R, v3: t_of_cursor(R, Rr + 3.0),
                        lambda R, t, v3: loop_marble(R, sb, R.cursor_rank(t), v3),
                        lambda R: R.R3(Rr + 3.0, sl))})

# ---- gate arrivals (3): head marble vs gate-line node at t0 ----
for g in V4.GATES:
    gr, t0 = g["rank"], g["t0"]
    rows.append({"kind": "gate_arrival", "event": f"{g['id']} gate rank {gr:.0f}",
                 **both(lambda R, v3: t0,
                        lambda R, t, v3: marble_world(R, t, R.cursor_rank(t), 0.0, v3),
                        lambda R: R.R3(gr, 0.0))})

# ---- BPM pulse / gate bob: centroid drift during a hold (fixed cam) ----
pulse = {}
for tag, R, v3 in (("v3", V3, True), ("v4", V4, False)):
    g = R.GATES[0]
    cam = R.master_cam(g["t0"] + 2.0)
    cents = []
    for dt in (0.0, 0.25, 0.5):  # pulse 1.0 -> ~0.14 -> 1.0 at 120 BPM
        t = g["t0"] + 2.0 + dt
        p = marble_world(R, t, R.cursor_rank(t), 0.0, v3)
        (sx, sy), _, _ = cam.one(p)
        cents.append((sx, sy))
    pulse[tag] = {
        "pulse_values": [round(R.beat_pulse(g["t0"] + 2.0 + dt), 3) for dt in (0.0, 0.25, 0.5)],
        "max_centroid_drift_px": round(max(
            math.hypot(a[0] - b[0], a[1] - b[1]) for a in cents for b in cents), 3),
        "note": "pulse term enters draw_marble radius only (r += px(2)*pulse), "
                "center is the projected world point; v3 drift is its gate bob",
    }

def agg(kind_rows, tag, key):
    vals = [r[tag][key] for r in kind_rows if r.get(tag) and r[tag].get(key) is not None]
    if not vals:
        return None
    return {"n": len(vals), "max": max(vals), "mean": round(sum(vals) / len(vals), 3)}

summary = {}
for kind in sorted(set(r["kind"] for r in rows)):
    kr = [r for r in rows if r["kind"] == kind]
    summary[kind] = {tag: {"at_event": agg(kr, tag, "dist_at_event_px"),
                           "nearest_frame": agg(kr, tag, "dist_nearest_frame_px")}
                     for tag in ("v3", "v4")}

worst = {}
for tag in ("v3", "v4"):
    cand = [(r[tag]["dist_at_event_px"], r["kind"], r["event"]) for r in rows
            if r.get(tag) and r[tag].get("dist_at_event_px") is not None]
    worst[tag] = [{"dist_px": d, "kind": k, "event": e}
                  for d, k, e in sorted(cand, reverse=True)[:5]]

snap = {}
for tag, R in (("v3", V3), ("v4", V4)):
    snap[tag] = {}
    for m in R.MERGES:
        if m["short"] in ("2843792", "06fdec8"):
            pts = R.lane_pts_rs(m); b = float(m["merge_base_rank"])
            snap[tag][m["short"]] = {
                "slot_at_base": R.slot_at(pts, b),
                "slot_at_base_plus_0.05": round(R.slot_at(pts, b + 0.05), 3),
                "note": "v3 lane polyline ran backwards (exclusive time-ranks "
                        "precede merge-base rank): marble teleported a full "
                        "lane (165 world units, ~101 px) within one frame "
                        "after the split; v4 elbows clamped monotonic"}

out = {"resolution": "2560x1440", "fps": FPS, "summary": summary,
       "worst_offenders": worst, "pulse_hold_drift": pulse,
       "lane_snap_check": snap, "rows": rows}
(HERE / "sync_measurements4.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
for kind, s in summary.items():
    print(f"{kind:26s} v3 max {s['v3']['at_event']['max']:8.2f}px  "
          f"v4 max {s['v4']['at_event']['max']:8.3f}px  "
          f"(nearest frame: v3 {s['v3']['nearest_frame']['max']:8.2f}  "
          f"v4 {s['v4']['nearest_frame']['max']:8.2f})  n={s['v4']['at_event']['n']}")
print("pulse hold drift px: v3", pulse["v3"]["max_centroid_drift_px"],
      " v4", pulse["v4"]["max_centroid_drift_px"])
print("worst v3:", worst["v3"][0], "\nworst v4:", worst["v4"][0])
print("-> sync_measurements4.json")
