---
business: Human Skills Training
type: roadmap
title: "Roadmap — the thin pointer launcher, and single ownership of every fact"
status: INSTALLED-2026-08-20-awaiting-effectiveness-check
owner: Chris Danilo
date: 2026-08-19  # corrected: this work was done 2026-08-19; filenames retain "08-20" to avoid breaking wikilinks
related: ["[[method]]", "[[LAUNCHER-outreach-draft-machine]]", "[[Cold-Outreach-Sequence-CCR&R]]", "[[CAPA-2026-08-20-unreconciled-run-manifest]]", "[[CAPA-2026-08-20-housekeeping-nonatomic]]"]
---

> ⏱️ **DATE CORRECTION, 2026-08-19.** This document and its filename were originally dated
> **2026-08-20**. That was wrong — all of this work was done on **2026-08-19**. Filenames are left
> as-is because several program files link to them by name and renaming would break those links.
> **Where the text says "2026-08-20" about work that was DONE, read 2026-08-19. Forward-looking dates
> ([Org 0102] Email 2 due 2026-08-20, effectiveness windows) are correct as written.**

# Roadmap — the thin pointer launcher

> ✅ **INSTALLED 2026-08-20. Chris approved the P7 obligation diff and the thin launcher is live in
> the scheduled task.** Stages 0–5 complete; the three-run effectiveness check is the only thing
> outstanding. Diff and full launcher text: [[LAUNCHER-thin-PROPOSED]].
> **Drift surface 27 → 0.** Launcher length ~9,900 words → ~250.
> **Rollback:** [[LAUNCHER-outreach-draft-machine]] holds the fat version verbatim.

## The finding that reframes the whole job

**Drift is not a launcher problem. The launcher is just where we happened to look.**
Measured 2026-08-20, three restatement failures live in the machine right now:

| Where | What it says | What is true | Stale by |
|---|---|---|---|
| **The installed launcher** | ~22 restatements of facts owned elsewhere | — | 3–4 found stale on 08-18 over 6 days |
| 🔴 **[[method]] "Approved copy" table** | *"Email 1 — v2, Chris's rewrite 2026-08-11"* · attachments `HST_InAction.gif` / `HST_Details.pdf` | **Email 1 is v6.** Attachments were renamed to `HST_WorkshopInAction.gif` / `HST_Flyer.pdf` on 08-12 — **a rename [[method]] documents elsewhere in its own file** | **4 revisions** |
| 🔴 **[[Cold-Outreach-Sequence-CCR&R]] header** | *"Email 2 is now v2 (Chris, 2026-08-18)"* | Its own body, 250 lines later: *"v3 is the form"* | **1 revision — the file disagrees with itself** |

**The program file is staler than the launcher we were about to rewrite for being stale.**

> ## THE PRINCIPLE: ONE OWNER PER FACT. EVERYTHING ELSE POINTS.
>
> Every fact — a template version, a message ID, a cap, a budget, a rule — has **exactly one owner
> file**. No other file restates it; they name the owner and stop.
> **Thinness is not the goal. It is what single ownership produces.**

**Why this is the right frame and "make the launcher shorter" is not:** shortening the launcher moves
~22 drift candidates out of one file. Single ownership removes the *category*. The [[method]] and
copy-file staleness above would both have been prevented by it, and neither would have been touched
by a launcher rewrite.

## The measurable target

**Drift surface = the count of statements in a file that assert a fact owned by another file.**
One command, checkable any time, and it goes in the nightly report beside the file-freshness line.

| File | Drift surface today | Target |
|---|---|---|
| Installed launcher | **~22** | **≤ 3** (the irreducible set below) |
| [[method]] | ≥ 1 confirmed stale (copy table) | **0** — it must not restate template versions or filenames |
| [[Cold-Outreach-Sequence-CCR&R]] | 1 (self-contradiction) | **0** |

## 🔴 The safety rule that makes thinning legal — a sharpening of P7

**P7 says: never remove the last independent statement of an obligation.** Thinning removes
redundancy, so P7 and this roadmap are in direct tension. The resolution matters:

> **A copy that lives inside a CONDITIONAL phase is not a reliable second statement.**
> The `(refresh as a delta at discovery)` parenthetical was fatal to delete because its only other
> copy sat inside **Phase 6**, which had silently stopped executing. **The test is not "does a second
> copy exist" — it is "is the second copy on a path that runs EVERY time."**

**So nothing leaves the launcher until its owner-file copy is verified to sit on an unconditional
path.** That check is Stage 2 and it is a hard gate.

## Stages

### Stage 0 · Build the instrument *(before changing anything)*

- Write the drift-surface counter as a script: for each program file, count assertions that restate
  a fact owned elsewhere (versions, message IDs, numeric caps, budgets, named rules).
- **Record today's baseline** so the change is measurable rather than felt.
- Add the count to the nightly report next to `File freshness:`.

**Gate:** baseline recorded for launcher, [[method]], copy file, [[STATE]].

### Stage 1 · Classify every launcher statement

Sort all ~90 lines into four buckets:

| Bucket | Action |
|---|---|
| **Irreducible** — cannot live anywhere else | Stays. See the list below |
| **Duplicated, owner is on an unconditional path** | ✅ Safe to cut |
| **Duplicated, owner is inside a conditional phase** | 🔴 **Do NOT cut.** Fix the owner first (move it to an unconditional path), then cut |
| **Orphan — exists ONLY in the launcher** | 🔴 **Rehome to its owner file BEFORE cutting.** Cutting first destroys the rule |

**Already measured 2026-08-20 — the orphan risk is small, which is why this is worth doing:**
16 of 17 launcher concepts have a live [[method]] counterpart. The exceptions are the two
**irreducible** harness instructions below, plus template versions — which are correctly owned by
[[Cold-Outreach-Sequence-CCR&R]] and simply should not be in the launcher at all.

**Gate:** every statement classified in writing. **P7 obligation diff produced** — the list of every
write/refresh/update/record/verify instruction being removed, with its surviving owner named.

### Stage 2 · Fix the owners *(the real work, and it is not optional)*

Before the launcher loses a single line:

1. 🔴 **Delete the stale copy table from [[method]]** and replace it with a pointer to
   [[Cold-Outreach-Sequence-CCR&R]]. **[[method]] must not name a template version or an attachment
   filename** — it does not own them.
2. 🔴 **Fix the copy file's self-contradiction** — the header says Email 2 is v2; its own body says
   v3. The body is right.
3. **Verify each cut-candidate's owner is on an unconditional path.** Any owner inside a conditional
   phase gets moved first — exactly as the suppression refresh was moved from Phase 6 to Phase 0.

**Gate:** drift surface of [[method]] and the copy file = **0**. Only then does Stage 3 begin.

### Stage 3 · Write the thin launcher

**The irreducible set — everything a launcher must own because nothing else can:**

1. **Identity** — who this is for and what it is
2. **The vault path**, and **abort if unreachable** *(if the vault is gone, the program is gone — this cannot be delegated to the program)*
3. **The first-output-line format** *(a harness instruction, not a program rule)*
4. **Execute autonomously, make reasonable choices, don't ask** *(harness)*
5. **One pointer:** *"read [[method]] and follow its phases in order"*
6. **The precedence rule:** *"if this launcher disagrees with the program files, the program files win"*

**Everything else is deleted**, because it has an owner. No versions. No message IDs. No caps. No
budgets. No rule restatements. No report structure.

⚠️ **This makes [[method]] genuinely load-bearing.** Today the launcher is a partial safety net for a
program file that fails to load or fails to be read carefully. **After this there is no net** — which
is the point (a net that silently goes stale is worse than none), but it means Stage 2 must be real.

### Stage 4 · Verify before installing

- Drift-surface count on the new launcher → **≤ 3**
- **P7 obligation diff** reviewed by Chris — every removed obligation, with its surviving owner
- **Dry-run the checklist by hand:** walk [[method]] phase by phase with only the thin launcher in
  hand and confirm every one of the ~20 manifest obligations is still reachable
- Keep the fat launcher in [[LAUNCHER-outreach-draft-machine]] as the rollback

**Gate:** Chris approves the obligation diff. Nothing installs without it.

### Stage 5 · Install and watch for three runs

- Install via `update_scheduled_task`; mirror it to [[LAUNCHER-outreach-draft-machine]]
- **Effectiveness check, three runs:** does every run manifest still balance, and does the report
  still carry every mandatory block? **A dropped obligation means Stage 2 missed an owner** — restore
  it to its owner file, not to the launcher

## Rollback

**One call.** The fat launcher is preserved verbatim in [[LAUNCHER-outreach-draft-machine]] and can
be reinstalled with `update_scheduled_task` in under a minute. **No vault data is touched by any
stage except Stage 2**, which only corrects statements that are already wrong.

## Risks, honestly

| Risk | Severity | Mitigation |
|---|---|---|
| **Stage 2 misses an owner and a rule silently dies** | 🔴 **High — this is the real risk** | The P7 obligation diff is a written, reviewed list. The three-run effectiveness check catches survivors |
| [[method]] fails to load and there is no longer a partial net | Medium | [[method]] failing to load already aborts the run — the net was never reliable in that case |
| The drift-surface count becomes a number nobody reads | Medium | It goes in the report beside `File freshness:`, which is already scored |
| Effort spent here is effort not spent approaching orgs | Low | Stages 0–2 are a few hours once; 08-19 cost a full report and four runs of stale suppression |

## What this does NOT do

- **It does not fix the degradation curve.** That is the two-task split, still undecided. This is
  orthogonal and strictly an improvement either way — **and it should be done first**, because if the
  run is ever split, thin launchers are what stop the split from tripling the drift surface.
- **It does not reduce what the run must read.** [[method]] is still 1,757 lines. That is the
  separate weight-cut work Chris approved (rationale → [[method-rationale]], plus the never-fired
  rule audit).
- **It does not make [[method]] correct.** It makes it the single place to correct.
