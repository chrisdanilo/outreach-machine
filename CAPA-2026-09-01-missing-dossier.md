---
business: Human Skills Training
type: capa
title: "CAPA 2026-09-01 — the dossier stopped being produced after one run, and nothing noticed"
status: control applied, awaiting Chris's ratification
owner: Chris Danilo
raised_by: Chris ("where is the dossier file? it's been missing the last two or so mornings")
related: ["[[method]]", "[[dossier-2026-08-28]]", "[[review-2026-08-31]]", "[[review-2026-09-01]]", "[[CAPA-2026-08-20-unreconciled-run-manifest]]", "[[CAPA-2026-08-26-unlabelled-sends]]"]
---

# CAPA — the send-ready dossier ran once, then vanished, and the manifest could not see it go

**Chris caught this. No control caught it, and no control could have** — for the reason in §3.

---

## 1 · What happened, with dates

| Date | Send-ready artifact | Where the per-org cards lived |
|---|---|---|
| 08-11 → 08-18 | `review-dossier-YYYY-MM-DD.md` | One combined file |
| 08-19 → 08-27 | `review-YYYY-MM-DD.md` | Cards inside the review file |
| **08-28** | 🆕 **`dossier-2026-08-28.md`** — **the split** | **Cards in the dossier; findings in `review-2026-08-28.md`** |
| **08-31** | 🔴 **NONE** | **Nowhere.** |
| **09-01** | 🔴 **NONE** *(until this CAPA)* | Nowhere |

**The split on 08-28 was deliberate and it was right.** `dossier-2026-08-28.md` opens with a status
table and says *"Findings and rule detail live in [[review-2026-08-28]]."* `review-2026-08-28.md`
contains **zero** `## N ·` organisation cards and never uses the word *dossier*. Two artifacts, two
jobs: **one you send from, one you learn from.**

**Then it ran exactly once.**

### What Chris actually received on 08-31 instead

The entire card content for ten new organisations was this, inside §5 of a 51 KB review file:

> *"All 10 new organisations are MKT-001 and stay. [Org 0070] · [Org 0963] · CRR Santa Barbara · Crystal
> Stairs · [Org 1329] · Central Valley CSN · Community Connection for Child Care
> (Kern) · Child Action · Iredell County PYC · Chatham County Partnership."*

**Ten names. No addresses, no titles, no thread IDs, no source URLs, no attachment gate, no
redundancy count, no send order.** Everything needed to review a draft before sending it was in Gmail
and nowhere else. **Chris sent all 27 anyway** — which is the point in §4.

---

## 2 · Root cause — the split was made in the RUN, not in the PROGRAM

🔴 **§0.3 THE RUN has 22 steps. None of them produces a dossier.**

**Step 16 reads, in full:** *"Write `review-YYYY-MM-DD.md` — decisions → mandated blocks → header table
→ cards."* **That is the only artifact §0.3 orders.** A grep of §0 (method.md lines 1–800) returns the
word *dossier* exactly **twice**, and neither is an instruction:

| Where | Text | What it is |
|---|---|---|
| §0.3 step **18b** | *"put its one line at the **TOP of the dossier**"* | A reference to an object |
| §0.6 | *"← TOP LINE OF EVERY DOSSIER (Chris, 2026-08-28)"* | A reference to an object |

**Both say where to put a line in the dossier. Neither says to write one.**
🔴 **No file anywhere in the vault orders a `dossier-YYYY-MM-DD.md`.** The 08-28 run invented the split,
did it well, recorded it in `STATE` — *"built the dossier newest-first for my convenience, not Chris's
outbox order"* — and **never installed the obligation into §0.**

**So the 08-31 run followed §0.3 correctly and the artifact disappeared.** Step 16 was executed. Step 16
was marked complete. The manifest balanced. **Nothing was skipped, because a step that does not exist
cannot be skipped.**

### This is a known mechanism, running in the opposite direction

[[CAPA-2026-08-20-unreconciled-run-manifest]] §2b installed the **P7 refactor rule** after a compression
pass silently deleted four write-obligations: *"a list that said what each file is FOR became a list of
what to OPEN."* **P7 guards the DELETION of an obligation.**

🔴 **This is the ADDITION of an artifact without the obligation** — and it has the same blind spot, for
the same structural reason: **the run manifest is generated FROM §0. Anything not in §0 is invisible to
the manifest and therefore un-auditable.** P7 protects what is written down. It cannot protect a
convention that only ever existed in one night's judgement.

**Same shape as [[CAPA-2026-08-26-unlabelled-sends]] §3**, where a Phase 3 obligation was *shadowed* by
§0.3's shorter chain. There the obligation existed in the archive and lost to §0. **Here it existed
nowhere but in a habit, and lost to §0 immediately.**

---

## 3 · Why no control caught it, and why none could have

| Control | Why it was silent |
|---|---|
| **Run manifest** (`N obligations · N completed · N skipped · N FAILED`) | It is built from §0. The dossier is not in §0. **The manifest reported 22 of 22 and it was telling the truth** |
| **§0.5 pass condition** | Counts `invalid`, `M`, `HELD`, `preflight_holds`, `new_orgs_drafted`. **No clause asks whether the deliverable exists** |
| **§0.6 mandated lines** | 30 lines. **Not one of them names the dossier** — the word appears only as *"TOP LINE OF EVERY DOSSIER"*, describing where a different line goes |
| **File-freshness line** | Lists ledgers and logs. **The dossier was never added to it** |
| **`bin/` scripts** | Six scripts compute numbers. **None checks that an output file was produced** |

🔴 **Every control the machine has measures the QUALITY of the work. Not one measures whether the thing
Chris actually opens was produced.** That is the gap, stated plainly.

---

## 4 · The cost, and why it was invisible from the inside

**Chris sent all 27 drafts on 08-31 without a dossier.** That is exactly what makes this expensive
rather than harmless:

> *"It takes too long to resolve these root issues with you each morning so this has become our
> pattern."* — Chris, 2026-08-27, recorded in [[CAPA-2026-08-26-u8-plaintext-template]]

**He absorbed it by hand, twice, and the machine's own metrics all came back green.** `Yield`, `Pace`,
`Outreach floor`, `Pre-flight`, `Run manifest` — every one passed on 08-31. **A run can hit every
number it scores and still fail to deliver the only artifact its user opens.**

⚠️ **And the failure mode compounds silently.** Reviewing a draft from inside Gmail means opening
sixteen messages to check sixteen recipient sets. **The dossier is not a convenience — it is the only
place the evidence behind a recipient choice is visible before the send.** Two mornings of sending
without it is two mornings where a `tony.armadillo@`-class address had no review surface at all.

---

## 5 · Corrective action — APPLIED 2026-09-01T10:55Z

> ⚠️ **P7 rule 1 compliance — DIFF OF DELETED OBLIGATIONS: NONE.** This pass is purely additive. The
> single replacement (§0.5's dossier clause → the `run_integrity.py` exit clause) **broadened** the
> obligation; the dossier is still named and still fails the run. Nothing was shortened, merged or
> de-duplicated.

### The insight that changed the design

**Chris's original ask was "why is the dossier missing." Building the check revealed that existence is
only one of three ways an artifact fails, and all three were live on the same night.**

| Failure mode | Instance | How long it had been broken |
|---|---|---|
| **EXISTENCE** — never written | the dossier | 2 runs |
| **EXECUTION** — the artifact is never written, so its *consumer* never runs | `runs/<date>/sent_sweep.json` | 🔴 **Every run ever.** `bin/ledger_reconcile.py` is listed **LIVE** in §0.10 and **had never once executed** |
| **AGREEMENT** — written correctly, never read back | `runs/2026-08-31/drafts.json` | 🔴 The `As-sent delta` line has an `M` slot and **nothing had ever computed it** |

**A control that only checked existence would have closed one of three.**

### ✅ What was built

| # | Control | Where |
|---|---|---|
| **C1** | **§0.3 step 16b** — write `dossier-YYYY-MM-DD.md`; **not written → the run FAILS.** Step 16 relabelled *the learning artifact*, 16b *the sending artifact* | [[method]] §0.3 |
| **C2** | 🆕 **`config.json.expected_outputs`** — the run's deliverables declared as **DATA, not prose.** 9 rows, each with `binding` and a `why` | `config.json` |
| **C3** | 🆕 **P7b · THE MIRROR** — *"any pass that ADDS a deliverable must declare it in `expected_outputs` in the same session that invents it."* Sits directly beneath P7, which guards the opposite direction | [[method]] RUN EFFICIENCY |
| **C4** | 🆕 **`bin/run_integrity.py`** — the three checks above, as countable objects. Report line `Integrity:`. **BINDING** for `binding:true` outputs; **SHADOW 3 runs** for the two diffs, per §0.10's graduated-gate precedent | `bin/` |
| **C5** | **§0.3 step 3** now seeds the run manifest from `expected_outputs` as well as from §0 — closing the loop the CAPA identified | [[method]] §0.3 |
| **C6** | **§0.3 steps 5 and 15** now *oblige* the two orphan artifacts: `sent_sweep.json` at GATHER, `drafts_observed.json` from the read-back that step 15 already performs | [[method]] §0.3 |
| **C7** | **§0.5** pass condition: `run_integrity.py` exits 0 or 2 — **never 1** | [[method]] §0.5 |

### 🔴 What the control found on its FIRST run — four live defects, none previously visible

| # | Finding | Severity |
|---|---|---|
| **1** | **`As-sent delta` was M = 5, not the M = 0 the run reported at 09:35Z** — nor the M = 2 it was corrected to at 10:14Z. **Both earlier numbers were recalled; 5 is measured.** Kern (To swapped + 2 Cc) · Child Action (+2 Cc) · **CVCSN (+`findcare@`)** · [Org 0444] (−`QSLAHelpDesk@`) · CRRSBC (−2 Cc, +2 Cc) | 🔴 High |
| **2** | 🔴 **`findcare@org0242.example` was ADDED BY CHRIS, not drafted by the machine.** The run spent the entire night reporting it as the machine's *third* live-page V3 failure and built decision **D1** on that count. **Machine V3 failures stand at two.** Re-attributed in `calibration-log.jsonl`, `config`, [[contacted]] and the review | 🔴 **High — it inflated the evidence behind a decision put to Chris** |
| **3** | **`bin/migrate_contacted.py` and `bin/bounce_rate.py` stripped `_` from addresses** as if it were markdown emphasis. **The underscore is legal in an email address.** Ledger B held `person1240@org0809.example` for a real address `person1238@org0809.example` — invisible to de-dup, to U4 and to the bounce cross-check. Regex fixed in both; ledger regenerated | 🔴 High |
| **4** | `run_integrity.py`'s own To join-key was not case-normalised, and Gmail lower-cases the domain on write (`person0955@org0687.example` → `@org0687.example`). **The script's first run reported a false divergence against itself.** Fixed | Low |

⚠️ **Findings 1–3 had all been true for days and every metric had come back green throughout.** That is
the argument for the control, made better than any reasoning could.

### 📋 Still proposed, not applied

| # | Item | Why not |
|---|---|---|
| **C8** | **Backfill `dossier-2026-08-31.md`** | 🔴 **Recommended AGAINST.** Those 27 drafts are sent and reconciled. A backfilled dossier is a historical artifact nobody sends from, and creating one invites reading it as evidence the run produced it |
| **C9** | **Promote the two diff checks to BINDING** after 3 clean runs | The graduated-gate discipline in §0.10 exists for a reason; a new gate that blocks on day one blocks on its own bugs — as finding 4 demonstrates |

---

## 6 · Effectiveness check — how we know this is closed

**Not "the dossier was written tonight."** That is a single observation, and this defect was *born* from
a single good observation on 08-28.

🔴 **CLOSED when three consecutive runs print an `Integrity:` line with `binding outputs ok` and a
non-zero `Dossier:` card count, and at least one of those runs is one that otherwise went badly** —
because the question is not whether the deliverable survives a good night. It is whether it survives a
bad one.

**Tracking:** run **1 of 3** — 2026-09-01. `Integrity: outputs 9/9 present · binding outputs ok ·
drafts read-back: clean · as-sent delta: M = 5`. `dossier-2026-09-01.md`, 16 cards.
