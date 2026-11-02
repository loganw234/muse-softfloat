import pathlib
p=pathlib.Path("worktrees/w1-f32/build/w1/f32_rem-l1.vec")
def cls32(b):
    e=(b>>23)&0xff; f=b&0x7fffff
    if e==0xff: return "inf" if f==0 else "nan"
    if e==0: return "zero" if f==0 else "sub"
    return "norm"
hits=[]
subres=[]
for line in p.read_text().splitlines():
    if line.startswith('#') or not line.strip(): continue
    t=line.split()
    # op rm a b -> r flags prov
    a=int(t[2],16); b=int(t[3],16); r=int(t[5],16); fl=int(t[6],16)
    if cls32(b)=="inf" and cls32(a)=="sub":
        hits.append(line)
    if cls32(r)=="sub" and fl:
        subres.append(line)
print("subnormal x, inf y cases:", len(hits))
for h in hits[:10]: print(h)
print("subnormal results with any flag:", len(subres))
for h in subres[:10]: print(h)
