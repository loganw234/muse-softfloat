#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
export TMPDIR=$PWD/scratch/lead/tmp
mkdir -p "$TMPDIR"
export TMP="$(cygpath -w "$TMPDIR")" TEMP="$(cygpath -w "$TMPDIR")"
export GIT_CONFIG_COUNT=3
export GIT_CONFIG_KEY_0=safe.directory GIT_CONFIG_VALUE_0=C:/Users/logan/source/repos/Muse-Softfloat/muse-softfloat
export GIT_CONFIG_KEY_1=safe.directory GIT_CONFIG_VALUE_1=C:/Users/logan/source/repos/Muse-Softfloat/worktrees/w1-f32
export GIT_CONFIG_KEY_2=safe.directory GIT_CONFIG_VALUE_2=C:/Users/logan/source/repos/Muse-Softfloat/worktrees/w1-f64
PY=.venv/Scripts/python.exe
PLANT=softfloat-bootstrap-kit/tools/plant.py
BASE=4cdb912dbd5ebda4fa2bc29168883dc4527d4091
$PY scratch/lead/make_drafts.py || exit 1
echo "--- make f32 copy ---"
$PY $PLANT make --repo worktrees/w1-f32 --base $BASE --out worktrees/verify-f32 --key scratch/lead/keys/w1-f32-draft.json
echo make32_rc=$?
echo "--- make f64 copy ---"
$PY $PLANT make --repo worktrees/w1-f64 --base $BASE --out worktrees/verify-f64 --key scratch/lead/keys/w1-f64-draft.json
echo make64_rc=$?
echo "--- dispatch checks ---"
$PY $PLANT check --dispatch --worktree --repo worktrees/verify-f32 --key scratch/lead/keys/key-*.json 2>&1 | head -5 || true
ls scratch/lead/keys/
