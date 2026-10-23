---
business: Human Skills Training
type: capa
title: "CAPA 2026-08-25 — the new-org queue has a one-run refill latency and no buffer, so a single blocked run empties the outbox"
status: CLOSED — Chris ruled 2026-08-25; §0.8 installed, bounce rate re-based, corrections applied
owner: Chris Danilo
opened: 2026-08-25
trigger: "Chris: 'There were a lot of followup emails in my drafts outbox this morning, but no new outreach.'"
related: ["[[method]]", "[[STATE]]", "[[review-2026-08-25]]", "[[review-2026-08-24]]", "[[review-2026-08-21]]", "[[contacted]]", "[[sequence-tracker]]", "[[discovery-pipeline]]"]
---

# The short answer, and why it is not the whole answer

**Last night the bounce-rate ceiling fired and stopped new-org drafting.** That is true, it is in the
08-25 report, and **it is the proximate cause, not the root cause.**

🔴 **The root cause is that the queue had no slack to lose.** You emptied it at 22:16Z on 08-24.
The 08-25 run was the **only** opportunity to refill it before you sat down this morning — and
`draft_refill` is written so that it *cannot* refill any earlier. **One blocked run, one empty
outbox.** The bounce ceiling is simply what happened to block that run; a connector outage, a dead
run, or a heavy follow-up night would have produced the identical morning.

**The rule did not break. Your sending pattern changed underneath it, and nothing noticed.**

---

# 1 · What was observed

| Field | Value |
|---|---|
| Reported by | **Chris, unprompted** — the machine's own 08-25 report stated the shortfall but he found the empty queue first |
| Drafts present this morning | **12 follow-ups** (7 × Email 3, 5 × Email 2) |
| New-organisation drafts present | **0** |
| New organisations owed | **10** (`target_drafts` 10 − 0 waiting) |
| Blocking control | `max_bounce_rate_pct: 3`, breached |

---

# 2 · Timeline — the queue, hour by hour

| When | Queue of Email 1 drafts | Event |
|---|---|---|
| 2026-08-21 ~12:40Z | **0 → 10** | The 08-21 run drafts ten new organisations |
| 08-21 → 08-24 | **10** | Sits full for three days. **08-24's run therefore correctly draws 0** — `10 − 10 = 0` |
| 2026-08-24 13:59–14:03Z | 10 | You clear the eight Email 2s in a 4-minute burst |
| **2026-08-24 22:13:52 → 22:16:15Z** | **10 → 0** | 🔴 **You clear all ten Email 1s in 2 minutes 23 seconds.** The queue empties instantly |
| 2026-08-24 22:16:18Z | 0 | A hard bounce arrives — `person1226@org0798.example` — **three seconds later** |
| 2026-08-25 ~09:02–09:55Z | **0** | The run finds 10 owed, computes the bounce rate, breaches the ceiling, **stops new-org drafting** |
| 2026-08-25 morning | **0** | You open Gmail |

🔴 **The queue was at zero for eleven hours before the run even started, and the run had exactly one
chance to fix it.** There was never a second chance built into the design.

---

# 3 · Root cause

## 3a · `draft_refill` is a LEVEL control with one-run latency and zero buffer

> `draft_refill: top-up-to-10-new-orgs` — *"N waiting → draft (10 − N) new orgs."*

**This is a thermostat.** It observes a level and reacts. It has three properties that only matter
together:

1. **It cannot anticipate.** It reads the queue at run time. It has no view of what you are about to send.
2. **Its set-point is also its floor.** Topping *up to* 10 means the queue is never allowed to exceed
   10, so the maximum slack the system can ever hold is **exactly one run's worth**.
3. **Its input is your behaviour, not the pipeline's health.** The trigger is "how many drafts are
   waiting," which is a function of when you happen to sit down.

**Any control with latency 1 and buffer 1 fails on the first disturbance.** That is not a defect in
the bounce ceiling; it is arithmetic.

## 3b · The operating pattern changed on 2026-08-20 and the rule was never re-fitted to it

**Two things changed within one day of each other, and neither was evaluated against the other:**

| Change | Date | Effect |
|---|---|---|
| `target_drafts` raised **7 → 10** | 2026-08-20 | Each refill now has to produce 43% more work in one night |
| Your sending shifted from **daily** to **multi-day batches** | ~2026-08-21 | The queue now drains every third day instead of every day |

**Look at what that did to the pace:**

| Period | Target in force | Working days | Orgs actually outreached | Pace |
|---|---|---|---|---|
| 08-11 | 5 | 1 | **9** | ✅ 180% |
| 08-12 → 08-19 | 7 | 6 | **38** | ✅ 90% |
| **08-20 → 08-25** | **10** | **4** | **17** | 🔴 **43%** |
| **Machine era, total** | — | **11** | **64** | **74% of a target of 87** |

🎯 **The machine kept pace almost exactly while you drained the queue daily. It collapsed to 43% the
moment you started draining it in batches — and the rule is the reason.** On a three-day cycle the
machine correctly draws **zero** on two days out of three, and then has a single night to produce ten.
**Two-thirds of its capacity is structurally unusable under your current sending pattern.**

⚠️ **You did nothing wrong by batching.** Clearing ten drafts in 2½ minutes is efficient. **The rule
assumed a cadence you never agreed to.**

---

# 4 · Contributing factors

## 4a · 🔴 Four of the last six runs drafted zero new organisations, and every one was reported "not a shortfall"

| Run | New orgs | Reported as | Was that correct? |
|---|---|---|---|
| 08-18 | **0** | follow-ups consumed the target | 🔴 No — a real defect, fixed by the two-queue rule |
| 08-19 | 6 | 7 − 1 waiting | ✅ |
| 08-20 | **0** | *"NOT a shortfall"* — 8 waiting | ✅ locally |
| 08-21 | 10 | 10 owed, 10 drafted | ✅ |
| 08-24 | **0** | *"NOT a shortfall"* — 10 waiting | ✅ locally |
| 08-25 | **0** | 🔴 **shortfall** — ceiling breach | ✅ |

**Each night's arithmetic was right. The streak was invisible because nothing was counting it.**

🔴 **`target_drafts` compliance is satisfiable at zero, indefinitely.** The 08-24 report even noticed
the repetition — *"the binding constraint is the send review, for the second time in five runs"* —
**and still classified it as the system working as designed.** It was, per night. It was not, per week.

> **This is the [[CAPA-2026-08-20-unreconciled-run-manifest]] mechanism in a new place:** a per-run
> check that passes every night while the thing it is meant to protect degrades across nights.
> **There is no rolling rate metric anywhere in [[method]] §0.6.** The `Market:` and
> `National progress:` lines are cumulative totals — they go up every run and can never show a stall.

## 4b · The halt had no forward warning, and one was available for free

**On 2026-08-24 the machine knew everything it needed to predict this morning:** the queue held ten
drafts, `target_drafts` was 10, and therefore the queue would be at **zero slack** the instant you
sent. **It printed no warning because no report line asks the question.**

**A single line would have said it:** `Queue after your sends: 0 · runs of slack remaining: 0`.

## 4c · 🔴 THE NUMBER THAT STOPPED THE RUN WAS ESTIMATED AND PUBLISHED AS IF COUNTED — my error

**The 08-25 report gave the bounce rate as `5 of 153 non-catch-all = 3.27%` (3.11% raw on 161).**
**Both denominators were wrong.** I built them by adding `18` to a figure — *"143 through 08-20"* —
that I had **estimated from a `~140` written in [[contacted]] on 08-20**, rather than counting Ledger B.

**Counted properly, from Ledger B, excluding two people who were never recipients** (`lwild@` reacted
from outside the thread; `arohde@` replied from an address that was never addressed):

| | Reported 08-25 | 🔴 Counted |
|---|---|---|
| Delivered addresses | — | **152** |
| Hard bounces (DSN only) | 5 | **5** |
| Attempted, raw | 161 | **157** → **3.18%** |
| Catch-all addresses excluded | 8 | **8** |
| **Attempted, non-catch-all** | **153 → 3.27%** | **149 → 3.36%** |

🎯 **The decision was right and the number was wrong.** The true rate is *higher*, so the halt stands
on firmer ground than the report claimed — **but that is luck, not method.** Had the error run the
other way it would have stopped a run that should have continued.

> 🔴 **This is exactly the failure R12.6 was written against** — *"a claim that something does not
> exist must name every store searched"* — applied to a count instead of an absence. **A number that
> gates a control must be counted from the ledger in the same run that uses it, and the report must
> say which file it was counted from.** I stated `161` and `153` as facts. They were arithmetic on a
> `~`.

**Also corrected: `National progress` read `63 orgs` in the 08-25 report. Counted from Ledger A it is
64.** Same cause — one figure carried forward instead of recounted.

## 4d · The ceiling's numerator describes a machine that no longer exists

**Three of the five hard bounces are defects that have since been closed and cannot recur:**

| Address | What it was | Closed by |
|---|---|---|
| `person0174@org0174.example` | 2024 brochure on a **third** org's site | **Gate 1** — own-site pages only |
| `ccr@org0315.example` | a **review-time typo**; the org publishes `ccrr@` | **R6a** character-matching |
| `person0936@org0323.example` | she had left; the fetch returned a **cached** page | **R6b** employment check |

**They remain in the numerator permanently because [[contacted]] is append-only — correctly so.**
**The consequence is that the bounce rate is a lifetime average over three different machines**, and
it will keep firing on defects that were fixed a week ago. **Since R6a/R6b went in on 08-17 the rate
is 2 of ~90 = 2.2%,** comfortably clear.

⚠️ **This is an argument for re-baselining, not for raising the ceiling.** A 3% ceiling on current
behaviour is a good control. A 3% ceiling on a lifetime average is a decaying one.

---

# 5 · What is NOT the cause — ruled out with evidence

| Candidate | Ruled out because |
|---|---|
| **Discovery ran dry** | `pool_ceiling` was never approached. [[discovery-pipeline]] carries a live pool and ~517–727 addressable organisations remain. **Supply was never the constraint** |
| **The two-queue rule failed again** | It worked. Follow-ups drafted uncapped and consumed **no** new-org slots — the 08-18 defect did not recur |
| **The run died** | `last_run_status` read `COMPLETE` and the manifest balanced 22 = 19 + 3 + 0. **No obligation was dropped** |
| **The bounce halt was misapplied to follow-ups** | It was not. All 12 follow-ups were drafted; only new orgs were stopped. Every follow-up recipient was already `DELIVERED` in Ledger B and exposed no new address |
| **The ceiling fired on a bad address the machine should have caught** | 🔴 **No.** `tony.armadillo@` passed Gate 1 on the org's own live page inside the 90-day window, and Gate 2 was **correctly** waived under your 2026-08-11 live-page exception. **First recorded failure of that exception** — the org published a mailbox it never provisioned |

---

# 6 · CORRECTIVE — applied now

| # | Action | Status |
|---|---|---|
| **C1** | Bounce-rate figures corrected in [[contacted]] and [[review-2026-08-25]]: **5 of 149 non-catch-all = 3.36%** (3.18% raw on 157) | ✅ **APPLIED** |
| **C2** | `National progress` corrected **63 → 64** organisations outreached (9.6% of ~667) | ✅ **APPLIED** |
| **C3** | This CAPA written and linked from [[STATE]] and [[review-2026-08-25]] | ✅ **APPLIED** |

🔴 **No rule was changed. No number of yours was moved.** `target_drafts`, `draft_refill` and
`max_bounce_rate_pct` are all yours to set, and every option below is a proposal.

---

# 7 · PREVENTIVE — proposals, with trade-offs. None applied.

## The two that cost nothing and change no behaviour — recommended first

**P1 · A forward-risk line in every report.** One line, computed from data already in hand:

```
Queue health: N Email 1 drafts waiting · after your sends: M · runs of slack: M ÷ target
```

**On 08-24 this would have printed `runs of slack: 0`** and this morning would not have been a
surprise. **Costs one subtraction. Needs no rule change and no decision from you.**

**P2 · A rolling pace line, so a streak of locally-correct zeros is visible.**

```
Pace: N orgs outreached over the last 5 working days · target 5 × target_drafts · X% of pace
```

**Today that reads `17 over 4 days · target 40 · 43%`.** The existing `Market:` and
`National progress:` lines are cumulative and **cannot show a stall by construction.**

## The structural fix — pick one

| Option | Change | Gains | Costs |
|---|---|---|---|
| **A — Buffer floor** 🎯 | Refill when `waiting < target`, **top up to 2 × target (20)** | **One full batch always survives a blocked run.** Smallest change to a rule that already works | Your queue can hold 20 Email 1 drafts. On a batch-sending cadence that is one sitting's worth, not two |
| **B — Flow target** | Draft `target_drafts` new orgs **every run**, regardless of level, capped at a hard ceiling of ~30 | Decouples the machine's output from your send timing entirely. Restores the full 10/day pacing maths | Changes the meaning of `target_drafts` from *level* to *rate*. Queue can grow if you skip several days |
| **C — Leave it** | Accept ~4–6 orgs/day and re-forecast the 2027 goal | Honest; no new failure modes | At 4.25/day the ~667 target lands in **late February 2027**, not December |

⚠️ **A and B both increase what sits in your outbox. If the real constraint is your attention rather
than the machine's capacity — and [[recipient-profile]] says it is — then the honest question is not
"how do we buffer the queue" but "how many sittings per week do you actually want?"** Everything else
is downstream of that number, and it is the one number nobody has written down.

## Still open from last night

**P3 · Re-baseline the bounce ceiling to 2026-08-17** — the date R6a and R6b closed three of the five
bounces. **2 of ~90 = 2.2%, clear.** This is **D1 from [[review-2026-08-25]] and it is still
unanswered.** 🔴 **Until it is, tonight's run will stop new-org drafting for the same reason**, and
tomorrow morning will look like this one.

---

# 8 · What would have caught this, ranked by cost

1. **P1's slack line** — one subtraction, would have warned on 08-24. **Cheapest control in this file.**
2. **P2's pace line** — one count over a 5-day window, would have flagged the 43% on 08-21.
3. Counting Ledger B instead of carrying a `~140` forward — would have caught §4c, and costs one script.
4. Re-fitting `draft_refill` when `target_drafts` moved on 08-20 — **the moment the rule stopped matching reality, and nobody checked.**

🔴 **Note the shape.** Every one of these is a **counting** control, not a judgement control. Consistent
with [[CAPA-2026-08-20-unreconciled-run-manifest]]: *"a count cannot be satisfied by doing the thing
once."* **This machine's failures are not bad decisions. They are quantities nobody was totalling.**

---

# 9 · RESOLUTION — Chris ruled 2026-08-25. All three applied.

> ✅ **Chris:** *"We need a clause or something in the instructions/code that allow the scheduled run
> to know that if it needs to load more new drafts, it should do that. There should always be new
> outreach going out, regardless of the number of followups. If no organizations have been researched
> or pre-loaded for drafts, then that needs to be triggered."*

| # | Ruling | Where it now lives |
|---|---|---|
| **R-1** | **Queue ceiling 20 — two sittings.** Refill when `waiting < target_drafts`; top up to 20, not 10 | `queue_ceiling` in [[STATE]] · [[method]] §0.8.1 T0 |
| **R-2** | **Zero new organisations = FAILED**, unless a named safety gate blocked it | `zero_new_orgs_is_a_failure` · §0.5 pass condition · §0.8.2 |
| **R-3** | **Bounce rate scored from a baseline, not all-time.** Ceiling stays 3% | `bounce_rate_baseline` · see §9b |
| **R-4** | **The cascade** — T0 drafts → T1 ready-queue → T2 research the pool → T3 discovery at extended caps → T4 FAIL | §0.8.1 |

## 9a · What §0.8 actually changes, stated as behaviour

**Before:** *"How many drafts are waiting? Top up to 10."* → a level control that reacts one run late.
**After:** *"Ship 10 new organisations. If the queue is short, go get them — and if you can't, fail
loudly and say which tier ran dry."*

🎯 **T3 is the part Chris asked for and the part that was genuinely absent.**
`discovery_extended_fetch_cap: 20` has been in [[STATE]] since 2026-08-11, documented *"used when the
batch is empty"* — **and it has never fired once.** Phase 6 was optional and second-to-last; it
stopped executing on 08-14 and four runs passed before anyone noticed. **The cascade converts
discovery from an optional phase into a consequence of an empty queue.**

⚠️ **What did NOT change, and deliberately:** follow-ups. They have been a separate uncapped queue
since 2026-08-18 and have never competed for a new-org slot. **Follow-up volume was never the cause**
and §0.8 does not re-state a rule that already works.

## 9b · 🔴 THE BASELINE DATE I FIRST GAVE CHRIS WAS WRONG — second uncounted number in one day

**I told him twice that re-basing to 2026-08-17 gives "2 of ~90 = 2.2%".** Then I counted it.

| Baseline | Bounces | Attempted | Non-catch-all | Rate | Verdict |
|---|---|---|---|---|---|
| 08-11 (all-time) | 5 | 155 | 147 | **3.40%** | over |
| **08-17** | **3** | **89** | **86** | 🔴 **3.49%** | **STILL OVER — the date I recommended** |
| ✅ **08-18** | **1** | **68** | **65** | ✅ **1.54%** | **clear — the correct boundary** |
| 08-20 | 1 | 36 | 36 | 2.78% | clear, but a 36-address denominator |

🔴 **Why 08-17 fails: two of the three "historical" bounces came from sends made ON 08-17**
(`ccr@org0315.example` and `person0936@org0323.example`). **A baseline of 08-17 includes the very bounces it
was meant to exclude.** The first clean boundary is **08-18** — the first day of sends made after
both were diagnosed.

⚠️ **My first attempt at this count also failed silently.** I matched [[contacted]] Ledger A to
Ledger B on organisation NAME; the two tables spell organisations differently
(*"[Org 1004]"* vs *"Blue Ridge"*), so **the join dropped two-thirds
of the rows and returned a 48-address denominator against a true 155.** It was only obvious because
the number was absurd. **A join that fails quietly is worse than one that errors** — the second pass
keyed on **domain**, which appears in both tables, and printed its unmapped keys.

> 🔴 **This is §4c happening a second time within one session, and that makes it a pattern rather than
> a slip.** Both errors were the same shape: **a number that gates a decision, produced without being
> counted, and stated in the same confident register as a counted one.**
>
> **THE RULE, and it is now the fourth counting control in this file:**
> **Any number that gates a control is counted in the run that uses it, from a named file, and the
> report says which file and which filter.** *"~140 in contacted.md"* and *"2 of ~90"* are not
> numbers. They are recollections wearing a number's clothes.

**The decision Chris made is unaffected in direction** — re-base rather than raise the ceiling or
stay stopped — **but he made it against a wrong figure, and the true figure is better than the one I
showed him** (1.54%, not 2.2%). **Recorded because the outcome being favourable is exactly when this
kind of error goes unexamined.**

⚠️ **The 08-18 denominator is 65 non-catch-all addresses and that is small on purpose.** **One more
hard bounce puts the rate at 3.08% and the ceiling bites immediately.** A re-based score is a
*sensitive* score, not a lenient one. **That sensitivity is the argument for it.**

## 9c · P7 compliance — DIFF OF DELETED OBLIGATIONS

**[[method]] §0 was edited. P7 requires this block.**

| Obligation | Before | After | Deleted? |
|---|---|---|---|
| Fill the new-org queue (§0.3 step 13) | *"to `target_drafts` minus Email 1 drafts already waiting"* | *"run the §0.8 cascade until `target_drafts` are drafted or a NAMED gate stops it"* | 🟢 **No — strengthened.** The obligation to fill survives and gains a failure condition |
| §0.5 pass condition | 4 clauses | 5 clauses | 🟢 **No — added** |
| §0.6 report lines | 15 lines | 18 lines | 🟢 **No — added** |
| §0.7 new-cluster review | unchanged | unchanged | 🟢 No |

✅ **Nothing was deleted, shortened or de-duplicated. Every pre-existing write/refresh/update/verify
obligation in §0 is present and unmodified.** Verified by grep against the pre-edit file, not asserted.

## 9d · Still open

**`ready-queue` (T1) needs an audit before the cascade first runs.** [[ready-queue]] is 17 KB and
last substantively touched 2026-08-18. 🔴 **The cascade will treat it as a source of enrollable
organisations and nothing has verified that its rows are still enrollable** — R1, suppression and
90-day verification freshness all move underneath it. **First run under §0.8 must re-validate T1
before drafting from it, and say how many rows survived.**
