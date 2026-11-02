import json, subprocess
from pathlib import Path

REPO = "muse-softfloat"

def git_time(sha):
    return subprocess.check_output(
        ["git", "-C", REPO, "log", "-1", "--format=%cI", sha]).decode().strip()

def append(path, rows):
    p = Path(path)
    before = p.read_bytes()
    existing = [json.loads(x) for x in before.decode("utf-8").splitlines() if x.strip()]
    with p.open("ab") as out:
        if not before.endswith(b"\n"):
            out.write(b"\n")
        for r in rows:
            out.write((json.dumps(r) + "\n").encode("utf-8"))
    after = p.read_bytes()
    assert after[:len(before)] == before
    now = [json.loads(x) for x in after.decode("utf-8").splitlines() if x.strip()]
    print(p.name, len(existing), "->", len(now))
    return now

# --- corrections: C5 (carried) + NC1 + NC2, all auditor-sourced, lead-accepted
twiddle_brief = "ledger/briefs/w5-twiddledoc.md"
print("twiddle brief exists:", Path(twiddle_brief).exists())
append(f"{REPO}/docs/metrics/corrections.jsonl", [
    {"wave": "wave5", "brief": "ledger/briefs/w5-twiddledoc.md",
     "by": "verifier-w5twiddledoc", "at": "2026-10-28",
     "text": "TWIDDLES.md:370 kiss_fftr.c sha 56->64 chars (fix a41f026, merge 97d1cbe); rowed late at the seal per auditor-adherence-seal C5",
     "accepted": True},
    {"wave": "wave6", "brief": "ledger/briefs/w6-metrics.md",
     "by": "auditor-adherence-seal", "at": "2026-11-01T17:17:07-07:00",
     "text": "merge 47f5ea7 body + RECORD seal entry say briefs 39->44 (the metrics branch alone); the union merge actually added 6 rows (captions 1 + metrics 5) = 45 nonempty rows in the merged tree",
     "accepted": True},
    # NC2 intentionally NOT rowed: lead re-check 2026-11-01 found the
    # ledger span-end line already reads 2026-10-30T15:43:55-07:00;
    # recorded in the RECORD seal entry instead of a phantom row.
])

# --- escalations SD-4: three late revision-round rows, stamps from git/passes
passes = [json.loads(x) for x in open(f"{REPO}/docs/metrics/passes.jsonl", encoding="utf-8") if x.strip()]
def pass_end(agent):
    rs = [r for r in passes if r.get("agent") == agent]
    assert rs, agent
    return rs[-1]["end"]

print("fix commit times:",
      {s: git_time(s) for s in ("caf00b0", "8751b11", "e1b0b46")})
append(f"{REPO}/docs/metrics/escalations.jsonl", [
    {"wave": "wave6", "from": "verifier-w6ci", "to": "lead",
     "sent": pass_end("verifier-w6ci"), "means": "file", "test": False,
     "answered": git_time("caf00b0"),
     "note": "F3 finding on the verified parcel; genuine fix caf00b0 merged post-copy without re-verification, disclosed and CI-reproven (late row per auditor SD-4)"},
    {"wave": "polish", "from": "verifier-polish1", "to": "lead",
     "sent": pass_end("verifier-polish1"), "means": "file", "test": False,
     "answered": git_time("8751b11"),
     "note": "twiddle_gate genuine fix 8751b11 merged post-copy without re-verification, disclosed (late row per auditor SD-4)"},
    {"wave": "wave6", "from": "parcel-w6judgemap", "to": "lead",
     "sent": pass_end("parcel-w6judgemap"), "means": "file", "test": False,
     "answered": git_time("e1b0b46"),
     "note": "demo interval expectation still carried the pre-augint hash on main; lead restamped it in e1b0b46 pre-merge (late row per auditor SD-4)"},
])
print("done")
