#!/usr/bin/env bash
# 17_run.sh - seam census: counts/claims/dispatch-trace/regen/controls.
# Never writes into the copy: regeneration goes to out/ tmp dirs.
set -u
export PATH=/mingw64/bin:/usr/bin:$PATH
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
COPY=$ROOT/worktrees/verify5-alg1
VDIR=$ROOT/scratch/verifier-w5alg1
OUT=$VDIR/out
PY=$ROOT/.venv/Scripts/python.exe
mkdir -p "$OUT"
cd "$ROOT" || exit 9
echo "--- counts / claims / inventory ---"
$PY -u "$VDIR/17_seam.py"
echo "--- math_bin dispatch trace (hypot rows must carry NULL call) ---"
grep -h "hypot" "$COPY/tests/msf_dispatch.h"
echo "--- hypot runner behavior: planned rows SKIP by name ---"
printf 'msf16_hypot te 3c00 3c00 -> 3c00 00 probe:planned\n' > "$OUT/hypot_probe.vec"
"$OUT/msf_runner.exe" verify "$OUT/hypot_probe.vec"
echo "runner exit on planned hypot line: $?"
echo "--- unknown sig token refused ---"
$PY -u "$VDIR/17_unknown_sig.py"
echo "--- regenerate gen_tables twice: byte-identical + match committed ---"
rm -rf "$OUT/regen1" "$OUT/regen2"
MSF_PYTHON=$PY $PY "$COPY/tools/gen_tables.py" "$OUT/regen1" > "$OUT/regen1.log" 2>&1 || { tail -5 "$OUT/regen1.log"; exit 1; }
MSF_PYTHON=$PY $PY "$COPY/tools/gen_tables.py" "$OUT/regen2" > "$OUT/regen2.log" 2>&1 || { tail -5 "$OUT/regen2.log"; exit 1; }
for f in include/muse_softfloat.h src/msf_formats.h tests/msf_dispatch.h docs/COVERAGE.tsv; do
  cmp -s "$OUT/regen1/$f" "$OUT/regen2/$f" || { echo "REGEN NOT BYTE-IDENTICAL: $f"; exit 1; }
  cmp -s "$COPY/$f" "$OUT/regen1/$f" || { echo "REGEN DRIFT vs committed: $f"; exit 1; }
  echo "regen stable+clean: $f"
done
echo "--- copy tree still clean (no verifier writes inside) ---"
git -C "$COPY" status --short | head -5
echo "seam script done"
