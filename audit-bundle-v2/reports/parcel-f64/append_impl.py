import csv, pathlib, sys
sys.stdout.reconfigure(encoding="utf-8")
root=pathlib.Path("worktrees/w1-f64")
lines=[l for l in (root/"docs/COVERAGE.tsv").read_text().splitlines(True) if not l.startswith("#")]
rows=list(csv.DictReader(lines, delimiter="\t"))
names=[r["name"] for r in rows if r["wave"]=="1" and r["name"].startswith("msf64_")]
print(len(names))
p=root/"tables/implemented.tsv"
txt=p.read_bytes().decode("utf-8")
existing=set()
for line in txt.splitlines():
    if line and not line.startswith("#") and "\t" in line:
        existing.add(line.split("\t")[0])
dup=[n for n in names if n in existing]
print("dups", dup)
assert not dup and len(names)==173
assert txt.endswith("\n")
add="".join(f"{n}\t1\n" for n in names)
p.write_bytes((txt+add).encode("utf-8"))
print("appended", len(add.splitlines()))
