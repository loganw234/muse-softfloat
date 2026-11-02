import sys, pathlib
sys.path.insert(0,"worktrees/w1-f64/tests")
sys.stdout.reconfigure(encoding="utf-8")
import gen_vectors_f64 as g
from fractions import Fraction as F
out=[]
ns=[4999,5000,5001,6000,7000,8190,8191,8192,8193,10000]
xs=g.pool64()[:20]
for nv in ns:
    for s in (1,-1):
        nb=g.make_bits("f64", F(s*nv))
        # also fractional variant truncating to same int
        nbf=g.make_bits("f64", F(s*nv)+ (F(1,2) if s>0 else -F(1,2)))
        for a in xs:
            for rm in g.RMS:
                r,f=g.ref_scaleb(a,nb,rm); out.append(g.line("msf64_scale_b",rm,[a,nb],r,f,"exact-f64:scaleb-edge"))
                r,f=g.ref_scaleb(a,nbf,rm); out.append(g.line("msf64_scale_b",rm,[a,nbf],r,f,"exact-f64:scaleb-edge"))
g.write(pathlib.Path("worktrees/w1-f64/build/w1/scaleb-edge.vec"), out)
print(len(out))
