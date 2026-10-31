#!/usr/bin/env bash
# F-01 reproduction: shrink/weaken the committed vector corpus, regenerate manifest + expect-counts from the
# SAME files exactly as tools/run.sh smoke does, and verify. Every step still prints VERDICT: PASS.
# Usage (repo root, runner built as run.sh builds it -> $R):  bash tamper_corpus.sh /path/to/msf_runner.exe
set -u; R=${1:?runner}; T=$(mktemp -d); VECS=$(sed -n 's/^VECS="\(.*\)"$/\1/p' tools/run.sh)
mkdir -p $T/tests/vectors && cp tests/vectors/*.vec $T/tests/vectors/ && cd $T
gate() { sha256sum $VECS > m.txt
  awk '!/^#/ && NF>0 {t=$NF; if (substr(t,length(t))=="\r") t=substr(t,1,length(t)-1); print t}' $VECS | sort | uniq -c | awk '{print $2, $1}' > e.txt
  $R verify --manifest m.txt --expect-counts e.txt $VECS > v.log 2>&1; echo "   rc=$? $(grep -E '^total' v.log|head -1) $(grep -E '^VERDICT' v.log|head -1)"; }
echo "A. untouched";                gate
n=$(wc -l < tests/vectors/aug-f64.vec); head -n $((n/10)) tests/vectors/aug-f64.vec > x && cp x tests/vectors/aug-f64.vec
echo "B. 10% of aug-f64.vec kept";  gate
grep '^#' tests/vectors/trig-f64.vec > x && cp x tests/vectors/trig-f64.vec
echo "C. trig-f64.vec emptied";     gate
awk 'NR>4 && NR<=3995 && !/^#/ {print "# " $0; next} {print}' tests/vectors/arith-f32.vec > x && cp x tests/vectors/arith-f32.vec
echo "D. 3,991 arith-f32 lines commented out"; gate
