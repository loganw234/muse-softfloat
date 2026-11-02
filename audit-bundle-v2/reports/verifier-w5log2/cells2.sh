#!/usr/bin/env bash
# cells2.sh - targeted recentre-boundary probes.
set -u
export PATH=/c/msys64/mingw64/bin:$PATH
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5log2
ulimit -v 4194304
cd "$SCR" || exit 9
for cell in "f64 log2 3ff0000000000000" "f64 log2 4000000000000000" \
  "f64 log2 3ff6a09e667f3bcc" "f64 log2 3fe0000000000000" \
  "f64 log2 3ff0000000000001" "f64 log2 4008000000000000" \
  "f32 log2 3f800000" "f32 log2 40000000" \
  "f64 log2p1 3ff0000000000000" "f64 log2p1 bfe0000000000000"; do
  # shellcheck disable=SC2086
  ./build/vlog2.exe one $cell 2>&1 | grep -E 'MISMATCH|one:'
done
