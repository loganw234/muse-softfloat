# A fifth round: a site that prints nothing it didn't read, and a verifier on the lead's own commits

Reconstructed after the round from its ledger, which is archived beside this
file as [archive/round5-ledger.zip](archive/round5-ledger.zip), and from the
session's transcripts. It covers one round of one project: the lead's shared
core and its verifier, then two waves of parcels, each parcel with a
verifier of its own. Mid-round a verifier was added on the lead's own
commits, because the lead had broken the round's own rule. The last
sections propose what METHOD.md should say differently, which is the
owner's to settle, and record how the round ended.

The lead wrote this file's first draft from its own summary of the round.
Read against the ledger before the commit, 12 of that draft's claims were
wrong or had no source. Its verifier then found one more, and two
addresses in the archive (observation 14).

## The setting

- **The project.** loganw.dev (github.com/loganw234/loganw.dev, MIT), the
  owner's personal site, live at loganw.dev. It is a static site
  generated from the owner's other repositories, under HonestFramework.
  - Every figure is read from a source: a repository at the commit
    `pins.json` names, the committed GitHub snapshot, or the site's own
    ledger, `docs/VALIDATION.md`. What no file backs is marked *stated*,
    with who said it and when.
  - One command, `bash verify/run.sh --require-all`, holds that. It refuses
    a numeral outside a figure's mark, a mark whose text isn't its fact's,
    a figure that no longer reads the same at its source, and more. It is
    run before every push, and every push to main deploys.
- **What is new against rounds 1 to 4:**
  1. **The parcels and their verifiers ran on Sonnet 5**, at the owner's
     word: "For the agents involving parcels, as they arent 'code heavy'
     tasks, dispatch them as Sonnet models". The lead, and the two verifiers
     of the lead's code, ran on Opus 5.5 (the cost notes give one
     exception).
  2. **A verifier on the lead's commits mid-round.** Round 4 put a verifier
     on the lead's P0 before dispatch. This round kept that, and its plan
     also said the lead's later seam commits go past a verifier before main
     moves. The lead broke that rule, found it, and added **verifier-seam**
     (observation 2).
  3. **Planted controls on two parcel verifiers**, kept light: the owner's
     "can be light on this project".
  4. **Gates that read text a browser renders.** The site promises a
     reader facts: an email address appears nowhere but the contact, a
     username appears on one page only, and a figure's source stands beside
     it. Each is checked by reading published HTML. How those checks
     converged is most of this round's story (observations 1 and 3).
  5. **The owner's own data.** It covers the owner's personal address, and
     how to refer to the owner, whose pronouns weren't stated until the
     round's end.
- **The round.** The plan is loganw.dev's docs/ROUND1.md.
  - **P0**, the lead's shared core: the facts layer, the page shell, the
    build and its gate, and Home. Then **verifier-P0**.
  - **Wave 1:** **P1**, Record and Verify; **P2**, the map on a phone, and
    the three Threads; **P3**, Work and five project dossiers.
  - **Wave 2:** **P4**, Corrections and Propose; **P5**, Method and About.
  - **Where:** each parcel worked in a worktree the harness made. The ledger
    sat outside every repository.

## Timeline (2026-09-29 into the 30th, local time, UTC-7; from the ledger's own timestamps)

| when | what |
|---|---|
| 15:11 | P0 committed as `2c02ffe`, not pushed; verifier-P0 dispatched on it. |
| 15:57 | verifier-P0: NOT READY. The first of its early findings: a figure printed as a plain string passed every gate. |
| 17:37 | The owner approves the biography, and clears the lead to begin once the verifier finishes. |
| 17:51 | verifier-P0: NOT READY again. |
| 18:05 | The owner: parcel agents on Sonnet. |
| 18:13-19:26 | verifier-P0: NOT READY eight times more. Six of them were stylesheet rules that could hide a figure or its source. The last, a form feed, was answered with CSS's own tokenizing rules and a second parser, tinycss2, as a cross-check, which the owner approved. |
| 19:34 | verifier-P0: READY at `ed990fb`, after ten NOT READY verdicts. Merged, pushed, deployed. |
| 19:41 | Wave 1 dispatched on Sonnet: P1, P2, P3. |
| 19:50 | Live at loganw.dev. |
| 20:38 | P3 reported. The lead's control on verifier-P3 is sealed, and verifier-P3 dispatched on the planted commit. verifier-P1: NOT READY. |
| 21:04 | Control unsealed: verifier-P3 found both plants, and nothing else wrong in P3's own work. |
| 21:16 | P1 merged, after two send-backs. |
| 21:22 | P3 merged. The lead notes a seam to check at P2's merge: P3's dossiers read relations.json, while P2 derives StoryDocs' edges. |
| 21:26 | verifier-P2: NOT READY, on a control that never exercised case-folding. The lead finds the owner's address in P2's facts.json arguments, and adds a site-wide gate. |
| 21:37 | P2 fixes both. Its branch history holds the address in earlier commits, so it is to be squash-merged. |
| 22:01 | P2 squash-merged, so that main's history never holds the address in a file. **The lead records that it has broken the round's rule:** eight of its own commits reached main with no verifier. verifier-seam is dispatched on Opus, and wave 2 waits. |
| 22:43-00:50 | verifier-seam: NOT READY four times. Each time it found a way past the text gates. |
| 00:16 | The lead stops answering shapes one at a time, and holds pages to a subset of HTML that Python's parser and a browser read alike. |
| 00:27 | Wave 2 dispatched on Sonnet (P4, P5), beside verifier-seam's re-check. The lead records why it changed its earlier decision to wait. |
| 00:56 | The owner's address found in three ledger files, one of them the lead's own brief. The lead redacts two, and P4 its own. |
| 01:10 | `07b1526` answers verifier-seam, and a finding P4 filed: a lead control took the first `snapshot_date` fact in facts.json to be the one the map draws. Two other controls that picked a fact by its method are fixed with it. |
| 01:26 | verifier-seam: READY at `07b1526`. |
| 01:34 | `07b1526` live. CI now resolves the pinned Python, 3.12.9. |
| 01:43 | Control unsealed: verifier-P4 found both plants, and nothing else wrong in P4's own work. |
| 01:47 | verifier-P4: READY on P4's own tip. P4 merged locally. |
| 02:01 | verifier-P5: NOT READY. A "newest entry" on Method had gone stale, and "stated once" was held by no gate. The lead adds `ONLY_HERE` to the seam. |
| 02:25 | verifier-P5: READY. P5 merged locally. |
| 02:45-03:00 | verifier-seam, on the lead's commits since `07b1526`: NOT READY twice. `ONLY_HERE` missed attributes and fullwidth copies, then punctuation variants. |
| 03:16 | verifier-seam: READY at `8260fa8`. Pushed: all nine pages live at 03:21. |
| 03:29 | The lead finds "Logan, in his own register" live on About, where the round's rule said to write "Logan". Corrected, verified, and live at 03:42. |
| 04:48 | The owner's five decisions. The round closes, and this ledger is archived. |
| 05:03 | The owner, on the pronoun: "He/his is fine". The lead records the checks on this file's draft. |
| 05:29 | verifier-cs5, on this file's first commit: NOT READY on one count and two addresses in the archive. Accepted: the archive is redacted, and the unpushed commit replaced. |
| 05:34 | verifier-cs5: READY on the replaced commit. The only changes after it are a blank line it noted, this row, and the ledger entry recording it, which makes the lead's count 70. |

## What the method predicted, and what happened

1. **A gate that lists what to refuse is walked past, again.** Case study
   4's observations 10 and 14 said so, and this round repeated it twice.
   - **verifier-P0:** ten NOT READY verdicts on the shared core. Six were
     stylesheet rules that hid a figure or its source: a hiding rule
     nothing checked, then transparent text spelled another way, six more
     spellings, nested and at-rule blocks, a quote inside an unquoted
     `url()`, and a form feed. What held was a tokenizer that follows CSS
     Syntax 3, with an independent parser, tinycss2, as a cross-check.
   - **verifier-seam:** the same, for HTML (observation 3).
2. **The lead broke its own rule, and the rule was right.**
   - **The rule.** The round's plan said: "The lead's seam commits and
     records (VALIDATION entries, commit messages) go past a verifier before
     main moves."
   - **What happened.** After P0's READY, the lead pushed eight commits of
     its own with only its own gate, among them an email gate, one list of
     edges for the map and the dossiers, and the site's own ledger as a
     source. It recorded this at 22:01, in the entry for P2's merge.
   - **What the verifier found.** verifier-seam's early findings, and then
     its first verdict, found gate-kind defects in three of those commits:
     - the email gate read raw bytes, so an encoded address passed;
     - the edges control compared two functions, not the published pages;
     - the ledger facts cited an entry by its line, so an insertion swapped
       entries silently.
   - Its first four verdicts were all NOT READY. The lead's own gate was no
     substitute for someone else's.
3. **Text read by two parsers converged only when the two were made to
   agree.** verifier-seam's verdicts, in order:
   - **Raw bytes.** An address passed as a character reference, as
     percent-encoding, or split by a `<wbr>`.
   - **Decoded readings.** Then a stray end tag, a `<td>` outside a table
     and a `<title>` in the body passed. A browser repairs each of these
     another way than Python's parser reads it. With all ten source labels
     on Verify wrapped in `<title>`, each drew 0 px wide in Chromium, while
     the check still counted each beside its figure.
   - **The fix.** The lead held pages to a subset of HTML both read alike:
     - strict nesting, and each element only where HTML allows it;
     - text only where a browser draws it;
     - one way to write a tag;
     - HTML's own whitespace;
     - no comment.

     The site's own pages already fit it.
   - **Then the subset's own gaps,** each closable:
     - an SVG `<title>` inside `<text>`;
     - a no-break space, which Python's `strip()` counts as whitespace and
       HTML doesn't;
     - an override character written as a reference;
     - an end tag holding an attribute. The desktop's Python 3.12.9 and
       CI's 3.12.14 read that two ways, so the Python version is now pinned
       in one file that the desktop and CI both read.
   - **Then READY.** The shapes still open are stated as limits where the
     claim is made: text put together by layout alone, look-alike letters
     from another script, and an address spelled out for a person.
   - **An allowlist held here.** Case study 4's observation 14 found
     allowlists over spellings falling too. This one held because it was
     drawn where the check's reading and a browser's agree, not from the
     spellings found so far.
4. **Planted controls caught 2 of 2, twice. The second could have been
   passed by a diff.**
   - **verifier-P3** found a paraphrase that added "and on the card", and
     an unsourced superlative.
   - **verifier-P4** found a rule of engagement misquoted ("within a day",
     where the spec says "in days"), and an unsourced sentence.
   - **The weakness.** verifier-P4 found its plants by diffing the planted
     commit against P4's tip, which the lead's ledger named. It judged both
     on their content too, so the finding stands. But a control whose
     parcel tip is in the ledger tests the verifier's diff, not its
     reading.
5. **Parcels and verifiers on Sonnet held.** Every parcel reached READY.
   What its verifier found:
   - **P1:** an entry link nothing checked, and prose that stated
     cft-fp256's contract outside any quote, then one more such sentence.
     Two send-backs.
   - **P2:** a control that never exercised case-folding.
   - **P3:** past the planted control, one typed sentence judged
     borderline. P3 quoted it, and four more its own sweep found.
   - **P4:** nothing in its own work.
   - **P5:** a stale "newest entry", and a "stated once" nothing held.

   The lead found two more at P2: the address in its facts.json arguments,
   and the seam in observation 6. verifier-P5 passed a pronoun
   (observation 11).
6. **A seam between two parcels belonged to neither, again.**
   - **What broke.** P3's dossiers read relations.json for their
     Connections. P2's map also drew edges it derived from StoryDocs'
     directories at StoryDocs' pin.
   - **The effect.** Four of the five dossiers missed StoryDocs' edges.
     cft-rebound had none to miss.
   - **Who found it.** The lead, at P3's merge, to check at P2's.
   - **The fix.** One list of edges, read by both. Later the gate compared
     the published pages themselves, after verifier-seam showed that the
     first control compared two functions.
7. **A seam change broke an assumption the other way.** One of the lead's
   controls took the first `snapshot_date` fact in facts.json to be the one
   the map draws, on Home. P4's `corrections.py` sorts before `home.py`, so
   the control read another page's fact.
   - P4 filed it with a standalone reproduction, and fixed nothing outside
     its files. P5 hit it independently: its `about.py` sorts before
     `home.py` too.
   - The lead fixed it, with two other controls that picked a fact by its
     method.
8. **The owner's address travelled further than any rule allowed.**
   - **P2** keyed an account by its email in facts.json's arguments. The
     lead found it before merge. The site gained a gate, and P2 was
     squash-merged so that main's history never held the address in a file.
   - **The lead** had itself written the author identity strings into P2's
     brief.
   - **P4** copied the address from its own environment into its ledger
     file, in the sentence saying it must never be written.
   - **In the ledger,** a side note from verifier-seam led the lead to count
     it in three files. The lead redacted two, and P4 its own. verifier-seam
     then measured none left.
   - **The lesson.** Agents see the owner's address in their environment.
     The site's privacy stage now refuses an address in any file main's
     history holds, and reports only a count.
9. **Controls that tested nothing.**
   - **CRLF.** On Windows, 22 of the `write_text` calls in the lead's
     controls wrote CRLF line endings. The lead first recorded 24;
     verifier-seam counted 22, and the fix added two more, all LF.
     Carriage returns left in a restored MANIFEST had satisfied five new
     controls, which named no file.
   - **The raw text.** Two email controls were caught by raw text that
     still held the whole address. Their joining rule was never exercised.
   - **Neither showed as a failure.** Every control now names the rule it
     exercises, and every restore keeps LF.
10. **The records overstated how things were measured, three times.**
    Each time, a record said shapes "passed every stage" that verifier-seam
    had measured at unit level only:
    - an IDN domain, a non-ASCII top-level domain and an address literal;
    - two of three unassigned default-ignorable code points;
    - a fullwidth copy of the statement `ONLY_HERE` holds.

    After the third, the records named each shape's level, and
    verifier-seam's last pass found them right.
11. **A rule a brief states, and no gate reads, is the verifier's alone
    to hold.**
    - During the round, the owner's pronouns hadn't been stated. At 22:20
      the lead found "he" and "his" for the owner in code comments, one of
      them its own. It fixed them, and put a rule in wave 2's common brief
      and in each of its dispatches: write "Logan".
    - P5 wrote "Logan, in his own register" on About. verifier-P5 read that
      line and passed it, and afterwards recorded the miss as its own.
    - The lead found it on the live page after the deploy. The fix went
      past verifier-P5 before the next push, and the verifier checklist now
      names it.
    - Ten lines of the ledger, all written before the rule, use "he", "his"
      or "himself" for the owner, and stand as written.
    - At the round's end the owner settled it: "He/his is fine". The
      observation stands for any rule a brief states and no gate reads.
12. **Finished agents left processes running.**
    - Watch loops, and two local web servers that parcels had started,
      outlived the agents that started them. One server had no bind
      address, so it listened on every interface. They held the worktree
      folders open, so the cleanup couldn't delete them.
    - Stopping the loops woke one finished verifier, verifier-P3. Its
      watch's exit reached it as a notification. It checked the two later
      commits to its files, recorded its watch's end as a lapse of its own,
      and said it had re-armed its watch, on a closed round.
13. **The owner's decisions were few and quick.**
    - During the round: the biography, the repository, the Sonnet
      direction, a parser for the cross-check, and one door's wording.
    - At its end: five answers in one message, and one more word on the
      pronoun.

    The lead held back what was the owner's: the labels on GitHub,
    deletions, and where to archive.
14. **The case study's own draft needed the ledger.**
    - The lead wrote the first draft from its own summary of the round, not
      from the ledger.
    - Read against the ledger, the transcripts and the repositories before
      the commit, 12 of its claims were wrong or had no source. The ledger's
      last entry lists them.
      - Five were plain errors: a count of verdicts, a merge time, a count
        of writes, a page left out, and a control count given for the wrong
        commit.
      - Seven had grown in the retelling. For example, "more than all the
        agents together" was true only of the agents with transcripts.
    - Its verifier, on Sonnet, then found two more things in the commit.
      - The verifiers' entry count was one short. One of verifier-P4's
        headings had lost its timestamp, and the lead's count read
        timestamped headings only.
      - The archive held two GitHub noreply addresses, of two named public
        accounts. The lead's own check had allowed them, and the verifier
        held the archive to the site's narrower rule for what it publishes.
        They were redacted, and the unpushed commit replaced, so that
        ParcelRound's history never holds them.
    - This is observation 2 again, at the round's end: the lead's records
      need a reader who isn't the lead.

## Cost of the round (measured from the transcripts)

Each agent's usage is summed from its own transcript, once per message.
"Output" is what it generated. "Read" is its input and cache reads and
writes, mostly the cache re-read on every turn.

| agent | model | messages | output tokens | tokens read |
|---|---|---:|---:|---:|
| verifier-P0 (the shared core) | Opus 5.5 | 344 | 166,933 | 188,799,976 |
| P1: Record and Verify | Sonnet 5 | 170 | 84,253 | 67,583,833 |
| P2: the map on a phone, Threads | Sonnet 5 | 297 | 129,102 | 145,550,697 |
| P3: Work, five dossiers | Sonnet 5 | 273 | 87,883 | 130,059,746 |
| verifier-P1 | Sonnet 5 | 88 | 44,745 | 25,994,875 |
| verifier-P2 | Sonnet 5 | 88 | 25,289 | 19,861,079 |
| verifier-P3 | Sonnet 5 | 113 | 34,007 | 33,630,944 |
| verifier-seam (the lead's own commits) | Opus 5.5 | 342 | 136,261 | 183,676,748 |
| P5: Method and About | Sonnet 5 | 142 | 13,745 | 60,827,101 |
| verifier-P4 | Sonnet 5 | 80 | 15,363 | 19,804,157 |
| verifier-P5 | Sonnet 5 | 124 | 8,939 | 31,652,093 |
| agents, P4 aside | | 2,061 | 746,520 | 907,441,249 |
| the lead, during the round | Opus 5.5 | 900 | 1,278,391 | 530,384,559 |

- **P4's transcript file is empty.** At its end the harness reported
  648,345 tokens, 230 tool uses and 50.1 minutes. One more transcript file
  is empty. It was written at 20:45, most likely by the one subagent P2
  disclosed. Neither is counted here.
- **The models are the transcripts' own.**
  - Every Sonnet agent's transcript records `claude-sonnet-5`. The owner's
    direction had said "(5.5 is current)".
  - 10 of verifier-seam's 342 messages, from 01:19 to 01:26, record
    `claude-opus-4-8`. Its READY on `07b1526`, at 01:26, falls in that
    stretch. The transcript doesn't say why.
  - Each Opus row, the lead's included, counts one harness message with no
    tokens.
- **The lead's row** counts its own messages from the round's first ledger
  entry, 15:11:26, to the close at 04:48.
- **The two Opus verifiers** generated 303,194 of the agents' 746,520 output
  tokens. The nine Sonnet agents with transcripts generated 443,326.
- **The lead's own share.** It generated 1,278,391 output tokens, more than
  the eleven agents with transcripts together. It built the shared core and
  every seam change, and it answered each of verifier-seam's findings
  itself.
- **Wall-clock durations aren't compared here.** Agents that waited on
  their watches ran for hours of idle time.

## What METHOD.md should say differently (proposed; the owner's to settle)

Each item says whether it is **new**, a **reinforcement** of a rule the
method already has, or an **extension** of one. One is marked as an
observation, not yet a rule. The bracket names the observations each rests
on.

**§2, the lead's work and the seam.**
- **The lead's seam commits and records go past a verifier before main
  moves, all round, not only P0** (reinforcement: this round's plan had
  the rule, and the lead broke it). [2]
- **When a seam changes mid-round, the lead checks its own controls for
  assumptions the change breaks.** Examples are a fact picked by its
  position, or a page taken to be unbuilt (new). [7]

**§3, the brief.**
- **No brief holds the owner's personal data** (new). Tell every agent its
  environment holds it, and that no file may. A privacy gate over what a
  push publishes holds the rule. [8]
- **A rule the brief states and no gate reads goes on the verifier's
  checklist by name** (new). [11]

**§5, gates.**
- **Where a gate reads text another program renders, hold the input to a
  subset both read alike,** rather than listing the shapes to refuse or
  allow (extension of case study 4's observations 10 and 14). [1, 3]
- **Pin the parser's version in one file that the desktop and CI both
  read** (new). [3]
- **A control names the rule it exercises, and restores the bytes it
  planted over exactly** (new). [9]

**§6, verifiers.**
- **A planted control's parcel tip stays out of the ledger until its
  verifier reports** (extension of the sealing this round used). [4]
- **A record names the level at which each shape was measured, the full
  gate or a unit-level call** (new). [10]
- **An agent stops its own background work, its watches and servers,
  before it reports, and the lead checks for leftovers at cleanup** (new).
  [12]

**The round's end.**
- **The case study is written from the ledger, not from the lead's
  memory, and read against it by someone other than the lead before it is
  pushed** (extension of §2's rule to the round's last record). [14]

**Models.**
- **Parcels, and their verifiers, can run on a smaller model when the work
  is sentences rather than code** (observation, not yet a rule). The
  defects this round's Sonnet verifiers missed were each caught later, by
  the lead. [5, 11]
- **Take each agent's model from its transcript, not from its dispatch**
  (new). [the cost notes]

## The round's end (2026-09-30)

**What was delivered.**
- **loganw.dev**, live, all nine pages, deployed from `57bd202`:
  - Home and Threads (with its three threads);
  - Work (with its five dossiers);
  - Method, About, Record and Verify;
  - Corrections and Propose, with DISPROOF and proposal issue forms.
- **Its gate:** at `8260fa8`, 11 of 11 stages, nothing skipped, 314
  controls caught. `57bd202` changed About's lede, two comments and the
  records, and passed 11 of 11 again.
- **The owner's decisions at the close:**
  - About's two drafted sentences are approved.
  - The workloads door keeps its wording: "Keep it, at worst aspirational,
    at best already true".
  - The DISPROOF and proposal labels are created on GitHub.
  - The parcels' worktrees and branches are cleaned up.
  - This ledger is archived here, with this case study.
  - And on the pronoun: "He/his is fine".

**What carries forward.**
- **A small batch of the lead's changes, triaged in the ledger's last
  entries,** goes past a verifier before its push:
  - the owner's decisions, in SPEC.md, and About's approved sentences;
  - the `ONLY_HERE` limits in the page contract;
  - the note that `run.sh` checks Python's version string;
  - a docstring in `corrections.py`.
- **Method's "This is the one place the site states it"** shows a reader no
  limit. Whether to add one is the owner's call.
- **The proposals above,** which are the owner's to adopt or not.

**The ledger** is archived at
[archive/round5-ledger.zip](archive/round5-ledger.zip). It holds 38 files,
each with its last-modified time, and each read back byte for byte against
its source:

- the lead's 70 entries;
- the five parcels' 24;
- the seven verifiers' 61, one of them under a heading that lost its
  timestamp, as the entry after it says;
- the nine briefs, and the ledger's README;
- the fifteen urgent messages.

Before archiving, the lead checked it three ways.

- No file holds the owner's address's domain.
- No file names a private repository the site doesn't read.
- No file holds an email address except the contact, the commit trailer's,
  and addresses at example domains. Two GitHub noreply addresses were
  redacted to reach that.

Each wave's durable findings were folded into loganw.dev's own
docs/VALIDATION.md as it merged. The working copy is kept until this
archive is pushed, then deleted, as the method says.

## Postscript (2026-10-02)

Added by round 6's lead. The text above is unchanged.

- **The batch named under "What carries forward"** went past
  verifier-close in loganw.dev. That verifier said NOT READY on three
  earlier versions of the round's close entry, and every finding was
  accepted (loganw.dev's docs/VALIDATION.md, the entry "the round
  closes"). Its side note on `80c9f32` is answered in `d093ba6`.
  - The text read records no READY on the version pushed.
  - Both commits are on loganw.dev's main, which GitHub also has
    (`43c36a2` on 2026-10-02).
- **This case study and its archive** join ParcelRound's main in
  round 6. Whether, and when, they are pushed is the owner's word, and
  CASE-STUDY-6.md records it.
- **The proposals above** are settled in [ADOPTION.md](ADOPTION.md).
  - CS5#1, #7 and #10 are adopted in round 6: each was practised in a
    later round.
  - The other ten stay pending. Nine were practised only in this round,
    and CS5#8 not at all.
- **The ledger's working copy**, `loganw-dev-ledger/`, is kept until this
  archive is pushed, as the round's end above says. Deleting it is the
  owner's word.
