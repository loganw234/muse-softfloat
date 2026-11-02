import sys
sys.path.insert(0, "tests")
import gen_vectors_str as g

for fmt in ("f16", "f32", "f64"):
    fp = g.fmt_params(fmt)
    p = fp["p"]
    qs = [1 << (p - 1), (1 << (p - 1)) + 2, (1 << p) - 2,
          (1 << (p - 1)) + (1 << (p // 2 + 1))]
    for big_e in (0, -7, 9, fp["emin"] + 3, fp["emin"], fp["emin"] - 1, fp["emin"] - 6):
        for q in qs:
            odd = 2 * q + 1
            e2 = big_e - p
            if e2 >= 0:
                digs = str(odd << e2); dexp = len(digs) - 1
            else:
                digs = str(odd * 5 ** (-e2)); dexp = len(digs) - 1 + e2
            kept = digs[:g.H]
            info = ""
            if len(digs) > g.H + 1 and int(kept[-1]) % 2 == 0:
                s = kept[0] + "." + kept[1:] + "50000" + f"e{dexp}"
                te = g.from_decimal_ref(s, "te", fmt)[:2]
                ta = g.from_decimal_ref(s, "ta", fmt)[:2]
                info = f" CAND te={te} ta={ta} diff={te != ta} s={s}"
            print(fmt, "big_e", big_e, "q", q, "len", len(digs), "last20", kept[-1] if len(digs) >= 20 else "-", info)
