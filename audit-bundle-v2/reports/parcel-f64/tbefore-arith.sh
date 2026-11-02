#!/usr/bin/env bash
set -uo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w1-f64
build/w1/controls/msf_runner_tbefore.exe verify build/w1/directed-check/arith-f64.vec > build/w1/logs/tbefore-arith2.log 2>&1
echo "rc=$?"
grep -E '^(total|VERDICT)' build/w1/logs/tbefore-arith2.log
grep '^FAIL' build/w1/logs/tbefore-arith2.log | head -10 || true
grep -c '^FAIL' build/w1/logs/tbefore-arith2.log || true
