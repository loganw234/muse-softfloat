#!/usr/bin/env bash
# verifier-w164 (2): independent Berkeley differential driver in verify-f64.
# Usage: v-berk.sh PHASE (A|C|cmp|conv|one FN RM LEVEL TAKE [KEEP])
set -uo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify-f64
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
mkdir -p build/w1v/tmp build/w1v/logs
export TMPDIR=$PWD/build/w1v/tmp
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
export MSF_TESTFLOAT_GEN='C:\Users\logan\source\repos\Muse-Softfloat\scratch\oracles\TestFloat-3e\build\Linux-x86_64-GCC\testfloat_gen.exe'
PY=../../.venv/Scripts/python.exe
RUNNER=build/smoke/msf_runner.exe
PHASE="${1:-A}"

run_case() {
    local fn="$1" rm="$2" level="$3" take="$4" keep="${5:-0}"
    local tag="${fn}-${rm}-l${level}"
    if [ "$take" != "0" ]; then tag="${tag}-t${take}"; fi
    local vec="build/w1v/${tag}.vec"
    local ilog="build/w1v/logs/${tag}.ingest.log"
    local vlog="build/w1v/logs/${tag}.verify.log"
    local t0 t1 rc_i rc_v
    t0=$(date +%s)
    echo "CASE START $tag $(date -Iseconds)"
    if [ "$take" = "0" ]; then
        $PY tests/berkeley_ingest.py --fn "$fn" --rm "$rm" --level "$level" --out "$vec" > "$ilog" 2>&1
    else
        $PY tests/berkeley_ingest.py --fn "$fn" --rm "$rm" --level "$level" --take "$take" --out "$vec" > "$ilog" 2>&1
    fi
    rc_i=$?
    cat "$ilog"
    if [ $rc_i -ne 0 ]; then
        echo "CASE FAIL-INGEST $tag rc=$rc_i"
        return 1
    fi
    "$RUNNER" verify "$vec" > "$vlog" 2>&1
    rc_v=$?
    grep -E '^(file|prov|total|VERDICT)' "$vlog" || true
    grep '^FAIL' "$vlog" | head -8 || true
    grep -c '^SKIP' "$vlog" | sed "s/^/skips: /" || true
    t1=$(date +%s)
    echo "CASE END $tag ingest_rc=$rc_i verify_rc=$rc_v seconds=$((t1-t0))"
    if [ "$keep" != "1" ] && [ $rc_v -eq 0 ]; then
        rm -f "$vec"
    fi
    return $rc_v
}

FAILS=0
case "$PHASE" in
A)
    for fn in f64_add f64_sub f64_mul f64_div f64_sqrt; do
        for rm in te tz tp tn ta; do
            run_case "$fn" "$rm" 1 0 0 || FAILS=$((FAILS+1))
        done
    done
    run_case f64_rem - 1 0 0 || FAILS=$((FAILS+1))
    for rm in te tz tp tn ta; do
        run_case f64_roundToInt "$rm" 1 0 0 || FAILS=$((FAILS+1))
    done
    ;;
conv)
    for rm in te tz tp tn ta; do
        run_case f32_to_f64 "$rm" 1 0 0 || FAILS=$((FAILS+1))
        run_case f64_to_f32 "$rm" 1 0 1 || FAILS=$((FAILS+1))
        for fn in f64_to_i32 f64_to_i64 f64_to_ui32 f64_to_ui64 i32_to_f64 i64_to_f64 ui32_to_f64 ui64_to_f64; do
            run_case "$fn" "$rm" 1 0 0 || FAILS=$((FAILS+1))
        done
    done
    ;;
cmp)
    for fn in f64_eq f64_eq_signaling f64_le f64_le_quiet f64_lt f64_lt_quiet; do
        run_case "$fn" - 1 0 0 || FAILS=$((FAILS+1))
    done
    ;;
C)
    for rm in te tz tp tn ta; do
        run_case f64_mulAdd "$rm" 1 500000 0 || FAILS=$((FAILS+1))
    done
    ;;
one)
    run_case "$2" "$3" "$4" "${5:-0}" "${6:-0}" || FAILS=$((FAILS+1))
    ;;
*)
    echo "bad phase $PHASE"; exit 2;;
esac
echo "PHASE $PHASE DONE fails=$FAILS $(date -Iseconds)"
exit $FAILS
