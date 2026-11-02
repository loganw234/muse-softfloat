#!/usr/bin/env bash
# verifier-w5twiddledoc gate re-run (Git Bash).
# Builds the copy's demo/twiddle_gate.c against a fresh Fork B tree
# from the copy's demo/make_kissfft_tree.py and reproduces the
# PROVENANCE field count + mismatch count. Offline: pristine input
# is the evidence trail's pinned pristine extract.
set -eu
cd "$(dirname "$0")/../.." || exit 9
V="${MSF_PYTHON:-.venv/Scripts/python.exe}"
COPY=worktrees/verify5-twiddledoc
PRISTINE=scratch/parcel-w4kissfft/pristine
TREE=scratch/verifier-w5twiddledoc/kissfft-tree
OUT=scratch/verifier-w5twiddledoc/out
mkdir -p "$OUT"
"$V" "$COPY/demo/make_kissfft_tree.py" "$PRISTINE" "$TREE"
WT="$COPY"
CORE="$WT/src/msf16.c $WT/src/msf32.c $WT/src/msf64.c $WT/src/msf_flags.c $WT/src/msf_wide.c $WT/src/msf_roundpack.c $WT/src/msf_string.c $WT/src/msf_math.c"
gcc -std=c11 -O2 -Wall -Wextra -ffp-contract=off -fno-fast-math \
  -Dkiss_fft_scalar=double \
  -I"$WT" -I"$WT/compat" -I"$TREE" \
  "$COPY/demo/twiddle_gate.c" $CORE "$WT/compat/msf_aeabi.c" \
  "$COPY/demo/kissfft_host_shim.c" \
  -Wl,--wrap=sinpi,--wrap=cospi,--wrap=floor -lm -lmpfr -lgmp \
  -o "$OUT/twiddle_gate.exe"
"$OUT/twiddle_gate.exe" | tee "$OUT/gate-verify.txt"
"$V" scratch/verifier-w5twiddledoc/census_check.py "$OUT/gate-verify.txt"
