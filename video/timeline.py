"""The proof timeline AS DATA. Re-cutting = editing this list (or a JSON copy).

Schema: each scene is a dict with kind/t0/t1 plus kind-specific params.
Times are seconds; cuts land on the 0.5 s beat grid (style.BEAT).
`*word*` in kinetic text renders in the scene accent colour.
`source` is printed bottom-right on the frame: where the number came from.
"""
from __future__ import annotations

import style as S

C = lambda rgb: list(rgb)  # noqa: E731 - JSON-friendly colours

PROOF: list[dict] = [
    {
        "kind": "kinetic", "t0": 0.0, "t1": 3.0, "accent": C(S.CYAN), "zoom": True,
        "kicker": "muse-softfloat // proof cut",
        "lines": [
            {"text": "NO *FPU.*", "at": 0.15, "size": 150},
            {"text": "NO *EXCUSES.*", "at": 0.75, "size": 150},
        ],
        "sub": "IEEE 754 softfloat for the RP2040 - built by Muse models, verified in public",
        "sub_at": 1.5,
        "source": "muse-softfloat/README.md",
    },
    {
        "kind": "counter", "t0": 3.0, "t1": 6.0, "accent": C(S.AMBER),
        "kicker": "committed test vectors // smoke gate",
        "target": 52168, "count_dur": 1.7, "size": 210,
        "label": "VECTORS. EVERY COMMIT.",
        "sub": "plus 1,117,504 more in the standard merge gate",
        "source": "docs/RECORD.md - Wave 1 entry",
    },
    {
        "kind": "barchart", "t0": 6.0, "t1": 8.5, "accent": C(S.CYAN),
        "kicker": "real data // docs/metrics/passes.jsonl",
        "title": "WHO DID THE WORK",
        "series": "tool_uses_by_agent",
        "sub": "tool uses per agent, summed live from passes.jsonl at render time",
        "source": "docs/metrics/passes.jsonl (27 rows)",
    },
    {
        "kind": "linechart", "t0": 8.5, "t1": 11.0, "accent": C(S.GREEN),
        "kicker": "real data // passes in time order",
        "title": "THE WORK, ACCUMULATING",
        "sub": "cumulative tool uses across every recorded agent pass",
        "source": "docs/metrics/passes.jsonl",
    },
    {
        "kind": "ticker", "t0": 11.0, "t1": 13.5, "accent": C(S.VIOLET),
        "kicker": "git log // muse-softfloat",
        "title": "EVERY COMMIT. VERIFIED.",
        "source": "git -C muse-softfloat log (live at render)",
    },
    {
        "kind": "orbit", "t0": 13.5, "t1": 19.5, "accent": C(S.CYAN),
        "kicker": "the workload // REBOUND IAS15",
        "lines_rgb": [
            ["IAS15", 120, C(S.INK)],
            ["ON AN RP2040", 84, C(S.CYAN)],
            ["WITH NO FPU", 84, C(S.AMBER)],
        ],
        "sub": "same integrator source - same bits out",
        "source": "muse-softfloat/README.md - the public proof",
    },
    {
        "kind": "stat", "t0": 19.5, "t1": 22.5, "accent": C(S.PINK),
        "kicker": "the method, in numbers",
        "stats": [
            {"value": "9/10", "label": "PLANTS CAUGHT", "sub": "independent Spark verifiers"},
            {"value": "37M+", "label": "BERKELEY CASES", "sub": "TestFloat 3e, post-fix"},
            {"value": "409", "label": "OF 783 GATED", "sub": "operation instantiations"},
        ],
        "plant_dots": True,
        "source": "docs/metrics/plants.jsonl + docs/RECORD.md",
    },
    {
        "kind": "hash", "t0": 22.5, "t1": 24.5, "accent": C(S.GREEN),
        "kicker": "board proof // 2,767 vectors on RP2040",
        "title": "SAME HASH. BOTH MACHINES.",
        "source": "docs/RECORD.md - Wave 1 board run",
    },
    {
        "kind": "kinetic", "t0": 24.5, "t1": 26.5, "accent": C(S.AMBER), "zoom": True,
        "kicker": "muse-softfloat",
        "lines": [
            {"text": "IEEE 754,", "at": 0.1, "size": 140},
            {"text": "*HONESTLY.*", "at": 0.6, "size": 140},
        ],
        "sub": "full 3-minute cut: STORYBOARD.md",
        "sub_at": 1.2,
        "source": "github.com/loganw234 (see repo README)",
    },
]

# ---------------------------------------------------------------------------
# THE FINAL CUT - 180.0 s, 29 scenes, 9 segments (STORYBOARD.md as-built).
# Every number below traces via data.SOURCES to docs/RECORD.md / README.md /
# tools/run.sh / the IAS15 hash files; each scene's `source` prints on frame.
FINAL: list[dict] = [
    # -- 1. Hook 0-8 ---------------------------------------------------------
    {
        "kind": "kinetic", "t0": 0.0, "t1": 4.0, "accent": C(S.CYAN), "zoom": True,
        "kicker": "muse-softfloat // the film",
        "lines": [
            {"text": "NO *FPU.*", "at": 0.15, "size": 150},
            {"text": "NO *EXCUSES.*", "at": 0.85, "size": 150},
        ],
        "sub": "IEEE 754 softfloat for the RP2040",
        "sub_at": 1.8,
        "source": "muse-softfloat/README.md",
    },
    {
        "kind": "kinetic", "t0": 4.0, "t1": 8.0, "accent": C(S.AMBER), "zoom": True,
        "kicker": "the claim",
        "lines": [
            {"text": "THE WHOLE *STANDARD.*", "at": 0.15, "size": 118},
            {"text": "ON A CHIP WITH *NONE.*", "at": 0.9, "size": 118},
        ],
        "sub": "built by Muse models - verified by Muse models - in public",
        "sub_at": 1.9,
        "source": "muse-softfloat/README.md + commit trailers (git log)",
    },
    # -- 2. The problem 8-30 --------------------------------------------------
    {
        "kind": "kinetic", "t0": 8.0, "t1": 14.0, "accent": C(S.RED),
        "kicker": "the problem // RP2040 bootrom float",
        "lines": [
            {"text": "DENORMALS IN: *ZERO*", "at": 0.3, "size": 80},
            {"text": "DENORMALS OUT: *ZERO*", "at": 1.5, "size": 80},
            {"text": "NaNs: *INFINITIES*", "at": 2.7, "size": 80},
            {"text": "EXCEPTION FLAGS: *NONE*", "at": 3.9, "size": 80},
        ],
        "source": "docs/RECORD.md Wave 0 - survey S3 (bootrom)",
    },
    {
        "kind": "kinetic", "t0": 14.0, "t1": 20.0, "accent": C(S.RED), "zoom": True,
        "kicker": "why it matters",
        "lines": [
            {"text": "FINE FOR AN *LED.*", "at": 0.2, "size": 112},
            {"text": "FATAL FOR AN *INTEGRATOR.*", "at": 1.1, "size": 112},
        ],
        "source": "docs/RECORD.md Wave 0 - survey S3 delta",
    },
    {
        "kind": "kinetic", "t0": 20.0, "t1": 26.0, "accent": C(S.RED),
        "kicker": "the problem // pico-sdk layer",
        "lines": [
            {"text": "AND THE SDK?", "at": 0.2, "size": 104},
            {"text": "FMA: *UNFUSED.*", "at": 1.2, "size": 104},
            {"text": "fmaf: *DOUBLE-ROUNDING.*", "at": 2.3, "size": 88},
        ],
        "sub": "recorded in its own source comments - survey S3",
        "sub_at": 3.4,
        "source": "docs/RECORD.md Wave 0 - survey S3 (SDK)",
    },
    {
        "kind": "kinetic", "t0": 26.0, "t1": 30.0, "accent": C(S.CYAN), "zoom": True,
        "kicker": "the answer",
        "lines": [
            {"text": "THAT'S THE *BOOTROM.*", "at": 0.15, "size": 112},
            {"text": "OURS DOES THE *STANDARD.*", "at": 0.95, "size": 104},
        ],
        "source": "muse-softfloat/README.md - Status",
    },
    # -- 3. The contract 30-55 ------------------------------------------------
    {
        "kind": "counter", "t0": 30.0, "t1": 36.0, "accent": C(S.AMBER),
        "kicker": "the contract // operation instantiations",
        "target": 783, "count_dur": 2.2, "size": 230,
        "label": "OF 783. ALL OF THEM.",
        "sub": "every Clause 5 instantiation - binary16, binary32, binary64",
        "source": "docs/RECORD.md Wave 3 - 783 of 783 (+ docs/COVERAGE.tsv)",
    },
    {
        "kind": "stat", "t0": 36.0, "t1": 44.0, "accent": C(S.CYAN),
        "kicker": "the contract // what 'all of it' means",
        "stats": [
            {"value": "3", "label": "FORMATS", "sub": "binary16 / 32 / 64"},
            {"value": "4", "label": "ROUNDING MODES", "sub": "+ ties-to-away operations"},
            {"value": "H=20", "label": "DECIMAL DIGITS", "sub": "correctly rounded conversions"},
        ],
        "source": "docs/RECORD.md Wave 0 (S1) + Wave 3 (H=20)",
    },
    {
        "kind": "kinetic", "t0": 44.0, "t1": 50.0, "accent": C(S.CYAN), "zoom": True,
        "kicker": "ground rule",
        "lines": [
            {"text": "754-2019 IS THE *CONTRACT.*", "at": 0.2, "size": 104},
            {"text": "NOT THE *ORACLE.*", "at": 1.2, "size": 118},
        ],
        "source": "muse-softfloat/README.md - ground rules",
    },
    {
        "kind": "kinetic", "t0": 50.0, "t1": 55.0, "accent": C(S.GREEN),
        "kicker": "the oracle",
        "lines": [
            {"text": "THE ORACLE IS *EXECUTABLE.*", "at": 0.2, "size": 100},
        ],
        "sub": "each row gated vs Berkeley TestFloat 3e, MPFR, or an exact reference",
        "sub_at": 1.4,
        "source": "muse-softfloat/README.md - Status",
    },
    # -- 4. The method 55-85 --------------------------------------------------
    {
        "kind": "kinetic", "t0": 55.0, "t1": 60.0, "accent": C(S.VIOLET), "zoom": True,
        "kicker": "the method // ParcelRound",
        "lines": [
            {"text": "PARCELS,", "at": 0.15, "size": 140},
            {"text": "NOT *PROMPTS.*", "at": 0.8, "size": 140},
        ],
        "source": "muse-softfloat/README.md + AGENTS.md",
    },
    {
        "kind": "barchart", "t0": 60.0, "t1": 68.0, "accent": C(S.CYAN),
        "kicker": "real data // docs/metrics/passes.jsonl",
        "title": "WHO DID THE WORK",
        "series": "tool_uses_by_agent",
        "sub": "tool uses per agent - summed live from passes.jsonl at render time",
        "source": "docs/metrics/passes.jsonl (live at render)",
    },
    {
        "kind": "ticker", "t0": 68.0, "t1": 74.0, "accent": C(S.VIOLET),
        "kicker": "git log // muse-softfloat",
        "title": "EVERY COMMIT. VERIFIED.",
        "source": "git -C muse-softfloat log (live at render)",
    },
    {
        "kind": "linechart", "t0": 74.0, "t1": 80.0, "accent": C(S.GREEN),
        "kicker": "real data // passes in time order",
        "title": "THE WORK, ACCUMULATING",
        "sub": "cumulative tool uses across every recorded agent pass",
        "source": "docs/metrics/passes.jsonl (live at render)",
    },
    {
        "kind": "kinetic", "t0": 80.0, "t1": 85.0, "accent": C(S.PINK),
        "kicker": "the method // verification",
        "lines": [
            {"text": "EVERY PARCEL GETS A *VERIFIER.*", "at": 0.2, "size": 92},
            {"text": "ITS ONLY JOB: *DISCONFIRM.*", "at": 1.3, "size": 100},
        ],
        "source": "muse-softfloat/README.md - ground rules",
    },
    # -- 5. The catch 85-110 --------------------------------------------------
    {
        "kind": "kinetic", "t0": 85.0, "t1": 92.0, "accent": C(S.RED),
        "kicker": "the catch // Wave 1, mid-flight",
        "lines": [
            {"text": "OUR KERNEL WAS *WRONG.*", "at": 0.3, "size": 112},
            {"text": "OUR REFERENCE *AGREED.*", "at": 1.8, "size": 112},
        ],
        "sub": "the lead's code, twice over - kernel and Python reference",
        "sub_at": 3.2,
        "source": "docs/RECORD.md Wave 1 - Slips, attributed",
    },
    {
        "kind": "kinetic", "t0": 92.0, "t1": 98.0, "accent": C(S.AMBER),
        "kicker": "the catch // why nobody saw it",
        "lines": [
            {"text": "EVERY SELF-CONSISTENT", "at": 0.3, "size": 102},
            {"text": "GATE *PASSED.*", "at": 1.4, "size": 118},
        ],
        "source": "docs/RECORD.md Wave 1 - checkpoint findings",
    },
    {
        "kind": "kinetic", "t0": 98.0, "t1": 104.0, "accent": C(S.CYAN), "zoom": True,
        "kicker": "the catch // the turn",
        "lines": [
            {"text": "*BERKELEY* DISAGREED.", "at": 0.25, "size": 122},
        ],
        "sub": "a parcel escalated against its own lead's code - and was upheld",
        "sub_at": 1.6,
        "source": "docs/RECORD.md Wave 1 - parcel-f32 escalation",
    },
    {
        "kind": "kinetic", "t0": 104.0, "t1": 110.0, "accent": C(S.GREEN),
        "kicker": "the catch // the fix",
        "lines": [
            {"text": "TININESS, CLAUSE *7.5.*", "at": 0.25, "size": 108},
            {"text": "FIXED. *RE-GATED.* PUSHED.", "at": 1.4, "size": 102},
        ],
        "sub": "commit 53acb1a - Spark recheck: oracle differential 2400/2400",
        "sub_at": 2.6,
        "source": "docs/RECORD.md Wave 1 - fixes 53acb1a / b37fb12",
    },
    # -- 6. The scale 110-135 -------------------------------------------------
    {
        "kind": "counter", "t0": 110.0, "t1": 115.0, "accent": C(S.AMBER),
        "kicker": "the scale // committed test vectors",
        "target": 85148, "count_dur": 1.9, "size": 210,
        "label": "VECTORS IN THE SMOKE GATE.",
        "sub": "the standard merge gate adds 1,117,504 more (Wave 1 count)",
        "source": "docs/RECORD.md Wave 3 (smoke) + Wave 1 (standard)",
    },
    {
        "kind": "stat", "t0": 115.0, "t1": 122.0, "accent": C(S.PINK),
        "kicker": "the scale // external evidence",
        "stats": [
            {"value": "37M+", "label": "BERKELEY CASES", "sub": "combined post-fix - 'exceeds'"},
            {"value": "6.1M x5", "label": "F16 FMA, BERKELEY L1", "sub": "cases in each of 5 modes"},
            {"value": "65,536", "label": "BINARY16 ENCODINGS", "sub": "exhaustive unary sweeps"},
        ],
        "source": "docs/RECORD.md Wave 1 + Wave 2",
    },
    {
        "kind": "stat", "t0": 122.0, "t1": 130.0, "accent": C(S.GREEN),
        "kicker": "the scale // planted-defect verification",
        "stats": [
            {"value": "24/25", "label": "PLANTS CAUGHT", "sub": "independent Spark verifiers"},
            {"value": "3", "label": "WAVES PLANTED", "sub": "9/10, then 10/10, then 5/5"},
            {"value": "1", "label": "MISS", "sub": "kept, named, learned from"},
        ],
        "plant_dots": True,
        "plant_note": "the Wave 1 miss taught us byte-identity - RECORD.md tells it straight",
        "source": "docs/metrics/plants.jsonl (live) + docs/RECORD.md Waves 1-3",
    },
    {
        "kind": "kinetic", "t0": 130.0, "t1": 135.0, "accent": C(S.AMBER), "zoom": True,
        "kicker": "ground rule",
        "lines": [
            {"text": "NOT READY IS A *VERDICT*", "at": 0.2, "size": 112},
            {"text": "WE *SHIP.*", "at": 1.1, "size": 132},
        ],
        "sub": "9 named negative controls - all refused, every smoke run",
        "sub_at": 2.0,
        "source": "tools/run.sh controls() + docs/RECORD.md Wave 1 (9/9)",
    },
    # -- 7. The board proof 135-152 -------------------------------------------
    {
        "kind": "hash", "t0": 135.0, "t1": 143.0, "accent": C(S.GREEN),
        "kicker": "board proof // final tree - RP2040 e66440a2cb6f5c2b",
        "title": "SAME HASH. BOTH MACHINES.",
        "hash": "729f495d3e92bcd82931bd42b237705ad5333fe3ffeba4f5e3b39b0b2583f2b9",
        "type_dur": 3.5,
        "sub": "2,489-vector f16/xf sample - a sample, said plainly; not full-volume replay",
        "source": "docs/RECORD.md Wave 2, re-replayed Wave 3 - hash identical",
    },
    {
        "kind": "stat", "t0": 143.0, "t1": 149.0, "accent": C(S.CYAN),
        "kicker": "board samples // string rows host-gated (RECORD Wave 3)",
        "stats": [
            {"value": "2,767", "label": "WAVE 1 SAMPLE", "sub": "binary32/64, hash-identical"},
            {"value": "2,489", "label": "WAVE 2 SAMPLE", "sub": "f16/xf - re-run on final tree"},
            {"value": "47,107", "label": "AEABI CHECKS", "sub": "selftest on the RP2040 itself"},
        ],
        "source": "docs/RECORD.md Waves 1-3 - samples, not full-volume replay",
    },
    {
        "kind": "kinetic", "t0": 149.0, "t1": 152.0, "accent": C(S.CYAN), "zoom": True,
        "kicker": "the workload",
        "lines": [
            {"text": "THEN THE *REAL*", "at": 0.1, "size": 128},
            {"text": "*WORKLOAD.*", "at": 0.6, "size": 128},
        ],
        "source": "muse-softfloat/README.md - the public proof",
    },
    # -- 8. IAS15 climax 152-174 ----------------------------------------------
    {
        "kind": "orbit", "t0": 152.0, "t1": 166.0, "accent": C(S.CYAN),
        "kicker": "the workload // REBOUND IAS15, figure-8",
        "fig8": True, "scale": 320.0, "trail": 300, "cx_frac": 0.63,
        "lines_rgb": [
            ["REBOUND'S IAS15", 88, C(S.INK)],
            ["UNMODIFIED SOURCE", 60, C(S.CYAN)],
            ["SAME BITS OUT", 60, C(S.AMBER)],
        ],
        "sub": "period: 944 board steps - time-lapsed here",
        "sub_at": 2.0,
        "tag": "ILLUSTRATION: same figure-8 ICs, Python float64 - proof = hash-lock, next",
        "source": "claim: docs/RECORD.md Wave 3",
    },
    {
        "kind": "hashlock", "t0": 166.0, "t1": 174.0, "accent": C(S.GREEN),
        "kicker": "IAS15 on silicon // the hash-lock",
        "title": "STEP BY STEP. BIT BY BIT.",
        "steps": [0, 944, 2000],
        "stamp": "2,001 / 2,001 RECORDS - BIT-IDENTICAL ON SILICON",
        "sub": "measured: 1.58 steps/s at 125 MHz (1,000-step block) - one period = 944 steps, ~10 min",
        "source": "hashes_native.txt == hashes_board.txt (re-compared at render)",
    },
    # -- 9. Close 174-180 ------------------------------------------------------
    {
        "kind": "kinetic", "t0": 174.0, "t1": 180.0, "accent": C(S.AMBER), "zoom": True,
        "kicker": "muse-softfloat",
        "lines": [
            {"text": "IEEE 754,", "at": 0.15, "size": 144},
            {"text": "*HONESTLY.*", "at": 0.75, "size": 144},
        ],
        "sub": "github.com/loganw234/muse-softfloat - MIT - Meta AI Developer Hackathon 2026",
        "sub_at": 1.7,
        "source": "muse-softfloat/README.md + LICENSE",
    },
]

TOTAL = PROOF[-1]["t1"]
TOTAL_FINAL = FINAL[-1]["t1"]


def validate(timeline: list[dict]) -> None:
    prev_end = 0.0
    for sc in timeline:
        assert sc["t1"] > sc["t0"], sc
        assert abs(sc["t0"] - prev_end) < 0.02, f"gap/overlap before {sc['kind']} at {sc['t0']}"
        for t_ in (sc["t0"], sc["t1"]):
            beats = t_ / S.BEAT
            assert abs(beats - round(beats)) < 0.02, f"cut at {t_}s is off the beat grid"
        prev_end = sc["t1"]


if __name__ == "__main__":
    validate(PROOF)
    print(f"proof timeline OK: {len(PROOF)} scenes, {TOTAL:.1f}s")
    for sc in PROOF:
        print(f"  {sc['t0']:5.1f}-{sc['t1']:5.1f}  {sc['kind']}")
    validate(FINAL)
    print(f"final timeline OK: {len(FINAL)} scenes, {TOTAL_FINAL:.1f}s")
    for sc in FINAL:
        print(f"  {sc['t0']:5.1f}-{sc['t1']:5.1f}  {sc['kind']:9}  {sc.get('kicker', '')}")
