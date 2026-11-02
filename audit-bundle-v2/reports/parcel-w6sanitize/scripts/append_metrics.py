import hashlib, json, os
path = r"C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w6-sanitize\docs\metrics\briefs.jsonl"
before = open(path, "rb").read()
assert before.endswith(b"\n"), "precondition: newline-terminated"
print(f"pre-existing CRLF in file: {before.count(chr(13).encode() + chr(10).encode())} (committed bytes, left intact)")
row = {
    "wave": "wave6",
    "work": "Wave 6 queue item 3: sanitize budget in tools/run.sh (fifth budget; MSF_SANITIZE=trap default on this host, full for Linux/CI; SKIP-BY-NAME when the sanitizer runtime is absent) with deliberate-UB canaries in tests/, additive Ubuntu sanitize CI job running full; trap run zero findings over unit + 411213 committed + 1117504 extras + 5505024 aug pool, standard verdicts byte-identical normalized",
    "author": "parcel-w6sanitize",
    "base": "537b08edce17112da8f84353abcb2c693f2a5e65",
    "time_box_min": 480,
    "ceiling_lines": 0,
    "ceiling_text": "no line ceiling stated in brief w6-sanitize.md; owned-files list is the bound (tools/run.sh, .github/workflows/ci.yml additive job, AGENTS.md budget list, tests/sanitize_canary_*.c, this row)",
}
line = (json.dumps(row, ensure_ascii=True) + "\n").encode("ascii")
assert b"\r" not in line
with open(path, "ab") as f:
    f.write(line)
after = open(path, "rb").read()
print(f"before {len(before)}B sha256={hashlib.sha256(before).hexdigest()}")
print(f"after  {len(after)}B appended={len(after)-len(before)} prefix_intact={after[:len(before)] == before}")
last = after[len(before):]
print("appended parses:", json.loads(last)["author"], "| CR in appended bytes:", b"\r" in last)
