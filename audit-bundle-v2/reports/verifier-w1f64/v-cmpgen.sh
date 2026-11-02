#!/usr/bin/env bash
set -uo pipefail
A=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/w1-f64
B=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify-f64
echo "=== F_ constants branch vs copy ==="
grep -n "^F_" "$A/tests/gen_vectors_f64.py" "$B/tests/gen_vectors_f64.py"
echo "=== gen diff branch->copy ==="
diff "$A/tests/gen_vectors_f64.py" "$B/tests/gen_vectors_f64.py" | head -n 60
echo "=== vec diff branch->copy ==="
diff "$A/tests/vectors/arith-f64.vec" "$B/tests/vectors/arith-f64.vec" | head -n 30
echo "=== vec line counts ==="
wc -l "$A/tests/vectors/arith-f64.vec" "$B/tests/vectors/arith-f64.vec"
