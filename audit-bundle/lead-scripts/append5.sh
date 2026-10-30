#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
mkdir -p scratch/lead/tmp
export TMPDIR=$PWD/scratch/lead/tmp
bash softfloat-bootstrap-kit/tools/ledger.sh append ledger lead "Model probe: native spawns inherit lead model; Workflow admits muse-spark-1.3" < scratch/lead/model-probe.txt
echo rc=$?
