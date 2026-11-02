#!/usr/bin/env python3
"""Cross-check: every COVERAGE row whose rounding column carries
the attribute has at least one committed ta vector line."""
import pathlib
import sys

wt = pathlib.Path(sys.argv[1])
cov = (wt / "docs/COVERAGE.tsv").read_text(encoding="utf-8").splitlines()
hdr = None
attr_rows = []
round_vals = {}
for line in cov:
    if line.startswith("#") or not line.strip():
        continue
    f = line.split("\t")
    if hdr is None:
        hdr = f
        continue
    d = dict(zip(hdr, f))
    round_vals[d.get("rounding", "?")] = round_vals.get(d.get("rounding", "?"), 0) + 1
    if d.get("rounding") == "attr":
        attr_rows.append(d)
print("rounding column values:", round_vals)
print("attribute rows:", len(attr_rows))

ta_ops = set()
for p in sorted((wt / "tests/vectors").glob("*.vec")):
    for line in p.read_text(encoding="utf-8").splitlines():
        t = line.split()
        if len(t) >= 2 and t[1] == "ta" and not line.startswith("#"):
            ta_ops.add(t[0])
print("distinct ta ops:", len(ta_ops))
names = {r[hdr[0]] for r in attr_rows}
print("first col header:", hdr[0], "sample:", sorted(names)[:3])
missing = sorted(names - ta_ops)
extra = sorted(o for o in (ta_ops - names) if not o.startswith("internal."))
print("attr rows with NO ta line:", len(missing), missing[:20])
print("ta ops not attribute rows (excl internal.pack):",
      len(extra), extra[:20])
print("internal pack ta ops:",
      sorted(o for o in ta_ops if o.startswith("internal.")))
sys.exit(0 if not missing else 1)
