#!/usr/bin/env bash
# p5_genmut.sh - refusal mutants on SCRATCH copies (never the copy).
# Each mutant must abort generation (nonzero exit).
set -u
WS=/c/Users/logan/source/repos/Muse-Softfloat
COPY=$WS/worktrees/verify4-seam
SCR=$WS/scratch/verifier-w4seam
export MSF_PYTHON=$WS/.venv/Scripts/python.exe
MUT=$SCR/mut
rm -rf "$MUT"
mk() { rm -rf "$MUT/$1"; mkdir -p "$MUT/$1/tables" "$MUT/$1/tools";
  cp "$COPY/tables/formats.tsv" "$COPY/tables/operations.tsv" "$COPY/tables/implemented.tsv" "$MUT/$1/tables/";
  cp "$COPY/tools/gen_tables.py" "$MUT/$1/tools/"; }
run() { (cd "$MUT/$1" && "$MSF_PYTHON" tools/gen_tables.py "$MUT/$1/out" > "$MUT/$1/log.txt" 2>&1); echo "$1 exit: $? | $(tail -1 "$MUT/$1/log.txt" 2>/dev/null || tail -c 200 "$MUT/$1/log.txt")"; }
T=$COPY/tables/operations.tsv
# 1. unknown claim token on a tier2 family
mk m-unknown-claim; awk -F'\t' 'BEGIN{OFS=FS} $1=="minimum"{$12="C-BOGUS"} {print}' "$T" > "$MUT/m-unknown-claim/tables/operations.tsv"
# 2. reserved SF-1 token C-ULP on a tier2 family
mk m-reserved-ulp; awk -F'\t' 'BEGIN{OFS=FS} $1=="minimum"{$12="C-ULP"} {print}' "$T" > "$MUT/m-reserved-ulp/tables/operations.tsv"
# 2b. reserved token C-754-EXC
mk m-reserved-exc; awk -F'\t' 'BEGIN{OFS=FS} $1=="minimum"{$12="C-754-EXC"} {print}' "$T" > "$MUT/m-reserved-exc/tables/operations.tsv"
# 2c. reserved token C-API
mk m-reserved-api; awk -F'\t' 'BEGIN{OFS=FS} $1=="minimum"{$12="C-API"} {print}' "$T" > "$MUT/m-reserved-api/tables/operations.tsv"
# 3. tier/claim mispairing: tier1 family with C-754
mk m-mispair; awk -F'\t' 'BEGIN{OFS=FS} $1=="add"{$12="C-754"} {print}' "$T" > "$MUT/m-mispair/tables/operations.tsv"
# 4. unknown authority
mk m-authority; awk -F'\t' 'BEGIN{OFS=FS} $1=="minimum"{$9="host-libm"} {print}' "$T" > "$MUT/m-authority/tables/operations.tsv"
# 5. unknown tier
mk m-tier; awk -F'\t' 'BEGIN{OFS=FS} $1=="minimum"{$11="3"} {print}' "$T" > "$MUT/m-tier/tables/operations.tsv"
# 6. unknown sig
mk m-sig; awk -F'\t' 'BEGIN{OFS=FS} $1=="minimum"{$5="pair_result"} {print}' "$T" > "$MUT/m-sig/tables/operations.tsv"
for m in m-unknown-claim m-reserved-ulp m-reserved-exc m-reserved-api m-mispair m-authority m-tier m-sig; do run "$m"; done
