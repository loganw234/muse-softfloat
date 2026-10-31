"""Independent check of the headline claim: run STOCK REBOUND 5.2.2 (PyPI wheel) on the project's
figure-8 initial conditions (bit patterns from board/ias15_ic.h) with the project's configuration
(G=1, dt0=0.01, eps=1e-9, min_dt=0, adaptive_mode=2/PRS23, BASIC gravity) and compare t, dt and
dt_last_done bit patterns with demo/expected-ias15.txt (2,001 records) step by step."""
import struct, sys, rebound
REPO = sys.argv[1]
def d(h): return struct.unpack(">d", struct.pack(">Q", h))[0]
def b(x): return struct.unpack(">Q", struct.pack(">d", x))[0]
P = [
 [0x3fef0a469565ad59,0xbfcf1d7dffb52c72,0,0x3fddd647fb166140,0x3fdbabe14f90b6f2,0x8000000000000000,0,0,0,0x3ff0000000000000,0],
 [0xbfef0a469565ad59,0x3fcf1d7dffb52c72,0,0x3fddd647fb166140,0x3fdbabe14f90b6f2,0x8000000000000000,0,0,0,0x3ff0000000000000,0],
 [0,0,0,0xbfedd647fb166140,0xbfebabe14f90b6f2,0,0,0,0,0x3ff0000000000000,0],
]
exp = [l.split() for l in open(REPO + "/demo/expected-ias15.txt") if l.strip() and not l.startswith("#")]
sim = rebound.Simulation()
sim.G = d(0x3ff0000000000000)
sim.integrator = "ias15"
sim.gravity = "basic"
sim.integrator.epsilon = d(0x3e112e0be826d695)
sim.integrator.min_dt = 0.0
sim.integrator.adaptive_mode = "PRS23"
sim.dt = d(0x3f847ae147ae147b)
for p in P:
    sim.add(m=d(p[9]), x=d(p[0]), y=d(p[1]), z=d(p[2]), vx=d(p[3]), vy=d(p[4]), vz=d(p[5]), r=d(p[10]))
print("rebound", rebound.__version__, rebound.__build__, "| N =", sim.N, "| eps bits", hex(b(sim.integrator.epsilon)), "| adaptive_mode", sim.integrator.adaptive_mode)
first_bad = None; nbad = 0; ncmp = 0
for k in range(0, 2001):
    if k > 0:
        sim.steps(1)
    got = ("%016x" % b(sim.t), "%016x" % b(sim.dt), "%016x" % b(sim.dt_last_done))
    want = (exp[k][3], exp[k][4], exp[k][5])
    ncmp += 1
    if got != want:
        nbad += 1
        if first_bad is None:
            first_bad = (k, got, want)
print("records compared:", ncmp, "| mismatching records (t,dt,dt_last_done):", nbad)
if first_bad:
    k, g, w = first_bad
    print("first mismatch at step", k, "\n  stock  :", g, "\n  project:", w)
    print("  t stock=%r project=%r" % (struct.unpack('>d', bytes.fromhex(g[0]))[0], struct.unpack('>d', bytes.fromhex(w[0]))[0]))
else:
    print("ALL t/dt/dt_last_done bit patterns identical to stock REBOUND 5.2.2 for steps 0..2000")

# ---- part 2: recompute the project's H_state (IAS15FH1, board/ias15_hash.c) from STOCK REBOUND state ----
import hashlib
def u64(x): return struct.pack("<Q", b(x))
def h_state(sim, k):
    h = hashlib.sha256()
    h.update(b"IAS15FH1"); h.update(bytes([0x53]))
    h.update(struct.pack("<Q", k)); h.update(struct.pack("<Q", sim.N))
    h.update(u64(sim.t)); h.update(u64(sim.dt)); h.update(u64(sim.dt_last_done)); h.update(u64(sim.G))
    for i in range(sim.N):
        p = sim.particles[i]
        for v in (p.x, p.y, p.z, p.vx, p.vy, p.vz, p.ax, p.ay, p.az, p.m, p.r):
            h.update(u64(v))
    return h.hexdigest()

sim2 = rebound.Simulation()
sim2.G = d(0x3ff0000000000000); sim2.integrator = "ias15"; sim2.gravity = "basic"
sim2.integrator.epsilon = d(0x3e112e0be826d695); sim2.integrator.min_dt = 0.0; sim2.integrator.adaptive_mode = "PRS23"
sim2.dt = d(0x3f847ae147ae147b)
for p in P:
    sim2.add(m=d(p[9]), x=d(p[0]), y=d(p[1]), z=d(p[2]), vx=d(p[3]), vy=d(p[4]), vz=d(p[5]), r=d(p[10]))
bad = 0; first = None
for k in range(0, 2001):
    if k > 0: sim2.steps(1)
    hs = h_state(sim2, k)
    if hs != exp[k][1]:
        bad += 1
        if first is None: first = (k, hs, exp[k][1])
print("H_state (particle state + t,dt,dt_last_done,G) recomputed from STOCK REBOUND vs committed: compared 2001, mismatches", bad)
if first: print("  first mismatch at step", first[0], "\n   stock  :", first[1], "\n   project:", first[2])
else: print("  ALL 2,001 H_state hashes identical -> every particle field (x y z vx vy vz ax ay az m r) bit-identical to stock REBOUND 5.2.2 at every step")
