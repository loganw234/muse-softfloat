**Role:** study-video-why (new "why a custom softfloat" segment draft)

**Task (owner):** Draft a 10-20s segment justifying the
project: show the workload and its requirements, show
the default/standard floating-point options available
on this platform, show why they are not suitable here
(or what they lack in comparison - mostly the IEEE
754 specifics), then settle on the custom option.
Owner thinks it goes at the start; final placement is
a lead assembly decision, so deliver it as a standalone
segment with clean in/out frames compatible with both
slots (before the messenger intro, or right after it
on the white plane) and say which you designed for.

**Facts - source everything, invent nothing:**
- Ground truth is in-repo: `docs/studies/SF-0.md`
  (platform survey + the measured SDK flavours:
  bootrom-routed pico float/double, libgcc, compiler
  flavours; what each does with rounding modes, flags,
  NaN payloads, subnormals, fma contraction), SF-1/SF-2
  for the requirements the workloads added (correctly
  rounded transcendental-adjacent ops, five rounding
  attributes incl. tiesToAway, augmented ops, exact
  exception flags), RECORD for what shipped.
- The workload requirements beat: IAS15 needs
  bit-identical binary64 across desktop and a chip
  with no FPU (RP2040); interval geometry needs
  directed rounding on demand; KissFFT Fork B needs
  correctly rounded sinPi/cosPi twiddles at runtime.
- Each default option gets its honest lacks measured
  or cited from SF-0 (e.g. fixed rounding only, no
  exception flags, payload laundering, no binary16,
  no augmented ops, contraction nondeterminism) -
  whatever SF-0 actually says; where SF-0 is silent,
  say "not measured" instead of filling in.
- The custom settle: IEEE 754-2019 semantics named
  (five attributes, flags, payloads preserved,
  correctly rounded incl. hard cases), proven
  bit-identical on silicon.

**Form:** 2560x1440 master (NEW house rule from the
owner: 1080p assemblies pixelate on zooms - render at
1440p, zooms rendered parametrically at output scale,
never crop-upscale beyond 1.5x; deliver the 1440p mp4;
a 1080p downscale twin is welcome but the 1440p is the
deliverable), 30 fps, 120 BPM grid, video/ idiom
(style.py read first). Energetic, legible, comparative
- a lineup/elimination feel is fine. Rough draft.

**Fences:** scratch only (`scratch/study-video-why/`),
repo untouched, nothing committed; never open/search/
list anything with `cft` in its name; do not consult
third-party softfloat source for the comparison
(publicly documented behavior + SF-0 measurements
only; if a claim needs a number you cannot source,
drop the claim); no timings framed as performance
superiority claims (correctness/semantics comparison
only, sizes may be shown as records).

**Outputs:** segment mp4 (probe-verified at 1440p),
beat stills (workload card, each option card, settle
frame), an options-facts JSON/md with per-claim
sources (SF-0 section/page pointers),
`scratch/study-video-why/report.md` (READY/NOT READY;
beat sheet; placement recommendation; claims dropped
for lack of source), `ledger/study-video-why.md`.
Structured complete/evidence/unresolved. Script files,
Git Bash, MSF_PYTHON pinned, memory ceilings.
