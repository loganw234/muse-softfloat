"""Build process_graph.json for gitvisual v7: the real agent-episode
graph behind the merged git topology, with FULL accounting.

Sources (repo copy only, read-only):
  history.json                      (spine: 141 commits to a73e97d)
  muse-softfloat/docs/metrics/passes.jsonl  (94 rows)
  muse-softfloat/docs/metrics/briefs.jsonl  (37 rows)
  muse-softfloat/docs/metrics/plants.jsonl  (150 rows, 30 verifiers x 5)

Accounting contract (brief study-video-gitvisual-v7.md):
  - every passes row maps to exactly one episode (94 rows -> 94
    episodes; the `lead` wave0 author row IS the spine episode, so
    93 lane episodes + 1 spine episode - the on-screen /93 counter
    counts lane episodes and says so);
  - every plants verifier attaches to a verifier episode or is
    named in `unmapped_plants_verifiers`;
  - every briefs row is joined to an episode or named in
    `unmapped_briefs` with a reason. Nothing is silently dropped.

Rank anchoring: episode start/end timestamps map to fractional
spine rank by linear interpolation between bracketing commit
committer-dates (history ranks are committer-date order). If the
row's `commit` is in history, `commit_rank` is that exact rank and
(for author/fixer rows) the draw end is the joining merge rank.

Joins:
  - author/fixer -> git merge: passes commit is the merge's
    second parent or one of its exclusive commits.
  - verifier -> merge: via the author episode with identical
    `work` (exact string), else by plants-work token overlap -
    recorded in `merge_join_how`.
  - brief -> episode: (author, work) exact, else unique author.
  - plants -> verifier episode: verifier name == passes agent.

Slots: git lane slots replicate gitvisual6.assign_lanes exactly
(asserted against the same algorithm here); episode slots are
greedy-packed around them on the draw spans. Max concurrency is
computed on the same spans.

Run: $MSF_PYTHON prep_process_graph.py  -> process_graph.json
"""
import bisect, json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
WS = HERE.parent.parent
REPO = WS / "muse-softfloat"
MET = REPO / "docs" / "metrics"

HIST = json.loads((HERE / "history.json").read_text(encoding="utf-8"))
COMMITS, MERGES = HIST["commits"], HIST["merges"]
BY_HASH = {c["hash"]: c for c in COMMITS}
LAST = HIST["commit_count_all"] - 1


def _ts(s):
    return datetime.fromisoformat(s).timestamp()


CT = [_ts(c["date"]) for c in COMMITS]
assert all(CT[i] <= CT[i + 1] for i in range(len(CT) - 1)), "commit dates not monotone in rank"


def rank_of_time(tstr):
    """Fractional spine rank of a timestamp. Inside the commit range:
    linear interpolation between bracketing committer-dates. Before
    the first commit (the Wave 0 morning: episodes ran 09:24-10:50
    toward the 10:50 root commit) extrapolate at the first
    inter-commit rate instead of clamping - clamping would fabricate
    ~14-way overlap at rank 0 out of sequential batches. Negative
    ranks are honest wall-clock positions before the root commit."""
    t = _ts(tstr)
    if t < CT[0]:
        return (t - CT[0]) / (CT[1] - CT[0]), "extrapolated_before_root"
    if t > CT[-1]:
        return LAST + (t - CT[-1]) / (CT[-1] - CT[-2]), "extrapolated_after_head"
    i = bisect.bisect_right(CT, t) - 1
    if i >= LAST:
        return float(LAST), "interp"
    if CT[i + 1] <= CT[i]:
        return float(i), "interp"
    return i + (t - CT[i]) / (CT[i + 1] - CT[i]), "interp"


def git_slots_r2():
    """gitvisual6.assign_lanes, verbatim algorithm (r2 geometry)."""
    lanes, taken = {}, []
    cycle, order = [-1, 1, -2, 2, -3, 3, -1, 2, -2, 1], [-1, 1, -2, 2, -3, 3, -4, 4]
    for k, m in enumerate([m for m in MERGES if m["target"] == "main"]):
        first = cycle[k % len(cycle)]
        for slot in [first] + [s for s in order if s != first]:
            if not any(s == slot and not (m["rank"] < a - 1 or m["merge_base_rank"] > b + 1)
                       for s, a, b in taken):
                lanes[m["short"]] = slot
                taken.append((slot, m["merge_base_rank"], m["rank"])); break
    return lanes


GIT_SLOTS = git_slots_r2()
MERGE_MAIN = {m["short"]: m for m in MERGES if m["target"] == "main"}

# merge lookup by any exclusive/second-parent commit hash
MERGE_OF_COMMIT = {}
for m in MERGES:
    if m["target"] != "main":
        continue
    MERGE_OF_COMMIT[m["second_parent"]] = m
    for h in m["exclusive_commits"]:
        MERGE_OF_COMMIT[h] = m

passes = [json.loads(l) for l in (MET / "passes.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
briefs = [json.loads(l) for l in (MET / "briefs.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
plants = [json.loads(l) for l in (MET / "plants.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]

# ---- episodes: one per passes row, in start order ----
for _i, _p in enumerate(passes):
    _p["_row"] = _i
passes_sorted = sorted(passes, key=lambda p: (p["start"], p["agent"]))
episodes = []
for i, p in enumerate(passes_sorted):
    sr, s_how = rank_of_time(p["start"])
    er, e_how = rank_of_time(p["end"])
    cm = p.get("commit")
    c_rank = BY_HASH[cm]["rank"] if cm in BY_HASH else None
    role = "lead" if p["agent"] == "lead" else p["role"]
    ep = {
        "id": f"E{i + 1:03d}", "passes_index": p["_row"],
        "agent": p["agent"], "role": role, "passes_role": p["role"],
        "wave": p["wave"], "work": p["work"], "pass": p["pass"],
        "start": p["start"], "end": p["end"],
        "start_rank": round(sr, 3), "end_rank": round(er, 3),
        "start_anchor": s_how, "end_anchor": e_how,
        "commit": cm, "commit_rank": c_rank,
        "commit_exact": c_rank is not None,
        "kind": "spine" if role == "lead" else "lane",
        "merge_short": None, "merge_rank": None, "merge_branch": None,
        "merge_join_how": None, "brief_base": None, "brief_base_rank": None,
        "plants": [], "plants_caught": 0, "plants_missed": 0,
    }
    if cm and cm in MERGE_OF_COMMIT:
        m = MERGE_OF_COMMIT[cm]
        ep.update(merge_short=m["short"], merge_rank=m["rank"],
                  merge_branch=m["branch"],
                  merge_join_how="second_parent" if cm == m["second_parent"] else "exclusive_commit")
    episodes.append(ep)

# verifier -> merge via identical work of an author/fixer episode
by_work_auth = {}
for ep in episodes:
    if ep["passes_role"] in ("author", "fixer") and ep["merge_short"]:
        by_work_auth.setdefault(ep["work"], ep)
for ep in episodes:
    if ep["role"] == "verifier" and not ep["merge_short"]:
        host = by_work_auth.get(ep["work"])
        if host:
            ep.update(merge_short=host["merge_short"], merge_rank=host["merge_rank"],
                      merge_branch=host["merge_branch"], merge_join_how="same_work_author")

# briefs -> episodes
unmapped_briefs = []
for b in briefs:
    cands = [e for e in episodes if e["agent"] == b["author"] and e["work"] == b["work"]]
    how = "author+work"
    if len(cands) > 1:
        # a brief commissions pass 1; later fixer rounds share agent+work
        first = [e for e in cands if e["passes_role"] == "author" and e["pass"] == 1]
        if len(first) == 1:
            cands, how = first, "author+work+pass1"
    if not cands:
        cands = [e for e in episodes if e["agent"] == b["author"]]
        how = "author_unique"
    base_rank = BY_HASH[b["base"]]["rank"] if b["base"] in BY_HASH else None
    if len(cands) == 1:
        cands[0]["brief_base"] = b["base"]
        cands[0]["brief_base_rank"] = base_rank
        cands[0]["brief_join_how"] = how
    else:
        reason = ("no passes episode (outside passes.jsonl scope)"
                  if not cands else f"ambiguous: {len(cands)} episodes for author")
        if base_rank is None:
            reason += "; base commit not in frozen history (post-a73e97d)"
        unmapped_briefs.append({"wave": b["wave"], "author": b["author"],
                                 "work": b["work"], "base": b["base"],
                                 "base_in_history": base_rank is not None,
                                 "reason": reason})

# plants -> verifier episodes
plants_by_verifier = defaultdict(list)
for pl in plants:
    plants_by_verifier[pl["verifier"]].append(pl)
unmapped_plants = []
ver_eps = {e["agent"]: e for e in episodes if e["role"] == "verifier"}
for verifier, rows in sorted(plants_by_verifier.items()):
    ticks = [{"plant": r["plant"], "grade": r["grade"]} for r in sorted(rows, key=lambda r: r["plant"])]
    if verifier in ver_eps:
        ep = ver_eps[verifier]
        ep["plants"] = ticks
        ep["plants_caught"] = sum(1 for t in ticks if t["grade"] == "caught")
        ep["plants_missed"] = sum(1 for t in ticks if t["grade"] != "caught")
    else:
        unmapped_plants.append({
            "verifier": verifier, "wave": rows[0]["wave"], "work": rows[0]["work"],
            "plants": len(rows),
            "caught": sum(1 for r in rows if r["grade"] == "caught"),
            "missed": sum(1 for r in rows if r["grade"] != "caught"),
            "reason": "no passes.jsonl verifier episode (passes frozen at Wave 5 / pre-close snapshot)"})

# ---- draw spans (geometry truth; data ranks above stay untouched) ----
for ep in episodes:
    if ep["kind"] == "spine":
        ep.update(draw_start=0.0, draw_end=float(LAST), slot=0, endpoint="spine")
        continue
    ds, de = ep["start_rank"], ep["end_rank"]
    notes = []
    if ep["role"] == "author" and ep["merge_short"]:
        m = MERGE_MAIN[ep["merge_short"]]
        ds, de = float(m["merge_base_rank"]), float(m["rank"])
        ep.update(git_lane=ep["merge_short"], endpoint="merge",
                  slot=GIT_SLOTS[ep["merge_short"]])
        notes.append("draw span = git lane (merge-base..merge); marble rides git geometry")
    elif ep["role"] == "fixer" and ep["merge_short"]:
        de = float(ep["merge_rank"])
        ep.update(endpoint="merge")
        notes.append("red return lane ends at its merge rank")
    elif ep["role"] == "author":
        ep.update(endpoint="merge")  # returns to spine at end (no git merge found)
        notes.append("AUTHOR WITHOUT GIT MERGE JOIN - returns at end_rank")
    elif ep["role"] == "verifier":
        # Data over brief wording: most merge-joined verifiers end
        # minutes before their merge commit (verdict gates merge),
        # but the Wave 1 pair ran 05:23-05:50 AFTER the 05:17/05:18
        # merges (post-merge planted verification; grades recorded
        # at rank 21). No clamping: the lane ends at its true
        # timestamp rank; the exceptions are named in accounting.
        ep.update(endpoint="verdict")
        if ep["merge_rank"] is not None and de > ep["merge_rank"]:
            notes.append("verdict AFTER merge rank (post-merge verification, by timestamps)")
    else:  # surveyor
        ep.update(endpoint="doc")
    if ep["role"] == "fixer":
        ep["endpoint"] = "merge"
    ep["draw_start"] = round(ds, 3)  # may be < 0: pre-root work (see rank_of_time)
    ep["draw_end"] = round(min(float(LAST), max(de, ds)), 3)
    ep["draw_notes"] = notes

# ---- slot packing for non-git lane episodes ----
occupied = []  # (slot, lo, hi)
for short, slot in GIT_SLOTS.items():
    m = MERGE_MAIN[short]
    occupied.append((slot, float(m["merge_base_rank"]) - 0.5, float(m["rank"]) + 0.5))
slot_order = [s for k in range(1, 13) for s in (-k, k)]
lane_eps = [e for e in episodes if e["kind"] == "lane" and "slot" not in e]
# verifiers prefer the side of their author's git slot, one step out
for ep in sorted(lane_eps, key=lambda e: (e["draw_start"], e["id"])):
    lo, hi = ep["draw_start"] - 0.25, ep["draw_end"] + 0.25
    pref = []
    if ep["role"] == "verifier" and ep["merge_short"] in GIT_SLOTS:
        gs = GIT_SLOTS[ep["merge_short"]]
        step = 1 if gs > 0 else -1
        pref = [gs + step, gs + 2 * step, gs - step]
    for slot in pref + [s for s in slot_order if s not in pref]:
        if all(not (s == slot and not (hi < a or lo > b)) for s, a, b in occupied):
            ep["slot"] = slot
            occupied.append((slot, lo, hi))
            break
    else:
        raise AssertionError(f"no slot for {ep['id']}")

# ---- concurrency on draw spans (lane episodes only) ----
events = []
for ep in episodes:
    if ep["kind"] == "lane":
        events.append((ep["draw_start"], 1, ep["id"]))
        events.append((ep["draw_end"], -1, ep["id"]))
events.sort(key=lambda x: (x[0], -x[1]))
cur, best, best_at, best_set, active = 0, 0, None, [], set()
for rank, delta, eid in events:
    if delta == 1:
        active.add(eid); cur += 1
        if cur > best:
            best, best_at, best_set = cur, rank, sorted(active)
    else:
        active.discard(eid); cur -= 1

# active-count profile sampled every 0.25 ranks over the film axis
def active_at(r):
    return sum(1 for e in episodes if e["kind"] == "lane"
               and e["draw_start"] <= r <= e["draw_end"])


profile = [active_at(r / 4.0) for r in range(0, LAST * 4 + 1)]
profile_sorted = sorted(profile)
busiest_film_rank = max(range(len(profile)), key=lambda i: profile[i]) / 4.0

slots_used = sorted({e["slot"] for e in episodes if e["kind"] == "lane"})
accounting = {
    "passes_rows": len(passes),
    "episodes": len(episodes),
    "lane_episodes": sum(1 for e in episodes if e["kind"] == "lane"),
    "spine_episodes": sum(1 for e in episodes if e["kind"] == "spine"),
    "by_role": dict(Counter(e["role"] for e in episodes)),
    "by_passes_role": dict(Counter(e["passes_role"] for e in episodes)),
    "commit_exact": sum(1 for e in episodes if e["commit_exact"]),
    "commit_absent_or_outside": sum(1 for e in episodes if not e["commit_exact"]),
    "merge_joined": sum(1 for e in episodes if e["merge_short"]),
    "brief_joined": sum(1 for e in episodes if e.get("brief_base")),
    "briefs_rows": len(briefs), "briefs_unmapped": len(unmapped_briefs),
    "plants_rows": len(plants),
    "plants_verifiers": len(plants_by_verifier),
    "plants_verifiers_mapped": len(plants_by_verifier) - len(unmapped_plants),
    "plants_rows_mapped": sum(len(e["plants"]) for e in episodes),
    "plants_rows_unmapped": sum(u["plants"] for u in unmapped_plants),
    "verifier_episodes_with_plants": sum(1 for e in episodes if e["role"] == "verifier" and e["plants"]),
    "verifier_episodes_without_plants": sorted(
        e["agent"] for e in episodes if e["role"] == "verifier" and not e["plants"]),
    "authors_without_merge_join": sorted(
        e["agent"] for e in episodes if e["role"] == "author" and not e["merge_short"]),
    "git_merges_into_main": len(MERGE_MAIN),
    "git_merges_owned_by_author_episode": sorted({e["merge_short"] for e in episodes
                                                   if e["role"] == "author" and e["merge_short"]}),
    "git_merges_lead_only_no_episode": sorted(
        s for s in MERGE_MAIN
        if s not in {e["merge_short"] for e in episodes if e["merge_short"]}),
    "sub_rank_draw_spans": sum(1 for e in episodes if e["kind"] == "lane"
                               and e["draw_end"] - e["draw_start"] < 1.0),
    "max_concurrent_lane_episodes": best,
    "max_concurrency_at_rank": best_at,
    "max_concurrency_episodes": best_set,
    "slots_used": slots_used,
    "slot_range": [min(slots_used), max(slots_used)],
    "active_profile_median": profile_sorted[len(profile_sorted) // 2],
    "active_profile_p90": profile_sorted[int(0.9 * len(profile_sorted))],
    "busiest_film_rank_ge0": busiest_film_rank,
    "active_at_busiest_film_rank": active_at(busiest_film_rank),
    "verifiers_ending_after_merge": sorted(
        e["agent"] for e in episodes if e["role"] == "verifier"
        and e["merge_rank"] is not None and e["end_rank"] > e["merge_rank"]),
    "pre_root_episodes": sum(1 for e in episodes if e["draw_start"] < 0),
    "min_draw_start": min(e["draw_start"] for e in episodes if e["kind"] == "lane"),
}
assert accounting["passes_rows"] == accounting["episodes"] == 94
assert accounting["lane_episodes"] == 93 and accounting["spine_episodes"] == 1
assert accounting["plants_rows_mapped"] + accounting["plants_rows_unmapped"] == len(plants)
assert len({e["passes_index"] for e in episodes}) == 94

out = {
    "sources": {"history": "history.json (141 commits to a73e97d)",
                "passes": "muse-softfloat/docs/metrics/passes.jsonl",
                "briefs": "muse-softfloat/docs/metrics/briefs.jsonl",
                "plants": "muse-softfloat/docs/metrics/plants.jsonl"},
    "role_colors_deep": {"lead": "lead / main", "author": "parcels",
                         "verifier": "verifiers", "surveyor": "studies",
                         "fixer": "escalations"},
    "git_slots": GIT_SLOTS,
    "accounting": accounting,
    "unmapped_plants_verifiers": unmapped_plants,
    "unmapped_briefs": unmapped_briefs,
    "episodes": episodes,
}
(HERE / "process_graph.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps(accounting, indent=1))
print("unmapped plants verifiers:", [u["verifier"] for u in unmapped_plants])
print("unmapped briefs:", [(u["author"], u["wave"]) for u in unmapped_briefs])
print("-> process_graph.json")
