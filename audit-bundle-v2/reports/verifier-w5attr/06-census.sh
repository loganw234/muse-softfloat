#!/usr/bin/env bash
# 06-census.sh - coverage census: all 255 attr rows carry ta lines;
# decided-vs-relabeled split per family; zero new inventory rows vs
# parent; committed ta volume vs directed column.
set -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
V="$SCRATCH"
export TMPDIR="$V/tmp" TMP="$V/tmp" TEMP="$V/tmp"
echo "== inventory: parent vs copy =="
git -C "$COPY" show 889ec2e:docs/COVERAGE.tsv | awk '!/^#/&&NF' | wc -l
awk '!/^#/&&NF' "$COPY/docs/COVERAGE.tsv" | wc -l
echo "== attr rows in copy COVERAGE =="
"$MSF_PYTHON" - "$COPY/docs/COVERAGE.tsv" <<'EOF'
import csv,sys
lines=[l for l in open(sys.argv[1]) if not l.startswith("#")]
rows=list(csv.DictReader(lines,delimiter="\t"))
attr=[r for r in rows if r.get("rounding")=="attr"]
print("total",len(rows),"attr",len(attr))
from collections import Counter
print("attr split",Counter((r.get("tier"),r.get("status")) for r in attr))
print("implemented total",sum(1 for r in rows if r.get("status")=="implemented"))
EOF
echo "== attr rows with zero committed ta lines (per-op check) =="
"$MSF_PYTHON" - "$COPY/docs/COVERAGE.tsv" "$COPY/tests/vectors" <<'EOF'
import csv,sys,glob,re,os
lines=[l for l in open(sys.argv[1]) if not l.startswith("#")]
rows=list(csv.DictReader(lines,delimiter="\t"))
vecs={}
for f in glob.glob(sys.argv[2]+"/*.vec"):
    ops=set()
    for l in open(f,errors="replace"):
        if l.startswith("#") or not l.strip(): continue
        p=l.split()
        if len(p)>2 and p[1]=="ta": ops.add(p[0])
    vecs[f]=ops
allops=set().union(*vecs.values())
attr=[r["name"] for r in rows if r.get("rounding")=="attr"]
missing=[a for a in attr if a not in allops]
print("attr rows:",len(attr),"missing ta:",len(missing))
for m in missing[:20]: print("MISSING:",m)
EOF
echo "== ta lines per committed vector file =="
grep -c " ta " "$COPY"/tests/vectors/*.vec
echo "== total ta lines =="
grep -h " ta " "$COPY"/tests/vectors/*.vec | wc -l
echo "== relabeled (trig ta-relabel) lines =="
grep -h "ta-relabel" "$COPY"/tests/vectors/*.vec | wc -l
echo "== tz lines (directed column reference) =="
grep -h " tz " "$COPY"/tests/vectors/*.vec | wc -l
