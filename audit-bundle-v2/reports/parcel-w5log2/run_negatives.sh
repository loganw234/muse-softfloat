#!/usr/bin/env bash
# Negative controls for parcel-w5log2 (design Sec. 7). Each
# plant must be REFUSED. Never run in a quoted build.
set -u
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
cd "$ROOT/worktrees/w5-log2"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export TMPDIR="$ROOT/scratch/parcel-w5log2/tmp"
PY="$ROOT/.venv/Scripts/python.exe"
B=build/explog
NC=$B/nc
mkdir -p "$NC" "$TMPDIR"
ulimit -v 4194304 2>/dev/null || true
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c"
CFLAGS="-std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off"
VECS="tests/vectors/explog-f16.vec tests/vectors/explog-f32.vec tests/vectors/explog-f64.vec"
FAIL=0
expect_refused() {
    if "$2" verify $VECS > "$NC/$1.verify.log" 2>&1; then
        echo "NC-$1: NOT REFUSED (runner passed a planted defect)"; FAIL=1
    else
        n=$(grep -c '^FAIL' "$NC/$1.verify.log" || true)
        nl=$(grep '^FAIL' "$NC/$1.verify.log" | grep -c 'log2' || true)
        echo "NC-$1: refused as required (runner FAIL lines: $n, log lines: $nl)"
        grep '^FAIL' "$NC/$1.verify.log" | head -3
    fi
}
build_runner() {
    local out=$1; shift
    gcc $CFLAGS "$@" -DMSF_BUILD_ID="\"nc\"" $SRCLIST tests/runner.c tests/sha256.c -o "$out" 2> "$out.build.log" \
        || { echo "build failed for $out"; cat "$out.build.log"; exit 1; }
}
SRCLIST="$SRC"
cp -r include "$NC/include"

# NC-EKa: Ek tampered 100 bits (EK_NARROW widens interval):
# baseline wc log2 decides all at stage 1 (*/0/0); the
# tampered build must migrate to stage 2/3 or mismatch.
gcc -std=c11 -O3 -Wall -Wextra -Werror -ffp-contract=off \
    -DMSF_EXPLOG_TEST_COUNTERS -DMSF_EXPLOG_EK_NARROW=100 \
    $SRC tests/explog_exhaustive.c -lmpfr -lgmp \
    -o "$NC/harness-eknarrow.exe" 2> "$NC/harness-eknarrow.build.log" \
    || { echo "NC-EKa build failed"; cat "$NC/harness-eknarrow.build.log"; exit 1; }
WC2=../../scratch/oracles/core-math-3b2163bb87c222c7db17a721425fbef31e98fd94/src/binary64/log2/log2.wc
"$NC/harness-eknarrow.exe" wc log2 "$WC2" > "$NC/NCEKa.wc.log" 2>&1
hits=$(grep 'counters:' "$NC/NCEKa.wc.log" | sed 's/.*stage hits //; s/ final.*//')
s2=$(echo "$hits" | cut -d/ -f2); s3=$(echo "$hits" | cut -d/ -f3)
mm=$(grep -o 'mismatches=[0-9]*' "$NC/NCEKa.wc.log" | cut -d= -f2)
if [ "${s2:-0}" -gt 0 ] || [ "${s3:-0}" -gt 0 ] || [ "${mm:-0}" -gt 0 ]; then
    echo "NC-EKa-ek-tamper-replay: refused as required (stage hits $hits mismatches=$mm vs baseline */0/0)"
else
    echo "NC-EKa-ek-tamper-replay: NOT REFUSED (stage hits $hits)"; FAIL=1
fi

# NC-EKb: hand-narrowed EK_LOG refused by re-derivation
"$PY" tools/gen_explog_tables.py "$NC/regen.h" > "$NC/regen.log" 2>&1
sed 's/{ 146, 242, 370 }/{ 46, 142, 270 }/' src/msf_explog_tables.h > "$NC/narrowed.h"
if grep -q '46, 142, 270' "$NC/narrowed.h" && ! cmp -s "$NC/narrowed.h" "$NC/regen.h"; then
    echo "NC-EKb-ek-regen: refused as required (hand-narrowed EK_LOG differs from generator proof)"
else
    echo "NC-EKb-ek-regen: NOT REFUSED"; FAIL=1
fi

# NC-TABLE: one hex digit of the 2/ln2 top limb flipped
rm -rf "$NC/srcT"; cp -r src "$NC/srcT"
"$PY" - "$NC/srcT/msf_explog_tables.h" <<'PYEOF'
import sys
p = sys.argv[1]
t = open(p).read()
assert "0xb8aa3b29u" in t
t = t.replace("0xb8aa3b29u", "0xb8aa3b2bu", 1)
open(p, "w", newline="\n").write(t)
print("flipped 2/ln2 limb digit in copy")
PYEOF
SRCLIST=$(echo "$SRC" | sed "s|src/|$NC/srcT/|g")
build_runner "$NC/runner-flip.exe"
expect_refused NC-TABLE "$NC/runner-flip.exe"
SRCLIST="$SRC"

# NC-DIVSTICKY: Wint masked to top 53 bits (sticky deleted)
rm -rf "$NC/srcS"; cp -r src "$NC/srcS"
"$PY" - "$NC/srcS/msf_math.c" <<'PYEOF'
import sys
p = sys.argv[1]
t = open(p).read()
a = "    top = log_top_index(wint, LOG_WLIMB);"
b = """    { /* PLANT: drop sticky below top 53 bits of w */
        int32_t tt_ = log_top_index(wint, LOG_WLIMB);
        if (tt_ > 52) {
            int32_t drop_ = tt_ - 52, li_;
            for (li_ = 0; li_ < (drop_ >> 5); li_++) { wint[li_] = 0u; }
            wint[drop_ >> 5] &= 0xffffffffu << (drop_ & 31);
        }
    }
    top = log_top_index(wint, LOG_WLIMB);"""
assert t.count(a) == 1, t.count(a)
t = t.replace(a, b)
open(p, "w", newline="\n").write(t)
print("planted sticky drop in copy")
PYEOF
SRCLIST=$(echo "$SRC" | sed "s|src/|$NC/srcS/|g")
build_runner "$NC/runner-sticky.exe"
expect_refused NC-DIVSTICKY "$NC/runner-sticky.exe"
gcc -std=c11 -O3 -Wall -Wextra -Werror -ffp-contract=off \
    -DMSF_EXPLOG_TEST_COUNTERS $SRCLIST tests/explog_exhaustive.c \
    -lmpfr -lgmp -o "$NC/harness-sticky.exe" 2> "$NC/harness-sticky.build.log" \
    || { echo "sticky harness build failed"; cat "$NC/harness-sticky.build.log"; exit 1; }
"$NC/harness-sticky.exe" one 2 3 7fe0000000000000 > "$NC/sticky-one.log" 2>&1
if grep -q BAD "$NC/sticky-one.log"; then
    echo "NC-DIVSTICKY named cell f64 log2p1(2^1022): BAD as required"
    cat "$NC/sticky-one.log"
else
    echo "NC-DIVSTICKY named cell: NOT REFUSED"; FAIL=1; cat "$NC/sticky-one.log"
fi
SRCLIST="$SRC"

# NC-RECENTRE: recentring compare flipped
rm -rf "$NC/srcR"; cp -r src "$NC/srcR"
"$PY" - "$NC/srcR/msf_math.c" <<'PYEOF'
import sys
p = sys.argv[1]
t = open(p).read()
a = "if (log_big_sq_ge_pow2(wint, (int)(top / 32 + 1), 2 * top + 1)) {"
b = "if (!log_big_sq_ge_pow2(wint, (int)(top / 32 + 1), 2 * top + 1)) { /* PLANT flipped */"
assert t.count(a) == 1, t.count(a)
t = t.replace(a, b)
open(p, "w", newline="\n").write(t)
print("flipped recentring compare in copy")
PYEOF
SRCLIST=$(echo "$SRC" | sed "s|src/|$NC/srcR/|g")
build_runner "$NC/runner-recentre.exe"
expect_refused NC-RECENTRE "$NC/runner-recentre.exe"
SRCLIST="$SRC"

# NC-POLEFLAG: divideByZero stripped on pole deliveries
rm -rf "$NC/srcP"; cp -r src "$NC/srcP"
"$PY" - "$NC/srcP/msf_math.c" <<'PYEOF'
import sys
p = sys.argv[1]
t = open(p).read()
a = "*flags |= MSF_FLAG_DIVISION_BY_ZERO;"
assert t.count(a) == 2, t.count(a)
t = t.replace(a, a + " *flags &= ~MSF_FLAG_DIVISION_BY_ZERO; /* PLANT strip */")
open(p, "w", newline="\n").write(t)
print("planted pole flag strip in copy")
PYEOF
SRCLIST=$(echo "$SRC" | sed "s|src/|$NC/srcP/|g")
build_runner "$NC/runner-pole.exe"
expect_refused NC-POLEFLAG "$NC/runner-pole.exe"
SRCLIST="$SRC"

# NC-1ULP: corrupt one hardest log2 expectation by 1 ulp
build_runner "$NC/runner-good.exe"
"$PY" - tests/vectors/explog-f64.vec "$NC/corrupt.vec" <<'PYEOF'
import sys
lines = open(sys.argv[1]).read().splitlines()
out = []
done = False
for ln in lines:
    if (not done and ln.startswith("msf64_log2 ")
            and ln.endswith("mpfr-explog:hardest")):
        t = ln.split()
        i = t.index("->")
        t[i+1] = "%x" % (int(t[i+1], 16) ^ 1)
        ln = " ".join(t)
        done = True
    out.append(ln)
assert done
open(sys.argv[2], "w", newline="\n").write("\n".join(out) + "\n")
print("flipped low bit of one hardest log2 expectation")
PYEOF
if "$NC/runner-good.exe" verify "$NC/corrupt.vec" > "$NC/NC1ULP.verify.log" 2>&1; then
    echo "NC-1ULP-hardest: NOT REFUSED"; FAIL=1
else
    echo "NC-1ULP-hardest: refused as required"
    grep '^FAIL' "$NC/NC1ULP.verify.log" | head -3
fi
if "$NC/runner-good.exe" verify $VECS > "$NC/good.verify.log" 2>&1; then
    echo "NC-sanity: good build passes committed explog vectors"
    grep -E '^(file|total|VERDICT)' "$NC/good.verify.log" | tail -4
else
    echo "NC-sanity: GOOD BUILD FAILED committed vectors"; FAIL=1
    tail -5 "$NC/good.verify.log"
fi
[ "$FAIL" -eq 0 ] && echo "NEGATIVE CONTROLS: ALL REFUSED" || echo "NEGATIVE CONTROLS: FAIL"
exit "$FAIL"
