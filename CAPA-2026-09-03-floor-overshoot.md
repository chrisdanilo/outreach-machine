---
business: Human Skills Training
type: capa
title: "CAPA 2026-09-03 — the run drafted 15 new organisations against a prescribed 10, and no rule said stop"
status: proposed — awaiting Chris's ratification
owner: Chris Danilo
raised_by: Chris ("why there were 15 new thread drafts in my outbox this morning instead of the normal, prescribed number")
related: ["[[method]]", "[[review-2026-09-03]]", "[[dossier-2026-09-03]]", "[[PROPOSAL-2026-09-03-systematic-territory-model]]", "[[CAPA-2026-08-25-empty-new-org-queue]]", "[[CAPA-2026-08-24-generic-inbox-descent]]"]
---

# CAPA — a floor with no ceiling, and a report that called the overshoot a win

## 1 · What happened

`config.target_drafts` is **10**. The 2026-09-03 run drafted **15** new organisations — 50% over —
and Chris found 15 first-contact threads in his outbox on a morning that also carried 15 follow-ups.
**30 drafts total.**

The run did not report this as an exception. It reported it as an achievement:

> *"🔴 FLOOR MET AT 150% — 15 of 10, no gate"* — `STATE.last_run_status`, written by the run
> *"Outreach floor: 54 carded · 15 drafted · target 10 · cascade tier reached: T3 · gate: none"* — the mandated report line
> *"MET at 150%, no gate needed"* — `dossier-2026-09-03.md` §5

🔴 **Nothing in the run's own output treated 15 as a problem, because nothing in §0 says it is one.**

---

## 2 · Root cause — three clauses, three different answers, no precedence

§0 states the nightly new-organisation count **three times** and they do not agree.

| # | Clause | Location | What it says the number is |
|---|---|---|---|
| **A** | `while new_orgs_drafted < target_drafts:` | §0.8.1a, the cascade loop | 🔴 **Exactly 10.** The loop exits the moment the count reaches `target_drafts` |
| **B** | *"Refill when `waiting < target_drafts`, **top up to `queue_ceiling`**"* | §0.8.1, the T0 row | **18.** 2 were waiting; `queue_ceiling` is 20 |
| **C** | *"`new_orgs_drafted >= target_drafts`"* | §0.5, the pass condition | **10 or more, unbounded.** 15 passes. So does 50 |

**The run followed C.** C is the pass condition — the thing that decides whether the night succeeded —
so it is the clause with the most gravitational pull on behaviour. **A is the operative instruction
and it is stricter, and the run read straight past it.**

🔴 **This is the §0.1 defect class, exactly.** §0.1 exists because on 2026-08-24 a level-4 convenience
rule beat a level-2 hard limit and shipped a four-recipient draft, *and nothing said which won*.
Tonight three clauses of the **same section** disagreed and nothing said which won. **§0.1 ranks rules
by CLASS. It has no answer when two rules of the same class contradict each other.**

### 2b · The deeper cause: §0.8 is armoured on one side only

Read §0.8 end to end and count the controls:

| Control | Guards against |
|---|---|
| The floor (§0.8) | drafting **too few** |
| The cascade T0→T4 (§0.8.1) | drafting **too few** |
| The loop (§0.8.1a) | drafting **too few** |
| The named gates (§0.8.2) | stopping early **without a reason** |
| Score-the-attempt (§0.8.3) | hitting the number with **bad recipients** |
| The slack line (§0.8.4) | the queue running **dry** |

🔴 **Six controls. All six point the same way.** Not one of them asks whether the run drafted too
many. That is not an oversight — it is history. §0.8 was installed 2026-08-25 after
[[CAPA-2026-08-25-empty-new-org-queue]] found **four of six runs had drafted zero new organisations
and every one of them passed.** The section was built in an emergency, to fix starvation, and it
worked. **Nobody wrote the other half, because at the time there was no other half to write.**

⚠️ `queue_ceiling: 20` looks like the missing ceiling and is not. It governs the **queue** — total
Email 1 drafts waiting — and Chris installed it (2026-08-25) so that *"one full batch always survives
a blocked run."* **It is a buffer control, not a workload control.** Read as a per-run instruction it
makes the problem worse, not better: clause B above would have had the run draft 18.

### 2c · Chris's own words define a RATE, and the machine stored it as a FLOOR

> ✅ **Chris, 2026-08-20, raising it 7 → 10:** *"I was thinking of **10 new outreaches a day**. So that
> would mean 10 new organizations."*

**"10 a day" is a rate.** `STATE` records it under the key `target_drafts` — *target*, not *minimum* —
and then §0.8 renamed it "the floor" in prose. **The word changed and the intent did not travel with
it.** Every clause written after 2026-08-25 inherited the floor reading.

### 2d · The report rewarded it

The mandated §0.6 line is `Outreach floor: N carded · N drafted · target N`. **Printing an actual
beside a target invites a ratio**, and the run duly wrote "150%" three times across three artifacts.
🔴 **A metric that renders overshoot as a percentage is a metric that asks to be maximised.**

---

## 3 · Why no control caught it

| Control | Why it was silent |
|---|---|
| `bin/preflight.py` | Per-draft assertions. It has no view of the batch size |
| `bin/run_integrity.py` | Checks that declared outputs **exist** and agree. Never asks whether there were too many |
| `bin/queue_health.py` | Printed `runs of slack: 1.5` — the overshoot, correctly measured, **and read as healthy** |
| §0.5 pass condition | `>=`. **The overshoot is what the pass condition is written to reward** |
| The run manifest | Counts obligations completed, not volume produced |

🎯 **The clearest evidence that this was invisible from the inside:** `queue_health.py` printed the
number that proves the overshoot, in the report, and the run quoted it approvingly.

---

## 4 · The cost

**Real, and paid in the only currency that is actually scarce here: Chris's hands and attention.**

Each Email 1 requires him to drag in `HST_WorkshopInAction.gif` inline, attach `HST_Flyer.pdf`, and
eyeball three recipients he has never seen before. **Five extra organisations is five extra rounds of
that, on a morning that already carried 15 follow-ups.**

| | Prescribed | Delivered |
|---|---|---|
| New organisations (hand-attached, unfamiliar recipients) | 10 | **15** |
| Follow-ups (no attachments except Email 3, known recipients) | 15 | 15 |
| **Total drafts in the outbox** | **25** | **30** |

⚠️ **And the marginal five were the weakest five.** §0.8.3's logic runs in reverse here: the cascade
ranks candidates, so organisations 11–15 are by construction lower-quality than 1–10. Two of tonight's
15 shipped at **Redundancy 1 of 3**, and one is the first Cloudflare-decoded card the machine has ever
produced. **Overshoot does not just add volume, it dilutes the batch** — and it spent Chris's scarcest
attention on the least-verified cards.

🔴 **The compounding cost is in [[PROPOSAL-2026-09-03-systematic-territory-model]]:** the same
unbounded-count pressure is what sent the run across **nine states in one night**. Volume overshoot
and territory scatter are **one defect with two symptoms** — a floor with no ceiling, chased across a
geography with no order.

---

## 5 · Corrective action — PROPOSED, not applied

🔴 **Nothing in this section has been applied.** It changes a gate and a pass condition; Chris ratifies.

### C1 · Make the count a BAND, and say which clause wins

```json
"target_drafts": 10,
"max_new_orgs_per_run": 10,
"_max_new_orgs_why": "🔴 Chris 2026-08-20 defined this as a RATE — '10 new outreaches a day' — and §0.8 stored it as a floor. A floor with no ceiling produced 15 on 2026-09-03. This key is the ceiling. When it and queue_ceiling disagree, THIS ONE WINS: queue_ceiling governs the buffer, this governs Chris's hands, and hands are the scarcer resource."
```

**§0.5 gains one clause:**
> 🆕 **AND `new_orgs_drafted <= max_new_orgs_per_run`.** Exceeding it is a FAILED pass condition, not
> a strong night.

**§0.8.1 T0 row is corrected** so B stops contradicting A:
> **Refill when `waiting < target_drafts`. Draft `min(target_drafts, queue_ceiling − waiting)`.**
> `queue_ceiling` caps the QUEUE across runs; it is never a per-run instruction.

### C2 · State the precedence inside §0.8, where the collision happened

> 🆕 **§0.8.0 · WHEN §0.8's OWN CLAUSES DISAGREE, THE NARROWEST BINDS.** The cascade loop (§0.8.1a) is
> the operative instruction. The pass condition (§0.5) is a TEST, not a licence — it describes the
> minimum a run must clear, never the maximum it may do. **A `>=` in a pass condition has never
> authorised anything.**

⚠️ **This generalises past this defect**, which is why it is worth installing: §0.1 ranks rules by
class and is silent when two rules of the *same* class collide. This is the same gap §0.1 was written
for, one level down.

### C3 · Park the surplus instead of drafting it — 🎯 the fix that costs nothing and fixes two things

The run had **~30 researched, gate-passed organisations** and drafted 15 because it had no other place
to put them.

🔴 **There is already a place. It is `ready-queue.md`, it IS the cascade's T1 tier, and it has been
empty and 7 runs stale** — which is precisely why every recent run has had to descend to T3 discovery
and re-research from scratch.

> 🆕 **THE SURPLUS RULE: research to the cascade's natural stopping point; draft to
> `max_new_orgs_per_run`; WRITE THE REMAINDER TO [[ready-queue]] with its evidence intact.**
> A researched organisation that is not drafted tonight is **not** waste — it is tomorrow's T1, and
> T1 is the cheapest tier in the cascade.

This converts overshoot from a cost into a buffer, refills the tier that has been dead for weeks, and
**cuts tomorrow's discovery cost to near zero.**

### C4 · Stop printing overshoot as a percentage

> **`Outreach floor: N carded · N drafted · target N · ceiling N · {ON TARGET | 🔴 OVER BY N | FAILED — <named gate>}`**

**Never a ratio.** `OVER BY 5` reads as the defect it is; `150%` reads as a win.

---

## 6 · Effectiveness check

**Closed after 3 consecutive runs printing `ON TARGET`, at least one of them a run where the cascade
had surplus available and parked it to `ready-queue` instead of drafting it.**

🔴 **The second condition is the real test.** A run with nothing spare will print `ON TARGET`
trivially. The control only proves itself on a night when the machine *could* have overshot and chose
not to — which is exactly the night this defect occurred.

**Leading indicator to watch:** `ready-queue.md` should stop being stale. If it is still empty after
three runs, C3 was written and not executed.
