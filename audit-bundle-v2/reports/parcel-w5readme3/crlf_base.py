from pathlib import Path
b = Path(__file__).with_name("out").joinpath("briefs-at-head.jsonl").read_bytes()
print(f"HEAD briefs.jsonl: {len(b)} bytes, CRLF={b.count(bytes([13, 10]))}")
cur = (Path(__file__).resolve().parents[2] / "worktrees" / "w5-readme3"
       / "docs" / "metrics" / "briefs.jsonl").read_bytes()
print(f"worktree briefs.jsonl: {len(cur)} bytes, CRLF={cur.count(bytes([13, 10]))}")
print("appended tail CRLF:", cur[len(b):].count(bytes([13, 10])))
print("prefix identical:", cur[:len(b)] == b)
