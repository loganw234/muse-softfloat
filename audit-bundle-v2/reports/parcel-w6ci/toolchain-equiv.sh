#!/usr/bin/env bash
# Local equivalents of the ci.yml "Toolchain inventory" step, run
# on the Windows host. The PATH/python lines below reproduce the
# exact run.sh lines being ported so their Windows behaviour is
# observable; the Linux sides are one-line guards (CI-only).
set -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
gcc --version | head -n 1
gcc -dumpmachine
/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe --version
arm-none-eabi-gcc --version | head -n 1
arm-none-eabi-nm --version | head -n 1
echo "--- ported-line probes ---"
[ -d /c/msys64/mingw64/bin ] && echo "PATH guard: /c/msys64/mingw64/bin present -> prepend fires (Windows)"
if command -v python >/dev/null 2>&1; then
    echo "python resolves ($(command -v python)) -> python3 fallback does not fire here"
else
    echo "python NOT on this PATH -> python3 fallback would be consulted"
    command -v python3 || echo "python3 also absent in Git Bash PATH"
fi
[ -x /c/msys64/mingw32/bin/gcc ] && echo "x87 control: mingw32 gcc present -> refusal control runs here" || echo "x87 control: mingw32 absent"
