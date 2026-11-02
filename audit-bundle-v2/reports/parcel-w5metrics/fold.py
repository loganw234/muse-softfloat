#!/usr/bin/env python3
"""w5-metrics fold: extractor output + ledger/RECORD/git annotations -> new rows.

Reads extract-out/{usage,passes}.jsonl (sanctioned extractor, --until the
SF-2-close record commit) and the frozen docs/metrics files; writes
new-{usage,passes,escalations,briefs}.jsonl in this scratch dir only.
Every restated value cites its record source in the tables below; the
script refuses (asserts) on any unmapped session or missing source row.
"""
import json
import re
from collections import defaultdict
from pathlib import Path

WS = Path(r"C:\Users\logan\source\repos\Muse-Softfloat")
WT = WS / "worktrees/w5-metrics"
HERE = Path(__file__).parent
SID = re.compile(r"session ([0-9a-f-]{36})")


def load(p):
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


inv = json.loads((HERE / "inventory1.json").read_text(encoding="utf-8"))
youare = {r["session"]: r["youare"] for r in inv["lead_subtree"]}

# Sessions whose dispatched role label is absent from early records; identity
# from ledger/scratch/commit records (see report for per-session citations).
OVERRIDES = {
    # verifier-sf1: 5 Workflow lens/synthesis children, brief sf1-verify.md,
    # ledger/verifier-sf1.md + scratch/sf1-verify/report.md (synthesis PASS).
    "d322adf0-83bd-73b6-82cd-8288d575c5ce": "verifier-sf1",
    "d322acf0-83bd-7203-82cd-8188d575c41b": "verifier-sf1",
    "d34d7516-1d09-749c-8c2b-f0cbe582aeb4": "verifier-sf1",
    "d34d7816-1d09-79b5-8c2b-f3cbe582b3cd": "verifier-sf1",
    "24110025-b6a7-7c1e-8700-bc5df2ed32e6": "verifier-sf1",
    # approval-audit: scratch/approval-audit/report.md (SF-0 licence audit).
    "18d430fa-c715-7776-8de8-5b60f11797de": "approval-audit",
    # twiddledoc fix child: authored a41f026 on wave5-twiddledoc inside this
    # span (commit body), appended to the parcel report/ledger; no own name.
    "921371d5-1bb5-7040-8b24-9b4df1999268": "parcel-w5twiddledoc",
}

brief_rows = load(WT / "docs/metrics/briefs.jsonl")
work_by_author = {r["author"]: r["work"] for r in brief_rows}

WORK_EXP2 = ("SF-2 Step 3a exp2/exp2m1 correctly rounded (6 rows, "
             "binary16/32/64 bundle; Tier 2 57 registered / 51 implemented)")
WORK_TRIGSPIKE = "SF-1 Step 2b sinPi/cosPi pricing spike (Fork B; PRICED-GO)"
WORK_METRICS = ("Wave 5 close metrics refresh (usage/passes/escalations/briefs "
                "brought current through SF-2 close, append-only)")

# agent -> (wave, role, work, extras dict, source-short)
A = {}
def reg(agent, wave, role, work, extras=None, src=""):
    A[agent] = (wave, role, work, extras or {}, src)

# --- wave0/wave1 lead-work checks never rowed (ledger verdict lines) ---
reg("verifier-extractor", "wave0", "verifier", "Wave 0 metrics extraction",
    {"a": 0, "b": 0, "verdict": "READY", "sent_back": False}, "scratch/verifier-extractor/report.md:13 READY (a)0 (b)0")
reg("sf0-evidence-auditor", "wave0", "surveyor", "SF-0 evidence audit", {}, "ledger/sf0-evidence-auditor.md")
reg("verifier-sf0", "wave0", "verifier", "SF-0 plan of record",
    {"a": 0, "b": 6, "verdict": "NOT READY", "sent_back": True}, "ledger/verifier-sf0.md (a)0 (b)6")
reg("rechecker-sf0", "wave0", "verifier", "SF-0 plan of record",
    {"a": 0, "b": 2, "verdict": "NOT READY", "sent_back": True}, "ledger/rechecker-sf0.md (a)0 (b)2")
reg("rechecker2-sf0", "wave0", "verifier", "SF-0 plan of record",
    {"a": 0, "b": 0, "verdict": "READY", "sent_back": False}, "ledger/rechecker2-sf0.md READY 0,0")
reg("approval-audit", "wave0", "surveyor", "SF-0 approval licence audit", {}, "scratch/approval-audit/report.md")
reg("verifier-approval", "wave0", "verifier", "SF-0 approval + MIT licence recording",
    {"a": 0, "b": 0, "verdict": "READY", "sent_back": False}, "ledger/verifier-approval.md READY 0,0")
reg("verifier-p0", "wave0", "verifier", "P0 shared seam",
    {"a": 0, "b": 0, "verdict": "READY", "sent_back": False}, "ledger/verifier-p0.md READY 0,0")
reg("verifier-w1prep", "wave1", "verifier", "Wave 1 lead prep (de2d48c)",
    {"a": 0, "b": 0, "verdict": "READY", "sent_back": False}, "ledger/verifier-w1prep.md READY 0,0")
reg("rechecker-nanfix", "wave1", "verifier", "NaN-truncate lead fix (4cdb912)",
    {"a": 0, "b": 0, "verdict": "READY", "sent_back": False}, "ledger/rechecker-nanfix.md READY 0,0")

# --- wave4 (work strings verbatim from briefs.jsonl where a row exists) ---
for a_ in ("study-tier2-kissfft", "study-tier2-interval", "study-tier2-clause9", "study-tier2-architecture"):
    reg(a_, "wave4", "surveyor", work_by_author[a_], {}, f"briefs.jsonl author={a_}")
reg("verifier-sf1", "wave4", "verifier", "SF-1 plan of record",
    {"a": 0, "b": 0, "verdict": "READY", "sent_back": False},
    "scratch/sf1-verify/report.md:1 PASS, no (a)/(b); READY mapping disclosed")
reg("verifier-w4seam", "wave4", "verifier", work_by_author["lead-seam"],
    {"a": 3, "b": 2, "verdict": "NOT READY", "sent_back": False},
    "scratch/verifier-w4seam/report.md (a1-a3)(b1-b2)")
reg("study-tier2-oracle0b", "wave4", "surveyor", work_by_author["study-tier2-oracle0b"], {}, "briefs.jsonl")
reg("parcel-w4minmax", "wave4", "author", work_by_author["parcel-w4minmax"],
    {"commit": "128e577e694bebacf11e0cb04548093e61366469"}, "merge 75309d4 2nd parent; RECORD Step 1")
reg("verifier-w4minmax", "wave4", "verifier", work_by_author["parcel-w4minmax"],
    {"a": 0, "b": 5, "verdict": "NOT READY", "sent_back": False}, "ledger/verifier-w4minmax.md (a)0 (b)5")
reg("study-tier2-trigspike", "wave4", "surveyor", WORK_TRIGSPIKE, {}, "brief w4-trigspike.md; ledger/study-tier2-trigspike.md")
reg("parcel-w4interval", "wave4", "author", work_by_author["parcel-w4interval"],
    {"commit": "1d55a8a08366bfc8bfd3ee7bc7a305347c82c705"}, "merge 20bc16b 2nd parent")
reg("verifier-w4interval", "wave4", "verifier", work_by_author["parcel-w4interval"],
    {"a": 2, "b": 3, "verdict": "NOT READY", "sent_back": False}, "ledger/verifier-w4interval.md tags (b)x3 (a)x2")
reg("parcel-w4trig", "wave4", "author", work_by_author["parcel-w4trig"],
    {"commit": "81b76357b357b802ebca9ba39a1e1d9005d5f485"}, "merge da46f51 2nd parent; RECORD Step 2c kernel")
reg("verifier-w4trig", "wave4", "verifier", work_by_author["parcel-w4trig"],
    {"a": 3, "b": 3, "verdict": "NOT READY", "sent_back": False},
    "ledger/verifier-w4trig.md (a)BUILD+(b1-b3)+(a)gen+(a)stale")
reg("parcel-w4kissfft", "wave4", "author", work_by_author["parcel-w4kissfft"],
    {"commit": "d322d0791a59b02db8c451fcc546e716673d8b50"}, "merge 32bbd93 2nd parent")
reg("verifier-w4kissfft", "wave4", "verifier", work_by_author["parcel-w4kissfft"],
    {"a": 4, "b": 1, "verdict": "NOT READY", "sent_back": False},
    "scratch/verifier-w4kissfft/report.md (b1)(a1-a4)")

# --- wave5 lead work + studies + audit ---
reg("verifier-readme", "wave5", "verifier", "post-Tier-2 README update",
    {"a": 5, "b": 1, "verdict": "NOT READY", "sent_back": True},
    "report F1-F5 (a) contradicted, F6 (b) no authority (brief classes); fix d87c87c after verdict")
reg("study-sf2-algebraic", "wave5", "surveyor", "SF-2 input study: algebraic Clause 9.2 bundle pricing", {}, "brief sf2-algebraic.md")
reg("study-sf2-attribute", "wave5", "surveyor", "SF-2 input study: roundTiesToAway fifth attribute pricing", {}, "brief sf2-attribute.md")
reg("study-sf2-augmented", "wave5", "surveyor", "SF-2 input study: Clause 9.5 augmented arithmetic design", {}, "brief sf2-augmented.md")
reg("study-sf2-explog", "wave5", "surveyor", "SF-2 input spike: exp/log Clause 9.2 pricing", {}, "brief sf2-explog.md")
reg("verifier-sf2", "wave5", "verifier", "SF-2 plan of record",
    {"a": 4, "b": 1, "verdict": "NOT READY", "sent_back": True},
    "report FAIL->NOT READY; F1(a)F2(b)F3(a)F4(c->a)F5(a); folded f3eea91")
reg("verifier-readme2", "wave5", "verifier", "Wave 5 README restatement",
    {"a": 5, "b": 0, "verdict": "NOT READY", "sent_back": False},
    "report F1-F5 all (a) contradicted claims (brief classes)")
reg("auditor-adherence-2", "wave5", "surveyor", "methods adherence audit (Phase 0 through Wave 5 Step 1)", {},
    "scratch/audit-adherence-2/report.md")

# --- wave5 parcels (author commit = merge second parent = branch tip) ---
reg("parcel-w5attr", "wave5", "author", work_by_author["parcel-w5attr"],
    {"commit": "8bfc8776929eb123bf078da76ce2676cbb9c4e7a"}, "merge 6e0f2f2 2nd parent; RECORD Step 1")
reg("verifier-w5attr", "wave5", "verifier", work_by_author["parcel-w5attr"],
    {"a": 3, "b": 2, "verdict": "NOT READY", "sent_back": False}, "scratch/verifier-w5attr/report.md:1 explicit 3(a)+2(b)")
reg("parcel-w5alg1", "wave5", "author", work_by_author["parcel-w5alg1"],
    {"commit": "b886e038d095bfad643ccb937f44abd03bcaaa7f"}, "merge 0de6a30 2nd parent; RECORD Step 2a")
reg("verifier-w5alg1", "wave5", "verifier", work_by_author["parcel-w5alg1"],
    {"a": 1, "b": 3, "verdict": "NOT READY", "sent_back": False}, "report (b1)(b2)(b3)+(a); ledger headline agrees")
reg("parcel-w5alg2", "wave5", "author", work_by_author["parcel-w5alg2"],
    {"commit": "e858498242967f2ef4713e96521253dd6c7a088d"}, "merge 4a80126 2nd parent; RECORD Step 2b")
reg("verifier-w5alg2", "wave5", "verifier", work_by_author["parcel-w5alg2"],
    {"a": 2, "b": 3, "verdict": "NOT READY", "sent_back": False}, "report table F1-F3 (b), F4-F5 (a)")
reg("parcel-w5site", "wave5", "author", work_by_author["parcel-w5site"],
    {"commit": "cd0970032fa1f4c7ada0f20d5721c7d35564fa6d"}, "merge 3a09c76 2nd parent")
reg("verifier-w5site", "wave5", "verifier", work_by_author["parcel-w5site"],
    {"a": 4, "b": 1, "verdict": "NOT READY", "sent_back": False},
    "brief classes: F1(b) behaviour, F2/F3/F5 (a) claims, F4 (c->a) link")
reg("parcel-w5demo", "wave5", "author", work_by_author["parcel-w5demo"],
    {"commit": "3feebb976d4df2b4da972fa2810d4e25c0ba13d6"}, "merge eac88b0 2nd parent")
reg("verifier-w5demo", "wave5", "verifier", work_by_author["parcel-w5demo"],
    {"a": 1, "b": 4, "verdict": "NOT READY", "sent_back": False},
    "brief classes: F1-F4 (b) wrong evidence, F5 (a)+(c) fresh-clone break")
reg("parcel-w5exp2", "wave5", "author", WORK_EXP2,
    {"commit": "2618b3454a5e439dd7b23531256ccb000c669128"}, "merge 7772da7 2nd parent; RECORD Step 3a")
reg("verifier-w5exp2", "wave5", "verifier", WORK_EXP2,
    {"a": 3, "b": 2, "verdict": "NOT READY", "sent_back": False},
    "report F1 (b) explicit; F2/F3/F5 (a) regression-family artefacts, F4 (b) wrong vector (cf. w3str F-D)")
reg("parcel-w5twiddledoc", "wave5", "author", work_by_author["parcel-w5twiddledoc"],
    {"commit": "0cad04332adfd2a22bbed5ffff04cfdc840eb274"}, "parcel tip at report; fix pass separately")
reg("verifier-w5twiddledoc", "wave5", "verifier", work_by_author["parcel-w5twiddledoc"],
    {"a": 7, "b": 0, "verdict": "NOT READY", "sent_back": True},
    "ledger/verifier-w5twiddledoc.md 7 blocking (a)-family doc claims; fix a41f026 followed")
reg("parcel-w5log2", "wave5", "author", work_by_author["parcel-w5log2"],
    {"commit": "826f836c8b7c55a0e0ee0cf52666451a8f2aa4a1"}, "merge cf81644 2nd parent; RECORD Step 3b")
reg("verifier-w5log2", "wave5", "verifier", work_by_author["parcel-w5log2"],
    {"a": 1, "b": 4, "verdict": "NOT READY", "sent_back": False},
    "ledger F1(a) F2(b) F3(b/c) F4(b) F5 vector artefact (b); brief (a)=wrong result")
reg("parcel-w5aug", "wave5", "author", work_by_author["parcel-w5aug"],
    {"commit": "37414532b82262dbdfdc54c67a7dcf49a5744194"}, "merge 4a0b0d4 2nd parent; RECORD Step 4")
reg("verifier-w5aug", "wave5", "verifier", work_by_author["parcel-w5aug"],
    {"a": 5, "b": 1, "verdict": "NOT READY", "sent_back": False},
    "report F1-F4 (a) wrong triples + (c) claim bullet ->a; F5 (b) artefact")
reg("study-kissfft-visual", "wave5", "surveyor", "KissFFT visual feasibility study", {}, "brief study-kissfft-visual.md")
reg("study-tokens-visual", "wave5", "surveyor", "tokens visual feasibility study (owner vs project tokens)", {},
    "brief study-tokens-visual.md")

# Pass grouping: agent -> list of passes; each pass = (sessions, role, extras, why)
FIX_COMMIT = "a41f026bf3e6b4b742d511179d12c837ec776e75"
GROUP_WHY = {
    "verifier-sf1": "5 lens/synthesis sessions folded to one reporting pass (attempt-1 pair stopped by owner parity rule; RECORD Wave 4 entry)",
    "verifier-w5exp2": "first verifier child died mid-probes without reporting (RECORD Step 3a); tokens retained in usage, pass is the second attempt's span set",
    "parcel-w5aug": "3 attempts on one branch (brief: aug x3 attempts); only the set reported a tip",
}

ex_u_rows = load(HERE / "extract-out/usage.jsonl")
ex_p_rows = load(HERE / "extract-out/passes.jsonl")
def sid_of(row):
    m = SID.search(row.get("note", ""))
    assert m, row
    return m.group(1)

ex_u = {sid_of(r): r for r in ex_u_rows}
ex_p = {sid_of(r): r for r in ex_p_rows}
frozen_sids = {sid_of(r) for r in load(WT / "docs/metrics/usage.jsonl")}
new_sids = [s for s in ex_u if s not in frozen_sids]
assert len(new_sids) == 62, len(new_sids)

def agent_of(sid):
    if sid in OVERRIDES:
        return OVERRIDES[sid]
    y = youare.get(sid)
    if y:
        return y
    lab = ex_u[sid]["agent"]  # native Role: label (sf0-evidence-auditor, study-tier2-*)
    assert lab != sid, f"no role label for {sid}"
    return lab

by_agent = defaultdict(list)
for sid in new_sids:
    by_agent[agent_of(sid)].append(sid)
unmapped = set(by_agent) - set(A)
assert not unmapped, f"agents without annotation: {unmapped}"
assert len(by_agent) == 54, (len(by_agent), sorted(by_agent))

REAS = re.compile(r"reasoning_tokens=(\d+)")
def reasoning(row):
    m = REAS.search(row.get("note", ""))
    return int(m.group(1)) if m else 0

usage_out, pass_out = [], []
for agent, sids in by_agent.items():
    wave, role, work, extras, src = A[agent]
    sids.sort(key=lambda s: ex_p[s]["start"])
    # --- usage: one row per (agent, model), summed over its sessions ---
    by_model = defaultdict(list)
    for s in sids:
        by_model[ex_u[s]["model"]].append(s)
    for model, ms in sorted(by_model.items()):
        rows = [ex_u[s] for s in ms]
        relabelled = any(r["agent"] != agent for r in rows)
        if len(ms) == 1:
            r = dict(rows[0])
            r["wave"] = wave
            r["agent"] = agent
            if relabelled:
                r["note"] += "; relabelled in w5-metrics fold (role label + ledger attribution)"
            r["note"] += "; backfill (w5-metrics)"
        else:
            r = {"wave": wave, "agent": agent, "model": model,
                 "output_tokens": sum(x["output_tokens"] for x in rows),
                 "input_tokens": sum(x["input_tokens"] for x in rows),
                 "source": "log",
                 "cached_tokens": sum(x["cached_tokens"] for x in rows),
                 "messages": sum(x["messages"] for x in rows),
                 "note": ("sessions " + ", ".join(ms) +
                          f"; label via role label + ledger attribution in w5-metrics fold; "
                          f"reasoning_tokens={sum(reasoning(x) for x in rows)}; backfill (w5-metrics)")}
        usage_out.append((ex_p[ms[0]]["start"], r))
    # --- passes ---
    if agent == "parcel-w5twiddledoc":
        author_sid, fix_sid = sids[0], sids[1]
        assert ex_p[fix_sid]["start"] > ex_p[author_sid]["end"]
        for num, (s, rrole, commit, why) in enumerate((
                (author_sid, "author", extras["commit"], ""),
                (fix_sid, "fixer", FIX_COMMIT,
                 "unnamed fix child after verifier-w5twiddledoc F2 (commit a41f026 body); same agent, pass 2")), 1):
            ep = ex_p[s]
            row = {"wave": wave, "agent": agent, "role": rrole, "work": work, "pass": num,
                   "start": ep["start"], "end": ep["end"], "tool_uses": ep["tool_uses"],
                   "source": "transcript",
                   "note": ep["note"] + (f"; {why}" if why else "") +
                           "; restated by w5-metrics fold from ledger/RECORD/git (extractor role_for gap)",
                   "commit": commit}
            pass_out.append((ep["start"], row))
        continue
    eps = [ex_p[s] for s in sids]
    if len(sids) == 1:
        note = eps[0]["note"] + "; restated by w5-metrics fold from ledger/RECORD/git (extractor role_for gap)"
        start, end, tools = eps[0]["start"], eps[0]["end"], eps[0]["tool_uses"]
    else:
        shas = []
        for e in eps:
            m = re.search(r"sha256 ([0-9a-f]{12})", e["note"])
            shas.append(m.group(1) if m else "?")
        note = ("sessions " + ", ".join(sids) + "; transcript sha256 " + ",".join(shas) +
                "; " + GROUP_WHY[agent] +
                "; restated by w5-metrics fold from ledger/RECORD/git (extractor role_for gap)")
        start = min(e["start"] for e in eps)
        end = max(e["end"] for e in eps)
        tools = sum(e["tool_uses"] for e in eps)
    row = {"wave": wave, "agent": agent, "role": role, "work": work, "pass": 1,
           "start": start, "end": end, "tool_uses": tools, "source": "transcript", "note": note}
    row.update(extras)
    pass_out.append((start, row))

usage_out.sort(key=lambda t: t[0])
pass_out.sort(key=lambda t: t[0])
def write_jsonl(path, rows, spaced=False):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n" if spaced else json.dumps(r, separators=(",", ":")) + "\n")

write_jsonl(HERE / "new-usage.jsonl", [r for _, r in usage_out])
write_jsonl(HERE / "new-passes.jsonl", [r for _, r in pass_out])
print(f"usage new={len(usage_out)} passes new={len(pass_out)} agents={len(by_agent)}")

# --- escalations (sent stamps: urgent-file Written lines; ledger entry stamps) ---
esc = [
    {"wave": "wave3", "from": "video-final", "to": "lead", "sent": "2026-10-27T10:37:11-07:00",
     "means": "file", "test": True},
    {"wave": "wave4", "from": "study-tier2-kissfft", "to": "lead", "sent": "2026-10-27T13:55:26-07:00",
     "means": "file", "test": True},
    {"wave": "wave4", "from": "study-tier2-clause9", "to": "lead", "sent": "2026-10-27T13:56:00-07:00",
     "means": "file", "test": True},
    {"wave": "wave4", "from": "study-tier2-interval", "to": "lead", "sent": "2026-10-27T13:56:08-07:00",
     "means": "file", "test": True},
    {"wave": "wave4", "from": "study-tier2-architecture", "to": "lead", "sent": "2026-10-27T13:56:19-07:00",
     "means": "file", "test": True},
    {"wave": "wave5", "from": "parcel-w5alg1", "to": "lead", "sent": "2026-10-28T06:36:21-07:00",
     "means": "file", "test": False, "answered": "2026-10-28T06:59:35-07:00",
     "note": "board build wiring for src/msf_alg.c outside owned files; lead wired it at merge in 109b814"},
    {"wave": "wave5", "from": "parcel-w5alg2", "to": "lead", "sent": "2026-10-28T07:51:02-07:00",
     "means": "file", "test": False, "answered": "2026-10-28T08:55:26-07:00",
     "note": "tests/VECTORS.md mpfr-alg tag wording says rSqrt only, outside owned files; generalised by lead in 53d2265"},
]
write_jsonl(HERE / "new-escalations.jsonl", esc, spaced=True)

# --- briefs (only sourceable base+timebox; own row last) ---
briefs_new = [
    {"wave": "wave4", "work": WORK_TRIGSPIKE, "author": "study-tier2-trigspike",
     "base": "b704b4c9b805b584a2e221c3fa889017d480ac88", "time_box_min": 300, "ceiling_lines": 0,
     "ceiling_text": "scratch design note only; 0 repository lines (brief w4-trigspike.md)",
     "note": "row authored late at the w5-metrics refresh (brief + ledger/study-tier2-trigspike.md)"},
    {"wave": "wave5", "work": WORK_EXP2, "author": "parcel-w5exp2",
     "base": "4a8012636d5b2c5785935dc64bc137a39d4556d6", "time_box_min": 900, "ceiling_lines": 0,
     "ceiling_text": "no line ceiling stated in brief w5-exp2.md; owned-files list is the bound, generated files/vectors excluded",
     "note": "row authored late at the w5-metrics refresh; named missing by parcel-w5log2 (RECORD Step 3b)"},
    {"wave": "wave5", "work": WORK_METRICS, "author": "parcel-w5metrics",
     "base": "5142594f1f70be997de3cb5c28b7bf4d8ea80bc5", "time_box_min": 480, "ceiling_lines": 0,
     "ceiling_text": "no line ceiling stated in brief w5-metrics.md; owned-files list is the bound (docs/metrics appends only)"},
]
write_jsonl(HERE / "new-briefs.jsonl", briefs_new, spaced=True)
print(f"escalations new={len(esc)} briefs new={len(briefs_new)}")
for agent in sorted(A):
    print(f"SRC {agent}: {A[agent][4]}")

