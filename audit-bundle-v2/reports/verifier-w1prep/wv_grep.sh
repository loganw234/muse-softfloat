#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/muse-softfloat || exit 9
echo '--- word-exact float/double in src include (expect no output) ---'
grep -rnwE 'float|double' src include
echo "WORDSCAN_RC:$?"
echo '--- third-party softfloat vendoring in src include (expect no output) ---'
grep -rniE 'hauser|jhauser|uc regents|softfloat-3e' src include
echo "VENDOR_RC:$?"
echo '--- berkeley/testfloat mentions outside oracle/test plumbing ---'
grep -rniE 'berkeley|testfloat' src include | head -n 20
echo "PLUMB_RC:$?"
echo '--- git status (expect only ignored build/ + scratch) ---'
git -c safe.directory=C:/Users/logan/source/repos/Muse-Softfloat/muse-softfloat status --short | head -n 20
echo "STATUS_DONE"
