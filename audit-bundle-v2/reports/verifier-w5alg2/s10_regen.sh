#!/usr/bin/env bash
# s10_regen.sh - regeneration gate: vector regeneration (expect the
# generator's exact-py/MPFR cross-decision to refuse) and table
# regeneration drift (gen_tables.py into tmp, diffed, never applied).
set -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export MSF_PYTHON="${MSF_PYTHON:-$(pwd)/.venv/Scripts/python.exe}"
export TMPDIR="$(pwd)/scratch/verifier-w5alg2/tmp"
export TMP="$TMPDIR" TEMP="$TMPDIR"
mkdir -p "$TMPDIR" scratch/verifier-w5alg2/out
ulimit -v 2097152
OUT=scratch/verifier-w5alg2/out
COPY=worktrees/verify5-alg2
{
echo "--- vector regeneration attempt 1 ---"
export MSF_ALG_DECIDER="$(pwd)/$OUT/alg_decider.exe"
rm -rf "$TMPDIR/regen1" && mkdir -p "$TMPDIR/regen1"
(cd $COPY && $MSF_PYTHON tests/gen_vectors_alg.py "$TMPDIR/regen1") > $OUT/s10_regen1.log 2>&1
echo "rc=$?"
tail -5 $OUT/s10_regen1.log
echo "--- vector regeneration attempt 2 (byte-stability is moot if 1 refuses) ---"
rm -rf "$TMPDIR/regen2" && mkdir -p "$TMPDIR/regen2"
(cd $COPY && $MSF_PYTHON tests/gen_vectors_alg.py "$TMPDIR/regen2") > $OUT/s10_regen2.log 2>&1
echo "rc=$?"
tail -3 $OUT/s10_regen2.log
echo "--- table regeneration drift ---"
rm -rf "$TMPDIR/gen-check" && mkdir -p "$TMPDIR/gen-check"
(cd $COPY && $MSF_PYTHON tools/gen_tables.py "$TMPDIR/gen-check") > $OUT/s10_gen.log 2>&1
echo "gen rc=$?"
for f in include/muse_softfloat.h src/msf_formats.h tests/msf_dispatch.h docs/COVERAGE.tsv; do
  if cmp -s "$COPY/$f" "$TMPDIR/gen-check/$f"; then
    echo "IDENTICAL $f"
  else
    echo "DRIFT $f"
  fi
done
echo "--- tier inventory (run.sh logic, committed COVERAGE) ---"
awk -F '\t' -v t1exp="783" -v t2exp="45" '
  /^#/ { next }
  !hdr { for (i = 1; i <= NF; i++) col[$i] = i; hdr = 1; next }
  { tier = $(col["tier"]); status = $(col["status"]); claim = $(col["claim"])
    if (status != "implemented" && status != "planned") bad++
    if (tier == "1") { t1++; if (status == "implemented") t1i++
      if (claim != "required") bad++ }
    else if (tier == "2") { t2++; if (status == "implemented") t2i++
      else if (status == "planned") t2p++
      if (claim != "C-754") bad++ }
    else bad++ }
  END { printf "tier1 %d/%d tier2 impl %d planned %d reg %d bad %d\n",
    t1i, t1, t2i, t2p, t2, bad }' $COPY/docs/COVERAGE.tsv
grep -c "hypot" $COPY/docs/COVERAGE.tsv
grep "hypot" $COPY/tables/implemented.tsv || echo "implemented.tsv: NO hypot rows"
} 2>&1 | tee $OUT/s10_regen.log
