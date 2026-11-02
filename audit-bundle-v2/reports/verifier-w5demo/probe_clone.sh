#!/usr/bin/env bash
export MSF_PYTHON=python
V=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5demo
echo "=== clone test: real git clone, fetch must refuse on ignore gap ==="
rm -rf "$V/clonetest"
git clone -q /c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify5-demo "$V/clonetest" 2>/dev/null
cd "$V/clonetest" || exit 9
git log --oneline -1
bash demo/fetch.sh --offline > /tmp/probeClone.log 2>&1; echo "CLONE_FETCH_EXIT=$?"
cat /tmp/probeClone.log
echo "=== ls-files third-party sweep in the clone ==="
git ls-files | grep -ciE 'kiss|rebound|extract|cache' ; echo "(count above; 0 = clean)"
git ls-files demo/cache | wc -l
echo "=== disposable repo: ignore-gap vs fixed ==="
rm -rf "$V/ignoretest" && mkdir -p "$V/ignoretest/demo" && cd "$V/ignoretest" || exit 9
git init -q .
cp /c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify5-demo/demo/fetch.sh /c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify5-demo/demo/fetch.py demo/
mkdir -p docs/metrics
cp /c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify5-demo/docs/metrics/fetches.jsonl docs/metrics/
printf '# Demo downloads\n# refuses to run if this path would be.\ndemo/cache2/\n' > .gitignore
git add -A >/dev/null 2>&1
echo "--- with copy's cache2 entry: ---"
bash demo/fetch.sh --offline > /tmp/probeIgn1.log 2>&1; echo "IGNOREGAP_EXIT=$?"; cat /tmp/probeIgn1.log
printf '# Demo downloads\ndemo/cache/\n' > .gitignore
echo "--- with corrected cache entry: ---"
bash demo/fetch.sh --offline > /tmp/probeIgn2.log 2>&1; echo "FIXED_EXIT=$?"; cat /tmp/probeIgn2.log
