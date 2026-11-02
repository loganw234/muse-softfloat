import mpmath

mpmath.mp.dps = 50
for name, x in [("2^-1074", mpmath.mpf(2) ** -1074),
                ("(2^52-1)*2^-1074", (2**52 - 1) * mpmath.mpf(2) ** -1074),
                ("2^-1022", mpmath.mpf(2) ** -1022)]:
    # 1-cospi(x) = 2 sinpi(x/2)^2, computed without cancellation
    d = 2 * mpmath.sinpi(x / 2) ** 2
    print(name, "1-cospi(x) =", mpmath.nstr(d, 8), "positive:", d > 0)
print("true cosPi(x) < 1 strictly -> tz/tn must deliver next below 1")
