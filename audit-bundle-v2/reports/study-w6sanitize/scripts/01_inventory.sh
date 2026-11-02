#!/usr/bin/env bash
# Probe 1 inventory: every plausible host C compiler on this machine.
set -u
cd "$(dirname "$0")/.." || exit 9
mkdir -p logs tmp
export TMPDIR=$PWD/tmp
export TMP="$(cygpath -w "$TMPDIR" 2>/dev/null || echo "$TMPDIR")"
export TEMP="$TMP"
LOG=logs/01_inventory.log
{
echo "date: $(date '+%Y-%m-%d %H:%M:%S %z')"
echo "host: $(hostname 2>/dev/null)"
echo "bash: $BASH_VERSION"
echo "PATH=$PATH"
echo
echo "== candidate paths =="
for p in \
  /c/msys64/mingw64/bin/gcc.exe /c/msys64/mingw64/bin/clang.exe \
  /c/msys64/clang64/bin/clang.exe /c/msys64/clang64/bin/gcc.exe \
  /c/msys64/ucrt64/bin/gcc.exe /c/msys64/ucrt64/bin/clang.exe \
  /c/msys64/mingw32/bin/gcc.exe /c/msys64/mingw32/bin/clang.exe \
  /c/msys64/clang32/bin/clang.exe \
  "/c/Program Files/LLVM/bin/clang.exe" \
  "/c/Program Files/Microsoft Visual Studio/2022/Community/VC/Tools/MSVC" \
  "/c/Program Files/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC"
do
  if [ -e "$p" ]; then echo "PRESENT $p"; else echo "absent  $p"; fi
done
echo
echo "== on PATH (mingw64+usr first, as run.sh does) =="
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
for c in gcc clang cc clang-cl cl arm-none-eabi-gcc x86_64-w64-mingw32-gcc i686-w64-mingw32-gcc; do
  if command -v "$c" >/dev/null 2>&1; then echo "FOUND $c -> $(command -v "$c")"; else echo "absent-on-PATH $c"; fi
done
echo
show() {
  c="$1"
  echo "---- $c ----"
  if [ -x "$c" ] || command -v "$c" >/dev/null 2>&1; then
    "$c" --version 2>&1 | head -3
    echo "dumpmachine: $("$c" -dumpmachine 2>&1 | head -1)"
    echo "dumpversion: $("$c" -dumpversion 2>&1 | head -1)"
    echo "libasan: $("$c" -print-file-name=libasan.a 2>&1 | head -1) | $("$c" -print-file-name=libasan.dll.a 2>&1 | head -1) | $("$c" -print-file-name=libclang_rt.asan-x86_64.a 2>&1 | head -1)"
    echo "libubsan: $("$c" -print-file-name=libubsan.a 2>&1 | head -1) | $("$c" -print-file-name=libubsan.dll.a 2>&1 | head -1)"
  else
    echo "not executable/found"
  fi
}
show /c/msys64/mingw64/bin/gcc
show /c/msys64/mingw64/bin/clang
show /c/msys64/clang64/bin/clang
show /c/msys64/ucrt64/bin/gcc
show /c/msys64/ucrt64/bin/clang
show /c/msys64/mingw32/bin/gcc
show gcc
show clang
show cc
show arm-none-eabi-gcc
echo
echo "== sanitizer runtime files under msys64 (bounded, dirs only) =="
ls /c/msys64/mingw64/lib/gcc/x86_64-w64-mingw32/*/libasan* /c/msys64/mingw64/lib/libasan* /c/msys64/mingw64/bin/libasan* 2>&1 | head -30
ls /c/msys64/mingw64/lib/gcc/x86_64-w64-mingw32/*/libubsan* /c/msys64/mingw64/lib/libubsan* /c/msys64/mingw64/bin/libubsan* 2>&1 | head -30
ls /c/msys64/clang64/lib/clang/*/lib/windows/*asan* /c/msys64/clang64/lib/clang/*/lib/windows/*ubsan* 2>&1 | head -30
ls /c/msys64/ucrt64/lib/gcc/x86_64-w64-mingw32/*/libasan* /c/msys64/ucrt64/lib/gcc/x86_64-w64-mingw32/*/libubsan* 2>&1 | head -30
} > "$LOG" 2>&1
cat "$LOG"
