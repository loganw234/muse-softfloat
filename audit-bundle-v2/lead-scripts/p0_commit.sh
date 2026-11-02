#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/muse-softfloat || exit 9
git add -A
git status --short | head -50
git commit -F ../scratch/lead/p0-commit-body.txt
echo "commit rc=$?"
git log --format='%H | %aI | %s' -3
git status --porcelain; echo CLEAN_ABOVE
