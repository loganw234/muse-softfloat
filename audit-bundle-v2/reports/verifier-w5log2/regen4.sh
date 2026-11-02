#!/usr/bin/env bash
# regen4.sh - scratch copy of the vector generator with UNDERFLOW
# restored to 0x08: does the settled table then agree (esp. log
# families), and are Step-3a exp lines byte-prefixes preserved?
set -u
export PATH=/c/msys64/mingw64/bin:$PATH
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5log2
COPY=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify5-log2
PY=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
ulimit -v 4194304
cd "$SCR" || exit 9
cp "$COPY/tests/gen_vectors_explog.py" build/genfix.py
"$PY" - <<'EOF'
p = 'build/genfix.py'
s = open(p).read()
assert 'UNDERFLOW = 0x04' in s
s = s.replace('UNDERFLOW = 0x04', 'UNDERFLOW = 0x08')
open(p, 'w').write(s)
print('patched')
EOF
export MSF_EXPLOG_DECIDER="$SCR/build/own_exhaustive.exe"
rm -rf "$SCR/build/vecF"
cd "$COPY" || exit 9
"$PY" "$SCR/build/genfix.py" "$SCR/build/vecF" > "$SCR/logs/vecF.log" 2>&1
echo "vecF rc=$?"
tail -4 "$SCR/logs/vecF.log"
for f in explog-f16.vec explog-f32.vec explog-f64.vec; do
  if cmp -s "$SCR/build/vecF/$f" tests/vectors/$f; then echo "VS-COMMIT-SAME $f"; else echo "VS-COMMIT-DIFF $f"; fi
done
