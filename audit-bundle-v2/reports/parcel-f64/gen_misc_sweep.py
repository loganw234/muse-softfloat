import sys, random, pathlib
sys.path.insert(0, "worktrees/w1-f64/tests")
sys.stdout.reconfigure(encoding="utf-8")
import gen_vectors_f64 as g

rng=random.Random(0xBEEF)
specials={"f64": g.pool64()+g.nan_pool64(), "f32": g.pool32()+g.nan_pool32()}
prov="exact-f64:misc-sweep-scratch"
out=[]
def rb(fmt): return g.rand_bits(rng, fmt, specials)

N=120000
modes_toint=[("ties_to_even","te",0),("ties_to_away","ta",0),("toward_zero","tz",0),
             ("toward_positive","tp",0),("toward_negative","tn",0),
             ("exact_ties_to_even","te",1),("exact_ties_to_away","ta",1),
             ("exact_toward_zero","tz",1),("exact_toward_positive","tp",1),
             ("exact_toward_negative","tn",1)]
itoks=list(g.INT_RANGES.keys())
rint_named=[("ties_to_even","te"),("ties_to_away","ta"),("toward_zero","tz"),
            ("toward_positive","tp"),("toward_negative","tn")]
for i in range(N):
    k=i%12
    if k==0:
        a,b=rb("f64"),rb("f64"); r,f=g.ref_remainder(a,b)
        out.append(g.line("msf64_remainder","-",[a,b],r,f,prov))
    elif k in (1,2):
        a=rb("f64"); suf,mode,ex=modes_toint[rng.randrange(10)]; itok=rng.choice(itoks)
        r,f=g.ref_to_int(a,mode,ex,itok)
        out.append(g.line("msf64_to_%s_%s"%(itok,suf),"-",[a],r,f,prov))
    elif k==3:
        itok=rng.choice(itoks); w=g.INT_RANGES[itok][2]
        lo,hi,_=g.INT_RANGES[itok]; v=rng.randrange(lo,hi+1)
        rm=rng.choice(g.RMS); r,f=g.ref_from_int(v,rm)
        out.append(g.line("msf64_from_"+itok,rm,[v&((1<<w)-1)],r,f,prov))
    elif k==4:
        a=rb("f64")
        if rng.random()<0.5:
            suf,mode=rint_named[rng.randrange(5)]; r,f=g.ref_rint(a,mode,0)
            out.append(g.line("msf64_round_to_integral_"+suf,"-",[a],r,f,prov))
        else:
            rm=rng.choice(g.RMS); r,f=g.ref_rint(a,rm,1)
            out.append(g.line("msf64_round_to_integral_exact",rm,[a],r,f,prov))
    elif k==5:
        a=rb("f64"); up=rng.random()<0.5; r,f=g.ref_next(a,up)
        out.append(g.line("msf64_next_up" if up else "msf64_next_down","-",[a],r,f,prov))
    elif k==6:
        a=rb("f64"); r,f=g.ref_logb(a)
        out.append(g.line("msf64_log_b","-",[a],r,f,prov))
    elif k==7:
        a,nb=rb("f64"),rb("f64"); rm=rng.choice(g.RMS); r,f=g.ref_scaleb(a,nb,rm)
        out.append(g.line("msf64_scale_b",rm,[a,nb],r,f,prov))
    elif k in (8,9):
        suf,code,sig=g.PREDICATES[rng.randrange(len(g.PREDICATES))]
        a=rb("f64")
        if rng.random()<0.5:
            b=rb("f64"); r,f=g.ref_compare("f64",a,"f64",b,code,sig)
            out.append(g.line("msf64_compare_"+suf,"-",[a,b],r,f,prov))
        else:
            b=rb("f32"); r,f=g.ref_compare("f64",a,"f32",b,code,sig)
            out.append(g.line("msf64_compare_%s_f32"%suf,"-",[a,b],r,f,prov))
    elif k==10:
        a,b=rb("f64"),rb("f64"); mag=rng.random()<0.5; r,f=g.ref_total(a,b,mag)
        out.append(g.line("msf64_total_order_mag" if mag else "msf64_total_order","-",[a,b],r,f,prov))
    else:
        fa=rng.choice(("f32","f64")); a=rb(fa); rm=rng.choice(g.RMS)
        r,f=g.ref_conv(fa,a,rm)
        out.append(g.line("msf64_from_"+fa,rm,[a],r,f,prov))
p=pathlib.Path("worktrees/w1-f64/build/w1/misc-sweep.vec")
g.write(p,out)
print("misc sweep cases",len(out))
