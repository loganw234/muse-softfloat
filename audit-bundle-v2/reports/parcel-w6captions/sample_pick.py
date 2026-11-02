"""Sampled truth-check helper: print midpoint times for chosen cue indices.

Usage (from the workspace root):
  .venv/Scripts/python.exe scratch/parcel-w6captions/sample_pick.py
"""
import sys
from pathlib import Path

WS = Path(__file__).resolve().parent.parent.parent
WT = WS / "worktrees" / "w6-captions"
sys.path.insert(0, str(WT / "video" / "segments"))
sys.path.insert(0, str(WT / "video"))
import captions as C  # noqa: E402

# 15 samples spread over all five segments (cue numbers are 1-based
# into the sorted cue list, matching the .srt numbering).
SAMPLES = [1, 6, 12, 19, 34, 41, 49, 54, 59, 62, 66, 69, 70, 72, 77]

cues = C.build_cues()
print(f"cues: {len(cues)}")
for n in SAMPLES:
    c = cues[n - 1]
    mid = (C._ms(c.start) + C._ms(c.end)) / 2 / 1000
    text = " / ".join(c.lines)
    print(f"cue {n:2d} [{c.segment:9s}] {mid:8.3f}s  {c.start:9.3f}..{c.end:9.3f}  {text}")
