import csv, pathlib, collections, sys
sys.stdout.reconfigure(encoding="utf-8")
root=pathlib.Path("worktrees/w1-f64")
lines=[l for l in (root/"docs/COVERAGE.tsv").read_text().splitlines() if not l.startswith("#")]
rows=list(csv.DictReader(lines, delimiter="\t"))
names=[r["name"] for r in rows if r["wave"]=="1" and r["name"].startswith("msf64_")]
counts=collections.Counter()
total=0
for p in sorted((root/"build/w1/directed-check").glob("*.vec")):
    for line in p.read_text().splitlines():
        if not line or line.startswith("#"): continue
        counts[line.split()[0]]+=1; total+=1
print("directed total", total)
missing=[n for n in names if counts[n]==0]
print("names", len(names), "covered", len(names)-len(missing), "missing", missing)
for n in names:
    print(n, counts[n])
# sweep coverage
sc=collections.Counter()
p=root/"build/w1/cross-sweep-210000.vec"
if p.exists():
    for line in p.read_text().splitlines():
        if line and not line.startswith("#"): sc[line.split()[0]]+=1
    print("sweep distinct ops", sorted(sc.items()))
