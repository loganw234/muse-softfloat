# Generates wrappers.h: uniform uint64 wrappers + tables for the library's
# arithmetic entry points (homogeneous and formatOf mixed-format forms).
import itertools
F = [16, 32, 64]
def nm(op, d, srcs):
    if all(s == d for s in srcs):
        return f"msf{d}_{op}"
    return f"msf{d}_{op}_" + "_".join(f"f{s}" for s in srcs)
out = []
bins, uns, fmas, convs = [], [], [], []
for op in ["add", "sub", "mul", "div"]:
    for d, a, b in itertools.product(F, F, F):
        n = nm(op, d, [a, b]); w = "w_" + n
        out.append(f"static uint64_t {w}(uint64_t a, uint64_t b, int rm, msf_flags_t *fl) {{ return (uint64_t){n}((msf{a}_t)a, (msf{b}_t)b, (msf_rounding_t)rm, fl); }}")
        bins.append(f'{{"{n}", OP_{op.upper()}, {d}, {a}, {b}, {w}}}')
for d, a in itertools.product(F, F):
    n = nm("sqrt", d, [a]); w = "w_" + n
    out.append(f"static uint64_t {w}(uint64_t a, int rm, msf_flags_t *fl) {{ return (uint64_t){n}((msf{a}_t)a, (msf_rounding_t)rm, fl); }}")
    uns.append(f'{{"{n}", OP_SQRT, {d}, {a}, {w}}}')
    n = f"msf{d}_from_f{a}"; w = "w_" + n
    out.append(f"static uint64_t {w}(uint64_t a, int rm, msf_flags_t *fl) {{ return (uint64_t){n}((msf{a}_t)a, (msf_rounding_t)rm, fl); }}")
    uns.append(f'{{"{n}", OP_CONV, {d}, {a}, {w}}}')
for d, a, b, c in itertools.product(F, F, F, F):
    n = nm("fma", d, [a, b, c]); w = "w_" + n
    out.append(f"static uint64_t {w}(uint64_t a, uint64_t b, uint64_t c, int rm, msf_flags_t *fl) {{ return (uint64_t){n}((msf{a}_t)a, (msf{b}_t)b, (msf{c}_t)c, (msf_rounding_t)rm, fl); }}")
    fmas.append(f'{{"{n}", {d}, {a}, {b}, {c}, {w}}}')
with open("wrappers.h", "w") as fh:
    fh.write("\n".join(out) + "\n")
    fh.write("static const BinEnt BINS[] = {\n " + ",\n ".join(bins) + "\n};\n")
    fh.write("static const UnEnt UNS[] = {\n " + ",\n ".join(uns) + "\n};\n")
    fh.write("static const FmaEnt FMAS[] = {\n " + ",\n ".join(fmas) + "\n};\n")
print(len(bins), len(uns), len(fmas))

# integer conversions
ints = [("i",8),("u",8),("i",16),("u",16),("i",32),("u",32),("i",64),("u",64)]
ctype = lambda k,n: f"{'int' if k=='i' else 'uint'}{n}_t"
modes = ["ties_to_even","toward_zero","toward_positive","toward_negative","ties_to_away"]  # library mode order 0..4
o2, fr, to = [], [], []
for d in F:
    for k,n in ints:
        nmf = f"msf{d}_from_{k}{n}"; w = "w_"+nmf
        o2.append(f"static uint64_t {w}(uint64_t a, int rm, msf_flags_t *fl) {{ return (uint64_t){nmf}(({ctype(k,n)})a, (msf_rounding_t)rm, fl); }}")
        fr.append(f'{{"{nmf}", {d}, {1 if k=="i" else 0}, {n}, {w}}}')
        for ex in [0,1]:
            for mi,mname in enumerate(modes):
                nmt = f"msf{d}_to_{k}{n}_{'exact_' if ex else ''}{mname}"; w = "w_"+nmt
                o2.append(f"static uint64_t {w}(uint64_t a, msf_flags_t *fl) {{ return (uint64_t)({ctype(k,n)}){nmt}((msf{d}_t)a, fl); }}")
                to.append(f'{{"{nmt}", {d}, {1 if k=="i" else 0}, {n}, {ex}, {mi}, {w}}}')
rti = []
for d in F:
    for mi,mname in enumerate(modes):
        nmr = f"msf{d}_round_to_integral_{mname}"; w = "w_"+nmr
        o2.append(f"static uint64_t {w}(uint64_t a, int rm, msf_flags_t *fl) {{ (void)rm; return (uint64_t){nmr}((msf{d}_t)a, fl); }}")
        rti.append(f'{{"{nmr}", {d}, 0, {mi}, {w}}}')
    nmr = f"msf{d}_round_to_integral_exact"; w = "w_"+nmr
    o2.append(f"static uint64_t {w}(uint64_t a, int rm, msf_flags_t *fl) {{ return (uint64_t){nmr}((msf{d}_t)a, (msf_rounding_t)rm, fl); }}")
    rti.append(f'{{"{nmr}", {d}, 1, -1, {w}}}')
with open("wrappers2.h", "w") as fh:
    fh.write("\n".join(o2) + "\n")
    fh.write("static const FromEnt FROMS[] = {\n " + ",\n ".join(fr) + "\n};\n")
    fh.write("static const ToEnt TOS[] = {\n " + ",\n ".join(to) + "\n};\n")
    fh.write("static const RtiEnt RTIS[] = {\n " + ",\n ".join(rti) + "\n};\n")
print(len(fr), len(to), len(rti))
