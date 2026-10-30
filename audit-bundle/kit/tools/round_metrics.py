#!/usr/bin/env python3
"""The record's metric tables, made from the lead's JSONL files (METRICS.md).

    tools/round_metrics.py DIR [--wave W] [--repo REPO] [--out FILE]
        Reads the six files below from DIR and writes the tables as Markdown: the chain; time and tokens; time
        boxes and scope ceilings; plants; brief corrections; escalations. --wave keeps the rows of one wave; without
        it, every row counts. --repo is the project repository, where each piece of work's size is measured with
        git, from its brief's base to its author's last commit. A file that is absent leaves its tables out, and
        says so. Each table names the kit's version and the sha256 of every file it read.
    tools/round_metrics.py --selftest
        Makes the tables from fixtures, and checks that each malformed row below is refused.

The files, one JSON object a line. A field not listed is refused, so a misspelt field cannot drop a figure. Times
are ISO 8601 with an offset, or the ledger's own "2026-10-02 21:37:58 -0700"; a time without one is refused.

  usage.jsonl     the harness's or the API's usage, a row per agent or per pass, summed per agent:
                  wave, agent, model, output_tokens, input_tokens, source ("log", "api" or "transcribed");
                  optional cached_tokens, messages, note
  passes.jsonl    one row per pass of an agent, from its transcript:
                  wave, agent, role ("author", "verifier", "integration", "surveyor" or "fixer"), work, pass,
                  start, end, tool_uses, source ("transcript" or "transcribed");
                  an author's or fixer's pass also holds commit, the tip it reported;
                  a verifier's or the integration verifier's holds a and b, the counts of its findings in each
                  class, verdict ("READY" or "NOT READY") and sent_back (true or false);
                  optional note
  briefs.jsonl    one row per brief: wave, work, author, base, time_box_min, ceiling_lines; optional ceiling_text
                  (the brief's own words), note
  plants.jsonl    one row per plant, written at the reveal: wave, verifier, work, key_sha256, plant (its number in
                  the key), shape, grade ("caught" or "missed"), graded_by; optional checked_by, note
  corrections.jsonl  one row per "what this brief got wrong": wave, brief, by, at, text, accepted (true, false, or
                  null while the lead has not ruled); optional note
  escalations.jsonl  one row per escalation: wave, from, to, sent, means ("file" or "message"), test (true for the
                  test escalation at dispatch); optional answered, note

A row whose source is "transcribed" is marked in its table: it was copied from a harness's own counters, not read
from a log (METRICS.md, "Where each figure comes from").

Exit 0 when the tables are written; 1 when a file is refused, the line naming the file, its row and the reason; 2 on
bad usage; 3 if the tool itself failed.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import statistics
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

TIME = "time"
SHA256 = "sha256"
ANY_BOOL = "bool or null"
SPEC = {
    "usage.jsonl": ({"wave": str, "agent": str, "model": str, "output_tokens": int, "input_tokens": int,
                     "source": ("log", "api", "transcribed")},
                    {"cached_tokens": int, "messages": int, "note": str}),
    "passes.jsonl": ({"wave": str, "agent": str, "role": ("author", "verifier", "integration", "surveyor", "fixer"),
                      "work": str, "pass": int, "start": TIME, "end": TIME, "tool_uses": int,
                      "source": ("transcript", "transcribed")},
                     {"commit": str, "a": int, "b": int, "verdict": ("READY", "NOT READY"), "sent_back": bool,
                      "note": str}),
    "briefs.jsonl": ({"wave": str, "work": str, "author": str, "base": str, "time_box_min": int,
                      "ceiling_lines": int},
                     {"ceiling_text": str, "note": str}),
    "plants.jsonl": ({"wave": str, "verifier": str, "work": str, "key_sha256": SHA256, "plant": int, "shape": str,
                      "grade": ("caught", "missed"), "graded_by": str},
                     {"checked_by": str, "note": str}),
    "corrections.jsonl": ({"wave": str, "brief": str, "by": str, "at": TIME, "text": str, "accepted": ANY_BOOL},
                          {"note": str}),
    "escalations.jsonl": ({"wave": str, "from": str, "to": str, "sent": TIME, "means": ("file", "message"),
                           "test": bool},
                          {"answered": TIME, "note": str}),
}
CHECKING = ("verifier", "integration")
WRITING = ("author", "fixer")


class Refused(Exception):
    pass


def rmtree(path):
    """shutil.rmtree that also removes the read-only files git writes, which Windows will not delete as they are."""
    def retry(func, p, _exc):
        try:
            os.chmod(p, stat.S_IWRITE)
            func(p)
        except OSError:
            pass
    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=retry)
    else:
        shutil.rmtree(path, onerror=retry)


def parse_time(value):
    for fmt in (None, "%Y-%m-%d %H:%M:%S %z"):
        try:
            t = datetime.fromisoformat(value) if fmt is None else datetime.strptime(value, fmt)
        except (TypeError, ValueError):
            continue
        if t.tzinfo is not None:
            return t
    return None


def check_value(kind, value):
    if kind is TIME:
        return isinstance(value, str) and parse_time(value) is not None
    if kind is SHA256:
        return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None
    if kind is ANY_BOOL:
        return value is None or isinstance(value, bool)
    if isinstance(kind, tuple):
        return isinstance(value, str) and value in kind
    if kind is int:
        return isinstance(value, int) and not isinstance(value, bool) and value >= 0
    if kind is bool:
        return isinstance(value, bool)
    return isinstance(value, kind) and value.strip() != ""


def describe(kind):
    if isinstance(kind, tuple):
        return "one of " + ", ".join(kind)
    return {TIME: "a time with its offset", SHA256: "a sha256 in hex", ANY_BOOL: "true, false or null",
            int: "a whole number, 0 or more", bool: "true or false", str: "text"}[kind]


def read_rows(path):
    required, optional = SPEC[path.name]
    rows = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        where = "%s, row %d" % (path.name, n)
        try:
            row = json.loads(line)
        except json.JSONDecodeError as e:
            raise Refused("%s is not JSON: %s" % (where, e))
        if not isinstance(row, dict):
            raise Refused("%s is not an object" % where)
        unknown = sorted(set(row) - set(required) - set(optional))
        if unknown:
            raise Refused("%s: fields not in this file's list: %s" % (where, ", ".join(unknown)))
        missing = sorted(set(required) - set(row))
        if missing:
            raise Refused("%s: missing %s" % (where, ", ".join(missing)))
        for field, value in row.items():
            kind = required.get(field, optional.get(field))
            if not check_value(kind, value):
                raise Refused("%s: %s is %s, not %s" % (where, field, json.dumps(value), describe(kind)))
        if path.name == "passes.jsonl":
            check_pass(row, where)
        if path.name == "escalations.jsonl" and "answered" in row and \
                parse_time(row["answered"]) < parse_time(row["sent"]):
            raise Refused("%s: answered before it was sent" % where)
        row["_where"] = where
        rows.append(row)
    return rows


def check_pass(row, where):
    if parse_time(row["end"]) < parse_time(row["start"]):
        raise Refused("%s: the pass ends before it starts" % where)
    if row["pass"] < 1:
        raise Refused("%s: passes are numbered from 1" % where)
    if row["role"] in CHECKING:
        missing = [f for f in ("a", "b", "verdict", "sent_back") if f not in row]
        if missing:
            raise Refused("%s: a %s's pass needs %s" % (where, row["role"], ", ".join(missing)))
        if row["sent_back"] and row["verdict"] == "READY":
            raise Refused("%s: a READY pass that sent the work back" % where)
    else:
        extra = [f for f in ("a", "b", "verdict", "sent_back") if f in row]
        if extra:
            raise Refused("%s: an %s's pass does not hold %s" % (where, row["role"], ", ".join(extra)))
    if row["role"] in WRITING and "commit" not in row:
        raise Refused("%s: an %s's pass needs the commit it reported" % (where, row["role"]))


def minutes(row):
    return (parse_time(row["end"]) - parse_time(row["start"])).total_seconds() / 60


def num(n):
    return "{:,}".format(int(round(n)))


def times(n):
    return {0: "no", 1: "once", 2: "twice"}.get(n, "%d times" % n)


def kit_version():
    manifest = Path(__file__).resolve().parent.parent / "MANIFEST.txt"
    if not manifest.is_file():
        return "kit version unknown: no MANIFEST.txt beside tools/"
    first = manifest.read_text(encoding="utf-8").splitlines()[0]
    return "%s (MANIFEST.txt sha256 %s)" % (first, hashlib.sha256(manifest.read_bytes()).hexdigest()[:12])


def provenance(files, digests):
    read = ["%s sha256 %s" % (f, digests[f][:12]) for f in files if f in digests]
    return "_%s; read %s._" % (KIT, ", ".join(read))


def changed_lines(repo, base, commit):
    r = subprocess.run(["git", "diff", "--numstat", base, commit], cwd=repo, capture_output=True)
    if r.returncode:
        return None, "git diff failed: %s" % r.stderr.decode("utf-8", "replace").strip()[:120]
    total, binary = 0, 0
    for line in r.stdout.decode("utf-8", "replace").splitlines():
        added, deleted = line.split("\t")[:2]
        if added == "-":
            binary += 1
        else:
            total += int(added) + int(deleted)
    return total, (", %d binary file%s not counted" % (binary, "" if binary == 1 else "s")) if binary else ""


def chain(data, digests):
    briefs, passes, usage = data.get("briefs.jsonl", []), data["passes.jsonl"], data.get("usage.jsonl", [])
    models = {}
    for u in usage:
        models.setdefault(u["agent"], [])
        if u["model"] not in models[u["agent"]]:
            models[u["agent"]].append(u["model"])
    works = [b["work"] for b in briefs]
    works += [p["work"] for p in passes if p["work"] not in works and p["role"] in WRITING + CHECKING]
    works = list(dict.fromkeys(works))
    out = ["**The chain** (COMPUTED from the passes; (a), (b) per verifier pass, each as its report counts them):", "",
           provenance(["passes.jsonl", "briefs.jsonl", "usage.jsonl"], digests), "",
           "| work | author | verifier's passes | sent back |", "|---|---|---|---|"]
    for w in works:
        mine = sorted((p for p in passes if p["work"] == w), key=lambda p: (parse_time(p["start"]), p["pass"]))
        commits = [p["commit"][:7] for p in mine if p["role"] in WRITING]
        authors = list(dict.fromkeys(p["agent"] for p in mine if p["role"] in WRITING))
        who = ", then ".join("%s (%s)" % (a, "/".join(models.get(a, ["model not recorded"]))) for a in authors)
        checks = []
        for v in dict.fromkeys(p["agent"] for p in mine if p["role"] in CHECKING):
            vp = sorted((p for p in mine if p["agent"] == v and p["role"] in CHECKING), key=lambda p: p["pass"])
            checks.append("%s %s" % (v, "; ".join("%d, %d" % (p["a"], p["b"]) for p in vp)))
        back = sum(1 for p in mine if p["role"] in CHECKING and p["sent_back"])
        mark = " (transcribed)" if any(p["source"] == "transcribed" for p in mine) else ""
        out.append("| %s%s%s | %s | %s | %s |" % (w, " (%s)" % ", ".join(commits) if commits else "", mark,
                                                 who or "none recorded", "; ".join(checks) or "none recorded",
                                                 times(back)))
    return out


def time_and_tokens(data, digests):
    passes, usage = data.get("passes.jsonl", []), data.get("usage.jsonl", [])
    agents = list(dict.fromkeys([p["agent"] for p in passes] + [u["agent"] for u in usage]))
    out = ["**Time and tokens** (MEASURED from the usage and the transcripts, rows marked transcribed READ from a "
           "harness's counters; minutes from each pass's start to its end):", "",
           provenance(["passes.jsonl", "usage.jsonl"], digests), "",
           "| agent | model | passes | minutes, first pass; all | tool uses | output tokens | input tokens | cached |",
           "|---|---|---|---|---|---|---|---|"]
    sums = {}
    for a in agents:
        ps = sorted((p for p in passes if p["agent"] == a), key=lambda p: parse_time(p["start"]))
        us = [u for u in usage if u["agent"] == a]
        model = "/".join(dict.fromkeys(u["model"] for u in us)) or "not recorded"
        mins = [minutes(p) for p in ps]
        span = "" if not mins else num(mins[0]) if len(mins) == 1 else "%s; %s" % (num(mins[0]), num(sum(mins)))
        tools = sum(p["tool_uses"] for p in ps)
        o, i = sum(u["output_tokens"] for u in us), sum(u["input_tokens"] for u in us)
        cached = [u["cached_tokens"] for u in us if "cached_tokens" in u]
        mark = " (transcribed)" if any(r["source"] == "transcribed" for r in ps + us) else ""
        out.append("| %s%s | %s | %d | %s | %s | %s | %s | %s |" % (
            a, mark, model, len(ps), span or "none recorded", num(tools) if ps else "",
            num(o) if us else "not recorded", num(i) if us else "not recorded", num(sum(cached)) if cached else ""))
        s = sums.setdefault(model if us else None, [0, 0, 0, 0, 0])
        s[0] += 1
        s[1] += o
        s[2] += i
        s[3] += tools
        s[4] += sum(mins)
    out.append("")
    for model, (n, o, i, tools, mins) in sums.items():
        agents_ = "%d agent%s" % (n, "" if n == 1 else "s")
        if model is None:
            out.append("- **The %s with no usage recorded** (COMPUTED from the rows): %s tool uses, about %s minutes; "
                       "their tokens are not in usage.jsonl." % (agents_, num(tools), num(mins)))
        else:
            out.append("- **Sums for %s** (COMPUTED from the rows): %s, %s output tokens, %s input tokens, %s tool "
                       "uses, about %s minutes." % (model, agents_, num(o), num(i), num(tools), num(mins)))
    return out


def boxes(data, digests, repo):
    briefs, passes = data["briefs.jsonl"], data.get("passes.jsonl", [])
    out = ["**Time boxes and scope ceilings** (COMPUTED: the first pass of each brief's author against its box; "
           "each work's changed lines from its base to its author's last commit, by git):", "",
           provenance(["briefs.jsonl", "passes.jsonl"], digests), "",
           "| work | author | first pass, minutes | time box | changed lines | ceiling | size against ceiling |",
           "|---|---|---|---|---|---|---|"]
    for b in briefs:
        ps = sorted((p for p in passes if p["work"] == b["work"] and p["agent"] == b["author"]
                     and p["role"] in WRITING), key=lambda p: parse_time(p["start"]))
        first = num(minutes(ps[0])) if ps else "no pass recorded"
        if not ps:
            size, why = None, "no commit recorded"
        elif repo is None:
            size, why = None, "not measured: no --repo"
        else:
            size, why = changed_lines(repo, b["base"], ps[-1]["commit"])
        ceiling = "%s%s" % (num(b["ceiling_lines"]), ' ("%s")' % b["ceiling_text"] if "ceiling_text" in b else "")
        ratio = "%.1f times" % (size / b["ceiling_lines"]) if size is not None and b["ceiling_lines"] else ""
        out.append("| %s | %s | %s | %d | %s | %s | %s |" % (
            b["work"], b["author"], first, b["time_box_min"],
            (num(size) + why) if size is not None else why, ceiling, ratio))
    return out


def plants(data, digests):
    rows = data["plants.jsonl"]
    out = ["**Plants** (the lead's grading of each report against its key, by reading; what a rate measures is the "
           "lead's choice of plants and the verifiers' detection, together):", "",
           provenance(["plants.jsonl"], digests), "",
           "| verifier | work | key sha256 | plants | caught | missed | checked by |", "|---|---|---|---|---|---|---|"]
    groups = {}
    for r in rows:
        groups.setdefault((r["verifier"], r["work"], r["key_sha256"]), []).append(r)
    total = [0, 0]
    for (v, w, k), rs in groups.items():
        numbers = [r["plant"] for r in rs]
        if len(set(numbers)) != len(numbers):
            raise Refused("plants.jsonl: plant %s of key %s is graded twice" % (
                sorted(n for n in numbers if numbers.count(n) > 1)[0], k[:12]))
        c = sum(1 for r in rs if r["grade"] == "caught")
        total[0] += c
        total[1] += len(rs) - c
        checked = ", ".join(dict.fromkeys(r["checked_by"] for r in rs if "checked_by" in r)) or "not yet"
        out.append("| %s | %s | %s | %d | %d | %d | %s |" % (v, w, k[:12], len(rs), c, len(rs) - c, checked))
    out += ["", "- **In all** (COMPUTED): %d of %d plants caught." % (total[0], sum(total))]
    return out


def corrections(data, digests):
    rows = data["corrections.jsonl"]
    out = ["**Brief corrections** (each report's \"what this brief got wrong\", with the lead's ruling):", "",
           provenance(["corrections.jsonl"], digests), "",
           "| brief | corrections | accepted | rejected | not yet ruled |", "|---|---|---|---|---|"]
    for brief in dict.fromkeys(r["brief"] for r in rows):
        rs = [r for r in rows if r["brief"] == brief]
        out.append("| %s | %d | %d | %d | %d |" % (brief, len(rs), sum(1 for r in rs if r["accepted"] is True),
                                                  sum(1 for r in rs if r["accepted"] is False),
                                                  sum(1 for r in rs if r["accepted"] is None)))
    return out


def escalations(data, digests):
    rows = sorted(data["escalations.jsonl"], key=lambda r: parse_time(r["sent"]))
    out = ["**Escalations** (COMPUTED from the ledger's stamps: minutes from sent to answered):", "",
           provenance(["escalations.jsonl"], digests), "",
           "| sent | from | to | means | minutes to the answer |", "|---|---|---|---|---|"]
    waits = []
    for r in rows:
        if "answered" in r:
            m = (parse_time(r["answered"]) - parse_time(r["sent"])).total_seconds() / 60
            if not r["test"]:
                waits.append(m)
            wait = num(m)
        else:
            wait = "unanswered"
        out.append("| %s | %s%s | %s | %s | %s |" % (r["sent"], r["from"], " (the test)" if r["test"] else "",
                                                   r["to"], r["means"], wait))
    real = [r for r in rows if not r["test"]]
    tests = len(rows) - len(real)
    line = "- **In all** (COMPUTED): %d escalation%s, not counting %d test%s" % (
        len(real), "" if len(real) == 1 else "s", tests, "" if tests == 1 else "s")
    if waits:
        line += "; answered in a median of %s minutes, the longest %s" % (num(statistics.median(waits)),
                                                                          num(max(waits)))
    unanswered = sum(1 for r in real if "answered" not in r)
    out += ["", line + ("; %d unanswered." % unanswered if unanswered else ".")]
    return out


def make(directory, wave, repo):
    directory = Path(directory)
    if not directory.is_dir():
        raise Refused("%s is not a directory" % directory)
    data, digests = {}, {}
    for name in SPEC:
        p = directory / name
        if p.is_file():
            digests[name] = hashlib.sha256(p.read_bytes()).hexdigest()
            rows = read_rows(p)
            data[name] = [r for r in rows if wave is None or r["wave"] == wave]
    if not data:
        raise Refused("%s holds none of %s" % (directory, ", ".join(SPEC)))
    if repo is not None:
        if not os.path.isdir(repo):
            raise Refused("%s is not a directory" % repo)
        r = subprocess.run(["git", "rev-parse", "--git-dir"], cwd=repo, capture_output=True)
        if r.returncode:
            said = r.stderr.decode("utf-8", "replace").strip().splitlines() or ["exit %d" % r.returncode]
            raise Refused("git will not read %s as a repository: %s" % (repo, said[0]))
    out = ["### Metrics%s" % (" for wave %s" % wave if wave else ", every wave"), ""]
    made = [("the chain", ["passes.jsonl"], lambda: chain(data, digests)),
            ("time and tokens", ["passes.jsonl", "usage.jsonl"], lambda: time_and_tokens(data, digests)),
            ("time boxes and scope ceilings", ["briefs.jsonl"], lambda: boxes(data, digests, repo)),
            ("plants", ["plants.jsonl"], lambda: plants(data, digests)),
            ("brief corrections", ["corrections.jsonl"], lambda: corrections(data, digests)),
            ("escalations", ["escalations.jsonl"], lambda: escalations(data, digests))]
    for title, needs, table in made:
        if any(n in data for n in needs) if title == "time and tokens" else all(n in data for n in needs):
            out += table() + [""]
        else:
            out += ["_Not made: %s needs %s, absent from %s._" % (title, " or ".join(needs), directory.name), ""]
    return "\n".join(out)


def selftest():
    me = [sys.executable, "-I", str(Path(__file__).resolve())]
    t = Path(tempfile.mkdtemp(prefix="round-metrics-selftest-"))
    checks = failed = 0

    def check(cond, what):
        nonlocal checks, failed
        checks += 1
        if not cond:
            failed += 1
            print("FAIL: " + what)

    def run(*args):
        r = subprocess.run(me + [str(a) for a in args], capture_output=True)
        return r.returncode, r.stdout.decode("utf-8", "replace"), r.stderr.decode("utf-8", "replace")

    def write(d, name, rows):
        d.mkdir(exist_ok=True)
        (d / name).write_text("".join((r if isinstance(r, str) else json.dumps(r)) + "\n" for r in rows),
                              encoding="utf-8")

    try:
        repo = t / "repo"
        repo.mkdir()
        env_git = ["git", "-c", "user.name=selftest", "-c", "user.email=selftest@example.invalid",
                   "-c", "commit.gpgsign=false", "-c", "init.defaultBranch=main"]
        subprocess.run(env_git + ["init", "-q"], cwd=repo, check=True)
        (repo / "a.txt").write_text("one\n")
        subprocess.run(env_git + ["add", "-A"], cwd=repo, check=True)
        subprocess.run(env_git + ["commit", "-q", "-m", "base"], cwd=repo, check=True)
        base = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True).stdout.strip()
        (repo / "a.txt").write_text("one\ntwo\nthree\n")
        (repo / "b.txt").write_text("x\n" * 10)
        subprocess.run(env_git + ["add", "-A"], cwd=repo, check=True)
        subprocess.run(env_git + ["commit", "-q", "-m", "work"], cwd=repo, check=True)
        tip = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True).stdout.strip()

        d = t / "record"
        write(d, "usage.jsonl", [
            {"wave": "1", "agent": "P1", "model": "model-A", "output_tokens": 1000, "input_tokens": 50000,
             "cached_tokens": 40000, "source": "log"},
            {"wave": "1", "agent": "P1", "model": "model-A", "output_tokens": 234, "input_tokens": 1000,
             "source": "log"},
            {"wave": "1", "agent": "V1", "model": "model-B", "output_tokens": 500, "input_tokens": 9000,
             "source": "transcribed"}])
        write(d, "passes.jsonl", [
            {"wave": "1", "agent": "P1", "role": "author", "work": "P1", "pass": 1, "start": "2026-10-27 09:00:00 -0700",
             "end": "2026-10-27 10:30:00 -0700", "tool_uses": 100, "commit": tip, "source": "transcript"},
            {"wave": "1", "agent": "V1", "role": "verifier", "work": "P1", "pass": 1,
             "start": "2026-10-27T10:40:00-07:00", "end": "2026-10-27T11:10:00-07:00", "tool_uses": 30, "a": 0,
             "b": 2, "verdict": "NOT READY", "sent_back": True, "source": "transcript"},
            {"wave": "1", "agent": "P1", "role": "author", "work": "P1", "pass": 2, "start": "2026-10-27 11:20:00 -0700",
             "end": "2026-10-27 11:40:00 -0700", "tool_uses": 20, "commit": tip, "source": "transcript"},
            {"wave": "1", "agent": "V1", "role": "verifier", "work": "P1", "pass": 2,
             "start": "2026-10-27T11:45:00-07:00", "end": "2026-10-27T11:55:00-07:00", "tool_uses": 10, "a": 0,
             "b": 0, "verdict": "READY", "sent_back": False, "source": "transcript"},
            {"wave": "2", "agent": "P2", "role": "author", "work": "P2", "pass": 1, "start": "2026-10-28 09:00:00 -0700",
             "end": "2026-10-28 09:30:00 -0700", "tool_uses": 5, "commit": tip, "source": "transcribed"}])
        write(d, "briefs.jsonl", [
            {"wave": "1", "work": "P1", "author": "P1", "base": base, "time_box_min": 120, "ceiling_lines": 10,
             "ceiling_text": "about ten lines"}])
        key = "ab" * 32
        write(d, "plants.jsonl", [
            {"wave": "1", "verifier": "V1", "work": "P1", "key_sha256": key, "plant": 1, "shape": "a figure",
             "grade": "caught", "graded_by": "lead", "checked_by": "VI"},
            {"wave": "1", "verifier": "V1", "work": "P1", "key_sha256": key, "plant": 2, "shape": "a rule",
             "grade": "missed", "graded_by": "lead"}])
        write(d, "corrections.jsonl", [
            {"wave": "1", "brief": "P1", "by": "P1", "at": "2026-10-27 10:00:00 -0700", "text": "a path", "accepted": True},
            {"wave": "1", "brief": "P1", "by": "V1", "at": "2026-10-27 11:00:00 -0700", "text": "x", "accepted": None}])
        write(d, "escalations.jsonl", [
            {"wave": "1", "from": "P1", "to": "lead", "sent": "2026-10-27 09:01:00 -0700",
             "answered": "2026-10-27 09:02:00 -0700", "means": "file", "test": True},
            {"wave": "1", "from": "P1", "to": "lead", "sent": "2026-10-27 09:30:00 -0700",
             "answered": "2026-10-27 09:42:00 -0700", "means": "file", "test": False},
            {"wave": "1", "from": "V1", "to": "lead", "sent": "2026-10-27 10:50:00 -0700", "means": "message",
             "test": False}])
        rc, so, se = run(d, "--wave", "1", "--repo", repo)
        check(rc == 0, "the fixtures make tables: exit %d: %s" % (rc, se.strip()))
        want = [
            "| P1 (%s, %s) | P1 (model-A) | V1 0, 2; 0, 0 | once |" % (tip[:7], tip[:7]),
            "| P1 | model-A | 2 | 90; 110 | 120 | 1,234 | 51,000 | 40,000 |",
            "| V1 (transcribed) | model-B | 2 | 30; 40 | 40 | 500 | 9,000 |  |",
            "| P1 | P1 | 90 | 120 | 12 | 10 (\"about ten lines\") | 1.2 times |",
            "| V1 | P1 | %s | 2 | 1 | 1 | VI |" % key[:12],
            "- **In all** (COMPUTED): 1 of 2 plants caught.",
            "| P1 | 2 | 1 | 0 | 1 |",
            "| 2026-10-27 09:01:00 -0700 | P1 (the test) | lead | file | 1 |",
            "1 unanswered.",
            "2 escalations, not counting 1 test; answered in a median of 12 minutes, the longest 12",
            "softfloat-bootstrap-kit" if (Path(__file__).resolve().parent.parent / "MANIFEST.txt").is_file()
            else "kit version unknown",
            "passes.jsonl sha256 ",
        ]
        for w in want:
            check(w in so, "the tables hold %r" % w)
        check("P2" not in so, "--wave 1 leaves out wave 2's rows")
        check("- **Sums for model-A** (COMPUTED from the rows): 1 agent, 1,234 output tokens, 51,000 input tokens, "
              "120 tool uses, about 110 minutes." in so, "the sums per model")
        rc, so, _ = run(d)
        check(rc == 0 and "| P2 (%s) (transcribed) |" % tip[:7] in so and "not measured: no --repo" in so,
              "every wave, and no --repo")
        check("- **The 1 agent with no usage recorded** (COMPUTED from the rows): 5 tool uses, about 30 minutes; "
              "their tokens are not in usage.jsonl." in so, "an agent with no usage is not summed as zero tokens")

        def refused(reason, name, row):
            bad = t / ("bad-%d" % checks)
            write(bad, name, [row])
            rc, so, se = run(bad)
            check(rc == 1 and se.startswith("round_metrics.py: refused: ") and reason in se,
                  "want exit 1 naming %r, got exit %d: %s" % (reason, rc, se.strip()))

        u = {"wave": "1", "agent": "P1", "model": "m", "output_tokens": 1, "input_tokens": 1, "source": "log"}
        refused("fields not in this file's list: ouput_tokens", "usage.jsonl", dict(u, ouput_tokens=5))
        refused("missing input_tokens", "usage.jsonl", {k: v for k, v in u.items() if k != "input_tokens"})
        refused("output_tokens is -1", "usage.jsonl", dict(u, output_tokens=-1))
        refused("output_tokens is true", "usage.jsonl", dict(u, output_tokens=True))
        refused("source is \"guess\"", "usage.jsonl", dict(u, source="guess"))
        p = {"wave": "1", "agent": "P1", "role": "author", "work": "P1", "pass": 1,
             "start": "2026-10-27 09:00:00 -0700", "end": "2026-10-27 10:00:00 -0700", "tool_uses": 1,
             "commit": tip, "source": "transcript"}
        refused("start is \"2026-10-27 09:00:00\", not a time with its offset", "passes.jsonl",
                dict(p, start="2026-10-27 09:00:00"))
        refused("ends before it starts", "passes.jsonl", dict(p, end="2026-10-27 08:00:00 -0700"))
        refused("needs the commit", "passes.jsonl", {k: v for k, v in p.items() if k != "commit"})
        refused("does not hold a, b", "passes.jsonl", dict(p, a=0, b=1))
        refused("needs a, b, verdict, sent_back", "passes.jsonl", dict(p, role="verifier"))
        refused("a READY pass that sent the work back", "passes.jsonl",
                dict(p, role="verifier", a=0, b=0, verdict="READY", sent_back=True))
        refused("not JSON", "briefs.jsonl", "not json")
        e = {"wave": "1", "from": "P1", "to": "lead", "sent": "2026-10-27 09:30:00 -0700", "means": "file",
             "test": False}
        refused("answered before it was sent", "escalations.jsonl", dict(e, answered="2026-10-27 09:00:00 -0700"))
        twice = t / "twice"
        row = {"wave": "1", "verifier": "V1", "work": "P1", "key_sha256": key, "plant": 1, "shape": "s",
               "grade": "caught", "graded_by": "lead"}
        write(twice, "plants.jsonl", [row, dict(row, grade="missed")])
        rc, _, se = run(twice)
        check(rc == 1 and "graded twice" in se, "a plant graded twice is refused: %s" % se.strip())
        rc, _, se = run(t / "absent")
        check(rc == 1 and "is not a directory" in se, "an absent directory is refused")
        refused("is not an object", "usage.jsonl", "[1, 2]")
        refused("passes are numbered from 1", "passes.jsonl", dict(p, **{"pass": 0}))
        refused('key_sha256 is "abc", not a sha256 in hex', "plants.jsonl", dict(row, key_sha256="abc"))
        refused('accepted is "maybe", not true, false or null', "corrections.jsonl",
                {"wave": "1", "brief": "P1", "by": "P1", "at": "2026-10-27 10:00:00 -0700", "text": "x",
                 "accepted": "maybe"})
        refused('sent_back is "yes", not true or false', "passes.jsonl",
                dict(p, role="verifier", a=0, b=0, verdict="READY", sent_back="yes"))
        refused('agent is "", not text', "usage.jsonl", dict(u, agent=""))
        refused('agent is " ", not text', "usage.jsonl", dict(u, agent=" "))
        nothing = t / "nothing"
        nothing.mkdir()
        rc, _, se = run(nothing)
        check(rc == 1 and "holds none of" in se, "a directory with none of the files is refused: %s" % se.strip())
        plain = t / "plain"
        plain.mkdir()
        rc, _, se = run(d, "--repo", plain)
        check(rc == 1 and "as a repository: " in se, "a --repo that is no repository is refused, with git's reason: %s"
              % se.strip())
        rc, _, se = run(d, "--repo", plain / "absent")
        check(rc == 1 and "is not a directory" in se, "a --repo that is no directory is refused: %s" % se.strip())
        rc, _, _ = run()
        check(rc == 2, "no arguments is bad usage, exit 2 (got %d)" % rc)
    finally:
        rmtree(t)
    print("round_metrics.py selftest: %d checks, %d failed" % (checks, failed))
    return 0 if failed == 0 else 1


KIT = kit_version()


def main(argv=None):
    ap = argparse.ArgumentParser(prog="round_metrics.py", description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("dir", nargs="?")
    ap.add_argument("--wave")
    ap.add_argument("--repo")
    ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.dir:
        ap.print_usage(sys.stderr)
        return 2
    try:
        text = make(a.dir, a.wave, a.repo)
        if a.out:
            Path(a.out).write_text(text, encoding="utf-8")
            print("wrote %s" % a.out)
        else:
            sys.stdout.write(text)
        return 0
    except Refused as e:
        print("round_metrics.py: refused: %s" % e, file=sys.stderr)
        return 1
    except Exception as e:
        print("round_metrics.py: the tool failed: %s: %s" % (type(e).__name__, e), file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
