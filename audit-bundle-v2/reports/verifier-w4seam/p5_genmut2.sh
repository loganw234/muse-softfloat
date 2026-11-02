#!/usr/bin/env bash
# p5_genmut2.sh - corrected authority/sig mutants (cols: 4=sig, 8=authority).
set -u
WS=/c/Users/logan/source/repos/Muse-Softfloat
COPY=$WS/worktrees/verify4-seam
MUT=$WS/scratch/verifier-w4seam/mut
T=$COPY/tables/operations.tsv
PY=$WS/.venv/Scripts/python.exe
for m in m-authority m-sig; do rm -rf "$MUT/$m"; mkdir -p "$MUT/$m/tables" "$MUT/$m/tools";
  cp "$COPY/tables/formats.tsv" "$COPY/tables/implemented.tsv" "$MUT/$m/tables/";
  cp "$COPY/tools/gen_tables.py" "$MUT/$m/tools/"; done
awk -F'\t' 'BEGIN{OFS=FS} $1=="minimum"{$8="host-libm"} {print}' "$T" > "$MUT/m-authority/tables/operations.tsv"
awk -F'\t' 'BEGIN{OFS=FS} $1=="minimum"{$4="pair_result"} {print}' "$T" > "$MUT/m-sig/tables/operations.tsv"
awk -F'\t' '$1=="minimum"{print "authority-mutant row:", $1, $8}' "$MUT/m-authority/tables/operations.tsv"
awk -F'\t' '$1=="minimum"{print "sig-mutant row:", $1, $4}' "$MUT/m-sig/tables/operations.tsv"
for m in m-authority m-sig; do (cd "$MUT/$m" && "$PY" tools/gen_tables.py "$MUT/$m/out" > "$MUT/$m/log.txt" 2>&1);
  echo "$m exit: $? | $(tail -1 "$MUT/$m/log.txt")"; done
