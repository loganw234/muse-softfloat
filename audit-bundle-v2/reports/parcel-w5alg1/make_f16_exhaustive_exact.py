"""Independent leg: binary16 exhaustive expectations from the
generator's exact integer decider only (no MPFR, no C decider),
emitted as a runner vector file. Plus a briefs.jsonl parse.
"""
import importlib.util
import json
import pathlib
import sys

WT = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2])

spec = importlib.util.spec_from_file_location(
    "gen_alg", WT / "tests/gen_vectors_alg.py")
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

lines = ["# scratch gate: exact-py exhaustive binary16 rSqrt "
         "(all encodings x 5 modes), generated not committed"]
for x in range(65536):
    exp = g.exact_decide("f16", x)
    for rm, (rb, rf) in zip(g.RMS, exp):
        lines.append(f"msf16_r_sqrt {rm} {x:x} -> {rb:x} {rf:02x} "
                     f"exact-py-alg:f16-exhaustive")
out.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
print(f"wrote {out}: {len(lines) - 1} cases")

p = WT / "docs/metrics/briefs.jsonl"
n = 0
for ln in p.read_text(encoding="utf-8").splitlines():
    if ln.strip():
        json.loads(ln)
        n += 1
print(f"briefs.jsonl: {n} JSON rows parse")
