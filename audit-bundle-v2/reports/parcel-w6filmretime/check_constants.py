import sys
from pathlib import Path
SEG = Path(r"C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w6-filmretime\video\segments")
sys.path.insert(0, str(SEG))
import idea, why, intro_outro as io
print("idea DUR", idea.DUR, "NFRAMES", idea.NFRAMES)
print("idea BLOCKS scenes", sorted(set(b[0] for b in idea.BLOCKS)))
for b in idea.BLOCKS: print("  idea", b[0], b[1], b[2])
print("why DUR", why.DUR, "NFRAMES", why.NFRAMES)
for b in why.BLOCKS: print("  why", b[0], b[1], b[2], b[3][:1])
print("why has scene_title:", hasattr(why, "scene_title"))
print("io INTRO/OUTRO", io.INTRO_DUR, io.OUTRO_DUR, "PANEL_T", io.PANEL_T, "SS", io.SS)
print("io BLOCKS_OUTRO", io.BLOCKS_OUTRO)
total = io.INTRO_DUR + idea.DUR + why.DUR + io.OUTRO_DUR
print("subtotal without gitvisual", total)
# rule check: dwell >= rule for idea/why blocks (words approx like gitvisual rule)
import math, re
def words(lines):
    n = 0
    for ln in lines:
        n += len([w for w in ln.split() if re.search(r"[A-Za-z0-9]", w)])
    return n
def rule(w): return math.ceil(max(1.5, 0.5 + w / 2.5) * 2) / 2
for name, blocks in (("idea", idea.BLOCKS), ("why", why.BLOCKS)):
    bad = []
    for s, a, b, lines in blocks:
        d = b - a
        if d + 1e-9 < rule(words(lines)):
            bad.append((s, a, round(d,2), rule(words(lines)), lines))
    print(name, "rule violations:", bad)
# frame smoke at scene boundaries
for t in (0.0, 0.5, 4.9, 5.0, 10.9, 11.0, 21.5, 25.0, 25.9):
    im = idea.frame(t); print("idea frame", t, im.size, im.getpixel((5,5)))
for t in (0.0, 0.4, 0.5, 6.9, 7.0, 13.5, 20.5, 25.5, 31.0, 31.9):
    im = why.frame(t); print("why frame", t, im.size, im.getpixel((5,5)))
