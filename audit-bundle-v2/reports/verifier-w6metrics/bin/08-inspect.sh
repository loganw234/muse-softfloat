#!/bin/bash
# Probe 2d/5/6a: commit/branch inspection, coverage list, RECORD tables.
set -u
DUP="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6metrics/dup"
OUT="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6metrics/out"
export MSF_PYTHON="C:/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe"
cd "$DUP"
echo "=== f01dc96 (own-briefs-row base) ==="
git log --oneline -2 f01dc96055f24b4aa5450bdadabf44fa5308abb9 2>&1
git merge-base --is-ancestor f01dc96055f24b4aa5450bdadabf44fa5308abb9 cdc40ae 2>&1 && echo "f01dc96 ancestor-of-base" || echo "f01dc96 NOT-ancestor-of-base"
git merge-base --is-ancestor cdc40ae f01dc96055f24b4aa5450bdadabf44fa5308abb9 2>&1 && echo "base ancestor-of-f01dc96" || echo "base NOT-ancestor-of-f01dc96"
echo "=== ef0215b (fixer commit) recheck ==="
git cat-file -t ef0215b140a0eeb12ea3d4e64113a4ea0421b053 2>&1
git log --all --oneline 2>/dev/null | grep -i ef0215b | head -3
echo "=== branches containing fixer base 0708e2e ==="
git branch -a --contains 0708e2e1a91dd9c1f9a30bf7d7c3fea8ef51ee78 2>&1 | head -5
echo "=== wave6-popups branch tip ==="
git log --oneline -3 wave6-popups 2>&1 | head -5
echo "=== RECORD.md presence ==="
ls docs/RECORD.md 2>&1; grep -n '1,196,128,770\|1196128770\|1,418,065,198' docs/RECORD.md 2>&1 | head -5
