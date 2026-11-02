import collections, pathlib, re, subprocess

WS = pathlib.Path("C:/Users/logan/source/repos/Muse-Softfloat")
WT = WS / "worktrees/w2-f16"
SCR = WS / "scratch/parcel-f16"
out = []
def emit(s):
    out.append(s); print(s)

# Berkeley grouped subtotals
jobs = []
for line in (SCR / "berkeley-results.log").read_text().splitlines():
    m = re.match(r"JOB (\S+) cases=(\d+) verify=(\S+)", line)
    if m:
        jobs.append((m.group(1), int(m.group(2)), m.group(3)))
groups = collections.OrderedDict()
for tag, n, v in jobs:
    fn = tag.rsplit("-", 2)[0] if "-l" in tag else tag
    # tag: fn-rm-l<level>[-takeN]; fn may contain dashes rarely; split on -l<digit>
    mm = re.match(r"(.+?)-([a-z]+|-)-l(\d)(?:-take\d+)?$", tag)
    fn, rm, lvl = mm.group(1), mm.group(2), mm.group(3)
    groups.setdefault((fn, int(lvl)), []).append((rm, n, v))
emit("Berkeley jobs: %d, cases: %d, all PASS: %s" %
     (len(jobs), sum(n for _, n, _ in jobs), all(v == "PASS" for _, _, v in jobs)))
for (fn, lvl), items in groups.items():
    per = ",".join("%s=%d" % (rm, n) for rm, n, _ in items)
    emit("  %s L%d: %d cases (%s) %s" %
         (fn, lvl, sum(n for _, n, _ in items), per,
          "PASS" if all(v == "PASS" for _, _, v in items) else "FAIL"))

# git state
GIT = ["git", "-c", "safe.directory=C:/Users/logan/source/repos/Muse-Softfloat/worktrees/w2-f16",
       "-C", str(WT)]
emit("git log -1: " + subprocess.run(GIT + ["log", "--oneline", "-1"],
     capture_output=True, text=True).stdout.strip())
emit("git status --short:")
emit(subprocess.run(GIT + ["status", "--short"], capture_output=True, text=True).stdout)
emit("git diff --stat (vs HEAD):")
emit(subprocess.run(GIT + ["diff", "--stat"], capture_output=True, text=True).stdout)
emit("untracked:")
emit(subprocess.run(GIT + ["ls-files", "--others", "--exclude-standard"],
     capture_output=True, text=True).stdout)

# line counts of hand-written owned files
for p in ["src/msf16.c", "tests/gen_vectors_f16.py"]:
    emit("%s: %d lines" % (p, len((WT / p).read_text(encoding="utf-8").splitlines())))
vtot = 0
for p in sorted((WT / "tests/vectors").glob("*f16.vec")):
    emit("vector %s: %d bytes" % (p.name, p.stat().st_size))
    vtot += p.stat().st_size
emit("my committed vector bytes total (6 files): %d" %
     sum((WT / ("tests/vectors/" + n)).stat().st_size for n in
         ["arith-f16.vec", "fma-sqrt-f16.vec", "conv-int-f16.vec",
          "toint-f16.vec", "rint-misc-f16.vec", "compare-f16.vec"]))
(SCR / "inventory.txt").write_bytes(("\n".join(out) + "\n").encode())
print("wrote inventory.txt")
