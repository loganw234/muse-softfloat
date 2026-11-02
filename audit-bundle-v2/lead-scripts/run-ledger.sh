#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
mkdir -p scratch/lead/tmp
export TMPDIR=$PWD/scratch/lead/tmp
echo "--- grep test on body ---"
grep -c '^Measured:' scratch/lead/seed-phase0.txt || echo "grep Measured failed rc=$?"
grep -c '^Believed:' scratch/lead/seed-phase0.txt || echo "grep Believed failed rc=$?"
grep -c '^For:' scratch/lead/seed-phase0.txt || echo "grep For failed rc=$?"
wc -l scratch/lead/seed-phase0.txt
echo "--- ledger append ---"
bash softfloat-bootstrap-kit/tools/ledger.sh append ledger lead "Phase 0 seeded: environment facts, kit route, known plant.py limit" < scratch/lead/seed-phase0.txt
echo "ledger rc=$?"
ls -l ledger/
head -6 ledger/lead.md 2>/dev/null
