# Vector format

One case per line, space-separated, `#` starts a comment, blank lines
are ignored. Every counted line carries a provenance tag as its last
field; a vector whose provenance the runner cannot print does not
count toward a gate (SF-0 Section 4.3).

Provenance budget (SF-1 Step 0a): the runner's tag table is capped
at `MAX_PROV` 128 and refuses rather than undercount. A new Tier 2
generator introduces one tag family per generator, not one per
function or file, and names its oracle and seed policy below at
merge. Raising the cap is seam work that must re-watch the
overflow refusal; it is never a silent constant bump.

## Public operations

```
<op> <rm> <args...> -> <result> <flags> <provenance>
```

- `<op>` is a generated API name from `docs/COVERAGE.tsv`.
- `<rm>` is `te|tz|tp|tn|ta` for attribute-taking operations
  (five attributes; `ta` = roundTiesToAway, SF-2 Step 1), `-`
  otherwise.
- `<args...>` are operand bit patterns as hexadecimal integers,
  truncated to the operation's kind width.
- `<result>` is the expected result bits (integers and predicates in
  plain hexadecimal too).
- `<flags>` is the expected flag delta as two hex digits (bits per
  `MSF_FLAG_*`), or `--` for operations that take no flags pointer.

Example:

```
msf16_class - 7e01 -> 1 -- exact-py:f16-exhaustive
```

## Augmented pairs (Clause 9.5, SF-2 Step 4)

```
<op> - <a> <b> -> <head> <tail> <flags> <provenance>
```

Two-result lines for the `aug_pair` signature only. `-` is
required: the clause fixes the rounding direction
(roundTiesTowardZero), so there is no attribute to state.
Both results and the flag delta compare exactly; no masking
mode applies. The board harness replies to a pair line with
`R <head> <tail> <flags>` and folds the two-result canonical
line (`<op> <a> <b> -> <head> <tail> <flags>`) into the
whole-run hash, byte-identical to the host runner's.

## The round-and-pack kernel (internal)

```
internal.pack16|pack32|pack64 <rm> <sign> <exp2> <sig128> <sticky> -> <result> <flags> <provenance>
```

`sign` and `sticky` are `0|1`, `exp2` is a signed decimal exponent,
`sig128` is up to 32 hex digits. Semantics: `msf_pack_generic` in
`src/msf_roundpack.c`. `<rm>` may also be `ta` (ties-to-away).

## Comparison directives

A `# compare=<mode>` comment line sets the comparison rule for the
rest of the file (the runner prints it in the file summary; default
`exact`): `nan-class` requires only a quiet NaN where a NaN is
expected; `berkeley-int` skips the delivered integer where invalid
is signaled. See runner.c for the exact rules. Masking is always
printed, never silent (SF-0 §4.3).

## Provenance tags in use

| tag | meaning |
|---|---|
| `exact-py:f16-exhaustive` | every binary16 encoding, expected values from the bit-decode reference in `tests/gen_vectors.py` |
| `exact-py:directed-encodings` | hand-directed exponent/payload edge sets per format, same reference |
| `exact-py:copysign-sample` | seeded sample of binary16 pairs (seed in the generator) |
| `exact-py:pack64-directed` | directed round/pack boundaries, expectations from the independent rational reference in `tests/gen_vectors.py` |
| `exact-py:pack32-directed`, `exact-py:pack16-directed` | same reference at binary32/binary16 parameters |
| `exact-py:pack64-sweep` | seeded random round/pack sweep, same reference |
| `berkeley:testfloat_gen-*` | streamed `testfloat_gen` output (from the P0 oracle bring-up onward; the runner inventory prints the oracle hash from the fetch record) |
| `exact-py-t2:directed-minmax` | Clause 9.6 directed class/sign/magnitude pool pairs at all 3 formats, expectations from the independent bit/rational reference in `tests/gen_vectors_tier2.py` (SF-1 Step 1) |
| `exact-py-t2:directed-payload` | Clause 9.7 directed payload boundaries at all 3 formats, same reference |
| `exact-py-t2:payload-f16-exhaustive` | generated at gate time: every binary16 encoding per payload op, plus `is_signaling` on every setter-result encoding |
| `exact-py-t2:minmax-f16-sweep` | generated at gate time: every binary16 encoding as second operand against named boundary first operands, all 8 min/max names |
| `exact-py-t2:seeded-sweep` | generated at gate time: seeded (20261027) binary32/64 pair and encoding sweeps, same reference |
| `mpfr640-trig:specials` | Clause 9.2 sinPi/cosPi specials (zeros, infinities, quiet/signaling NaN payload samples) at all 3 formats, expectations from MPFR at 640-bit precision via the bracketed decider in `tests/trig_exhaustive.c`, cross-checked by the settled-table reference in `tests/gen_vectors_trig.py` (SF-1 Step 2c) |
| `mpfr640-trig:anchors` | integer and half-integer anchors including the ulp>=1 region and +-1 ulp neighbours (both settled zero-sign cells in every mode), same decider |
| `mpfr640-trig:lattice` | k/8 lattice across 9 scales with +-3 ulp neighbours (bounce pairs around anchors), same decider |
| `mpfr640-trig:tiny` | smallest/largest subnormal and smallest-normal neighbourhood inputs (saturation family near +-1), same decider |
| `mpfr640-trig:hardest` | measured-hardest input excerpts: binary64 patterns from the published worst-case input sets (Step 2b mechanical census, inputs only), binary32 from a parcel mpmath margin scan, binary16 the spike-measured maxima; every expectation re-decided by the same MPFR decider |
| `mpfr640-trig:seeded` | seeded finite-encoding class sweep (seeds in the generator), same decider |
| `mpfr640-trig:<family>-ta-relabel` | SF-2 Step 1: the same input's decided `te` expectation relabeled `ta`; sinPi/cosPi of a dyadic input is never a rounding midpoint (Niven), so ta == te in bits and flags. Relabeled, NOT independently decided; theorem note in the parcel-w5attr report |
| `mpfr-alg:specials` | Clause 9.2 rSqrt+hypot specials at all 3 formats (signed zeros/infinities, quiet/signaling NaN payload samples, negative finite samples), expectations table-decided from the settled 9.2.1 cells in `tests/alg_decider.c` and `tests/gen_vectors_alg.py` and cross-checked - the `rSqrt(-0)` cell is never MPFR-sourced (SF-2 Step 2a) |
| `mpfr-alg:directed` | rSqrt+hypot directed exact/edge pool: perfect-square lattice (+-1 ulp neighbours), powers of two, smallest/largest subnormal, smallest normal, largest finite, same split as above: MPFR Step 0b operation recipe via `tests/alg_decider.c`, cross-decided per case by the generator's exact integer decider in all five modes |
| `mpfr-alg:ties` | rSqrt+hypot midpoint-adjacent constructions (encodings nearest the reciprocal square of sampled destination midpoints; exact ties are unattainable for rSqrt, so these are the hardest-to-round inputs), same decider split |
| `mpfr-alg:seeded` | rSqrt+hypot seeded sweep (seeds in the generator), same decider split |
| `mpfr-explog:specials` | Clause 9.2 exp2+exp2m1 specials at all 3 formats (signed zeros, infinities - not invalid for this bundle - quiet/signaling NaN payload samples), expectations from the adaptive-precision MPFR bracket decider in `tests/explog_decider.c` (five modes, first-principles grid narrowing), cross-checked by the settled-table reference in `tests/gen_vectors_explog.py` (SF-2 Step 3a) |
| `mpfr-explog:integers` | exp2+exp2m1 integer anchors: every exact/tie cell of the design table (exp2 at emin-p the u/2 tie, exp2m1 at p+1 and -(p+1) the binade-midpoint ties, exact powers/subnormal powers, overflow integers) with +-1 ulp neighbours, same decider split as above (C decider vs the generator's exact Fraction rounder, all five modes incl. ties-to-away) |
| `mpfr-explog:cuts` | exp2+exp2m1 kernel cut thresholds (emax+1, emax+2, emin-p, -(p+1)) at -3..+3 ulp, same decider |
| `mpfr-explog:lattice` | exp2+exp2m1 dyadic m/8 lattice at 7 scales with +-2 ulp neighbours, same decider |
| `mpfr-explog:tiny` | exp2+exp2m1 smallest/largest subnormal and smallest-normal neighbourhood inputs (near-1 composition family), same decider |
| `mpfr-explog:strips` | exp2m1 saturation strip ladder from -(p+1) upward and the exp2 subnormal-result strip around emin-p and overflow strip below emax+1, same decider |
| `mpfr-explog:hardest` | exp2+exp2m1 spike-measured plain-class hardest binary64 patterns (inputs only, SF-2 spike Sec. 2.1) with +-2 ulp neighbours, same decider |
| `mpfr-explog:seeded` | exp2+exp2m1 seeded finite-encoding class sweep (seeds in the generator), same decider |
| `mpfr-explog:*` (all families) | `ta` lines are INDEPENDENTLY decided by the five-mode decider (exact ties exist at integer inputs), never relabeled from `te` - the deliberate contrast with `mpfr640-trig:<family>-ta-relabel` |
| `mpfr-explog:specials` (log2/log2p1 lines) | Clause 9.2 log specials incl. the divideByZero poles (log2 at +-0, log2p1 at -1), domain-invalid cells (x<0 / x<-1 incl. -inf -> default qNaN), signed zeros (log2p1), +inf, NaN payload samples; same decider, cross-checked by the generator's independent settled-table restatement (SF-2 Step 3b) |
| `mpfr-explog:powers` | log2/log2p1 exact-power anchors (x=2^k incl. subnormal x; log2p1 x=2^k-1) with +-1 ulp neighbours - the only exact results (log2 of a dyadic is an integer or irrational; tie set empty, so no tie cells exist to anchor), same decider split |
| `mpfr-explog:sqrt2` | log significands straddling floor(sqrt2*2^(p-1)) - the exact recentring square-compare boundary - at several exponents (log2p1 both x-side and 1+x-side), same decider |
| `mpfr-explog:near1` | log x = 1 at -6..+6 ulp (log2 near-0 results; log2p1 w-near-2 attractor), same decider |
| `mpfr-explog:tiny` (log lines) | log smallest/largest subnormal neighbourhoods plus the +-2^-j ladder across the log2p1 tiny-path threshold 2^-8/2^-9 with +-1 ulp neighbours (identity-attractor family), same decider |
| `mpfr-explog:pole` | log2p1 pole neighbourhood: x=-1 at +-6 ulp and x=-1+2^-j approaches, same decider |
| `mpfr-explog:sticky` | log2p1 x=2^k (w=2^k+1 wide-span attractor; the s-division sticky Ek line decides these in directed modes) with +-2 ulp neighbours, same decider |
| `mpfr-explog:domain` | log negative-domain samples and largest-finite anchors (default-qNaN + invalid cells decided by the table on both sides), same decider |
| `mpfr-explog:lattice`/`hardest`/`seeded` (log lines) | log2/log2p1 share the exp bundle's lattice shape; hardest = spike plain-class maxima patterns (log2 0x7fe61555f75885b4, log2p1 0x44ee499f19ecc9fb, inputs only) +-2 ulp; seeded = per-function seeds in the generator; log `ta` lines are independently decided exactly as the exp rows state (no relabel, although the log tie set is empty) |

Berkeley's flag bits are ordered differently from `MSF_FLAG_*`
(inexact=1, underflow=2, overflow=4, infinite/divide-by-zero=8,
invalid=16, measured from its header at P0 bring-up). Berkeley
vectors are translated to our bit order at ingest, and the runner
prints the translation it applied; raw Berkeley flag bytes never
enter a committed vector file.

Generated vector files are produced into the build directory by
`tools/run.sh` (generate-and-replay; nothing budgets storage).
Small directed files under `tests/vectors/` are committed with their
generator named in the header line.
