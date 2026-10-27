#!/usr/bin/env bash
# tools/run.sh - the one front door (SF-0 Section 5.1). Run from the
# repository root under Git Bash on this host:
#
#   tools/run.sh smoke|standard|board|bench
#
#   smoke    minutes: drift check, host+target builds, symbol/type
#            scans, unit tests, committed vector sets, the P0 negative
#            controls (each watched to fail before it is trusted)
#   standard the merge gate: smoke + exhaustive binary16 sweeps +
#            the seeded pack64 sweep (oracle-priced sets join as the
#            waves claim operations)
#   board    lead-run under <ledger>/board.lock: delegates to
#            board/run_board.sh (same sampled vectors on the RP2040)
#   bench    never a correctness verdict: board/run_bench.sh
#
# Every budget prints its inventory BEFORE results: compilers, oracle
# and semantics choices, what ran by category, vectors by provenance,
# skips by name. Exit status only counts with that inventory.
set -u
cd "$(dirname "$0")/.." || exit 9
BUDGET="${1:-}"
case "$BUDGET" in smoke|standard|board|bench) ;; *) echo "usage: tools/run.sh smoke|standard|board|bench"; exit 2;; esac

export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
BUILD=build/$BUDGET
mkdir -p "$BUILD/tmp"
export TMPDIR=$PWD/$BUILD/tmp
export TMP="$(cygpath -w "$TMPDIR" 2>/dev/null || echo "$TMPDIR")"
export TEMP="$TMP"
PY="${MSF_PYTHON:-}"
[ -z "$PY" ] && [ -x ../.venv/Scripts/python.exe ] && PY=../.venv/Scripts/python.exe
[ -z "$PY" ] && PY=python
HOST_CC="${MSF_HOST_CC:-gcc}"
ARM_CC="${MSF_ARM_CC:-arm-none-eabi-gcc}"
CFLAGS="-std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off"
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c"
START=$(date +%s)
fail() { echo "RUN.SH: FAIL - $1"; exit 1; }

echo "== budget: $BUDGET =="
echo "date: $(date '+%Y-%m-%d %H:%M:%S %z')"
echo "python: $PY ($($PY --version 2>&1))"
echo "semantics: IEEE 754-2019; tininess after rounding (SF-0 2.5); H=20"

check_host_compiler() {
    # SF-0 4.2 / 5.3: only the pinned x86-64 path, FLT_EVAL_METHOD==0.
    local cc="$1" dm
    dm=$($cc -dumpmachine 2>/dev/null)
    case "$dm" in x86_64-*) ;; *) echo "compiler REFUSED: $cc dumpmachine=$dm (need x86_64-*)"; return 1;; esac
    cat > "$BUILD/probe.c" <<'EOF'
#include <stdio.h>
int main(void){ printf("FLT_EVAL_METHOD=%d\n", __FLT_EVAL_METHOD__); return __FLT_EVAL_METHOD__ == 0 ? 0 : 1; }
EOF
    $cc -std=c11 "$BUILD/probe.c" -o "$BUILD/probe.exe" 2>"$BUILD/probe.log" || { echo "compiler REFUSED: probe build failed"; return 1; }
    "$BUILD/probe.exe" > "$BUILD/probe.out" 2>&1 || { echo "compiler REFUSED: $(cat "$BUILD/probe.out")"; return 1; }
    echo "host compiler: $cc dumpmachine=$dm $($cc -dumpversion) $(cat "$BUILD/probe.out")"
    return 0
}

drift_check() {
    rm -rf "$BUILD/gen-check"
    $PY tools/gen_tables.py "$BUILD/gen-check" > "$BUILD/gen.log" 2>&1 || fail "generator failed (see $BUILD/gen.log)"
    local f
    for f in include/muse_softfloat.h src/msf_formats.h tests/msf_dispatch.h docs/COVERAGE.tsv; do
        cmp -s "$f" "$BUILD/gen-check/$f" || fail "GENERATED FILE DRIFT: $f differs from tables/ - regenerate with tools/gen_tables.py"
    done
    echo "drift check: 4 generated files byte-identical to tables/"
}

build_host() { # $1 = output exe, $2.. = extra flags
    local out="$1"; shift
    local id="host-$($HOST_CC -dumpmachine)-gcc$($HOST_CC -dumpversion)"
    $HOST_CC $CFLAGS "$@" -DMSF_BUILD_ID="\"$id\"" $SRC tests/runner.c tests/sha256.c -o "$out" > "$BUILD/build.log" 2>&1 \
        || { cat "$BUILD/build.log"; fail "host build failed"; }
    echo "built $out ($id)"
}

symbol_scan() {
    if ! command -v $ARM_CC >/dev/null 2>&1; then
        echo "symbol scan: SKIP-BY-NAME $ARM_CC not found (target gate not run)"
        return 0
    fi
    echo "target compiler: $($ARM_CC --version | head -1)"
    mkdir -p "$BUILD/arm"
    local f
    for f in $SRC; do
        $ARM_CC -std=c11 -Os -Wall -Wextra -Werror -mcpu=cortex-m0plus -mthumb -ffreestanding -c "$f" -o "$BUILD/arm/$(basename "$f" .c).o" >> "$BUILD/build.log" 2>&1 \
            || { cat "$BUILD/build.log"; fail "target build failed: $f"; }
    done
    ${ARM_CC%gcc}nm -u $BUILD/arm/*.o > "$BUILD/arm-undefined.txt" 2>/dev/null
    sort -u "$BUILD/arm-undefined.txt" | grep -E ' [A-Za-z_]' > "$BUILD/arm-undefined-sorted.txt" || true
    echo "target undefined symbols ($(wc -l < "$BUILD/arm-undefined-sorted.txt")):"
    cat "$BUILD/arm-undefined-sorted.txt"
    if grep -Eq '__aeabi_[fd]|__add[sd]f3|__sub[sd]f3|__mul[sd]f3|__div[sd]f3|__truncdfsf2|__extendsfdf2|__float|__fix|__unord|malloc|free|printf' "$BUILD/arm-undefined-sorted.txt"; then
        fail "SYMBOL SCAN: refused helper symbol in target objects (SF-0 5.3)"
    fi
    echo "symbol scan: clean"
}

type_scan() {
    if grep -rnwE 'float|double' src include > "$BUILD/type-scan.txt" 2>&1; then
        cat "$BUILD/type-scan.txt"
        fail "TYPE SCAN: hardware arithmetic type named in src/ or include/ (SF-0 3.2/5.3)"
    fi
    echo "type scan: clean (no float/double words in src/ include/)"
}

write_manifest() { # $1 = manifest file; rest = files
    local m="$1"; shift
    # one process, one stream: per-file >> appends were measured to
    # land at offset 0 on this host's sandboxed filesystem (2026-10-26)
    sha256sum "$@" > "$m"
    echo "manifest: $m ($(wc -l < "$m") entries)"
}

write_expect_counts() { # $1 = out file; rest = vector files
    local out="$1"; shift
    awk '!/^#/ && NF>0 {print $NF}' "$@" | sort | uniq -c | awk '{print $2, $1}' > "$out"
    echo "expect-counts: $out ($(wc -l < "$out") provenance tags)"
}

# ---- negative controls (SF-0 5.2, the P0-applicable set) ----
# Each control must be REFUSED (runner/budget nonzero or refusal line).
CTRL_FAIL=0
control_ok() { echo "control $1: refused as required"; }
control_bad() { echo "control $1: NOT REFUSED"; CTRL_FAIL=1; }

controls() {
    local R="$BUILD/msf_runner.exe" C="$BUILD/controls"
    mkdir -p "$C"
    # 1. corrupted expected-result bit (first is_signaling case flipped)
    awk 'BEGIN{d=0} /^msf16_is_signaling/ && !d {for(i=1;i<=NF;i++) if($i=="->") $(i+1)=($(i+1)=="1"?"0":"1"); d=1} {print}' \
        tests/vectors/encodings-f16.vec > "$C/corrupt.vec"
    "$R" verify "$C/corrupt.vec" > "$C/corrupt.log" 2>&1
    [ $? -ne 0 ] && grep -q 'VERDICT: FAIL' "$C/corrupt.log" && control_ok corrupted-expected-bit || control_bad corrupted-expected-bit
    # 2. wrong NaN polarity expectation: swap signaling<->quiet class ids
    awk 'BEGIN{d=0} /^msf32_class/ && !d && $NF=="exact-py:directed-encodings" {for(i=1;i<=NF;i++) if($i=="->" && ($(i+1)=="0"||$(i+1)=="1")) {$(i+1)=($(i+1)=="0"?"1":"0"); d=1}} {print}' \
        tests/vectors/encodings-f32.vec > "$C/nanpol.vec"
    "$R" verify "$C/nanpol.vec" > "$C/nanpol.log" 2>&1
    [ $? -ne 0 ] && control_ok wrong-nan-expectation || control_bad wrong-nan-expectation
    # 3. wrong rounding mode (all pack64 te<->tz)
    awk '{if($1=="internal.pack64"){if($2=="te")$2="tz"; else if($2=="tz")$2="te"} print}' \
        tests/vectors/pack64.vec > "$C/wrongrm.vec"
    "$R" verify "$C/wrongrm.vec" > "$C/wrongrm.log" 2>&1
    [ $? -ne 0 ] && control_ok wrong-rounding-mode || control_bad wrong-rounding-mode
    # 4. wrong flag bit (first nonzero pack64 flags zeroed)
    awk 'BEGIN{d=0} $1=="internal.pack64" && !d && $(NF-1)!="00" {$(NF-1)="00"; d=1} {print}' \
        tests/vectors/pack64.vec > "$C/wrongflag.vec"
    "$R" verify "$C/wrongflag.vec" > "$C/wrongflag.log" 2>&1
    [ $? -ne 0 ] && control_ok wrong-flag-bit || control_bad wrong-flag-bit
    # 5. stale/tampered manifest replay
    sed '1s/^./0/' "$BUILD/manifest.txt" > "$C/bad-manifest.txt"
    "$R" verify --manifest "$C/bad-manifest.txt" tests/vectors/encodings-f16.vec > "$C/manifest.log" 2>&1
    [ $? -ne 0 ] && grep -q 'MANIFEST MISMATCH' "$C/manifest.log" && control_ok stale-manifest || control_bad stale-manifest
    # 6. skipped-vector count mismatch
    awk '{if(NR==1) $2=$2+1; print}' "$BUILD/expect.txt" > "$C/bad-expect.txt"
    "$R" verify --expect-counts "$C/bad-expect.txt" tests/vectors/encodings-f16.vec > "$C/count.log" 2>&1
    [ $? -ne 0 ] && grep -q 'COUNT MISMATCH' "$C/count.log" && control_ok count-mismatch || control_bad count-mismatch
    # 7. wrong-tininess-polarity build at the smallest-normal boundary
    build_host "$C/msf_runner_tininess_before.exe" -DMSF_TININESS_AFTER_ROUNDING=0
    "$C/msf_runner_tininess_before.exe" verify tests/vectors/pack64.vec > "$C/tininess.log" 2>&1
    [ $? -ne 0 ] && grep -q '^FAIL' "$C/tininess.log" && control_ok wrong-tininess-polarity || control_bad wrong-tininess-polarity
    # 8. refused x87 host compiler path
    if [ -x /c/msys64/mingw32/bin/gcc ]; then
        if check_host_compiler /c/msys64/mingw32/bin/gcc > "$C/x87.log" 2>&1; then control_bad x87-compiler-refusal; else control_ok x87-compiler-refusal; fi
    else
        echo "control x87-compiler-refusal: SKIP-BY-NAME /c/msys64/mingw32 absent on this host"
    fi
    # 9. planned-only replay must not verdict PASS (verifier-p0 note i;
    # op must stay planned - msf16_from_decimal until Wave 3 lands)
    printf 'msf16_from_decimal te 1.0 -> 3c00 00 control:planned\n' > "$C/planned.vec"
    "$R" verify "$C/planned.vec" > "$C/planned.log" 2>&1
    [ $? -ne 0 ] && grep -q 'SKIP.*not implemented' "$C/planned.log" && grep -q 'VERDICT: FAIL' "$C/planned.log" && control_ok planned-only-verdict || control_bad planned-only-verdict
    [ "$CTRL_FAIL" -eq 0 ] || fail "a negative control was not refused"
    echo "negative controls: all refused"
}

VECS="tests/vectors/encodings-f16.vec tests/vectors/encodings-f32.vec tests/vectors/encodings-f64.vec tests/vectors/copysign.vec tests/vectors/pack64.vec tests/vectors/pack32.vec tests/vectors/pack16.vec tests/vectors/arith-f32.vec tests/vectors/fma-sqrt-f32.vec tests/vectors/conv-int-f32.vec tests/vectors/toint-f32.vec tests/vectors/rint-misc-f32.vec tests/vectors/compare-f32.vec tests/vectors/arith-f64.vec tests/vectors/conv-f64.vec tests/vectors/misc-f64.vec tests/vectors/compare-f64.vec tests/vectors/nan-f64.vec"

smoke() {
    check_host_compiler "$HOST_CC" || fail "host compiler refused"
    drift_check
    build_host "$BUILD/msf_runner.exe"
    "$BUILD/msf_runner.exe" unit > "$BUILD/unit.log" 2>&1 || { cat "$BUILD/unit.log"; fail "unit tests"; }
    grep -E 'unit (sha256|flags|versions|wide)|unit:' "$BUILD/unit.log"
    write_manifest "$BUILD/manifest.txt" $SRC tests/runner.c tests/sha256.c include/muse_softfloat.h src/msf_formats.h tests/msf_dispatch.h $VECS
    write_expect_counts "$BUILD/expect.txt" $VECS
    "$BUILD/msf_runner.exe" verify --manifest "$BUILD/manifest.txt" --expect-counts "$BUILD/expect.txt" $VECS > "$BUILD/verify.log" 2>&1 \
        || { tail -30 "$BUILD/verify.log"; fail "vector verify"; }
    grep -E '^(file|prov|total|VERDICT|manifest)' "$BUILD/verify.log"
    type_scan
    symbol_scan
    controls
}

standard() {
    smoke
    $PY tests/gen_vectors.py f16-exhaustive "$BUILD/f16-exhaustive.vec" > "$BUILD/gen-f16.log" 2>&1 || fail "f16 exhaustive generation"
    $PY tests/gen_vectors.py pack-sweep "$BUILD/pack-sweep.vec" 200000 > "$BUILD/gen-sweep.log" 2>&1 || fail "pack sweep generation"
    grep -h . "$BUILD/gen-f16.log" "$BUILD/gen-sweep.log" | grep -E 'wrote|dropped'
    "$BUILD/msf_runner.exe" verify "$BUILD/f16-exhaustive.vec" "$BUILD/pack-sweep.vec" > "$BUILD/verify-standard.log" 2>&1 \
        || { tail -30 "$BUILD/verify-standard.log"; fail "standard vector verify"; }
    grep -E '^(file|prov|total|VERDICT)' "$BUILD/verify-standard.log"
}

case "$BUDGET" in
    smoke) smoke ;;
    standard) standard ;;
    board)
        [ -x board/run_board.sh ] || fail "board budget: board/run_board.sh missing"
        bash board/run_board.sh || fail "board budget (see output above)" ;;
    bench)
        [ -x board/run_bench.sh ] || fail "bench budget: board/run_bench.sh missing"
        bash board/run_bench.sh || fail "bench budget (see output above)" ;;
esac
echo "budget $BUDGET: PASS in $(( $(date +%s) - START ))s (logs in $BUILD/)"
exit 0
