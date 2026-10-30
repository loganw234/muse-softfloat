# Known limits stated by the behaviour they concede

ParcelRound METHOD.md section 5: a limit is stated by the behaviour it concedes, not by the plants that found it.

## 4a. What still passes

- **From:** cft-fp256's docs/VALIDATION.md at `39f9801`: the entry "gates that could pass a damaged input", lines 23515-23521. Not in this kit.
- **What it shows** (the kit's reading): Limits stated as what still passes: "It guards accident, not forgery"; a skip by name where git cannot say.
- **Cut:** 3 line(s): 23517 (a term from the gate's list); 23520 (a term from the gate's list); 23521 (a term from the gate's list).

> **5. Known limits** (Logan's rule: they merge).
> - **The stamp is a file, like the record:** a `MODEL` copied from a current directory onto an older set and its older record passes. It guards accident, not forgery.
> [line 23517 cut: it holds a term from the gate's arithmetic list]
> - **The history leg is a SKIP in a shallow clone, with no git and in a folder inside another repository,** and only a full clone sees a lost commit; the form leg cannot tell a real clean build from a well-formed commit that never existed. A fork that rewrote its history fails 1b by name in a full clone, which is true: its certificates name commits it lacks.
> - **`make` is held by its decision function, not by a run:** no gate runs `make`; `keep_decision` is tested and a test reads the source of `make_version_1` for the call, and the real `make` was run only in scratch.
> [line 23520 cut: it holds a term from the gate's arithmetic list]
> [line 23521 cut: it holds a term from the gate's arithmetic list]

## 4b. What did not run, stated as limits

- **From:** cft-fp256's docs/VALIDATION.md at `39f9801`: the entry "the card scheduler's staged runner", lines 23382-23392. Not in this kit.
- **What it shows** (the kit's reading): Limits stated as costs and as what did not run: "The guard is a look, not a lock". The section's last line, its verifier's notes kept as limits, is cut for a term on the gate's list.
- **Cut:** 1 line(s): 23392 (a term from the gate's list).

> **4. Known limits** (Logan's rule: they merge).
> - **Nothing here ran on the card, the box, XRT or the network.** The build's checks are driven by a fake host tree (a Makefile that makes shell-script tools, an `ldd` on PATH that says what each case needs), the remote and the bundle are scratch repositories, and the steps run the driver's stand-in or small scripts; the real `make` and `ldd`, `git fetch` of github.com, the real tools and a real `driver-quick` are the lead's first runs.
> - **The random-slice case-count hold is the driver's, and not here:** the soak step passes no expected count for a random slice, as the driver's default run does, and no test reads a stand-in random slice's printed count. Parcel P5 (KL-23) adds the hold per mode to the driver and changes the stand-in's random branch; it is to be imported once P5 has merged (the lead re-runs this suite on the merged tree).
> - **`clone-built` is the buildreal trap's scope** (ignored files under `host/`), not the study's wording; a job asking for the dry tests on a SHA an earlier job built is refused by it until the clone is gone (retention is S4's).
> - **The guard is a look, not a lock,** as the driver's is: it sees the processes alive when it asks, and the card's lock is the scheduler's own. It is skipped for a dry job.
> - **`commit-unpushed` needs the remote's branch heads:** a commit reachable only from a tag or a pull-request ref is not shown pushed. A new SHA is a full clone of its source. **With `code.remote` null (the default) every bundle job at a pushed commit is refused `commit-unpushed` unless it says `allow_unpushed`,** so the box's `config.json` must set `code.remote`.
> - **A driver run's own directory (`driver-quick`) is a subdirectory of the job's,** which S1's `SHA256SUMS` does not list (it lists a directory's files); the step's console log is a file and is covered. The leg records are the driver's schema in `job.jsonl`, with no `run_start`, so the driver's report and the figure extracts cannot read a staged job's directory yet (S4).
> - **`rc-only` is raised by nothing;** the study lists it among the refusal names. **The two new parsers are held to fixtures made from the suite's and the driver's source,** not to their real output on a card day; a change of wording is a `parse_error`, never a pass. The step types are the U50's (a card of another kind brings its own steps with its kind).
> - **Windows runs less:** the build, the real-tool steps, `run_step`'s process checks and the real-process guard scenario need make, sh, nice, timeout or /proc and are skipped by name there, with the plants that need them; the dry jobs through the whole runner run there. `run_step`'s Windows path (`terminate()`, `taskkill`) was not run.
> - **S3 and S4:** no window (`kind: window` is refused `window-unsupported`), preemption, restart recovery, metric, fold, retention or extract; the scheduler's own commit is not yet in its records. `driver-quick` passes `--image NAME=PATH --sha NAME=SHA` only for registry images the driver names (quad, single, deep). The step timeouts are the driver's for its legs and guesses for the rest (`vectors` 1,800 s, `drytests` 3,600 s, `driver-quick` 5,400 s, a soak slice 1,800 s; each overridable by `timeout_s`).
> [line 23392 cut: it holds a term from the gate's arithmetic list]

---

These passages are excerpts of cft-fp256's docs/VALIDATION.md. cft-fp256 is Copyright 2026 Logan W., under the Apache License 2.0. The kit's NOTICE.md says what else it carries, and under which licence.
