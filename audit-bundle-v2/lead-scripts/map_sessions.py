import json, pathlib, sys
base = pathlib.Path.home() / ".local/share/muse/sessions/2026/10/26"
for sid in ["18d430fa-c715-7776-8de8-5b60f11797de", "3dcbbf23-a4c0-7a0a-864a-8f730b0823a2",
            "41abe4fe-02c6-75f8-8ab1-4a474ba58c40", "8e119253-cde0-7254-8af1-445793ca5f3c",
            "b036aaa1-65b3-7ce0-87cb-fdf6bbec9158", "01a179ad-6c14-7af1-bf07-662141f70b3f",
            "8f86c39e-be05-7194-8369-e69ed098e14c"]:
    p = base / sid / "session.jsonl"
    if not p.exists():
        print(sid, "MISSING"); continue
    found = ""
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines()[:400]:
        if "You are " in line or "Role:" in line:
            i = max(line.find("You are "), line.find("Role:"))
            found = line[i:i+110].replace("\\n", " ")
            break
    print(sid[:8], "->", found[:110] if found else "(no marker in first 400 lines)")
