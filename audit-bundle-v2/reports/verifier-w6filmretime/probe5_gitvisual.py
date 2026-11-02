"""Probe 5: gitvisual sync from the copy's own modules/history."""
import json, sys
sys.path.insert(0, "worktrees/verify6-filmretime/video/segments")
sys.path.insert(0, "worktrees/verify6-filmretime/video")
import gitvisual as G

HIST = json.loads(open(
    "worktrees/verify6-filmretime/video/segments/history.json").read())
MERGES = HIST["merges"]
ranks = {m["short"]: m["rank"] for m in MERGES}
print("IAS_RANK:", G.IAS_RANK, "history d9718cf:", ranks.get("d9718cf"))
g1 = HIST["gate_anchors"]["gate1_kissfft_merge"]
print("G1_RANK:", G.G1_RANK, "history gate1:", g1, ranks.get(g1))
print("LAST_RANK:", G.LAST_RANK, "commit_count_all-1:",
      HIST["commit_count_all"] - 1)
print("gate ranks:", [g["rank"] for g in G.GATES])
for g in G.GATES:
    print(f"gate {g['id']}: rank={g['rank']} t0={g['t0']} t1={g['t1']} "
          f"window={round(g['t1'] - g['t0'], 2)}")
print("legs (dur, ra->rb):",
      [(round(tb - ta, 2), ra, rb) for (ta, tb, ra, rb) in G.LEGS])
print("TOTAL:", G.TOTAL)
# cursor_rank on gate rank at t0 and through window
import math
ok = True
for g in G.GATES:
    for dt in (0.0, (g["t1"] - g["t0"]) / 2, (g["t1"] - g["t0"]) - 0.01):
        c = G.cursor_rank(g["t0"] + dt)
        if abs(c - g["rank"]) > 1e-9:
            ok = False
            print(f"MISMATCH gate {g['id']} t0+{dt}: cursor={c} rank={g['rank']}")
print("cursor-on-rank-through-window:", ok)
# monotonic over dense sample
ts = [i * 0.1 for i in range(int(G.TOTAL * 10) + 1)]
vals = [G.cursor_rank(t) for t in ts]
mono = all(b + 1e-9 >= a for a, b in zip(vals, vals[1:]))
print("monotonic 0.1s sample:", mono,
      "min/max:", min(vals), max(vals))
# at-event check: node arrival times hold popup dwell (event position = arrival)
print("ARRIVALS:", [round(a, 2) for a in G.ARRIVALS])
print("T_BRIDGE recompute:", round(G.ARRIVALS[-1] + G.POPUP_DWELL[-1], 2))
