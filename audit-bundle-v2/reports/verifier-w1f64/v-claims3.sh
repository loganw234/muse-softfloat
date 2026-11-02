#!/usr/bin/env bash
# verifier-w164: off-limits files copy vs parcel-merge commit on main.
set -uo pipefail
G="C:/Program Files/Git/bin/git.exe"
M=/c/Users/logan/source/repos/Muse-Softfloat/muse-softfloat
V=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify-f64
for f in tools/run.sh tests/msf_dispatch.h include/muse_softfloat.h docs/COVERAGE.tsv; do
  if "$G" -c safe.directory="$M" -C "$M" show 06fdec8:"$f" | cmp -s - "$V/$f"; then
    echo "EQ-06fdec8 $f"
  else
    echo "NE-06fdec8 $f"
  fi
done
echo "=== base->copy diffs of off-limits files, first lines ==="
"$G" -c safe.directory="$V" -C "$V" diff 4cdb912 --stat -- src/msf_roundpack.c tests/berkeley_ingest.py tests/gen_vectors.py tools/run.sh tests/msf_dispatch.h include/muse_softfloat.h docs/COVERAGE.tsv src/msf_formats.h tests/vectors/pack16.vec tests/vectors/pack32.vec tests/vectors/pack64.vec
