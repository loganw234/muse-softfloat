# cleanroom.py — auditor-adherence-final tree scan (Git Bash, MSF_PYTHON pinned)
# Verifies no vendored third-party source in the tracked src/include/compat tree.
# Usage: "$MSF_PYTHON" scratch/audit-adherence-final/cleanroom.py (run from workspace root)
import subprocess, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
MSF = ROOT / "muse-softfloat"
def git(*a):
    return subprocess.run(["git", "-C", str(MSF)] + list(a), capture_output=True,
                          text=True, encoding="utf-8", errors="replace").stdout
files = git("ls-files").splitlines()
print("tracked", len(files))
marks = ["testfloat", "berkeley", "core-math", "coremath", "rebound",
         "john hauser", "copyright (c)"]
for f in files:
    fl = f.lower()
    if not (fl.startswith("src/") or fl.startswith("include/") or fl.startswith("compat/")):
        continue
    t = (MSF / f).read_text(encoding="utf-8", errors="replace").lower()
    for mk in marks:
        if mk in t:
            print("HIT", f, mk)
            break
print("kissfft refs:")
print(git("grep", "-i", "-n", "kissfft", "--", "src", "include", "compat")[:800])
