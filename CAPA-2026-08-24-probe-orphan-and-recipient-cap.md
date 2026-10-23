---
business: Human Skills Training
type: capa
title: CAPA 2026-08-24 — an orphaned probe draft, and a 4-recipient draft that broke the cap
status: DIAGNOSED — one cleanup executed, no rules applied
owner: Chris Danilo
opened: 2026-08-24
trigger: "Chris supplied two screenshots: a surviving NIGHT SHIFT CAPABILITY PROBE draft, and the [Org 0546] Email 2 compose header showing four recipients against a three-name greeting"
related: ["[[method]]", "[[STATE]]", "[[review-2026-08-24]]", "[[review-2026-08-21]]", "[[CAPA-2026-08-18-unqueried-tier1-roster]]", "[[CAPA-2026-08-20-unreconciled-run-manifest]]"]
---

# Two defects, one family

**Both are cases where the machine HAD the authority to act correctly and deferred instead** — once to
a cleanup step that never ran, once to Chris's review. **Neither was a missing rule. Both were an
available action not taken.**

🔴 **One cleanup was executed** (the probe draft is trashed — it was the machine's own litter and its
own body promised its removal). **No rule was changed. No method file was edited.**

---

# DEFECT 1 · The probe draft that promised its own deletion and survived three days

## What was found

| Field | Value |
|---|---|
| Subject | `[NIGHT SHIFT CAPABILITY PROBE — delete] multi-recipient array test 2026-08-21` |
| Draft / message | `r2797419477732116534` / `<thread-id>` |
| Created | **2026-08-21T12:34:48Z** |
| Found | **2026-08-24 — three days and four runs later** |
| To | `<PERSONAL_EMAIL>` · `<SENDER_EMAIL>` *(self-addressed)* |
| Labels | **`DRAFT` only — no `Label_2`** |
| Body, verbatim | *"Automated capability probe for CI-024 (Gmail multi-recipient regression). Not for sending. **This draft is trashed by the same run that created it.**"* |

**It was the 08-21 shape test.** Created 12:34:48Z; the ten Email 1 drafts followed at 12:36:49–12:40:40Z.
[[method]] requires it: *"FIRST WRITE OF EVERY RUN IS A SHAPE TEST."* **The probe did its job.
Only its disposal failed.**

## Root causes — three, layered

### 1a · 🔴 The artifact asserts a future event as an accomplished fact

**The body says the draft "is trashed by the same run that created it." It was not.** The sentence was
true as an *intention* and false as a *statement*, and it was written into a permanent artifact before
the thing it describes had happened.

> 🔴 **This is [[method]] R12.6 — *"a claim that something does not exist must name every store
> searched"* — pointed at the future instead of the past.** The same discipline applies: **a
> capability probe may describe what it IS, never what will subsequently be done to it.**
> The correct body names the run and says *"delete on sight if you are reading this"* — which converts
> a broken promise into a working instruction to whoever finds it.

### 1b · 🔴 IT WAS INVISIBLE TO EVERY SWEEP THAT SHOULD HAVE CAUGHT IT — and that is structural

**Four orphan-recovery passes ran while this draft sat there** (08-21 resumed, 08-24 morning, and two
mid-day reconciliations). **None saw it. Neither scope could.**

| Sweep | Scope as written | Why it missed |
|---|---|---|
| [[method]] Phase 4 orphan recovery | *"`list_drafts` → **every thread carrying `CCR&R outreach`**"* | 🔴 **The probe carries no `Label_2`.** It is outside the defined scope **by construction** |
| This run's own passes (×3) | `list_drafts` with `query: subject:"Question about PD"` | 🔴 **A filtered query. A sample, not a sweep** |

> 🔴 **THIS IS R12.1 RECURRING IN A NEW PLACE, AND I COMMITTED IT THREE TIMES TODAY.**
> R12.1 exists because bounce detection sampled *"the threads with follow-ups due"* and missed two real
> bounces across three runs. The lesson was written down as **"a sample is not a sweep"** and the
> bounce query was made mailbox-wide. **The DRAFT sweep never got the same treatment** — and
> [[method]]'s own wording (*"every thread carrying `CCR&R outreach`"*) actively instructs a filtered
> scope. **The machine created an artifact deliberately outside the label scope, then swept only
> inside it.**

**The generalisable form: a cleanup sweep must be scoped WIDER than the thing being cleaned up, never
equal to it.** An orphan is by definition an object that fell out of its expected category — **so
scoping orphan recovery to that category cannot work.**

### 1c · The blast radius was small but the placement was bad

**Sending it would have been harmless** — it is addressed to Chris. But it sat in the Drafts folder for
three days **with a Send button, beside real client drafts, during a window in which Chris was
explicitly clearing at speed** (*"I have to send them out today and I don't have time"*).
⚠️ **And the screenshot shows HubSpot `Log 1/1` and `Track` both ON**, so a mis-send would have written
a tracked CRM record against Chris's own address.

**The machine put a zero-value object with a live Send button into a queue it knows a human clears
fast.** That is a placement error independent of the low consequence.

## ✅ Action taken

**Trashed** (`<thread-id>`). **Drafts folder verified empty** immediately afterward.

## Candidate controls — NOT APPLIED

| # | Candidate | Closes |
|---|---|---|
| **1** | 🎯 **Orphan recovery sweeps ALL drafts, unfiltered** — `list_drafts` with no query, then classify. **The R12.1 fix applied to drafts** | 1b, and it is the one that would have caught this |
| **2** | 🎯 **The probe body may not describe its own disposal.** Replace with: *"Automated shape test, run YYYY-MM-DD. If you are reading this, the run failed to delete it — delete on sight."* | 1a. Turns a broken promise into a working instruction |
| **3** | **Label the probe `Label_2` at creation** so it falls inside the existing sweep even if #1 is rejected | 1b, cheaply |
| **4** | **Verify the trash and report it**: the run's report carries `Probe: created <id> · trashed ✅` — a countable object, per this file's own doctrine that counted rules fire and remembered ones do not | The whole defect |
| **5** | **Probe against a thread the run already owns, or skip the probe** when the first real draft can serve as the shape test — which it can, since [[method]] says *"make it a real draft you needed anyway"* | Removes the artifact entirely. **[[method]] already prefers this and the 08-21 run did not follow it** |

🔴 **Candidate 5 deserves emphasis: [[method]] already says the shape test should be a real draft.**
*"FIRST WRITE OF EVERY RUN IS A SHAPE TEST. **Make it a real draft you needed anyway**, read it back
with `list_drafts`, and record which shape worked."* **The 08-21 run created a synthetic probe instead —
against the written rule.** Had it followed the rule, no orphan could exist.

---

# DEFECT 2 · A four-recipient draft with a three-name greeting

## What was found

**The [Org 0546] Email 2 draft this run created at 09:10:32Z:**

```
To:  person0485@org0319.example
Cc:  person0784@org0319.example, person0560@org0319.example, person0684@org0319.example
     → FOUR recipients
Greeting: "Hey [Person 0227], Lashonda, and Katy,"
     → THREE names. jagnew@ ([Person 0284]) is on the email and named nowhere.
```

✅ **It never reached a prospect in that state.** Chris removed `jagnew@` at review and sent to three
(`<thread-id>`, 14:02:23Z), with the greeting then matching. **But he had to do it by hand, and
the machine had both the authority and the obligation to do it first.**

## Root causes — two rule breaks and one ambiguity

### 2a · 🔴 The hard recipient cap was broken

> **[[method]], quoting Chris 2026-08-11:** *"Let's agree that it's 1 person in the 'to' field and up
> to two people in the CC field."* · **"Three people on a thread, never four. More than that reads as
> a blast rather than a note."**

**The draft had four.** Not a preference — a cap Chris set by quote.

### 2b · 🔴 The greeting and the recipient field disagreed

[[method]] documents this exact class from 2026-08-18: *"A greeting naming someone who is not a
recipient is a visible defect in front of a prospect."* **This is the inverse — a recipient the
greeting does not name — and it is the same integrity failure.** The card even flagged it
(`Redundancy: 4 of 3`), which proves the machine **saw** it.

### 2c · 🔴 THE ACTUAL ROOT CAUSE — a convenience rule was allowed to override a hard cap

**The reasoning the run used:**
1. `followup_recipients: inherit-from-email-1` — reuse the Email 1 set **as sent**
2. **R5** — recipients are fixed at Email 1; adding is forbidden
3. ∴ inherit all four; raise the greeting as a question (**D3**)

**Step 3 does not follow, and here is the hole:**

> 🔴 **R5 forbids ADDING. It is silent on REMOVING — and R5's own table says so explicitly:**
> *"A recipient **bounced** → ✅ Remove them + the parenthetical (R2). **Removing is fine; adding is
> not.**"*

**So the authority to drop `jagnew@` and return to three was already written down, in the same rule
the run cited as its reason not to.** R2 removes bounced addresses routinely; nothing restricts
removal to bounces.

**The mechanism, stated generally because it will recur:** `inherit-from-email-1` is a **convenience**
rule — it exists so follow-ups need no re-verification. The 1-To/2-Cc cap is a **hard** rule Chris set
by quote. **Nothing in [[method]] states which wins when they collide, and the run let the convenience
rule win.** That silence is the defect.

### 2d · The compounding error — a violation was reported as a question

**D3 asked:** *"Who is [Person 0284], and should the greeting say her name?"* — framing a **cap breach**
as a **naming preference**, and offering a default (*"greeting stays as-is"*) that **preserved the
violation**.

🔴 **[[method]] Phase 5 says a recipient Chris changes is a defect report against the machine.**
**This inverts it: the machine handed Chris its own defect as a decision to make.**
**The correct handling was: drop to three, state on the card who was dropped and why, and let Chris
add her back if he wanted her.** Fail-closed, which is the standing posture.

## Where it came from — and the miss is older than today

**Email 1, as Chris sent it on 2026-08-14, already carried four recipients and a three-name greeting.**
So the machine **inherited** the defect — **but then propagated it for ten days across two emails
without once naming it a cap violation.**

| Run | Opportunity | Outcome |
|---|---|---|
| 2026-08-14 | As-sent reconciliation should have flagged 4 recipients against a cap of 3 | 🔴 missed |
| 2026-08-21 | Email 2 drafted for this cohort *([Org 0546] carried, not sent)* | 🔴 missed |
| 2026-08-24 | Draft rebuilt by this run | 🔴 **seen and not acted on** |

⚠️ **The as-sent reconciliation records what Chris sent but does not VALIDATE it.** R13 fans the
as-sent set out to four stores; **no step asks whether the as-sent set is legal.** A human-introduced
cap breach therefore enters the record as ground truth and propagates.

## Candidate controls — NOT APPLIED

| # | Candidate | Closes |
|---|---|---|
| **1** | 🎯 **State the precedence explicitly in [[method]]: the 1-To/2-Cc cap OUTRANKS `inherit-from-email-1`.** When an inherited set exceeds the cap, **drop the lowest-ranked recipient under R4** and name the drop on the card | 2c — the root cause |
| **2** | 🎯 **A greeting/recipient parity check before any draft is created**: every recipient is named in the greeting, and every name in the greeting is a recipient. **Mismatch → HOLD, not a question.** Arithmetic, not judgement | 2b, both directions |
| **3** | **Validate the as-sent set, don't just record it.** R13's fan-out gains one test: does the as-sent set satisfy the cap? A breach is reported as a finding about the *thread*, not a correction to Chris | The 08-14 miss and its propagation |
| **4** | **A cap breach is never a `D`-item.** Hard rules get enforced and reported; only genuine judgement calls go in the decisions table | 2d |

---

# What the two defects share

**In both cases the machine had a correct, cheap, available action and did not take it:**

| | Available action | What happened instead |
|---|---|---|
| **Probe** | One `trash_message` call | Deferred to a step that never ran, then swept with a scope that could not see it |
| **Duval** | Drop one Cc, name it on the card | Deferred to Chris's review as an open question |

🔴 **Neither needed a new rule. Both needed an existing one to be used.**
**And in both cases the machine's own artifact recorded the problem** — the probe body described the
deletion, the Duval card printed `Redundancy: 4 of 3` — **so the information was present and
unactioned.** *Seeing it is not the hard part. Acting on it is.*

⚠️ **Consistent with this machine's whole documented history:** every rule that fires reliably is
attached to a **countable object that blocks an artifact from existing**; every rule that fails to
fire is a judgement with no object. **`Redundancy: 4 of 3` is a count that blocks nothing.**
Candidate control 2 above turns it into one.
