#!/usr/bin/env python3
"""Extract per-agent metrics from Muse session transcripts.

    python tools/extract_session_metrics.py --session-dir DIR [--wave wave0] [--out-dir DIR]
             [--author-commit AGENT=SHA ...] [--verdict AGENT=A,B,READY,true ...]
        Reads DIR/session.jsonl (the lead) and DIR/subagent/*/session.jsonl,
        and writes usage.jsonl + passes.jsonl in the input shape of the kit's
        round_metrics.py, plus a human summary on stdout. Author commits and
        verifier verdicts are not in transcripts; they are supplied explicitly
        from the ledger via the annotation flags, and the run refuses author
        or verifier passes left unannotated rather than inventing them.
    python tools/extract_session_metrics.py --selftest
        Builds synthetic transcripts in a temp directory and checks sums,
        distinct tool-call counting, reminder-session exclusion, and refusals.

What is counted, and from where (measured on this project's transcripts):
- Tokens: only payload.event.kind == "model_completed" records carry a
  provider usage dict (input_tokens, output_tokens, cached_tokens,
  cache_write_tokens, cache_read_tokens, reasoning_tokens). Other records
  echo token numbers (goal attribution etc.) and are NOT counted. An exact
  duplicate model_completed (same session file, timestamp, model, usage and
  duration) is counted once. usage.jsonl carries output/input and the
  provider's cached_tokens verbatim; cache read/write sums are printed in
  the human summary but not merged into that field.
- Tool uses: distinct call ids in assistant_tool_calls_committed events.
- Messages: one per model_completed event.
- Start/end: first/last recorded_at (microseconds since the Unix epoch) in
  the session file, converted to local ISO 8601 with offset.
- Agent label: the lead for the main file; for children, the "Role: X" in
  the first started prompt, else a searched label (verifier-wave0,
  restatement pre-checker, model-selection probe), else the session id.
- Sessions whose first prompt marks them as reminder observers are internal
  harness sessions, not dispatched work: excluded, and counted in the
  summary so the exclusion is visible rather than silent.

Exit 0 on success; 1 on a refusal, naming the file and reason; 2 on bad usage.
"""
import argparse
import collections
import hashlib
import json
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

USAGE_INT_FIELDS = ("input_tokens", "output_tokens", "cached_tokens",
                    "cache_write_tokens", "cache_read_tokens", "reasoning_tokens")

WORK_BY_AGENT = {
    "lead": "wave0-lead",
    "harness-smoke-test": "harness-probe",
    "escalation-test": "harness-probe",
    "main-check": "harness-probe",
    "spark-probe": "harness-probe",
    "recount-probe": "harness-probe",
    "verifier-phase0": "phase0-scaffold",
    "rechecker-phase0": "phase0-scaffold",
    "rechecker2-phase0": "phase0-scaffold",
    "verifier-wave0": "wave0-record",
    "prechecker-wave0": "wave0-record",
}
WORK_BY_PREFIX = (("reader-", "readthrough"), ("surveyor-", "survey"))


class Refused(Exception):
    pass


def work_for(agent, wave):
    if agent in WORK_BY_AGENT:
        return WORK_BY_AGENT[agent]
    for prefix, work in WORK_BY_PREFIX:
        if agent.startswith(prefix):
            return work
    return wave


def role_for(agent):
    if agent == "lead":
        return "author"
    if agent.startswith(("verifier", "rechecker")):
        return "verifier"
    return "surveyor"


def iso_local(micros):
    return datetime.fromtimestamp(micros / 1_000_000, tz=timezone.utc).astimezone().isoformat(timespec="seconds")


def parse_until(text):
    if text is None:
        return None
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        raise Refused(f"--until is not an ISO 8601 timestamp: {text!r}")
    if dt.tzinfo is None:
        raise Refused("--until needs a numeric offset, e.g. 2026-10-26T11:22:00-07:00")
    return round(dt.timestamp() * 1_000_000)


def first_strings(obj, out, limit=40):
    if len(out) >= limit:
        return
    if isinstance(obj, str):
        out.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            first_strings(v, out, limit)
    elif isinstance(obj, list):
        for v in obj:
            first_strings(v, out, limit)


def read_records(path):
    records = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as e:
            raise Refused(f"{path.name} line {lineno}: unparseable JSON ({e.msg})")
    return records


def extract_session(path, is_main, wave, until_micros=None):
    records = read_records(path)
    stamps = []
    tool_ids = set()
    usage_by_model = collections.defaultdict(lambda: collections.Counter())
    messages_by_model = collections.Counter()
    seen_completions = set()
    prompt_texts = []
    for rec in records:
        if not isinstance(rec, dict):
            continue
        ts = rec.get("recorded_at")
        if until_micros is not None and isinstance(ts, int) and ts > until_micros:
            continue
        if isinstance(ts, int):
            stamps.append(ts)
        payload = rec.get("payload")
        if not isinstance(payload, dict):
            continue
        ev = payload.get("event")
        if not isinstance(ev, dict):
            continue
        kind = ev.get("kind")
        if kind == "started" and isinstance(ev.get("prompt"), str):
            prompt_texts.append(ev["prompt"])
        elif kind == "assistant_tool_calls_committed":
            for call in ev.get("tool_calls") or []:
                cid = call.get("call_id") or call.get("id")
                if cid:
                    tool_ids.add(cid)
        elif kind == "model_completed":
            usage = ev.get("usage")
            model = ev.get("model")
            if not isinstance(usage, dict) or not isinstance(model, str):
                raise Refused(f"{path}: model_completed without usage dict/model string")
            key = (ts, model, ev.get("duration_ms")) + tuple(usage.get(f) for f in USAGE_INT_FIELDS)
            if key in seen_completions:
                continue
            seen_completions.add(key)
            for field in USAGE_INT_FIELDS:
                value = usage.get(field, 0)
                if not isinstance(value, int) or value < 0:
                    raise Refused(f"{path}: usage field {field} is not a non-negative int: {value!r}")
                usage_by_model[model][field] += value
            messages_by_model[model] += 1
    if not stamps or not usage_by_model:
        if until_micros is not None:
            return None
        raise Refused(f"{path}: no recorded_at stamps" if not stamps
                      else f"{path}: no model_completed usage records")

    def searched_label(text):
        low = text.lower()
        # Precedence matters: the pre-checker's own brief quotes the verifier
        # it is checking, so its label must win over "verifier-wave0".
        if "independent recount" in low or "recount-probe" in low:
            return "recount-probe"
        if "model-selection probe" in low:
            return "spark-probe"
        if "restatement pre-checker" in low or "pre-check wave 0" in low:
            return "prechecker-wave0"
        if "verifier-wave0" in low or "wave 0 record entry" in low:
            return "verifier-wave0"
        return None

    head = "\n".join(prompt_texts[:2])
    if is_main:
        agent, how = "lead", "main session file"
    else:
        m = re.search(r"Role:\s*([A-Za-z0-9_-]+)", head)
        label = searched_label(head)
        if m:
            agent, how = m.group(1), "Role: in first started prompt"
        elif label:
            agent, how = label, "searched label"
        else:
            # Workflow children open with a protocol prompt; search deeper text.
            deep = []
            for rec in records[:400]:
                first_strings(rec, deep)
            label = searched_label("\n".join(deep))
            if label:
                agent, how = label, "searched deep label"
            else:
                agent, how = path.parent.name, "session id (unlabelled)"
    internal = (not is_main) and "reminder observer" in head.lower()
    return {
        "agent": agent, "how": how, "internal": internal,
        "session": path.parent.name, "start": min(stamps), "end": max(stamps),
        "tool_uses": len(tool_ids), "usage_by_model": usage_by_model,
        "messages_by_model": messages_by_model,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def parse_annotations(author_commits, verdicts):
    commits, verdict_map = {}, {}
    for item in author_commits or []:
        agent, sep, sha = item.partition("=")
        if not sep or not agent or not re.fullmatch(r"[0-9a-f]{7,40}", sha):
            raise Refused(f"--author-commit wants AGENT=SHA (7-40 hex), got {item!r}")
        commits[agent] = sha
    for item in verdicts or []:
        agent, sep, rest = item.partition("=")
        parts = rest.split(",")
        ok = (sep and agent and len(parts) == 4 and parts[0].isdigit() and parts[1].isdigit()
              and parts[2] in ("READY", "NOT READY") and parts[3] in ("true", "false"))
        if not ok:
            raise Refused(f"--verdict wants AGENT=A,B,READY|NOT READY,true|false, got {item!r}")
        if parts[2] == "READY" and parts[3] == "true":
            raise Refused(f"--verdict for {agent}: a READY pass that sent the work back")
        verdict_map[agent] = {"a": int(parts[0]), "b": int(parts[1]),
                              "verdict": parts[2], "sent_back": parts[3] == "true"}
    return commits, verdict_map


def run(session_dir, wave, out_dir, author_commits=None, verdicts=None, until=None):
    session_dir = Path(session_dir)
    main_file = session_dir / "session.jsonl"
    if not main_file.is_file():
        raise Refused(f"no session.jsonl in {session_dir}")
    until_micros = parse_until(until)
    files = [(main_file, True)] + [(p, False) for p in sorted((session_dir / "subagent").glob("*/session.jsonl"))]
    sessions = [s for s in (extract_session(p, is_main, wave, until_micros) for p, is_main in files) if s]
    work = [s for s in sessions if not s["internal"]]
    internal = [s for s in sessions if s["internal"]]
    if not work:
        raise Refused("no non-internal sessions found")

    commits, verdict_map = parse_annotations(author_commits, verdicts)
    known = {s["agent"] for s in work}
    for agent in sorted(set(commits) | set(verdict_map)):
        if agent not in known:
            raise Refused(f"annotation names unknown agent {agent!r} (known: {sorted(known)})")

    usage_rows, pass_rows = [], []
    for s in work:
        for model in sorted(s["usage_by_model"]):
            u = s["usage_by_model"][model]
            usage_rows.append({
                "wave": wave, "agent": s["agent"], "model": model,
                "output_tokens": u["output_tokens"], "input_tokens": u["input_tokens"],
                "source": "log", "cached_tokens": u["cached_tokens"],
                "messages": s["messages_by_model"][model],
                "note": f"session {s['session']}; label via {s['how']}; reasoning_tokens={u['reasoning_tokens']}",
            })
        row = {
            "wave": wave, "agent": s["agent"], "role": role_for(s["agent"]),
            "work": work_for(s["agent"], wave), "pass": 1,
            "start": iso_local(s["start"]), "end": iso_local(s["end"]),
            "tool_uses": s["tool_uses"], "source": "transcript",
            "note": f"session {s['session']}; transcript sha256 {s['sha256'][:12]}",
        }
        if row["role"] in ("author", "fixer"):
            if s["agent"] not in commits:
                raise Refused(f"author pass for {s['agent']} needs --author-commit {s['agent']}=SHA")
            row["commit"] = commits[s["agent"]]
        if row["role"] in ("verifier", "integration"):
            if s["agent"] not in verdict_map:
                raise Refused(f"verifier pass for {s['agent']} needs --verdict {s['agent']}=A,B,VERDICT,SENT_BACK")
            row.update(verdict_map[s["agent"]])
        pass_rows.append(row)

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, rows in (("usage.jsonl", usage_rows), ("passes.jsonl", pass_rows)):
        with open(out_dir / name, "w", encoding="utf-8", newline="\n") as f:
            for row in rows:
                f.write(json.dumps(row, separators=(",", ":")) + "\n")

    def totals(rows):
        return (sum(r["output_tokens"] for r in rows), sum(r["input_tokens"] for r in rows),
                sum(r.get("cached_tokens", 0) for r in rows), sum(r.get("messages", 0) for r in rows))

    print(f"sessions: {len(work)} work, {len(internal)} internal reminder sessions excluded"
          + (f"; cutoff --until {until}" if until else ""))
    print(f"{'agent':<26} {'model':<24} {'min':>6} {'tools':>5} {'msgs':>4} {'out tok':>10} {'in tok':>12} {'cached':>10}")
    by_model = collections.defaultdict(list)
    for row in usage_rows:
        by_model[row["model"]].append(row)
    pass_by_agent = {r["agent"]: r for r in pass_rows}
    for row in sorted(usage_rows, key=lambda r: -r["output_tokens"]):
        s = next(x for x in work if x["agent"] == row["agent"])
        mins = (s["end"] - s["start"]) / 60_000_000
        print(f"{row['agent']:<26} {row['model']:<24} {mins:>6.1f} {pass_by_agent[row['agent']]['tool_uses']:>5} "
              f"{row['messages']:>4} {row['output_tokens']:>10,} {row['input_tokens']:>12,} {row['cached_tokens']:>10,}")
    for model in sorted(by_model):
        o, i, c, m = totals(by_model[model])
        print(f"TOTAL {model}: out={o:,} in={i:,} cached={c:,} messages={m}")
    o, i, c, m = totals(usage_rows)
    print(f"TOTAL all work sessions: out={o:,} in={i:,} cached={c:,} messages={m}, "
          f"tool_uses={sum(r['tool_uses'] for r in pass_rows)}")
    cache_rw = collections.Counter()
    for s in work:
        for u in s["usage_by_model"].values():
            cache_rw["cache_read_tokens"] += u["cache_read_tokens"]
            cache_rw["cache_write_tokens"] += u["cache_write_tokens"]
            cache_rw["reasoning_tokens"] += u["reasoning_tokens"]
    print("raw cache/reasoning sums (not merged into cached_tokens):", dict(cache_rw))
    print(f"wrote {out_dir / 'usage.jsonl'} ({len(usage_rows)} rows), {out_dir / 'passes.jsonl'} ({len(pass_rows)} rows)")
    return 0


def _rec(ts, kind, **kw):
    ev = {"kind": kind}
    ev.update(kw)
    return json.dumps({"recorded_at": ts, "payload": {"kind": "run", "event": ev}})


def selftest():
    checks = failed = 0

    def check(cond, what):
        nonlocal checks, failed
        checks += 1
        if not cond:
            failed += 1
            print("FAIL:", what)

    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "sess"
        (root / "subagent" / "c1").mkdir(parents=True)
        (root / "subagent" / "c2").mkdir(parents=True)
        (root / "subagent" / "c3").mkdir(parents=True)
        u = {"input_tokens": 100, "output_tokens": 7, "cached_tokens": 3,
             "cache_write_tokens": 1, "cache_read_tokens": 2, "reasoning_tokens": 4}
        main = [
            _rec(1_000_000, "started", prompt="Hello lead"),
            _rec(2_000_000, "model_completed", model="m-lead", duration_ms=10, usage=u),
            _rec(2_000_000, "model_completed", model="m-lead", duration_ms=10, usage=u),  # exact dup
            _rec(3_000_000, "assistant_tool_calls_committed",
                 tool_calls=[{"call_id": "a", "name": "x"}, {"call_id": "a", "name": "x"}, {"call_id": "b", "name": "y"}]),
        ]
        (root / "session.jsonl").write_text("\n".join(main) + "\n", encoding="utf-8")
        child = [
            _rec(1_500_000, "started", prompt="Role: verifier-x Objective: check"),
            _rec(2_500_000, "model_completed", model="m-spark", duration_ms=5,
                 usage={**u, "input_tokens": 50, "output_tokens": 3}),
        ]
        (root / "subagent" / "c1" / "session.jsonl").write_text("\n".join(child) + "\n", encoding="utf-8")
        reminder = [
            _rec(1_200_000, "started", prompt="You are a reminder observer for the main agent."),
            _rec(1_300_000, "model_completed", model="m-spark", duration_ms=5, usage=u),
        ]
        (root / "subagent" / "c2" / "session.jsonl").write_text("\n".join(reminder) + "\n", encoding="utf-8")
        precheck = [
            _rec(1_400_000, "started", prompt="You are a restatement pre-checker checking verifier-wave0 findings."),
            _rec(1_600_000, "model_completed", model="m-spark", duration_ms=5, usage=u),
        ]
        (root / "subagent" / "c3" / "session.jsonl").write_text("\n".join(precheck) + "\n", encoding="utf-8")

        out = Path(td) / "out"
        try:
            run(root, "waveT", out)
            check(False, "unannotated author/verifier passes refused")
        except Refused:
            check(True, "unannotated author/verifier passes refused")
        check(run(root, "waveT", out, author_commits=["lead=abc1234"],
                  verdicts=["verifier-x=0,1,NOT READY,true"]) == 0,
              "run succeeds on synthetic sessions with annotations")
        usage = [json.loads(x) for x in (out / "usage.jsonl").read_text().splitlines()]
        passes = [json.loads(x) for x in (out / "passes.jsonl").read_text().splitlines()]
        check(len(usage) == 3 and len(passes) == 3, "reminder session excluded (3 work rows)")
        pre = next(r for r in passes if r["agent"] == "prechecker-wave0")
        check(pre["role"] == "surveyor", "pre-checker label wins over verifier-wave0 in its own brief")
        lead = next(r for r in usage if r["agent"] == "lead")
        check(lead["output_tokens"] == 7 and lead["messages"] == 1, "duplicate model_completed counted once")
        check(next(r for r in passes if r["agent"] == "lead")["tool_uses"] == 2, "distinct tool call ids")
        ver = next(r for r in passes if r["agent"] == "verifier-x")
        check(ver["role"] == "verifier", "role from started prompt")
        try:
            run(Path(td) / "missing", "waveT", out)
            check(False, "missing session dir refused")
        except Refused:
            check(True, "missing session dir refused")
    print(f"extract_session_metrics selftest: {checks} checks, {failed} failed")
    return 1 if failed else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--session-dir", help="Muse session directory holding session.jsonl")
    ap.add_argument("--wave", default="wave0")
    ap.add_argument("--out-dir", default="docs/metrics")
    ap.add_argument("--author-commit", action="append", default=[],
                    help="AGENT=SHA for an author pass (repeatable; from the ledger)")
    ap.add_argument("--verdict", action="append", default=[],
                    help="AGENT=A,B,READY|NOT READY,true|false for a verifier pass (repeatable; from the ledger)")
    ap.add_argument("--until", help="ISO 8601 cutoff with offset; count only records at or before it, "
                                     "so a live session's numbers stay reproducible")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    try:
        if a.selftest:
            return selftest()
        if not a.session_dir:
            ap.error("--session-dir is required unless --selftest")
        return run(a.session_dir, a.wave, a.out_dir, a.author_commit, a.verdict, a.until)
    except Refused as e:
        print(f"extract_session_metrics: refused: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
