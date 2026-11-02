# verifier-w6sanitize (Wave 6 sanitize verifier)

Full report: `scratch/verifier-w6sanitize/report.md`. Copy
`worktrees/verify6-sanitize` left untouched (status clean); all runs in
`scratch/verifier-w6sanitize/dup`.

## Verdict: REJECT

- `tools/run.sh:44` refusal inverted (`= sanitize` for `!=`):
  explicit trap/full/bogus + sanitize all REFUSED rc=2;
  `MSF_SANITIZE=full` + standard silently runs standard rc=0
  (merge-gate re-flavour leak). Full-flavour path unreachable.
- Default sanitize SKIPs in 0 s (`ld: cannot find -lubsan`); trap
  unlinkable on this host — claimed 44-56 s trap PASS not reproduced.
- `ub` canary dead as invoked (argc=1, `INT_MAX-100+1` never
  overflows); would fail its own gate under live UBSan.
- CI sanitize job runs `MSF_SANITIZE=trap` (`ci.yml:112`) while name,
  comment, and artifact paths claim full; exits 2 as written; SKIP
  would be green (exit 0, no PASS assertion).
- AGENTS.md sanitize cost/flavour text stale (no 44-56 s PASS here;
  full REFUSED not SKIP; CI runs trap).
- PASS: standard in dup (411213 + 1117504, aug PASS, all controls
  refused); seams clean (probe/ARM plain; SANFLAGS only in
  canary/host/aug builds); runner.c strncpy fix present.
