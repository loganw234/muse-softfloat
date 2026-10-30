#!/usr/bin/env bash
# examples/host/build.sh - one-command host on-ramp.
#
# Builds the library sources plus examples/host/main.c, runs
# the program, and diffs its stdout against the committed
# examples/host/expected.txt. Exits nonzero on any mismatch
# (build failure, program self-check failure, or diff).
#
# Why a script rather than only a documented compiler line:
# the single line below is the whole build, but the script
# also runs the program and enforces the output diff, so the
# same one command serves a fresh clone, this Windows host
# under Git Bash (AGENTS.md), and Linux CI unchanged.
#
#   bash examples/host/build.sh          # build + run + diff
#   bash examples/host/build.sh regen    # rewrite expected.txt
#                                        # (intentional changes
#                                        # only; review the diff)
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT" || exit 9

# Same toolchain resolution as tools/run.sh: MSYS2 first when
# present (Windows host); plain system compiler elsewhere.
[ -d /c/msys64/mingw64/bin ] && export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
CC="${MSF_HOST_CC:-${CC:-gcc}}"
BUILD=build/example-host
mkdir -p "$BUILD/tmp"
export TMPDIR=$PWD/$BUILD/tmp
export TMP="$(cygpath -w "$TMPDIR" 2>/dev/null || echo "$TMPDIR")"
export TEMP="$TMP"

SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c src/msf_aug.c"
fail() { echo "host example: FAIL - $1"; exit 1; }

echo "compiler: $CC $($CC -dumpmachine 2>/dev/null) $($CC -dumpversion 2>/dev/null)"
$CC -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off -Iinclude \
    $SRC examples/host/main.c -o "$BUILD/msf_example_host.exe" \
    > "$BUILD/build.log" 2>&1 \
    || { cat "$BUILD/build.log"; fail "build (see $BUILD/build.log)"; }
echo "built $BUILD/msf_example_host.exe"

"$BUILD/msf_example_host.exe" > "$BUILD/got.raw" 2>&1 \
    || { cat "$BUILD/got.raw"; fail "program self-checks (nonzero exit)"; }
# Committed files are LF (AGENTS.md); a Windows-host program
# writing through the C runtime's text mode emits CRLF, so
# compare CR-stripped. On Linux this changes nothing.
tr -d '\r' < "$BUILD/got.raw" > "$BUILD/got.txt"
cat "$BUILD/got.txt"

if [ "${1:-}" = "regen" ]; then
    cp "$BUILD/got.txt" examples/host/expected.txt
    echo "host example: expected.txt regenerated - review the change before committing"
    exit 0
fi

diff -u examples/host/expected.txt "$BUILD/got.txt" > "$BUILD/diff.log" 2>&1 \
    || { cat "$BUILD/diff.log"; fail "stdout differs from examples/host/expected.txt"; }
echo "host example: PASS (stdout matches examples/host/expected.txt)"
