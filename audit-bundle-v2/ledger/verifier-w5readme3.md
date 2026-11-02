# verifier-w5readme3 (NOT READY)

Copy `worktrees/verify5-readme3` at `5986b5d` (parent `e9c57fb`).
Brief `ledger/briefs/verify-w5readme3.md` obeyed; parcel branch, other
worktrees, keys, `scratch/lead/`, `scratch/parcel-w5readme3/`,
`ledger/lead.md` never consulted; nothing with `cft` in its name
opened/searched/listed. Copy unmodified (clean at close); all builds,
serves, and replays ran outside it. Scripts (Git Bash, `MSF_PYTHON`
pinned to workspace `.venv`) and full detail:
`scratch/verifier-w5readme3/report.md` (first line NOT READY).

Re-derived (own commands): COVERAGE 849 = 783 + 66/66, 0 unconfirmed;
dispatch 849 = 822 runnable + 9 pairs + 18 nonhex; committed vectors
411,213 = runner PASS; standard 917,504 + 200,000 = 1,117,504 PASS;
aug pool 5,505,024 PASS; attr 273 = has_rm 273; plants 109/115 by-wave
(9/10, 10/10, 5/5, 25/25, 41/45, 9/10, 10/10); metrics 93/94/20;
briefs 31 rows, frozen 30-row prefix byte-identical, new row base
`e9c57fb` real; drift 4/4; unit PASS; Zig archive sha `b5663f69…`
re-verified.

Findings (8): README headline 859 (re-derived 849); README benefit line
inverts RECORD's study-model labelling (RECORD.md:971-975); data.json
pair-excluded 0 (re-derived 9) and plants 115/115 (re-derived 109/115,
own rows sum 109/115) — not producible by committed build_data.py;
sample idx 1258 exp2(0) expects …0001 vs committed .vec …0000 (wasm
correct, exactly 1); numbers table renders pair-excluded 0 (exclusion
printed in index.html, site/README, repo README but not the table);
replay-log 0-mismatch claim irreproducible (actual: 1 mismatch, exit 1);
wasm byte-identity holds only same-directory (code sections identical,
DWARF paths differ; committed 770,233 B vs rebuild 768,126 B).

Not done: full smoke control battery / scans, one-time exhaustives
(quoted), board, pixel QA / non-Edge, live Pages post-merge.
