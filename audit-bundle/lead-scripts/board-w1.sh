#!/usr/bin/env bash
# Wave 1 board replay: sampled committed f32/f64 vectors through the RP2040
# harness, whole-run hash host == board. Run from muse-softfloat/.
set -u
cd "$(dirname "$0")/../../muse-softfloat" || exit 9
source board/common.sh
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:/c/Program Files/CMake/bin:$PATH"
take_lock "Wave 1 board replay (sampled f32/f64 vectors)"
SAMPLE="$BOARD_BUILD/board-w1.vec"
$PY ../scratch/lead/board_w1_sample.py "$SAMPLE" || board_fail "sample build"
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off \
    src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c \
    tests/runner.c tests/sha256.c -o "$BOARD_BUILD/msf_runner.exe" \
    > "$BOARD_BUILD/host-build-w1.log" 2>&1 || board_fail "host runner build"
"$BOARD_BUILD/msf_runner.exe" verify "$SAMPLE" > "$BOARD_BUILD/host-verify-w1.log" 2>&1 || board_fail "host verify"
"$BOARD_BUILD/msf_runner.exe" hash "$SAMPLE" > "$BOARD_BUILD/host-hash-w1.log" 2>&1 || board_fail "host hash"
EXPECT_SHA=$(grep '^whole-run-sha256' "$BOARD_BUILD/host-hash-w1.log" | awk '{print $2}')
echo "host: $(grep -E '^(total|VERDICT)' "$BOARD_BUILD/host-verify-w1.log") sha256=$EXPECT_SHA"
build_fw fw
flash_uf2 "$BOARD_BUILD/fw/msf_board_harness.uf2"
$PY board/host_replay.py "$SAMPLE" --expect-sha256 "$EXPECT_SHA" \
    > "$BOARD_BUILD/replay-w1.log" 2>&1 || { cat "$BOARD_BUILD/replay-w1.log"; board_fail "board replay"; }
cat "$BOARD_BUILD/replay-w1.log"
sha256sum "$BOARD_BUILD/fw/msf_board_harness.uf2" "$BOARD_BUILD/fw/msf_board_harness.elf"
echo "wave1 board replay: PASS"
