from pathlib import Path
import sys
sys.path.insert(0, "C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6captions/scripts")
from strict import parse_srt, parse_vtt
base = Path("C:/Users/logan/source/repos/Muse-Softfloat")
spans = parse_srt((base / "worktrees/verify6-captions/video/out/assembly_v6.srt").read_text(encoding="utf-8"))
lines = []
for i, (a, b, ls) in enumerate(spans, start=1):
    lines.append(f"{i:3d} {a/1000:8.3f}..{b/1000:8.3f} mid={(a+b)/2000:8.3f} | {' / '.join(ls)[:120]}")
(base / "scratch/verifier-w6captions/cues.txt").write_text("\n".join(lines), encoding="utf-8")
print(f"wrote {len(lines)} cues")
