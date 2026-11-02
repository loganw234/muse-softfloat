#!/usr/bin/env bash
# v05_wasm.sh - rebuild msf.wasm in scratch via recorded Zig recipe,
# byte-compare with committed, replay committed + regen samples headless.
set -u
ROOT="$PWD"
V="$ROOT/worktrees/verify5-readme3"
W="$ROOT/scratch/verifier-w5readme3/wasm"
ZIG="$ROOT/scratch/parcel-w5site/zig-x86_64-windows-0.17.0/zig.exe"
mkdir -p "$W/tmp" "$W/committed" "$W/regen"
export TMPDIR="$W/tmp" TMP="$W/tmp" TEMP="$W/tmp"
"$ZIG" version
cd "$V"
# Same command shape as site/build.py: zig cc -target wasm32-freestanding ...
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_alg.c src/msf_aug.c src/msf_flags.c src/msf_math.c src/msf_roundpack.c src/msf_string.c src/msf_wide.c"
# shellcheck disable=SC2086
"$ZIG" cc -target wasm32-freestanding -O2 -nostdlib -Wl,--no-entry "-Wl,-z,stack-size=1048576" -Wl,--export=msf_op_count -Wl,--export=msf_run -Wl,--export=msf_result_lo -Wl,--export=msf_result_hi -Wl,--export=msf_result_flags -Wl,--export=msf_result_ok $SRC site/glue.c -o "$W/msf.wasm" > "$W/build.log" 2>&1 || { echo "WASM BUILD FAIL"; tail -10 "$W/build.log"; exit 1; }
ls -l "$W/msf.wasm"
sha256sum "$W/msf.wasm" "$V/site/msf.wasm"
cmp "$W/msf.wasm" "$V/site/msf.wasm" && echo "BYTE-IDENTICAL" || echo "BYTES-DIFFER"
# Replay committed trio
cp "$V/site/ops.json" "$V/site/vectors-sample.json" "$W/committed/"
cp "$W/msf.wasm" "$W/committed/"
cp "$V/site/replay.mjs" "$W/committed/"
echo "--- replay committed sample through rebuilt wasm ---"
node "$W/committed/replay.mjs" "$W/committed/" > "$W/replay-committed.log" 2>&1
echo "replay exit: $?"
cat "$W/replay-committed.log" | head -15
# Replay regen trio
cp "$ROOT/scratch/verifier-w5readme3/regen/ops.json" "$ROOT/scratch/verifier-w5readme3/regen/vectors-sample.json" "$W/regen/"
cp "$W/msf.wasm" "$W/regen/"
cp "$V/site/replay.mjs" "$W/regen/"
echo "--- replay regen sample through rebuilt wasm ---"
node "$W/regen/replay.mjs" "$W/regen/" > "$W/replay-regen.log" 2>&1
echo "replay exit: $?"
cat "$W/replay-regen.log" | head -15
