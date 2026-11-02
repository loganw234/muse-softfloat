#!/usr/bin/env bash
# v01_counts.sh - re-derive every public number from the verify copy (read-only).
set -u
V="$PWD/worktrees/verify5-readme3"
P="$PWD/scratch/verifier-w5readme3"
export MSF_PYTHON="$PWD/.venv/Scripts/python.exe"
LOG="$P/v01_counts.log"
: > "$LOG"
echo "== COVERAGE ==" | tee -a "$LOG"
"$MSF_PYTHON" - "$V" >> "$LOG" 2>&1 <<'EOF'
import sys
from pathlib import Path
from collections import Counter
V = Path(sys.argv[1])
rows = []
for line in (V/"docs"/"COVERAGE.tsv").read_text().splitlines():
    if not line or line.startswith("#") or line.startswith("name\t"):
        continue
    f = line.split("\t")
    rows.append(f)
print("coverage_rows =", len(rows))
print("tier:", dict(Counter(f[12] for f in rows)))
print("status:", dict(Counter(f[8] for f in rows)))
print("authority unconfirmed:", sum(1 for f in rows if f[9]=="unconfirmed"))
# fifth attribute census
attr = [f for f in rows if len(f) > 13 and f[13].strip() not in ("", "-")]
print("attr_rows(col13 non-empty) =", len(attr))
import collections
print("attr values:", dict(collections.Counter(f[13] for f in rows if len(f)>13)))
# Tier2 families
t2 = [f for f in rows if f[12]=="2"]
print("tier2 rows =", len(t2))
print("tier2 dests:", dict(Counter(f[3] for f in t2)))
print("tier2 waves:", dict(Counter(f[7] for f in t2)))
EOF
echo "== DISPATCH ==" | tee -a "$LOG"
"$MSF_PYTHON" - "$V" >> "$LOG" 2>&1 <<'EOF'
import sys, re
from pathlib import Path
V = Path(sys.argv[1])
text = (V/"tests"/"msf_dispatch.h").read_text()
i = text.find("static const msf_op_desc_t MSF_OPS[]")
j = text.find("};", i)
pat = re.compile(r'\{\s*"([^"]+)",\s*"([^"]+)",\s*(MSF_SIG_\w+),\s*(MSF_RK_\w+),\s*\{\s*(MSF_AK_\w+),\s*(MSF_AK_\w+),\s*(MSF_AK_\w+)\s*\},\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\w+),\s*(\w+)\s*\}')
ops = list(pat.finditer(text[i:j]))
print("dispatch_total =", len(ops))
runnable = [m for m in ops if m.group(13) != "0"]
pair = [m for m in ops if m.group(13)=="0" and m.group(14)!="0"]
nonhex = [m for m in ops if m.group(13)=="0" and m.group(14)=="0"]
print("runnable(call!=0) =", len(runnable))
print("pair(call==0,pair!=0) =", len(pair))
print("nonhex(both 0) =", len(nonhex))
print("pair names:", sorted(m.group(1) for m in pair))
print("has_rm census:", sum(1 for m in ops if m.group(9)=="1"))
EOF
echo "== VECTORS ==" | tee -a "$LOG"
"$MSF_PYTHON" - "$V" >> "$LOG" 2>&1 <<'EOF'
import sys
from pathlib import Path
V = Path(sys.argv[1])
tot = 0
per = {}
for p in sorted((V/"tests"/"vectors").glob("*.vec")):
    n = sum(1 for raw in p.read_text().splitlines() if (s:=raw.strip()) and not s.startswith("#"))
    per[p.name] = n
    tot += n
print("committed_total =", tot)
print("files =", len(per))
for k, v in per.items():
    print(f"  {k}: {v}")
EOF
echo "== PLANTS ==" | tee -a "$LOG"
"$MSF_PYTHON" - "$V" >> "$LOG" 2>&1 <<'EOF'
import sys, json
from pathlib import Path
from collections import Counter
V = Path(sys.argv[1])
plants = [json.loads(l) for l in (V/"docs"/"metrics"/"plants.jsonl").read_text().splitlines() if l.strip()]
print("plants_total =", len(plants))
print("caught =", sum(1 for p in plants if p.get("grade")=="caught"))
print("by_wave:", dict(Counter((p["wave"], p.get("grade")) for p in plants)))
waves = {}
for p in plants:
    w = waves.setdefault(p["wave"], {"caught":0,"total":0})
    w["total"] += 1
    if p.get("grade")=="caught": w["caught"] += 1
for w in sorted(waves): print(f"  {w}: {waves[w]['caught']}/{waves[w]['total']}")
EOF
echo "== METRICS ROWS ==" | tee -a "$LOG"
for f in usage.jsonl passes.jsonl escalations.jsonl briefs.jsonl fetches.jsonl; do
  if [ -f "$V/docs/metrics/$f" ]; then
    n=$(grep -c . "$V/docs/metrics/$f")
    echo "$f lines=$n" | tee -a "$LOG"
  else
    echo "$f MISSING" | tee -a "$LOG"
  fi
done
echo "== done ==" | tee -a "$LOG"
