#!/bin/bash
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
P=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
printf '%s\n' 'import sys' 'print(sys.version)' > /tmp/mptest.py
cat /tmp/mptest.py
$P /tmp/mptest.py
echo "rc=$?"
$P -c "pass"
echo "rc2=$?"
