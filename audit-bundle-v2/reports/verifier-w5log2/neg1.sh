#!/usr/bin/env bash
# neg1.sh - NC-1ULP: flip the low bit of one hardest expectation;
# the runner must refuse (FAIL verdict).
set -u
export PATH=/c/msys64/mingw64/bin:$PATH
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5log2
COPY=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify5-log2
ulimit -v 4194304
cd "$SCR" || exit 9
grep -E 'msf64_log2(p1)? .*mpfr-explog:hardest' "$COPY/tests/vectors/explog-f64.vec" | head -5 > build/nc1.vec
wc -l build/nc1.vec
# flip the low bit of the result field on line 1 (field 5)
PY=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
"$PY" - <<'EOF'
lines = open('build/nc1.vec').read().splitlines()
t = lines[0].split(' ')
rb = int(t[4], 16) ^ 0x1
t[4] = '%x' % rb
lines[0] = ' '.join(t)
open('build/nc1mut.vec','w').write('\n'.join(lines) + '\n')
EOF
diff build/nc1.vec build/nc1mut.vec | head -4
./build/msf_runner.exe verify build/nc1mut.vec > logs/nc1.log 2>&1
echo "runner rc=$?"
tail -3 logs/nc1.log
grep -c '^FAIL' logs/nc1.log
