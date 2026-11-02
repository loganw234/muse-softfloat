#!/usr/bin/env bash
# Probe 1 canaries: compile AND run, for each candidate compiler x flag set.
# Verdict per cell comes from observed exit codes + sanitizer text in logs.
set -u
cd "$(dirname "$0")/.." || exit 9
mkdir -p logs tmp canary/bin
export TMPDIR=$PWD/tmp
export TMP="$(cygpath -w "$TMPDIR" 2>/dev/null || echo "$TMPDIR")"
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
LOG=logs/02_canaries.log
: > "$LOG"

CANDIDATES="mingw64-gcc:/c/msys64/mingw64/bin/gcc mingw32-gcc:/c/msys64/mingw32/bin/gcc miniconda-gcc:/c/Users/logan/AppData/Local/Programs/Miniconda3/Library/mingw-w64/bin/gcc"
FLAGSETS="both:-fsanitize=address,undefined asan:-fsanitize=address ubsan:-fsanitize=undefined"
PROGS="clean heap ub ub_shift"

for cand in $CANDIDATES; do
  name="${cand%%:*}"; cc="${cand#*:}"
  {
    echo "===== CANDIDATE $name : $cc ====="
    if [ ! -x "$cc" ]; then echo "ABSENT: $cc not executable"; echo; continue; fi
    "$cc" --version 2>&1 | head -1
    echo "dumpmachine=$("$cc" -dumpmachine 2>&1 | head -1)"
    for fs in $FLAGSETS; do
      fname="${fs%%:*}"; flags="${fs#*:}"
      echo "--- flagset $fname : $flags -fno-sanitize-recover=all ---"
      for prog in $PROGS; do
        exe="canary/bin/${name}-${fname}-${prog}.exe"
        clog="canary/bin/${name}-${fname}-${prog}.build.log"
        rlog="canary/bin/${name}-${fname}-${prog}.run.log"
        if "$cc" -std=c11 -O1 -g $flags -fno-sanitize-recover=all "canary/${prog}.c" -o "$exe" > "$clog" 2>&1; then
          echo "BUILD-OK  $prog"
        else
          rc=$?
          echo "BUILD-FAIL($rc) $prog :: $(head -2 "$clog" | tr '\n' ' ')"
          continue
        fi
        case "$prog" in
          heap) timeout 30 "$exe" 64 > "$rlog" 2>&1 ;;
          ub_shift) timeout 30 "$exe" 40 > "$rlog" 2>&1 ;;
          *) timeout 30 "$exe" > "$rlog" 2>&1 ;;
        esac
        rc=$?
        first=$(head -3 "$rlog" | tr '\n' ' ' | cut -c1-220)
        echo "RUN exit=$rc $prog :: $first"
      done
    done
    # unsanitized control: heap/ub should run (or crash without sanitizer text)
    echo "--- flagset none (control) ---"
    for prog in clean heap ub; do
      exe="canary/bin/${name}-none-${prog}.exe"
      clog="canary/bin/${name}-none-${prog}.build.log"
      rlog="canary/bin/${name}-none-${prog}.run.log"
      if "$cc" -std=c11 -O1 -g "canary/${prog}.c" -o "$exe" > "$clog" 2>&1; then
        case "$prog" in heap) timeout 30 "$exe" 64 > "$rlog" 2>&1 ;; *) timeout 30 "$exe" > "$rlog" 2>&1 ;; esac
        rc=$?
        echo "RUN exit=$rc $prog :: $(head -2 "$rlog" | tr '\n' ' ' | cut -c1-160)"
      else
        echo "BUILD-FAIL control $prog :: $(head -2 "$clog" | tr '\n' ' ')"
      fi
    done
    echo
  } >> "$LOG" 2>&1
done

{
echo "===== OTHER ROUTES ====="
for c in zig tcc docker wsl; do
  if command -v "$c" >/dev/null 2>&1; then echo "FOUND $c -> $(command -v "$c")"; else echo "absent-on-PATH $c"; fi
done
ls "/c/Program Files (x86)/Microsoft Visual Studio/Installer/vswhere.exe" 2>&1 | head -1
ls /c/msys64/clang64/bin /c/msys64/ucrt64/bin 2>&1 | head -4
} >> "$LOG" 2>&1
cat "$LOG"
