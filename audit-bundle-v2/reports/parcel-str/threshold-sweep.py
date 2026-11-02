import sys
sys.path.insert(0, r"C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w3-str\tests")
import gen_vectors_str as g

lines = ["# threshold corridor sweep (scratch)"]
mantissas = ["1", "1.7", "1.79", "1.8", "2.22", "2.5", "3.4", "3.41", "4.9",
             "6.55", "6.6", "7.4", "9.99", "1.0000000000000000001", "9.9999999999999999999"]
# exponent corridors crossing the C TU's per-format magnitude bands
exps = {
    "f16": list(range(-14, 0)) + list(range(0, 10)),
    "f32": list(range(-52, -36)) + list(range(34, 46)),
    "f64": list(range(-332, -316)) + list(range(302, 318)),
}
for fmt in ["f16", "f32", "f64"]:
    for m in mantissas:
        for e in exps[fmt]:
            for sgn in ["", "-"]:
                s = f"{sgn}{m}e{e}"
                for rm in g.RMS:
                    lines.append(g.from_dec_line(s, rm, fmt, "exact-str:threshold"))
    # hex corridors around emin/emax
    fp = g.fmt_params(fmt)
    for e2 in range(fp["emin"] - fp["p"] - 3, fp["emin"] - fp["p"] + 6):
        for hs in ["0x1p", "0x3p", "0x1.8p", "0xff.8p"]:
            for rm in g.RMS:
                lines.append(g.from_hex_line(f"{hs}{e2}", rm, fmt, "exact-str:threshold-hex"))
    for e2 in range(fp["emax"] - 2, fp["emax"] + 4):
        for hs in ["0x1p", "0x1.fffffffffffffp", "0x1.8p"]:
            for rm in g.RMS:
                lines.append(g.from_hex_line(f"{hs}{e2}", rm, fmt, "exact-str:threshold-hex"))
out = r"C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-str\bulk\threshold.vec"
import pathlib
pathlib.Path(out).write_bytes(("\n".join(lines) + "\n").encode())
print("wrote", len(lines) - 1, "threshold vectors")
