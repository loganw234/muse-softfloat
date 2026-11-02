import pathlib, random, sys
sys.path.insert(0, r"C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w3-str\tests")
import gen_vectors_str as g

S = r"C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-str"
rng = random.Random(31337)
lines = ["# long-string sweep (scratch)"]
fmts = ["f16", "f32", "f64"]
for i in range(6000):
    fmt = fmts[i % 3]
    rm = rng.choice(g.RMS)
    nd = rng.randint(21, 800)
    digits = rng.choice("123456789") + "".join(rng.choice("0123456789") for _ in range(nd - 1))
    dexp = rng.randint(-330, 315)
    s = f"{rng.choice(['','-'])}{digits[0]}.{digits[1:]}e{dexp}"
    lines.append(g.from_dec_line(s, rm, fmt, "exact-str:long-dec"))
for i in range(3000):
    fmt = fmts[i % 3]
    rm = rng.choice(g.RMS)
    nd = rng.randint(33, 300)
    digs = "".join(rng.choice("0123456789abcdef") for _ in range(nd))
    p = rng.randint(-1200, 1200)
    s = f"{rng.choice(['','-'])}0x{digs[0]}.{digs[1:]}p{p}"
    lines.append(g.from_hex_line(s, rm, fmt, "exact-str:long-hex"))
# exact full-length midpoints (beyond H) at random binades per fmt
for fmt in fmts:
    fp = g.fmt_params(fmt)
    for _ in range(60):
        q = rng.getrandbits(fp["p"]) | (1 << (fp["p"] - 1))
        e2 = rng.randint(fp["emin"] - fp["p"], fp["emax"] - fp["p"])
        s = g._midpoint_string(2 * q + 1, e2)
        if len(s) > 3000:
            continue
        for rm in g.RMS:
            lines.append(g.from_dec_line(s, rm, fmt, "exact-str:long-mid"))
out = S + r"\bulk\longstring.vec"
pathlib.Path(out).write_bytes(("\n".join(lines) + "\n").encode())
print("wrote", len(lines) - 1)
