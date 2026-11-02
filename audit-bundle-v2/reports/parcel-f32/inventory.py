import csv, pathlib, collections
root=pathlib.Path("worktrees/w1-f32")
lines=[l for l in open(root/"docs/COVERAGE.tsv", encoding='utf-8').read().splitlines() if not l.startswith('#')]
rows=list(csv.DictReader(lines, delimiter='\t'))
print("header", list(rows[0].keys()))
print("sample", rows[0])
mine=[r for r in rows if r.get('wave')=='1' and r[list(r.keys())[0]].startswith('msf32_')]
print("count mine", len(mine))
for r in mine:
    print("\t".join(r.values()))
print("--- implemented.tsv ---")
print(open(root/"tables/implemented.tsv").read())
print("--- operations head ---")
for line in open(root/"tables/operations.tsv").read().splitlines()[:5]:
    print(repr(line))
