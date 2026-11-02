"""Dump popup/timing constants from gitvisual.py for the timing-freeze proof."""
import sys

sys.path.insert(0, "video/segments")
import gitvisual as g

print("POPUP_WORDS", g.POPUP_WORDS)
print("POPUP_DWELL", g.POPUP_DWELL)
print("ARRIVALS", g.ARRIVALS)
print("T_BRIDGE", g.T_BRIDGE)
print("T_REPLAY", g.T_REPLAY)
print("SHIFT", g.SHIFT)
print("TOTAL", g.TOTAL)
print("T_BOX", g.T_BOX, "T_FADE", g.T_FADE)
print("GATES", [(d["rank"], d["t0"], d["t1"]) for d in g.GATES])
print("LEGS", g.LEGS)
print("POPUP5")
for t, lines in g.POPUP5:
    print("  %r %r" % (t, lines))
