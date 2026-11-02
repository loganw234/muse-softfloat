"""Extract the REAL branch/merge history of muse-softfloat to history.json.

Ground truth = git only (log/branch/merge-base/rev-list reads).
Axis order = global commit rank from `git log --all --topo-order --reverse`
(parents before children). Nothing is invented: every branch lane in the
renderer is one real merge's second-parent chain, forked at its real
merge-base and merged at its real merge commit.

Run:  $MSF_PYTHON extract_history.py     (MSF_PYTHON = workspace .venv python)
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent / "muse-softfloat"
SEP = "\x1f"


def git(*args: str) -> str:
    r = subprocess.run(["git", "-C", str(REPO), "--no-pager", *args],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout.strip()


def main() -> int:
    raw = git("log", "--all", "--topo-order", "--reverse",
              f"--format=%H{SEP}%h{SEP}%P{SEP}%cI{SEP}%D{SEP}%s")
    commits = []
    for rank, line in enumerate(raw.splitlines()):
        h, short, parents, cdate, deco, subj = line.split(SEP, 5)
        commits.append({
            "rank": rank, "hash": h, "short": short,
            "parents": parents.split() if parents else [],
            "date": cdate, "decorations": deco.strip(),
            "subject": subj, "is_merge": len(parents.split()) > 1,
        })
    # Axis order: committer-date order (ties by topo rank). Verified below to
    # keep every parent before its children on this repo (0 violations), so
    # the replay is both chronological and parentage-true.
    commits.sort(key=lambda c: (c["date"], c["rank"]))
    for i, c in enumerate(commits):
        c["rank"] = i
    by_hash = {c["hash"]: c for c in commits}
    bad = [(c["short"], p[:7]) for c in commits for p in c["parents"]
           if by_hash[p]["rank"] > c["rank"]]
    assert not bad, f"date order breaks parentage: {bad}"

    branches = []
    for line in git("branch", f"--format=%(refname:short){SEP}%(objectname)").splitlines():
        name, tip = line.split(SEP, 1)
        branches.append({"name": name, "tip": tip,
                         "tip_short": by_hash[tip]["short"] if tip in by_hash else tip[:7]})

    main_fp = git("log", "--first-parent", "--reverse", "main", "--format=%H").splitlines()
    main_set = set(main_fp)
    for c in commits:
        c["on_main_first_parent"] = c["hash"] in main_set

    def attribute(second_parent: str) -> str:
        for b in branches:
            if b["tip"] == second_parent:
                return b["name"]
        # nearest branch tip that has second_parent as ancestor
        best, best_d = "", 10 ** 9
        for b in branches:
            if b["name"] == "main":
                continue
            cnt = git("rev-list", "--count", f"{second_parent}..{b['tip']}")
            anc = subprocess.run(["git", "-C", str(REPO), "merge-base", "--is-ancestor",
                                  second_parent, b["tip"]], capture_output=True)
            if anc.returncode == 0 and int(cnt) < best_d:
                best, best_d = b["name"], int(cnt)
        return best or "(unattributed)"

    merges = []
    for c in commits:
        if not c["is_merge"]:
            continue
        p1, p2 = c["parents"][0], c["parents"][1]
        base = git("merge-base", p1, p2)
        chain = git("rev-list", "--reverse", "--topo-order", f"{p1}..{p2}").splitlines()
        merges.append({
            "hash": c["hash"], "short": c["short"], "date": c["date"],
            "subject": c["subject"], "rank": c["rank"],
            "first_parent": p1, "second_parent": p2,
            "second_parent_short": by_hash[p2]["short"] if p2 in by_hash else p2[:7],
            "merge_base": base,
            "merge_base_short": by_hash[base]["short"] if base in by_hash else base[:7],
            "merge_base_rank": by_hash[base]["rank"] if base in by_hash else None,
            "target": "main" if c["on_main_first_parent"] else "(branch)",
            "target_branch": next((b for b in ("w1-f32", "w1-f64") if f"into {b}" in c["subject"]), ""),
            "branch": attribute(p2) if c["on_main_first_parent"] else f"lead-fix -> {next((b for b in ('w1-f32', 'w1-f64') if f'into {b}' in c['subject']), '?')}",
            "exclusive_commits": chain,
            "exclusive_ranks": [by_hash[h]["rank"] for h in chain if h in by_hash],
        })
    merges.sort(key=lambda m: m["rank"])

    # commits belonging to exactly one merge's exclusive chain (lane members)
    lane_of: dict[str, str] = {}
    for m in merges:
        for h in m["exclusive_commits"]:
            lane_of.setdefault(h, m["short"])
    for c in commits:
        c["lane_merge"] = lane_of.get(c["hash"], "")

    head = git("rev-parse", "main")
    data = {
        "repo": "muse-softfloat",
        "extracted_from": "git -C muse-softfloat log --all --topo-order --reverse (+ branch / merge-base / rev-list reads)",
        "axis": "rank = committer-date order, ties by topo order; asserted parent-before-child for all 141 commits (0 violations). Rank spacing is uniform per commit, NOT proportional to elapsed wall-clock.",
        "head_main": head, "head_short": by_hash[head]["short"],
        "commit_count_all": len(commits),
        "main_first_parent_count": len(main_fp),
        "merge_count": len(merges),
        "merges_into_main": sum(1 for m in merges if m["target"] == "main"),
        "branch_count": len(branches),
        "date_first": commits[0]["date"], "date_last": commits[-1]["date"],
        "branches": branches, "commits": commits, "merges": merges,
        "gate_anchors": {
            "gate1_kissfft_merge": next((m["short"] for m in merges if "KissFFT" in m["subject"]), None),
            "gate2_metrics_merge": next((m["short"] for m in merges if "metrics refresh" in m["subject"]), None),
        },
        "node_events": NODE_EVENTS,
        "legend": LEGEND,
    }
    out = HERE / "history.json"
    out.write_text(json.dumps(data, indent=1), encoding="utf-8")
    print(f"commits={len(commits)} main_fp={len(main_fp)} merges={len(merges)} "
          f"into_main={data['merges_into_main']} branches={len(branches)}")
    print(f"span {data['date_first']} .. {data['date_last']}  head={data['head_short']}")
    print(f"gate anchors: {data['gate_anchors']}")
    for m in merges:
        print(f"  rank {m['rank']:3d} {m['short']} base={m['merge_base_short']}(r{m['merge_base_rank']}) "
              f"chain={len(m['exclusive_commits']):2d} branch={m['branch']:16s} target={m['target']}  {m['subject'][:62]}")
    print(f"wrote {out} ({out.stat().st_size} bytes)")
    return 0


LEGEND = [
    {"system": "lead / main", "meaning": "the lead's main line; only READY work merges here"},
    {"system": "parcels", "meaning": "boxed work parcels on their own branches/worktrees"},
    {"system": "verifiers", "meaning": "independent disconfirm-only checks; NOT READY = sendback"},
    {"system": "plants", "meaning": "planted defects grading the verifiers (caught / missed)"},
    {"system": "gates", "meaning": "smoke / standard / board gates a merge must pass"},
    {"system": "studies", "meaning": "read-only feasibility studies in scratch, before parcels"},
    {"system": "escalations", "meaning": "a parcel stops and asks the lead to rule (fence working)"},
]

NODE_EVENTS = [
    {
        "id": "parcel", "system": "parcels", "title": "PARCEL",
        "lines": ["parcel-f32: 173 binary32 instantiations",
                  "owns src/msf32.c only - shared kernels stay lead-owned"],
            "source": "muse-softfloat/docs/RECORD.md Wave 1 entry (lines 323-332)",
    },
    {
        "id": "escalation", "system": "escalations", "title": "ESCALATION",
        "lines": ["parcel-f32 escalates: pack tininess is wrong (Clause 7.5)",
                  "Berkeley disagreed; every self-consistent gate had passed",
                  "ruled for the parcel - lead fixes 53acb1a / b37fb12"],
        "source": "RECORD.md Wave 1 (lines 334-347); docs/metrics/escalations.jsonl wave1 parcel-f32 2026-10-26T22:11:37-07:00 -> answered 22:14:00",
    },
    {
        "id": "verifier", "system": "verifiers", "title": "VERIFIER - SENDBACK",
        "lines": ["verifier-w5twiddledoc: NOT READY",
                  "printed SHA-256 is 56 hex chars - truncated, invalid",
                  "measured 64-char value is what the demo tooling enforces"],
        "source": "ledger/verifier-w5twiddledoc.md (blocking findings); fix landed as commit a41f026 on wave5-twiddledoc",
    },
    {
        "id": "plants", "system": "plants", "title": "PLANTS GRADED",
        "lines": ["Wave 1: 9 of 10 planted defects caught",
                  "the miss: weakened generator boundary, filed benign",
                  "detection without the byte-identity norm"],
        "source": "RECORD.md Wave 1 (lines 348-363); docs/metrics/plants.jsonl wave1 verifier-w1f32 plant 5 grade=missed",
    },
    {
        "id": "gates", "system": "gates", "title": "GATES",
        "lines": ["smoke 52,168 vectors - standard adds 1,117,504",
                  "9/9 negative controls refused",
                  "board: 2,767 sampled vectors, host == RP2040 hash"],
        "source": "RECORD.md Wave 1 (lines 364-374; whole-run SHA-256 4d7c2a28... identical host/board, board ID e66440a2cb6f5c2b)",
    },
    {
        "id": "study", "system": "studies", "title": "STUDY",
        "lines": ["feasibility first, read-only, in scratch",
                  "two study visuals wait ahead - as gates"],
        "source": "scratch/study-kissfft-visual/report.md + scratch/study-tokens-visual/report.md (both FEASIBLE WITH WORK); Wave 0 surveys S1-S4 in RECORD.md lines 13, 64-67",
    },
    {
        "id": "lead_merge", "system": "lead / main", "title": "LEAD MERGE",
        "lines": ["only READY work rejoins the main line",
                  "2843792 - Merged Wave 1 binary32 parcel (READY 26c76aa)"],
        "source": "git -C muse-softfloat log: merge 2843792 (2026-10-27 05:17:07 -0700), parents 52a6715 + 26c76aa (w1-f32 tip)",
    },
]


if __name__ == "__main__":
    sys.exit(main())
