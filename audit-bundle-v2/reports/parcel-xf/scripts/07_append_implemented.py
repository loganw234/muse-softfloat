import csv, pathlib
root = pathlib.Path(r"C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w2-xf")
def read_tsv(p):
    lines=[l for l in open(p, encoding="utf-8") if not l.startswith("#")]
    return list(csv.DictReader(lines, delimiter="\t"))
cov=read_tsv(root/"docs/COVERAGE.tsv")
names=[r["name"] for r in cov if r["wave"]=="2" and (r["name"].startswith("msf32_") or r["name"].startswith("msf64_"))]
assert len(names)==126, len(names)
p=root/"tables/implemented.tsv"
data=p.read_bytes()
assert b"\r" not in data, "CR found in implemented.tsv"
assert data.endswith(b"\n")
existing=set(l.split("\t")[0] for l in data.decode("utf-8").splitlines() if l and not l.startswith("#"))
assert not (existing & set(names)), existing & set(names)
append="".join("%s\t2\n" % n for n in names).encode("utf-8")
with open(p,"ab") as f: f.write(append)
new=p.read_bytes()
assert b"\r" not in new
lines=new.decode("utf-8").splitlines()
rows=[l for l in lines if l and not l.startswith("#")]
print("implemented.tsv rows now:", len(rows)-1, "appended:", len(names))
print("tail:", rows[-3:])
