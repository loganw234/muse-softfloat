#!/usr/bin/env bash
# Integration re-make: for each merge commit, git merge-tree the two
# parents and compare the resulting tree OID with the merge's tree.
# implemented.tsv conflicts were resolved by union+regen, so xf/str
# merges may differ in generated files only - print the diffstat.
cd /c/Users/logan/source/repos/Muse-Softfloat/muse-softfloat || exit 9
for m in a05412f 71fbd53 d9718cf 1357863 2843792 06fdec8; do
  p1=$(git rev-parse $m^1) p2=$(git rev-parse $m^2)
  want=$(git rev-parse $m^{tree})
  got=$(git merge-tree --write-tree $p1 $p2 2>/dev/null | head -1)
  if [ "$got" = "$want" ]; then
    echo "$m REMAKE-IDENTICAL"
  else
    echo "$m differs (conflict-resolved merge); diffstat vs merge tree:"
    git diff --stat $got $want | tail -6
  fi
done
