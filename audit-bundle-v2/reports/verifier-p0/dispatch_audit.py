"""verifier-p0 dispatch audit: status/fn consistency + symbol resolution."""
import pathlib
import re
import subprocess

DISP = pathlib.Path(r"C:\Users\logan\source\repos\Muse-Softfloat\muse-softfloat\tests\msf_dispatch.h")
rows = re.findall(r'\{\s*"([^"]+)",\s*"([^"]+)",\s*MSF_SIG_\w+,\s*MSF_RK_\w+,'
                  r'\s*\{[^}]*\},\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(0|\(void \*\)(\w+))\s*\}',
                  DISP.read_text())
print("dispatch rows:", len(rows))
impl = [r for r in rows if r[5] == "1"]
plan = [r for r in rows if r[5] == "0"]
print("implemented:", len(impl), "planned:", len(plan))
bad = 0
for (name, std, nargs, hasrm, hasfl, status, wave, fn0, fnsym) in rows:
    if status == "1":
        if fnsym != name:
            bad += 1
            print("IMPL-BAD:", name, fn0, fnsym)
    else:
        if fn0 != "0" or fnsym != "":
            bad += 1
            print("PLAN-BAD:", name, fn0, fnsym)
print("status/fn inconsistencies:", bad)
# symbol resolution in a host build: nm the smoke runner
p = subprocess.run(["C:/msys64/mingw64/bin/nm.exe",
                    r"C:\Users\logan\source\repos\Muse-Softfloat\muse-softfloat\build\smoke\msf_runner.exe"],
                   capture_output=True, text=True, timeout=60)
syms = set()
for ln in p.stdout.splitlines():
    parts = ln.split()
    if len(parts) == 3:
        syms.add(parts[2].lstrip("_"))
missing = [r[0] for r in impl if r[0] not in syms and r[8] not in syms]
print("impl names missing from host build:", missing if missing else "none")
