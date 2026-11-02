#!/usr/bin/env bash
# 11-relabdiff.sh - every committed ta-relabel line must equal its te mate
# in result+flags; list all divergences.
set -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
V="$SCRATCH"
export TMPDIR="$V/tmp" TMP="$V/tmp" TEMP="$V/tmp"
"$MSF_PYTHON" - "$COPY/tests/vectors" <<'PYEOF'
import glob,sys
d=sys.argv[1]
nrel=0
divs=[]
for f in sorted(glob.glob(d+"/trig-*.vec")):
    te={}
    talines=[]
    for l in open(f,errors="replace"):
        if l.startswith("#") or not l.strip(): continue
        p=l.split()
        if len(p)>6 and p[6].endswith("-ta-relabel"): talines.append(p)
        elif len(p)>5 and p[1]=="te": te[(p[0],p[2])]=(p[4],p[5])
    nrel+=len(talines)
    for p in talines:
        mate=te.get((p[0],p[2]))
        if mate!=(p[4],p[5]): divs.append((f.split("/")[-1]," ".join(p),mate))
print("relabel lines:",nrel,"divergences:",len(divs))
for x in divs[:10]: print(x)
PYEOF
