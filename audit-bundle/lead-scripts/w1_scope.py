import pathlib
cov = pathlib.Path("muse-softfloat/docs/COVERAGE.tsv").read_text(encoding="utf-8").splitlines()
rows = [l.split("\t") for l in cov if l and not l.startswith("#")]
hdr, rows = rows[0], rows[1:]
ix = {k: hdr.index(k) for k in ("name", "std_name", "dest", "sources", "wave", "status")}
w1 = [r for r in rows if r[ix["wave"]] == "1" and r[ix["status"]] != "implemented"]
def owner(r):
    name = r[ix["name"]]
    if name.startswith("msf64_"):
        return "f64"
    if name.startswith("msf32_"):
        return "f32"
    return "??"
from collections import Counter
print("wave1 unimplemented:", len(w1))
print(Counter(owner(r) for r in w1))
for own in ("f32", "f64"):
    fams = Counter(r[ix["std_name"]] for r in w1 if owner(r) == own)
    print("==", own, sum(fams.values()))
    for k in sorted(fams):
        print("  %-38s %d" % (k, fams[k]))
# write name lists for briefs
for own in ("f32", "f64"):
    names = [r[ix["name"]] for r in w1 if owner(r) == own]
    pathlib.Path("scratch/lead/w1-%s-names.txt" % own).write_text("\n".join(names) + "\n")
print("lists written")
