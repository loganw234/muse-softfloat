#!/usr/bin/env bash
# run_example.sh - on-ramp example on silicon (lead-only).
#
# Follows the board pattern (board/run_board.sh): takes
# <ledger>/board.lock through board/common.sh, builds the
# firmware, flashes it, reads the USB CDC output until the
# EXAMPLE-RESULT line, and checks that every line of the
# host expectation (examples/host/expected.txt) appeared
# verbatim - the board must print the same result lines as
# the host. Run from anywhere; the script finds the repo
# root. MSF_BOARD_SERIAL / MSF_BOARD_PORT select the board
# on a multi-board bus, as in board/common.sh.
set -u
cd "$(dirname "$0")/../.." || exit 9
source board/common.sh

echo "== pico example (lead-only, under board lock) =="
echo "date: $(date '+%Y-%m-%d %H:%M:%S %z')"
echo "pico-sdk: $PICO_SDK_PATH"
take_lock "examples: pico on-ramp example"

EX_BUILD=build/example-pico
cmake -S examples/pico -B "$EX_BUILD" -G Ninja \
    -DCMAKE_MAKE_PROGRAM="$NINJA" -DPICO_SDK_PATH="$PICO_SDK_PATH" \
    -DCMAKE_BUILD_TYPE=Release \
    > "$EX_BUILD-cmake.log" 2>&1 \
    || { tail -20 "$EX_BUILD-cmake.log"; board_fail "cmake configure (examples/pico)"; }
cmake --build "$EX_BUILD" > "$EX_BUILD-build.log" 2>&1 \
    || { tail -30 "$EX_BUILD-build.log"; board_fail "firmware build (examples/pico)"; }
echo "built firmware in $EX_BUILD"
sha256sum "$EX_BUILD/msf_example.uf2" "$EX_BUILD/msf_example.elf"

flash_uf2 "$EX_BUILD/msf_example.uf2"
$PY board/read_until.py EXAMPLE-RESULT > "$EX_BUILD/board.log" 2>&1 \
    || { cat "$EX_BUILD/board.log"; board_fail "example read"; }
tr -d '\r' < "$EX_BUILD/board.log" > "$EX_BUILD/board.txt"
cat "$EX_BUILD/board.txt"
grep -q 'EXAMPLE-RESULT PASS' "$EX_BUILD/board.txt" \
    || board_fail "pico example did not PASS on the board"

missing=0
while IFS= read -r line; do
    grep -Fxq -- "$line" "$EX_BUILD/board.txt" || {
        echo "missing board line: $line"
        missing=1
    }
done < examples/host/expected.txt
[ "$missing" -eq 0 ] \
    || board_fail "board output differs from examples/host/expected.txt"

echo "pico example: PASS (board printed every host-expected line)"
