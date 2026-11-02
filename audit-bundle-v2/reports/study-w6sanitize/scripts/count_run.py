import re, subprocess, sys, time
# count_run.py <tree_win> <exe_win> — run all-files verify once,
# print every file:/prov:/total:/VERDICT: line verbatim.
tree, exe = sys.argv[1:3]
with open(tree + r"\tools\run.sh", encoding="utf-8") as f:
    vecs = re.search(r'^VECS="([^"]+)"', f.read(), re.M).group(1).split()
t0 = time.time()
p = subprocess.run([exe, "verify"] + vecs, cwd=tree, capture_output=True,
                   text=True, errors="replace", timeout=3600)
dt = time.time() - t0
print(f"rc={p.returncode} t={dt:.2f}s files={len(vecs)}")
for ln in (p.stdout + p.stderr).splitlines():
    if ln.startswith(("file", "prov", "total", "VERDICT", "manifest")):
        print(ln)
