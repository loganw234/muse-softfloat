#!/usr/bin/env bash
# Fresh-clone rehearsal (brief acceptance d) + corruption
# probes (acceptance a, watched failing). Scratch only.
set -u
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
WT=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/w6-examples
RH=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w6examples/rehearsal
rm -rf "$RH"
mkdir -p "$RH"
(cd "$WT" && tar --exclude=./.git --exclude=./build -cf - .) | (cd "$RH" && tar -xf -)
[ ! -e "$RH/.git" ] || { echo "REHEARSAL FAIL: .git present in copy"; exit 1; }
echo "copy ok (no .git): $(ls "$RH" | tr '\n' ' ')"
cd "$RH" || exit 9

echo "== rehearsal 1/4: README command literally =="
bash examples/host/build.sh > rehearsal-clean.log 2>&1
rc=$?
tail -3 rehearsal-clean.log
[ $rc -eq 0 ] || { echo "REHEARSAL FAIL: clean run rc=$rc"; exit 1; }
grep -q 'host example: PASS' rehearsal-clean.log || { echo "REHEARSAL FAIL: no PASS line"; exit 1; }
echo "rehearsal clean: PASS rc=0"

cp examples/host/expected.txt expected.bak
cp examples/host/main.c main.bak

echo "== rehearsal 2/4: corrupt expected.txt (one hex digit) =="
sed -i 's/3fb999999999999a/3fb999999999999b/' examples/host/expected.txt
bash examples/host/build.sh > rehearsal-corrupt-expect.log 2>&1
rc=$?
tail -6 rehearsal-corrupt-expect.log
[ $rc -ne 0 ] || { echo "REHEARSAL FAIL: corrupted expectation was accepted"; exit 1; }
grep -q 'host example: FAIL' rehearsal-corrupt-expect.log || { echo "REHEARSAL FAIL: no FAIL line"; exit 1; }
echo "corrupt expected.txt: refused rc=$rc (watched failing)"
cp expected.bak examples/host/expected.txt

echo "== rehearsal 3/4: corrupt pinned constant in main.c =="
sed -i 's/0x3fb999999999999a/0x3fb999999999999b/' examples/host/main.c
bash examples/host/build.sh > rehearsal-corrupt-main.log 2>&1
rc=$?
grep -E 'EXAMPLE (PASS|FAIL)|host example: FAIL' rehearsal-corrupt-main.log || true
[ $rc -ne 0 ] || { echo "REHEARSAL FAIL: corrupted constant was accepted"; exit 1; }
grep -q 'EXAMPLE FAIL' rehearsal-corrupt-main.log || { echo "REHEARSAL FAIL: program did not self-report FAIL"; exit 1; }
echo "corrupt main.c constant: refused rc=$rc (watched failing)"
cp main.bak examples/host/main.c

echo "== rehearsal 4/4: restored tree passes again =="
bash examples/host/build.sh > rehearsal-restored.log 2>&1
rc=$?
tail -2 rehearsal-restored.log
[ $rc -eq 0 ] || { echo "REHEARSAL FAIL: restored run rc=$rc"; exit 1; }
echo "REHEARSAL ALL PASS"
