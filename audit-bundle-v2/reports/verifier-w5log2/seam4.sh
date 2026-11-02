#!/usr/bin/env bash
# seam4.sh - dispatch/header/doc rows for the 6 log instantiations.
set -u
export PATH=/c/msys64/mingw64/bin:$PATH
COPY=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify5-log2
cd "$COPY" || exit 9
echo "--- dispatch log rows:"
grep -c 'log2' tests/msf_dispatch.h
grep -n 'msf64_log2p1\|msf16_log2[^p]' tests/msf_dispatch.h | head -6
echo "--- VECTORS.md log rows:"
grep -n 'log2' tests/VECTORS.md | head -12
echo "--- WIDTHS.md log row:"
grep -n 'log' docs/WIDTHS.md | head -6
echo "--- briefs.jsonl parcel row:"
grep -o 'parcel-w5log2[^,]*' docs/metrics/briefs.jsonl | head -3
echo "--- header decls:"
grep -n 'msf16_log2\|msf64_log2p1' include/muse_softfloat.h | head -4
