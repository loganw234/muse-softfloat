"""build_data.py - regenerate the site's JSON data from the repository.

Outputs (next to this file):
  data.json            metrics strip inputs: instantiation counts from
                       docs/COVERAGE.tsv, plant scores by wave from
                       docs/metrics/plants.jsonl, committed-vector
                       totals counted from tests/vectors/*.vec
  ops.json             op table for the UI, parsed from the generated
                       dispatch table tests/msf_dispatch.h (index order
                       matches the C table the WASM glue drives),
                       joined with docs/COVERAGE.tsv metadata
  vectors-sample.json  bundled sample of committed vector lines for
                       the "deal me a committed vector" mode and the
                       Node replay proof (replay.mjs)

Deterministic: sorted inputs, fixed sampling rule, LF output.
Run from anywhere: paths resolve relative to the repo root (parent of
this file's directory).
"""
import collections
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = Path(__file__).resolve().parent

KIND_WIDTH = {
    "F16": 16, "I16": 16, "U16": 16,
    "F32": 32, "I32": 32, "U32": 32,
    "F64": 64, "I64": 64, "U64": 64,
    "I8": 8, "U8": 8,
    # BOOL / CLASS / INT / SPECIAL / NONE compare at 64 (tests/runner.c
    # kind_width default arm).
}
RM_TOKENS = {"te": 0, "tz": 1, "tp": 2, "tn": 3, "ta": 4, "-": -1}


def kind_width(kind: str) -> int:
    return KIND_WIDTH.get(kind, 64)


def git_short() -> str:
    try:
        out = subprocess.run(
            ["git", "-c", f"safe.directory={ROOT}", "-C", str(ROOT),
             "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=15)
        return out.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def parse_dispatch() -> list[dict]:
    text = (ROOT / "tests" / "msf_dispatch.h").read_text(
        encoding="utf-8", errors="replace")
    i = text.find("static const msf_op_desc_t MSF_OPS[]")
    j = text.find("};", i)
    if i < 0 or j < 0:
        raise SystemExit("MSF_OPS table not found in tests/msf_dispatch.h")
    pat = re.compile(
        r'\{\s*"([^"]+)",\s*"([^"]+)",\s*(MSF_SIG_\w+),\s*(MSF_RK_\w+),'
        r'\s*\{\s*(MSF_AK_\w+),\s*(MSF_AK_\w+),\s*(MSF_AK_\w+)\s*\},'
        r'\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\w+),'
        r'\s*(\w+)\s*\}')
    ops = []
    for idx, m in enumerate(pat.finditer(text[i:j])):
        name, std, sig, retk, a0, a1, a2 = m.group(1, 2, 3, 4, 5, 6, 7)
        nargs, has_rm, has_flags, status, wave = (
            int(m.group(8)), int(m.group(9)), int(m.group(10)),
            int(m.group(11)), int(m.group(12)))
        call = m.group(13)
        pair_call = m.group(14)
        strip = lambda k: k.replace("MSF_AK_", "").replace("MSF_RK_", "")
        ops.append({
            "i": idx, "name": name, "std": std,
            "sig": sig.replace("MSF_SIG_", ""), "ret": strip(retk),
            "args": [strip(a) for a in (a0, a1, a2)][:nargs],
            "nargs": nargs, "rm": bool(has_rm), "flags": bool(has_flags),
            "status": status, "wave": wave,
            # call != "0": single-result ops the glue drives. call ==
            # "0" with pair_call != "0": Clause 9.5 augmented pairs
            # (head+tail, clause-fixed rounding) - the page's
            # single-result shape cannot hold two results, so they
            # stay out of the UI/replay with the exclusion printed.
            # Both "0": character conversions + flag-management ops,
            # not hex-drivable.
            "runnable": call != "0",
            "pair": call == "0" and pair_call != "0",
        })
    if not ops:
        raise SystemExit("no ops parsed from tests/msf_dispatch.h")
    return ops


def parse_coverage() -> tuple[dict, list[dict]]:
    rows = []
    for line in (ROOT / "docs" / "COVERAGE.tsv").read_text(
            encoding="utf-8", errors="replace").splitlines():
        if not line or line.startswith("#") or line.startswith("name\t"):
            continue
        f = line.split("\t")
        rows.append({
            "name": f[0], "std": f[1], "clause": f[2], "dest": f[3],
            "sources": f[4], "wave": f[7], "status": f[8],
            "authority": f[9], "tier": f[12],
        })
    return {r["name"]: r for r in rows}, rows


def vector_lines():
    """Yield (file_name, tokens) for every counted vector line."""
    for path in sorted((ROOT / "tests" / "vectors").glob("*.vec")):
        for raw in path.read_text(encoding="utf-8",
                                  errors="replace").splitlines():
            s = raw.strip()
            if s and not s.startswith("#"):
                yield path.name, s.split()


def main() -> int:
    ops = parse_dispatch()
    cov_by_name, cov_rows = parse_coverage()
    for op in ops:
        c = cov_by_name.get(op["name"], {})
        op["dest"] = c.get("dest", "")
        op["clause"] = c.get("clause", "")
        op["tier"] = c.get("tier", "")
        op["authority"] = c.get("authority", "")
        op["retw"] = kind_width(op["ret"])
        op["argw"] = [kind_width(a) for a in op["args"]]

    # --- vectors: totals + per-op buckets for the sample ---------------
    total_vectors = 0
    per_file = collections.Counter()
    by_op: dict[str, list[dict]] = collections.defaultdict(list)
    runnable = {op["name"]: op for op in ops if op["runnable"]}
    for fname, tok in vector_lines():
        total_vectors += 1
        per_file[fname] += 1
        op_name = tok[0]
        if op_name not in runnable or "~" in tok:
            continue  # internal.pack*, char ops, masked expectations
        if "->" not in tok:
            continue
        arrow = tok.index("->")
        op = runnable[op_name]
        args = tok[2:arrow]
        # Single-result lines only: exactly result, flags, prov after
        # the arrow. A two-result pair line (head, tail, flags, prov)
        # must never be misread as result=head, flags=tail.
        if len(args) != op["nargs"] or len(tok) != arrow + 4:
            continue
        by_op[op_name].append({
            "op": op_name, "rm": tok[1], "args": args,
            "result": tok[arrow + 1], "flags": tok[arrow + 2],
            "prov": tok[arrow + 3], "file": fname,
        })

    # Sample rule (deterministic): per op, first line + middle line.
    sample = []
    for op_name in sorted(by_op):
        lines = by_op[op_name]
        picks = {0, len(lines) // 2}
        for p in sorted(picks):
            sample.append(lines[p])
    sample_ops_covered = len({s["op"] for s in sample})

    # --- plants by wave --------------------------------------------------
    plants = [json.loads(l) for l in
              (ROOT / "docs" / "metrics" / "plants.jsonl").read_text(
                  encoding="utf-8").splitlines() if l.strip()]
    by_wave: dict[str, dict] = {}
    for p in plants:
        w = by_wave.setdefault(p["wave"], {"caught": 0, "total": 0})
        w["total"] += 1
        if p.get("grade") == "caught":
            w["caught"] += 1
    wave_order = ["wave1", "wave2", "wave3", "wave4", "wave5", "readme"]
    plant_rows = [{"wave": w, **by_wave[w]}
                  for w in wave_order if w in by_wave]
    plant_rows += [{"wave": w, **v} for w, v in sorted(by_wave.items())
                   if w not in wave_order]

    tier_counts = collections.Counter(r["tier"] for r in cov_rows)
    status_counts = collections.Counter(r["status"] for r in cov_rows)

    data = {
        "base": git_short(),
        "instantiations": {
            "total": len(cov_rows),
            "tier1": tier_counts.get("1", 0),
            "tier2": tier_counts.get("2", 0),
            "implemented": status_counts.get("implemented", 0),
            "source": "docs/COVERAGE.tsv",
        },
        "vectors": {
            "total": total_vectors,
            "files": dict(sorted(per_file.items())),
            "source": "tests/vectors/*.vec (counted lines)",
        },
        "plants": {
            "caught": sum(1 for p in plants if p.get("grade") == "caught"),
            "total": len(plants),
            "by_wave": plant_rows,
            "source": "docs/metrics/plants.jsonl",
        },
        "sample": {
            "vectors": len(sample),
            "ops_covered": sample_ops_covered,
            "ops_runnable": len(runnable),
            "ops_total": len(ops),
            "ops_pair_excluded": sum(1 for op in ops if op["pair"]),
            "ops_nonhex_excluded": sum(
                1 for op in ops if not op["runnable"] and not op["pair"]),
            "source": "tests/vectors/*.vec via site/build_data.py",
        },
    }

    ops_out = [{k: op[k] for k in (
        "i", "name", "std", "sig", "ret", "args", "nargs", "rm", "flags",
        "runnable", "pair", "dest", "clause", "tier", "authority",
        "retw", "argw")}
        for op in ops]

    def dump(name: str, obj) -> None:
        (SITE / name).write_text(
            json.dumps(obj, indent=1, sort_keys=False) + "\n",
            encoding="utf-8", newline="\n")

    dump("data.json", data)
    dump("ops.json", ops_out)
    dump("vectors-sample.json", sample)
    print(f"ops={len(ops)} runnable={len(runnable)} "
          f"coverage_rows={len(cov_rows)} vectors={total_vectors} "
          f"sample={len(sample)} sample_ops={sample_ops_covered} "
          f"plants={data['plants']['caught']}/{data['plants']['total']} "
          f"base={data['base']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
