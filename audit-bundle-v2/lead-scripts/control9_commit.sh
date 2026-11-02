#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/muse-softfloat || exit 9
git add tools/run.sh tables/implemented.tsv
git commit -F ../scratch/lead/control9-body.txt
echo "commit rc=$?"
git log --format='%H | %s' -3
