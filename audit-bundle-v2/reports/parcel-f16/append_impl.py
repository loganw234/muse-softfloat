import csv, pathlib
wt = pathlib.Path("worktrees/w2-f16")
lines = [l for l in open(wt/"docs/COVERAGE.tsv", encoding="utf-8") if not l.startswith("#")]
rows = list(csv.DictReader(lines, delimiter="\t"))
mine = [r["name"] for r in rows if r["wave"] == "2" and r["name"].startswith("msf16_")]
assert len(mine) == 236, len(mine)
p = wt/"tables/implemented.tsv"
data = p.read_bytes()
assert b"\r" not in data, "CR present before append"
assert data.endswith(b"\n")
existing = set()
for l in data.decode().splitlines():
    if l and not l.startswith("#") and not l.startswith("name\t"):
        existing.add(l.split("\t")[0])
assert not (existing & set(mine)), existing & set(mine)
append = "".join("%s\t2\n" % n for n in mine)
with open(p, "ab") as fh:
    fh.write(append.encode("utf-8"))
data2 = p.read_bytes()
print("appended", len(mine), "rows; total bytes", len(data2), "CR count", data2.count(b"\r"))
print("first mine", mine[0], "last mine", mine[-1])
