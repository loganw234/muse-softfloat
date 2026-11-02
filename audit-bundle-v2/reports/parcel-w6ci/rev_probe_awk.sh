#!/usr/bin/env bash
# rev_probe_awk.sh - probe how this host's awk(s) see the CR in
# encodings-f32.vec (fully CRLF), to design a Linux-semantics
# proof that does not rely on MSYS text mode. Target line 1024:
# msf32_class - 7f800001 -> 0 -- exact-py:directed-encodings<CR>
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w6-ci || exit 9
F=tests/vectors/encodings-f32.vec
WS=/c/Users/logan/source/repos/Muse-Softfloat
PY="$WS/.venv/Scripts/python.exe"

echo "--- which awk (Git Bash default) ---"
command -v awk; awk --version 2>&1 | head -1
echo "--- SHELLOPTS/BASH: $BASH $BASH_VERSION"

show() { # label, then hexdump stdin
  echo "[$1]"
  od -c | head -3
}

echo "== A: awk file-arg (as run.sh calls it) =="
awk 'NR==1024 { print $NF }' "$F" | show "A last field"
echo "== B: cat | awk =="
cat "$F" | awk 'NR==1024 { print $NF }' | show "B last field"
echo "== C: python binary stdout | awk =="
"$PY" -c "import sys; sys.stdout.buffer.write(open(sys.argv[1],'rb').read())" "$F" \
  | awk 'NR==1024 { print $NF }' | show "C last field"
echo "== D: awk file-arg with BINMODE=3 =="
awk -v BINMODE=3 'NR==1024 { print $NF }' "$F" | show "D last field"
echo "== E: python binary | awk BINMODE=3 =="
"$PY" -c "import sys; sys.stdout.buffer.write(open(sys.argv[1],'rb').read())" "$F" \
  | awk -v BINMODE=3 'NR==1024 { print $NF }' | show "E last field"

echo "== F: match test old condition, python-source pipe =="
"$PY" -c "import sys; sys.stdout.buffer.write(open(sys.argv[1],'rb').read())" "$F" \
  | awk 'NR==1024 { print ($NF=="exact-py:directed-encodings") ? "MATCH" : "NOMATCH", length($NF) }'
echo "== G: awk output to file (redirection), hex of line end =="
awk 'NR==1024 { print $NF }' "$F" > "$WS/scratch/parcel-w6ci/rev-probe-out.txt"
od -c "$WS/scratch/parcel-w6ci/rev-probe-out.txt" | head -3
echo "== H: awk length of \$NF and \$0 on line 1024 (file arg) =="
awk 'NR==1024 { print "NF=" NF, "lenNF=" length($NF), "len0=" length($0) }' "$F"
"$PY" -c "import sys; d=open(sys.argv[1],'rb').read().split(b'\n')[1023]; print('python: raw line len incl CR =', len(d), 'last field len =', len(d.split()[-1]), 'tag len plain =', len(b'exact-py:directed-encodings'))" "$F"
