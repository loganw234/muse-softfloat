#!/usr/bin/env bash
export MSF_HOST_CC=/c/msys64/mingw64/bin/gcc MSF_PYTHON=python
F=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5demo/fresh
cd "$F" || exit 9
cp demo/expected-ias15.txt /tmp/exp-ias15.good
cp demo/expected-kissfft.txt /tmp/exp-kf.good
sed -i 's/^2000 5d4530a668d360897477a63f90dfb0f7c86b33eb3e462f5a464028d083f48abb /2000 4d4530a668d360897477a63f90dfb0f7c86b33eb3e462f5a464028d083f48abb /' demo/expected-ias15.txt
sed -i 's/^KF 256 complex fwd 27f34c36d864da235da695fcc5778ce0e4f9212f7852882eaefc8be09e36067e$/KF 256 complex fwd 27f34c36d864da235da695fcc5778ce0e4f9212f7852882eaefc8be09e36067d/' demo/expected-kissfft.txt
grep -c '^2000 4d4530a6' demo/expected-ias15.txt
grep -c '36067d$' demo/expected-kissfft.txt
bash demo/run_demo.sh board --offline > /tmp/probeGreen.log 2>&1
echo "GREEN_EXIT=$?"
grep -E 'SHIMOPS|steps_compared|12/12|rows=|summary|IAS15 |KissFFT|interval |demo (host|board)|REFUSED|missing|lock|flash' /tmp/probeGreen.log | head -30
tail -3 /tmp/probeGreen.log
ls /tmp/probeGreen.log
find /c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5demo -name 'board.lock' 2>/dev/null; echo "LOCK_SWEEP_DONE"
cp /tmp/exp-ias15.good demo/expected-ias15.txt
cp /tmp/exp-kf.good demo/expected-kissfft.txt
echo "expected files restored to copy state"
