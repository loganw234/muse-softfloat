NOT READY

Audit of `worktrees/verify-readme2/README.md` Status/deferred/studies-row
claims (L16-61, L78) against in-copy evidence only
(`docs/COVERAGE.tsv`, `docs/RECORD.md`, `docs/metrics/plants.jsonl`,
`docs/studies/SF-2.md`, `docs/studies/SF-1.md` §7, `docs/studies/SF-0.md`
§2.7, committed recount of `tests/vectors/`, public header enum).
Stance: disconfirm only. The copy was not modified. Nothing with `cft`
in its name was opened, searched, or listed. Counts were recomputed by
`scratch/verifier-readme2/recount_vectors.sh` and `census.sh` under
Git Bash (MSF_PYTHON unset in this environment; scripts fell back to
`python3`): 42 vector files, 171,423 committed data lines, 21,858 `ta`
data lines; COVERAGE 822 data rows (783 tier 1 + 39 tier 2, all
`implemented`; rounding `attr` 255 / `named` 255 / `none` 312);
plants 65 rows: 61 `caught`, 4 `missed`.

## Per-claim table

| README claim (line) | In-copy source | Agree? |
|---|---|---|
| L18-19 "822 of 822 instantiations" | COVERAGE recount: 822 data rows, all `status=implemented` | Agree |
| L20-22 "SF-0, SF-1 and SF-2 are the approved plans of record" | `docs/studies/SF-2.md` L3: "Status: APPROVED plan of record, 2026-10-28"; SF-1 approved `fe213fd` per RECORD L606-609; all three files present in `docs/studies/` | Agree |
| L23-26 "full Clause 5 surface for binary16/32/64 ... (783/783)" | COVERAGE recount: 783 tier-1 rows, all implemented | Agree |
| L23-24 "correctly rounded decimal/hex character conversions (H=20)" | `include/muse_softfloat.h` L115: `#define MSF_DECIMAL_H 20` | Agree |
| L26-28 "plus 39 Tier 2 rows: 9.6 min/max semantics, payload accessors, correctly rounded sinPi/cosPi, every family at all three formats" | COVERAGE recount: 39 tier-2 rows, all implemented, `dest` 13 f16 / 13 f32 / 13 f64; std names exactly min/max/Number/Magnitude forms (24, cl. 9.6), get/setPayload forms (9, cl. 9.7), sinPi/cosPi (6, cl. 9.2) | Agree |
| L29-31 "196,404 committed vectors" | Recount: **171,423** data lines in 42 `tests/vectors/*.vec` files; RECORD Wave-5-Step-1 entry: "Committed smoke is now **171,423 vectors**" | DISAGREE (F1) |
| L31 "`standard` adds 1,117,504" | RECORD L636 (Step 0a era: "85,148 committed + 1,117,504 generated"); `tools/run.sh` `standard()` still generates f16-exhaustive + pack-sweep on top of smoke | Agree (by record/code reading; the generated leg was not executed) |
| L32-33 "verified wave by wave ... (65 of 65 plants caught to date)" | `plants.jsonl`: 61 `caught` / 65 total; 4 `missed` (wave1 plant 5; readme plant 4; wave5 plants 1, 5, each with a lead `note`); RECORD: "**5 of 5** (61 of 65 cumulative)" | DISAGREE (F2) |
| L34-37 "REBOUND's IAS15 ... reproduces ... for 2,000 steps (2,001/2,001 records)" | RECORD L558-559: "`matched=2001 first_divergence=None`; step-2000 ... match the unmodified desktop build exactly" | Agree |
| L37-38 "interval-geometry catalogue streams host==board bit-for-bit" | RECORD L703-706: "the full catalogue streamed to the genuine board matches the host bit-for-bit: IW1 SHA-256 `ce81d66e...a9aec` on both sides, 710/710 rows, 616,754 counted ops" | Agree |
| L38-41 "KissFFT ... matches all 12 configuration hashes at the gated sizes N=256/1024/4096" | RECORD L760-764: "all **12/12 KF hash rows are bit-identical** ... At the gated power-of-two sizes (N=256/1024/4096, complex and real, forward and inverse)"; Fork-B/scratch-only wording matches L747-752 | Agree |
| L45-48 front door / run.sh / standard merge gate | `tools/run.sh` exists with `smoke\|standard\|board\|bench`, inventory-before-verdict and refusal controls (read, not executed) | Agree (no execution; not a numbered claim under audit) |
| L50-51 "`roundTiesToAway` has landed as the fifth public rounding attribute" | Header L60-66: `MSF_ROUND_TIES_TO_AWAY = 4` fifth enum value with SF-2-Step-1 comment; RECORD L770-783 (Step 1 landed `8bfc877`/`6e0f2f2`) | Agree (the landing, not the scope) |
| L51-52 "across all 822 attribute-carrying rows" | COVERAGE `rounding=attr`: **255** rows (83 f16 + 83 f32 + 83 f64 + 6 `size`); RECORD: "Zero new rows; all **255** attribute-carrying rows now carry ties-to-away evidence" | DISAGREE (F3) |
| L52-53 "`rSqrt`/`hypot`, the `exp2`/`log2` pairs, and Clause 9.5 augmented arithmetic have landed in SF-2's order" | COVERAGE still 822 rows (SF-2 §1 closes at 822+27=849, none of the 27 present); zero header declarations matching rSqrt/hypot/exp2/log2/aug; RECORD: "SF-2 continues with the algebraic bundle (`rSqrt`, `hypot` first)" — i.e. Steps 2-4 unstarted | DISAGREE (F4) |
| L54-61 deferred/refused list generally (9.2 remainder, 9.4 reductions, dynamic wrappers, public roundToOdd, binary128/decimal/Clause 8 out) | SF-1 §7 (L560-579): wrappers/9.5/9.4/other-9.2 deferred, roundToOdd "never as public 754 surface", standing refusals from SF-0 §§2.7/11; SF-2 §1: reductions "NO-GO, nowhere in the library", roundToOdd "NO-GO as a promotion"; SF-0 §2.7 L286-287: "Never in this project: binary128 or decimal formats, Clause 8 alternate exception handling ..." | Agree, except F5 |
| L56 "`pow`/`powr` priced for a later wave" | SF-1 §7: "`pow`/`powr` **refused** in any first sequence"; SF-2 §1: "`pow`/`powr` (**refused**)"; SF-2 §9: "`pow`/`powr`, reductions, wrappers, `roundToOdd`: remain as Sec. 1 states". "Priced" in SF-2 §10 attaches to the `pown`/`compound`/`rootn` leg-(c) spike, not to `pow`/`powr` | DISAGREE (F5) |
| L78 studies row ("SF-0, SF-1 and SF-2, the approved plans of record") | Same as L20-22 row above | Agree |

## Findings (README line refs)

- F1 (L31): vector total overstated. README says 196,404; the copy's
  vectors recount to 171,423 and RECORD's latest entry agrees
  (171,423). Delta +24,981 has no in-copy authority.
- F2 (L32-33): plant score overstated. README says 65/65 caught;
  `plants.jsonl` grades 61 caught and 4 missed (each miss carries a
  lead `note`), and RECORD's cumulative reads "61 of 65". Even
  excluding the three plan/meta plants (readme-4, wave5-1, wave5-5),
  the wave-1 generator-pool plant (wave1 plant 5, `missed`) alone
  contradicts 65/65.
- F3 (L51-52): attribute-row scope overstated. README says
  roundTiesToAway landed "across all 822 attribute-carrying rows";
  the copy has 255 attribute-carrying rows (`rounding=attr`) and
  RECORD's Step-1 entry says exactly "all 255 attribute-carrying
  rows". 822 is the whole inventory, not the attribute subset.
- F4 (L52-53): unlanded families claimed landed. README presents
  `rSqrt`/`hypot`, `exp2`/`log2` pairs, and Clause 9.5 augmented
  arithmetic as landed; in-copy they are SF-2 Steps 2-4, still
  planned — COVERAGE holds 822 rows (not 849), the public header
  declares none of the new names, and RECORD's latest entry says
  "SF-2 continues with the algebraic bundle (`rSqrt`, `hypot`
  first)". (Order is also misstated as landed fact: Step 1 strictly
  precedes Steps 2-4 per SF-2 §7, and only Step 1 has landed.)
- F5 (L56): refusal softened. README describes `pow`/`powr` as
  "priced for a later wave"; both studies say **refused** (SF-1 §7,
  SF-2 §§1/9). This is the same gloss plants.jsonl wave5-plant-5
  records as missed ("refused pow/powr softened to a priced
  deferral").

## Notes (corroborated, no finding)

- `ta` evidence volume cross-checks: 21,858 `ta` data lines recounted
  vs RECORD's "21,858 committed `ta` lines (10,985 decided; 10,873
  relabeled trig lines)" — exact agreement.
- "Standard adds 1,117,504" is carried from RECORD's Step-0a/Step-1
  era entries; the generated leg was not executed in this audit, so
  its current-HEAD value is single-source (RECORD + run.sh shape),
  not a second independent count. No contradicting evidence found.
- Wave-5-Step-1 board replay claims (968-vector replay, 419/419 `ta`
  stride sample) were read in RECORD only; the board artefacts behind
  them were not re-probed (outside the brief's probe list).
