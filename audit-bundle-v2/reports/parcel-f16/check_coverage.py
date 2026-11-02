import csv, pathlib, sys, collections
root = pathlib.Path("worktrees/w2-f16")
lines = [l for l in open(root/"docs/COVERAGE.tsv", encoding="utf-8") if not l.startswith("#")]
rows = list(csv.DictReader(lines, delimiter="\t"))
mine = set(r["name"] for r in rows if r["wave"] == "2" and r["name"].startswith("msf16_"))
seen = collections.Counter()
for p in sys.argv[1:]:
    for line in open(p, encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        seen[line.split()[0]] += 1
missing = sorted(mine - set(seen))
print("covered", len(mine) - len(missing), "of", len(mine), "missing", missing)
print("ops not in my 236:", sorted(set(seen) - mine))
if mine & set(seen):
    print("min count", min(seen[n] for n in mine if n in seen))
sys.exit(1 if missing or (set(seen) - mine) else 0)
