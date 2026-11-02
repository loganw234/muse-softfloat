#!/usr/bin/env bash
set -uo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat
echo "copy-only rows: $(diff /tmp/impl-copy.txt /tmp/impl-main.txt | grep -c '^<')"
echo "main-only non-msf32 rows: $(diff /tmp/impl-copy.txt /tmp/impl-main.txt | grep '^>' | grep -vc 'msf32_')"
echo "=== off-limits: copy vs main ==="
for f in src/msf_roundpack.c tests/berkeley_ingest.py tests/gen_vectors.py tools/run.sh tests/msf_dispatch.h include/muse_softfloat.h docs/COVERAGE.tsv src/msf_formats.h tests/vectors/pack16.vec tests/vectors/pack32.vec tests/vectors/pack64.vec; do
  if cmp -s "worktrees/verify-f64/$f" "muse-softfloat/$f"; then echo "EQ-MAIN $f"; else echo "NE-MAIN $f"; fi
done
