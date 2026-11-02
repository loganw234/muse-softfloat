#!/bin/sh
# Linux-channel probes for verifier-w6ci. Run under WSL bash from repo root.
DUP=/mnt/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6ci/dup
VEC=$DUP/tests/vectors/encodings-f32.vec
OUT=/mnt/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6ci
echo "== awk identity =="
awk --version 2>&1 | head -1
echo "== input endings =="
file "$VEC"
total=$(wc -l < "$VEC")
crlf=$(grep -c "$(printf '\r$')" "$VEC")
echo "lines=$total crlf=$crlf"
echo "== P1: inventory pipe masks missing tool =="
nonexistent-tool-xyz-123 --version 2>/dev/null | head -n 1
echo "pipeline-status=$? (0 means a missing tool does NOT fail the step)"
echo "== P2a: control-2 OLD program on Linux channel =="
awk 'BEGIN{d=0} /^msf32_class/ && !d && $NF=="exact-py:directed-encodings" {for(i=1;i<=NF;i++) if($i=="->" && ($(i+1)=="0"||$(i+1)=="1")) {$(i+1)=($(i+1)=="0"?"1":"0"); d=1}} {print}' "$VEC" > "$OUT/old-nanpol.vec"
cmp -s "$VEC" "$OUT/old-nanpol.vec" && echo "OLD: byte-identical to input (mutant unmutated)" || echo "OLD: differs"
echo "== P2b: control-2 NEW program on Linux channel =="
awk 'BEGIN{d=0} {t=$NF; if (substr(t,length(t))=="\r") t=substr(t,1,length(t)-1)} /^msf32_class/ && !d && $NF=="exact-py:directed-encodings" {for(i=1;i<=NF;i++) if($i=="->" && ($(i+1)=="0"||$(i+1)=="1")) {$(i+1)=($(i+1)=="0"?"1":"0"); d=1}} {print}' "$VEC" > "$OUT/new-nanpol.vec"
cmp -s "$VEC" "$OUT/new-nanpol.vec" && echo "NEW: byte-identical to input (STILL unmutated -> fix is no-op)" || echo "NEW: differs"
cmp "$VEC" "$OUT/new-nanpol.vec" | head -2
echo "== P2c: what $NF looks like on Linux channel =="
awk 'NR==1024 {printf "len(NF)=%d last-char-code=%d\n", length($NF), strtonum("0x" sprintf("%02x", substr($NF,length($NF),1)) + 0))}' "$VEC" 2>/dev/null || awk 'NR==1024 {printf "NF=[%s] len=%d\n", $NF, length($NF)}' "$VEC"
echo "== P2d: tag stage OLD vs NEW on all committed vecs =="
cd "$DUP" || exit 1
awk '!/^#/ && NF>0 {print $NF}' tests/vectors/*.vec 2>/dev/null | sort | uniq -c | awk '{print $2, $1}' > "$OUT/old-expect.txt"
awk '!/^#/ && NF>0 {t=$NF; if (substr(t,length(t))=="\r") t=substr(t,1,length(t)-1); print $NF}' tests/vectors/*.vec 2>/dev/null | sort | uniq -c | awk '{print $2, $1}' > "$OUT/new-expect.txt"
echo "OLD tags with CR: $(grep -c "$(printf '\r')" "$OUT/old-expect.txt")"
echo "NEW tags with CR: $(grep -c "$(printf '\r')" "$OUT/new-expect.txt")"
cmp -s "$OUT/old-expect.txt" "$OUT/new-expect.txt" && echo "OLD==NEW (strip had no effect, prints \$NF)" || echo "OLD differs from NEW"
echo "== toolchain =="
gcc --version | head -n 1
gcc -dumpmachine
command -v arm-none-eabi-gcc >/dev/null 2>&1 && arm-none-eabi-gcc --version | head -1 || echo "arm-none-eabi-gcc: MISSING (symbol scan will SKIP-BY-NAME)"
