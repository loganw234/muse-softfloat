"""17_unknown_sig.py - unknown sig token must be refused (SystemExit)."""
import importlib.util
import sys

_spec = importlib.util.spec_from_file_location(
    "gent", "worktrees/verify5-alg1/tools/gen_tables.py")
gent = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gent)

row = {"sig": "math_bogus", "op": "bogus", "std_name": "Bogus",
       "clause": "9.2", "rounding": "attr", "flags": "yes", "wave": "5",
       "tier": "2", "claim": "C-754", "authority": "mpfr-exact",
       "vectors": "directed-alg", "comparison": "exact"}
try:
    gent.expand(row)
except SystemExit as e:
    print("unknown sig refused as required: SystemExit %s" % e)
    sys.exit(0)
print("UNKNOWN SIG NOT REFUSED")
sys.exit(1)
