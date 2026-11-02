#!/usr/bin/env bash
# probe1: budgets smoke + standard in the copy; logs into scratch/verifier-w1f32
set -u
W=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify-f32
S=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w1f32
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
export MSF_TESTFLOAT_GEN=C:/Users/logan/source/repos/Muse-Softfloat/scratch/oracles/TestFloat-3e/build/Linux-x86_64-GCC/testfloat_gen.exe
cd "$W" || exit 9
tools/run.sh smoke > "$S/p1-smoke.log" 2>&1
echo "SMOKE_EXIT=$?" > "$S/p1-smoke.exit"
tools/run.sh standard > "$S/p1-standard.log" 2>&1
echo "STANDARD_EXIT=$?" > "$S/p1-standard.exit"
echo done-probe1
