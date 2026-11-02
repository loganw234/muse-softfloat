"""Probe 3: dwell RULE audit from the copy's computed BLOCKS values."""
import math, re, sys
sys.path.insert(0, "worktrees/verify6-filmretime/video/segments")
sys.path.insert(0, "worktrees/verify6-filmretime/video")
import render_why as B
import idea, why, intro_outro as io

def RULE(words):
    return math.ceil(max(1.5, 0.5 + words / 2.5) * 2.0) / 2.0

def words_of(lines):
    n = 0
    for ln in lines:
        for tok in ln.split():
            if re.search(r"[A-Za-z0-9]", tok):
                n += 1
    return n

def audit(name, blocks):
    bad, n = [], 0
    for (s, t0, tg, lines) in blocks:
        n += 1
        w = words_of(lines)
        dwell = tg - t0
        r = RULE(w)
        if not (dwell + 1e-9 >= r and dwell > 0):
            bad.append((s, round(t0, 2), round(tg, 2), lines, w, r, round(dwell, 2)))
    print(f"{name}: {n} rows checked, {len(bad)} violations")
    for b in bad[:20]:
        print("  VIOL:", b)
    return bad

allbad = []
allbad += audit("idea.BLOCKS", idea.BLOCKS)
allbad += audit("why.BLOCKS", why.BLOCKS)
allbad += audit("intro.BLOCKS_INTRO", io.BLOCKS_INTRO)
allbad += audit("intro_outro.BLOCKS_OUTRO", io.BLOCKS_OUTRO)

# gone-times vs scene cut constants
print("idea cuts:", idea.T_IDEA, idea.T_COR, idea.T_PROVE, idea.T_METH, idea.T_Q,
      "DUR", idea.DUR, "FADE_T", idea.FADE_T)
print("why cuts:", why.O_SPEC, why.O_O1, why.O_O2, why.O_O3, why.O_SETTLE,
      "DUR", why.DUR, "FADE_T", why.FADE_T)
print("outro DUR:", io.OUTRO_DUR, "INTRO_DUR:", io.INTRO_DUR,
      "PANEL_T:", io.PANEL_T)
# per-scene gone consistency
for name, blocks in (("idea", idea.BLOCKS), ("why", why.BLOCKS)):
    byscene = {}
    for (s, t0, tg, lines) in blocks:
        byscene.setdefault(s, set()).add(tg)
    multi = {k: v for k, v in byscene.items() if len(v) > 1}
    print(name, "scenes with >1 gone-time:", multi if multi else "none")
# overlaps: scene intervals in output time
def intervals(blocks):
    iv = {}
    for (s, t0, tg, lines) in blocks:
        if s not in iv:
            iv[s] = [t0, tg]
        else:
            iv[s][0] = min(iv[s][0], t0)
    return iv
print("idea scene spans:", intervals(idea.BLOCKS))
print("why scene spans:", intervals(why.BLOCKS))

# gitvisual popup dwells recomputed
sys.path.insert(0, "worktrees/verify6-filmretime/video/segments")
import gitvisual as G
print("POPUP_WORDS:", G.POPUP_WORDS)
print("POPUP_DWELL:", G.POPUP_DWELL)
print("recomputed RULE:", [RULE(w) for w in G.POPUP_WORDS])
print("dwell+0.5 ok:", all(abs(d - (RULE(w) + 0.5)) < 1e-9
                           for d, w in zip(G.POPUP_DWELL, G.POPUP_WORDS)))
print("TOTAL:", G.TOTAL, "T_BRIDGE:", G.T_BRIDGE, "T_REPLAY:", G.T_REPLAY,
      "SHIFT:", G.SHIFT, "T_BOX:", G.T_BOX, "T_FADE:", G.T_FADE)
print("OVERALL VIOLATIONS:", len(allbad))
