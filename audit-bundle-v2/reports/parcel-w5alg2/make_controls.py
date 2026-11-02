"""Build hypot negative-control mutant vector files."""
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
f64 = lines_of("alg-f64.vec")

# 1. qNaN/inf mutant: hypot(qNaN, +inf) expected +inf -> NaN.
ls = list(f16)
i, t = find(ls, lambda t: len(t) == 8 and "_hypot" in t[0] and t[1] == "te"
            and t[2] == "7e00" and t[3] == "7c00", "qNaN,inf")
assert t[5] == "7c00" and t[6] == "00", t
t[5] = "7e00"
ls[i] = " ".join(t)
write("mut_qnan_inf.vec", ls)
print(f"mut_qnan_inf: f16 line {i+1} hypot(qNaN,inf) +inf -> NaN")

# 2. 1-ulp-moved hardest: f64 ties te inexact result +1 ulp.
ls = list(f64)
i, t = find(ls, lambda t: len(t) == 8 and "_hypot" in t[0]
            and t[-1] == "mpfr-alg:ties" and t[1] == "te" and t[6] == "10",
            "f64 ties te inexact")
t[5] = f"{int(t[5], 16) + 1:x}"
ls[i] = " ".join(t)
write("mut_ulp.vec", ls)
print(f"mut_ulp: f64 line {i+1} result +1 ulp")

# 3. stripped inexact on the study tie (f16 62c 67b).
ls = list(f16)
i, t = find(ls, lambda t: len(t) == 8 and "_hypot" in t[0] and t[1] == "te"
            and t[2] == "62c" and t[3] == "67b", "study tie")
assert t[6] == "10", t
t[6] = "00"
ls[i] = " ".join(t)
write("mut_noinexact.vec", ls)
print(f"mut_noinexact: f16 line {i+1} study-tie inexact stripped")

# 4. mode swap on a subnormal-output case: exchange tp/tn
# expectations for one f16 pair whose output is subnormal.
ls = list(f16)
groups = {}
order = []
for i, ln in enumerate(ls):
    t = ln.split()
    if len(t) == 8 and "_hypot" in t[0]:
        key = (t[2], t[3])
        if key not in groups:
            groups[key] = {}
            order.append(key)
        groups[key][t[1]] = i
done = False
for key in order:
    g = groups[key]
    if "tp" in g and "tn" in g:
        tp_t = ls[g["tp"]].split()
        tn_t = ls[g["tn"]].split()
        res = int(tp_t[5], 16)
        if 0 < res < 0x0400 and tp_t[5] != tn_t[5]:
            tp_t[5], tn_t[5] = tn_t[5], tp_t[5]
            tp_t[6], tn_t[6] = tn_t[6], tp_t[6]
            ls[g["tp"]] = " ".join(tp_t)
            ls[g["tn"]] = " ".join(tn_t)
            print(f"mut_modeswap: f16 pair {key} tp/tn swapped "
                  f"(subnormal output {tp_t[5]})")
            done = True
            break
assert done, "no f16 subnormal-output pair with tp != tn"
write("mut_modeswap.vec", ls)
