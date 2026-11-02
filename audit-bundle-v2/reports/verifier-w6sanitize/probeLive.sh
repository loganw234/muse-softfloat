#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6sanitize/dup || exit 9
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
mkdir -p ../live/plain ../live/traperr
CFLAGS="-std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off"
echo "--- plain builds (no sanitizer flags) ---"
for c in clean ub ub_shift heap heap_far; do
  args=""
  if [ "$c" = ub_shift ]; then args="40"; fi
  if [ "$c" = heap ]; then args="64"; fi
  if [ "$c" = heap_far ]; then args="8 64"; fi
  gcc $CFLAGS "tests/sanitize_canary_${c}.c" -o "../live/plain/${c}.exe" 2> "../live/plain/${c}-build.log" || { echo "$c plain BUILD FAIL"; continue; }
  "../live/plain/${c}.exe" $args > "../live/plain/${c}.log" 2>&1
  echo "$c plain: rc=$? out=[$(cat ../live/plain/${c}.log)]"
done
echo "--- traperr builds (-fsanitize-undefined-trap-on-error, NOT file flags; link check) ---"
for c in clean ub ub_shift heap heap_far; do
  args=""
  if [ "$c" = ub_shift ]; then args="40"; fi
  if [ "$c" = heap ]; then args="64"; fi
  if [ "$c" = heap_far ]; then args="8 64"; fi
  gcc $CFLAGS -fsanitize-undefined-trap-on-error "tests/sanitize_canary_${c}.c" -o "../live/traperr/${c}.exe" 2> "../live/traperr/${c}-build.log" || { echo "$c traperr BUILD FAIL: $(cat ../live/traperr/${c}-build.log)"; continue; }
  "../live/traperr/${c}.exe" $args > "../live/traperr/${c}.log" 2>&1
  echo "$c traperr: rc=$? out=[$(cat ../live/traperr/${c}.log)]"
done
