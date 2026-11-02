#!/bin/bash
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 1
grep -n "B1 S" scratch/verifier-sf0/report.md
grep -n "Auditor-disposition" scratch/verifier-sf0/report.md
grep -n "What was not done" scratch/verifier-sf0/report.md
grep -n "N15" scratch/verifier-sf0/report.md
grep -n "N1 S12" scratch/verifier-sf0/report.md
