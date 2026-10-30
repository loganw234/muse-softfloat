# verifier-w5site (Wave 5 site parcel, copy `worktrees/verify5-site` @ `1e6722d`)

NOT READY — 5 findings, full evidence in
`scratch/verifier-w5site/report.md` (scripts beside it).

Replay (self-run under Node through the copy's `site/msf.wasm`):
`msf_op_count=828`, sample=1596, `replayed=1596 mismatches=0`. Known-answer
probes 5/5 vs `include/muse_softfloat.h`: te/ta tie splits
0x3f800000/0x3f800001 (flags 0x10), div-by-zero 0x02, overflow 0x14,
hypot(3,4)=5. Census: COVERAGE 828 rows (783/45, all implemented), vectors
182,518 with exact per-file match, plants 80 rows / 75 caught, ops
828/runnable 810, sample 1596 covering 798 ops with every line found
verbatim in `tests/vectors/`. Degraded mode exercised for real (headless
Edge, WASM 404): down-banner labels recorded results as recorded; real
`app.js` deal branch shows "Recorded result shown" with `(recorded)` kind.
pages.yml uploads `site/` with correct permissions; no runtime external
requests; claim surface is parent `a0acf2a` + owned files only.

Findings: F1 flag chips swap UNDERFLOW/INEXACT (`site/app.js:11-14` vs
header `:70-74`). F2 `site/data.json` plants top-level 80 vs file 75
(generator yields 75; page status line says 80/80 while its table says
75/80); ops.json + vectors-sample.json regenerate byte-identical. F3 page
claims exp2/log2/augmented "landed" (`index.html:179-180`) with zero such
COVERAGE/dispatch rows and no RECORD landing. F4 root README live-URL href
uses `muse_softfloat` (underscore) vs `muse-softfloat` everywhere else.
F5 KissFFT panel says "unmodified:" though RECORD requires never
"unmodified" (patched at three sites). Not done: wasm rebuild (no
toolchain here, skippable), Pages run + live URL (owner action at merge),
pixel QA, non-Edge browsers.
