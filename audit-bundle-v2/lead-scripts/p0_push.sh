#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/muse-softfloat || exit 9
git add tests/runner.c tools/run.sh
git commit -F ../scratch/lead/p0-fix-body.txt
echo "commit rc=$?"
git log --format='%H | %s' -3
