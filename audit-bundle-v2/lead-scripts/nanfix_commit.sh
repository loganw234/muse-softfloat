#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/muse-softfloat || exit 9
git add src/msf_decode.h
git commit -F ../scratch/lead/nanfix-body.txt
echo "commit rc=$?"
git log --format='%H | %s' -2
git show --stat HEAD | tail -3
