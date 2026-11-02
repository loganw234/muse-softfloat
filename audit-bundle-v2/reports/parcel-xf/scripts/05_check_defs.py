import csv, pathlib, re
root = pathlib.Path(r"C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w2-xf")
def read_tsv(p):
    lines=[l for l in open(p, encoding="utf-8") if not l.startswith("#")]
    return list(csv.DictReader(lines, delimiter="\t"))
cov=read_tsv(root/"docs/COVERAGE.tsv")
w2=[r["name"] for r in cov if r["wave"]=="2" and (r["name"].startswith("msf32_") or r["name"].startswith("msf64_"))]
src32=(root/"src/msf32.c").read_text(encoding="utf-8")
src64=(root/"src/msf64.c").read_text(encoding="utf-8")
def count_def(name, src):
    # count wrapper lines naming it (macro lines or plain definitions)
    n=0
    for l in src.splitlines():
        if name in l and ("DEF_" in l or l.startswith(("msf32_t ","msf64_t ","int "))):
            n+=1
    # comparisons built by token pasting: handle separately
    return n
bad=[]
for name in w2:
    src = src32 if name.startswith("msf32_") else src64
    n = count_def(name, src)
    if "_compare_" in name:
        # pasted: check predicate+named macro line exists
        pred = name.split("_compare_",1)[1][:-len("_f16")]
        n = 1 if (f"DEF_CMP_F16({pred}," in src) else 0
    if n!=1:
        bad.append((name,n))
print("checked", len(w2), "bad:", bad)
# ensure no w2 name accidentally in other file definitions
for name in w2:
    other = src64 if name.startswith("msf32_") else src32
    if name in other:
        print("CROSS-FILE mention:", name)
print("done")
