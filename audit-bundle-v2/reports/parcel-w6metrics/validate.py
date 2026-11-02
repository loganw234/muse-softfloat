#!/usr/bin/env python3
"""Build combined-check copies (frozen file + new rows) in scratch and hash them."""
import hashlib
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
WS = Path(r"C:\Users\logan\source\repos\Muse-Softfloat")
HERE = Path(__file__).parent
DST = WS / "worktrees/w6-metrics/docs/metrics"
OUT = HERE / "combined-check"
OUT.mkdir(exist_ok=True)
for name in ("usage", "passes", "escalations", "briefs"):
    before = (DST / f"{name}.jsonl").read_bytes()
    assert before.endswith(b"\n"), name
    new = (HERE / f"new-{name}.jsonl").read_bytes()
    combined = before + new
    (OUT / f"{name}.jsonl").write_bytes(combined)
    print(f"{name}: rows {before.decode('utf-8').count(chr(10))} "
          f"-> {combined.decode('utf-8').count(chr(10))}; prefix sha256 {hashlib.sha256(before).hexdigest()[:16]}; "
          f"combined sha256 {hashlib.sha256(combined).hexdigest()[:16]}")
print("combined-check written")
