#!/usr/bin/env bash
# p5_invmut.sh - inventory mutants judged by the COPY's own inventory_check
# (function + constants extracted verbatim from tools/run.sh, never the copy).
set -u
WS=/c/Users/logan/source/repos/Muse-Softfloat
COPY=$WS/worktrees/verify4-seam
SCR=$WS/scratch/verifier-w4seam
IM=$SCR/invmut; rm -rf "$IM"; mkdir -p "$IM"
cp "$COPY/docs/COVERAGE.tsv" "$IM/base.tsv"
# extract the copy's real logic: constant lines + function body
grep -E '^TIER[12]_TOTAL_EXPECTED=' "$COPY/tools/run.sh" > "$IM/logic.sh"
sed -n '/^inventory_check/,/^}/p' "$COPY/tools/run.sh" >> "$IM/logic.sh"
judge() { ( . "$IM/logic.sh"; if inventory_check "$IM/$1" > "$IM/$1.result" 2>&1; then echo "$1: ACCEPTED | $(cat "$IM/$1.result")"; else echo "$1: REFUSED | $(cat "$IM/$1.result")"; fi ); }
C="$COPY/docs/COVERAGE.tsv"
awk -F'\t' 'BEGIN{OFS=FS} /^#/||$1=="name"{print;next} !d&&$13=="1"&&$9=="implemented"{$9="planned";d=1} {print}' "$C" > "$IM/t1-flip.tsv"
awk -F'\t' '/^#/||$1=="name"{print;next} !d&&$13=="2"{d=1;next} {print}' "$C" > "$IM/t2-delete.tsv"
head -1 "$C" > /dev/null
{ grep -E '^#' "$C"; grep -vE '^#' "$C" | head -1; awk -F'\t' 'BEGIN{OFS=FS} /^#/||$1=="name"{print;next} {print} END{print "msf16_extra\tminimum\t9.6\tf16\tf16\tnone\tyes\t4\tplanned\tproject-exact\tdirected-classes\texact\t2\tC-754"}' "$C"; } > "$IM/t2-add.tsv"
awk -F'\t' 'BEGIN{OFS=FS} /^#/||$1=="name"{print;next} !d&&$13=="2"{$14="C-API";d=1} {print}' "$C" > "$IM/t2-badclaim.tsv"
judge base.tsv; judge t1-flip.tsv; judge t2-delete.tsv; judge t2-add.tsv; judge t2-badclaim.tsv
