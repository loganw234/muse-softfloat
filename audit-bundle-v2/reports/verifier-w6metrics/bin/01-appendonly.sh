#!/bin/bash
# Probe 1: append-only. Parent file bytes must be exact byte prefix of tip.
set -u
DUP="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6metrics/dup"
OUT="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6metrics/out"
PARENT="cdc40ae"
cd "$DUP"
for f in usage passes escalations briefs; do
  P="$OUT/parent-$f.jsonl"
  T="docs/metrics/$f.jsonl"
  git show "$PARENT:docs/metrics/$f.jsonl" > "$P" 2>"$OUT/parent-$f.err"
  rc=$?
  if [ $rc -ne 0 ]; then echo "$f: git show FAILED"; cat "$OUT/parent-$f.err"; continue; fi
  pn=$(wc -l < "$P" | tr -d ' '); tn=$(wc -l < "$T" | tr -d ' ')
  pb=$(wc -c < "$P" | tr -d ' '); tb=$(wc -c < "$T" | tr -d ' ')
  ph=$(sha256sum "$P" | cut -d' ' -f1); ph8=${ph:0:16}
  # byte-prefix test: first pb bytes of tip equal parent bytes
  head -c "$pb" "$T" | cmp -s - "$P"
  cmp_rc=$?
  echo "$f: parent_rows=$pn tip_rows=$tn parent_bytes=$pb tip_bytes=$tb parent_sha256_16=$ph8 prefix_cmp_rc=$cmp_rc"
done
echo "=== diff numstat parent..tip ==="
git diff --numstat "$PARENT" HEAD -- docs/metrics/
echo "=== tip file sha256 (first16) ==="
sha256sum docs/metrics/usage.jsonl docs/metrics/passes.jsonl docs/metrics/escalations.jsonl docs/metrics/briefs.jsonl | sed 's#docs/metrics/##'
