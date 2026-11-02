import sys
from pathlib import Path
SEG = Path(r"C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w6-filmretime\video\segments")
sys.path.insert(0, str(SEG))
import gitvisual as G
print("TOTAL", G.TOTAL, "T_FADE", G.T_FADE, "T_BOX", G.T_BOX, "SHIFT", G.SHIFT)
print("T_BRIDGE", G.T_BRIDGE, "T_REPLAY", G.T_REPLAY)
print("POPUP_DWELL", G.POPUP_DWELL, "rule", [G.rule_dwell(w) for w in G.POPUP_WORDS])
print("ARRIVALS", G.ARRIVALS)
for g in G.GATES:
    print("gate", g["id"], g["rank"], g["t0"], g["t1"], "dur", g["t1"]-g["t0"],
          "cursor@t0", G.cursor_rank(g["t0"]), "cursor@mid", G.cursor_rank((g["t0"]+g["t1"])/2))
print("LEGS", G.LEGS, "leg durs", [b-a for a,b,_,_ in G.LEGS])
print("cursor at T_BOX", G.cursor_rank(G.T_BOX), "LAST", G.LAST_RANK)
prev, mono = -1.0, True
for k in range(int(G.TOTAL*20)+1):
    c = G.cursor_rank(k/20.0)
    mono = mono and c >= prev - 1e-12
    prev = c
print("cursor monotonic", mono)
# gate ranks unchanged check vs history anchors
print("IAS/G1/LAST ranks", G.IAS_RANK, G.G1_RANK, G.LAST_RANK)
