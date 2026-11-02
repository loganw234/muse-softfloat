"""Render eyeball-check stills from render_gitvisual5 in one process."""
import sys
from pathlib import Path
import render_gitvisual5 as R

OUT = Path(__file__).resolve().parent / "stills5"
OUT.mkdir(exist_ok=True)
TIMES = [float(x) for x in sys.argv[1:]] or [8.0]
for t in TIMES:
    p = OUT / f"chk_{t:05.1f}s.png"
    R.frame_at(t).save(p)
    print(t, "->", p, "cursor", round(R.cursor_rank(t), 1), flush=True)
