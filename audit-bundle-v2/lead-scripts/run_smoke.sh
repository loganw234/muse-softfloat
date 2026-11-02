#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/muse-softfloat || exit 9
bash tools/run.sh smoke
echo "SMOKE_RC=$?"
