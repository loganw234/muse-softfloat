#!/usr/bin/env bash
set -uo pipefail
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR="$ROOT/scratch/parcel-xf/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-xf\tmp'
export TEMP="$TMP"
cd "$ROOT/worktrees/w2-xf" || exit 9
bash tools/run.sh standard > "$ROOT/scratch/parcel-xf/logs/19_standard_full.log" 2>&1
echo "standard exit=$?"
grep -E '^(total|VERDICT|budget|drift|type scan|symbol scan|negative|file build)' "$ROOT/scratch/parcel-xf/logs/19_standard_full.log"
G="git -c safe.directory=$PWD"
echo "== changed files vs base dd48b08 =="
$G diff --stat dd48b08..HEAD
echo "== hand-written line count (src + gen, insertions+deletions) =="
$G diff --numstat dd48b08..HEAD -- src/msf32.c src/msf64.c tests/gen_vectors_xf.py
echo "== implemented.tsv diff shape =="
$G diff --numstat dd48b08..HEAD -- tables/implemented.tsv
echo "== status =="
$G status --porcelain
$G log --oneline dd48b08..HEAD
