# audit-2026-10-31/artifacts

Small reproduction aids that back the findings in `../REPORT.md`. Nothing here is part of the project; nothing in the repository was modified by the audit.

| path | backs | what |
|---|---|---|
| `agent-findings-ledger.md` | all | condensed record of the eleven agents' returned reports (every cited line/number) plus the lead's verification notes |
| `lead-notes.md` | all | lead working notes (baseline gates, static analysis, performance, IAS15 replication) |
| `tamper_corpus.sh` | F-01 | shrink/weaken the vector corpus; the smoke vector step still passes |
| `tamper_ae.sh`, `controls.sh` | F-01, F-06 | test-infra agent's tamper matrix and negative-control re-runs |
| `st/` (`drv.c`, `make_cases.py`) | F-02, F-13 | driver + generator for the exponent-clamp and beyond-20-digit reproductions |
| `strings-patch/msf_string_expclamp.diff` | F-02 | verified fix (64-bit exponent accumulation); `t_clamp.py` = the agent's reproductions |
| `sc1/` (`evil.vec`, `ok.vec`, `security_rerun_quick.sh`) | F-03 | over-long `internal.pack` op-name repro (build the runner with ASan, run `hash` mode) |
| `kill/*.vec` | F-05 | five Berkeley/exact-derived kill vector files (75 / 138 / 5,500 / 372 / 120 lines); all pass on the unmutated library |
| `test-infra-decider-lp64.diff` | F-06 | unified diff (against the repo) of the one-line LP64 fix in `tests/trig_exhaustive.c` and `tests/explog_decider.c`: `(unsigned long)(sig & 0xffffffffULL)` |
| `bench/bench.c` | F-11 | host micro-benchmark vs Berkeley SoftFloat 3e |
| `stock_rebound_compare.py` | headline IAS15 claim | stock REBOUND 5.2.2 vs the project's 2,001 recorded records and hashes |
| `ed1/p.c` | F-24 | NaN-sign corner vs Berkeley |
| `f16probe.mjs` | F-22 | site binary16 entry vs round-to-nearest-even |

**Note.** The agent-provided scripts (`tamper_ae.sh`, `controls.sh`, `sc1/security_rerun_quick.sh`) and the two ledgers contain absolute paths from the audit session's scratch area (`/tmp/claude-0/...`); edit the `A=`/`SP=` variables before running them elsewhere. The agents' full harnesses (several GB of logs and builds) lived only in that scratch area and are not part of this folder.
