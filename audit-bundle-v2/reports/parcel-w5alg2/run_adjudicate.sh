#!/usr/bin/env bash
set -u
WS=/c/Users/logan/source/repos/Muse-Softfloat
S="$WS/scratch/parcel-w5alg2"
echo "MPFR decider on the disagreement samples (tp is 3rd pair):"
"$S/out/alg_decider.exe" decide < "$S/out/adjudicate_in.txt"
