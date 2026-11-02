#!/usr/bin/env bash
# 09_reaudit.sh - rerun refined audit on baseline + positive counterparts.
set -u
VROOT="/c/Users/logan/source/repos/Muse-Softfloat"
OUT="$VROOT/scratch/verifier-w4interval"
export MSF_PYTHON="/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe"
for t in base p1 m3; do
  if [ "$t" = base ]; then
    H="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w4interval/build/host_out.txt"
  else
    H="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w4interval/mut/${t}.txt"
  fi
  "$MSF_PYTHON" "C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w4interval/03_audit.py" "$H" "$t-refined" 2>&1 | tee "$OUT/mut/audit_${t}.txt"
done
echo "--- P1 SUMMARY + hash ---"
grep -E "SUMMARY|HOST_SHA256" "$OUT/mut/p1.txt" | cut -c1-160
