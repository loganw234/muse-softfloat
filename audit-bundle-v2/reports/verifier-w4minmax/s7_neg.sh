#!/usr/bin/env bash
# verifier-w4minmax s7: own negative controls (scratch vector copies),
# fixed-runner experiment (scratch only), misc checks.
set -u
COPY=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify4-minmax
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w4minmax
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
OUT=$SCR/out-neg
mkdir -p "$OUT/ctrl"
cd "$COPY" || exit 9
R=build/smoke/msf_runner.exe
echo "== misc: Unmatched-paren quirk source =="
grep -n 'Unmatched' "$SCR/out-smoke/standard.log" | head -3
grep -c 'Unmatched' build/standard/*.log 2>/dev/null | head
grep -n 'Unmatched' "$SCR/out-smoke/smoke.log" | head -3
echo "== misc: implemented.tsv wave column =="
git diff 8578114 HEAD -- tables/implemented.tsv | grep '^+[^+]' | awk -F'\t' '{print $NF}' | sort | uniq -c
echo "== misc: mpfr availability =="
"$MSF_PYTHON" -c "import gmpy2; print('gmpy2', gmpy2.version())" 2>&1 | head -2
ls /c/msys64/mingw64/bin/*mpfr* 2>/dev/null | head -3
echo "== controls vs COPY runner (each: pristine PASS? corrupted FAIL?) =="
mk() { # $1=name $2=file $3=awk-program(corrupt first match) $4=desc
  awk "$3" "$2" > "$OUT/ctrl/$1.vec"
}
# C1: sNaN plain delivery, strip invalid (use passing plain sNaN line)
grep -m1 '^msf16_minimum - 7c01 3c00' tests/vectors/minmax-f16.vec > "$OUT/ctrl/c1-base.txt" || grep -m1 ' 7c01 3c00 ' tests/vectors/minmax-f16.vec > "$OUT/ctrl/c1-base.txt"
cat "$OUT/ctrl/c1-base.txt"
awk 'NR==FNR{line=$0; next} {print} END{}' "$OUT/ctrl/c1-base.txt" /dev/null > /dev/null
L=$(cat "$OUT/ctrl/c1-base.txt")
printf '%s\n' "$L" > "$OUT/ctrl/c1-good.vec"
printf '%s\n' "$L" | awk '{$(NF-1)="00"; print}' > "$OUT/ctrl/c1-bad.vec"
cat "$OUT/ctrl/c1-good.vec" "$OUT/ctrl/c1-bad.vec"
"$R" verify "$OUT/ctrl/c1-good.vec" > "$OUT/ctrl/c1-good.log" 2>&1; echo "c1-good rc=$? $(grep -E '^total' "$OUT/ctrl/c1-good.log")"
"$R" verify "$OUT/ctrl/c1-bad.vec" > "$OUT/ctrl/c1-bad.log" 2>&1; echo "c1-bad rc=$? $(grep -E '^total' "$OUT/ctrl/c1-bad.log")"
# C3: -0/+0 swapped on passing same-sign zero line
printf 'msf16_minimum - 0 0 -> 0 00 exact-py-t2:directed-minmax\n' > "$OUT/ctrl/c3-good.vec"
printf 'msf16_minimum - 0 0 -> 8000 00 exact-py-t2:directed-minmax\n' > "$OUT/ctrl/c3-bad.vec"
"$R" verify "$OUT/ctrl/c3-good.vec" > "$OUT/ctrl/c3-good.log" 2>&1; echo "c3-good rc=$? $(grep -E '^total' "$OUT/ctrl/c3-good.log")"
"$R" verify "$OUT/ctrl/c3-bad.vec" > "$OUT/ctrl/c3-bad.log" 2>&1; echo "c3-bad rc=$? $(grep -E '^total' "$OUT/ctrl/c3-bad.log")"
# C4: magnitude tie-break corrupted (passing +1/-1 line)
printf 'msf16_minimum_magnitude - 3c00 bc00 -> bc00 00 exact-py-t2:directed-minmax\n' > "$OUT/ctrl/c4-good.vec"
printf 'msf16_minimum_magnitude - 3c00 bc00 -> 3c00 00 exact-py-t2:directed-minmax\n' > "$OUT/ctrl/c4-bad.vec"
"$R" verify "$OUT/ctrl/c4-good.vec" > "$OUT/ctrl/c4-good.log" 2>&1; echo "c4-good rc=$? $(grep -E '^total' "$OUT/ctrl/c4-good.log")"
"$R" verify "$OUT/ctrl/c4-bad.vec" > "$OUT/ctrl/c4-bad.log" 2>&1; echo "c4-bad rc=$? $(grep -E '^total' "$OUT/ctrl/c4-bad.log")"
# C5: NaN payload altered (passing plain qNaN delivery)
printf 'msf16_minimum - 7e01 3c00 -> 7e01 00 exact-py-t2:directed-minmax\n' > "$OUT/ctrl/c5-good.vec"
printf 'msf16_minimum - 7e01 3c00 -> 7e02 00 exact-py-t2:directed-minmax\n' > "$OUT/ctrl/c5-bad.vec"
"$R" verify "$OUT/ctrl/c5-good.vec" > "$OUT/ctrl/c5-good.log" 2>&1; echo "c5-good rc=$? $(grep -E '^total' "$OUT/ctrl/c5-good.log")"
"$R" verify "$OUT/ctrl/c5-bad.vec" > "$OUT/ctrl/c5-bad.log" 2>&1; echo "c5-bad rc=$? $(grep -E '^total' "$OUT/ctrl/c5-bad.log")"
# C7: setPayload(0) expected +0 (passing DQAN line)
printf 'msf16_set_payload - 0 -> 7e00 -- exact-py-t2:directed-payload\n' > "$OUT/ctrl/c7-good.vec"
printf 'msf16_set_payload - 0 -> 0 -- exact-py-t2:directed-payload\n' > "$OUT/ctrl/c7-bad.vec"
"$R" verify "$OUT/ctrl/c7-good.vec" > "$OUT/ctrl/c7-good.log" 2>&1; echo "c7-good rc=$? $(grep -E '^total' "$OUT/ctrl/c7-good.log")"
"$R" verify "$OUT/ctrl/c7-bad.vec" > "$OUT/ctrl/c7-bad.log" 2>&1; echo "c7-bad rc=$? $(grep -E '^total' "$OUT/ctrl/c7-bad.log")"
# C8: inadmissible input expected NaN (passing +0 line)
printf 'msf16_set_payload - bfff -> 0 -- exact-py-t2:directed-payload\n' > "$OUT/ctrl/c8-good.vec"
printf 'msf16_set_payload - bfff -> 7e00 -- exact-py-t2:directed-payload\n' > "$OUT/ctrl/c8-bad.vec"
"$R" verify "$OUT/ctrl/c8-good.vec" > "$OUT/ctrl/c8-good.log" 2>&1; echo "c8-good rc=$? $(grep -E '^total' "$OUT/ctrl/c8-good.log")"
"$R" verify "$OUT/ctrl/c8-bad.vec" > "$OUT/ctrl/c8-bad.log" 2>&1; echo "c8-bad rc=$? $(grep -E '^total' "$OUT/ctrl/c8-bad.log")"
# C9: flags token 00 where -- required
printf 'msf16_get_payload - 7e01 -> 3c00 -- exact-py-t2:directed-payload\n' > "$OUT/ctrl/c9-good.vec"
printf 'msf16_get_payload - 7e01 -> 3c00 00 exact-py-t2:directed-payload\n' > "$OUT/ctrl/c9-bad.vec"
"$R" verify "$OUT/ctrl/c9-good.vec" > "$OUT/ctrl/c9-good.log" 2>&1; echo "c9-good rc=$? $(grep -E '^total' "$OUT/ctrl/c9-good.log")"
"$R" verify "$OUT/ctrl/c9-bad.vec" > "$OUT/ctrl/c9-bad.log" 2>&1; echo "c9-bad rc=$? $(grep -E '^total' "$OUT/ctrl/c9-bad.log")"
# C2: plain/Number swapped on single-qNaN (passing plain line, swap op token)
printf 'msf16_minimum - 7e00 3c00 -> 7e00 00 exact-py-t2:directed-minmax\n' > "$OUT/ctrl/c2-good.vec"
printf 'msf16_minimum_number - 7e00 3c00 -> 7e00 00 exact-py-t2:directed-minmax\n' > "$OUT/ctrl/c2-bad.vec"
"$R" verify "$OUT/ctrl/c2-good.vec" > "$OUT/ctrl/c2-good.log" 2>&1; echo "c2-good rc=$? $(grep -E '^total' "$OUT/ctrl/c2-good.log")"
"$R" verify "$OUT/ctrl/c2-bad.vec" > "$OUT/ctrl/c2-bad.log" 2>&1; echo "c2-bad rc=$? $(grep -E '^total' "$OUT/ctrl/c2-bad.log")"
# C6: quiet bit flipped on a signaling setter expectation (needs correct impl; see fixed-runner part)
printf 'msf16_set_payload_signaling - 3c00 -> 7c01 -- exact-py-t2:directed-payload\n' > "$OUT/ctrl/c6-good.vec"
printf 'msf16_set_payload_signaling - 3c00 -> 7e01 -- exact-py-t2:directed-payload\n' > "$OUT/ctrl/c6-bad.vec"
"$R" verify "$OUT/ctrl/c6-good.vec" > "$OUT/ctrl/c6-good.log" 2>&1; echo "c6-good(copy) rc=$? $(grep -E '^total' "$OUT/ctrl/c6-good.log")"
"$R" verify "$OUT/ctrl/c6-bad.vec" > "$OUT/ctrl/c6-bad.log" 2>&1; echo "c6-bad(copy) rc=$? $(grep -E '^total' "$OUT/ctrl/c6-bad.log")"
exit 0
