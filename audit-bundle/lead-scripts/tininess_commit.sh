#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/muse-softfloat || exit 9
git add src/msf_roundpack.c tests/gen_vectors.py tests/berkeley_ingest.py tests/vectors/pack64.vec tests/vectors/pack32.vec tests/vectors/pack16.vec
git status --short | head -20
git commit -F ../scratch/lead/tininess-fix-body.txt
echo "commit rc=$?"
git log --format='%H | %s' -2
git status --porcelain; echo DONE_ABOVE
