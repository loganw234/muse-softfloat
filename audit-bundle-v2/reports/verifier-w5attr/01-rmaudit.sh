#!/usr/bin/env bash
# 01-rmaudit.sh - re-audit every rm switch in src/ by source read.
# Counts switch sites on rm, lists MSF_IROUND mentions, and checks that
# exactly the study's two string sites carry ta cases.
set -u
S="$COPY/src"
echo "== files under $S =="
ls "$S"
echo
echo "== every MSF_IROUND mention in src/ =="
grep -rn "MSF_IROUND" "$S"
echo
echo "== switch sites on rm in src/ =="
grep -rn "switch *(rm)" "$S"
echo
echo "== ta arms by file =="
grep -rn "TIES_TO_AWAY" "$S"
echo
echo "== default-arm wording near each switch =="
grep -rn -A2 "toward zero" "$S" | head -n 30
