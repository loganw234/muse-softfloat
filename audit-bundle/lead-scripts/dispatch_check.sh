#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
export TMPDIR=$PWD/scratch/lead/tmp
export GIT_CONFIG_COUNT=4
export GIT_CONFIG_KEY_0=safe.directory GIT_CONFIG_VALUE_0=C:/Users/logan/source/repos/Muse-Softfloat/worktrees/verify-f32
export GIT_CONFIG_KEY_1=safe.directory GIT_CONFIG_VALUE_1=C:/Users/logan/source/repos/Muse-Softfloat/worktrees/verify-f64
export GIT_CONFIG_KEY_2=safe.directory GIT_CONFIG_VALUE_2=C:/Users/logan/source/repos/Muse-Softfloat/worktrees/w1-f32
export GIT_CONFIG_KEY_3=safe.directory GIT_CONFIG_VALUE_3=C:/Users/logan/source/repos/Muse-Softfloat/worktrees/w1-f64
PY=.venv/Scripts/python.exe
PLANT=softfloat-bootstrap-kit/tools/plant.py
$PY $PLANT check --dispatch --repo worktrees/w1-f32 --copy worktrees/verify-f32 --key scratch/lead/keys/key-1779df0.json --sha256 71ef8ff19d0520f2a01ac12b763117756b31de413c52b1e9ad9c6e4f942e1aac
echo check32_rc=$?
$PY $PLANT check --dispatch --repo worktrees/w1-f64 --copy worktrees/verify-f64 --key scratch/lead/keys/key-d1e9442.json --sha256 e6bbc65c59fdd1e1ee1e25b1954562e97782143b7b01f1e075af4062964d3f01
echo check64_rc=$?
