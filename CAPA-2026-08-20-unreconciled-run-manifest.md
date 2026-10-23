---
business: Human Skills Training
type: CAPA
title: "CAPA 2026-08-20 — the run has a to-do list nobody counts, so items have been dropping silently for four runs"
status: controls-installed-awaiting-effectiveness-check
owner: Chris Danilo
raised_by: Chris Danilo
date: 2026-08-19  # corrected: this work was done 2026-08-19; filenames retain "08-20" to avoid breaking wikilinks
severity: high
related: ["[[method]]", "[[STATE]]", "[[hubspot-suppression]]", "[[recipient-profile]]", "[[review-2026-08-19]]", "[[CAPA-2026-08-18-unqueried-tier1-roster]]"]
---

> ⏱️ **DATE CORRECTION, 2026-08-19.** This document and its filename were originally dated
> **2026-08-20**. That was wrong — all of this work was done on **2026-08-19**. Filenames are left
> as-is because several program files link to them by name and renaming would break those links.
> **Where the text says "2026-08-20" about work that was DONE, read 2026-08-19. Forward-looking dates
> ([Org 0102] Email 2 due 2026-08-20, effectiveness windows) are correct as written.**

# CAPA — the run's own completion is a judgement with no object

## What Chris saw

The 2026-08-19 run produced thirteen correct drafts and then never delivered its report. Chris found
out by asking. When asked what went wrong, the run gave **two different wrong answers in a row** —
first "it ran low on context," then "the sequence was wrong" — before being told to stop guessing
and investigate.

**Both answers were wrong, and being wrong twice is itself part of the finding.** The run reached
for explanations of *last night* because last night was the only thing it had looked at. The actual
defect is older, wider, and had been running unnoticed for four runs.

## 1 · What actually happened

**The report is not the only launcher obligation that has been silently skipped. It is the one that
happened to be visible, because Chris was waiting for it.**

An audit of the vault's file-modification dates and internal delta logs against the launcher's
enumerated obligations:

| Launcher / method obligation | Last actually done | Runs missed | How it was found |
|---|---|---|---|
| 🔴 **Refresh [[hubspot-suppression]]** — *"Rebuild at the start of every discovery run, before gating anything. A cached suppression list is a stale suppression list."* | **2026-08-13** (delta log's last entry) | **08-14, 08-17, 08-18, 08-19 — FOUR** | File mtime + its own delta log |
| 🔴 **Update `last_refresh` in that file's frontmatter** | Frontmatter reads `2026-08-12T09:30Z`; the delta log says the 08-13 run set it to `2026-08-13T09:10Z` | The file **disagrees with itself** | Frontmatter vs delta log |
| **Load [[golden-references]] before drafting an Email 1** | Not loaded 2026-08-19, despite six Email 1 drafts | ≥1 | The run used a forward-master ID remembered from STATE instead |
| **Fold recipient learning into [[recipient-profile]]** — *"recipient patterns are folded into recipient-profile immediately"* | 2026-08-18 | 1 | No 08-19 entry; the notes went into [[sequence-tracker]] instead |
| **Phase 7 report** | 2026-08-18 | 1 | Chris asked |
| **Any record that a run did or did not finish** | **Never existed** | all | [[STATE]] presents 08-19 as a clean pass |

**`contacted.md` was correctly not touched** — nothing was sent — so that one is not a miss.

### The suppression miss is the serious one, and it is not cosmetic

[[hubspot-suppression]] is a **safety** control. It is what stops the machine cold-emailing someone
who has become a client, has an open deal, or whom Chris has already talked to. [[method]] Phase 6
states the reasoning explicitly: *"HubSpot changes daily: a prospect becomes a customer, a deal
opens, Chris BCCs someone new. A cached suppression list is a stale suppression list — the same
failure class as the 2024 brochure that caused the bounce."*

**It has been seven calendar days stale across four runs, and every one of those runs reported a
clean suppression check.** The 2026-08-19 report said *"✅ all 4 lists, clean"* for six new
organisations. That statement was true against a list last updated on 08-13. **The check ran; the
list was stale; nothing in the machine could tell the difference.**

**No harm is known to have resulted.** No bounce, no complaint, no wrong-recipient incident has
surfaced. That is luck, not control.

### Why the roster sweep fired correctly on the same night

**On 2026-08-19 the roster sweep worked perfectly** — 8 orgs carded, 0 invalid, 0 people left
unqueried, and at [Org 1300] it ran *before* the ranking descended, which
is the exact ordering whose absence caused the 08-18 defect.

**That is the control group, and it is the whole proof.** The roster sweep fired because
[[CAPA-2026-08-18-unqueried-tier1-roster]] gave it a **countable object that blocks an artefact**:
the `Roster resolution:` line, three arithmetic identities, and *"no line, no card."* A run cannot
skip it and still produce a valid card.

Everything that drifted — the suppression refresh, the golden-references load, the recipient-profile
write, the report — is **prose in a launcher with no object and no artefact gate.**

## 2 · Root cause

> **The run's own completeness is the last remaining judgement with no object in this machine.**

This is not a new root cause. It is **the same root cause the 08-18 CAPA already identified and
wrote down**, applied one level up — to the run itself rather than to a step inside it:

> *"Every rule in this machine that fires reliably is attached to a countable object and blocks an
> artefact from existing — the two gates, `email_status`, the pronoun ban. Every rule that has
> failed to fire is a judgement with no object… **A count cannot be satisfied by doing the thing
> once.**"*

The launcher is a ~90-line prose to-do list. The run reads it, forms an intention, and executes from
working memory. **Nothing enumerates the obligations. Nothing counts them. Nothing compares what was
done against what was owed.** So an obligation is met when the run happens to remember it, and
skipped silently when it does not — and the longer and more eventful the run, the more the tail-end
obligations lose.

**Two amplifiers, both real, neither the cause:**

- **Ordering.** Optional housekeeping (archiving, the launcher self-edit) sat between the work and
  the report on 08-19, and the launcher edit threw a permission error that ended the run. Fixing the
  order would have saved *that* report. **It would not have refreshed the suppression list, which
  sits at the FRONT of the phase order and was skipped anyway.** Ordering is a mitigation.
- **Context length.** Long runs degrade — that is why the RUN EFFICIENCY section exists. But the
  08-19 run had room to spare, and the suppression refresh is a Phase 6 item skipped on four runs of
  varying length. **Capacity is not the variable.**

### Second-order cause: a dead run is indistinguishable from a clean one

The 08-19 run died on an error and **wrote nothing anywhere saying so.** [[STATE]]'s run-status entry
reads as a successful, passing run — because the run wrote that entry *before* it died, describing
what it intended to have done. There is no `IN PROGRESS` marker, no failure record, no coverage
statement. **A future run reading STATE would have no way to know the previous one did not finish**,
and would not know to check what it left behind.

That is why a four-run suppression gap survived four opportunities to be caught.

### 🔴 2 · b — THE REFACTOR DID CONTRIBUTE, AND HERE IS THE EXACT LINE IT DELETED

**Chris asked whether the recent refactoring caused this. Partly yes — it is the second of two
causes, and the timeline separates them cleanly.**

**The drift began 2026-08-14. The RUN EFFICIENCY refactor landed 2026-08-18.** So the refactor
cannot have caused the first three misses. It caused the fourth, and it removed the last thing that
would have caught the first three.

#### Cause 1 (08-14 onward) — the refresh is nested inside a phase that stopped running

[[method]] states the obligation in exactly [Org 0934], **line 1391, inside PHASE 6 — DISCOVERY
INCREMENT**: *"Rebuild [[hubspot-suppression]] at the start of every discovery run, before gating
anything."*

**Phase 6 is optional, bounded, and second-to-last.** [[STATE]] says `pool_ceiling: 80` — *"Above
this, discovery skips"* — and [[method]] Phase 1 step 4 says new-territory discovery runs *"only if
the target still isn't met."*

**From 2026-08-14 the batch stopped being filled by Phase 6 and started being filled by Phase 1.**
Florida's 30 coalitions arrived as a single list from the statewide association and were then worked
as Stage C page-reads — that is Phase 1 batch-filling, not the Phase 6 CCAoA parameter sweep. Texas
on 08-19 was the same shape. **Phase 6 proper has not executed since 2026-08-13 — and neither has
the suppression rebuild that lives inside it.**

The run entries confirm it and were mis-read until now: 08-13 records *"Discovery: not run as new
territory"* **and refreshed the list anyway**; 08-14 records real Florida discovery **and did not.**
The variable was never "did discovery happen." It was **"did PHASE 6 execute."**

🔴 **This is an original design flaw, not a refactor artefact.** It sat harmless while every night
was a new-territory sweep, and went live the moment Florida changed how the batch got filled.
**A safety control was made conditional on an optimisation.**

#### Cause 2 (08-19) — the refactor converted OBLIGATIONS into LOADS

The pre-refactor launcher, preserved in [[LAUNCHER-outreach-draft-machine]], listed the files in
**semantic groups that carried each file's purpose**:

```
SUPPRESSION — all four checked before any draft exists
9. outreach-machine/hubspot-suppression.md (refresh as a delta at discovery) ·
10. Lists/CCRR-Suppression-Already-Contacted.md ·
```

```
THE DASHBOARD
2. outreach-machine/discovery-pipeline.md — criteria, the VALUE-ORDERED state queue … Update every run.
```

```
4. golden-references.md — the "forward-master" emails … Name the master you used in every Email 1 report line.
```

The RUN EFFICIENCY refactor replaced all of that with a **two-column load table**:

> `LOAD EVERY RUN: method.md · STATE.md · sequence-tracker.md · discovery-pipeline.md ·
> Cold-Outreach-Sequence-CCR&R.md · contacted.md · hubspot-suppression.md · recipient-profile.md`
> `LOAD ONLY WHEN NEEDED: … golden-references.md — only when an Email 1 is drafted …`

**Four obligations were deleted as collateral, and every one of them is a WRITE:**

| Deleted phrase | What it obliged | Consequence on 08-19 |
|---|---|---|
| **`(refresh as a delta at discovery)`** | the suppression list must be **written**, not just read | 🔴 The launcher's only independent statement of the refresh obligation. Gone. The run read the list, checked against it, and reported "clean" |
| **`Update every run`** (discovery-pipeline) | the dashboard must be **written** | Survived only because [[method]] Phase 6 carries a separate loud 🔴 heading saying the same thing |
| **`Name the master you used in every Email 1 report line`** | golden-references must be **opened** per Email 1 | Demoted to "only when needed." Six Email 1 drafts, file never loaded, master ID used from memory |
| **`SUPPRESSION — all four checked before any draft exists`** | the group's *purpose* | The heading that made the obligation visible at a glance |

> 🔴 **THE GENERALISABLE FINDING, and it is the point of this section:**
> **The refactor optimised token cost by describing every file in terms of WHAT TO READ. In doing
> so it silently converted every file into a read-only object.** A list that said *what each file is
> for* became a list of *what to open*. **Nothing in the new table can express an obligation to
> write, so every write obligation stated only in the launcher was deleted without being noticed.**
>
> The efficiency goal was legitimate and worked — setup cost fell from ~120,000 tokens and the
> delegate-to-a-subagent rule kept ~400,000 tokens of research out of the main run on 08-19.
> **The cost was not the tokens saved. It was that a compression pass ran over a document
> containing safety controls, and nothing checked what fell out.**

#### Why this matters more than either cause alone

Cause 1 made the refresh stop firing. **Cause 2 removed the backstop that would have caught it.**
The launcher's parenthetical was redundant with method.md — right up until the moment method.md's
copy became unreachable, at which point the redundancy was the only remaining control. **It was
deleted as duplication two days before it was needed.**

### Contributing: the task tooling was available, used once, and abandoned

The run created **one** task at the start ("Phase 0 — Send-state reconciliation"), never updated it,
never marked it complete, and never added the other ~19 obligations. The environment issued five
reminders about the unused task list over the course of the run and all five were ignored. **The
instrument that would have made the manifest countable was present and idle.**

## 3 · Corrective action — this instance

| # | Action | Status |
|---|---|---|
| C1 | **Refresh [[hubspot-suppression]]** | ✅ **DONE 2026-08-20.** Connector was reachable. 412 records modified since 08-13, 68 carrying a suppression signal, **all but two already captured by the original build.** The two new ones (`ryanlasal@`, `jdunham@` at org0077.example) are **the machine's own sends logged back via the BCC**, not new relationships — the known BCC feedback-loop defect, still raised and still not auto-applied. 🟢 **All six orgs drafted on 08-19 re-checked against the refreshed list: CLEAN.** `last_refresh` → `2026-08-20T12:15Z` |
| C2 | Reconcile the `last_refresh` frontmatter against the delta log | ✅ **DONE 2026-08-20** — frontmatter had drifted to `2026-08-12T09:30Z` while the log said `2026-08-13T09:10Z`. Now superseded by the real refresh |
| C3 | Deliver the 2026-08-19 report | ✅ Done 2026-08-20, in chat |
| C4 | Correct the stale connector capability note in [[method]] (single-string → arrays verified 08-19) | ✅ Done 2026-08-20 |
| C5 | Write the 08-19 recipient learn-pass into [[recipient-profile]] | ✅ **DONE 2026-08-20** — RULE F (tier-on-role found 4 title-less Tier-1 people), OBSERVATION E (vendor title conflict reversing direction vs [Org 0582]), OBSERVATION F (first Tier-4 greeting, unsettled), OBSERVATION G (org-scale gauge took the CEO off twice) |
| C6 | Record in [[STATE]] that the 2026-08-19 run **did not complete** | ✅ **DONE 2026-08-20** — a correction block now sits above the 08-19 entry listing all six dropped obligations, and `last_run_status` in the frontmatter reads INCOMPLETE |

⚠️ **C1 may be blocked on connector authorisation.** The HubSpot connector requires auth and was not
exercised on 08-19. **Whether it is currently reachable is unverified — do not assume either way.**
If it is unreachable, that is a finding to report, not a reason to draft against a stale list.

## 4 · Preventive action — ✅ ALL SEVEN INSTALLED 2026-08-20 (Chris: *"implement your recommended preventative actions"*)

| # | Control | Installed in |
|---|---|---|
| **P1** | Run manifest built at Phase 0 via `TaskCreate` | [[method]] Phase 0 step 1b · [[STATE]] `run_manifest` · launcher STEP 2 |
| **P2** | `Run manifest:` completion line, report invalid without it | [[method]] Phase 7 · [[STATE]] `run_manifest_line` · launcher STEP 3 |
| **P3** | `File freshness:` line, >1 run stale = defect | [[method]] Phase 7 · [[STATE]] `file_freshness_line` · launcher STEP 3 |
| **P4** | `last_run_status` IN PROGRESS → COMPLETE | [[method]] Phase 0 step 1a + final act · [[STATE]] frontmatter + config · launcher |
| **P5** | Report before optional housekeeping | [[method]] RUN EFFICIENCY · launcher (moved to the top of the goal statement) |
| **P6** | Suppression refresh lifted to Phase 0 and made a Phase 2 gate | [[method]] Phase 0 step 1c, Phase 2, Phase 6 pointer · [[STATE]] ×2 keys · launcher item 9 |
| **P7** | Refactor rule — diff of deleted obligations | [[method]] RUN EFFICIENCY · [[STATE]] `refactor_obligation_diff` · launcher EFFICIENCY RULES |

**Eight new rows were added to the Failure modes table in [[method]]** so each control fails an
artefact rather than relying on memory.

🔴 **The launcher was also restored to a PURPOSE-GROUPED list** (THE PROGRAM / THE DASHBOARD / THE
COPY / STATE / SUPPRESSION), with every write obligation stated inline — reversing the 08-18
compression that caused cause 2. It now opens with: *"EACH FILE BELOW CARRIES ITS OBLIGATION. A file
listed only as a load is a file whose write obligation has been lost."*

### The original proposals, as written

**All four follow the one control pattern with a track record in this machine: a countable object
that blocks an artefact from existing.** None of them is a new judgement.

### P1 · THE RUN MANIFEST — enumerate the obligations as real tasks at Phase 0

**Before any work, the run materialises every launcher and method obligation as an explicit task**
using the task tooling that already exists (`TaskCreate` / `TaskUpdate`) — not as prose, not as
intention. Roughly 20 items: the two reconciliations, the suppression refresh, each phase, each file
write, the report.

**Every task ends in exactly one of three states: `completed`, `skipped — <stated reason>`, or
`FAILED — <what broke>`.** A blank state is not permitted.

*Why this and not "try harder to remember": the machine has five documented cases of a remembered
rule failing to fire, and zero of a counted one failing.*

### P2 · THE COMPLETION LINE — mandatory in every report, and it is arithmetic

**Every report carries this line, in this exact shape, and a report without it is invalid:**

```
Run manifest: N obligations · N completed · N skipped (reason each) · N FAILED
```

> 🔴 **Identity: `obligations = completed + skipped + FAILED`.** If it does not balance, the run is
> reported as INCOMPLETE regardless of how many drafts it produced.

**This is the object P1 needs.** P1 without P2 regresses the first time a run gets busy — exactly as
`spend_lookup_when_unpublished` did on the day it was ratified. **A skipped item with a stated reason
is a fine outcome; a skipped item nobody counted is the defect.**

### P3 · FILE-FRESHNESS ASSERTIONS — print the dates, let arithmetic do the catching

**Every report prints the last-modified date of each file the run is obliged to write**, with the
run-count gap:

```
File freshness: hubspot-suppression 2026-08-13 🔴 4 runs stale · recipient-profile 2026-08-18 ·
sequence-tracker 2026-08-19 ✅ · verification-log 2026-08-19 ✅ · discovery-pipeline 2026-08-19 ✅
```

🔴 **Anything more than one run stale is a DEFECT and the report names it.** This is the control that
would have caught the suppression gap on 08-14 — the morning after it first happened, not seven days
and four runs later. **It costs one `ls` and it needs no judgement at all.**

### P4 · THE IN-PROGRESS MARKER — make a dead run visibly dead

**[[STATE]] gets a `last_run_status` field, written at the START of every run:**

`last_run_status: IN PROGRESS — began 2026-08-20T09:02Z`

**It is flipped to `COMPLETE — report delivered <timestamp>` as the run's final act, after the
report.** If a run dies at any point, the field stays `IN PROGRESS`.

**The next run reads it first.** Finding `IN PROGRESS` means the previous run failed: the new run
reports that, checks what the dead run left behind, and completes any orphaned obligation before
starting its own. **Right now a dead run and a clean run leave identical records** — which is the
mechanism that let this hide.

### P6 · 🔴 LIFT THE SUPPRESSION REFRESH OUT OF PHASE 6 — the direct fix for cause 1

**Move the suppression refresh to PHASE 0, alongside the send-state reconciliation, and make it
unconditional.** It is a safety control and must not be nested inside an optional, skippable,
second-to-last phase whose execution depends on how the batch happened to get filled.

**Restate it as a gate, in the pattern that works:** no organisation passes Phase 2 unless
[[hubspot-suppression]]'s `last_refresh` is **today**. If the connector is unreachable, that is a
reported failure and new-org drafting holds — **it is never a reason to draft against a stale list.**

*Rationale: `suppression_recheck_at_draft: true` already asserts the Phase 2 check runs against
"today's list." That assertion has been false for four runs. Either the refresh moves to where the
assertion can be true, or the assertion has to be deleted — and deleting it is not acceptable for a
safety control.*

### P7 · A REFACTOR RULE — compression passes must not silently drop obligations

**Any future pass that shortens, restructures or "de-duplicates" the launcher, [[method]] or any
program file must produce a diff of DELETED OBLIGATIONS and put it in the report.** An obligation is
any instruction to **write, refresh, update, record or verify** — as opposed to read.

🔴 **Redundancy between the launcher and the program files is a CONTROL, not waste.** The
`(refresh as a delta at discovery)` parenthetical was redundant with [[method]] Phase 6 — right up
until Phase 6 stopped executing, at which point it was the only remaining statement of the
obligation. **It was deleted as duplication two days before it was needed.**

**Never remove the last independent statement of an obligation in the name of efficiency.**

### P5 · Report before optional housekeeping — a mitigation, kept as one

Write the report as soon as the drafts and the review file exist, **before** archiving, launcher
edits or dashboard polish. Those can fail; the report must not fail with them.

**Demoted deliberately from where this CAPA started.** It would have saved the 08-19 report and would
not have touched the suppression gap. **Real, small, and not the fix** — recorded so it is not
mistaken for one.

## 5 · Effectiveness check

**The next three runs. One question against each:**

> **Does the report's `Run manifest:` line balance, and does `File freshness:` show nothing more than
> one run stale?**

**Pass = the identity holds AND no file is >1 run stale AND `FAILED = 0`, on all three runs.**
Any run whose manifest does not balance, or that reports a file 2+ runs stale, reopens this CAPA.

⚠️ **A `skipped` item is not a failure** — a stated reason is a legitimate outcome and must not be
scored as one, or the cheapest route to a clean report becomes not listing the obligation. **Same
trap as folding `B` into `M` in the 08-18 CAPA.**

## 6 · What this does NOT fix — set expectations

- **It does not stop a run dying mid-flight.** Connector errors, permission aborts and interruptions
  will keep happening. **It makes the death visible and the unfinished work recoverable by the next
  run** — that is the whole claim.
- **It does not make the run faster.** The manifest adds overhead at Phase 0. That is the trade.
- **It does not tell you whether the drafts are any good.** Coverage is not quality. The two gates,
  the roster sweep and the pre-send self-check still own that.
- **It does not retroactively validate the last four runs' suppression checks.** Those were run
  against a stale list and should be treated as unverified. **C1 is the only thing that closes that,
  and it is open.**
