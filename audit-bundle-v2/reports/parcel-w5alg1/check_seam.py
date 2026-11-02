"""Seam negative controls for parcel-w5alg1 (scratch only).

1. An unknown sig token fed to gen_tables.expand() must refuse.
2. The math_bin token expands hypot to 3 planned-shaped rows.
3. Tier counts on the regenerated COVERAGE: tier1 783, tier2 45.
Run from the worktree root with MSF_PYTHON.
"""
import csv
import importlib.util
import sys

spec = importlib.util.spec_from_file_location("gen_tables", "tools/gen_tables.py")
gt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gt)

base = {
    "op": "probe_op", "std_name": "probe", "clause": "9.2",
    "sig": "bogus_sig", "rounding": "attr", "flags": "yes",
    "wave": "5", "authority": "mpfr-exact", "vectors": "v",
    "comparison": "exact", "tier": "2", "claim": "C-754",
}
try:
    gt.expand(dict(base))
    print("CONTROL unknown-sig: NOT REFUSED")
    sys.exit(1)
except SystemExit as e:
    print(f"CONTROL unknown-sig: refused as required ({e})")

row = dict(base)
row.update({"op": "hypot", "std_name": "hypot", "sig": "math_bin"})
out = gt.expand(row)
names = [o["name"] for o in out]
print(f"math_bin expansion: {names} argkinds={[o['argkinds'] for o in out]}")
assert names == ["msf16_hypot", "msf32_hypot", "msf64_hypot"], names
assert all(o["sources"] == o["dest"] + "," + o["dest"] for o in out)
assert all(o["sig"] == "math_bin" for o in out)

row.update({"op": "r_sqrt", "std_name": "rSqrt", "sig": "math_un"})
out = gt.expand(row)
names = [o["name"] for o in out]
print(f"math_un expansion: {names}")
assert names == ["msf16_r_sqrt", "msf32_r_sqrt", "msf64_r_sqrt"], names

with open("docs/COVERAGE.tsv", encoding="utf-8") as fh:
    rows = [r for r in csv.DictReader(
        (ln for ln in fh if not ln.startswith("#")), delimiter="\t")]
t1 = [r for r in rows if r["tier"] == "1"]
t2 = [r for r in rows if r["tier"] == "2"]
t1i = sum(1 for r in t1 if r["status"] == "implemented")
t2i = sum(1 for r in t2 if r["status"] == "implemented")
t2p = [r["name"] for r in t2 if r["status"] == "planned"]
print(f"coverage: tier1 {t1i} implemented of {len(t1)}; "
      f"tier2 {t2i} implemented of {len(t2)}; planned: {t2p}")
assert len(t1) == 783 and t1i == 783, (len(t1), t1i)
assert len(t2) == 45, len(t2)
print("SEAM CHECKS: PASS")
