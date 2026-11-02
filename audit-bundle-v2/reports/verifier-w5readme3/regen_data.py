"""Rerun the copy's build_data.py with outputs redirected outside the copy."""
import sys
from pathlib import Path

COPY = Path("worktrees/verify5-readme3").resolve()
OUT = Path("scratch/verifier-w5readme3/regen").resolve()
OUT.mkdir(parents=True, exist_ok=True)

src = (COPY / "site" / "build_data.py").read_text(encoding="utf-8")
ns = {"__name__": "regen_build_data", "__file__": str(COPY / "site" / "build_data.py")}
exec(compile(src, str(COPY / "site" / "build_data.py"), "exec"), ns)
# Redirect: ROOT stays the copy (inputs), SITE becomes scratch out (outputs).
ns["SITE"] = OUT
assert str(ns["ROOT"]) == str(COPY), (ns["ROOT"], COPY)
rc = ns["main"]()
print("regen rc =", rc)
