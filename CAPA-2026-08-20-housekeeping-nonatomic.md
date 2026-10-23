---
business: Human Skills Training
type: CAPA
title: "CAPA 2026-08-20 — the run's only destructive operation is non-atomic, non-idempotent, undocumented, and scheduled last"
status: controls-installed-awaiting-effectiveness-check
owner: Chris Danilo
raised_by: Chris Danilo
date: 2026-08-19  # corrected: this work was done 2026-08-19; filenames retain "08-20" to avoid breaking wikilinks
severity: high
related: ["[[method]]", "[[STATE]]", "[[sequence-tracker]]", "[[CAPA-2026-08-20-unreconciled-run-manifest]]", "[[rule-exhaust-self-recovery]]"]
---

> ⏱️ **DATE CORRECTION, 2026-08-19.** This document and its filename were originally dated
> **2026-08-20**. That was wrong — all of this work was done on **2026-08-19**. Filenames are left
> as-is because several program files link to them by name and renaming would break those links.
> **Where the text says "2026-08-20" about work that was DONE, read 2026-08-19. Forward-looking dates
> ([Org 0102] Email 2 due 2026-08-20, effectiveness windows) are correct as written.**

# CAPA — why the housekeeping failed, and what it actually did to the vault

## What Chris asked

> *"But why did housekeeping fail and why did it break other outputs?"*

**Two separate questions, and the honest answers point in different directions.** The first has a
precise, reproducible, mechanical answer. **The second's answer is "it didn't — and that is the
alarming part, because it very nearly did and nothing would have noticed."**

## 1 · What actually happened, step by step

The 2026-08-19 run's Phase 4 housekeeping had three jobs: archive the oversized
[[sequence-tracker]], archive the oversized [[STATE]], and update the scheduled task. Here is the
actual sequence:

| # | Operation | Result |
|---|---|---|
| 1 | Append [[sequence-tracker]] lines 56–187 to `archive/sequence-tracker-archive-through-2026-08-18.md` | ✅ **SUCCEEDED** — archive grew 78,034 → 90,166 bytes |
| 2 | Build the replacement file in `/tmp/st.md` | ✅ succeeded |
| 3 | `mv /tmp/st.md sequence-tracker.md` | 🔴 **FAILED** — `inter-device move failed … unable to remove target: Operation not permitted` |
| 4 | Retry with `cp /tmp/st.md sequence-tracker.md` | ✅ succeeded |
| 5–7 | Same three steps for [[STATE]], using `cp` from the start | ✅ succeeded |
| 8 | `update_scheduled_task` | 🔴 **FAILED** — tool permission stream aborted. **The run ended here. The report was never written.** |

### The mechanism, confirmed by reproduction rather than inference

**Reproduced deliberately on 2026-08-20:**

```
cp  /tmp/probe.txt  <vault>/_probe_target.md   → OK
mv  /tmp/probe.txt  <vault>/_probe_target.md   → inter-device move failed;
                                                 unable to remove target: Operation not permitted
mv  <vault>/a.md    <vault>/b.md               → OK
rm  <vault>/_probe_target.md                   → Operation not permitted
```

**`/tmp` lives inside the Linux sandbox; the vault is a mounted host filesystem.** A cross-device
`mv` is a copy followed by an *unlink of the target*, and unlink is not permitted on the mount.
**`cp` works because it truncates and rewrites in place without unlinking.** `mv` *within* the vault
works. **`rm` never works.**

🔴 **This is a stable, knowable property of the environment that was written down nowhere.** It had
to be discovered by failing — the same class of defect as the Gmail connector parameter shape, and
it belongs in the same "capability claims" discipline.

## 2 · Did it break other outputs? — the honest answer is NO, and that is the finding

**Every file was verified on 2026-08-20. Nothing is corrupted and nothing was lost:**

| Check | Result |
|---|---|
| Archives double-appended? | ✅ **No** — exactly one `ROLLED IN FROM` header in each archive |
| Content lost at the splice seam? | ✅ **No** — Westchester, [Person 0326], ACCORD, [Person 0472], Five County all present in the archive |
| Live files structurally sound? | ✅ **Yes** — frontmatter intact, no truncated tables, no orphaned rows |
| Live holds carried forward as claimed? | ✅ **Yes** — the pointer block reproduces every still-live hold |

**One real but benign defect found:** the roll-in copied lines 56–**187** while the live file was cut
at 56–**177**, so **ten lines are duplicated** — the `OPEN DEFECT WITH A DATE — 2026-08-20` section
now appears once in the live tracker and **twice** in the archive (lines 669 and 1076), because the
08-18 archival had already captured it. **Duplication, not loss.** Nothing reads the archive during a
normal run, so it is cosmetic. **It is also proof that the boundary arithmetic was done by hand and
was wrong by ten lines** — which is the point.

### 🔴 So what actually went wrong: the vault survived on a judgement call, not a control

**Between step 1 and step 4 the vault was in an inconsistent state**: the archive had already
received 12 KB of content that the live file still also contained. **Had the run retried the failed
block wholesale — the obvious, natural response to a failed command — the archive would have been
silently double-appended.**

It did not, because the run happened to notice: *"If I re-run the whole block it would double-append.
Let me only do the splice now."* **That is a person catching a landmine, not a machine that cannot
step on one.** A different run, or the same run three hours later with less room, steps on it.

**That is the honest answer to Chris's second question. The housekeeping did not break other outputs
on 08-19. It was one obvious retry away from doing so, and nothing in the machine would have flagged
it — not then, and not on any later run, because nothing reads the archives.**

## 3 · Root cause

> **The run performs its ONLY destructive operation at the point where it is most degraded and least
> supervised, using a three-step non-atomic, non-idempotent sequence, against a filesystem whose
> constraints are undocumented — and it does so AFTER the deliverable that would have reported the
> failure.**

**Four properties compound, and each is individually defensible:**

| Property | Why it exists | What it costs |
|---|---|---|
| **It is the run's only DESTRUCTIVE step** | Everything else is additive — append a log, create a draft. Archiving is the only operation that *removes* content from a live file | A bug here loses data; a bug anywhere else duplicates it |
| **It is non-atomic** — append-to-archive, build, overwrite-live | Written as three shell steps because that is how it was first done | A failure between steps leaves the vault inconsistent |
| **It is non-idempotent** — retrying step 1 appends twice | Nobody designed it to be retried | The natural response to failure corrupts the archive |
| **It runs LAST** | It was framed as "cleanup" | It executes at maximum context, minimum attention, and after the report that would have reported it |

🔴 **"Housekeeping" is the wrong mental model and it is doing real damage.** The word implies
low-stakes tidying. **In this machine it names the single highest-risk operation in the run.**
Nothing else can destroy vault content. It should be treated with the care given to a send.

### Contributing: the size rule creates pressure to do it every night

[[method]]'s RUN EFFICIENCY rule fires archiving at ~35 KB. [[sequence-tracker]] crossed it on 08-19
and again after tonight's edits. **A destructive operation on a nightly trigger, with no atomicity,
is a defect waiting on a slow enough night.**

## 4 · Corrective action — this instance

| # | Action | Status |
|---|---|---|
| C1 | Verify no data was lost or duplicated by the 08-19 archival | ✅ **DONE 2026-08-20** — full audit above. No loss, no double-append |
| C2 | Record the 10-line archive overlap so it is not mistaken for corruption later | ✅ **DONE** — documented in §2 |
| C3 | Reproduce and document the `mv`/`rm` filesystem constraint | ✅ **DONE 2026-08-20** — reproduced deliberately; written into [[method]] |
| C4 | Remove the probe file created during reproduction | ⚠️ **PARTIAL.** `rm` is not permitted and Chris declined the delete-permission prompt. **Contents overwritten with a tombstone note; `_probe_target.md` is inert and safe for Chris to delete by hand.** Recorded rather than hidden |

## 5 · Preventive action — ✅ INSTALLED 2026-08-20

### P8 · WRITE-IN-PLACE ONLY. Never `mv` across the sandbox boundary, never `rm` in the vault

**Documented in [[method]] as a dated capability fact, in the same discipline as the Gmail connector
shape.** `cp` to overwrite; `mv` only within the vault; `rm` never works. **When a delete is genuinely
needed, ask via the delete-permission tool rather than reporting it as impossible — and if it is
declined, neutralise the file's contents and tell Chris, rather than leaving unexplained litter.**

### P9 · ARCHIVING IS A SINGLE IDEMPOTENT TRANSACTION, OR IT DOES NOT RUN

**The three-step sequence is replaced by one rule:**

> 🔴 **Build the new live file FIRST, in memory or in `/tmp`. Verify it. Then, and only then, do the
> two writes — archive append and live overwrite — back to back with no other work between them.
> If the archive append succeeds and the live overwrite fails, DO NOT RETRY THE BLOCK.** Re-do only
> the overwrite. **Before any archive append, grep the archive for that run's roll-in header
> (`ROLLED IN FROM … <date>`); if it is already present, the append has happened — skip it.**

**The header grep is the idempotency key.** It is a countable object: *the append either already
happened or it did not*, and the run can tell without judgement.

### P10 · 🔴 ARCHIVING IS NOT HOUSEKEEPING. IT IS A DESTRUCTIVE OPERATION AND IT MOVES.

**Two changes, and the second is the load-bearing one:**

1. **Renamed throughout from "housekeeping" to `DESTRUCTIVE — ARCHIVE ROTATION`.** The word was doing
   real harm: it licensed running the run's only data-destroying step at the point of least attention.
2. 🔴 **It runs AFTER the report is delivered, and a failure there is a reported line, never a dead
   run.** Combined with P5 from [[CAPA-2026-08-20-unreconciled-run-manifest]], the deliverable is now
   strictly upstream of every operation that can fail destructively.

### P11 · Size-triggered rotation gets a floor, so it cannot fire on a degraded run

**Archive rotation runs only when BOTH are true: the file is over ~35 KB AND the run has already
delivered its report.** If the report has not gone out, **rotation is `skipped — report not yet
delivered`** on the run manifest and happens tomorrow. **A file being 40 KB for one extra day costs
nothing. A corrupted archive costs history that cannot be reconstructed.**

### P12 · Verify the splice, don't trust the arithmetic

**After any archive rotation, before reporting it complete:**
- `grep -c` the roll-in header in the archive → **must be exactly 1**
- Spot-check 3 distinct strings from the rolled-out range → **must be present in the archive**
- Confirm the live file's frontmatter and first heading are intact

**The 08-19 splice was off by ten lines because the boundaries were computed by hand and never
checked.** Three greps would have caught it.

## 6 · Effectiveness check

**The next three runs that trigger an archive rotation.** One question against each:

> **Does the archive contain exactly one roll-in header for that date, do the spot-checked strings
> resolve, and was the rotation performed only after the report went out?**

**Pass = one header · all spot-checks resolve · rotation strictly after the report.**
Any double-append, any missing string, or any rotation attempted before the report reopens this CAPA.

## 7 · What this does NOT fix

- **It does not make the scheduled-task edit reliable.** That failure was a tool permission abort,
  not a filesystem problem. **P5 + P10 mean it can no longer take the report down with it** — that is
  the whole claim.
- **It does not shrink the files.** The size pressure is real and rotation still has to happen; it
  just happens at a safer moment.
- **It does not audit the archives already written.** The 08-18 and 08-19 roll-ins were verified here.
  Earlier ones were not, and **no run reads the archives, so an older corruption would still be
  invisible.** A one-off archive integrity pass is worth doing and is **not** scheduled.
