#!/usr/bin/env bash
# Negative controls NC1-NC5 for parcel-w5exp2. Each plant must
# be REFUSED (runner VERDICT: FAIL / nonzero). Never run in a
# build whose results are quoted.
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w5-exp2
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
PY=../../.venv/Scripts/python.exe
B=build/explog
NC=$B/nc
mkdir -p "$NC"
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c"
CFLAGS="-std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off"
VECS="tests/vectors/explog-f16.vec tests/vectors/explog-f32.vec tests/vectors/explog-f64.vec"
FAIL=0
expect_refused() { # $1 name, $2 exe
    if "$2" verify $VECS > "$NC/$1.verify.log" 2>&1; then
        echo "NC-$1: NOT REFUSED (runner passed a planted defect)"; FAIL=1
    else
        n=$(grep -c '^FAIL' "$NC/$1.verify.log" || true)
        echo "NC-$1: refused as required (runner FAIL lines: $n)"
        grep '^FAIL' "$NC/$1.verify.log" | head -3
    fi
}
build_runner() { # $1 out, $2.. extra flags, sources via SRCLIST env
    local out=$1; shift
    gcc $CFLAGS "$@" -DMSF_BUILD_ID="\"nc\"" $SRCLIST tests/runner.c tests/sha256.c -o "$out" 2> "$out.build.log" \
        || { echo "build failed for $out"; cat "$out.build.log"; exit 1; }
}
SRCLIST="$SRC"

# NC1a (replay form): Ek exponents tampered 100 bits off the
# generator integers (interval widened). Bits stay correct
# (the interval still brackets), so the catch is behavioral:
# baseline wc replay decides everything at stage 1
# (hits N/0/0); the tampered build must show stage-2/3 hits.
gcc -std=c11 -O3 -Wall -Wextra -Werror -ffp-contract=off \
    -DMSF_EXPLOG_TEST_COUNTERS -DMSF_EXPLOG_EK_NARROW=100 \
    $SRC tests/explog_exhaustive.c -lmpfr -lgmp \
    -o "$NC/harness-eknarrow.exe" 2> "$NC/harness-eknarrow.build.log" \
    || { echo "NC1a build failed"; cat "$NC/harness-eknarrow.build.log"; exit 1; }
WC2=../../scratch/oracles/core-math-3b2163bb87c222c7db17a721425fbef31e98fd94/src/binary64/exp2/exp2.wc
"$NC/harness-eknarrow.exe" wc exp2 "$WC2" > "$NC/NC1a.wc.log" 2>&1
hits=$(grep 'counters:' "$NC/NC1a.wc.log" | sed 's/.*stage hits //; s/ final.*//')
s2=$(echo "$hits" | cut -d/ -f2); s3=$(echo "$hits" | cut -d/ -f3)
if [ "${s2:-0}" -gt 0 ] || [ "${s3:-0}" -gt 0 ]; then
    echo "NC1a-ek-tamper-replay: refused as required (stage hits $hits vs baseline */0/0)"
else
    echo "NC1a-ek-tamper-replay: NOT REFUSED (stage hits $hits)"; FAIL=1
fi

# NC1b: generator re-derivation refuses a hand-narrowed header
$PY tools/gen_explog_tables.py "$NC/regen.h" > "$NC/regen.log" 2>&1
sed 's/{ 147, 243, 371 }/{ 47, 143, 271 }/' src/msf_explog_tables.h > "$NC/narrowed.h"
if grep -q '47, 143, 271' "$NC/narrowed.h" && ! cmp -s "$NC/narrowed.h" "$NC/regen.h"; then
    echo "NC1b-ek-regen: refused as required (hand-narrowed EK_EXP differs from generator proof)"
else
    echo "NC1b-ek-regen: NOT REFUSED"; FAIL=1
fi

# NC2: constant-table digit flip (one hex digit of the ln2 top limb)
rm -rf "$NC/src2"; cp -r src "$NC/src2"
$PY - "$NC/src2/msf_explog_tables.h" <<'PYEOF'
import sys
p = sys.argv[1]
t = open(p).read()
assert "0xb17217f7u" in t
t = t.replace("0xb17217f7u", "0xb17217f9u", 1)
open(p, "w", newline="\n").write(t)
print("flipped ln2 limb digit in copy")
PYEOF
cp -r include "$NC/include"
SRCLIST=$(echo "$SRC" | sed "s|src/|$NC/src2/|g")
build_runner "$NC/runner-flip.exe"
expect_refused NC2-table-flip "$NC/runner-flip.exe"
SRCLIST="$SRC"

# NC2b: truncated-table-precision plant in a copied tree:
# keep only the top limb of every table-derived value
# (table error up to 2^-32 relative at every stage). The
# subtler 2- and 3-limb drops were measured NOT to bite
# this vector set (their error sits below the hardest
# committed input's boundary distance), so the watched
# control uses the deterministic top-limb form; NC2 above
# is the subtle single-digit flip.
rm -rf "$NC/src2b"; cp -r src "$NC/src2b"
$PY - "$NC/src2b/msf_math.c" <<'PYEOF'
import sys
p = sys.argv[1]
t = open(p).read()
a = """    out->e = en->e;
#ifdef MSF_EXPLOG_DROP_LIMB
    out->m[0] = 0u;
    out->m[1] = 0u;
#endif"""
b = """    out->e = en->e;
    { int j_; /* PLANT: top-limb-only table precision */
      for (j_ = 0; j_ + 1 < n; j_++) { out->m[j_] = 0u; } }"""
assert t.count(a) == 1, t.count(a)
t = t.replace(a, b)
open(p, "w", newline="\n").write(t)
print("planted 3-limb drop in copy")
PYEOF
SRCLIST=$(echo "$SRC" | sed "s|src/|$NC/src2b/|g")
build_runner "$NC/runner-droplimb.exe"
expect_refused NC2b-drop-limb "$NC/runner-droplimb.exe"
SRCLIST="$SRC"

# NC3: cut thresholds off by one (exp2 zero cut and exp2m1 saturation)
rm -rf "$NC/src3"; cp -r src "$NC/src3"
$PY - "$NC/src3/msf_math.c" <<'PYEOF'
import sys
p = sys.argv[1]
t = open(p).read()
a = "if (explog_cmp_int(&d, e_tie) < 0) {"
b = "if (explog_cmp_int(&d, e_tie) <= 0) {"
assert t.count(a) == 1
t = t.replace(a, b)
c = "if (explog_cmp_int(&d, -(fp->precision + 1)) < 0) {"
d = "if (explog_cmp_int(&d, -(fp->precision + 2)) < 0) {"
assert t.count(c) == 1
t = t.replace(c, d)
open(p, "w", newline="\n").write(t)
print("shifted both cut thresholds in copy")
PYEOF
SRCLIST=$(echo "$SRC" | sed "s|src/|$NC/src3/|g")
build_runner "$NC/runner-cut.exe"
expect_refused NC3-cut-off-by-one "$NC/runner-cut.exe"
SRCLIST="$SRC"

# NC4: tie-branch flag strip (inexact cleared on the exact-integer
# pow2 pack path, which carries the emin-p tie)
rm -rf "$NC/src4"; cp -r src "$NC/src4"
$PY - "$NC/src4/msf_math.c" <<'PYEOF'
import sys
p = sys.argv[1]
t = open(p).read()
a = """    uint32_t big[1];
    big[0] = 1u;
    return trig_pack_big(fp, sign, big, 1, n, 0, rm, flags);"""
b = """    uint32_t big[1];
    uint64_t r_;
    big[0] = 1u;
    r_ = trig_pack_big(fp, sign, big, 1, n, 0, rm, flags);
    *flags &= ~MSF_FLAG_INEXACT; /* PLANT: flag strip */
    return r_;"""
assert t.count(a) == 1
t = t.replace(a, b)
open(p, "w", newline="\n").write(t)
print("planted flag strip in copy")
PYEOF
SRCLIST=$(echo "$SRC" | sed "s|src/|$NC/src4/|g")
build_runner "$NC/runner-flagstrip.exe"
expect_refused NC4-flag-strip "$NC/runner-flagstrip.exe"
SRCLIST="$SRC"

# NC5: 1-ulp corruption of a hardest expected value in the vectors
build_runner "$NC/runner-good.exe"
$PY - tests/vectors/explog-f64.vec "$NC/corrupt.vec" <<'PYEOF'
import sys
lines = open(sys.argv[1]).read().splitlines()
out = []
done = False
for ln in lines:
    if not done and ln.endswith("mpfr-explog:hardest"):
        t = ln.split()
        i = t.index("->")
        t[i+1] = "%x" % (int(t[i+1], 16) ^ 1)
        ln = " ".join(t)
        done = True
    out.append(ln)
assert done
open(sys.argv[2], "w", newline="\n").write("\n".join(out) + "\n")
print("flipped low bit of one hardest expectation")
PYEOF
if "$NC/runner-good.exe" verify "$NC/corrupt.vec" > "$NC/NC5.verify.log" 2>&1; then
    echo "NC5-1ulp-hardest: NOT REFUSED"; FAIL=1
else
    echo "NC5-1ulp-hardest: refused as required"
    grep '^FAIL' "$NC/NC5.verify.log" | head -3
fi
# and the good build must PASS the real vectors (control sanity)
if "$NC/runner-good.exe" verify $VECS > "$NC/good.verify.log" 2>&1; then
    echo "NC-sanity: good build passes committed explog vectors"
    grep -E '^(file|total|VERDICT)' "$NC/good.verify.log"
else
    echo "NC-sanity: GOOD BUILD FAILED committed vectors"; FAIL=1
    tail -5 "$NC/good.verify.log"
fi
[ "$FAIL" -eq 0 ] && echo "NEGATIVE CONTROLS: ALL REFUSED" || echo "NEGATIVE CONTROLS: FAIL"
exit "$FAIL"
