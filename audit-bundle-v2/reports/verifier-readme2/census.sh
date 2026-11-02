#!/usr/bin/env bash
# Attr-row census from docs/COVERAGE.tsv + plant grades from plants.jsonl.
# Usage: MSF_PYTHON=python3 bash census.sh <repo-copy-root>
set -u
PY="${MSF_PYTHON:-python3}"
ROOT="${1:?copy root required}"
"$PY" - "$ROOT" <<'EOF'
import collections, json, pathlib, sys
root = pathlib.Path(sys.argv[1])
hdr = None
rows = []
for l in (root / "docs" / "COVERAGE.tsv").read_text().splitlines():
    if not l.strip() or l.startswith("#"):
        continue
    if hdr is None:
        hdr = l.split("\t")
        continue
    rows.append(dict(zip(hdr, l.split("\t"))))
print("coverage_data_rows=", len(rows))
print("status=", dict(collections.Counter(r["status"] for r in rows)))
print("tier=", dict(collections.Counter(r["tier"] for r in rows)))
print("rounding=", dict(collections.Counter(r["rounding"] for r in rows)))
print("tier2_std=", sorted({r["std_name"] for r in rows if r["tier"] == "2"}))
print("has_rsqrt=", any("rsqrt" in r["name"].lower() for r in rows))
print("has_hypot=", any("hypot" in r["name"].lower() for r in rows))
print("has_exp2=", any("exp2" in r["name"].lower() for r in rows))
print("has_log2=", any("log2" in r["name"].lower() for r in rows))
print("has_aug=", any("aug" in r["name"].lower() for r in rows))
prows = [json.loads(l) for l in (root / "docs" / "metrics" / "plants.jsonl").open() if l.strip()]
print("plants_total=", len(prows), "grades=", dict(collections.Counter(r.get("grade") for r in prows)))
for r in prows:
    if r.get("grade") != "caught":
        print("MISSED:", r.get("wave"), r.get("verifier"), "plant", r.get("plant"), "-", r.get("shape"))
EOF
