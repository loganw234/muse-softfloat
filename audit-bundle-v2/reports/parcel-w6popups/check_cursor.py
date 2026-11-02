"""Probe (d): cursor exactly on each gate rank at its t0; TOTAL 108.0."""
import sys

sys.path.insert(0, "video/segments")
import gitvisual as g

g.assign_lanes()
g.all_lane_pts()
ok = True
for gate in g.GATES:
    cur = g.cursor_rank(gate["t0"])
    match = abs(cur - gate["rank"]) < 1e-9
    ok &= match
    print("gate rank=%s t0=%s cursor=%s exact=%s"
          % (gate["rank"], gate["t0"], cur, match))
print("TOTAL", g.TOTAL, "is108", g.TOTAL == 108.0)
mono = all(g.cursor_rank(t + 0.01) >= g.cursor_rank(t)
           for t in [x * 0.5 for x in range(0, 216)])
print("cursor monotonic:", mono)
assert ok and g.TOTAL == 108.0 and mono
print("CURSOR SPOT CHECK: PASS")
