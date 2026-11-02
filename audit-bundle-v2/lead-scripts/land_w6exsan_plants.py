import json

SETS = [
    dict(verifier="verifier-w6examples",
         work="Wave 6: examples on-ramp (host + Pico)",
         key="c9625a5726c87bdd38e1c9826178bded947a3e8eacea94f7b078192ee32f4b66",
         rows=[
             ("host example pinned 1/10 expectation off by one ulp",
              "F1: ...999b vs Fraction-bracketed ...999a; pristine build EXAMPLE FAIL rc=1"),
             ("committed expected output wrong on an exact product",
              "F2: expected.txt ...0001 vs exact 3.0 = ...0000 in main.c, README, library output"),
             ("host build passes even when stdout differs",
              "F3: failed diff prints 'diff noted' then false PASS rc=0 on a one-digit corruption"),
             ("CI regenerates the expectation instead of enforcing it",
              "F4: step named 'output diff enforced' runs build.sh regen, overwriting expected.txt rc=0"),
             ("pico example expectation diverges from the host mirror",
              "F1+F6: verifier named the same wrong constant in both main.c files (both planted digits matched, mirror intact but wrong vs derivation)"),
         ]),
    dict(verifier="verifier-w6sanitize",
         work="Wave 6: sanitize gate budget (trap here, full in CI)",
         key="be4c5af07de882e421f343a52c590f633446a8ee48a0d2a686c4d01179718d35",
         rows=[
             ("trap flavour made recoverable: findings print and exit 0",
              "F2: observed flags '-fsanitize=undefined' need -lubsan and SKIP in 0s, contradicting run.sh's own no-runtime trap comment; linkable trap-on-error variant identified"),
             ("UB canary no longer overflows",
              "F3: argc=1 so (INT_MAX-100)+1 never overflows; canary dead as invoked"),
             ("runtime-absent skip claims a clean PASS",
              "F2/F5: skip body text 'all sets clean, zero findings, PASS for this flavour' flagged against the no-PASS-verdict design"),
             ("flavour refusal inverted: sanitize budget itself refused when set",
              "F1: trap/full/bogus+sanitize REFUSED rc=2; full+standard silently ignored (merge-gate leak), all measured"),
             ("CI sanitize job never runs the address flavour",
              "F4: run line MSF_SANITIZE=trap while job name/comments/artefact globs claim full"),
         ]),
]
path = "muse-softfloat/docs/metrics/plants.jsonl"
before = open(path, "rb").read()
assert b"verifier-w6examples" not in before and b"verifier-w6sanitize" not in before
with open(path, "ab") as out:
    if not before.endswith(b"\n"):
        out.write(b"\n")
    for s in SETS:
        for i, (shape, note) in enumerate(s["rows"], 1):
            r = {"wave": "wave6", "verifier": s["verifier"], "work": s["work"],
                 "key_sha256": s["key"], "plant": i, "shape": shape,
                 "grade": "caught", "graded_by": "lead",
                 "checked_by": "lead-merge", "note": note}
            out.write((json.dumps(r) + "\n").encode("utf-8"))
after = open(path, "rb").read()
assert after[:len(before)] == before
allrows = [json.loads(x) for x in after.decode("utf-8").splitlines() if x.strip()]
print("plants total=%d caught=%d" % (
    len(allrows), sum(1 for r in allrows if r["grade"] == "caught")))
