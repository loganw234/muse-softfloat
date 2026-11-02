#!/usr/bin/env bash
# 10_probe.sh - environment record (Git Bash, relative paths).
set -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
COPY="$ROOT/worktrees/verify5-exp2"
SCR="$ROOT/scratch/verifier-w5exp2"
ORACLE="$ROOT/scratch/oracles"
{
echo "== verifier-w5exp2 env probe =="
echo "date: $(date '+%Y-%m-%d %H:%M:%S %z')"
echo "ROOT=$ROOT"
PY="$ROOT/.venv/Scripts/python.exe"
echo "MSF_PYTHON=$PY"
"$PY" --version 2>&1
"$PY" -c "import mpmath; print('mpmath', mpmath.__version__)" 2>&1
echo "bash gcc: $(gcc -dumpmachine 2>&1) $(gcc --version 2>&1 | head -1)"
echo "mingw64 gcc: $(/c/msys64/mingw64/bin/gcc -dumpmachine 2>&1) $(/c/msys64/mingw64/bin/gcc --version 2>&1 | head -1)"
echo "mpfr header: $(grep -m1 MPFR_VERSION_STRING /c/msys64/mingw64/include/mpfr.h 2>/dev/null || echo MISSING)"
grep -c "mpfr_exp2m1" /c/msys64/mingw64/include/mpfr.h 2>/dev/null || echo "no mpfr_exp2m1 decl count"
echo "mpfr lib: $(ls /c/msys64/mingw64/lib/libmpfr* 2>/dev/null || echo MISSING)"
echo "arm: $(arm-none-eabi-gcc --version 2>&1 | head -1)"
echo "which arm: $(which arm-none-eabi-gcc 2>&1)"
echo "copy HEAD: $(git -C "$COPY" rev-parse HEAD 2>&1) $(git -C "$COPY" log -1 --format=%s 2>&1)"
echo "copy status bytes: $(git -C "$COPY" status --short 2>&1 | wc -l)"
echo "parent a0acf2a: $(git -C "$COPY" log -1 --format=%s a0acf2a 2>&1)"
echo "--- oracle tree ---"
ls "$ORACLE" 2>&1
echo "--- nproc/mem ---"
nproc 2>&1; free -m 2>&1 | head -2 || true
} 2>&1 | tee "$SCR/10_probe.log"
