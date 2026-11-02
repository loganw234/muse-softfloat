import pathlib, re, collections
p=pathlib.Path("scratch/parcel-f32/regate-berkeley-results.log")
jobs=[]
for line in p.read_text().splitlines():
    m=re.match(r"JOB (\S+) cases=(\d+) verify=(\S+)", line)
    if m: jobs.append((m.group(1), int(m.group(2)), m.group(3)))
print("jobs", len(jobs), "cases", sum(n for _,n,_ in jobs), "non-PASS", [j for j in jobs if j[2]!="PASS"])
def s(pred,label):
    sel=[j for j in jobs if pred(j[0])]
    print(label, "jobs", len(sel), "cases", sum(n for _,n,_ in sel), [t for t,_,_ in sel])
s(lambda t: t.startswith(("f32_mul-","f32_div-")) and "-l1" in t, "mul/div L1 all modes")
s(lambda t: t.startswith(("f32_mul-","f32_div-")) and "-l2" in t, "mul/div L2 te+tz")
s(lambda t: t.startswith(("f32_mul-te-l2","f32_div-te-l2")), "mul/div L2 te only")
s(lambda t: t.startswith("f32_mulAdd"), "mulAdd L1 take2M all modes")
s(lambda t: t=="f32_eq---l1", "eq")
s(lambda t: t=="f32_eq_signaling---l1", "eq_signaling")
blocked = sum(n for t,n,_ in jobs if (t.startswith(("f32_mul-","f32_div-"))) or t.startswith("f32_mulAdd") or t in ("f32_eq---l1","f32_eq_signaling---l1"))
print("blocked+extra (mul/div all incl L2tz, mulAdd, eq, eq_sig) cases", blocked)
# pre-fix failing-case total from report: mul L1 16+13+12+16=57, div 8+14+15+8=45, L2 28+5, mulAdd 134+316+317+134=901, eq1967
print("pre-fix failing cases named in report:", 57+45+33+901+1967)
