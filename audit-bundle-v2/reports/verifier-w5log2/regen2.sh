#!/usr/bin/env bash
# regen2.sh - gen_explog_tables.py twice; byte-compare runs and committed.
set -u
export PATH=/c/msys64/mingw64/bin:$PATH
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5log2
COPY=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify5-log2
PY=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
ulimit -v 4194304
cd "$COPY" || exit 9
"$PY" tools/gen_explog_tables.py "$SCR/build/expA.h" > "$SCR/logs/genexpA.log" 2>&1
echo "genA rc=$?"
"$PY" tools/gen_explog_tables.py "$SCR/build/expB.h" > "$SCR/logs/genexpB.log" 2>&1
echo "genB rc=$?"
if cmp -s "$SCR/build/expA.h" "$SCR/build/expB.h"; then echo "REGEN-TWICE: identical"; else echo "REGEN-TWICE: DIFFER"; fi
if cmp -s "$SCR/build/expA.h" src/msf_explog_tables.h; then echo "VS-COMMITTED: identical"; else echo "VS-COMMITTED: DIFFER"; fi
echo "--- EK lines committed:"
grep -n 'EK_LOG\|EK_TINY\|NTERMS_LOG\|NTERMS_TINY' src/msf_explog_tables.h
echo "--- EK lines regenerated:"
grep -n 'EK_LOG\|EK_TINY\|NTERMS_LOG\|NTERMS_TINY' "$SCR/build/expA.h"
echo "--- EK proof print (tail of genA log):"
tail -12 "$SCR/logs/genexpA.log"
