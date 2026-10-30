#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# run_demo.sh - one entry point for the reproducible workload demo.
#
#   bash demo/run_demo.sh host [--offline]
#       fetch (or use the seeded cache) -> regenerate the IAS15
#       extract and the Fork-B-patched KissFFT tree -> IAS15 host
#       identity (native and soft-interposed builds vs
#       demo/expected-ias15.txt) -> KissFFT host proof (12 hashes
#       vs demo/expected-kissfft.txt) -> interval host run (IW1
#       hash vs demo/expected-interval.txt) -> summary table.
#
#   bash demo/run_demo.sh board [--offline]
#       the host stages, then - only if they all pass and a full
#       preflight finds the SDK, ARM toolchain, cmake, ninja,
#       picotool, pyserial python, and the ledger layout - drives
#       the existing lead board scripts (board/ias15_run.sh,
#       board/kissfft_run.sh, board/interval_run.sh) with the
#       demo cache wired in.  Any missing item refuses the board
#       stage by name before a lock is taken or anything flashes.
#
# Everything fetched or generated from third-party source stays in
# the gitignored demo/cache/.  See demo/README.md.
set -u
cd "$(dirname "$0")/.." || exit 9

MODE=""
OFFLINE=""
for arg in "$@"; do
    case "$arg" in
        host|board) MODE="$arg" ;;
        --offline) OFFLINE="--offline" ;;
        *) echo "usage: bash demo/run_demo.sh host|board [--offline]"; exit 2 ;;
    esac
done
[ -n "$MODE" ] || { echo "usage: bash demo/run_demo.sh host|board [--offline]"; exit 2; }

CACHE=demo/cache
B=$CACHE/build
EX=$CACHE/ias15-extract
KFTREE=$CACHE/kissfft-tree
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c src/msf_aug.c"
mkdir -p "$B/tmp"
export TMPDIR=$PWD/$B/tmp
export TMP="$(cygpath -w "$TMPDIR" 2>/dev/null || echo "$TMPDIR")"
export TEMP="$TMP"

R_IAS15="NOT RUN"
R_KISSFFT="NOT RUN"
R_INTERVAL="NOT RUN"
R_BOARD=""

echo "== muse-softfloat workload demo: $MODE ${OFFLINE:-(network allowed)} =="
echo "date: $(date '+%Y-%m-%d %H:%M:%S %z')"

# ---- prerequisites ------------------------------------------------
missing=""
note_missing() { missing="$missing
  - $1"; }

PY="${MSF_PYTHON:-}"
if [ -z "$PY" ]; then
    if command -v python3 >/dev/null 2>&1; then PY=python3;
    elif command -v python >/dev/null 2>&1; then PY=python; fi
fi
if [ -z "$PY" ]; then
    note_missing "Python (python3 or python on PATH, or MSF_PYTHON set)"
elif ! "$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' 2>/dev/null; then
    note_missing "usable Python >= 3.8 at $PY"
    PY=""
fi

CC="${MSF_HOST_CC:-gcc}"
cc_ok=0
if command -v "$CC" >/dev/null 2>&1; then
    case "$($CC -dumpmachine 2>/dev/null)" in
        x86_64-*) cc_ok=1 ;;
    esac
fi
if [ "$cc_ok" = 0 ] && [ -x /c/msys64/mingw64/bin/gcc ]; then
    # MSYS2 layout aid: a bare `gcc` here is often the 32-bit one.
    CC=/c/msys64/mingw64/bin/gcc
    case "$($CC -dumpmachine 2>/dev/null)" in
        x86_64-*) cc_ok=1 ;;
    esac
fi
# A compiler named by path needs its own directory first on PATH
# (measured on MSYS2: otherwise cc1 picks up another toolchain's
# DLLs and exits silently).
case "$CC" in
    */*) PATH="$(dirname "$CC"):$PATH"; export PATH ;;
esac
if [ "$cc_ok" = 0 ]; then
    note_missing "x86-64 host C compiler (gcc with -dumpmachine x86_64-*; set MSF_HOST_CC)"
else
    cat > "$B/probe.c" <<'EOF'
#include <stdio.h>
int main(void) { printf("FLT_EVAL_METHOD=%d\n", __FLT_EVAL_METHOD__); return __FLT_EVAL_METHOD__ == 0 ? 0 : 1; }
EOF
    if $CC -std=c11 "$B/probe.c" -o "$B/probe.exe" > "$B/probe.log" 2>&1 \
       && "$B/probe.exe" > "$B/probe.out" 2>&1; then
        echo "host compiler: $CC $($CC -dumpmachine) $($CC -dumpversion) $(cat "$B/probe.out")"
    else
        note_missing "host compiler with FLT_EVAL_METHOD==0 (probe failed; see $B/probe.log)"
    fi
    # The soft IAS15 build interposes via soft-float libcalls; the
    # flags must at least compile (runtime vacuity is refused by
    # the SHIMOPS count, not here).
    cat > "$B/probe_soft.c" <<'EOF'
double probe_add(double a, double b) { return a + b; }
EOF
    $CC -std=c99 -O2 -msoft-float -mno-sse2 -ffp-contract=off \
        -c "$B/probe_soft.c" -o "$B/probe_soft.o" > "$B/probe-soft.log" 2>&1 \
        || note_missing "host compiler support for -msoft-float -mno-sse2 (see $B/probe-soft.log)"
fi

if [ -n "$missing" ]; then
    echo "demo: REFUSED - missing prerequisites:$missing"
    echo "demo: nothing was built or downloaded."
    exit 2
fi
echo "python: $PY ($($PY --version 2>&1))"

# ---- fetch + regenerate -------------------------------------------
fetch_ok=1
echo "== fetch (pinned REBOUND + KissFFT only) =="
MSF_PYTHON="$PY" bash demo/fetch.sh $OFFLINE || fetch_ok=0

extract_ok=0
kissfft_tree_ok=0
if [ "$fetch_ok" = 1 ]; then
    echo "== regenerate IAS15 extract =="
    if "$PY" demo/make_ias15_extract.py "$CACHE/src/rebound" "$EX" \
            > "$B/make-ias15-extract.log" 2>&1; then
        cat "$B/make-ias15-extract.log"
        extract_ok=1
    else
        cat "$B/make-ias15-extract.log"
        echo "IAS15 extract generation FAILED"
    fi
    echo "== regenerate KissFFT Fork B tree =="
    if "$PY" demo/make_kissfft_tree.py "$CACHE/src/kissfft" "$KFTREE" \
            > "$B/make-kissfft-tree.log" 2>&1; then
        cat "$B/make-kissfft-tree.log"
        kissfft_tree_ok=1
    else
        cat "$B/make-kissfft-tree.log"
        echo "KissFFT tree generation FAILED"
    fi
fi

# ---- IAS15 host identity ------------------------------------------
if [ "$extract_ok" = 1 ]; then
    echo "== IAS15 host identity (2000 steps, native + soft) =="
    ias_ok=1
    NF="-std=c99 -O3 -march=x86-64 -ffp-contract=off -fno-fast-math -fno-unsafe-math-optimizations -fexcess-precision=standard -Wall -Wextra -Wno-unused-parameter"
    if $CC $NF -I$EX -Iboard -I. \
            $EX/integrator_ias15_min.c $EX/gravity_basic_min.c \
            $EX/sim_min.c $EX/ias15x.c board/ias15_hash.c \
            tests/sha256.c demo/ias15_host_main.c \
            -o "$B/ias15_native.exe" -lm > "$B/ias15-native-build.log" 2>&1 \
       && "$B/ias15_native.exe" 2000 "$B/hashes_native.txt" \
       && "$PY" demo/compare_ias15.py demo/expected-ias15.txt \
            "$B/hashes_native.txt" > "$B/ias15-native-compare.log" 2>&1; then
        echo "native : $(grep '^steps_compared' "$B/ias15-native-compare.log")"
    else
        echo "native build/run/compare FAILED (logs in $B/ias15-native-*)"
        tail -5 "$B/ias15-native-build.log" "$B/ias15-native-compare.log" 2>/dev/null
        ias_ok=0
    fi
    SF="-std=c99 -O3 -msoft-float -mno-sse2 -ffp-contract=off -fno-fast-math -fno-unsafe-math-optimizations -fno-builtin-fabs -fno-builtin-copysign -fno-builtin-sqrt -Wall -Wno-unused-parameter"
    if [ "$ias_ok" = 1 ] \
       && $CC $SF -DDEMO_IAS15_SOFT -I$EX -Iboard -I. -Iinclude -Isrc \
            $EX/integrator_ias15_min.c $EX/gravity_basic_min.c \
            $EX/sim_min.c $EX/ias15x.c board/ias15_hash.c \
            tests/sha256.c demo/ias15_host_main.c demo/ias15_host_shim.c \
            $SRC -o "$B/ias15_soft.exe" -lm > "$B/ias15-soft-build.log" 2>&1 \
       && "$B/ias15_soft.exe" 2000 "$B/hashes_soft.txt"; then
        shimops=$(grep '^# SHIMOPS' "$B/hashes_soft.txt" || true)
        ops=$(echo "$shimops" | sed -n 's/.*total=\([0-9]*\).*/\1/p')
        traps=$(echo "$shimops" | sed -n 's/.*traps=\([0-9]*\).*/\1/p')
        if [ -z "$ops" ] || [ "$ops" = 0 ] || [ "$traps" != 0 ]; then
            echo "soft   : REFUSED - interposition vacuous or trapped ($shimops)"
            ias_ok=0
        elif "$PY" demo/compare_ias15.py demo/expected-ias15.txt \
                "$B/hashes_soft.txt" > "$B/ias15-soft-compare.log" 2>&1; then
            echo "soft   : $(grep '^steps_compared' "$B/ias15-soft-compare.log") ($shimops)"
        else
            cat "$B/ias15-soft-compare.log"
            ias_ok=0
        fi
    elif [ "$ias_ok" = 1 ]; then
        echo "soft build/run FAILED (see $B/ias15-soft-build.log)"
        tail -5 "$B/ias15-soft-build.log"
        ias_ok=0
    fi
    [ "$ias_ok" = 1 ] && R_IAS15="PASS" || R_IAS15="FAIL"
else
    R_IAS15="FAIL (no extract)"
fi

# ---- KissFFT host proof -------------------------------------------
if [ "$kissfft_tree_ok" = 1 ]; then
    echo "== KissFFT Fork B host proof (12 configurations) =="
    KFF="-std=c11 -O2 -Wall -Wextra -ffp-contract=off -fno-fast-math -fno-builtin-sinpi -fno-builtin-cospi -fno-builtin-floor -fno-builtin-sqrt -Dkiss_fft_scalar=double"
    if $CC $KFF -I. -Icompat -I$KFTREE \
            demo/kissfft_host_main.c $KFTREE/kiss_fft.c $KFTREE/kiss_fftr.c \
            $SRC compat/msf_aeabi.c demo/kissfft_host_shim.c tests/sha256.c \
            -Wl,--wrap=sinpi,--wrap=cospi,--wrap=floor -lm \
            -o "$B/kissfft_host.exe" > "$B/kissfft-build.log" 2>&1 \
       && "$B/kissfft_host.exe" > "$B/kissfft-out.txt" 2>&1; then
        grep '^KF ' "$B/kissfft-out.txt" > "$B/kf-got.txt"
        grep '^KF ' demo/expected-kissfft.txt > "$B/kf-expect.txt"
        if grep -q '^HOST-PROOF anchors_fails=0' "$B/kissfft-out.txt" \
           && ! grep -q ' FAIL$' "$B/kissfft-out.txt" \
           && diff "$B/kf-expect.txt" "$B/kf-got.txt" > "$B/kf-diff.log" 2>&1; then
            echo "12/12 KF rows identical; anchors PASS"
            R_KISSFFT="PASS"
        else
            cat "$B/kissfft-out.txt" "$B/kf-diff.log"
            R_KISSFFT="FAIL"
        fi
    else
        echo "KissFFT build/run FAILED (see $B/kissfft-build.log, $B/kissfft-out.txt)"
        tail -5 "$B/kissfft-build.log"
        R_KISSFFT="FAIL"
    fi
else
    R_KISSFFT="FAIL (no patched tree)"
fi

# ---- interval host run ----------------------------------------------
echo "== interval host run (frozen catalogue, IW1 hash) =="
if $CC -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off \
        $SRC tests/sha256.c board/interval_workload.c board/interval_host.c \
        -o "$B/interval_host.exe" > "$B/interval-build.log" 2>&1 \
   && "$B/interval_host.exe" tests/interval_catalogue.tsv \
        > "$B/interval-out.txt" 2>&1; then
    want_rows=$(sed -n 's/^rows=\([0-9]*\)$/\1/p' demo/expected-interval.txt)
    want_hash=$(sed -n 's/^HOST_SHA256 \([0-9a-f]*\)$/\1/p' demo/expected-interval.txt)
    got_rows=$(sed -n 's/^SUMMARY rows=\([0-9]*\) .*/\1/p' "$B/interval-out.txt")
    got_hash=$(sed -n 's/^HOST_SHA256 \([0-9a-f]*\)$/\1/p' "$B/interval-out.txt")
    if [ -n "$want_rows" ] && [ "$got_rows" = "$want_rows" ] \
       && [ -n "$want_hash" ] && [ "$got_hash" = "$want_hash" ]; then
        echo "rows=$got_rows IW1 sha256 identical"
        R_INTERVAL="PASS"
    else
        echo "want rows=$want_rows hash=$want_hash"
        echo "got  rows=$got_rows hash=$got_hash"
        R_INTERVAL="FAIL"
    fi
else
    echo "interval build/run FAILED (see $B/interval-build.log, $B/interval-out.txt)"
    tail -5 "$B/interval-build.log"
    R_INTERVAL="FAIL"
fi

# ---- summary --------------------------------------------------------
echo "== summary (host) =="
printf '  %-10s %s\n' "IAS15" "$R_IAS15"
printf '  %-10s %s\n' "KissFFT" "$R_KISSFFT"
printf '  %-10s %s\n' "interval" "$R_INTERVAL"
host_ok=1
[ "$R_IAS15" = "PASS" ] && [ "$R_KISSFFT" = "PASS" ] && [ "$R_INTERVAL" = "PASS" ] || host_ok=0
if [ "$MODE" = "host" ]; then
    [ "$host_ok" = 1 ] && echo "demo host: PASS" || echo "demo host: FAIL"
    [ "$host_ok" = 1 ]
    exit $?
fi

# ---- board stage ------------------------------------------------------
echo "== board stage (lead-run scripts; preflight first) =="
if [ "$host_ok" != 1 ]; then
    echo "board stage REFUSED - host stages did not all PASS; the board is not driven on a red host proof."
    echo "demo board: FAIL (refused)"
    exit 1
fi

bmissing=""
bnote() { bmissing="$bmissing
  - $1"; }

# Ledger (board-lock home).  ias15/kissfft scripts accept ../ledger
# or ../../ledger; interval_run.sh needs ../ledger (main-checkout
# layout).  Resolve both before anything runs.
LEDGER_ANY=""
LEDGER_MAIN=""
if [ -d ../ledger ]; then
    LEDGER_MAIN="$(cd ../ledger && pwd)"
    LEDGER_ANY="$LEDGER_MAIN"
elif [ -d ../../ledger ]; then
    LEDGER_ANY="$(cd ../../ledger && pwd)"
fi
if [ -z "$LEDGER_ANY" ]; then
    bnote "ledger directory (../ledger or ../../ledger) - the board lock home; board runs need the workspace layout, see demo/README.md"
elif [ -f "$LEDGER_ANY/board.lock" ]; then
    bnote "free board (lock held: $(cat "$LEDGER_ANY/board.lock" | tr '\n' ' '))"
fi

SDK_PATH="${PICO_SDK_PATH:-/c/Users/logan/pico/pico-sdk}"
[ -f "$SDK_PATH/external/pico_sdk_import.cmake" ] \
    || bnote "Pico SDK at PICO_SDK_PATH (no external/pico_sdk_import.cmake under $SDK_PATH)"

ARM_CC="${MSF_ARM_CC:-arm-none-eabi-gcc}"
command -v "$ARM_CC" >/dev/null 2>&1 \
    || bnote "ARM toolchain ($ARM_CC on PATH, or set MSF_ARM_CC)"
command -v cmake >/dev/null 2>&1 \
    || bnote "cmake on PATH"

# picotool: same default as board/common.sh, else PATH.
PICOTOOL="${MSF_PICOTOOL:-/c/Users/logan/pico/picotool/picotool.exe}"
if [ ! -x "$PICOTOOL" ]; then
    if command -v picotool >/dev/null 2>&1; then
        PICOTOOL="$(command -v picotool)"
    else
        bnote "picotool (MSF_PICOTOOL, the board/common.sh default path, or PATH)"
    fi
fi

# ninja: board/common.sh defaults to ../.venv; cover the worktree
# layout (../../.venv) by exporting MSF_NINJA when found there.
NINJA_FOUND="${MSF_NINJA:-}"
if [ -z "$NINJA_FOUND" ]; then
    for cand in ../.venv/Scripts/ninja.exe ../../.venv/Scripts/ninja.exe; do
        if [ -x "$cand" ]; then NINJA_FOUND="$cand"; break; fi
    done
fi
if [ -z "$NINJA_FOUND" ] && command -v ninja >/dev/null 2>&1; then
    NINJA_FOUND="$(command -v ninja)"
fi
if [ -z "$NINJA_FOUND" ]; then
    bnote "ninja (MSF_NINJA, workspace .venv, or PATH)"
else
    export MSF_NINJA="$(cygpath -w "$NINJA_FOUND" 2>/dev/null | tr '\\' '/' || echo "$NINJA_FOUND")"
fi

"$PY" -c 'import serial' 2>/dev/null \
    || bnote "pyserial in the board python ($PY -c 'import serial' fails; set MSF_PYTHON)"

if [ -n "$bmissing" ]; then
    echo "board stage REFUSED - missing:$bmissing"
    echo "board stage: nothing was flashed and no lock was taken."
    echo "demo board: FAIL (refused)"
    exit 1
fi

echo "preflight OK: ledger=$LEDGER_ANY sdk=$SDK_PATH picotool=$PICOTOOL"
echo "flash target serial: ${MSF_BOARD_SERIAL:-untargeted - set MSF_BOARD_SERIAL when several boards share the bus}"
export MSF_PYTHON="$PY"
export MSF_PICOTOOL="$PICOTOOL"
export PICO_SDK_PATH="$SDK_PATH"
export IAS15_EXTRACT_DIR="$PWD/$EX"
export IAS15_REF_HASHES="$PWD/demo/expected-ias15.txt"
export IAS15_COMPARE="$PWD/demo/compare_ias15.py"
export MSF_KISSFFT_DIR="$PWD/$KFTREE"
export KISSFFT_EXPECT="$PWD/demo/expected-kissfft.txt"

board_ok=1
echo "== board: IAS15 (board/ias15_run.sh) =="
bash board/ias15_run.sh || board_ok=0
if [ "$board_ok" = 1 ]; then
    echo "== board: KissFFT (board/kissfft_run.sh) =="
    bash board/kissfft_run.sh || board_ok=0
fi
if [ "$board_ok" = 1 ]; then
    if [ -n "$LEDGER_MAIN" ]; then
        echo "== board: interval (board/interval_run.sh) =="
        bash board/interval_run.sh || board_ok=0
    else
        echo "board: interval SKIPPED - board/interval_run.sh requires ../ledger (main-checkout layout); run the board stage from the main checkout for that leg. Nothing extra was flashed for it."
    fi
fi
if [ "$board_ok" = 1 ]; then
    echo "demo board: PASS (host green; board scripts green as run above)"
    exit 0
fi
echo "demo board: FAIL (a board script failed; see its output above)"
exit 1
