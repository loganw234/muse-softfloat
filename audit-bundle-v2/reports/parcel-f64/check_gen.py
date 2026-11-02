import sys
sys.path.insert(0, "worktrees/w1-f64/tests")
sys.stdout.reconfigure(encoding="utf-8")
import gen_vectors_f64 as g
from fractions import Fraction as F
def show(name, val):
    print(name, val, [hex(x) if isinstance(x,int) else x for x in val] if isinstance(val,tuple) else val)
show("pack1.5", g.pack_value(F(3,2),"te"))
show("pack minsub/2 te", g.pack_value(F(2)**-1075,"te"))
show("pack minsub/2 tp", g.pack_value(F(2)**-1075,"tp"))
show("floorlog2 0.5", (g.floor_log2_frac(F(1,2)),))
show("floorlog2 3", (g.floor_log2_frac(F(3)),))
five=g.make_bits("f64",F(5)); three=g.make_bits("f64",F(3))
show("rem 5 3", g.ref_remainder(five,three))
print("expected -1 bits", hex(g.make_bits("f64",F(-1))))
show("sqrt2", g.ref_sqrt("f64", g.make_bits("f64",F(2)),"te"))
show("div1/3", g.ref_div("f64", g.make_bits("f64",F(1)), "f64", three, "te"))
show("rint -0.4ish te", g.ref_rint(g.make_bits("f64",F(-1,4)),"te",1))
show("toint 127.5 i8 te exact", g.ref_to_int(g.make_bits("f64",F(255,2)),"te",1,"i8"))
show("toint 126.5 i8 te exact", g.ref_to_int(g.make_bits("f64",F(253,2)),"te",1,"i8"))
show("toint -0.5 u8 tn exact", g.ref_to_int(g.make_bits("f64",F(-1,2)),"tn",1,"u8"))
show("scaleb 1, -inf", g.ref_scaleb(g.make_bits("f64",F(1)), 0xFFF0000000000000,"te"))
show("logb minsub", g.ref_logb(1))
print("pools", len(g.pool64()), len(g.pool32()))
print("SMALL SWEEP")
for ln in g.sweep(20, 42, "t"):
    print(ln)
