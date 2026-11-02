#!/bin/bash
# Probe H2: rerun mydecider with escalation, then diff vs parcel decide.
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
PY=$ROOT/.venv/Scripts/python.exe
V=$ROOT/scratch/verifier-w4trig
cd "$ROOT" || exit 9
"$PY" $V/mydecider.py $V/tmp/xdec.in $V/tmp/xdec.my.out > $V/log_xdec_my.txt 2>&1
echo "mydecider rc=$?"
cat $V/log_xdec_my.txt
grep -c '^UNDECIDED' $V/tmp/xdec.my.out
grep '^UNDECIDED' $V/tmp/xdec.my.out | sed 's/UNDECIDED \([a-z0-9_]*\).*/\1/' | sort | uniq -c
