#!/usr/bin/env bash
set -uo pipefail
A=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/w1-f64
B=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify-f64
for f in tests/gen_vectors_f64.py tests/vectors/arith-f64.vec tests/vectors/compare-f64.vec tests/vectors/conv-f64.vec tests/vectors/misc-f64.vec tests/vectors/nan-f64.vec tables/implemented.tsv include/muse_softfloat.h docs/COVERAGE.tsv tests/msf_dispatch.h src/msf_formats.h src/msf_roundpack.c tests/berkeley_ingest.py tests/gen_vectors.py tools/run.sh; do
  if cmp -s "$A/$f" "$B/$f"; then echo "IDENTICAL $f"; else echo "DIFFER $f"; fi
done
