
## 2026-10-26 21:55:22 -0700 - Design entry: 173 binary64 instantiations, kernel instances and special tables

Measured: base worktrees/w1-f64 at 4cdb912, clean at entry; docs/COVERAGE.tsv filtered wave=1 and name prefix msf64_ gives exactly 173 rows (script scratch/parcel-f64/inspect2.py, wave-1 total 346). Kernel headers read in full: msf_decode (value sig times 2^exp, NaN matrix if/else chain), msf_pack_generic domain (sig plus fraction below 1 unit recorded by sticky; sig zero with sticky outside domain), msf_u128 ops in msf_wide.c, runner compare modes, berkeley_ingest mappings. S1 extracts read for 5.3.1, 5.3.3, 5.8, 5.9, 5.10, 5.11, 6.3, 7.3 wording only; clause numbers cited, no standard text copied.
Believed: the design below builds every mandated kernel shape as specified; no mandate objection at entry time. Berkeley level-1/2 runs and project-exact sets are the test of the believed parts (remainder sign, scaleB infinite-N clamp, toInt Exact inexact scope).
For: lead, parcel-f32, verifier-w1

Design entry, parcel-f64 (binary64 destination; sources in {f32,f64} for wave 1).

Shared shape for every op: decode operands with msf_decode into (sign, class, sig, exp) with value sig times 2^exp. Deliver NaNs first through msf_nan_delivery at destination f64 in operand order (FMA order multiplicand, multiplier, addend), passing invalid_without_nan computed per op below; the helper signals invalid for a signaling input and for the no-NaN invalid case, and delivers the first quiet input without invalid otherwise. Then special infinite/zero cases, then one exact integer computation over msf_u128, then exactly one msf_pack_f64 (no intermediate rounding). Public rm values 0 to 3 map to the internal enum unchanged; ties-to-away (internal 4) appears only in named forms.

### General special-value rules (Clauses 6 and 7)

Sign of a product or quotient is the XOR of operand signs, zeros included. A zero sum from opposite effective signs is +0 in every mode except roundTowardNegative, where it is -0; a zero sum from like effective signs keeps that sign, so -0 plus -0 is -0. Overflow, underflow (tininess after rounding), and inexact come only from the single pack, except where an op below suppresses or adds inexact by name. Invalid cases with no NaN input deliver the default quiet NaN through the helper.

### add and sub (5.4.1, 4 dest/source combos each)

Specials: any NaN by helper. Opposite-signed infinities under the effective operation (inf plus -inf, inf minus inf) are invalid_without_nan. A single infinity, or two like-signed, deliver that infinity. Finite path: form both significands on one common scale aligned to the larger (dominant) exponent inside a 118-bit window (exact left shift when the scale gap is small, msf_u128_shr_jam for the smaller-exponent operand when the gap exceeds the window, which can only happen when that operand sits many bits below the dominant top so the jam bit can serve only as sticky evidence far below the round bit), add or subtract magnitudes by effective signs (sub flips the second sign), sign of the larger magnitude on subtraction, exact-zero sign per the rule above, one pack. Flags only from pack.

### mul (5.4.1)

Specials: NaN by helper; zero times infinity is invalid_without_nan. Infinity times nonzero (finite or infinite) is infinity with XOR sign; zero times finite is zero with XOR sign. Finite: msf_u128_mul_u64_u64 of the two significands (at most 53 by 53 bits), exponent sum, one pack.

### div (5.4.1, 7.3)

Specials: NaN by helper; 0/0 and inf/inf are invalid_without_nan. Finite nonzero divided by zero is infinity with XOR sign plus divisionByZero (7.3). Infinity divided by finite (zero included) is infinity XOR with no flag; finite divided by infinity is zero XOR; zero divided by finite nonzero is zero XOR. Finite nonzero path: binary long division over the conceptual dividend (dividend bits then scaling zeros, remainder kept under twice the divisor in u128) chosen so the quotient carries about 122 bits; final remainder nonzero is the sticky input to the one pack, so tie cases are decided from guard/round bits inside the quotient plus exact remainder evidence.

### sqrt (5.4.1)

Specials: NaN by helper; any negative nonzero operand including -inf is invalid_without_nan; sqrt(-0) is -0 and sqrt(+0) is +0; sqrt(+inf) is +inf. Finite positive: scale the significand by a left shift of about 120 minus its bit length, parity-adjusted so the remaining exponent is even, take the exact integer square root by bit trial (candidate squared with msf_u128_mul_u64_u64, root under 61 bits), remainder of the scaled integer minus root squared nonzero is sticky, one pack at half the remaining exponent. Dest f64 sqrt of f32/f64 inputs is never subnormal, but nothing in the code assumes that.

### fma (5.4.1, 8 combos)

Specials: NaN by helper in multiplicand, multiplier, addend order. A zero times infinity product is invalid: when the addend is a quiet NaN the caller also raises invalid and the helper delivers the addend (project ruling in the decode header); with a non-NaN addend it is invalid_without_nan. An infinite product plus an opposite-signed infinite addend is invalid_without_nan. Infinite product with finite or like-signed infinite addend delivers the product infinity (XOR sign); finite product plus infinite addend delivers the addend infinity. Finite: exact product (at most 106 bits) is one term, the addend the second; both enter the same signed two-term addition as add above (118-bit dominant window, jam only for a term whose top is far below the dominant top) and one pack. Zero product plus zero addend follows the zero-sum sign rule with the product XOR sign as the first addend sign.

### remainder (5.3.1)

Specials: NaN by helper; x infinite or y zero is invalid_without_nan. Finite x with y infinite returns x exactly; x zero with y nonzero returns x (its signed zero). Finite nonzero: magnitudes reduced by binary long division (process dividend bits at the exponent-difference scale, quotient parity recorded from the last quotient bit, iterations bounded by the exponent gap plus 53). With floor quotient q and exact remainder rem of the magnitudes: 2 times rem below |y| keeps q, above takes q plus 1 (result magnitude |y| minus rem and the sign that x minus n times y dictates), equal is the tie and takes whichever makes n even. A zero result takes the sign of x (5.3.1). The result is exact and is delivered through one pack with sticky zero; no flags on the finite path. Note the brief shorthand read as the zero-result sign rule only; the defining relation r equals x minus y times n fixes nonzero signs (for example remainder(5,3) is -1), which the Berkeley f64_rem sweep will confirm or refute.

### roundToIntegral family (5.3.1, 5.9; six rows)

Specials: NaN by helper (sNaN invalid); infinities and zeros return themselves with sign. Finite: if the decoded exponent is nonnegative the value is already integral and returns unchanged. Otherwise round the significand at the binary point (integer part, half bit, bits below half, fraction-nonzero are read off the u128 directly), incrementing the magnitude per the named direction (ties-to-even, ties-to-away, toward zero, toward positive, toward negative) or per the rm attribute for the Exact form, then pack the integer magnitude with the operand sign. Named forms signal no inexact (5.9); the Exact form signals inexact exactly when a nonzero fraction was discarded. Pack flags from this final pack are discarded (the integer is representable; no overflow or underflow is possible), only the Exact inexact is added by hand. A zero result keeps the operand sign.

### nextUp and nextDown (5.3.1)

Specials: NaN by helper (sNaN invalid, quiet delivered). nextUp(+inf) is +inf, nextUp(-inf) is the negative largest finite; mirrored for nextDown. Both zeros step to the smallest subnormal of the step direction's sign. Finite nonzero: step the encoding by one in magnitude (positive up or negative down increments the bit pattern, the other directions decrement it), which crosses subnormal/normal boundaries and largest-finite to infinity naturally. No flags except the sNaN invalid.

### scaleB (5.3.3) and logB (5.3.3)

scaleB specials: NaN by helper in (x, N) order. For nonzero N, scaleB of signed zero is that zero and of signed infinity is that infinity (5.3.3 as extracted); scaleB(x, signed zero N) is x. Finite nonzero x and finite N: N is truncated toward zero to an integer (project ruling for the language-defined non-integral case), clamped to plus or minus 5000 only when its magnitude passes that (results and flags are already saturated many binades earlier), then one pack of the x significand at exponent plus N, so overflow/underflow/inexact are the pack's. Infinite N is treated as the clamp of its sign through the same pack path for finite nonzero x (language-defined space, recorded here as the project choice), while zero and infinite x keep the clause outcomes above. logB specials: NaN by helper; logB of signed zero is -inf plus divisionByZero; logB of either infinity is +inf. Finite nonzero: exponent is decoded exp plus significand bit length minus 1 (subnormals count leading zeros through their bit length), delivered as an exact f64 integer via one pack; no flags.

### convertFormat (5.4.2; msf64_from_f32, msf64_from_f64)

NaN by helper at dest f64 from the source format (same-format conversion still quiets a signaling NaN with invalid). Infinity and zero keep sign. Finite: the decoded significand and exponent go straight to one pack (widening from f32 is exact; same-format is the identity).

### convertFromInt (5.4.1; 8 widths)

Sign and magnitude of the integer (magnitude computed in unsigned arithmetic so the most negative value is exact), one pack at exponent zero. Flags only from pack (inexact only beyond 53 bits).

### convertToInteger family (5.4.1, 5.8; 10 variants by 8 widths)

Specials: any NaN signals invalid and delivers 0 (project rule in the public header); infinity signals invalid and saturates (positive to the destination maximum, negative to the minimum, which is 0 for unsigned). Finite: round the exact value to a mathematical integer in the magnitude domain (same half/below/fraction reads as roundToIntegral; already-integral large values are range-classified by bit length before any shift can overflow). If that integer is outside the destination range, invalid is signaled and the saturated endpoint delivered, with no inexact even in Exact variants, because 5.8 scopes its inexact sentence to results that differ from the operand yet are representable (S1 extract lines for 5.8 read for this point). If inside range, that integer is delivered (negative values rounding to magnitude zero deliver 0, including to unsigned); inexact is signaled only by the five Exact variants and only when a nonzero fraction was discarded. Boundary care: the negative signed limit magnitude is one past the positive maximum, and directed modes at the endpoints (for example 127.5 ties cases) go through the same magnitude rounding then range check, never a pre-check on the unrounded value.

### comparisons (5.6.1, 5.11; 22 predicates by 2 second-operand formats)

Relation first: unordered if any operand is a NaN; else infinities order as -inf below every finite below +inf with like infinities equal; else msf_cmp_finite on the decoded pair (signed zeros equal). Predicate truth sets from Tables 5.1 and 5.2 as extracted: Equal {equal}; NotEqual {less, greater, unordered}; Greater {greater}; GreaterEqual {equal, greater}; Less {less}; LessEqual {less, equal}; NotGreater {less, equal, unordered}; NotLess {equal, greater, unordered}; LessUnordered {less, unordered}; GreaterUnordered {greater, unordered}; Unordered {unordered}; Ordered {less, equal, greater}; each in its quiet or signaling spelling per the tables (22 total, with Unordered and Ordered quiet-only). Flags: signaling forms signal invalid on any NaN operand; quiet forms signal invalid only on a signaling NaN operand (5.11). No other flag is possible.

### totalOrder and totalOrderMag (5.10)

Encoding key within f64: a negative encoding maps to its bitwise complement, a non-negative encoding to itself with the sign bit set; totalOrder(x,y) is key(x) at most key(y) as unsigned integers. This yields -NaN below -inf up through finite values with -0 below +0, to +inf below +NaN; signaling below quiet for positive NaNs and the reverse for negative NaNs; payload order beyond that is the encoding order, which 5.10 leaves implementation-defined. totalOrderMag applies the same keys to the magnitudes (sign bit cleared first). No flags (no flags parameter exists); NaNs signal nothing here.

### Files and gates planned

Owned edits only: src/msf64.c; new tests/gen_vectors_f64.py (independent Fraction references, patterns read from tests/gen_vectors.py without editing it); new committed tests/vectors files with f64 in the name kept under 1 MB total; appends of exactly my 173 rows at the end of tables/implemented.tsv; regenerated outputs of tools/gen_tables.py. Gates per the brief: tools/run.sh smoke in the worktree; Berkeley ingest sweeps into build/w1 replayed by the runner (level 1 complete in every applicable mode for the named f64 functions and conversions, level 2 --take 2000000 te and tz for add/sub/mul/div/sqrt, f64_mulAdd level 1 --take 2000000 every mode, eq/le/lt plus quiet level 1 complete); project-exact directed sets for everything Berkeley does not decide plus at least 200k seeded cross-format arithmetic cases into build only; the four named negative controls demonstrated in scratch logs. Times recorded as under third-party load, never quoted as rates.

## 2026-10-27 05:15:04 -0700 - Re-gate by regater-f64: lead fixes merged, all blocked cases green, READY at cb10ee2

Measured: regater-f64 merged b37fb12 (via 53acb1a) into worktrees/w1-f64 as 80cbc97 on 2026-10-27; only conflict tables/implemented.tsv, resolved as the LF union (244 lines, 173 parcel rows kept), gen_tables.py output byte-identical (783 instantiations, 236 implemented). Post-merge re-runs, all wall times under third-party load and not rates: Berkeley blocked set complete PASS 10,418,176 (mul/div level 1 te tp tn ta 8x46,464; mul te level 2 take 2,000,000; mulAdd level 1 take 2,000,000 te tp tn ta; f64_eq as ingested 46,464 now quiet); project-exact directed PASS (arith line 1824 included), seeded sweeps 210,000 (0xF64) and 150,000 (0xC0FFEE) PASS, misc sweep 120,000 PASS; four negative controls all refused on the final rerun; tools/run.sh smoke PASS 29,982 with 9/9 controls (planned-only names msf16_add) and standard PASS plus 1,117,504 generated. One classification during the re-gate: the first control rerun showed the wrong-tininess build passing the directed arith file, because the preliminary claim predated the generator pack restatement and line 1824 (first shape) is tiny under both tininess definitions; four second-shape directed mul cases were added (exact below 2^emin, unbounded rounding reaching it, corroborated by the ingested Berkeley case and an exact Fraction proof in scratch/parcel-f64/regate-tinyproof2.py), after which the before build fails arith by exactly those four and the correct build passes 11,057 directed cases. Commits 80cbc97 (merge) and cb10ee2 (re-gate) on w1-f64 over 5153324; worktree clean; never pushed. Full restated report in scratch/parcel-f64/report.md.
Believed: the parcel is READY for the lead merge; the only named skip remains the sibling parcel's msf32_from_f64 row (f64_to_f32 5x768 skipped-planned), and the board budget stays lead-only and was not run here.
For: lead, verifier-w1, parcel-f32

Hand-written total 1,788 of 3,000 (src/msf64.c 880, tests/gen_vectors_f64.py 908 after the 8 line second shape addition); committed parcel vector files 11,057 cases, 998,736 bytes. Coverage counted 173 of 173 wave-1 msf64 instantiations in the directed sets (scratch/parcel-f64/regate-coverage.log). Re-gate drivers and logs: scratch/parcel-f64/regate-step2.sh, regate-step3.sh, regate-step45.sh, regate-fix-directed.sh and their outer logs; tallies in scratch/parcel-f64/regate-tally.log.
