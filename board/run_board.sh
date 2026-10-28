#!/usr/bin/env bash
# run_board.sh - P0 board budget (SF-0 Sections 5.1, 6 item 7).
# Lead-run under <ledger>/board.lock: builds the harness and hello
# firmware, flashes each in turn, replays the board-smoke vector set
# over USB CDC comparing results and the whole-run hash against the
# host, then checks the interposition hello's results on silicon.
set -u
cd "$(dirname "$0")/.." || exit 9
source board/common.sh

echo "== board budget =="
echo "date: $(date '+%Y-%m-%d %H:%M:%S %z')"
echo "picotool: $("$PICOTOOL" version 2>/dev/null | head -1)"
echo "pico-sdk: $PICO_SDK_PATH"
echo "board target: serial=${MSF_BOARD_SERIAL:-untargeted} port=${MSF_BOARD_PORT:-auto}"
take_lock "P0 board budget: harness replay + interposition hello"

# host side: runner + board-smoke vectors + expected whole-run hash
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off \
    src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c \
    tests/runner.c tests/sha256.c -o "$BOARD_BUILD/msf_runner.exe" \
    > "$BOARD_BUILD/host-build.log" 2>&1 || board_fail "host runner build"
$PY tests/gen_vectors.py board-smoke "$BOARD_BUILD/board-smoke.vec" > "$BOARD_BUILD/gen.log" 2>&1 || board_fail "board-smoke generation"
"$BOARD_BUILD/msf_runner.exe" verify "$BOARD_BUILD/board-smoke.vec" > "$BOARD_BUILD/host-verify.log" 2>&1 || board_fail "host verify of board-smoke set"
"$BOARD_BUILD/msf_runner.exe" hash "$BOARD_BUILD/board-smoke.vec" > "$BOARD_BUILD/host-hash.log" 2>&1 || board_fail "host hash"
EXPECT_SHA=$(grep '^whole-run-sha256' "$BOARD_BUILD/host-hash.log" | awk '{print $2}')
[ -n "$EXPECT_SHA" ] || board_fail "no host whole-run hash"
echo "host: $(grep -E '^(total|VERDICT)' "$BOARD_BUILD/host-verify.log") sha256=$EXPECT_SHA"

"$PICOTOOL" info -a > "$BOARD_BUILD/picotool-info.log" 2>&1 || true
grep -E 'chip|revision|rom' "$BOARD_BUILD/picotool-info.log" || true

build_fw fw
flash_uf2 "$BOARD_BUILD/fw/msf_board_harness.uf2"
PORT_ARG=()
if [ -n "${MSF_BOARD_PORT:-}" ]; then
    PORT_ARG=(--port "$MSF_BOARD_PORT")
    echo "replay port: $MSF_BOARD_PORT (MSF_BOARD_PORT)"
fi
$PY board/host_replay.py ${PORT_ARG[@]+"${PORT_ARG[@]}"} "$BOARD_BUILD/board-smoke.vec" --expect-sha256 "$EXPECT_SHA" \
    > "$BOARD_BUILD/replay.log" 2>&1 || { cat "$BOARD_BUILD/replay.log"; board_fail "board replay"; }
cat "$BOARD_BUILD/replay.log"

flash_uf2 "$BOARD_BUILD/fw/msf_hello.uf2"
$PY board/read_until.py HELLO-RESULT > "$BOARD_BUILD/hello.log" 2>&1 || { cat "$BOARD_BUILD/hello.log"; board_fail "hello read"; }
cat "$BOARD_BUILD/hello.log"
grep -q 'HELLO-RESULT PASS' "$BOARD_BUILD/hello.log" || board_fail "interposition hello did not PASS"

echo "artifacts (name them in the record):"
sha256sum "$BOARD_BUILD/fw/msf_board_harness.uf2" "$BOARD_BUILD/fw/msf_board_harness.elf" \
          "$BOARD_BUILD/fw/msf_hello.uf2" "$BOARD_BUILD/fw/msf_hello.elf"
echo "board budget: PASS"
