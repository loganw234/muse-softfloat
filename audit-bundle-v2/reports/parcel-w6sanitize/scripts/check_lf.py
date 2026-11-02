import subprocess
wt = r"C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w6-sanitize"
files = ["tools/run.sh", ".github/workflows/ci.yml", "AGENTS.md",
         "tests/sanitize_canary_clean.c", "tests/sanitize_canary_ub.c",
         "tests/sanitize_canary_ub_shift.c", "tests/sanitize_canary_heap.c",
         "tests/sanitize_canary_heap_far.c"]
for f in files:
    d = open(wt + "\\" + f.replace("/", "\\"), "rb").read()
    print(f, len(d), "B CR=", d.count(b"\r"))
