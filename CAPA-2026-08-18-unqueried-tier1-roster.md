---
business: Human Skills Training
type: CAPA
title: "CAPA 2026-08-18 — six training-titled people were identified, recorded on the card, and never submitted to the vendor"
status: controls-installed-awaiting-effectiveness-check
owner: Chris Danilo
raised_by: Chris Danilo
date: 2026-08-18
severity: high
related: ["[[method]]", "[[ready-to-draft-2026-08-18-FL]]", "[[verification-log]]", "[[STATE]]", "[[CAPA-2026-08-17-dossier-draft-divergence]]", "[[recipient-profile]]"]
---

# CAPA — the roster was read correctly and then never queried

## What Chris saw

> *"The [Org 0539] website shows these personnel. Several of them have 'training' in their titles,
> but the email draft the machine drafted doesn't list them."*

He is right, and the same shape is present at a second organisation in the same batch
([Org 0549]), which is why this is filed as a systemic defect rather than a one-org miss.

---

## 1 · What actually happened

**This is not a scraping failure.** The run read `https://[Org 0576]/about/team/` correctly and
recorded every training-titled person on the dossier card. Re-fetched 2026-08-18 for this CAPA — the
live page matches the card exactly.

The card even names the concentration as the org's selling point:

> *"this organisation employs five Assessment and Training Specialists and a Coaching and Training
> Specialist. That is a training department in all but name, and the largest concentration of
> training-titled staff found in Florida so far."*
> — [[ready-to-draft-2026-08-18-FL]], card 5, Pain Hypothesis

**The failure is one step later: of eight Tier-1 candidates at that org, two were submitted to Apollo
and six were never submitted at all.**

| Person | Title (org's own team page) | Tier under current rules | Submitted to vendor? | Outcome |
|---|---|---|---|---|
| [Person 0044] | Coaching and Training Specialist | 1 | ✅ yes | `verified` → on the draft |
| [Person 0583] | CCR&R Specialist | 1 | ✅ yes | no result (1 credit) |
| [Person 0413] | CCR&R Specialist | 1 | 🔴 **no** | filed "address unknown" |
| [Person 0331] | Assessment and Training Specialist | 1 | 🔴 **no** | filed "address unknown" |
| [Person 0392]-Otto | Assessment and Training Specialist | 1 | 🔴 **no** | filed "address unknown" |
| [Person 0066] | Assessment and Training Specialist | 1 | 🔴 **no** | filed "address unknown" |
| [Person 0100] | Assessment and Training Specialist | 1 | 🔴 **no** | filed "address unknown" |
| [Person 0493] | Assessment and Training Specialist | 1 | 🔴 **no** | filed "address unknown" |
| Al Henderson | Executive Director | 2 (decision-maker) | 🔴 **no** | filed "address unknown" |

**Consequence.** The thread descended to tier 3 — a generic `ccrr@org0320.example` inbox that Apollo
would not even return an `email_status` for — while six untested Tier-1 candidates sat on the same
page. The draft that is sitting in Chris's Drafts folder is weaker than the evidence supported.

### Budget was not the constraint

| Figure | Value | Source |
|---|---|---|
| Credits spent, whole run | 9 (3,913 → 3,904) | [[verification-log]], 2026-08-18 credit accounting |
| Deeper-lookup budget used | **0 of 25** | same entry, stated twice |
| Standard match cost | 1 credit each | same entry |
| Cost of the 7 missing lookups | **~7 credits, one `people_bulk_match` call** | ≤10 per call per [[method]] Run Efficiency |

The run had 16 credits of standing nightly authority left unspent and a hard per-run cap of 1,000.

### Recurrence in the same batch

| Org | Named + titled on the org's own site | Submitted to vendor |
|---|---|---|
| [Org 0539] | 9 | 2 |
| [Org 0587] | 4 ([Person 0352], [Person 0159], [Person 0314], [Person 0606]) | 1 |
| ELC Florida's Gateway | 2 (LaShone Surrency, [Person 0117]) | 1 |

**Across three orgs: 15 people identified on their employer's own pages, 4 submitted.** Eleven people
were filed as unreachable without anyone asking whether they were reachable.

---

## 2 · Root cause

**The rule that should have caught this already exists and was ratified the same day.**
`spend_lookup_when_unpublished: true` — [[STATE]], 2026-08-18:

> *"When a Tier-1 person or decision-maker is named on the organisation's own page and no address is
> published, spend the vendor lookup. 'Not published' is a fact about the website, not the person."*

And [[method]], the preferred ranking:

> 🔴 *"Never skip a tier to avoid work."*

**So the rule fired for two people and not for the other seven. The root cause is that the rule is
written as a permission with no object and no completeness test.**

Three specific defects, in order of how much each contributed:

**A · The rule never says WHICH named people must be submitted.** It says *spend the lookup* — it does
not say *for every Tier-1 and Tier-2 person on the roster*. So "spend the lookup" is satisfied by
spending one. Phase 1's only guidance is *"highest-tier contacts first"* — a priority ordering with no
floor underneath it.

**B · The stopping condition is "sendable," not "resolved."** A thread holds 1 To + up to 2 Cc. Once
[Person 0044] resolved and the CCR&R inbox provided a route to the function, the org was sendable —
and nothing in the method says to keep resolving after that point. **The machine stopped looking
because it had enough recipients, not because it had run out of candidates.** That is why the miss
landed on training-titled people specifically: they were surplus to the three slots, so they were
never priced.

**C · The dossier records "not looked up" and "looked up, nothing found" identically.** On card 5,
[Person 0583] (1 credit spent, no result) and [Person 0331] (never queried) both read
*"no — address unknown"*, and the Evidence column for the six unqueried people is `—`. **The defect
is therefore invisible at review.** This is the same class of harm as
[[CAPA-2026-08-17-dossier-draft-divergence]] — the review artefact does not describe what the run
actually did — reached by a different route.

**Contributing:** the org-scale gauge and the "right-size the To" rule train the run to *narrow* the
recipient set. Nothing anywhere in the method tells it to *widen the candidate set first*. Narrowing
from a pool of one is not a decision.

---

## 3 · Corrective action — this instance

### 🔴 Containment failed — both threads were already sent before the CAPA opened

[[sequence-tracker]] states *"Still in Drafts: 3 — [Org 0539] · [Org 0587] · ELC Florida's Gateway."*
**That record is stale.** `list_drafts` returns exactly **one** draft in the whole folder
(ELC Florida's Gateway). Escambia and [Org 0587] were both sent at **2026-08-18 22:16 UTC**:

| Thread | Sent as |
|---|---|
| `<thread-id>` — [Org 0539] | **To** `person0339@org0320.example` · **Cc** `amitchell@` + `ccrr@` + `slindsey@` · greeting *"Daw, Skyey, Angela and team,"* |
| `<thread-id>` — [Org 0587] | **To** `person1177@org0330.example` · **Cc** `person0786@org0330.example` |

**A second defect surfaces here, and it is a Phase 4 record-keeping failure:** the tracker's send
state is written from the run's own intent, not from a post-hoc read of Gmail. Six of seven drafts
had left the folder and the file still said three were waiting. **Add to the effectiveness check:
Phase 4 must reconcile the tracker against `list_drafts` at the end of every run.**

**Three things Chris did by hand at review, all of which are evidence:**

1. He **added `person0339@org0320.example`** ([Person 0161], Operations Director) and promoted her to the To.
2. He **added `person1131@org0320.example`** — an address the machine spent a credit on and could not
   resolve. Under the current rules the machine may not construct that address from a colleague's
   pattern; Chris could, and did.
3. The greeting went out reading **"Daw, Skyey, Angela and team,"** — a truncated first name. Minor,
   but it is the cost of hand-editing a greeting at send time and it argues for getting the recipient
   set right before the draft exists.

### The lookups, run 2026-08-18 for this CAPA

**Credit accounting. Before: 3,903 remaining. After: 3,899. Spend: 4.** Itemised: 4 × standard person
match. Six of the ten returned null and were **not** charged; the two Gateway matches returned null
and were not charged. **Reconciles exactly.**

| Person | Org | Result | Usable? |
|---|---|---|---|
| **[Person 0331]** | Escambia | **`person0720@org0320.example` · `email_status: verified`** · Apollo id `63db07c21bfad6000179e84f` · Apollo title *Training & Assessment Specialist*, subdepartment `learning_development` | ✅ **YES — passes both gates** |
| [Person 0392]-Otto | Escambia | `person0820@org0320.example` · **`email_status: extrapolated` (0.7)** | 🔴 **HOLD.** Apollo guessing from a pattern. No second independent source — the team page publishes no addresses. Per [[CAPA-2026-08-11-extrapolated-address]], do not use |
| Al Henderson | Escambia | matched, `email_status: unavailable`, no address | 🔴 HOLD |
| [Person 0066] · [Person 0100] · [Person 0493] · [Person 0413] | Escambia | **no match, 0 credits** | Record as *identified, vendor queried, no result* |
| [Person 0606] | [Org 0587] | `person1186@org0330.example` · `verified` · Apollo title *Development and Special Programs Director* | ⚠️ usable but **not a PD buyer** — development = fundraising. Not recommended for this thread |
| [Person 0159] · [Person 0314] | [Org 0587] | **no match, 0 credits** | Record as *identified, vendor queried, no result* |
| [Person 0588] · [Person 0117] | Gateway | **no match, 0 credits** | Record as *identified, vendor queried, no result* |

**The headline: `person0720@org0320.example` is a verified, named Assessment and Training Specialist
who was one batched vendor call away the whole time — and the run had 16 credits of unspent nightly
authority when it closed.** Her address also independently corroborates the org's first-initial +
surname convention, which is the same pattern Chris used by hand for `dengel@` and `slindsey@`.

### Remaining actions

| # | Action | Status |
|---|---|---|
| C1 | Run the missing lookups (10 people, Escambia + [Org 0587]) | ✅ **done** — 4 credits, results above |
| C2 | Rebuild the Escambia Email 1 thread | 🔴 **NOT POSSIBLE — already sent.** [Person 0331] can only join at Email 2, which requires an explicit override of `followup_recipients: inherit-from-email-1`. **Chris's call** |
| C3 | ELC Florida's Gateway | ⏳ **the only live draft.** See below |
| C4 | [Org 0587] | ✅ no change warranted — nothing usable came back for the PD function |
| C5 | Correct card 5's Power Map so *queried-null* and *never-queried* are visually distinct | ⏳ pending |
| C6 | 🆕 Reconcile [[sequence-tracker]] send state against `list_drafts` | ⏳ pending |

### C3 detail — what the Gateway lookup produced

New Check-1 evidence found for this CAPA, not present in the original card:

- **[Person 0588], Child Development Coordinator** — printed verbatim on the org's own CCR&R page
  👉 `https://www.[Org 0579]/families/child-care-resource-and-referral/`, listed under
  **"ELC-FG Warm Line Contacts"**: *"[Person 0588], Child Development Coordinator (555) 010-0141"*.
  She is the named contact for the CCR&R function → **Tier 1 on role evidence.** No address published;
  **Apollo returned no match.**
- **The org runs its own PD calendar** — its Provider Services page links *"Professional Development
  Training and Coalition Events"* at `elcfg.gosignmeup.com`. Someone owns that calendar. The staff
  directory would name them.
- 🔴 **The staff directory is still the blocker.** `https://www.[Org 0579]/about-us/94-staff-directory/`
  publishes the entire directory as one JPEG (`/wp-content/uploads/2026/07/directory.jpg`, uploaded
  2026-07 — inside the 90-day window). The fetch tool rejects it: *"Image content is not supported."*
  **This is the single highest-value unblock for this org** and it needs a human screenshot or a
  browser session.
- Apollo's own roster for `[Org 0579]` returns 10 people and **contains neither Barnes nor
  Skinner** — it does list two *Quality Outcomes Coordinators*, but vendor-only names cannot pass
  Check 1 and were not used.

**Credit accounting for this CAPA's lookups. Before: 3,903 left. Spend: 0** (both matches returned
null and Apollo consumed nothing). Reconciles exactly.

---

## 4 · Preventive action — ✅ INSTALLED 2026-08-18

> ✅ **Chris, 2026-08-18:** *"go ahead and implement this fully and let's use the next run as the test."*

**All four are live** in [[method]], [[dossier-template]] and [[STATE]]. Exact locations:

| # | Control | Installed at |
|---|---|---|
| **P1** | The roster sweep, as a **gate** | [[method]] Phase 2 · `roster_sweep` + `roster_sweep_cap_per_org` in [[STATE]] |
| **P2** | The roster resolution line + the three states | [[method]] Phase 2 evidence protocol ruling 6 · [[dossier-template]] · `roster_resolution_line` + `evidence_three_states` |
| **P3** | Unspent budget printed as a defect | [[method]] Phase 1 and Phase 7 · `unspent_lookup_budget_is_a_defect` |
| **P4** | `BLOCKED — DIRECTORY NOT MACHINE-READABLE` | [[method]] Phase 2 · `blocked_directory_handler` |

**Plus two the implementation surfaced that were not in the original proposal:**

- **Send-state reconciliation moved to Phase 0.** The Phase 4 orphan recovery was already correct;
  it just runs at the wrong end. Chris sends *between* runs, which is the one window nothing watched.
  `send_state_reconciliation: phase-0-and-phase-4`.
- **"Sweep, then descend" written into the ranking.** *"Descend until you can send"* was being read
  as *"stop as soon as you can send."* You cannot know what tier an org supports until the sweep runs.

**The design principle, recorded in [[method-rationale]]:** every rule in this machine that fires
reliably is attached to a **countable object** and blocks an artefact from existing. Every rule that
has failed to fire is a judgement with no object. **P2 is therefore the load-bearing control** — P1
tells the run what to do, P2 makes it impossible to have not done it and still produce a valid card.

**Deliberately NOT done: the `method.md` size refactor.** It is the right next move — ~95 KB now, and
long runs degrade on setup — but changing the document's shape in the same run as the test would move
two variables at once. Queued for after 2026-08-25.

### The original proposals, as written

### P1 · The roster sweep — make the lookup an obligation with an object

Add to [[method]] Phase 2, before the roster gate:

> **🔴 THE ROSTER SWEEP — every Tier-1 and Tier-2 candidate goes to the vendor in one call.**
>
> Before choosing recipients, list **every** person named on the organisation's own pages whose title
> or role evidence puts them at Tier 1 or Tier 2. **Submit all of them whose address is unpublished in
> a single `people_bulk_match` (≤10 per call), then choose the To and Cc from what comes back.**
>
> **Resolve first, narrow second.** The org-scale gauge and the right-size-the-To rule apply to the
> *resolved* set, never to the set the run happened to look up. A thread carries 3 people; that is a
> reason to choose well, not a reason to stop resolving at 3.
>
> **Cap: 10 per org per run** — one batched call, ~10 credits worst case. Beyond 10 candidates, take
> the highest-tier 10 and record the number deferred.

### P2 · The resolution ledger — make the gap visible on the card

Add a mandatory line to every dossier card, and make its absence invalidate the card:

> ⚠️ **SUPERSEDED — this was the first draft.** The installed schema has nine fields and three
> identities, and it is defined in [[method]] Phase 2 ruling 6 and [[dossier-template]]. It adds
> `named on page` (a coverage denominator), `published`, `held` and `deferred`. **Use the installed
> version; this line is kept only to show what changed.**
>
> `Roster resolution: N Tier-1/2 candidates identified · N unpublished · N submitted to vendor · N resolved · N queried-null`
>
> **A card where `unpublished ≠ submitted` is invalid** and must state the reason per person.

And change the Power Map's Evidence column to distinguish the two states explicitly:

| State | How it must read |
|---|---|
| Looked up, nothing came back | `🔍 VENDOR QUERIED — no match (1 credit, YYYY-MM-DD)` |
| Never looked up | `⛔ NOT QUERIED — reason: ______` |
| Never looked up, no reason | **card invalid** |

### P3 · Report the unspent budget as a defect signal

[[method]] Phase 1 already says *"'1 of 5' with budget left unspent is a defect."* Extend it to
lookups:

> **A run that closes with named, unpublished Tier-1 people AND unspent lookup budget must report
> that pairing explicitly as a defect**, not as thrift. On 2026-08-18 the report recorded
> *"0 of 25 spent"* as a clean line item; it was the symptom.

### P4 · Image and PDF directories are a known blocker with a standing handler

Three orgs are now blocked on unreadable directories — ELC Florida's Gateway (JPEG),
[Org 0550] (PDF), [Org 0566] (no fetchable page). Standing handler:

> When an org's staff directory is an image or PDF, **do not file it as a failed read and move on.**
> Card it as `BLOCKED — DIRECTORY NOT MACHINE-READABLE`, put the direct asset URL on the card, and
> queue it for a human screenshot or a browser session. **The org is not unreachable; the file format
> is.** Same logic as the address rule: *"'Not published' is a fact about the website."*

---

## 5 · Effectiveness check

Re-audit the next three runs against one question: **for every org carded, does the number of Tier-1/2
candidates with unpublished addresses equal the number submitted to the vendor?** Any gap without a
per-person stated reason is a repeat, and this CAPA reopens.

---

## 6 · What this does NOT fix — set expectations

**A roster sweep will not put six trainers on one email.** The thread still holds 1 To + up to 2 Cc.
The gain is that the run picks the best three from eight resolved candidates instead of taking the
one that happened to resolve. At [Org 0539] specifically, if two or three of the five Assessment and
Training Specialists come back verified, the thread becomes a tier-1 send addressed to actual training
staff — instead of a generic inbox the vendor would not verify.
