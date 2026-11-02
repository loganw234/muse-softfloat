#!/bin/bash
# Probe J: binary64 100% worst-case gates (vehicle), with input dumps for
# independent set comparison; classify specials among wc inputs.
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
V=$ROOT/scratch/verifier-w4trig
OR=$ROOT/scratch/oracles/core-math-3b2163bb87c222c7db17a721425fbef31e98fd94/src/binary64
cd "$ROOT" || exit 9
$V/tmp/trigx.exe wc sin $OR/sinpi/sinpi.wc $V/tmp/wc_sin.dump > $V/out/wc_sin.log 2>&1
echo "wc sin rc=$?"
tail -3 $V/out/wc_sin.log
$V/tmp/trigx.exe wc cos $OR/cospi/cospi.wc $V/tmp/wc_cos.dump > $V/out/wc_cos.log 2>&1
echo "wc cos rc=$?"
tail -3 $V/out/wc_cos.log
