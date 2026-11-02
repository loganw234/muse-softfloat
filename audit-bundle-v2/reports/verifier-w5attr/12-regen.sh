#!/usr/bin/env bash
# 12-regen.sh - regeneration determinism: run each pure-python generator's
# directed leg twice, byte-compare; compare against committed sets.
set -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
V="$SCRATCH"
mkdir -p "$V/tmp/rg1" "$V/tmp/rg2"
export TMPDIR="$V/tmp" TMP="$V/tmp" TEMP="$V/tmp"
T="$COPY/tests"
run2() { # $1 = generator base name (no .py)
  "$MSF_PYTHON" "$T/$1.py" directed "$V/tmp/rg1/$1" > "$V/tmp/rg1/$1.log" 2>&1 || { echo "$1 run1 rc=$?"; tail -n 3 "$V/tmp/rg1/$1.log"; return 1; }
  "$MSF_PYTHON" "$T/$1.py" directed "$V/tmp/rg2/$1" > "$V/tmp/rg2/$1.log" 2>&1 || { echo "$1 run2 rc=$?"; tail -n 3 "$V/tmp/rg2/$1.log"; return 1; }
  local ok=1
  for f in "$V/tmp/rg1/$1"/*; do
    b=$(basename "$f")
    if cmp -s "$f" "$V/tmp/rg2/$1/$b"; then :; else echo "$1: TWICE-DIFFERS: $b"; ok=0; fi
    if [ -f "$COPY/tests/vectors/$b" ]; then
      if cmp -s "$f" "$COPY/tests/vectors/$b"; then :; else echo "$1: COMMITTED-DIFFERS: $b"; ok=0; fi
    else
      echo "$1: no committed file for $b"
    fi
  done
  [ $ok -eq 1 ] && echo "$1: twice-identical + committed-match"
}
for g in gen_vectors_str gen_vectors_f16 gen_vectors_f32 gen_vectors_xf; do run2 "$g"; done
echo "== f64 (directed writes fixed names) =="
"$MSF_PYTHON" "$T/gen_vectors_f64.py" directed "$V/tmp/rg1/f64" > "$V/tmp/rg1/f64.log" 2>&1; echo "f64 run1 rc=$?"
"$MSF_PYTHON" "$T/gen_vectors_f64.py" directed "$V/tmp/rg2/f64" > "$V/tmp/rg2/f64.log" 2>&1; echo "f64 run2 rc=$?"
for f in "$V/tmp/rg1/f64"/*; do
  b=$(basename "$f")
  cmp -s "$f" "$V/tmp/rg2/f64/$b" && echo "twice-identical: $b" || echo "TWICE-DIFFERS: $b"
  if [ -f "$COPY/tests/vectors/$b" ]; then cmp -s "$f" "$COPY/tests/vectors/$b" && echo "committed-match: $b" || echo "COMMITTED-DIFFERS: $b"; fi
done
