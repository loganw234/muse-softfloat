#!/usr/bin/env bash
# 13-strref.sh - test the copy's str reference te-vs-ta on committed
# beyond-h inputs; re-run the beyond-h search per format with counts.
set -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
V="$SCRATCH"
export TMPDIR="$V/tmp" TMP="$V/tmp" TEMP="$V/tmp"
"$MSF_PYTHON" - "$COPY/tests" <<'PYEOF'
import sys
sys.path.insert(0,sys.argv[1])
import gen_vectors_str as g
for s,fmt in [("7.41098468761869816265e-324","f64"),
              ("1.22010707855224609375e-4","f16"),
              ("2.50000000000000000005","f64")]:
    te=g.from_decimal_ref(s,"te",fmt)[:2]
    ta=g.from_decimal_ref(s,"ta",fmt)[:2]
    print(s,fmt,"te=",tuple(hex(x) for x in te),"ta=",tuple(hex(x) for x in ta),
          "DIFFER" if te!=ta else "same")
print("RMS:",g.RMS)
print("ref dec_round_inc has ta:", "TIES_TO_AWAY" in open(sys.argv[1]+"/gen_vectors_str.py").read().split("def dec_round_inc_ref")[1][:400]
      if "def dec_round_inc_ref" in open(sys.argv[1]+"/gen_vectors_str.py").read() else "n/a")
PYEOF
