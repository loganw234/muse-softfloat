import csv, pathlib, sys, collections
root=pathlib.Path("worktrees/w1-f32")
lines=[l for l in open(root/"docs/COVERAGE.tsv", encoding='utf-8').read().splitlines() if not l.startswith('#')]
rows=list(csv.DictReader(lines, delimiter='\t'))
mine=set(r['name'] for r in rows if r['wave']=='1' and r['name'].startswith('msf32_'))
seen=collections.Counter()
for p in sys.argv[1:]:
    for line in open(p, encoding='utf-8'):
        if line.startswith('#') or not line.strip(): continue
        seen[line.split()[0]]+=1
missing=sorted(mine-set(seen))
print("covered", len(mine)-len(missing), "missing", missing)
extra=sorted(set(seen)-mine)
print("ops not in my 173:", extra)
print("min count", min(seen[n] for n in mine if n in seen) if mine&set(seen) else 0)
