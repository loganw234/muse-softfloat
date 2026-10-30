
## 2026-10-27 05:49:50 -0700 - wave-1 binary32 parcel verified NOT READY (div 2x, div0 flag, sub inf sign)

NOT READY verdict on the wave-1 binary32 parcel (verify-f32 at 1779df0).

Measured: run.sh smoke PASS (29982 vectors) and standard PASS (+1117504) with all
9 negative controls refusing, but neither budget replays the parcel's own
*-f32.vec files; replaying them with the copy's runner gives 449 mismatches in
arith-f32.vec (400 div, 48 sub, 1 stale add line), all other f32 families PASS.
Berkeley differential over approx 2.01M level-1 cases: 1823008 pass; sub fails
335x5 modes (infinite operand sign flip); div fails 37989/37883/37883/37883/38005
(2x quotient plus missing divisionByZero, 1751 of them flag-only 00-vs-02). My
own exact-rational probe over 127958 directed cases passes every project-exact
family (next, scaleB, logB, totalOrder skeleton + payload antisymmetry, remainder,
22 compares incl cross-format, Exact variants, 8/16-bit ints, cross-format arith
incl midpoint traps, NaN matrix, saturation) with failures only at the same
three loci. Tables regenerate 4/4 identical; vectors 4/6 identical (arith:5 stale,
conv-int 16 benign operand-choice lines). implemented.tsv holds 173 wave-1 rows,
all msf32_.

### Root causes (all in src/msf32.c, none fixed)

Div 2x (all four div instantiations): exponent -62 at line 204 should be -63;
smallest repro msf32_div te 3f800000 3f800000. Missing div0 flag (same function,
lines 182-184): finite/zero returns infinity with flags 00, want 02. Sub
inf sign (all four sub instantiations, add_impl lines 122-127): infinite
subtrahend path returns INF32(b.sign) instead of the negated effb; smallest
repro msf32_sub te 0 7f800000, want ff800000. Stale committed line
arith-f32.vec:5 wants 80000000 for add(0,-tiny), true and regenerated value is
80000001 (implementation correct).

### Claim deviations

Shared files changed vs base 4cdb912 although expected byte-identical
(msf_roundpack.c Clause 7.5 tininess fix, gen_vectors.py same fix, ingest eq fix,
run.sh control-op swap, pack vec flag updates); the new tininess behavior is
independently corroborated by my probe, but the claim is false as stated, and the
HEAD (READY) message is contradicted by the 449 mismatches.

Believed: the three code defects are small, localized, and independently
reproducible; everything outside div/sub-homogeneous-and-cross is genuinely
clean across two independent oracles.

For: the lead, to send div/sub back for fixes, regenerate-and-rerun the parcel
gate over the full *-f32.vec set, and correct or re-scope the READY claim.
