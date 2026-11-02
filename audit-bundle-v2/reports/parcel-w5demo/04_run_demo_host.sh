#!/usr/bin/env bash
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w5-demo || exit 9
for f in demo/fetch.sh demo/run_demo.sh; do bash -n "$f" && echo "bash -n OK: $f"; done
python -m py_compile demo/fetch.py demo/make_ias15_extract.py demo/make_kissfft_tree.py demo/compare_ias15.py && echo "py_compile OK"
time bash demo/run_demo.sh host --offline
echo "RUN_DEMO_EXIT=$?"
