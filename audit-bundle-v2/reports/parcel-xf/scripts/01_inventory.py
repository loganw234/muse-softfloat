import csv, collections, pathlib
root = pathlib.Path(r"C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w2-xf")
def read_tsv(p):
    lines=[l for l in open(p, encoding="utf-8") if not l.startswith("#")]
    return list(csv.DictReader(lines, delimiter="\t"))
cov=read_tsv(root/"docs/COVERAGE.tsv")
print("cols", list(cov[0].keys()), "total", len(cov))
w2=[r for r in cov if r["wave"]=="2" and (r["name"].startswith("msf32_") or r["name"].startswith("msf64_"))]
print("wave2 count", len(w2))
print(collections.Counter(r["name"][:5] for r in w2))
print(collections.Counter(r["authority"] for r in w2))
print(collections.Counter(r["status"] for r in w2))
print(collections.Counter(r["dest"] for r in w2))
# group by std_name + sources pattern
for r in w2:
    print("\t".join([r["name"], r["std_name"], r["clause"], r["dest"], r["sources"], r["rounding"], r["flags"], r["authority"], r["vectors"], r["comparison"]]))
imp=read_tsv(root/"tables/implemented.tsv")
print("\nimplemented rows", len(imp))
impl={r["name"]:r["wave"] for r in imp}
print("wave2 already in implemented:", [(r["name"],impl[r["name"]]) for r in w2 if r["name"] in impl])
# also wave1 implemented msf32/64 count
print("implemented msf32", sum(1 for n in impl if n.startswith("msf32_")), "msf64", sum(1 for n in impl if n.startswith("msf64_")))
# Check header declarations exist for w2 names
hdr=(root/"include/muse_softfloat.h").read_text(encoding="utf-8")
missing=[r["name"] for r in w2 if r["name"] not in hdr]
print("missing from header:", missing)
dispatch=(root/"tests/msf_dispatch.h").read_text(encoding="utf-8")
print("missing from dispatch:", [r["name"] for r in w2 if r["name"] not in dispatch])
