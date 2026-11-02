#!/usr/bin/env bash
# v07_wasmsame.sh - two rebuilds, identical absolute invocation like build.py.
set -u
ROOT="$PWD"
V="$ROOT/worktrees/verify5-readme3"
W="$ROOT/scratch/verifier-w5readme3/wasm"
ZIG="$ROOT/scratch/parcel-w5site/zig-x86_64-windows-0.17.0/zig.exe"
mkdir -p "$W/same"
export TMPDIR="$W/same" TMP="$W/same" TEMP="$W/same"
cd "$V"
SRC="$V/src/msf16.c $V/src/msf32.c $V/src/msf64.c $V/src/msf_alg.c $V/src/msf_aug.c $V/src/msf_flags.c $V/src/msf_math.c $V/src/msf_roundpack.c $V/src/msf_string.c $V/src/msf_wide.c"
# shellcheck disable=SC2086
"$ZIG" cc -target wasm32-freestanding -O2 -nostdlib -Wl,--no-entry "-Wl,-z,stack-size=1048576" -Wl,--export=msf_op_count -Wl,--export=msf_run -Wl,--export=msf_result_lo -Wl,--export=msf_result_hi -Wl,--export=msf_result_flags -Wl,--export=msf_result_ok $SRC "$V/site/glue.c" -o "$W/same/msf.wasm" > "$W/same-b1.log" 2>&1 || { echo "B1 FAIL"; tail -5 "$W/same-b1.log"; exit 1; }
sha256sum "$W/same/msf.wasm"
cp "$W/same/msf.wasm" "$W/same/msf_b1.wasm"
# shellcheck disable=SC2086
"$ZIG" cc -target wasm32-freestanding -O2 -nostdlib -Wl,--no-entry "-Wl,-z,stack-size=1048576" -Wl,--export=msf_op_count -Wl,--export=msf_run -Wl,--export=msf_result_lo -Wl,--export=msf_result_hi -Wl,--export=msf_result_flags -Wl,--export=msf_result_ok $SRC "$V/site/glue.c" -o "$W/same/msf.wasm" > "$W/same-b2.log" 2>&1 || { echo "B2 FAIL"; tail -5 "$W/same-b2.log"; exit 1; }
sha256sum "$W/same/msf.wasm"
cmp "$W/same/msf_b1.wasm" "$W/same/msf.wasm" && echo "SAME-PATH-IDENTICAL" || echo "SAME-PATH-DIFFERS"
