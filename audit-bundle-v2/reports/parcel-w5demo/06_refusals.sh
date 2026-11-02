#!/usr/bin/env bash
set -u
WS=/c/Users/logan/source/repos/Muse-Softfloat
T=$WS/scratch/parcel-w5demo/refusal-test
rm -rf "$T"
mkdir -p "$T"
git clone -q --no-hardlinks "$WS/worktrees/w5-demo" "$T/repo" 2>/dev/null \
  || git -c safe.directory='*' clone -q --no-hardlinks "$WS/worktrees/w5-demo" "$T/repo"
cd "$T/repo" || exit 9
git checkout -q wave5-demo 2>/dev/null || true
echo "clone HEAD: $(git log -1 --oneline)"

echo "===== R1: tracked file under demo/cache must refuse ====="
mkdir -p demo/cache/archives
echo dummy > demo/cache/archives/dummy.txt
git add -f demo/cache/archives/dummy.txt
bash demo/fetch.sh --offline; echo "R1_EXIT=$? (want non-zero)"
git rm -q --cached demo/cache/archives/dummy.txt
rm -rf demo/cache

echo "===== R2: gitignore entry removed must refuse ====="
sed -i '/^demo\/cache\/$/d' .gitignore
grep -c 'demo/cache' .gitignore || echo "(entry gone)"
bash demo/fetch.sh --offline; echo "R2_EXIT=$? (want non-zero)"
git checkout -q .gitignore

echo "===== R3: clean checkout offline-empty fails on archive, not on ignore ====="
bash demo/fetch.sh --offline; echo "R3_EXIT=$? (want 1, archive-missing message above)"
echo "REFUSALS DONE"
