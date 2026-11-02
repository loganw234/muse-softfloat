import re, pathlib, csv
wt=pathlib.Path("worktrees/w2-f16")
hdr=(wt/"include/muse_softfloat.h").read_text()
# coverage names
lines=[l for l in open(wt/"docs/COVERAGE.tsv") if not l.startswith("#")]
rdr=csv.DictReader(lines, delimiter="\t")
names=[r["name"] for r in rdr if r["wave"]=="2" and r["name"].startswith("msf16_")]
print(len(names))
for n in names:
    m=re.search(re.escape(n)+r"\([^;]*\);", hdr)
    print(m.group(0) if m else ("MISSING "+n))
