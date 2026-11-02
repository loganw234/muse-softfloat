import csv, pathlib, re, collections
root=pathlib.Path("worktrees/w1-f64")
rows=list(csv.DictReader(open(root/"docs/COVERAGE.tsv"), delimiter="\t"))
print("coverage fields", rows[0].keys())
w1=[r for r in rows if r.get("wave")=="1" and r.get("name","").startswith("msf64_")]
print("w1 msf64 count", len(w1))
for r in w1:
    print(r)
print("--- implemented.tsv ---")
print(open(root/"tables/implemented.tsv").read())
print("--- formats ---")
print(open(root/"tables/formats.tsv").read())
print("--- operations head ---")
for line in open(root/"tables/operations.tsv").read().splitlines()[:40]:
    print(line)
