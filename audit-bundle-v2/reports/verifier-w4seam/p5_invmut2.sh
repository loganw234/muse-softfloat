#!/usr/bin/env bash
# p5_invmut2.sh - clean Tier2-add mutant (one well-formed extra planned row).
set -u
WS=/c/Users/logan/source/repos/Muse-Softfloat
COPY=$WS/worktrees/verify4-seam
IM=$WS/scratch/verifier-w4seam/invmut
cp "$COPY/docs/COVERAGE.tsv" "$IM/base.tsv"
cp "$IM/base.tsv" "$IM/t2-add-clean.tsv"
printf 'msf16_extra\tminimum\t9.6\tf16\tf16\tnone\tyes\t4\tplanned\tproject-exact\tdirected-classes\texact\t2\tC-754\n' >> "$IM/t2-add-clean.tsv"
wc -l "$IM/base.tsv" "$IM/t2-add-clean.tsv"
tail -1 "$IM/t2-add-clean.tsv" | awk -F'\t' '{print NF " fields; tier=" $13 " claim=" $14}'
( . "$IM/logic.sh"; if inventory_check "$IM/t2-add-clean.tsv" > "$IM/t2-add-clean.tsv.result" 2>&1; then echo "t2-add-clean: ACCEPTED | $(cat "$IM/t2-add-clean.tsv.result")"; else echo "t2-add-clean: REFUSED | $(cat "$IM/t2-add-clean.tsv.result")"; fi )
