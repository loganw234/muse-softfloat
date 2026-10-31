import itertools
F = [16, 32, 64]
# predicate: (name, kind) kind: relation set and signaling flag
P = [("quiet_equal","E",0,0),("quiet_not_equal","LGU",0,0),("signaling_equal","E",1,0),("signaling_not_equal","LGU",1,0),
     ("quiet_greater","G",0,0),("quiet_greater_equal","GE",0,0),("quiet_less","L",0,0),("quiet_less_equal","LE",0,0),
     ("quiet_not_greater","LEU",0,0),("quiet_not_less","GEU",0,0),("quiet_less_unordered","LU",0,0),("quiet_greater_unordered","GU",0,0),
     ("quiet_unordered","U",0,0),("quiet_ordered","LGE",0,0),
     ("signaling_greater","G",1,0),("signaling_greater_equal","GE",1,0),("signaling_less","L",1,0),("signaling_less_equal","LE",1,0),
     ("signaling_not_greater","LEU",1,0),("signaling_not_less","GEU",1,0),("signaling_less_unordered","LU",1,0),("signaling_greater_unordered","GU",1,0)]
out, ents = [], []
for a, b in itertools.product(F, F):
    for name, rel, sig, _ in P:
        n = f"msf{a}_compare_{name}" + ("" if a == b else f"_f{b}")
        w = "w_" + n
        out.append(f"static int {w}(uint64_t x, uint64_t y, msf_flags_t *fl) {{ return {n}((msf{a}_t)x, (msf{b}_t)y, fl); }}")
        ents.append(f'{{"{n}", {a}, {b}, "{rel}", {sig}, {w}}}')
mm = ["minimum","maximum","minimum_number","maximum_number","minimum_magnitude","maximum_magnitude","minimum_magnitude_number","maximum_magnitude_number"]
mme = []
for d in F:
    for i, n0 in enumerate(mm):
        n = f"msf{d}_{n0}"; w = "w_" + n
        out.append(f"static uint64_t {w}(uint64_t x, uint64_t y, msf_flags_t *fl) {{ return (uint64_t){n}((msf{d}_t)x, (msf{d}_t)y, fl); }}")
        mme.append(f'{{"{n}", {d}, {i}, {w}}}')
with open("wrappers3.h", "w") as fh:
    fh.write("\n".join(out) + "\n")
    fh.write("static const CmpEnt CMPS[] = {\n " + ",\n ".join(ents) + "\n};\n")
    fh.write("static const MmEnt MMS[] = {\n " + ",\n ".join(mme) + "\n};\n")
print(len(ents), len(mme))
