#!/usr/bin/env bash
# Git facts for annotations: main first-parent log with dates, parcel branch tips.
WS=/c/Users/logan/source/repos/Muse-Softfloat
cd "$WS/muse-softfloat" || exit 1
echo "=== HEAD ==="
git log --oneline -5
echo "=== 5142594 date ==="
git show -s --format="%H %cI %s" 5142594
git show -s --format="%H %cI %s" 7d0ed81
git show -s --format="%H %cI %s" 4a0b0d4
echo "=== first-parent main log since wave3 close (f458f26..) ==="
git log --first-parent --format="%h %cI %s" f458f26..HEAD | head -100
echo "=== branches ==="
git branch -a --format="%(refname:short) %(objectname:short)"
