#!/usr/bin/env bash
R=/c/Users/logan/source/repos/Muse-Softfloat
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd "$R/scratch/verifier-w3str" || exit 9
echo "=== fuzz from-dec: lines with te mode and >20 sig digits:"
"$R/.venv/Scripts/python.exe" - <<'EOF'
import re
n = tot = 0
ex = []
for ln in open("fuzz/vw-fuzz-from-dec.vec"):
    if ln.startswith("#"):
        continue
    tot += 1
    m = re.match(r"msf\d+_from_decimal (\w+) IN=(\S+)", ln)
    rm, s = m.group(1), m.group(2)
    if rm != "te":
        continue
    t = s.lstrip("+-")
    if t[:4].lower() in ("inf", "nan", "sna"):
        continue
    import re as R
    mm = R.match(r"(\d*)\.?(\d*)[eE]?([+-]?\d*)$", t)
    if not mm:
        continue
    digs = (mm.group(1) + mm.group(2)).lstrip("0")
    if len(digs) > 20:
        n += 1
        if len(ex) < 5:
            ex.append((s, digs))
print("te+%d>20sig: %d/%d" % (21, n, tot))
for s, d in ex:
    print(" ", s, len(d))
EOF
