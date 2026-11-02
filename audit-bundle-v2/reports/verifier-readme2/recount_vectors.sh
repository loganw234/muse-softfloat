#!/usr/bin/env bash
# Recount committed vectors + ties-to-away lines from tests/vectors/.
# Usage: MSF_PYTHON=python3 bash recount_vectors.sh <repo-copy-root>
set -u
PY="${MSF_PYTHON:-python3}"
ROOT="${1:?copy root required}"
"$PY" - "$ROOT" <<'EOF'
import pathlib, sys
d = pathlib.Path(sys.argv[1]) / "tests" / "vectors"
tot = ta = files = 0
per = {}
for f in sorted(d.glob("*.vec")):
    files += 1
    n = t = 0
    for l in f.open(encoding="utf-8", errors="replace"):
        s = l.strip()
        if not s or s.startswith("#"):
            continue
        n += 1
        if " ta " in l:
            t += 1
    per[f.name] = (n, t)
    tot += n
    ta += t
print(f"files={files} committed_vectors={tot} ta_data_lines={ta}")
EOF
