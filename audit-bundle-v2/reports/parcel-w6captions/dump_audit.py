import sys, json
from pathlib import Path
WT = Path("worktrees/w6-captions").resolve()
SEG = WT / "video" / "segments"
sys.path.insert(0, str(SEG))
sys.path.insert(0, str(WT / "video"))

import idea, why, intro_outro
print("=== IDEA BLOCKS", len(idea.BLOCKS))
for b in idea.BLOCKS: print(b)
print("=== WHY BLOCKS", len(why.BLOCKS))
for b in why.BLOCKS: print(b)
print("=== INTRO", intro_outro.BLOCKS_INTRO)
print("=== OUTRO", len(intro_outro.BLOCKS_OUTRO))
for b in intro_outro.BLOCKS_OUTRO: print(b)
print("=== importing gitvisual...")
import gitvisual as g
print("POPUP5", g.POPUP5)
print("POPUP_DWELL", g.POPUP_DWELL)
print("ARRIVALS", g.ARRIVALS)
print("T_BRIDGE", g.T_BRIDGE, "T_REPLAY", g.T_REPLAY, "SHIFT", g.SHIFT,
      "T_BOX", g.T_BOX, "T_FADE", g.T_FADE, "TOTAL", g.TOTAL)
for gate in g.GATES: print("GATE", gate)
print("NODES", len(g.NODES))
print("DURs idea", idea.DUR, "why", why.DUR, "intro/outro", intro_outro.INTRO_DUR, intro_outro.OUTRO_DUR)
