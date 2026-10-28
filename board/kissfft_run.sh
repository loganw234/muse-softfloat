#!/usr/bin/env bash
# kissfft_run.sh - LEAD-RUN board sequence for the KissFFT Fork B
# workload (SF-1 Step 2c). Parcel agents do not run this: it takes
# <ledger>/board.lock, flashes, and opens the COM port. Written and
# compile-checked by parcel-w4kissfft; executed by the lead after
# merge - the board bit-identity run gates any on-silicon sentence.
#
# Sequence: take lock -> build with MSF_KISSFFT_DIR (Fork-B-patched
# scratch tree; the one named change is exact cycle fractions into
# sinpi/cospi - never "unmodified KissFFT") -> flash msf_kissfft
# (serial-targeted) -> capture KF rows -> require bit-identity
# against the host proof hashes. Artifacts in build/kissfft-board/.
#
# Usage, from the repository root:
#   MSF_KISSFFT_DIR=<workspace>/scratch/parcel-w4kissfft/tree \
#   KISSFFT_EXPECT=<workspace>/scratch/parcel-w4kissfft/out/hashes-main.txt \
#   MSF_BOARD_SERIAL=<serial> MSF_BOARD_PORT=<COMx> \
#   bash board/kissfft_run.sh
set -u
cd "$(dirname "$0")/.." || exit 9

if [ -d ../ledger ]; then
    KF_LEDGER_DIR="$(cd ../ledger && pwd)"
elif [ -d ../../ledger ]; then
    KF_LEDGER_DIR="$(cd ../../ledger && pwd)"
else
    echo "kissfft_run: ledger directory not found (../ledger or ../../ledger)"
    exit 9
fi
source board/common.sh
LEDGER_DIR="$KF_LEDGER_DIR"
LOCK="$LEDGER_DIR/board.lock"

[ -n "${MSF_KISSFFT_DIR:-}" ] || { echo "kissfft_run: MSF_KISSFFT_DIR not set"; exit 9; }
[ -f "$MSF_KISSFFT_DIR/kiss_fft.c" ] || { echo "kissfft_run: no kiss_fft.c under MSF_KISSFFT_DIR"; exit 9; }
grep -q 'MSF Fork B' "$MSF_KISSFFT_DIR/kiss_fft.c" \
    || { echo "kissfft_run: tree lacks the Fork B patch marker - refusing"; exit 9; }
[ -f "${KISSFFT_EXPECT:-}" ] || { echo "kissfft_run: KISSFFT_EXPECT not a file"; exit 9; }

OUT=build/kissfft-board
mkdir -p "$OUT"
echo "== KissFFT Fork B board run =="
echo "date: $(date '+%Y-%m-%d %H:%M:%S %z')"
echo "ledger: $LEDGER_DIR"
echo "patched tree: $MSF_KISSFFT_DIR"
sha256sum "$MSF_KISSFFT_DIR"/kiss_fft.c "$MSF_KISSFFT_DIR"/kiss_fftr.c \
          "$MSF_KISSFFT_DIR"/_kiss_fft_guts.h "$MSF_KISSFFT_DIR"/kiss_fft.h \
          "$MSF_KISSFFT_DIR"/kiss_fftr.h | tee "$OUT/tree-inputs.sha256"
take_lock "KissFFT Fork B board run: KF hash bit-identity at N=256/1024/4096"

"$PICOTOOL" info -a > "$OUT/picotool-info.log" 2>&1 || true
grep -E 'chip|revision|rom' "$OUT/picotool-info.log" || true

build_fw kissfftfw -DMSF_KISSFFT_DIR="$MSF_KISSFFT_DIR"
sha256sum "$BOARD_BUILD/kissfftfw/msf_kissfft.uf2" \
          "$BOARD_BUILD/kissfftfw/msf_kissfft.elf" | tee "$OUT/artifacts.sha256"

flash_uf2 "$BOARD_BUILD/kissfftfw/msf_kissfft.uf2"
$PY board/kissfft_host.py --expect "$KISSFFT_EXPECT" --rerun \
    > "$OUT/run.log" 2>&1 || { cat "$OUT/run.log"; board_fail "kissfft KF capture/compare"; }
cat "$OUT/run.log"
grep -q 'kissfft_host: PASS' "$OUT/run.log" || board_fail "board KF rows differ from host proof"

echo "kissfft board run: PASS (all KF rows bit-identical, patched source named above)"
