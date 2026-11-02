#!/usr/bin/env bash
# committed-vector regeneration (twice byte-stable; exp prefix check)
set -eu
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
cd "$ROOT/worktrees/w5-log2"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export MSF_PYTHON="$ROOT/.venv/Scripts/python.exe"
export TMPDIR="$ROOT/scratch/parcel-w5log2/tmp"
export MSF_EXPLOG_DECIDER="$PWD/build/explog/explog_exhaustive.exe"
mkdir -p "$TMPDIR" build/explog/vec1 build/explog/vec2
ulimit -v 2097152 2>/dev/null || true
echo "ulimit -v: $(ulimit -v) KB"
cp tests/vectors/explog-f16.vec tests/vectors/explog-f32.vec tests/vectors/explog-f64.vec build/explog/
"$MSF_PYTHON" tests/gen_vectors_explog.py build/explog/vec1
"$MSF_PYTHON" tests/gen_vectors_explog.py build/explog/vec2
for f in f16 f32 f64; do
    cmp "build/explog/vec1/explog-$f.vec" "build/explog/vec2/explog-$f.vec" \
        && echo "vec $f twice byte-identical"
    n=$(wc -l < "build/explog/explog-$f.vec")
    head -n "$n" "build/explog/vec1/explog-$f.vec" > build/explog/prefix-$f.vec
    if cmp -s "build/explog/explog-$f.vec" "build/explog/prefix-$f.vec"; then
        echo "vec $f: exp Step-3a lines byte-prefix preserved ($n lines)"
    else
        echo "vec $f: PREFIX CHANGED"; diff "build/explog/explog-$f.vec" "build/explog/prefix-$f.vec" | head -5; exit 1
    fi
done
cp build/explog/vec1/explog-f16.vec build/explog/vec1/explog-f32.vec build/explog/vec1/explog-f64.vec tests/vectors/
wc -l tests/vectors/explog-*.vec
grep -c "log2 " tests/vectors/explog-f64.vec || true
grep -c "log2p1 " tests/vectors/explog-f64.vec || true
