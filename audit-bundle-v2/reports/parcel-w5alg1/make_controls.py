"""Build the rSqrt negative-control mutant vector files.

Each mutant file is a full copy of one committed alg-*.vec with
exactly one class of corruption; the runner must REFUSE every
one (watched in 05_controls.sh). Prints the line(s) touched so
the control is auditable.
"""
import pathlib
import sys

WT = pathlib.Path(sys.argv[1])
OUT = pathlib.Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)


def lines_of(name):
    return (WT / "tests/vectors" / name).read_text(encoding="utf-8").splitlines()


def write(name, lines):
    (OUT / name).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def find(lines, pred, what):
    for i, ln in enumerate(lines):
        if ln.startswith("#") or not ln.strip():
            continue
        t = ln.split()
        if pred(t):
            return i, t
    raise SystemExit(f"control target not found: {what}")


f16 = lines_of("alg-f16.vec")
f32 = lines_of("alg-f32.vec")
f64 = lines_of("alg-f64.vec")

# 1. 1-ulp-moved hardest (midpoint-adjacent ties family) expectation.
ls = list(f64)
i, t = find(ls, lambda t: t[-1] == "mpfr-alg:ties" and t[1] == "te"
            and t[5] == "10", "ties te inexact")
t[4] = f"{int(t[4], 16) + 1:x}"
ls[i] = " ".join(t)
write("mut_ulp.vec", ls)
print(f"mut_ulp: alg-f64 line {i + 1} result moved +1 ulp")

# 2a. specials mutant: rSqrt(-0) flipped to +inf (the MPFR cell).
ls = list(f16)
i, t = find(ls, lambda t: t[2] == "8000", "f16 -0 input")
assert t[4] == "fc00", t  # shipped: -inf
t[4] = "7c00"
ls[i] = " ".join(t)
write("mut_negzero.vec", ls)
print(f"mut_negzero: alg-f16 line {i + 1} -0 result flipped to +inf")

# 2b. specials mutant: quiet-NaN payload mangled.
ls = list(f32)
i, t = find(ls, lambda t: t[-1] == "mpfr-alg:specials"
            and (int(t[2], 16) >> 23) & 0xff == 0xff
            and (int(t[2], 16) >> 22) & 1, "f32 qNaN input")
t[4] = f"{int(t[4], 16) ^ 0x10:x}"
ls[i] = " ".join(t)
write("mut_qnan.vec", ls)
print(f"mut_qnan: alg-f32 line {i + 1} qNaN payload bit flipped")

# 2c. specials mutant: rSqrt(-1) delivered finite instead of NaN.
ls = list(f16)
i, t = find(ls, lambda t: t[2] == "bc00", "f16 -1 input")
assert t[4] == "7e00" and t[5] == "01", t
t[4], t[5] = "3c00", "00"
ls[i] = " ".join(t)
write("mut_negfinite.vec", ls)
print(f"mut_negfinite: alg-f16 line {i + 1} -1 result made finite 1.0")

# 3. inexact stripped on a midpoint-adjacent inexact case.
ls = list(f32)
i, t = find(ls, lambda t: t[-1] == "mpfr-alg:ties" and t[5] == "10",
            "f32 ties inexact")
t[5] = "00"
ls[i] = " ".join(t)
write("mut_noinexact.vec", ls)
print(f"mut_noinexact: alg-f32 line {i + 1} flags 10 -> 00")

# 4. directed-mode swap over a whole file (tp <-> tn).
ls = []
for ln in f32:
    if ln.startswith("#") or not ln.strip():
        ls.append(ln)
        continue
    t = ln.split()
    if t[1] == "tp":
        t[1] = "tn"
    elif t[1] == "tn":
        t[1] = "tp"
    ls.append(" ".join(t))
write("mut_dirswap.vec", ls)
print("mut_dirswap: alg-f32 all tp<->tn swapped")
print("MAKE-CONTROLS: PASS")
