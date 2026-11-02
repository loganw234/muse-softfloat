#!/usr/bin/env bash
set -uo pipefail
G="C:/Program Files/Git/bin/git.exe"
M=/c/Users/logan/source/repos/Muse-Softfloat/muse-softfloat
V=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify-f64
echo "===== run.sh: base->copy ====="
"$G" -c safe.directory="$V" -C "$V" diff 4cdb912 -- tools/run.sh
echo "===== run.sh: 06fdec8 -> main HEAD ====="
"$G" -c safe.directory="$M" -C "$M" diff 06fdec8 HEAD -- tools/run.sh | head -n 30
echo "===== dispatch/header/COVERAGE: copy vs 06fdec8 stat ====="
for f in tests/msf_dispatch.h include/muse_softfloat.h docs/COVERAGE.tsv; do
  "$G" -c safe.directory="$M" -C "$M" show 06fdec8:"$f" > /tmp/cmp-a.bin
  cp "$V/$f" /tmp/cmp-b.bin
  echo "--- $f: $(cmp -l /tmp/cmp-a.bin /tmp/cmp-b.bin | wc -l) differing bytes"
done
echo "===== main HEAD vs 06fdec8 stat (same files) ====="
"$G" -c safe.directory="$M" -C "$M" diff --stat 06fdec8 HEAD -- tools/run.sh tests/msf_dispatch.h include/muse_softfloat.h docs/COVERAGE.tsv tables/implemented.tsv
