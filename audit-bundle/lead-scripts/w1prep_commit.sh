#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/muse-softfloat || exit 9
git add -A
git status --short | head -40
git commit -F ../scratch/lead/w1prep-body.txt
echo "commit rc=$?"
git log --format='%H | %s' -2
git status --porcelain; echo CLEAN_ABOVE
