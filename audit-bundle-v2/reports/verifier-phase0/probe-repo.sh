#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 1
mkdir -p scratch/verifier-phase0/tmp
export TMPDIR=$PWD/scratch/verifier-phase0/tmp
G="git -c safe.directory=C:/Users/logan/source/repos/Muse-Softfloat/muse-softfloat -C muse-softfloat"
echo "=== HEAD / root ==="
$G rev-parse HEAD
$G rev-list --count HEAD
$G rev-parse --show-toplevel
echo "=== ls-files ==="
$G ls-files
echo "=== check-attr text ==="
$G check-attr text -- .gitattributes .gitignore AGENTS.md README.md docs/BOARD.md docs/HARNESS.md docs/KICKOFF.md
echo "=== core.autocrlf (read only) ==="
$G config --get core.autocrlf || echo "core.autocrlf: unset in queried scope rc=$?"
git config --global --get core.autocrlf || echo "global core.autocrlf: unset rc=$?"
echo "=== CR bytes in committed blobs (count lines ending CR) ==="
for f in .gitattributes .gitignore AGENTS.md README.md docs/BOARD.md docs/HARNESS.md docs/KICKOFF.md; do
  n=$($G show HEAD:"$f" | grep -c "$(printf '\r')" || true)
  echo "$f CR-lines=$n"
done
echo "=== check-ignore probes ==="
for p in x.pdf docs/a.pdf "754-2019.pdf" X.PDF .venv/foo.py .venv/Scripts/python.exe x.elf sub/x.uf2 x.bin x.hex build/x.o build-pico/x __pycache__/x.pyc x.pyc probe-tmp/x foo-tmp/x src/main.c docs/NOTE.md LICENSE src/lib.o; do
  if $G check-ignore -v "$p" >/dev/null 2>&1; then
    echo "IGNORED  $p  -- $($G check-ignore -v "$p")"
  else
    echo "not-ignored  $p"
  fi
done
echo "=== conflict markers in HEAD files ==="
$G grep -n -E '^(<{7}|>{7}|={7}( |$))' HEAD -- . || echo "no conflict-marker lines found rc=$?"
echo "=== secret-shaped patterns in HEAD files ==="
$G grep -n -E '(ghp_[A-Za-z0-9]|github_pat_|AKIA[0-9A-Z]{16}|BEGIN [A-Z ]*PRIVATE KEY|password *[:=]|secret *[:=]|token *[:=])' HEAD -- . || echo "no secret-shaped matches rc=$?"
echo "=== dubious ownership without safe.directory (expect refusal) ==="
git -C muse-softfloat status 2>&1 | head -n 6
echo "=== ledger outside worktree? ==="
$G ls-files -- ledger docs/RECORD.md docs/studies || true
ls -d ledger ledger/briefs ledger/urgent 2>&1
test -e ledger/board.lock && echo "board.lock EXISTS" || echo "board.lock absent"
echo "=== layout existence ==="
for d in muse-softfloat ledger ledger/briefs scratch worktrees .venv .venv/Scripts; do
  test -d "$d" && echo "dir OK $d" || echo "dir MISSING $d"
done
test -e muse-softfloat/LICENSE && echo "LICENSE exists" || echo "LICENSE absent"
test -e muse-softfloat/docs/RECORD.md && echo "RECORD exists" || echo "RECORD.md absent"
test -d muse-softfloat/docs/studies && echo "studies exists" || echo "docs/studies absent"
echo "=== pico-sdk path ==="
ls -d /c/Users/logan/pico/pico-sdk 2>&1 || echo "pico-sdk dir not readable/absent"
ls /c/Users/logan/pico/pico-sdk/pico_sdk_version.h 2>&1 || true
grep -i "PICO_SDK_VERSION" /c/Users/logan/pico/pico-sdk/pico_sdk_version.h 2>/dev/null | head -n 10 || echo "version header unread"
echo "=== DONE probe-repo ==="
