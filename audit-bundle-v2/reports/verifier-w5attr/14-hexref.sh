#!/usr/bin/env bash
# 14-hexref.sh - probe from_hex_ref te-vs-ta on the generator's own
# f16 candidates; count committed from-hex-ties lines.
set -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
V="$SCRATCH"
export TMPDIR="$V/tmp" TMP="$V/tmp" TEMP="$V/tmp"
echo "== committed from-hex-ties lines =="
grep -c "from-hex-ties" "$COPY/tests/vectors/from-hex-str.vec" || true
grep -c "from-hex-ties" "$COPY/tests/vectors/"*.vec || true
"$MSF_PYTHON" - "$COPY/tests" <<'PYEOF'
import sys
sys.path.insert(0,sys.argv[1])
import gen_vectors_str as g
p=11
emin=g.fmt_params("f16")["emin"]
print("f16 emin",emin)
n=0
for e in (0,-5,7,emin+2):
    for q in ((1<<(p-1)),(1<<(p-1))+2,(1<<p)-2):
        odd=2*q+1
        s=f"0x{odd:x}p{e-p}"
        te=g.from_hex_ref(s,"te","f16")[:2]
        ta=g.from_hex_ref(s,"ta","f16")[:2]
        print(s,"te=",[hex(x) for x in te],"ta=",[hex(x) for x in ta],
              "DIFFER" if te!=ta else "same")
        n+=te!=ta
print("differ count:",n)
PYEOF
