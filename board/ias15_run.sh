#!/usr/bin/env bash
# ias15_run.sh - LEAD-RUN board sequence for the IAS15 demo (SF-0
# Sec.9). Parcel agents do not run this: it takes <ledger>/board.lock,
# flashes, and opens the COM port. Sequence: build (existing CMake
# tree if present) -> flash msf_aeabi_selftest, require AEABI-RESULT
# PASS -> flash msf_ias15, "R 2000 1" capture -> compare against the
# desktop reference with the ias15-port comparator unchanged ->
# "T 2000" step-rate blocks (apparatus measurement, named clock in
# the RATE lines). Artifacts and logs land in build/ias15-board/.
#
# Usage, from the repository root (this worktree until merged):
#   IAS15_EXTRACT_DIR=<workspace>/scratch/ias15/extract \
#   IAS15_REF_HASHES=<workspace>/scratch/ias15/out/hashes_native.txt \
#   IAS15_COMPARE=<workspace>/scratch/ias15/work/compare_hashes.py \
#   bash board/ias15_run.sh
set -u
cd "$(dirname "$0")/.." || exit 9

# board/common.sh assumes the main-repo layout (../ledger); resolve
# the worktree layout (../../ledger) first, then source it with the
# LEDGER_DIR it computes only if that one exists.
if [ -d ../ledger ]; then
    IAS15_LEDGER_DIR="$(cd ../ledger && pwd)"
elif [ -d ../../ledger ]; then
    IAS15_LEDGER_DIR="$(cd ../../ledger && pwd)"
else
    echo "ias15_run: ledger directory not found (../ledger or ../../ledger)"
    exit 9
fi
source board/common.sh
LEDGER_DIR="$IAS15_LEDGER_DIR"  # re-pin after common.sh computed its own
LOCK="$LEDGER_DIR/board.lock"

[ -n "${IAS15_EXTRACT_DIR:-}" ] || { echo "ias15_run: IAS15_EXTRACT_DIR not set"; exit 9; }
[ -f "${IAS15_REF_HASHES:-}" ] || { echo "ias15_run: IAS15_REF_HASHES not a file"; exit 9; }
[ -f "${IAS15_COMPARE:-}" ] || { echo "ias15_run: IAS15_COMPARE not a file"; exit 9; }

OUT=build/ias15-board
mkdir -p "$OUT"
echo "== IAS15 board run =="
echo "date: $(date '+%Y-%m-%d %H:%M:%S %z')"
echo "ledger: $LEDGER_DIR"
echo "extract: $IAS15_EXTRACT_DIR"
sha256sum "$IAS15_EXTRACT_DIR"/*.c "$IAS15_EXTRACT_DIR"/*.h > "$OUT/extract-inputs.sha256"
cat "$OUT/extract-inputs.sha256"
take_lock "IAS15 board run: AEABI selftest + figure-8 hash equality + step-rate blocks"

"$PICOTOOL" info -a > "$OUT/picotool-info.log" 2>&1 || true
grep -E 'chip|revision|rom' "$OUT/picotool-info.log" || true

build_fw ias15fw -DIAS15_EXTRACT_DIR="$IAS15_EXTRACT_DIR"
echo "artifacts (name them in the record):"
sha256sum "$BOARD_BUILD/ias15fw/msf_aeabi_selftest.uf2" \
          "$BOARD_BUILD/ias15fw/msf_aeabi_selftest.elf" \
          "$BOARD_BUILD/ias15fw/msf_ias15.uf2" \
          "$BOARD_BUILD/ias15fw/msf_ias15.elf" | tee "$OUT/artifacts.sha256"

flash_uf2 "$BOARD_BUILD/ias15fw/msf_aeabi_selftest.uf2"
$PY board/ias15_host.py --until AEABI-RESULT \
    > "$OUT/selftest.log" 2>&1 || { cat "$OUT/selftest.log"; board_fail "aeabi selftest capture"; }
cat "$OUT/selftest.log"
grep -q 'AEABI-RESULT PASS' "$OUT/selftest.log" || board_fail "AEABI selftest did not PASS on silicon"

flash_uf2 "$BOARD_BUILD/ias15fw/msf_ias15.uf2"
$PY board/ias15_host.py --cmd "R 2000 1" --hashes "$OUT/hashes_board.txt" \
    > "$OUT/run2000.log" 2>&1 || { tail -20 "$OUT/run2000.log"; board_fail "ias15 R capture"; }
tail -5 "$OUT/run2000.log"
grep -q 'AEABI-LITE PASS' "$OUT/run2000.log" || true   # may race the open; R refuses if unready
grep -q 'nonfinite_hashed_fields=0 ' "$OUT/run2000.log" || board_fail "non-finite hashed fields on board run"
$PY "$IAS15_COMPARE" "$IAS15_REF_HASHES" "$OUT/hashes_board.txt" \
    > "$OUT/compare.log" 2>&1 || { cat "$OUT/compare.log"; board_fail "board hashes differ from desktop reference"; }
cat "$OUT/compare.log"

$PY board/ias15_host.py --cmd "T 2000" \
    > "$OUT/rate2000.log" 2>&1 || { tail -20 "$OUT/rate2000.log"; board_fail "ias15 T capture"; }
grep '^RATE' "$OUT/rate2000.log"

echo "ias15 board run: PASS (selftest PASS, 2001 hash rows equal, RATE lines above)"
