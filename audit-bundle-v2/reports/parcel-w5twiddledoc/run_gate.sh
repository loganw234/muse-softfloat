#!/usr/bin/env bash
# run_gate.sh - re-run the Fork B twiddle-provenance gate (parcel-w5twiddledoc).
# Git Bash. MSF_PYTHON pins the workspace .venv python.
set -eu
cd "$(dirname "$0")/../.." || exit 9
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
PY="${MSF_PYTHON:-$PWD/.venv/Scripts/python.exe}"
S=scratch/parcel-w5twiddledoc
WT=worktrees/w5-twiddledoc
TREE="$S/tree-fresh"
CORE="$WT/src/msf16.c $WT/src/msf32.c $WT/src/msf64.c $WT/src/msf_flags.c $WT/src/msf_wide.c $WT/src/msf_roundpack.c $WT/src/msf_string.c $WT/src/msf_math.c"
mkdir -p "$S/out" "$S/build"
echo "== gate build (today's tree + fresh Fork-B tree) =="
gcc -std=c11 -O2 -Wall -Wextra -ffp-contract=off -fno-fast-math -Dkiss_fft_scalar=double \
  -I$WT -I$WT/compat -I$TREE $WT/demo/twiddle_gate.c $CORE \
  $WT/compat/msf_aeabi.c $WT/demo/kissfft_host_shim.c \
  -Wl,--wrap=sinpi,--wrap=cospi,--wrap=floor -lm -lmpfr -lgmp -o "$S/build/gate5.exe" \
  2>&1 | tee "$S/out/build-gate5.log"
echo "== gate run =="
"$S/build/gate5.exe" | tee "$S/out/gate5.txt"
echo "GATE-RERUN DONE"
