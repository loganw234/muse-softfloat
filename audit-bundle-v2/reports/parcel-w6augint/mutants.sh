#!/usr/bin/env bash
# mutants.sh - run from worktree root. Rebuilds the two existing
# negative-control hooks on the new code and watches each fail:
#  rmswap  IW_RM_LO/HI swapped -> containment vs catalogue exact
#          must show decided-wrong > 0.
#  guard0  IW_STAGE3_GUARD=0 -> stage 3 must decide at least one
#          guard-family row the stock build leaves UNCERTAIN
#          (rows whose expansion sums are proven inexact by the
#          Fraction oracle in check_expansions.py).
set -u
WS=/c/Users/logan/source/repos/Muse-Softfloat
SCR=$WS/scratch/parcel-w6augint
PY=$WS/.venv/Scripts/python.exe
export MSF_PYTHON=$PY

bash "$SCR/build-run.sh" rmswap -DIW_RM_LO=MSF_ROUND_TOWARD_POSITIVE -DIW_RM_HI=MSF_ROUND_TOWARD_NEGATIVE || exit 1
bash "$SCR/build-run.sh" guard0 -DIW_STAGE3_GUARD=0 || exit 1

echo "== rmswap vs stock(differential + containment) =="
$PY "$SCR/compare_streams.py" "$SCR/stream-new.txt" "$SCR/stream-rmswap.txt" tests/interval_catalogue.tsv
echo "== guard0 vs stock =="
$PY "$SCR/compare_streams.py" "$SCR/stream-new.txt" "$SCR/stream-guard0.txt" tests/interval_catalogue.tsv
echo "== guard0 guard-family rows =="
grep -E 'RAY id=(682|683|684|685) ' "$SCR/stream-guard0.txt"
