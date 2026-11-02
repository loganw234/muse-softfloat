#!/usr/bin/env bash
set -u
WS=/c/Users/logan/source/repos/Muse-Softfloat
WT=$WS/worktrees/w5-demo
export TMPDIR=$WS/scratch/parcel-w5demo/tmp
mkdir -p "$TMPDIR"
cd "$WT" || exit 9
echo "== git check-ignore sanity =="
git check-ignore -v demo/cache/probe || echo "check-ignore says NOT ignored"
git ls-files -- demo/cache | head -3
echo "== offline, empty cache (must fail) =="
rm -rf demo/cache
bash demo/fetch.sh --offline; echo "exit=$?"
echo "== seed archives from scratch pins, offline (must pass) =="
mkdir -p demo/cache/archives
cp "$WS/scratch/ias15/work/rebound-262a9cce102c69ca2cf7f3c6c1264e5e60002b7d.tar.gz" demo/cache/archives/
cp "$WS/scratch/tier2-kissfft/kissfft-131.2.0.tar.gz" demo/cache/archives/
sha256sum demo/cache/archives/*
bash demo/fetch.sh --offline; echo "exit=$?"
echo "== extracted layout =="
ls demo/cache/src demo/cache/src/rebound/src/integrator_ias15.c demo/cache/src/kissfft/kiss_fft.c
echo "== rerun offline (idempotent) =="
bash demo/fetch.sh --offline; echo "exit=$?"
echo "FETCH-TEST DONE"
