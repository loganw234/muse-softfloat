#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify5-demo || exit 9
for f in board/ias15_run.sh board/kissfft_run.sh board/interval_run.sh board/ias15_api.h board/ias15_hash.c board/ias15_ic.h board/interval_host.c board/interval_workload.c board/kissfft_host.py tests/sha256.c tests/interval_catalogue.tsv compat/msf_aeabi.c docs/RECORD.md docs/BOARD.md docs/COVERAGE.tsv docs/metrics/fetches.jsonl; do
  [ -e "$f" ] || echo "MISSING: $f"
done
echo SWEEP_DONE
grep -c "ce81d66e9b0b0a4b654c4eb82664417780c6f09c3f866901002b286980ba9aec" /c/Users/logan/source/repos/Muse-Softfloat/ledger/parcel-w4interval.md
