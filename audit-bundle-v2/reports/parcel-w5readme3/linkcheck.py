"""linkcheck.py - every relative link/path in the edited docs resolves."""
import re
from pathlib import Path

WT = Path(__file__).resolve().parents[2] / "worktrees" / "w5-readme3"
bad = 0
for rel in ["README.md", "site/README.md"]:
    txt = (WT / rel).read_text(encoding="utf-8")
    base = (WT / rel).parent
    for m in re.finditer(r"\]\(([^)\s]+)\)", txt):
        url = m.group(1)
        if url.startswith(("http://", "https://", "#", "mailto:")):
            continue
        path = url.split("#")[0]
        if not path:
            continue
        ok = (base / path).exists()
        print(f"{'ok  ' if ok else 'MISS'} {rel} -> {url}")
        bad += 0 if ok else 1
# New where-things-live rows name directories/files in backticks.
for p in ["docs/TWIDDLES.md", "demo/README.md", "demo/run_demo.sh",
          "site/README.md", "site/index.html", "docs/metrics/README.md",
          "video/out/final.mp4", "video/README.md", "LICENSE",
          "docs/studies/SF-0.md", "docs/studies/SF-1.md",
          "docs/studies/SF-2.md", "docs/COVERAGE.tsv", "docs/RECORD.md"]:
    ok = (WT / p).exists()
    print(f"{'ok  ' if ok else 'MISS'} path {p}")
    bad += 0 if ok else 1
print("LINKCHECK", "PASS" if bad == 0 else f"FAIL ({bad})")
raise SystemExit(0 if bad == 0 else 1)
