#!/usr/bin/env python3
"""Generator refusal mutants for SF-1 Step 0a (scratch evidence)."""
import pathlib
import shutil
import subprocess
import sys

WS = pathlib.Path("C:/Users/logan/source/repos/Muse-Softfloat")
WT = WS / "worktrees" / "w4-seam"
BASE = WS / "scratch" / "lead" / "w4-seam-mutants"
PY = WS / ".venv" / "Scripts" / "python.exe"

CASES = {
    "unknown-claim": ("\trequired\n", "\tC-ULP\n", "claim 'C-ULP' not admitted"),
    "claim-mispair": ("\tC-754\n", "\trequired\n", "claim 'required' not admitted for tier 2"),
    "unknown-authority": ("\tberkeley\t", "\thost-libm\t", "unknown authority 'host-libm'"),
    "unknown-tier": ("\t1\trequired\n", "\t3\trequired\n", "unknown tier '3'"),
}

if BASE.exists():
    shutil.rmtree(BASE)
results = []
for name, (old, new, needle) in CASES.items():
    case = BASE / name
    (case / "tools").mkdir(parents=True)
    (case / "tables").mkdir(parents=True)
    shutil.copy2(WT / "tools" / "gen_tables.py", case / "tools" / "gen_tables.py")
    for fn in ("formats.tsv", "implemented.tsv"):
        shutil.copy2(WT / "tables" / fn, case / "tables" / fn)
    ops = (WT / "tables" / "operations.tsv").read_bytes().decode("utf-8")
    assert old in ops, (name, old)
    (case / "tables" / "operations.tsv").write_bytes(
        ops.replace(old, new, 1).encode("utf-8"))
    proc = subprocess.run([str(PY), str(case / "tools" / "gen_tables.py"),
                           str(case / "out")],
                          capture_output=True, text=True)
    log = proc.stdout + proc.stderr
    (case / "generator.log").write_bytes(log.encode("utf-8"))
    ok = proc.returncode != 0 and needle in log
    results.append((name, proc.returncode, ok, needle))
    print("%s: rc=%d refused=%s (%s)" % (name, proc.returncode, ok, needle))

if not all(ok for _, _, ok, _ in results):
    raise SystemExit("MUTANT NOT REFUSED: %r" % (results,))
print("all generator mutants refused")
