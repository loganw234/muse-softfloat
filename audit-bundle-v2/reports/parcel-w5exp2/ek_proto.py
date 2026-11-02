import math
from fractions import Fraction
import mpmath

def ln2_frac(dps):
    mpmath.mp.dps = dps
    v = mpmath.mp.log(2)
    sign, man, exp, _ = v._mpf_
    assert sign == 0
    return Fraction(man) * Fraction(2) ** exp

a = ln2_frac(260); b = ln2_frac(210)
diff = abs(a-b)
print("ln2 diff ~2^", math.log2(float(diff)))
assert diff < Fraction(2)**-600
U = (a + Fraction(2)**-590) / 2
print("U < 0.34658:", U < Fraction(34658,100000), float(U))

def tail_exp(K):
    return U**K / Fraction(math.factorial(K)) / (1 - U/Fraction(K+1))
def tail_m(K):
    return U**K / Fraction(math.factorial(K+1)) / (1 - U/Fraction(K+2))

def terms(W):
    K=1
    while True:
        if tail_exp(K) <= Fraction(2)**-(W+24) and tail_m(K) <= Fraction(2)**-(W+24):
            return K
        K+=1

def ek(W,K):
    eps = Fraction(2, 2**W)
    e_u = 2*eps + eps*eps
    # exp horner
    e = eps
    for k in range(K-2,-1,-1):
        rho = U / (Fraction(k+1)*(1 - U/Fraction(k+2)))
        e_prod = e_u + e + e_u*e + eps
        e = eps + rho*e_prod + eps
    e_v = e + tail_exp(K)
    # M horner: coeffs c_{k} for k=1..K, P_k = sum_{j>=k} u^{j-k}/(j+1)!
    e = eps
    for k in range(K-1,0,-1):
        rho = U / (Fraction(k+2)*(1 - U/Fraction(k+3)))
        e_prod = e_u + e + e_u*e + eps
        e = eps + rho*e_prod + eps
    e_m = e_u + e + e_u*e + eps + tail_m(K)
    bound = max(e_v, e_m)
    bits=0
    while Fraction(2)**-(bits+1) >= bound:
        bits+=1
    return bits-9, float(bound)

for W in (160,256,384):
    K=terms(W)
    E,bd = ek(W,K)
    print(f"W={W} K={K} EkExp={E} bound~{bd:.3e} tail_exp<={float(tail_exp(K)):.2e}")
