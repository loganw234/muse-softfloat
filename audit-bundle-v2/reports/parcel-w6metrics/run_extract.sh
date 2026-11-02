#!/usr/bin/env bash
# Sanctioned extractor: selftest, then full lead-subtree run at the Wave 6 close cutoff.
WS=/c/Users/logan/source/repos/Muse-Softfloat
PY=$WS/.venv/Scripts/python.exe
TOOL=$WS/worktrees/w6-metrics/tools/extract_session_metrics.py
SESS=/c/Users/logan/.local/share/muse/sessions/2026/10/26/01a17907-4147-7333-a565-56071da9d971
OUT=$WS/scratch/parcel-w6metrics/extract-out
mkdir -p "$OUT"
echo "=== selftest ==="
"$PY" "$TOOL" --selftest || exit 1
echo "=== extract (until 2026-10-30T16:08:00-07:00, committer time of base cdc40ae) ==="
# Verdicts below are copied from the frozen passes.jsonl rows (records) for the
# natively-labelled frozen verifiers in this subtree (same set as the w5 run);
# the fold drops those rows after the recount check. Wave 5-close/6 agents are
# session-id labelled, so the extractor demands nothing for them; their
# annotations enter at the fold from ledger/RECORD/git.
time "$PY" "$TOOL" --session-dir "$SESS" --wave backfill --out-dir "$OUT" \
  --until "2026-10-30T16:08:00-07:00" \
  --author-commit lead=dfc7a0200993470adf8d52b7d4d6da4d830bded0 \
  --verdict verifier-phase0=0,3,"NOT READY",true \
  --verdict rechecker-phase0=0,1,"NOT READY",true \
  --verdict rechecker2-phase0=0,0,READY,false \
  --verdict verifier-w2xf=3,3,"NOT READY",true \
  --verdict verifier-w2f16=1,4,"NOT READY",true \
  --verdict verifier-w3str=1,4,"NOT READY",true \
  --verdict verifier-wave0=0,2,"NOT READY",true
echo "exit=$?"
wc -l "$OUT/usage.jsonl" "$OUT/passes.jsonl"
