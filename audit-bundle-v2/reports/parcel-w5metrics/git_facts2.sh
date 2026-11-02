#!/usr/bin/env bash
# Branch tips (full), per-branch commit dates, merge second parents.
WS=/c/Users/logan/source/repos/Muse-Softfloat
cd "$WS/muse-softfloat" || exit 1
for b in wave4-seam wave4-minmax wave4-interval wave4-trig wave4-kissfft wave5-attr wave5-alg1 wave5-alg2 wave5-exp2 wave5-log2 wave5-aug wave5-site wave5-demo wave5-twiddledoc lead-readme lead-readme2 lead-sf2; do
  echo "=== $b ==="
  git log --format="%H %cI %s" "$b" --not main~60..main 2>/dev/null | head -2
  git log --format="%h %cI %s" -4 "$b"
done
echo "=== merges: second parents ==="
for m in b576c13 75309d4 20bc16b da46f51 32bbd93 6e0f2f2 0de6a30 4a80126 7772da7 cf81644 4a0b0d4 3a09c76 eac88b0 97d1cbe 3a12b71 889ec2e 0918eac; do
  git show -s --format="%h parents:%P %cI %s" "$m"
done
echo "=== key full SHAs ==="
for s in 5142594 4a80126 dfc7a02 8770745 de2d48c 4cdb912 fe213fd 32dac7d; do git rev-parse "$s"; done
echo "=== verify copy HEADs (worktrees) ==="
for w in verify-readme verify-readme2 verify-sf2 verify5-twiddledoc verify4-seam; do
  echo "-- $w"; git -C "$WS/worktrees/$w" log --format="%h %cI %s" -2 2>/dev/null
done
