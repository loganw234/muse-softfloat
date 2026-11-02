#!/bin/bash
# regen.sh - regenerate site JSON in a scratch copy and diff vs committed.
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat
R=scratch/verifier-w5site/regen
rm -rf "$R"
mkdir -p "$R/tests/vectors" "$R/docs/metrics"
cp -r worktrees/verify5-site/site "$R/site"
cp worktrees/verify5-site/tests/msf_dispatch.h "$R/tests/"
cp worktrees/verify5-site/tests/vectors/*.vec "$R/tests/vectors/"
cp worktrees/verify5-site/docs/COVERAGE.tsv "$R/docs/"
cp worktrees/verify5-site/docs/metrics/plants.jsonl "$R/docs/metrics/"
mkdir -p "$R/orig"
cp "$R/site/data.json" "$R/orig/data.json"
cp "$R/site/ops.json" "$R/orig/ops.json"
cp "$R/site/vectors-sample.json" "$R/orig/vectors-sample.json"
python "$R/site/build_data.py"
echo "--- diff data.json ---"
diff "$R/orig/data.json" "$R/site/data.json" && echo IDENTICAL-data
echo "--- diff ops.json ---"
diff -q "$R/orig/ops.json" "$R/site/ops.json" && echo IDENTICAL-ops
echo "--- diff vectors-sample.json ---"
diff -q "$R/orig/vectors-sample.json" "$R/site/vectors-sample.json" && echo IDENTICAL-sample
