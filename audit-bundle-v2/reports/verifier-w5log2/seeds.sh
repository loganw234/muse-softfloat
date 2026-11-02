#!/usr/bin/env bash
# seeds.sh - small seeded sweeps, own decider, all formats x log pair.
set -u
export PATH=/c/msys64/mingw64/bin:$PATH
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5log2
ulimit -v 4194304
cd "$SCR" || exit 9
./build/vlog2.exe seed f64 log2 12345 20000 seed-f64-log2 > logs/seed1.log 2>&1
tail -1 logs/seed1.log
./build/vlog2.exe seed f64 log2p1 99991 20000 seed-f64-log2p1 > logs/seed2.log 2>&1
tail -1 logs/seed2.log
./build/vlog2.exe seed f32 log2 777 20000 seed-f32-log2 > logs/seed3.log 2>&1
tail -1 logs/seed3.log
./build/vlog2.exe seed f32 log2p1 31337 20000 seed-f32-log2p1 > logs/seed4.log 2>&1
tail -1 logs/seed4.log
