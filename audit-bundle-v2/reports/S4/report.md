# S4 — IAS15 workload survey (REBOUND)

Surveyor S4, read-only. Date of survey: 2026-10-26.
Tags: **READ** = read in upstream source/docs at the pinned commit;
**MEASURED** = executed/compiled/counted by me this session;
**BELIEVED** = inference/recommendation, not observed upstream.
Every load-bearing claim carries a file:line or URL cite.

## 0. Provenance and licence (READ + MEASURED)

- Upstream: `https://github.com/hannorein/rebound`, shallow clone in
  `scratch/S4/rebound/` (my scratch only; nothing in the project repo changed).
- Pinned state (MEASURED, `git log -1`): commit
  `262a9cce102c69ca2cf7f3c6c1264e5e60002b7d`, 2026-10-16,
  "support netbsd and fix in Makefile for clang". `version.txt` = `5.2.2`.
  All `src/...:NNN` cites below are line numbers in that tree.
- **Licence (READ, exact):** file `LICENSE` at the repo root is the
  **GNU General Public License, Version 3, 29 June 2007** (full GPL-3.0 text,
  `LICENSE:1-4`). Per-file headers restate "either version 3 of the License,
  or (at your option) any later version" (e.g. `src/integrator_ias15.h:8-11`,
  `src/integrator_ias15.c:22-25`, `src/binarydata.h:11-14`). So: **GPL-3.0-or-later**.
  Consequence for a Pico port (BELIEVED, standard GPL reading): linking this
  code into a distributed firmware makes the combination GPL; a clean-room
  reimplementation from the papers avoids that, copying tables/code does not.
- Clean room: I did not open, search, or list anything with `cft` in its name,
  and followed no link to any `loganw234` cft project. The only third-party
  code read is hannorein/rebound plus the Rein & Tamayo 2017 arXiv paper.

## 1. IAS15 integrator source map

### 1.1 Who runs one step (READ)

Call chain for one accepted step (default build, no MPI/OpenMP/display):

```
reb_simulation_integrate / _steps            src/simulation.c:465,504
  reb_simulation_integrate_raw               src/simulation.c:372  (loop + exact-finish logic)
    reb_simulation_step (static)             src/simulation.c:517
      r->integrator.callbacks.step           src/simulation.c:530-531
        = reb_integrator_ias15_step          src/integrator_ias15.c:874
          while(!reb_integrator_ias15_step_try(r,state));   :878  (retry on reject)
            reb_integrator_ias15_alloc       src/integrator_ias15.c:244
            reb_simulation_update_acceleration  :297, and per stage :461
              -> gravity dispatch            src/simulation.c:643-692
                 REB_GRAVITY_BASIC (default) src/gravity.c:167  reb_gravity_basic_calculate_acceleration
                 REB_GRAVITY_COMPENSATED     src/gravity.c:284  reb_gravity_compensated_calculate_acceleration
                 (+ r->additional_forces(r) hook, src/simulation.c:689-691)
            predict_next_step                src/integrator_ias15.c:814 (end / on reject :742)
            copybuffers                      src/integrator_ias15.c:863
      post: boundary check, collision search (only if enabled),
            walltime bookkeeping             src/simulation.c:564-606
```

- Integrator registration object `reb_integrator_ias15` with `.step/.create/.free`
  and its binary field descriptors: `src/integrator_ias15.c:54-77`.
  Defaults at creation: `epsilon=1e-9`, `min_dt=0`, `adaptive_mode=PRS23`
  (`src/integrator_ias15.c:127-133`). IAS15 is the default integrator:
  `reb_simulation_create` calls `reb_simulation_set_integrator(r,"ias15")` and
  sets default gravity `REB_GRAVITY_BASIC`, `G=1`, `dt=0.001`
  (`src/simulation.c:98-122`). **Note: default gravity is the *uncompensated*
  BASIC routine, not COMPENSATED.**
- `reb_integrator_ias15_step` sets `gravity_ignore_terms=NONE`; for `N==0` it
  only advances `t`/`dt_last_done` (`src/integrator_ias15.c:874-883`). There is
  no `synchronize` callback for IAS15 (not set in `:54-77`), so
  `reb_simulation_synchronize` is a no-op for it.
- Files that execute in the default step path: `integrator_ias15.c`,
  `simulation.c` (dispatch, exit/finish logic, warnings), `gravity.c`
  (BASIC or COMPENSATED), `boundary.c` (only via `reb_boundary_get_ghostbox`,
  called once per ghost-box triple in BASIC — with open boundaries and
  `N_ghost_*=0` it returns the zero offset; COMPENSATED does not call it and
  ignores ghost boxes entirely), and `rebound.c` (message sink
  `reb_message`, `reb_sigint`). `tools.c` executes only if
  `r->calculate_megno` (MEGNO helpers, §2.4). Everything else in `src/`
  (other integrators, tree, collisions, display, server, output, archive)
  is off the default step path.

### 1.2 Coefficient storage: table constants, not computed (READ)

All Gauss–Radau coefficients are **hard-coded decimal table constants**,
`static const double`, in `src/integrator_ias15.c:182-193`:

| Table | Size | Line | Digits given |
|---|---|---|---|
| `safety_factor` | 1 (=0.25) | 182 | exact binary |
| `h[8]` Radau spacings | 8 | 185 | 28-31 sig. digits |
| `rr[28]` = h-differences | 28 | 187 | 25 sig. digits |
| `c[21]`, `d[21]` | 21+21 | 188-189 | 25 sig. digits |
| `w[8]` first-order weights (MEGNO only) | 8 | 193 | up to ~48 digits |

- They are **not** recomputed at runtime. An offline generator exists in the
  same file under `#ifdef GENERATE_CONSTANTS` (`:982-1067`, GMP `mpf_t` at
  512-bit precision, prints 25 digits, then `exit(0)`), but the enabling
  `#define GENERATE_CONSTANTS` is commented out (`:41-42`); it is dead code
  in any normal build. It documents the recurrences `rr=h_j-h_k` etc.
  (`:1010-1044`) if a port ever needs to regenerate tables in higher precision.
- Portability note (BELIEVED): the tables carry far more digits than a
  `double` holds, so the stored value is whatever the compiler's
  decimal→binary conversion produces. Bit-identical tables across compilers
  require correctly-rounded literal conversion (true for GCC/Clang and
  modern MSVC; still an assumption a Pico softfloat port must pin down —
  safest is to carry the constants as hex bit patterns in the port).
- Many further constants are **inline literals in expressions**, whose
  evaluation order is part of the numerics: the predictor polynomials use
  `7.*h/9., 3.*h/4., 5.*h/7., 2.*h/3., 3.*h/5., h/2., h/3.` (positions,
  `:419-421`) and `7./8. … 1./2.` variants (velocities, `:443-445`); the final
  series uses `/72.,/56.,/42.,/30.,/20.,/12.,/6.,/2.` for x and
  `/8.,/7.,/6.,/5.,/4.,/3.,/2.` for v, each as `b.pK[k]/DENOM*dt_done*dt_done`
  evaluated left-to-right (`:759-775`, with an explicit comment at `:757-758`
  that `dt_done*dt_done` is deliberately *not* precomputed, to avoid biased
  round-off at fixed dt). `predict_next_step` uses integer factors 7,6,…,210
  as doubles (`:844-850`, `:676-681`).

### 1.3 Predictor/corrector structure of one attempted step (READ)

`reb_integrator_ias15_step_try` (`src/integrator_ias15.c:280-812`) is the whole
algorithm. Sequence:

1. Ensure workspace (`reb_integrator_ias15_alloc`, `:281`; §4.2). Snapshot
   `x0,v0,a0` from particles (`:313-336`); snapshot compensated-acceleration
   residuals `csa0` from `gravity_cs` if gravity==COMPENSATED, else zero
   `csa0` (`:337-349`). Zero the per-attempt `csb` residuals (`:350-359`).
2. One acceleration evaluation at the step start (`:297`, before the loop;
   note it happens *before* the snapshot in source order — `a0` is read after).
3. Seed `g[0..6]` from the previous step's `b[0..6]` via the `d[]` table
   (`:361-369`). On the first step `b` is all zero (zeroed at alloc).
4. **Predictor–corrector loop** (`:386-606`), exits when any of (`:382-400`):
   `predictor_corrector_error < 1e-16`; or error stops decreasing
   (`iterations>2 && last <= current`); or `iterations>=12` (counts
   `iterations_max_exceeded`, warns once at the 10th such event, `:393-398`).
   Per iteration, for each Radau stage `n=1..7` (`:407-605`):
   set `r->t = t0 + dt*h[n]` (`:408`); predict positions from current `b`
   polynomial minus `csx` (`:411-433`); predict velocities *only if*
   MEGNO or velocity-dependent additional forces (`:434-458`); evaluate
   accelerations (`:461`); copy `at[]` (`:466-477`); then the stage's
   divided-difference update of `g.p{n-1}` and compensated update of
   `b.p0..p{n-1}` using `rr[]`/`c[]` (`:478-604`, seven near-identical cases).
   At stage 7 the corrector error is computed from the change in `b.p6`
   relative to `at[]` (`:579-600`; per-mode, §3).
   **Cost: 7 acceleration evaluations per iteration, plus the initial one;
   up to 12 iterations coded, i.e. up to 85 gravity evaluations per attempted
   step** (READ arithmetic). Typical iteration count is not stated in code.
5. New timestep chosen (§3, `:612-753`). If too small
   (`|dt_new/dt_done| < 0.25`): restore `x0,v0,a0` into particles, re-predict
   `b/e` from the saved `br/er`, return 0 → caller retries (`:709-746`).
6. Accept: final series accumulation into `x0/v0` with compensated summation
   (`:756-776`), `r->t += dt_done`, `dt_last_done=dt_done` (`:778-779`),
   write back to particles (`:787-806`), save `b→br, e→er` (two
   `copybuffers`, `:807-808`), then `predict_next_step(dt/dt_done)` to seed
   the next step's `b/e` (`:809-810`). `predict_next_step` zero-fills instead
   if `ratio > 20` (`:815-820`).

### 1.4 Compensated summation (READ)

One Kahan primitive, used pervasively:

```c
static inline void add_cs(double* p, double* csp, double inp){   // :237-242
    const double y = inp - *csp;
    const double t = *p + y;
    *csp = (t - *p) - y;
    *p = t;
}
```

Uses inside IAS15:

- **b-coefficient updates**: every `add_cs(&(b.pK[k]), &(csb.pK[k]), …)` in the
  seven stage cases (`:487,498-499,510-512,523-526,537-541,552-557,571-577`).
  `csb` is zeroed at each attempt (`:350-359`).
- **Stage acceleration differences**: `gk` starts as raw `at[k]` with the
  gravity routine's own residual `gravity_cs[k]`, then two compensated adds
  `-a0[k]` and `+csa0[k]` (`:484-485` and twins in every case). With BASIC
  gravity `gravity_cs` is aliased to the zeroed `csa0` array (`:345`), so the
  residuals are 0 but the Kahan path is still executed.
- **Final x/v series**: 9 compensated adds into `x0` (residual `csx`) and 8
  into `v0` (residual `csv`) per component (`:759-775`). **`csx/csv` persist
  across steps** — they are zeroed only when the workspace is (re)allocated
  (`:266-272`) — and the predictor polynomials subtract them (`-csx[k0] + …`,
  `:419`; `-csv[k0] + …`, `:443`). They are part of the saved integrator
  state (§4.3), so a restart that drops them is not bit-identical.
- **Gravity (COMPENSATED only)**: the same Kahan update inlined per pair per
  component, residuals in `r->gravity_cs[]` (`src/gravity.c:323-341` OpenMP
  form; `:430-468` sequential form). BASIC gravity uses plain `+=`
  (`src/gravity.c:207-212`).
- Softfloat relevance (BELIEVED): Kahan summation is destroyed by
  reassociation and changed by FMA contraction of its subexpressions; it is
  the single strongest reason the strict build in §5 forbids both. It also
  relies on round-to-nearest with no flush-to-zero: residuals are routinely
  subnormal-scale differences of nearly-equal numbers.

## 2. Complete inventory of FP operations beyond + − * /

Method (MEASURED): regex inventory script over the pinned tree
(`scratch/S4/inventory.py` → `scratch/S4/inventory.txt`), cross-checked by
reading every hit in the step path. Scope of "the step" = IAS15 file +
`reb_simulation_update_acceleration` + the gravity routine it dispatches to +
the `reb_simulation_step`/integrate wrapper.

### 2.1 In `src/integrator_ias15.c` (step + step-size control) (READ/MEASURED)

| Op | Count | Lines | Where |
|---|---|---|---|
| `sqrt()` | 3 calls (4 sites) | 690, 692 (×2), 701 | PRS23/AARSETH85 timescale + `sqrt(min_timescale2)` |
| `fabs()` | 10 | 581, 585, 592, 635, 637, 641, 652, 707, 709, 747 | error estimates, min_dt test, reject/cap tests |
| `copysign()` | 1 | 707 | `dt_new = copysign(min_dt, dt_new)` |
| `isnormal()` | 12 in step path | 200, 204, 582, 586, 593, 638, 642, 653, 659, 683, 695, 699 | guards on every max/error accumulation |
| `INFINITY` macro | 1 | 665 | initial `min_timescale2` |
| `sqrt7()` (own) | 2 calls | 660, 701 (def. 196-214) | 7th root, §3 — **replaces `pow`** |

Explicit negatives in this file (MEASURED by search): **no `pow` call**
(the only hit is the comment "Machine independent implementation of
pow(*,1./7.)", `:195`), **no `fmin/fmax`, no `fma/fmaf/fmal`, no trig/exp/log,
no `floor/ceil/fmod`, no `isnan/isinf/isfinite` calls, no `long double`,
no `float`**. All FP state is plain `double` (171 lines mention `double`).
Outside the step, the same file's `reb_integrator_ias15_timescale` helper
(`:886-980`, initial-dt helper, not called by the step) adds `sqrt` at
929, 974, 979 and `isnormal` at 906, 975, `INFINITY` at 897.

### 2.2 In gravity, as dispatched from the step (READ/MEASURED)

- Dispatch: `src/simulation.c:643-692`. BASIC
  (`src/gravity.c:167-282`): one **`sqrt`** per pair,
  `_r = sqrt(dx*dx+dy*dy+dz*dz+softening2)` (`:202` sequential active–active,
  `:243` test-particle; `:225,:268` are the `#else OPENMP` twins), then
  `prefact = G/(_r*_r*_r)` — i.e. `r⁻³` via two extra multiplies, **not**
  `pow` or rsqrt. Accumulation is plain `+=` in strict pair order
  `i=starti..N_active-1, j=startj..i-1` (`:195-214`), so the summation order
  (hence every rounding) is a function of particle index order.
- COMPENSATED (`src/gravity.c:284-531`): same single `sqrt` per pair
  (`:425,:482` sequential; `:319,:355,:390` OpenMP twins), but written
  `r2 = dx*dx+…; r = sqrt(r2); prefact = G/(r2*r)` (`:424-426`) — **a
  different rounding than BASIC's `G/(r*r*r)`**, so BASIC and COMPENSATED
  differ in the last bits even before compensation matters.
  No ghost boxes, no `reb_boundary_get_ghostbox` call in this routine.
- Off-default gravity in the same file (not in a direct-gravity step):
  JACOBI (`:108-165`, `sqrt` 129,146), TREE (`:47-107`, delegates to
  `tree.c`), variational BASIC (`:533-926`, `sqrt` at 563,602,650,702,793,
  874,905). Whole-file `sqrt` count = 18; **no other libm call anywhere in
  `gravity.c`** (no fabs/pow/fma), one `realloc` (§6).
- `additional_forces` user hook runs after gravity if set
  (`src/simulation.c:689-691`): arbitrary user FP, out of upstream's control;
  must be NULL for any reproducibility claim.

### 2.3 In the step wrapper (`src/simulation.c`) (READ/MEASURED)

- `copysign(1., r->dt)` for integration direction (`:311`), `tmax != INFINITY`
  test (`:317`), exact-finish `fabs(tmax)`, `fabs(r->t - tmax)` (`:323,327`),
  and `r->dt = copysign(r->dt, dt_sign)` (`:380`). These decide *whether and
  how big* the last step is, so they are part of step-size control.
- Only if `r->N_odes` (separate Bulirsch–Stoer ODEs, default off): `fabs` at
  `:540,546,547` plus everything in `integrator_bs.c` (which *does* call
  `pow` at `src/integrator_bs.c:522-523` — off the IAS15 path, but the one
  real `pow` in any integrator; MEASURED).
- Wallclock: `gettimeofday` twice per `reb_simulation_step`, then double
  arithmetic including `/1e6` into `walltime*` fields (`:518-603`).
  Numerically inert for the trajectory, but `walltime` is a saved binary
  field (§4.3), so whole-file byte compares see it.

### 2.4 Conditional: MEGNO (`src/tools.c`, only if `calculate_megno`) (READ)

`reb_tools_megno_deltad_delta` (`:1497-1516`) and `reb_tools_megno_update`
(`:1518-1536`): only `+ − * /` and `(double)` casts of the step counter —
**no libm calls**. But enabling MEGNO also flips on velocity prediction in
the step (`src/integrator_ias15.c:434`) and uses the `w[8]` table, so it
changes what the step computes even though it adds no transcendentals.
The rest of `tools.c` (orbits, random sampling: `pow/sin/cos/log/exp/cbrt/
atan2/sinh…`, 60+ `isnan` in particle constructors) is **never called by an
IAS15 step**; in a file-granular link it is pulled in by these two MEGNO
symbols only (dead-strippable, §6).

### 2.5 Types: no REAL typedef, no long double, no fma — anywhere (MEASURED)

Searched all 62 `src/*.[ch]` files (31,692 LOC total):

- **`long double`: 0 occurrences.** **`fma()/fmaf()/fmal()`: 0 calls.**
  **`__builtin_fma`: 0.** Any FMA in a build is purely a compiler contraction
  of `a*b+c` expressions (§5), never source-level.
- **`REAL`: no typedef exists.** The single hit is the English word in a
  comment (`src/frequency_analysis.c:117`, "SEPARATE REAL AND IMAGINARY
  PARTS"). There is **no compile-time precision switch**: every FP field in
  `reb_particle`, `reb_simulation`, and the IAS15 state is hardcoded
  `double` (`src/rebound.h:86-104,238-…`; `src/integrator_ias15.h:27-54`).
  A softfloat port changes the *implementation* of `double`, not a typedef.
- `float` appears only in display/GL types (`reb_vec3df`, `src/rebound.h:874-910`)
  and `display.c`'s one `powf` (`src/display.c:804`) — never in integration.
- `pow` in the whole tree: `tools.c:80,470,480,482` (random/Plummer
  sampling), `integrator_bs.c:522-523`, and the IAS15 comment. None in the
  IAS15 step path.

### 2.6 Places that assume IEEE-754 semantics (READ; softfloat checklist)

1. **`isnormal` as a finiteness+non-subnormal filter** (12 sites §2.1).
   Every error/max accumulation is `if (isnormal(x) && x > max) max = x;`.
   This silently *discards* zero, subnormal, Inf, and NaN candidates —
   correct only if classification matches IEEE exactly, including
   subnormals and signed zero (`isnormal(±0)==0`). A flush-to-zero
   softfloat would change *which* values pass, hence the chosen dt.
2. **Division by zero → Inf/NaN, then filtered, never trapped.** E.g.
   `errork = fabs(bk/ak)` with `ak==0` (`:592,652`), `maxb6/maxak` with both
   0 (`:599`), `v2*dt*dt/x2` with `x2==0` (`:635`), `epsilon/integrator_error`
   (`:660`), gravity `G/(r*r*r)` at `r==0` (coincident particles,
   `src/gravity.c:203`). All rely on non-trapping IEEE completion and on
   NaN comparisons being false so the `isnormal` guards can skip them.
3. **NaN comparison semantics in loop control.** If
   `predictor_corrector_error` becomes NaN (0/0 above), then
   `<1e-16` is false, `last <= current` is false, and only the
   `iterations>=12` cap terminates the loop (`:387-400`). Same style:
   `while(!step_try)` retry (`:878`) has **no retry bound** — a dt that
   keeps failing the 0.25 test loops forever (with `min_dt>0` the clamp
   guarantees eventual acceptance; with the default `min_dt=0` nothing in
   the code bounds it if errors stay NaN/huge).
4. **Inf arithmetic/comparison.** `min_timescale2 = INFINITY` then
   `timescale2 < min_timescale2` (`:665,695`); `tmax != INFINITY`
   (`simulation.c:317`); sentinel `1e300` (`:378`). Needs a real Inf that
   compares greater than every finite double and survives being copied.
5. **Signed zero / sign propagation.** `copysign(1.,dt)`,
   `copysign(min_dt,dt_new)`, `copysign(r->dt,dt_sign)` (§2.1/2.3) — the
   integration *direction* for `dt==±0` and for negative dt flows through
   the sign bit. `fabs` must map `-0→+0` for the `ak>maxak` idiom.
   Multiplying times/dts by `dtsign` (`simulation.c:319,350`) assumes
   `-1 * +0 == -0` style exactness only for comparisons, which IEEE gives.
6. **Correctly-rounded `sqrt` and `/`.** Gravity is `sqrt` + one division
   per pair; IAS15 divisions by `rr[]` constants and by small integers are
   everywhere. IEEE-754 mandates correct rounding for both — the port's
   softfloat sqrt/div must be correctly rounded (round-to-nearest-even)
   or trajectories diverge in the last bit immediately. The 7th root is
   safe by construction (own Newton iteration, §3) *provided* its +−*/
   are IEEE.
7. **Round-to-nearest, no reassociation, no excess precision.** The Kahan
   primitive `(t-*p)-y` (`:240`) is exact-zero only under RN with the
   written association; the long Horner chains (`:419-421,443-445,569`) and
   pair-ordered gravity sums are order-defined. Any x87-style excess
   precision or `-ffast-math` reassociation changes results (upstream says
   the same, §5.3).
8. **Decimal literal conversion.** Hundreds of literals (`1e-16`, `1e-9`,
   `5040.0`, all tables) must convert to the same doubles at compile time
   on host and target (see §1.2); runtime parsing is not involved in a step.
9. **Integer→double conversions** in the step path are only of small loop
   constants already written as literals; `(double)` counter casts occur
   in the MEGNO update and boundary code, exact for values < 2^53.
10. **No FP environment use:** no `fenv.h`, no rounding-mode changes, no
    exception-flag reads anywhere in `src/` (MEASURED: no `fesetround/
    fetestexcept` hits). The code assumes the default environment set by
    startup: RN, all exceptions masked. A port must guarantee the same at
    entry and after any IRQ/libcall.

## 3. Timestep adaptation, exactly as coded (READ)

All in `src/integrator_ias15.c:609-753`, executed only if `epsilon > 0`
(`:612`; `epsilon==0` ⇒ fixed `dt`, no adaptation, no rejection).
`safety_factor = 0.25` (`:182`). There are four `adaptive_mode`s
(`src/integrator_ias15.h:30-34`); default is **PRS23** (`:131`).

### 3.1 The "pow": there is none — `sqrt7(x) = x^(1/7)` by Newton (READ)

```c
// Machine independent implementation of pow(*,1./7.)          :195
static double sqrt7(double a){                                  :196
    double scale = 1;
    while(a<1e-7 && isnormal(a)){ scale *= 0.1;  a *= 1e7; }    :200-203
    while(a>1e2  && isnormal(a)){ scale *= 10;   a *= 1e-7; }   :204-207
    double x = 1.;
    for (size_t k=0; k<20;k++){                                 :209
        double x6 = x*x*x*x*x*x;                                :210
        x += (a/x6 - x)/7.;                                     :211
    }
    return x*scale;                                             :213
}
```

- **Exponent is exactly 1/7** at both call sites (below). Fixed 20 Newton
  iterations from `x=1`, no convergence test; argument pre-scaled by powers
  of 1e7 into ~[1e-7,1e2] (comment claims final validity [1e-14,1e8],
  `:197-198`). Outside that (0, subnormal, Inf, NaN, negative) the
  `isnormal` guards stop scaling and the iteration produces whatever it
  produces (e.g. `a=0` → x decays by factor 6/7 twenty times → tiny but
  nonzero; BELIEVED arithmetic, callers guard with `isnormal` first).
- This routine is *the* upstream reproducibility device: Rein & Tamayo 2017
  state they "implement our own routine to calculate 7th roots in order to
  avoid calling the machine-dependent pow() function"
  (https://ar5iv.labs.arxiv.org/html/1701.07423, §2). For a softfloat port
  it means **no libm pow is needed at all** — only IEEE +−*/ in this loop.

### 3.2 GLOBAL (old default) and INDIVIDUAL modes (`:625-663`)

Error estimate from the last series coefficient `b.p6` vs final acceleration
`at[]`:

- GLOBAL: `integrator_error = max_k|b.p6[k]| / max_k|at[k]|`, maxima taken
  only over `isnormal` values and skipping particles with
  `fabs(v2*dt*dt/x2) < 1e-16` (`:627-647`; note `integrator_error` is
  (re)assigned inside the particle loop, `:646` — equivalent to after-loop
  since maxima are monotone; if *every* particle is skipped it stays 0).
- INDIVIDUAL: `integrator_error = max_k |b.p6[k]/at[k]|` over `isnormal`
  ratios (`:648-657`).
- Then, exactly: **`dt_new = sqrt7(epsilon / integrator_error) * dt_done`**
  (`:660`), i.e. `dt_done · (epsilon/error)^(1/7)`. If the error is not
  normal (incl. 0): `dt_new = dt_done / safety_factor` = 4·dt_done (`:662`).

### 3.3 PRS23 (default) and AARSETH85 modes (`:664-705`)

Per particle i, from the b-polynomial at the step end (`:672-682`):
`y2=|a_end|², y3=|b0+2b1+…+7b6|², y4=|2b1+6b2+…+42b6|²,
y5=|6b2+24b3+…+210b6|²` (component sums; coefficients are derivative
multipliers, so y3/y4/y5 are |jerk·dt|², |snap·dt²|², |crackle·dt³|²).
Particles with non-normal `a0i=|a0|²` are skipped (`:683-687`). Then:

- PRS23: `timescale2 = 2.*y2/(y3 + sqrt(y4*y2))` (`:690`)
- AARSETH85: `timescale2 = (sqrt(y2*y4)+y3)/(sqrt(y3*y5)+y4)` (`:692`)
- `min_timescale2 = min over i` of normal values (`:695-697`), and exactly:

  **`dt_new = sqrt(min_timescale2) * dt_done * sqrt7(epsilon*5040.0)`** (`:701`)

  i.e. the 1/7 exponent now applies to the *constant* `5040·epsilon`
  (5040 = 7!, chosen to match the old GLOBAL scale at default epsilon,
  comment `:700`), not to a measured error. If no normal timescale:
  `dt_new = dt_done/safety_factor` (`:703`).
- The same PRS23 formula without the `sqrt7` factor is exposed for initial
  dt choice as `reb_integrator_ias15_timescale` (`:886-980`, final
  `return sqrt(min_timescale2)`, `:979`) — computed there from explicit
  pair jerk/snap terms rather than the b-polynomial.

### 3.4 Clamp, reject, cap — applied to every mode (READ)

In this order (`:707-752`):

1. `if (fabs(dt_new) < min_dt) dt_new = copysign(min_dt, dt_new);` (`:707`)
2. Reject: `if (fabs(dt_new/dt_done) < safety_factor /*0.25*/)` → restore
   particles, `r->dt = dt_new`, re-predict b/e unless first step, return 0
   (`:709-746`). The wrapper retries unboundedly (`:878`).
3. Cap growth: `if (fabs(dt_new/dt_done) > 1.0 && dt_new/dt_done > 1./safety_factor)
   dt_new = dt_done/safety_factor;` — max ×4 per step (`:747-751`).
   (Mixed signed/unsigned ratio tests as written; negative-dt integrations
   take the fabs branches first.)
4. `r->dt = dt_new` (`:752`); the *accepted* step always uses the old
   `dt_done` for its series (`:759-775`), then `predict_next_step(dt/dt_done)`.

Wrapper-level step-size interference (READ): with the default
`exact_finish_time=1`, `reb_check_exit` overwrites `r->dt = tmax - r->t`
for the last step (`src/simulation.c:318-341`) — an externally imposed dt
that bypasses IAS15's adaptation for that step (the step can still be
rejected and retried smaller by IAS15's own rule). Any bit-reproduction
harness must replicate this or disable `exact_finish_time`.

## 4. State layout, sizes, and raw-byte output routes

### 4.1 Particle layout and bytes/particle (READ + MEASURED)

`struct reb_particle` (`src/rebound.h:86-104`): 11 doubles in order
`x,y,z, vx,vy,vz, ax,ay,az, m, r` (=88 bytes, offsets 0..80), then three
pointers `name, ap, sim`, with `REB_PAD(4)` after each pointer on 32-bit
targets so the layout is width-independent (`src/rebound.h:31-38`).

MEASURED sizes (host gcc 16.1 32-bit MSYS via Git Bash, and
`arm-none-eabi-gcc 14.2.1 -mcpu=cortex-m0plus`, probe programs in
`scratch/S4/sizes.c`, `scratch/S4/arm_sizes.c`):

| Struct | Host32 (run) | Cortex-M0+ (nm -S) |
|---|---|---|
| `reb_particle` | **112 B** (name@88, ap@96, sim@104) | **112 B** (0x70) |
| `reb_vec3d` | 24 B | 24 B |
| `reb_simulation` | 592 B | 592 B (0x250) |
| `reb_integrator_ias15_state` | 88 B | 88 B (0x58) |
| `reb_binarydata_field` | 16 B | 16 B |
| `reb_simulationarchive_blob` | 12 B | 12 B |

BELIEVED (arithmetic from the PAD design): LP64 `reb_particle` is also
112 B (88 + 3×8, no pads) with identical double offsets; `reb_simulation`
and the IAS15 state are *not* width-stable (many pointers), but neither is
ever dumped whole (§4.3). The **FP state per particle is the first 88
bytes**; bytes 88-111 are pointers/padding and are meaningless off-process.

### 4.2 IAS15 workspace vs N (READ + MEASURED)

State struct `src/integrator_ias15.h:27-54`; allocation
`src/integrator_ias15.c:244-275`. With `Ntot = N + N_var` (or `N_map`),
`N3 = 3*Ntot`:

- 6 "dp7" arrays `g,e,b,csb,er,br`, each `7*N3` doubles = 42·N3 doubles.
- 7 flat arrays `at,x0,v0,a0,csx,csv,csa0`, each `N3` doubles = 7·N3.
- **Total = 49·N3 doubles = 147·Ntot doubles = 1176 bytes per particle**
  (MEASURED formula check: N=1→1,176 B; N=10→11,760 B; N=100→117,600 B),
  plus the 88-byte state struct, plus `Ntot × 112 B` particles, plus
  `N × 24 B` `gravity_cs` only under COMPENSATED gravity
  (`src/gravity.c:293-296`). Pico arithmetic (BELIEVED): N=10 needs
  ≈13 KB total FP workspace+particles; N=100 ≈129 KB — the workspace, not
  the particles, dominates by ~10:1, matching the paper's remark that an
  IAS15 snapshot is ~10× a WHFast one (arXiv:1701.07423, §3).
- Allocation is grow-only and rare: `realloc` of all 13 arrays only when
  `N3 > N_allocated` (`:252`). Quirk (READ): `realloc_dp7` re-zeroes the
  *entire* dp7 buffer after realloc (`:230-235`), so growing N mid-run
  wipes b/g/e history (and `csx/csv` are zeroed, `:266-272`) — a restart-
  from-scratch of the predictor, by design or by accident, but a port
  must reproduce it if it allows mid-run N changes.

### 4.3 Binary output routes suitable for bit comparison (READ)

Three routes, in increasing suitability:

**(a) In-memory serialization — best primitive.**
`reb_binarydata_simulation_to_stream(r,&buf,&size)`
(`src/binarydata.c:629-681`, public `REB_API` in `binarydata.h:72`):
64-byte ASCII header `"REBOUND Binary File. Version: <ver>\0<githash>"`
(`:638-641`; first 8 bytes as uint64 = `0x20444E554F424552` "REBOUND ",
`binarydata.c:38`), then a sequence of tagged fields
`{uint64 size_name; uint64 size_data} + name + raw native-endian data`
(`binarydata.h:83-86`, writer `:494-626`), then a `functionpointers` flag
field, an `end` field, and a 12-byte zeroed `reb_simulationarchive_blob`.
Field lists: simulation fields `binarydata.c:42-115` (t, G, dt, N,
particles as `N × sizeof(reb_particle)` **raw struct blob**, …), then
integrator fields with prefix `integrator.ias15.` from
`src/integrator_ias15.c:79-125` (epsilon, min_dt, adaptive_mode,
iterations_max_exceeded, and **all 13 workspace arrays** — this is what
makes restart bit-exact, cf. arXiv:1701.07423 §3 on storing IAS15's
internal arrays).

**(b) File form — Simulationarchive.** `reb_simulation_save_to_file`
(`src/simulationarchive.c:412-…`, public in `rebound.h:466`): first save
writes route (a) verbatim (`fopen("wb")`, `fwrite`, `:428-438`); saving
to an existing file *appends a diff stream* (fields differing from the
previous snapshot, via `reb_binarydata_diff` STREAM mode) + blob trailer
(`:588-609`). Readers: `reb_simulation_create_from_file(filename,snapshot)`
(`simulationarchive.c:95`, `rebound.h:425`). Auto-save variants by
interval/walltime/step (`rebound.h:468-472`). Docs:
`docs/binaryformat.md` (format), `docs/simulationarchive.md` (usage).

**(c) Built-in comparator.** `reb_simulation_diff(r1,r2,output_option)`
(`src/simulation.c:694-710`, `rebound.h:432-433`) and
`reb_simulation_diff_char` (`:621-634`) serialize both sims via (a) and
field-compare; particles are compared field-wise by `reb_particle_cmp`
(`src/particle.c`, `!=` on the 11 doubles **and on the `name` pointer** —
despite the header comment "ignoring pointers", `rebound.h:565`; `ap/sim`
are ignored). Return 0 iff equal.

**Caveats — why whole-file `cmp` is the wrong bit test** (READ):

1. The byte stream embeds non-trajectory data: version+git-hash header,
   `walltime`, `walltime_last_steps`, `rand_seed`, `steps_done`,
   `output_timing_last` (field list above) — two runs with identical
   trajectories differ in these bytes.
2. The `particles` blob includes raw pointer bytes (`name/ap/sim`) and,
   on 32-bit, pad bytes; `name_list` serialization even writes the
   *original pointer values* (`binarydata.c:603-614`, with the candid
   comment "This pointer arithmetic will fail on 32 bit architectures").
   Addresses differ run-to-run (ASLR/allocator), so raw bytes differ.
3. No endian or width conversion exists anywhere (MEASURED: no
   byteswap/hton in the format code; `REB_SIZE_T` fields write
   `sizeof(size_t)` bytes, `binarydata.c:524-529`). Files are portable
   only between same-endian, same-`size_t`-width builds in practice —
   an LP64 desktop file is **not** byte-identical to a 32-bit Pico file
   even with identical FP values.
4. Appended snapshots are diffs, not self-contained dumps (above).
5. `reb_particle_cmp` uses C `!=`: `-0.0` vs `+0.0` compare *equal* and
   `NaN != NaN` reports *differ* — it is a value comparator, not a
   bit comparator.

**Recommended bit-comparison protocol for this project** (BELIEVED):
serialize via route (a), parse fields, and byte-compare only the FP
payloads that define the trajectory: `t`, `dt`, `dt_last_done`, the first
88 bytes of each particle (or equivalently the 11 doubles), and — if
restart-equivalence is being tested — the 13 `integrator.ias15.*` arrays
+ `epsilon/min_dt/adaptive_mode`. On the Pico side, emit the same field
subset in a fixed little-endian, width-free framing and compare payloads.
Text output (`src/output.c`, `%e` formats `:265,286,337`) is *not*
bit-suitable: 6-digit default precision in several writers.

## 5. Desktop build: default flags, strict-IEEE flags, portability claims

### 5.1 What the default C build actually passes (READ)

There is no `OPTIMIZE` variable; the knob is `OPT`/`OPTLIB` in
`src/Makefile.defs`, included by the root `Makefile` and every example.
Non-Windows (`Makefile.defs:4-18,56-66`):

```
-std=c99 -Wpointer-arith -D_GNU_SOURCE -fPIC
Linux/FreeBSD/…:  -O3 -Wall -Wpedantic -Wno-strict-prototypes -g   (+ -Wextra for the lib)
Darwin:           -O3 -I/usr/local/include -Wall -Wpedantic -Wno-strict-prototypes -g
```

Measured negatives (searched `Makefile`, `src/Makefile`, `src/Makefile.defs`):
**no `-march`/`-mtune` anywhere, no `-ffast-math`/`-Ofast`, no
`-ffp-contract`, no `-fexcess-precision`, no `-mfpmath`**.
The install docs confirm no `-march=native` by default and suggest adding
it by hand for speed (`docs/quickstart/installation.md:112-118`).
Defaults also compile the web **SERVER on** (`Makefile.defs:90-92`,
`PREDEF+=-DSERVER` unless `SERVER=0`; examples export `SERVER=1`) and, on
x86_64, an AVX-512 assembly object for WHFast512 (`Makefile.defs:14-18`) —
both irrelevant to IAS15 numerics but extra code in a default build.
OpenMP is off unless `OPENMP=1` (`Makefile.defs:114-133`); MPI off unless
`MPI=1`. Windows C build: MSVC `/Ox /fp:precise` (`Makefile.defs:30`) —
already a strict-FP model — with `clang-cl` substituted when available
for AVX-512 (`:46-54`).

Python build (`setup.py:48-60`): non-Windows
`-fstrict-aliasing -std=c99 … -O3 -fPIC`; **`-ffp-contract=off` is added
only if the `FFP_CONTRACT_OFF` environment variable is set** (`:58-60`,
comment: "Turn off floating point contractions for bitwise
reproducibility"); on Windows x86_64 the forced clang-cl path always
appends `/clang:-ffp-contract=off` (`:81`). Docs tell users the same:
clang contracts by default; use `-ffp-contract=off` / `FFP_CONTRACT_OFF`
to reproduce exactly (`docs/quickstart/installation.md:119-124`).

**So (READ): a default desktop build does not, by itself, forbid FMA
contraction on FMA-baseline targets** (e.g. AArch64/clang). On baseline
x86-64 with no `-march`, the compiler has no FMA instruction to contract
into, which is (BELIEVED) why upstream gets away with leaving the flag
opt-in — but that is a property of the target, not of the build system.

### 5.2 Minimal strict-IEEE desktop flag set (BELIEVED — my recommendation)

Derived from §2.6's assumptions; upstream ships only the
`-ffp-contract=off` hint above, not this full set:

```
gcc/clang, library + problem:
  -std=c99 -O3            (keep upstream's std/opt level; -O level itself
                           is result-neutral under strict C99 FP rules)
  -ffp-contract=off       (no FMA contraction — the Kahan primitive and
                           Horner chains depend on it)
  -fno-fast-math -fno-unsafe-math-optimizations
                          (defensive: also blocks reassociation,
                           reciprocal approximations, finite-math-only
                           assumptions that would break isnormal/NaN logic)
  -fexcess-precision=standard
                          (no-op on x86-64/AArch64 SSE/NEON doubles;
                           essential if a 32-bit x86 build can see x87)
  (no -march=native; if a baseline must be named: -march=x86-64)
  OPENMP=0  MPI off  SERVER=0 OPENGL=0   (make variables)
MSVC: /Ox /fp:precise (already upstream default; never /fp:fast)
```

Two non-flag settings matter as much as flags (READ):
`OPENMP=1` changes gravity's summation order (BASIC switches from the
pair loop `src/gravity.c:196-214` to a per-i parallel loop `:217-232`;
COMPENSATED similarly `:310-343`) — results with OpenMP on are generally
**not bit-identical** to OpenMP off, regardless of FP flags. And
`additional_forces`, MEGNO, variational particles, and
`exact_finish_time` all change the computed step sequence (§2-3); pin
them in any cross-machine comparison.

### 5.3 Are results then portable-deterministic? Upstream claim vs evidence

Upstream's claim (READ): Rein & Tamayo 2017, "A new paradigm for
reproducing and analyzing N-body simulations" (MNRAS 467, 2377;
https://arxiv.org/abs/1701.07423) assert WHFast and IAS15 are "machine
independent" and simulations "automatically machine independent" when
initial conditions are shared in binary form. Their stated mechanism is
exactly what §2-3 verify in today's code: only IEEE-guaranteed ops in the
integrator, own 7th-root instead of `pow`, C99's no-rearrangement rule,
"-O3 is fine, --fast-math is not" (arXiv HTML §2). The docs repeat the
claim for the archive format ("still maintaining bit-wise
reproducibility", `docs/binaryformat.md:91`).

Assessment (BELIEVED, from the code read): the claim is **sound for the
IAS15+BASIC/COMPENSATED core under §5.2-style flags on IEEE hardware**,
because the complete libm surface is `sqrt` (IEEE correctly-rounded),
`fabs/copysign/isnormal` (exact classification/bit ops), and +−*/ — there
is genuinely no `pow`/trig/exp anywhere in the step. Residual risks, in
order: (1) FMA contraction if `-ffp-contract=off` is forgotten on
AArch64/clang (§5.1) — upstream knows, hence the opt-in env var; (2)
decimal-literal conversion differences in the long tables (§1.2);
(3) x87 excess precision on 32-bit x86 builds without
`-fexcess-precision=standard`; (4) OpenMP/test-particle/ghost-box and
`map` summation-order variants — deterministic per configuration, not
across configurations; (5) `sqrt7`'s fixed 20 iterations are only
"machine independent" because every op inside is IEEE — a softfloat
with a non-correctly-rounded division breaks it like everything else.
I found **no upstream issue or doc contradicting the claim** in the tree
or in web search (READ/MEASURED search, 2026-10-26); the
`FFP_CONTRACT_OFF` mechanism and the installation-page warning are the
upstream acknowledgment of risk (1). I did not run a cross-compiler
bit-comparison myself (survey is read-only; no second platform/compiler
pair was exercised) — portability beyond the code-level argument is
therefore BELIEVED, not MEASURED, in this report.

## 6. Minimal embeddable subset for a Pico port (direct gravity only)

Goal as briefed: IAS15 + direct (O(N²)) gravity, no collisions, no
output/display/server/archive machinery. Two ways to get there:

### 6.1 File-granular upstream link — does not shrink (READ/MEASURED)

Compiling upstream files whole pulls in far more than the step:
`simulation.c` references collisions, boundary, tree (via gravity),
archive, display/server hooks; `rebound.c`'s integrator registry uses
`REB_BUILTIN_INTEGRATORS` X-macro over **all 12 integrators**
(`src/rebound.c:65,74,94`; list in `src/rebound.h:205`), and
`integrator_ias15.c` itself references `tools.c` MEGNO symbols and the
binary-descriptor machinery. Without section garbage collection
(`-ffunction-sections -Wl,--gc-sections`) the linked set is effectively
the whole `src/Makefile:3` SOURCES list (~29 files, 31,692 LOC total in
`src/*.[ch]`, MEASURED). With gc-sections the *kept* code shrinks a lot
but every file must still compile (POSIX/GL/MPI headers, `gettimeofday`,
signals, sockets in `server.c`, etc.) — hostile to a bare-metal Pico
build. **Recommendation (BELIEVED): extract, don't link.**

### 6.2 Extracted subset — file list and rough LOC (READ basis, BELIEVED sizes)

Keep, in extract-and-trim form (upstream LOC measured; "kept" is my
estimate after deleting the named branches):

| Piece | Upstream source | LOC | Kept (est.) | Delete |
|---|---|---|---|---|
| IAS15 step core | `integrator_ias15.c` (+`.h` 59) | 1,067 | ~500-560 | field descriptors/binary glue (`:54-125` keep only create/free), `GENERATE_CONSTANTS` (`:982-1067`), timescale helper (`:886-980`), MEGNO branches, variational (`particles_var`) + `map` branches |
| Direct gravity | `gravity.c` (+`.h` 47) | 926 | ~70-110 | tree/jacobi/variational/jerk (all but one of BASIC or COMPENSATED sequential core, `:196-214` or `:416-470`), OpenMP twins, ghost boxes, test-particle splits (or keep, +30) |
| Sim/particle structs + step wrapper | `rebound.h` 913, `simulation.c` 874, `rebound.c` 515, `particle.c` 426 | 2,728 | ~150-250 | everything except: particle struct, minimal sim state (t, dt, G, softening, N), `update_acceleration` reduced to the one gravity call, integrate loop w/o heartbeat/display/archive/collision/walltime |
| Warning/error sink | `simulation.c:75-86` → `rebound.c:127-…` | ~40 | ~10 | replace with a no-op/counter stub |

**Total embeddable: roughly 750-950 lines of C99** (BELIEVED), dominated
by the irreducible step_try stage cases. External needs of that subset:
`<math.h>` only for `sqrt, fabs, copysign, isnormal, INFINITY`
(the latter four are trivial in a softfloat shim); `<string.h>` not
actually needed by the step (included at `integrator_ias15.c:39` but the
only memcpy is commented out, `:868-870`); `<stddef.h>/<stdint.h>` for
types. No file I/O, no signals, no `gettimeofday`, no threads if the
extract drops the wrapper's walltime code (`simulation.c:518-603`) — but
note the *upstream* `reb_simulation_step` calls `gettimeofday` twice per
step; dropping it changes nothing numerically.

Function-level keep-list (READ): `reb_integrator_ias15_create/free`,
`reb_integrator_ias15_step`, `reb_integrator_ias15_step_try`,
`reb_integrator_ias15_alloc`, `realloc_dp7`, `dpcast`, `add_cs`,
`sqrt7`, `predict_next_step`, `copybuffers`, the `h/rr/c/d` tables
(`w` only if MEGNO kept), `reb_gravity_basic_calculate_acceleration`
*or* `reb_gravity_compensated_calculate_acceleration` (pick one; they
round differently, §2.2 — BASIC is upstream's default), and a stub
`reb_simulation_warning`.

### 6.3 malloc / printf in the subset (MEASURED counts, READ sites)

- **IAS15:** `calloc` once at create (`integrator_ias15.c:128`);
  13 `realloc`s only when N grows (`:231,259-265`); 14 `free`s at destroy
  (`:137-150`). **Zero allocation per step at fixed N.** A Pico port can
  replace all of it with one static/arena block of `1176·Nmax + 88` bytes
  (§4.2) with identical numerics — allocation *pattern* is invisible to
  FP results except the re-zeroing quirk on growth (§4.2).
- **Gravity:** BASIC allocates nothing; COMPENSATED does one grow-only
  `realloc` of `gravity_cs` (`gravity.c:294`). Particles array itself is
  `realloc`-grown on add (`particle.c:56,188,196,207` area) — setup-time
  only, static array on Pico.
- **printf-family:** **none in the step path.** `integrator_ias15.c`
  printfs only inside the dead `GENERATE_CONSTANTS` block
  (`:985,1047-1064`). `gravity.c`: zero printf/fprintf (MEASURED).
  The one runtime message, the 10th-nonconvergence warning
  (`integrator_ias15.c:397`), travels `reb_simulation_warning` →
  `reb_message` (`rebound.c:127-149`, fprintf to stderr unless
  `save_messages`); a Pico stub (set a counter / UART line) preserves
  behavior visibility without stdio. Whole-upstream printfs live in
  output/binarydata/archive/server code, all excluded above.

### 6.4 Pico-specific notes (BELIEVED)

- RP2040 (Cortex-M0+) has no FPU; with the project's own softfloat,
  `double` ops are library calls — the step's cost drivers are the
  O(N²) sqrt/div pairs in gravity (7×iterations×pairs per step) and
  the long Horner chains. Nothing in the subset needs `pow`/trig/exp
  softfloat routines at all (the decisive fact of this survey).
- Keep `-ffp-contract=off` semantics in the toolchain sense: M0+ has no
  FMA, but the *desktop reference build* must be contraction-free for
  bit comparison (§5.2), and the compiler must not reassociate the Kahan
  code (`-fno-fast-math`, no unsafe optimizations) on either side.
- The unbounded reject-retry (`:878`) is a hang risk on-device: consider
  (deviating from upstream) `min_dt > 0`, which upstream code already
  supports and which bounds the loop in practice.
- GPL-3.0-or-later (§0) governs any copied tables/code.

## 7. Anything this brief got wrong

1. **"the exponent used in pow" presupposes a `pow` call — there is none.**
   IAS15 deliberately replaces `pow(x,1/7)` with its own `sqrt7` Newton
   routine (`integrator_ias15.c:195-214`); the exponent 1/7 never reaches
   libm. The only `pow` in any integrator is in Bulirsch–Stoer
   (`integrator_bs.c:522-523`), off-path.
2. **"REAL typedef switches" presupposes a precision-switch typedef — none
   exists.** No `REAL`, no `long double`, no build-time FP-width option
   anywhere in `src/` (§2.5). The port varies the implementation of
   `double`, not a source-level switch.
3. **`fma()` — none, at source level, anywhere.** FMA enters only via
   compiler contraction, which is why §5 is flags, not source.
4. **The brief's singular "the timestep adaptation formula" is four
   formulas** (INDIVIDUAL/GLOBAL/PRS23/AARSETH85) sharing one
   clamp/reject/cap tail, and the default changed in Jan 2024 to PRS23 —
   any older paper-derived expectation of `(eps/error)^(1/7)·dt` matches
   only the two legacy modes (§3).
5. **"Binary snapshot… suitable for bit comparison" needs qualification:**
   the upstream binary stream is *not* whole-file bit-comparable (embedded
   git hash, walltime, raw pointers in the particle blob, native
   `size_t`, diff-appended snapshots; §4.3). The suitable route is
   field-parsed payload comparison, as upstream's own `reb_simulation_diff`
   does.
6. **"OPTIMIZE" is not a REBOUND Makefile variable** (it's `OPT`/`OPTLIB`
   in `src/Makefile.defs`); and the default build is not contraction-safe
   on its own (`-ffp-contract=off` is opt-in via `FFP_CONTRACT_OFF` in the
   Python build only) — a strict desktop reference needs §5.2, not just
   `make`.
7. Minor: the brief implies compensated summation is an IAS15-internal
   detail to check; in fact there are *two independent* Kahan layers
   (integrator-internal, always on; gravity-level, only in the
   non-default COMPENSATED gravity, coupled via `gravity_cs`/`csa0`),
   and the default configuration (BASIC gravity) runs only the first.
8. Nothing in the brief was wrong about scope boundaries: IAS15+direct
   gravity does separate cleanly from collisions/output at the *function*
   level — but not at the *file* level (§6.1), which the brief's "file
   list" phrasing may have assumed.

— End of S4 report. Scratch artifacts: `scratch/S4/rebound/` (pinned
clone), `scratch/S4/inventory.py` / `inventory.txt`,
`scratch/S4/sizes.c`, `arm_sizes.c`, run scripts and outputs in
`scratch/S4/tmp/`.
