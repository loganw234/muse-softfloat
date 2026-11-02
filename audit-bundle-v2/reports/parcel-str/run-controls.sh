#!/usr/bin/env bash
set -u
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
W=$ROOT/worktrees/w3-str
S=$ROOT/scratch/parcel-str
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export TMPDIR=$S/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-str\tmp'
export TEMP="$TMP"
cd "$W" || exit 9
R=build/str/msf_runner.exe
mkdir -p "$S/controls"
"$R" verify tests/vectors/from-decimal-str.vec tests/vectors/from-hex-str.vec tests/vectors/to-decimal-str.vec tests/vectors/to-hex-str.vec > "$S/directed3.log" 2>&1
echo "trimmed directed rc=$?"
grep -E '^(total|VERDICT)' "$S/directed3.log"

# regen byte-identity: regenerate directed + tables and compare
sha256sum tests/vectors/*str*.vec > "$S/controls/vec-hash1.txt"
../.venv/Scripts/python.exe tests/gen_vectors_str.py directed tests/vectors > /dev/null 2>&1
sha256sum tests/vectors/*str*.vec > "$S/controls/vec-hash2.txt"
if cmp -s "$S/controls/vec-hash1.txt" "$S/controls/vec-hash2.txt"; then echo "regen vectors: byte-identical"; else echo "regen vectors: DIFFER"; fi

# control A: one flipped expected OUTPUT digit in a committed vector
awk 'BEGIN{d=0} /^msf64_to_decimal/ && !d { sub(/OUT=[0-9]/, "OUT=9", $0); d=1 } {print}' tests/vectors/to-decimal-str.vec > "$S/controls/flip-digit.vec"
"$R" verify "$S/controls/flip-digit.vec" > "$S/controls/flip-digit.log" 2>&1
echo "control flip-digit rc=$? (want nonzero)"
grep -m1 '^FAIL' "$S/controls/flip-digit.log" | cut -c1-160

# control B: one wrong consumed expectation (C=n -> C=n+1)
awk 'BEGIN{d=0} /^msf64_from_decimal/ && !d { if (match($0, /C=[0-9]+/)) { v=substr($0, RSTART+2, RLENGTH-2); sub(/C=[0-9]+/, "C=" (v+1), $0) } d=1 } {print}' tests/vectors/from-decimal-str.vec > "$S/controls/wrong-c.vec"
"$R" verify "$S/controls/wrong-c.vec" > "$S/controls/wrong-c.log" 2>&1
echo "control wrong-C rc=$? (want nonzero)"
grep -m1 '^FAIL' "$S/controls/wrong-c.log" | cut -c1-200

# control C: truncating mutant - scratch copy of msf_string.c with the
# ties/directed decisions replaced by toward-zero in dec_round_inc
# and a forced tz pack for from_decimal, i.e. parse never increments.
cp src/msf_string.c "$S/controls/msf_string_orig.c"
cp src/msf_string.c "$S/controls/msf_string_mut.c"
echo "mutant setup done"
