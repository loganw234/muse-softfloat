#!/usr/bin/env bash
# rev_linux_semantics.sh - Linux-semantics proof for the
# parcel-w6ci revision (control 2 CR fix), run on this Windows
# host under Git Bash.
#
# Method: GNU awk's BINMODE=3 forces binary-mode input AND
# output (its Windows/MSYS text translation off). That is
# exactly how awk behaves on Linux, where there is no text
# mode and a CR is an ordinary byte that stays attached to
# $NF. Measured on encodings-f32.vec line 1024 below: default
# (text) mode $NF length 27 (CR silently eaten - the masking
# that hid the bug), BINMODE=3 length 28 (CR present, Linux
# semantics). The OLD and NEW awk programs are then run
# verbatim through that channel and byte-compared (python,
# binary reads) against the original vector file.
set -u
WS=/c/Users/logan/source/repos/Muse-Softfloat
SC="$WS/scratch/parcel-w6ci"
SCW="C:/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w6ci"
PY="$WS/.venv/Scripts/python.exe"
cd "$WS/worktrees/w6-ci" || exit 9
F=tests/vectors/encodings-f32.vec

echo "== channel check: pick an awk whose BINMODE=3 exposes the CR =="
AWK=""
for a in /c/msys64/usr/bin/awk "$(command -v awk)"; do
    [ -n "$a" ] && [ -x "$a" ] || continue
    ndef=$("$a" 'NR==1024{print length($NF)}' "$F")
    nbin=$("$a" -v BINMODE=3 'NR==1024{print length($NF)}' "$F")
    echo "candidate $a : default len(\$NF)=$ndef BINMODE=3 len(\$NF)=$nbin"
    if [ "$nbin" = 28 ] && [ -z "$AWK" ]; then AWK="$a"; fi
done
[ -n "$AWK" ] || { echo "NO awk exposed CR under BINMODE=3 - proof unavailable"; exit 1; }
echo "using awk: $AWK"
"$AWK" --version 2>&1 | head -1

PROG_OLD='BEGIN{d=0} /^msf32_class/ && !d && $NF=="exact-py:directed-encodings" {for(i=1;i<=NF;i++) if($i=="->" && ($(i+1)=="0"||$(i+1)=="1")) {$(i+1)=($(i+1)=="0"?"1":"0"); d=1}} {print}'
PROG_NEW='BEGIN{d=0} {t=$NF; if (substr(t,length(t))=="\r") t=substr(t,1,length(t)-1)} /^msf32_class/ && !d && t=="exact-py:directed-encodings" {for(i=1;i<=NF;i++) if($i=="->" && ($(i+1)=="0"||$(i+1)=="1")) {$(i+1)=($(i+1)=="0"?"1":"0"); d=1}} {print}'
TAG_OLD='!/^#/ && NF>0 {print $NF}'
TAG_NEW='!/^#/ && NF>0 {t=$NF; if (substr(t,length(t))=="\r") t=substr(t,1,length(t)-1); print t}'

echo "== verbatim checks =="
grep -Fq "$PROG_NEW" tools/run.sh && echo "PROG_NEW verbatim in tools/run.sh: YES" || { echo "PROG_NEW NOT in run.sh"; exit 1; }
grep -Fq "$TAG_NEW" tools/run.sh && echo "TAG_NEW verbatim in tools/run.sh: YES" || { echo "TAG_NEW NOT in run.sh"; exit 1; }
git show eda5812:tools/run.sh > "$SC/rev-run-sh-old.txt" 2>/dev/null
grep -Fq "$PROG_OLD" "$SC/rev-run-sh-old.txt" && echo "PROG_OLD verbatim at eda5812: YES" || echo "PROG_OLD verbatim at eda5812: NO"
grep -Fq "$TAG_OLD" "$SC/rev-run-sh-old.txt" && echo "TAG_OLD verbatim at eda5812: YES" || echo "TAG_OLD verbatim at eda5812: NO"

echo "== control 2 mutation through Linux-semantics channel (BINMODE=3) =="
"$AWK" -v BINMODE=3 "$PROG_OLD" "$F" > "$SC/rev-nanpol-old-linux.vec"
"$AWK" -v BINMODE=3 "$PROG_NEW" "$F" > "$SC/rev-nanpol-new-linux.vec"
"$AWK" "$PROG_NEW" "$F" > "$SC/rev-nanpol-new-windows.vec"
"$PY" "$SCW/rev_byte_diff.py" compare "$F" "$SCW/rev-nanpol-old-linux.vec" "OLD prog, Linux semantics"
"$PY" "$SCW/rev_byte_diff.py" compare "$F" "$SCW/rev-nanpol-new-linux.vec" "NEW prog, Linux semantics"
"$PY" "$SCW/rev_byte_diff.py" line "$SCW/rev-nanpol-new-linux.vec" 1024 "NEW linux output"
"$PY" "$SCW/rev_byte_diff.py" line "$SCW/rev-nanpol-new-windows.vec" 1024 "NEW windows text-mode output"
"$PY" "$SCW/rev_byte_diff.py" line "$F" 1024 "original"

echo "== write_expect_counts first stage (provenance tags) =="
VECS=$(sed -n 's/^VECS="\(.*\)"$/\1/p' tools/run.sh)
echo "VECS files: $(echo $VECS | wc -w)"
"$AWK" -v BINMODE=3 "$TAG_OLD" $VECS > "$SC/rev-tags-old-linux.txt"
"$AWK" -v BINMODE=3 "$TAG_NEW" $VECS > "$SC/rev-tags-new-linux.txt"
"$AWK" "$TAG_OLD" $VECS > "$SC/rev-tags-old-windows.txt"
"$AWK" "$TAG_NEW" $VECS > "$SC/rev-tags-new-windows.txt"
echo "-- Linux channel, old vs new --"
"$PY" "$SCW/rev_byte_diff.py" tags "$SCW/rev-tags-old-linux.txt" "$SCW/rev-tags-new-linux.txt"
echo "-- Windows channel, old vs new --"
"$PY" "$SCW/rev_byte_diff.py" tags "$SCW/rev-tags-old-windows.txt" "$SCW/rev-tags-new-windows.txt"
echo "-- cross-channel identity of NEW program --"
cmp "$SC/rev-tags-new-windows.txt" "$SC/rev-tags-new-linux.txt" && echo "cmp NEW windows-output == NEW linux-output: IDENTICAL"
cmp "$SC/rev-tags-old-windows.txt" "$SC/rev-tags-new-windows.txt" && echo "cmp OLD windows-output == NEW windows-output: IDENTICAL (Windows behaviour unchanged)"

echo "== run.sh byte hygiene =="
"$PY" "$SCW/rev_byte_diff.py" check-runsh
echo "PROOF SCRIPT DONE"
