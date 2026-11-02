#!/usr/bin/env bash
# v06_wasmdet.sh - second identical rebuild (self-determinism) + section map.
set -u
ROOT="$PWD"
V="$ROOT/worktrees/verify5-readme3"
W="$ROOT/scratch/verifier-w5readme3/wasm"
ZIG="$ROOT/scratch/parcel-w5site/zig-x86_64-windows-0.17.0/zig.exe"
mkdir -p "$W/tmp2"
export TMPDIR="$W/tmp2" TMP="$W/tmp2" TEMP="$W/tmp2"
cd "$V"
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_alg.c src/msf_aug.c src/msf_flags.c src/msf_math.c src/msf_roundpack.c src/msf_string.c src/msf_wide.c"
# shellcheck disable=SC2086
"$ZIG" cc -target wasm32-freestanding -O2 -nostdlib -Wl,--no-entry "-Wl,-z,stack-size=1048576" -Wl,--export=msf_op_count -Wl,--export=msf_run -Wl,--export=msf_result_lo -Wl,--export=msf_result_hi -Wl,--export=msf_result_flags -Wl,--export=msf_result_ok $SRC site/glue.c -o "$W/msf2.wasm" > "$W/build2.log" 2>&1 || { echo "BUILD2 FAIL"; tail -5 "$W/build2.log"; exit 1; }
sha256sum "$W/msf.wasm" "$W/msf2.wasm"
cmp "$W/msf.wasm" "$W/msf2.wasm" && echo "SELF-DETERMINISTIC" || echo "SELF-DIFFERS"
sha256sum "$ROOT/scratch/parcel-w5site/zig-x86_64-windows-0.17.0.zip"
