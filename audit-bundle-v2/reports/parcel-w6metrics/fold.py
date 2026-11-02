#!/usr/bin/env python3
"""w6-metrics fold: extractor output + ledger/RECORD/git annotations -> new rows.

Reads extract-out/{usage,passes}.jsonl (sanctioned extractor, --until the
Wave 6 close base cdc40ae committer time) and the frozen docs/metrics files;
writes new-{usage,passes,escalations,briefs}.jsonl in this scratch dir only.
Every restated value cites its record source in the tables below; the script
refuses (asserts) on any unmapped session, unresolvable commit/base, or an
agent/session count that differs from the expected list built FIRST from
ledger/briefs + ledger files + git log (see report coverage table).
"""
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
WS = Path(r"C:\Users\logan\source\repos\Muse-Softfloat")
WT = WS / "worktrees/w6-metrics"
HERE = Path(__file__).parent
SID = re.compile(r"session ([0-9a-f-]{36})")


def load(p):
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def git(*args):
    r = subprocess.run(["git", "-C", str(WT), *args], capture_output=True, text=True)
    assert r.returncode == 0, (args, r.stderr)
    return r.stdout.strip()


def full(sha):
    return git("rev-parse", "--verify", f"{sha}^{{commit}}")


def ancestor(sha, ref="cdc40aec9b11eeab61ab3c6cc9940b5dbbac4a67"):
    r = subprocess.run(["git", "-C", str(WT), "merge-base", "--is-ancestor", sha, ref],
                       capture_output=True, text=True)
    assert r.returncode == 0, f"{sha} not ancestor of {ref}"


inv = json.loads((HERE / "inventory.json").read_text(encoding="utf-8"))
inv_by_sid = {r["session"]: r for r in inv["lead_subtree"]}

brief_rows = load(WT / "docs/metrics/briefs.jsonl")
work_by_author = {r["author"]: r["work"] for r in brief_rows}

# agent -> (wave, role, work, extras, source-short, expected session count)
A = {}
def reg(agent, wave, role, work, extras=None, src="", n=1):
    A[agent] = (wave, role, work, extras or {}, src, n)

W_METRICS5 = work_by_author["parcel-w5metrics"]
W_README3 = work_by_author["parcel-w5readme3"]
W_POLISH = work_by_author["lead-polish1"]
W_AUGINT = work_by_author["parcel-w6augint"]
W_CI = work_by_author["parcel-w6ci"]
W_EXAMPLES = work_by_author["parcel-w6examples"]
W_SANITIZE = work_by_author["parcel-w6sanitize"]
W_JUDGEMAP = work_by_author["parcel-w6judgemap"]
W_FILMRETIME = work_by_author["parcel-w6filmretime"]
W_POPUPS = work_by_author["parcel-w6popups"]
W_AUDITFINAL = "whole-project methods audit (Phase 0 through Wave 5 close)"
W_SANSTUDY = ("Wave 6 queue item 3 feasibility: ASan/UBSan pass over the host runners "
              "(compiler probes + largest feasible scratch runs, parcel shape recommendation)")
W_EPIDEMIC = "Epidemic Sound licence-fact study for the hackathon film music track (web research only)"
W_SPARKAUDIT = ("Spark stale-information polish audit (5 slices + critic + synthesis, "
                "read-only, audit-bundle excluded)")

# --- wave5 close (briefs rows already wave5) ---
reg("parcel-w5metrics", "wave5", "author", W_METRICS5,
    {"commit": full("3f29682")}, "merge a1a888f 2nd parent = wave5-metrics tip; report READY")
reg("verifier-w5metrics", "wave5", "verifier", W_METRICS5,
    {"a": 7, "b": 1, "verdict": "NOT READY", "sent_back": False},
    "report F1-F4 + minors F5-F8; kit rule (a)=regression vs in-copy record (F1,F3-F8), (b)=wrong answer (F2 token count); tip merged unchanged")
reg("parcel-w5readme3", "wave5", "author", W_README3,
    {"commit": full("498a916")}, "merge 5a387e5 2nd parent = wave5-readme3 tip; report READY")
reg("verifier-w5readme3", "wave5", "verifier", W_README3,
    {"a": 7, "b": 1, "verdict": "NOT READY", "sent_back": False},
    "report F1-F8; (b)=F5 wrong sample vector (w5log2/w5exp2 wrong-vector precedent), rest (a) claims vs tree; tip merged unchanged")
reg("auditor-adherence-final", "wave5", "surveyor", W_AUDITFINAL, {},
    "ledger/auditor-adherence-final.md: ADHERENT WITH SLIPS at bc807e6")

# --- polish round: 2026-10-29 film studies (post-close, pre-Wave-6 queue) ---
FILM5 = [
    ("study-video-intro-outro", "demo film intro/outro rough-draft scenes (phone messenger concept, Spark)"),
    ("study-video-gitvisual", "demo film git-visuals main segment rough draft"),
    ("study-video-intro-polish", "demo film intro/outro polish pass"),
    ("study-video-gitvisual-polish", "demo film git segment polish pass (v2)"),
    ("study-video-why", "demo film why-a-custom-softfloat segment draft"),
    ("study-video-gitvisual-v3", "demo film git segment rework v3 (staging)"),
    ("study-video-why-v2", "demo film idea-breakdown segment + slowed why comparison (v2)"),
    ("study-video-gitvisual-v4", "demo film git segment v4 (marble sync + packaging)"),
]
for agent, work in FILM5:
    reg(agent, "polish", "surveyor", work, {}, f"brief ledger/briefs/{agent}.md Role line")
reg("study-video-textpacing", "polish", "surveyor",
    "demo film text/pacing revision (word-count dwell rule, plain language; two parallel agents: front + git v5)",
    {}, "brief study-video-textpacing.md (two parallel agents); ledger/lead.md 2026-10-29 video entry Agent A/B", n=2)
reg("auditor-staleinfo-spark", "polish", "surveyor", W_SPARKAUDIT, {},
    "ledger/lead.md '2026-10-29 Spark stale-info polish audit': 5 slices + critic + synthesis", n=7)
reg("verifier-polish1", "polish", "verifier", W_POLISH,
    {"a": 4, "b": 0, "verdict": "NOT READY", "sent_back": True},
    "report F1-F4 all (a) changed claims vs tree (F3 link (c->a) site precedent); branch revised after verdict 8751b11 (verifier observation) + 227f69f before merge")

# --- wave6 ---
reg("parcel-w6augint", "wave6", "author", W_AUGINT,
    {"commit": full("5ce5ac5")}, "parcel tip in report/RECORD; branch tip 93886a8 is a later lead gate fix, merge 47a405f")
reg("study-w6sanitize", "wave6", "surveyor", W_SANSTUDY, {}, "brief study-w6sanitize.md Job; scratch/study-w6sanitize/report.md")
reg("parcel-w6ci", "wave6", "author", W_CI,
    {"commits": [full("eda5812"), full("5b53bf3")]},
    "pass1 tip eda5812 (ledger); sent back after Linux CI red, pass2 revision 5b53bf3 (lead.md 2026-10-30 CI entries); branch tip caf00b0 is a later lead fix", n=2)
reg("verifier-w6augint", "wave6", "verifier", W_AUGINT,
    {"a": 4, "b": 1, "verdict": "NOT READY", "sent_back": False},
    "report F1-F5; (b)=F1 426 decided-wrong (wrong answer), (a)=F2/F3 vs design record, F4 build (w4trig BUILD=(a) precedent), F5 numbers vs record; tip merged unchanged")
reg("verifier-w6ci", "wave6", "verifier", W_CI,
    {"a": 4, "b": 3, "verdict": "NOT READY", "sent_back": True},
    "report F1-F7 (F8 no finding); (b)=F2 gate runs smoke (site behaviour-swap precedent), F6/F7 wrong tag/control output; (a)=F1/F4 claims, F3 gate-hole (demo precedent), F5 host-gate regression; real F3 fixed post-verdict caf00b0 on branch before merge")
reg("parcel-w6examples", "wave6", "author", W_EXAMPLES,
    {"commit": full("b6e08fd")}, "merge b85e037 2nd parent = branch tip; ledger tip entry")
reg("parcel-w6sanitize", "wave6", "author", W_SANITIZE,
    {"commits": [full("1bc0979"), full("77e6e64")]},
    "pass1 tip 1bc0979 (ledger); sent back after CI sanitize build failure, pass2 revision 77e6e64 = merge 4486cb5 2nd parent (lead.md sanitize CI entries)", n=2)
reg("verifier-w6sanitize", "wave6", "verifier", W_SANITIZE,
    {"a": 5, "b": 0, "verdict": "NOT READY", "sent_back": False},
    "ledger 5 bullets all (a) vs in-copy record/claims (refusal, SKIP vs claimed PASS, dead canary gate-hole, CI claim, stale AGENTS text); report verdict REJECT mapped to kit NOT READY (FAIL->NOT READY precedent); tip merged unchanged")
reg("verifier-w6examples", "wave6", "verifier", W_EXAMPLES,
    {"a": 2, "b": 2, "verdict": "NOT READY", "sent_back": False},
    "report F1-F4; (b)=F1/F2 wrong constants (wrong answer), (a)=F3/F4 checks that cannot fail (gate-hole precedent); report 'NOT merge-ready' mapped to NOT READY; tip merged unchanged")
reg("parcel-w6judgemap", "wave6", "author", W_JUDGEMAP,
    {"commit": full("245a4f5")}, "parcel tip in ledger/report; branch tip e1b0b46 is a later lead fix, merge 870b82f")
reg("verifier-w6judgemap", "wave6", "verifier", W_JUDGEMAP,
    {"a": 4, "b": 1, "verdict": "NOT READY", "sent_back": False},
    "ledger map errors (1)-(5); (b)=(5) wrong expected-interval nibble (wrong-vector precedent), (1)-(4) (a) claims vs record; tip merged unchanged")
reg("study-video-gitvisual-v6", "wave6", "surveyor",
    "film git segment v6 revision in scratch (chase-language replay, falling-opening ending, tokens gate removed, interval epilogue gate) + r2 revision",
    {}, "brief study-video-gitvisual-v6.md; lead.md: r2 revision dispatched to study agent in same scratch", n=2)
reg("study-video-gitvisual-v7", "wave6", "surveyor",
    "film git segment v7 redesign: real process graph (role-coloured lanes per passes episode, plant ticks, DEEP legend)",
    {}, "brief study-video-gitvisual-v7.md Role line")
reg("parcel-w6filmretime", "wave6", "author", W_FILMRETIME,
    {"commit": full("1cfed36")}, "merge 3dfa3d8 2nd parent = branch tip; lead.md film retime entry")
reg("verifier-w6filmretime", "wave6", "verifier", W_FILMRETIME,
    {"a": 4, "b": 1, "verdict": "NOT READY", "sent_back": False},
    "report 3 blockers + 2 notes (findings 1-5); (b)=3 wrong gate rank/cursor behaviour, (a)=1 cap vs code, 2 dwells vs claim, 4/5 notes vs record; tip merged unchanged")
reg("surveyor-epidemiclicense", "wave6", "surveyor", W_EPIDEMIC, {},
    "brief study-epidemic-license.md Role; ledger verdicts PARTLY/PARTLY")
reg("parcel-w6popups", "wave6", "author", W_POPUPS,
    {"commit": full("0708e2e")}, "parcel tip in lead.md popup entry; fixer commit followed on same branch")
reg("fixer-w6popups", "wave6", "fixer", W_POPUPS,
    {"commit": full("ef0215b")}, "brief fix-w6popups.md; merge f36e171 2nd parent = fixer tip")
reg("verifier-w6popups", "wave6", "verifier", W_POPUPS,
    {"a": 6, "b": 0, "verdict": "NOT READY", "sent_back": False},
    "ledger blockers 1-6 all (a) code vs in-copy record (mp4/ledger/row correct, timing regression, mp4!=code); tip merged unchanged")

for agent, (wave, role, work, extras, src, n) in A.items():
    for key in ("commit",):
        if key in extras:
            ancestor(extras[key])
    for c in extras.get("commits", []):
        ancestor(c)

GROUP_WHY = {
    "study-video-textpacing": "two parallel text/pacing agents under one brief (front + git v5, lead.md video entry); folded to one reporting pass",
    "auditor-staleinfo-spark": "5 audit slices + critic + synthesis under one lead dispatch (lead.md Spark stale-info audit entry); folded to one reporting pass",
    "study-video-gitvisual-v6": "v6 draft + r2 revision by the same study agent in the same scratch (lead.md); folded to one reporting pass",
}
MULTI_PASS = {"parcel-w6ci", "parcel-w6sanitize"}  # each session reported its own tip

ex_u_rows = load(HERE / "extract-out/usage.jsonl")
ex_p_rows = load(HERE / "extract-out/passes.jsonl")
def sid_of(row):
    m = SID.search(row.get("note", ""))
    assert m, row
    return m.group(1)

ex_u = {}
for r in ex_u_rows:
    ex_u.setdefault(sid_of(r), []).append(r)
ex_p = {sid_of(r): r for r in ex_p_rows}
frozen_sids = set()
for r in load(WT / "docs/metrics/usage.jsonl"):
    for m in re.finditer(r"[0-9a-f]{8}-[0-9a-f-]{27,}", r.get("note", "")):
        frozen_sids.add(m.group(0))
new_sids = [s for s in ex_u if s not in frozen_sids]
assert len(new_sids) == 45, len(new_sids)

def agent_of(sid):
    r = inv_by_sid[sid]
    if r["youare"]:
        return r["youare"]
    labels = " ".join(r["labels"])
    hits = r["parcel_hits_head"]
    if "study-video-textpacing" in hits or "study-video-textpacing" in labels:
        return "study-video-textpacing"
    if "study-video-gitvisual-v7" in hits:
        return "study-video-gitvisual-v7"
    if "study-video-gitvisual-v6" in hits:
        return "study-video-gitvisual-v6"
    if r["start"].startswith("2026-10-29T20:0"):
        return "auditor-staleinfo-spark"
    lab = ex_u[sid][0]["agent"]
    assert lab != sid, f"no attribution for {sid} ({r['start']}, hits={hits}, labels={r['labels']})"
    return lab

by_agent = defaultdict(list)
for sid in new_sids:
    by_agent[agent_of(sid)].append(sid)
unmapped = set(by_agent) - set(A)
assert not unmapped, f"agents without annotation: {unmapped}"
missing = set(A) - set(by_agent)
assert not missing, f"expected agents with no session: {missing}"
for agent, sids in by_agent.items():
    assert len(sids) == A[agent][5], (agent, len(sids), A[agent][5])
assert len(by_agent) == 35, (len(by_agent), sorted(by_agent))

REAS = re.compile(r"reasoning_tokens=(\d+)")
def reasoning(row):
    m = REAS.search(row.get("note", ""))
    return int(m.group(1)) if m else 0

usage_out, pass_out = [], []
for agent, sids in by_agent.items():
    wave, role, work, extras, src, _n = A[agent]
    sids.sort(key=lambda s: ex_p[s]["start"])
    by_model = defaultdict(list)
    for s in sids:
        for r in ex_u[s]:
            by_model[r["model"]].append((s, r))
    for model, pairs in sorted(by_model.items()):
        rows = [r for _, r in pairs]
        ms = sorted({s for s, _ in pairs}, key=lambda s: ex_p[s]["start"])
        relabelled = any(r["agent"] != agent for r in rows)
        if len(rows) == 1:
            r = dict(rows[0])
            r["wave"] = wave
            r["agent"] = agent
            if relabelled:
                r["note"] += "; relabelled in w6-metrics fold (role label + ledger attribution)"
            r["note"] += "; backfill (w6-metrics)"
        else:
            r = {"wave": wave, "agent": agent, "model": model,
                 "output_tokens": sum(x["output_tokens"] for x in rows),
                 "input_tokens": sum(x["input_tokens"] for x in rows),
                 "source": "log",
                 "cached_tokens": sum(x["cached_tokens"] for x in rows),
                 "messages": sum(x["messages"] for x in rows),
                 "note": ("sessions " + ", ".join(ms) +
                          f"; label via role label + ledger attribution in w6-metrics fold; "
                          f"reasoning_tokens={sum(reasoning(x) for x in rows)}; backfill (w6-metrics)")}
        usage_out.append((ex_p[ms[0]]["start"], r))
    # --- passes ---
    if agent in MULTI_PASS:
        commits = extras["commits"]
        assert len(sids) == len(commits) == 2
        for num, (s, commit) in enumerate(zip(sids, commits), 1):
            ep = ex_p[s]
            why = "first tip sent back by the lead (CI evidence in lead.md); this is the revision pass" if num == 2 else ""
            row = {"wave": wave, "agent": agent, "role": role, "work": work, "pass": num,
                   "start": ep["start"], "end": ep["end"], "tool_uses": ep["tool_uses"],
                   "source": "transcript",
                   "note": ep["note"] + (f"; {why}" if why else "") +
                           "; restated by w6-metrics fold from ledger/RECORD/git (extractor role_for gap)",
                   "commit": commit}
            pass_out.append((ep["start"], row))
        continue
    eps = [ex_p[s] for s in sids]
    if len(sids) == 1:
        note = eps[0]["note"] + "; restated by w6-metrics fold from ledger/RECORD/git (extractor role_for gap)"
        start, end, tools = eps[0]["start"], eps[0]["end"], eps[0]["tool_uses"]
    else:
        shas = []
        for e in eps:
            m = re.search(r"sha256 ([0-9a-f]{12})", e["note"])
            shas.append(m.group(1) if m else "?")
        note = ("sessions " + ", ".join(sids) + "; transcript sha256 " + ",".join(shas) +
                "; " + GROUP_WHY[agent] +
                "; restated by w6-metrics fold from ledger/RECORD/git (extractor role_for gap)")
        start = min(e["start"] for e in eps)
        end = max(e["end"] for e in eps)
        tools = sum(e["tool_uses"] for e in eps)
    row = {"wave": wave, "agent": agent, "role": role, "work": work, "pass": 1,
           "start": start, "end": end, "tool_uses": tools, "source": "transcript", "note": note}
    row.update({k: v for k, v in extras.items() if k != "commits"})
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
nu = [r for _, r in usage_out]
print(f"appended usage totals: in={sum(r['input_tokens'] for r in nu):,} "
      f"out={sum(r['output_tokens'] for r in nu):,} cached={sum(r['cached_tokens'] for r in nu):,} "
      f"msgs={sum(r['messages'] for r in nu):,}")

# --- escalations: none sourceable for this span (see report) ---
write_jsonl(HERE / "new-escalations.jsonl", [], spaced=True)

# --- briefs (only sourceable base+timebox; own row last) ---
W_METRICS6 = ("Wave 6 close metrics refresh (usage/passes/escalations/briefs "
              "brought current through Wave 6 close, append-only)")
briefs_new = [
    {"wave": "wave5", "work": W_AUDITFINAL, "author": "auditor-adherence-final",
     "base": full("bc807e6"), "time_box_min": 360, "ceiling_lines": 0,
     "ceiling_text": "read-only audit; scratch report only, 0 repository lines (brief audit-adherence-final.md)",
     "note": "row authored late at the w6-metrics refresh (brief + ledger/auditor-adherence-final.md freeze bc807e6)"},
    {"wave": "wave6", "work": W_SANSTUDY, "author": "study-w6sanitize",
     "base": full("50aac59"), "time_box_min": 240, "ceiling_lines": 0,
     "ceiling_text": "read-only on the repo; scratch builds only, 0 repository lines (brief study-w6sanitize.md)",
     "note": "row authored late at the w6-metrics refresh (brief names repo at 50aac59)"},
    {"wave": "wave6",
     "work": "film git segment v6 revision in scratch (chase-language replay, falling-opening ending, tokens gate removed, interval epilogue gate; lead integrates after owner review)",
     "author": "study-video-gitvisual-v6",
     "base": full("97e10a4"), "time_box_min": 480, "ceiling_lines": 0,
     "ceiling_text": "scratch only; repo read-only for the study (brief study-video-gitvisual-v6.md)",
     "note": "row authored late at the w6-metrics refresh (brief base: production segment at main 97e10a4)"},
    {"wave": "wave6",
     "work": "lead send-back fix on parcel-w6popups: two popup-card counts corrected (19 parcels; 20 escalation filings, 3 fixes), gitvisual7.mp4 re-rendered, briefs row restated in place",
     "author": "fixer-w6popups",
     "base": full("0708e2e"), "time_box_min": 120, "ceiling_lines": 0,
     "ceiling_text": "one fixer commit on wave6-popups; owned-files list in brief fix-w6popups.md is the bound",
     "note": "row authored late at the w6-metrics refresh (brief fix-w6popups.md)"},
    {"wave": "wave6", "work": W_METRICS6, "author": "parcel-w6metrics",
     "base": "cdc40aec9b11eeab61ab3c6cc9940b5dbbac4a67", "time_box_min": 480, "ceiling_lines": 0,
     "ceiling_text": "no line ceiling stated in brief w6-metrics.md; owned-files list is the bound (docs/metrics appends only)"},
]
write_jsonl(HERE / "new-briefs.jsonl", briefs_new, spaced=True)
print(f"escalations new=0 briefs new={len(briefs_new)}")
for agent in sorted(A):
    print(f"SRC {agent}: {A[agent][4]}")
# frozen briefs base resolution check (report-only)
bad = []
for r in brief_rows:
    try:
        full(r["base"])
    except AssertionError:
        bad.append((r["author"], r["base"]))
print("frozen briefs bases that do not resolve:", bad)
