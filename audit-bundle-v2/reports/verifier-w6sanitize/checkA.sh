#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6sanitize || exit 9
echo "--- probeA.log tail ---"
tail -5 probeA.log
echo "--- verify.log verdict ---"
grep -E "VERDICT|total" dup/build/standard/verify.log
echo "--- verify-standard.log ---"
grep -E "VERDICT|total" dup/build/standard/verify-standard.log
echo "--- aug pool ---"
grep -E "VERDICT" dup/build/standard/aug-pool.log
echo "--- controls ---"
grep -E "control|refused|SKIP" probeA.log | head -25
