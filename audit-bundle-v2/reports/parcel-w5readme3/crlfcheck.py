"""crlfcheck.py - hand-edited files must stay LF (gitattributes * -text)."""
from pathlib import Path

WT = Path(__file__).resolve().parents[2] / "worktrees" / "w5-readme3"
files = ["README.md", "site/build_data.py", "site/build.py", "site/glue.c",
         "site/app.js", "site/index.html", "site/README.md",
         "docs/metrics/briefs.jsonl", "site/data.json", "site/ops.json",
         "site/vectors-sample.json"]
bad = []
for f in files:
    b = (WT / f).read_bytes()
    n = b.count(b"\r\n")
    print(f"{f}: {len(b)} bytes, CRLF={n}")
    if n:
        bad.append(f)
print("CRLFCHECK", "PASS" if not bad else f"FAIL {bad}")
raise SystemExit(0 if not bad else 1)
