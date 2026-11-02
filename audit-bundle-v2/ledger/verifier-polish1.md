# verifier-polish1 (ParcelRound verifier, stale-info cleanup)

**Verdict: NOT READY** — 4 findings. Full evidence: `scratch/verifier-polish1/report.md`.

Copy: `worktrees/verify-polish1` (HEAD `fa8a27a`, parent `400b271`). All runs in a duplicate under `scratch/verifier-polish1/`; copy never modified; `docs/metrics/plants.jsonl` never opened/read/grepped/cited.

## Findings

- **F1** — `README.md:102-104` gives `assembly_v5.mp4` as "180-second, 1920x1080"; re-derived 169.0 s, 2560x1440 (`ffmpeg -i` banner; those figures belong to `final.mp4`). Corroborated by `video/README.md:7`, `video/assemble.py:31-37`, measured segment banners.
- **F2** — `site/data.json:68` `plants.caught: 120` does not reproduce (rerun of `site/build_data.py` yields 114; `ops.json`/`vectors-sample.json` clean) and does not sum (`by_wave` caught = 114). `README.md:48` and the parcel evidence ("114/120") agree with 114.
- **F3** — `docs/BOARD.md:145` TWIDDLES link (`../TWIDDLES.md`) resolves to repo-root `TWIDDLES.md`, which does not exist (pre-existing at parent, but the parcel brief gates on it resolving).
- **F4** — `docs/BOARD.md:40-43` (new) swaps the LED pins vs `board/msf_led.h:17-19,42` and `docs/RECORD.md:863-866` (Pico GP25 GPIO; Zeros WS2812 GP16).

## Clean probes

- `tools/gen_tables.py` rerun: 4/4 outputs byte-identical; header decimal comment matches generator.
- `bash tools/run.sh smoke`: PASS (23 s; 411,213/411,213 vectors; tier1 783/783, tier2 66/66; all negative controls refused).
- Video commands: all resolve; segment self-names/outputs/durations check out; live `probe.py` run on `proof.mp4` matches the README verify block.
- Claim surface otherwise re-derives: clone serials = RECORD six-board entry; 5-mode enum = 4+1 = 273 attr rows; all 9 `audit-bundle/ledger/parcel-*.md` citations exist; CMakeLists flavour comment matches registrations.
- RECORD appendix-only (13+/0−); briefs 31 rows at close + polish = 32, none dropped; `498a916` ancestor, adds the Step 3a row.

## Not done

None required — all six brief probes ran (`standard` not required here). One out-of-scope observation: `demo/twiddle_gate.c:6` cites `ledger/parcel-w4kissfft.md` (no `audit-bundle/` prefix; absent from the bundle) — unchanged by the parcel, outside probe scope, not a finding.
