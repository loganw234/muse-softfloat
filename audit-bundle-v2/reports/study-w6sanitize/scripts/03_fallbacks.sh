#!/usr/bin/env bash
# Probe 1b: MSVC presence, pacman install routes, trap-on-error UBSan,
# docker / WSL reachability. Read-only except canary builds in scratch.
set -u
cd "$(dirname "$0")/.." || exit 9
mkdir -p logs tmp canary/bin
export TMPDIR=$PWD/tmp
export TMP="$(cygpath -w "$TMPDIR" 2>/dev/null || echo "$TMPDIR")"
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
LOG=logs/03_fallbacks.log
: > "$LOG"
say() { echo "$@" >> "$LOG"; }

say "===== MSVC via vswhere ====="
VSWHERE="/c/Program Files (x86)/Microsoft Visual Studio/Installer/vswhere.exe"
if [ -x "$VSWHERE" ]; then
  "$VSWHERE" -all -products '*' -property installationPath >> "$LOG" 2>&1
  "$VSWHERE" -all -products '*' -property displayName >> "$LOG" 2>&1
  "$VSWHERE" -latest -products '*' -find 'VC/Tools/MSVC/*/bin/Hostx64/x64/cl.exe' >> "$LOG" 2>&1
else
  say "vswhere absent"
fi
say
say "===== msys clang64/ucrt64 dir contents ====="
ls -la /c/msys64/clang64/bin >> "$LOG" 2>&1
ls -la /c/msys64/ucrt64/bin >> "$LOG" 2>&1
say
say "===== pacman installed gcc/clang/llvm packages ====="
pacman -Q > logs/pacman-Q.txt 2>&1
grep -E 'gcc|clang|llvm|compiler-rt|sanit' logs/pacman-Q.txt >> "$LOG" 2>&1 || say "(none matched)"
say "pacman -Q total packages: $(wc -l < logs/pacman-Q.txt)"
say
say "===== pacman available (local sync db, no network sync) ====="
pacman -Ss 'sanitizer|compiler-rt' > logs/pacman-Ss-sanit.txt 2>&1
say "--- -Ss sanitizer|compiler-rt (exit $?) ---"
head -20 logs/pacman-Ss-sanit.txt >> "$LOG"
pacman -Ss 'mingw-w64-clang-x86_64-clang ' > logs/pacman-Ss-clang.txt 2>&1
say "--- -Ss mingw-w64-clang-x86_64-clang (exit $?) ---"
head -10 logs/pacman-Ss-clang.txt >> "$LOG"
pacman -Si mingw-w64-x86_64-gcc > logs/pacman-Si-gcc.txt 2>&1
say "--- -Si mingw-w64-x86_64-gcc (exit $?) first lines ---"
grep -E '^(Name|Version|Depends On)' logs/pacman-Si-gcc.txt >> "$LOG" 2>&1
say
say "===== trap-on-error UBSan (mingw64 gcc, no libubsan needed?) ====="
GCC=/c/msys64/mingw64/bin/gcc
for variant in "trap:-fsanitize=undefined -fsanitize-undefined-trap-on-error -fno-sanitize-recover=all" "minimal:-fsanitize=undefined -fsanitize-minimal-runtime -fno-sanitize-recover=all"; do
  vname="${variant%%:*}"; vflags="${variant#*:}"
  say "--- variant $vname : $vflags ---"
  for prog in clean heap ub ub_shift; do
    exe="canary/bin/mingw64-${vname}-${prog}.exe"
    clog="canary/bin/mingw64-${vname}-${prog}.build.log"
    rlog="canary/bin/mingw64-${vname}-${prog}.run.log"
    if $GCC -std=c11 -O1 -g $vflags "canary/${prog}.c" -o "$exe" > "$clog" 2>&1; then
      case "$prog" in
        heap) timeout 30 "$exe" 64 > "$rlog" 2>&1 ;;
        ub_shift) timeout 30 "$exe" 40 > "$rlog" 2>&1 ;;
        *) timeout 30 "$exe" > "$rlog" 2>&1 ;;
      esac
      rc=$?
      say "RUN exit=$rc $prog :: $(head -3 "$rlog" | tr '\n' ' ' | cut -c1-200)"
    else
      say "BUILD-FAIL $prog :: $(head -2 "$clog" | tr '\n' ' ' | cut -c1-200)"
    fi
  done
done
say
say "===== docker / wsl reachability (bounded) ====="
timeout 25 docker info --format 'server={{.ServerVersion}} os={{.OSType}}' >> "$LOG" 2>&1
say "docker info exit=$?"
timeout 25 docker images --format '{{.Repository}}:{{.Tag}} {{.ID}}' >> "$LOG" 2>&1
say "docker images exit=$?"
timeout 25 wsl.exe -l -v >> "$LOG" 2>&1
say "wsl -l -v exit=$?"
cat "$LOG"
