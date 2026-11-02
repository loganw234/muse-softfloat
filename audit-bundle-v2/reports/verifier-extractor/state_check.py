import glob
import json
import re
import sys
from datetime import datetime, timezone

sys.path.insert(0, "C:/Users/logan/source/repos/Muse-Softfloat/muse-softfloat/tools")
from extract_session_metrics import extract_session

CUT = "2026-10-26T11:31:34-07:00"
BASE = "C:/Users/logan/.local/share/muse/sessions/2026/10/26/01a17907-4147-7333-a565-56071da9d971"

from pathlib import Path
files = [(Path(BASE + "/session.jsonl"), True)]
files += [(Path(p), False) for p in sorted(glob.glob(BASE + "/subagent/*/session.jsonl"))]

work, internal, dropped = [], [], []
for p, is_main in files:
    s = extract_session(p, is_main, "wave0", None)  # no cutoff: full picture
    sid = p.parent.name if not is_main else "MAIN"
    if s is None:
        dropped.append(sid)
    elif s["internal"]:
        internal.append((sid, s["agent"]))
    else:
        work.append((sid, s["agent"]))

print("work:", len(work))
for sid, a in work:
    print("  W", sid[:8], a)
print("internal:", len(internal))
for sid, a in internal:
    print("  I", sid[:8], a)
print("dropped-none:", len(dropped), dropped)

# now with cutoff: which sessions change state?
print("--- with cutoff ---")
work2, internal2, dropped2 = [], [], []
for p, is_main in files:
    from extract_session_metrics import parse_until
    s = extract_session(p, is_main, "wave0", parse_until(CUT))
    sid = p.parent.name if not is_main else "MAIN"
    if s is None:
        dropped2.append(sid)
    elif s["internal"]:
        internal2.append((sid, s["agent"]))
    else:
        work2.append((sid, s["agent"]))
print("work:", len(work2), "internal:", len(internal2), "dropped:", dropped2)
