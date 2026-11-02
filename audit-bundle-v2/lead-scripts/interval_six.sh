#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/../../muse-softfloat" || exit 9
export PATH="/c/Program Files/Git/cmd:/c/Program Files/Git/mingw64/bin:/c/Program Files/Git/usr/bin:/usr/bin:$PATH"
export TMPDIR="$PWD/../scratch/lead/tmp" TMP="$(cygpath -w "$PWD/../scratch/lead/tmp")" TEMP="$TMP"
mkdir -p "$TMPDIR"
export MSF_PYTHON="$PWD/../.venv/Scripts/python.exe"
SERIALS="E66440A2CB6F5C2B 5303284740C0AC1C 5303284740E09A9C 5303284718E6579C 5303284738B5859C 50543165208E249C"
SUM="$PWD/../scratch/lead/interval_six_summary.txt"
: > "$SUM"
fail=0
for s in $SERIALS; do
    log="$PWD/../scratch/lead/interval_six_$s.log"
    echo "=== $s ==="
    MSF_BOARD_SERIAL="$s" bash board/interval_run.sh > "$log" 2>&1
    rc=$?
    line=$(grep -E "BOARD_SHA256|interval board run:|BOARD: FAIL" "$log" | tail -n 3 | tr '\n' ' ')
    echo "$s rc=$rc $line" | tee -a "$SUM"
    [ $rc -eq 0 ] || fail=1
done
echo "SWEEP_DONE fail=$fail"
cat "$SUM"
exit $fail
