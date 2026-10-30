#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
mkdir -p scratch/lead/tmp
export TMPDIR=$PWD/scratch/lead/tmp
export GIT_CONFIG_COUNT=3
export GIT_CONFIG_KEY_0=safe.directory GIT_CONFIG_VALUE_0=C:/Users/logan/source/repos/Muse-Softfloat/worktrees/verify-f32
export GIT_CONFIG_KEY_1=safe.directory GIT_CONFIG_VALUE_1=C:/Users/logan/source/repos/Muse-Softfloat/worktrees/verify-f64
export GIT_CONFIG_KEY_2=safe.directory GIT_CONFIG_VALUE_2=C:/Users/logan/source/repos/Muse-Softfloat/muse-softfloat
bash softfloat-bootstrap-kit/tools/ledger.sh append ledger lead "Planted verification copies built for Wave 1 (key hashes recorded)" < scratch/lead/plant_keys.txt
echo ledger_rc=$?
.venv/Scripts/python.exe softfloat-bootstrap-kit/tools/plant.py check --help 2>&1 | head -25
