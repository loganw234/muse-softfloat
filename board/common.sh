#!/usr/bin/env bash
# common.sh - shared board-budget plumbing. Sourced by run_board.sh
# and run_bench.sh from the repository root (tools/run.sh board).
# The board is lead-held: taking <ledger>/board.lock is the first
# act, removing it (only if we wrote it) the last (docs/BOARD.md).
LEDGER_DIR="$(cd ../ledger 2>/dev/null && pwd)"
LOCK="$LEDGER_DIR/board.lock"
PICOTOOL="${MSF_PICOTOOL:-/c/Users/logan/pico/picotool/picotool.exe}"
[ -n "${PICO_SDK_PATH:-}" ] || PICO_SDK_PATH="/c/Users/logan/pico/pico-sdk"
PY="${MSF_PYTHON:-../.venv/Scripts/python.exe}"
NINJA="${MSF_NINJA:-$(cygpath -w ../.venv/Scripts/ninja.exe 2>/dev/null | tr '\\' '/' || echo ../.venv/Scripts/ninja.exe)}"
BOARD_BUILD=build/board-fw
export TMPDIR=$PWD/$BOARD_BUILD/tmp
mkdir -p "$TMPDIR"
export TMP="$(cygpath -w "$TMPDIR" 2>/dev/null || echo "$TMPDIR")"
export TEMP="$TMP"

board_fail() { echo "BOARD: FAIL - $1"; exit 1; }

take_lock() {
    [ -d "$LEDGER_DIR" ] || board_fail "ledger dir not found at ../ledger"
    [ -f "$LOCK" ] && board_fail "board.lock exists (held): $(cat "$LOCK")"
    printf 'lead (Muse Code)\n%s\n%s\n' "$1" "$(date '+%Y-%m-%d %H:%M:%S %z')" > "$LOCK"
    echo "board lock taken: $LOCK"
    trap 'rm -f "$LOCK"; echo "board lock released"' EXIT
}

build_fw() { # $1 = build subdir name, rest = extra cmake -D...
    local dir="$BOARD_BUILD/$1"; shift
    cmake -S board -B "$dir" -G Ninja -DCMAKE_MAKE_PROGRAM="$NINJA" \
        -DPICO_SDK_PATH="$PICO_SDK_PATH" -DCMAKE_BUILD_TYPE=Release "$@" \
        > "$dir-cmake.log" 2>&1 || { tail -20 "$dir-cmake.log"; board_fail "cmake configure ($dir)"; }
    cmake --build "$dir" > "$dir-build.log" 2>&1 || { tail -30 "$dir-build.log"; board_fail "firmware build ($dir)"; }
    echo "built firmware in $dir"
}

flash_uf2() { # $1 = uf2 path
    echo "flashing $1 sha256=$(sha256sum "$1" | cut -d' ' -f1)"
    # -f forces a running device (USB serial present) to reboot so
    # the load can proceed; measured necessary on this board, whose
    # firmware reset interface did not answer a plain reboot -u.
    # With several boards on the bus an untargeted load may pick
    # the wrong device: MSF_BOARD_SERIAL selects exactly one.
    local ser_arg=()
    echo "flash target serial: ${MSF_BOARD_SERIAL:-untargeted}"
    if [ -n "${MSF_BOARD_SERIAL:-}" ]; then
        ser_arg=(--ser "$MSF_BOARD_SERIAL")
    fi
    if ! "$PICOTOOL" load ${ser_arg[@]+"${ser_arg[@]}"} -f -x "$1" > "$BOARD_BUILD/flash.log" 2>&1; then
        cat "$BOARD_BUILD/flash.log"
        board_fail "picotool load failed - board may need hands (hold BOOTSEL while plugging in), see docs/BOARD.md"
    fi
    cat "$BOARD_BUILD/flash.log"
    sleep 2
}
