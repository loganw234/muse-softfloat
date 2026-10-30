#!/usr/bin/env bash
# interval_run.sh - Step 1c board sample (SF-1 Sections 5.2, 9).
# Lead-run under <ledger>/board.lock: builds the host runner and
# msf_interval firmware, flashes the named board only (picotool
# --ser; other boards may share the bus), streams the frozen
# catalogue, and requires the board IW1 SHA-256 to equal the
# host's. Env: MSF_BOARD_SERIAL (default: the genuine board in
# docs/BOARD.md), MSF_INTERVAL_TSV (default: the full catalogue).
set -u
cd "$(dirname "$0")/.." || exit 9
source board/common.sh

SERIAL="${MSF_BOARD_SERIAL:-E66440A2CB6F5C2B}"
TSV="${MSF_INTERVAL_TSV:-tests/interval_catalogue.tsv}"

echo "== interval board run =="
echo "date: $(date '+%Y-%m-%d %H:%M:%S %z')"
echo "picotool: $("$PICOTOOL" version 2>/dev/null | head -1)"
echo "target serial: $SERIAL"
take_lock "Step 1c interval board sample ($TSV, serial $SERIAL)"

export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
"$PY" tests/gen_interval_catalogue.py "$BOARD_BUILD/interval_catalogue.tsv" \
    > "$BOARD_BUILD/interval-gen.log" 2>&1 || board_fail "catalogue generation"
cmp "$BOARD_BUILD/interval_catalogue.tsv" tests/interval_catalogue.tsv \
    || board_fail "catalogue regeneration drift"
# A custom TSV should be a row subset of the frozen catalogue
# (a sampled run); its expected hash is computed from that file.
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off \
    src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c \
    src/msf_roundpack.c src/msf_string.c src/msf_aug.c tests/sha256.c \
    board/interval_workload.c board/interval_host.c \
    -o "$BOARD_BUILD/interval_host.exe" \
    > "$BOARD_BUILD/interval-host-build.log" 2>&1 || board_fail "host runner build"
"$BOARD_BUILD/interval_host.exe" "$TSV" > "$BOARD_BUILD/interval-host.log" 2>&1 \
    || { tail -5 "$BOARD_BUILD/interval-host.log"; board_fail "host interval run"; }
EXPECT_SHA=$(grep '^HOST_SHA256' "$BOARD_BUILD/interval-host.log" | awk '{print $2}')
[ -n "$EXPECT_SHA" ] || board_fail "no host IW1 hash"
echo "host: $(grep '^SUMMARY' "$BOARD_BUILD/interval-host.log")"
echo "host IW1 sha256=$EXPECT_SHA"

build_fw fw
UF2="$BOARD_BUILD/fw/msf_interval.uf2"
ELF="$BOARD_BUILD/fw/msf_interval.elf"
[ -f "$UF2" ] || board_fail "msf_interval.uf2 not built"
echo "flashing $UF2 sha256=$(sha256sum "$UF2" | cut -d' ' -f1) to serial $SERIAL"
if ! "$PICOTOOL" load --ser "$SERIAL" -f -x "$UF2" > "$BOARD_BUILD/interval-flash.log" 2>&1; then
    cat "$BOARD_BUILD/interval-flash.log"
    board_fail "picotool load failed - board may need hands (hold BOOTSEL while plugging in)"
fi
cat "$BOARD_BUILD/interval-flash.log"
sleep 2

$PY board/interval_board_host.py "$TSV" --serial "$SERIAL" \
    --expect-sha256 "$EXPECT_SHA" \
    > "$BOARD_BUILD/interval-board.log" 2>&1 \
    || { cat "$BOARD_BUILD/interval-board.log"; board_fail "board interval run"; }
cat "$BOARD_BUILD/interval-board.log"
grep -q 'board interval: PASS' "$BOARD_BUILD/interval-board.log" \
    || board_fail "board interval run did not PASS"

echo "artifacts (name them in the record):"
sha256sum "$UF2" "$ELF"
echo "interval board run: PASS"
