"""recount.py - recount every displayed number from the copy's own sources.

Reads ONLY worktrees/verify5-site. Compares against site/data.json,
site/ops.json, site/vectors-sample.json and prints a verdict per claim.
Run under Git Bash: python scratch/verifier-w5site/recount.py
"""
import json
import sys
from collections import Counter
from pathlib import Path

COPY = Path("worktrees/verify5-site")
SITE = COPY / "site"
ok = True

def check(name, got, want):
    global ok
    mark = "OK  " if got == want else "FAIL"
    if got != want:
        ok = False
    print(f"{mark} {name}: got={got} want={want}")

# --- vectors: non-blank, non-# lines ---
total = 0
per_file = Counter()
for p in sorted((COPY / "tests" / "vectors").glob("*.vec")):
    n = 0
    for raw in p.read_text(encoding="utf-8", errors="replace").splitlines():
        s = raw.strip()
        if s and not s.startswith("#"):
            total += 1
            n += 1
    per_file[p.name] = n
data = json.loads((SITE / "data.json").read_text(encoding="utf-8"))
check("vector total", total, data["vectors"]["total"])
check("vector total vs 182518", total, 182518)
check("per-file map", dict(sorted(per_file.items())), data["vectors"]["files"])

# --- coverage census ---
rows = [l for l in (COPY / "docs" / "COVERAGE.tsv").read_text(
    encoding="utf-8", errors="replace").splitlines()
    if l and not l.startswith("#") and not l.startswith("name\t")]
check("coverage rows", len(rows), data["instantiations"]["total"])
check("coverage rows vs 828", len(rows), 828)
tier = Counter(r.split("\t")[12] for r in rows)
stat = Counter(r.split("\t")[8] for r in rows)
check("tier1", tier.get("1", 0), data["instantiations"]["tier1"])
check("tier2", tier.get("2", 0), data["instantiations"]["tier2"])
check("implemented", stat.get("implemented", 0),
      data["instantiations"]["implemented"])
exp = [r.split("\t")[0] for r in rows
       if "exp2" in r.split("\t")[0].lower()
       or "log2" in r.split("\t")[0].lower()
       or "augment" in (r.split("\t")[1] + r.split("\t")[0]).lower()]
check("exp2/log2/augmented rows in COVERAGE", len(exp), 0)

# --- plants census ---
plants = [json.loads(l) for l in
          (COPY / "docs" / "metrics" / "plants.jsonl").read_text(
              encoding="utf-8").splitlines() if l.strip()]
caught = sum(1 for p in plants if p.get("grade") == "caught")
check("plants total", len(plants), data["plants"]["total"])
check("plants caught (file) vs data.json top-level",
      caught, data["plants"]["caught"])
waves = {}
for p in plants:
    w = waves.setdefault(p["wave"], {"caught": 0, "total": 0})
    w["total"] += 1
    if p.get("grade") == "caught":
        w["caught"] += 1
check("plants caught (file) vs sum of data.json by_wave",
      caught, sum(r["caught"] for r in data["plants"]["by_wave"]))
check("plants by_wave", waves,
      {r["wave"]: {"caught": r["caught"], "total": r["total"]}
       for r in data["plants"]["by_wave"]})

# --- ops.json ---
ops = json.loads((SITE / "ops.json").read_text(encoding="utf-8"))
check("ops total", len(ops), data["sample"]["ops_total"])
check("ops runnable", sum(1 for o in ops if o["runnable"]),
      data["sample"]["ops_runnable"])

# --- sample: recount + provenance spot check ---
sample = json.loads((SITE / "vectors-sample.json").read_text(
    encoding="utf-8"))
check("sample length", len(sample), data["sample"]["vectors"])
check("sample ops covered", len({s["op"] for s in sample}),
      data["sample"]["ops_covered"])
vec_lines = {}
for p in (COPY / "tests" / "vectors").glob("*.vec"):
    vec_lines[p.name] = set(
        l.strip() for l in p.read_text(encoding="utf-8",
                                       errors="replace").splitlines()
        if l.strip() and not l.strip().startswith("#"))
missing = 0
for s in sample:
    line = f"{s['op']} {s['rm']} {' '.join(s['args'])} -> " \
        f"{s['result']} {s['flags']} {s['prov']}"
    if line not in vec_lines.get(s["file"], set()):
        missing += 1
        if missing <= 5:
            print(f"  sample line not found verbatim: {line}")
check("sample lines found verbatim in tests/vectors/",
      len(sample) - missing, len(sample))

print("RECALL-RESULT:", "ALL-OK" if ok else "MISMATCHES-FOUND")
sys.exit(0 if ok else 1)
