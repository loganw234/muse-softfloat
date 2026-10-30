# options-facts — per-claim sources for the why segment

Rule (brief + task): on-screen option claims only from
`muse-softfloat/docs/studies/SF-0.md` (read in full, 837 lines),
including the S3 sections SF-0 cites by number (S3 = scratch/S3/report.md,
SF-0's own survey evidence). Workload requirements from SF-1/SF-2.
Settle claims from SF-0 + SF-1/SF-2 + RECORD (what shipped).
Where SF-0 is silent the screen says "not measured" (?) — never a lacks.

## Workloads (cards, 1.5–4.5 s)

| On screen | Source |
|---|---|
| IAS15: binary64 bit-identical, desktop = chip, every bit every step | Brief; SF-0 §1 (owner words), §9 (same extracted source, field-parsed hash) |
| Interval geometry: directed rounding on demand, down/up per call | Brief; SF-1 §0.2/§2.2 (directed FMA/div/sqrt already Tier 1; containment needs directed endpoints) |
| KissFFT Fork B: sinPi/cosPi twiddles at runtime, correctly rounded | Brief; SF-1 §0.4/§6.4 (Fork B adopted: correctly rounded of the exact angles, runtime generation for caller-chosen N) |
| RP2040 has no FPU — every float is software | Brief; SF-0 §3.4 (Cortex-M0+ helper-call model) |

## Job spec (checklist, 4.5–6.0 s)

| Row | Source |
|---|---|
| rounding attributes: all four + tiesToAway | SF-0 §2.3 (four required everywhere); SF-2 §2 Step 1 (tiesToAway fifth public attribute) |
| exception flags: invalid · div-by-zero · overflow · underflow · inexact | SF-0 §2.4 (five Clause 7 flags, exact conditions) |
| subnormals kept — never flushed | SF-0 §2.5/§2.7 ("Never: flush-to-zero/denormals-are-zero modes") |
| NaN payloads preserved | SF-0 §2.5 NaN matrix (payload propagation as project promise) |
| formats binary16/32/64 | SF-0 §2.2 (all three arithmetic formats) |
| correctly rounded — FMA, sqrt, sinPi/cosPi, hard cases | SF-0 §2.3 (correct rounding vs infinitely precise result, FMA one rounding); SF-1 §6 (trig pair correctly rounded) |
| augmented add/sub/mul, head + exact tail | SF-2 §5 Step 4 (Clause 9.5; interval exact stage is the named consumer) |

## Option 1 — SDK `pico` flavour → bootrom (6.0–8.0 s)

Flavour names pico/compiler/none: SF-0 §3.4 item 2 ("selected per target
like pico/compiler/none"); default = pico, bootrom-routed: S3 §1.3–1.4
(FP entry points tail-call the bootrom), cited by SF-0 §3.4/§8.

| On screen | Source |
|---|---|
| ✓ five basic ops correctly rounded * (+ − × ÷ √) | SF-0 §8: "the bootrom correctly rounds its five basic operations only subject to…"; S3 §2.2 (datasheet quote) |
| ✗ subnormals flushed to zero — in and out | SF-0 §3.4, §5.2, §8; S3 §2.2: "input denormals are treated as zero… output denormals are flushed to zero" |
| ✗ NaNs rendered as infinities — payloads gone | SF-0 §3.4 ("NaNs as infinities"), §5.2, §8; S3 §2.2 (same quote; payload loss is the direct consequence — worded as consequence, not a separate measurement) |
| ✗ one rounding mode: ties-to-even, no directed modes | SF-0 §8 "with one rounding mode"; S3 §2.2: "Only the round-to-nearest, even-on-tie rounding mode is supported" |
| ✗ exception flags: none exist | SF-0 §3.4 "no flags", §8; S3 §2.2 "No exception flags exist anywhere in this design" (MEASURED grep) |
| matrix b16+b32+b64 = ? | SF-0 makes no binary16 claim for the bootrom → not measured, shown ? |
| matrix augmented = ? | SF-0 silent → ? |

## Option 2 — SDK `compiler` flavour → libgcc (8.0–10.0 s)

| On screen | Source |
|---|---|
| falls through to compiler/libgcc | S3 §1.4 ("no custom implementation; falls thru to compiler"), flavour named in SF-0 §3.4 |
| ? directed rounding / flags / payloads / subnormals / binary16: not measured | SF-0 contains NO semantic measurement of libgcc: it appears only as a cycle/size baseline (§0 item 7, §8), a wrap target (§3.4), and a refused source on licence (§4.5). Honest cell = not measured |
| ✗ compiler FMA contraction varies by target | SF-0 §9: distribution-default builds refused because "contraction behaviour is target-dependent"; §4.2/§5.3 contraction refusals |
| footer: unmeasured semantics can't carry a bit-identity proof | Synthesis of the above + SF-0 §9's strict-build definition of the IAS15 claim |

## Option 3 — SDK `none` flavour (10.0–11.0 s)

| On screen | Source |
|---|---|
| panic("float support is disabled") — every float entry point is this stub | S3 §1.4 ("every wrapped symbol is a panic stub sharing one body"); flavour named in SF-0 §3.4 |

## Settle — Muse-Softfloat (13.5–15.0 s)

| On screen | Source |
|---|---|
| IEEE 754-2019 · binary16/32/64 · 849 instantiations | SF-0 §2.1–2.2; RECORD Wave 5 Step 4 close: "the library stands at 849 counted instantiations (783 Tier 1 + 66 Tier 2)" |
| five rounding attributes | SF-0 §2.3 (4) + RECORD Wave 5 Step 1 (roundTiesToAway fifth public attribute, all 255 attribute rows) |
| five exact flags | SF-0 §2.4 |
| payloads preserved | SF-0 §2.5 matrix |
| subnormals kept | SF-0 §2.5/§2.7 |
| augmented ops | SF-2 §5; RECORD Wave 5 Step 4 (shipped, all formats) |
| correctly rounded, hard cases in | SF-0 §2.3; RECORD: "every one correctly rounded under its clause" |
| proven bit-identical on RP2040 silicon | RECORD: IAS15 bit-identical on six boards (2026-10-28); per-family board replays bit-identical (Steps 1–4) |

## Claims dropped for lack of SF-0 source (not on screen)

1. "libgcc has fixed rounding only / no exception flags / launders NaN
   payloads / no binary16 / no augmented ops" — plausible-sounding list
   from the brief's examples; SF-0 measured none of it. Shown as
   "not measured" instead (the card's whole beat).
2. SDK C-layer `fmaf` double-rounding and unfused `fma` — real, but only
   in S3 §1.3 Tier C; SF-0 does not carry it. Excluded by the SF-0-only
   rule; available if the lead relaxes the rule to S3 generally.
3. Bootrom scientific functions "within 1 ULP" — S3 §2.2/datasheet via
   SF-0 §8 citation; cut for time, not for sourcing. Could return in a
   longer cut.
4. Bootrom cycle counts (_fadd 71, _ddiv 183; SF-0 §8, S3 §4.1) — sourced
   but excluded by the no-performance-framing fence.
5. Host libm twiddle near-misses (1,022/1,024) — SF-1 §2.3 measurement,
   about the desktop, not an RP2040 option. Off-topic for the lineup.
6. Any size comparison — sizes are permitted as records, but no sourced
   side-by-side exists in SF-0; dropped rather than invented.
