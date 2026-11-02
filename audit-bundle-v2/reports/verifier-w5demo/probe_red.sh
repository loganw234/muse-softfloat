#!/usr/bin/env bash
export MSF_HOST_CC=/c/msys64/mingw64/bin/gcc MSF_PYTHON=python
F=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5demo/fresh
cd "$F" || exit 9
cp demo/expected-interval.txt /tmp/expected-interval.good
sed -i 's/^HOST_SHA256 ce81d66e9b0b0a4b654c4eb82664417780c6f09c3f866901002b286980ba9aec$/HOST_SHA256 ce81d66e9b0b0a4b654c4eb82664417780c6f09c3f866901002b286980ba9aed/' demo/expected-interval.txt
grep '^HOST_SHA256' demo/expected-interval.txt
bash demo/run_demo.sh host --offline > /tmp/probeA.log 2>&1
echo "PROBE_A_EXIT=$?"
grep -A4 'summary (host)' /tmp/probeA.log
tail -1 /tmp/probeA.log
cp /tmp/expected-interval.good demo/expected-interval.txt
echo "expected-interval.txt restored"
