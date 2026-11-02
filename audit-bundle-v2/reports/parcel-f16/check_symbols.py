import csv, pathlib, subprocess, sys
wt = pathlib.Path("worktrees/w2-f16")
lines = [l for l in open(wt/"docs/COVERAGE.tsv") if not l.startswith("#")]
rows = list(csv.DictReader(lines, delimiter="\t"))
mine = [r["name"] for r in rows if r["wave"]=="2" and r["name"].startswith("msf16_")]
# symbols from nm on the object
nm = subprocess.run(["C:/msys64/mingw64/bin/nm.exe", "--defined-only",
                     "scratch/parcel-f16/msf16.o"], capture_output=True, text=True)
syms = set()
for line in nm.stdout.splitlines():
    parts = line.split()
    if parts: syms.add(parts[-1].lstrip("_"))
missing = [n for n in mine if n not in syms]
print("coverage names:", len(mine))
print("defined msf16_ symbols:", len([s for s in syms if s.startswith("msf16_")]))
print("missing:", missing)
impl_before = set()
for l in open(wt/"tables/implemented.tsv"):
    if l.startswith("#") or l.startswith("name\t"): continue
    impl_before.add(l.split("\t")[0].strip())
extra = sorted(s for s in syms if s.startswith("msf16_") and s not in mine and s not in impl_before)
print("extra new msf16_ symbols (should be none):", extra)
sys.exit(1 if missing or extra else 0)
