#!/usr/bin/env bash
# run_bench.sh - bench budget (SF-0 Sections 5.1, 6 item 9).
# NEVER a correctness verdict. Builds the bench skeleton under both
# SDK flavours (default pico = ROM-routed baselines, compiler =
# libgcc baselines), runs each on the board, prints placement/clock
# labels and sizes. No performance claim is made in P0.
set -u
cd "$(dirname "$0")/.." || exit 9
source board/common.sh

echo "== bench budget (skeleton; no performance claim) =="
take_lock "P0 bench skeleton"

build_fw bench-pico
build_fw bench-compiler -DMSF_BENCH_FLAVOUR=compiler

for f in bench-pico bench-compiler; do
    echo "--- $f sizes ---"
    arm-none-eabi-size "$BOARD_BUILD/$f/msf_bench.elf" "$BOARD_BUILD/$f/"*.elf 2>/dev/null | head -6
    arm-none-eabi-size "$BOARD_BUILD/$f/CMakeFiles/msf_core.dir/"*.obj 2>/dev/null \
        || find "$BOARD_BUILD/$f" -name 'msf_*.obj' -exec arm-none-eabi-size {} +
done

for f in bench-pico bench-compiler; do
    echo "--- $f on board ---"
    flash_uf2 "$BOARD_BUILD/$f/msf_bench.uf2"
    $PY board/read_until.py BENCH-DONE > "$BOARD_BUILD/$f-out.log" 2>&1 || { cat "$BOARD_BUILD/$f-out.log"; board_fail "bench run $f"; }
    cat "$BOARD_BUILD/$f-out.log"
done
echo "bench budget: done (skeleton numbers above; unquoted in any claim)"
