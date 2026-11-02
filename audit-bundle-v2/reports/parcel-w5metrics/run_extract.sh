#!/usr/bin/env bash
# Sanctioned extractor: selftest, then full lead-subtree run at the SF-2-close cutoff.
WS=/c/Users/logan/source/repos/Muse-Softfloat
PY=$WS/.venv/Scripts/python.exe
TOOL=$WS/worktrees/w5-metrics/tools/extract_session_metrics.py
SESS=/c/Users/logan/.local/share/muse/sessions/2026/10/26/01a17907-4147-7333-a565-56071da9d971
OUT=$WS/scratch/parcel-w5metrics/extract-out
mkdir -p "$OUT"
echo "=== selftest ==="
"$PY" "$TOOL" --selftest || exit 1
echo "=== extract (until 2026-10-29T11:39:55-07:00) ==="
# Verdicts below are copied from the frozen passes.jsonl rows (records) for the
# six natively-labelled frozen verifiers in this subtree; the fold drops those
# rows after the recount check. Wave 4-5 verifiers are session-id labelled, so
# the extractor demands nothing for them; their verdicts enter at the fold.
time "$PY" "$TOOL" --session-dir "$SESS" --wave backfill --out-dir "$OUT" \
  --until "2026-10-29T11:39:55-07:00" \
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
