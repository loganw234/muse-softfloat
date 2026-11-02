import pathlib, csv, re
root=pathlib.Path("worktrees/w1-f64")
lines=[l for l in open(root/"docs/COVERAGE.tsv") if not l.startswith("#")]
rows=list(csv.DictReader(lines, delimiter="\t"))
names=[r["name"] for r in rows if r["wave"]=="1" and r["name"].startswith("msf64_")]
hdr=open(root/"include/muse_softfloat.h").read().splitlines()
# extract decl lines containing name(
for n in names:
    for line in hdr:
        if n+"(" in line:
            print(line.strip())
            break
    else:
        print("MISSING", n)
print("---dispatch sample---")
d=open(root/"tests/msf_dispatch.h").read().splitlines()
print("\n".join(d[:150]))
print("---gen_tables key parts---")
gt=open(root/"tools/gen_tables.py").read()
print(gt[:12000])
