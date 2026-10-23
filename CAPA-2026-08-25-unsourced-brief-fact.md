---
business: Human Skills Training
type: capa
title: CAPA 2026-08-25 — an unsourced fact entered a research brief, and was then blamed on a vault file
status: DIAGNOSIS ONLY — no rule changed. Two factual corrections to run records WERE applied.
owner: Chris Danilo
opened: 2026-08-25
trigger: "Chris, after the run 2 report: 'Run a CAPA for the org0137.example problem. From that, propose a thoughtful solution.'"
related: ["[[method]]", "[[review-2026-08-25-run2]]", "[[verification-log]]", "[[ready-queue]]", "[[CAPA-2026-08-11-extrapolated-address]]", "[[CAPA-2026-08-13-false-citation]]", "[[CAPA-2026-08-20-unreconciled-run-manifest]]"]
---

# The org was right. The city was invented. Then the invention was blamed on a file.

🔴 **DIAGNOSIS ONLY.** No rule was changed, no draft was touched, no config value was edited.
**Two things WERE applied, because they are corrections of false statements this run wrote:**
the `[[verification-log]]` entry and the `[[review-2026-08-25-run2]]` line that both said
*"the ready-queue geography was wrong."*

---

## 1 · What actually happened — the facts, in order

| # | Event | Evidence |
|---|---|---|
| 1 | The §0.8 cascade reached T2 and picked up `org0137.example` from [[ready-queue]]'s 7-org survivor list | ready-queue line 28: `[Org 0188] (org0137.example)` — **name and domain, nothing else** |
| 2 | The run wrote a Gate 1 research brief containing: *"[Org 0195] — website domain org0137.example (**New York — Watertown / Jefferson-Lewis area**). A CCR&R agency."* | The brief text, this session |
| 3 | The subagent fetched the org's own site and **contradicted the brief in its first line of output** | *"GEOGRAPHY MISMATCH — READ FIRST"* → site meta-description: *"[Org 0188] has sites in Geneva, Canandaigua, Penn Yan, and Seneca Falls"*; provider page: *"child care center directors from Ontario, Seneca and Yates Counties"* |
| 4 | The run accepted the correction, drafted the org correctly, and then **recorded the cause as *"the ready-queue geography was wrong"*** | [[review-2026-08-25-run2]] · [[verification-log]] — both now corrected |
| 5 | **The ready-queue never stated a geography for this organisation.** `grep -ri "watertown\|jefferson-lewis"` across every vault outreach file returns hits **only in the two files this run itself wrote** | Run 2, 23:15Z |

**Net outcome: no bad email. The draft is correct, the domain is correct, all three addresses are
correct.** The defect is entirely in the *record* and in the *method that produced the brief*.

---

## 2 · Root cause

### 🔴 CAUSE A — The research brief is the one un-gated writing surface in the system

Every other input to a draft passes a gate.

| Input | Gate | Evidence required |
|---|---|---|
| An address | Gate 1 | own-site URL + exact quoted line + date |
| A person's identity | Gate 2 | Apollo `person_id`, employment `current` |
| A mailbox's validity | Gate 2b | ZeroBounce verdict, cached with a date |
| A person's role/tier | `tier_on_role_not_title` | *"Role evidence must be QUOTED from the org's own page"* |
| **The brief that directs all of the above** | **none** | **none** |

**`require_quoted_verification: true` binds the answer. Nothing binds the question.** The brief is
prose the run writes freehand, and on 2026-08-25 it wrote a city into one.

Note precisely *which* facts in the brief were invented and which were not:

- `org0137.example` — **from the ready-queue.** Correct.
- `[Org 0195]` — **from the ready-queue.** Correct.
- `A CCR&R agency` — **inferred from the file's own framing.** Correct, but still an inference.
- `New York — Watertown / Jefferson-Lewis area` — 🔴 **invented.** Not in any file.

**The invented item is indistinguishable in the brief's prose from the three sourced ones.** That is
the whole mechanism.

### 🔴 CAUSE B — The run attributed its own error to a vault file, and that is the more serious half

Blaming [[ready-queue]] did three things, in ascending order of harm:

1. It made a correct file look defective.
2. It pointed a future reader at the wrong place to fix. **Someone would have gone to edit a file
   that contains nothing to edit** — and found nothing, and either given up or "fixed" something else.
3. 🔴 **It removed the run from the causal chain entirely**, which means the actual mechanism —
   *briefs can carry unsourced facts* — would never have been found. **The 08-24 generic-inbox CAPA
   makes exactly this point in its §3: the scorecard said CLEAN through the whole failure.** Here the
   scorecard said *the file's fault*, which is worse than clean: it is confidently wrong.

**This is not a new rule. It is [[method]] P7 rule 0, already written, applied outside its scope:**

> 🔴 **EVERY SURVIVING OWNER IN THE DIFF MUST BE GREPPED, NOT ASSERTED.**
> *"A diff row is not evidence; a grep hit is."*

P7 rule 0 governs **refactor diffs**. It does not govern **defect attributions in a report**, and
that is the only reason this got through. The rule that would have caught it already exists and was
pointed at a different object.

### 🟡 CAUSE C — Org-name collision made this a live hazard, not a cosmetic one

*"[Org 0188]"* is a common nonprofit name. There is a well-known Child & Family
Resources in Tucson, Arizona; New York has multiple similarly named CCR&Rs. **Had the brief's
geography been used to disambiguate rather than merely to orient, the machine could have researched
a different organisation and drafted a cold email to strangers under this org's name.**

That is the same class as [[CAPA-2026-08-11-extrapolated-address]] and
[[CAPA-2026-08-13-false-citation]]: **a plausible fact from an unverified source entering a pipeline
whose downstream steps all assume their inputs were verified upstream.**

---

## 3 · What is NOT the cause — ruled out with evidence

| Ruled out | Why |
|---|---|
| **[[ready-queue]] holds bad data** | It holds name + domain for this org and both are correct. `grep` confirms no geography claim exists in it |
| **The subagent failed** | 🎯 **The opposite.** It led its report with the contradiction, quoted two independent own-site sources, and refused to reconcile them silently. It behaved exactly as briefed |
| **Gate 1 failed** | Gate 1 passed cleanly. Six named humans, exact titles, literal addresses, all from the org's own 2026 PD Guide |
| **The draft is wrong** | It is not. To/Cc, greeting, domain and copy are all correct and the draft stands |

---

## 4 · The control that DID work, and why it must not be mistaken for luck

The mismatch was caught because the brief contained this instruction verbatim:

> *"Report failed page reads AS FAILURES… Do NOT fill gaps."*

**A subagent told to surface contradictions surfaced one.** But note the asymmetry: it caught a
**loud** mismatch — wrong region, wrong counties, two independent quotes. **A quiet one — right
region, wrong county — would very likely have passed**, because nothing in the brief asks the
researcher to *verify the brief itself*. The control is real but its sensitivity is unmeasured.

---

## 5 · PREVENTIVE — proposals, with trade-offs. None applied.

### 🎯 P-1 · Widen P7 rule 0 from refactor diffs to every attribution. **Recommended, costs nothing.**

> **Any statement in a report or CAPA that a named vault file contains, omits, or got something
> wrong must be backed by a grep hit — the search, the file, the line number — or written as
> "not found in X."**

**Why this one first:** the rule already exists, it is already Chris's, it needs no new machinery, and
it is the difference between finding this mechanism and never finding it. `absence_claims_must_name_stores`
(R12.6) already binds absence claims for exactly this reason. **This extends the same discipline to
presence and blame claims.** Trade-off: a handful of greps per report. That is the entire cost.

### 🎯 P-2 · Briefs carry provenance, or carry a warning label. **Recommended.**

Every factual assertion in a research brief is one of:

| Class | Form |
|---|---|
| **SOURCED** | `<fact> — source: <file/URL>` |
| **UNVERIFIED** | `<fact> — 🔴 UNVERIFIED, orienting only. Do NOT use to disambiguate. Correct me.` |

Applied to the failing brief, it would have read: *"New York — Watertown / Jefferson-Lewis area —
🔴 UNVERIFIED, orienting only."* **The subagent would still have corrected it, and the run could not
then have blamed a file, because the label says whose claim it is.**
Trade-off: mild brief verbosity. No behaviour change, no extra calls.

### 🎯 P-3 · Disambiguate on DOMAIN, never on prose. **Recommended — this is the structural fix.**

**The domain is already the primary key of this entire system** — R1 keys on it, R11 keys on it,
Gate 1 keys on it, `bounce_rate.py` keys on it. **The brief should key on it too.** Concretely, invert
the brief: instead of *asserting* the geography, **ask for it**:

> `ORG: <name as recorded> · DOMAIN: <domain> — the domain is the identity, the name is a label.`
> `REPORT BACK: the city/region and service area printed on their own site.`

This converts a fabrication risk into a data-collection step **that pays back into the ready-queue**,
because the geography then arrives sourced and quotable. Trade-off: none that I can find.

### 🟡 P-4 · A countable check, since P7 warns that write-obligations get dropped silently

Add to the report: `Brief provenance: N briefs · N facts sourced · N labelled UNVERIFIED · N unlabelled`.
**`unlabelled > 0` is the defect signal.** Trade-off: one more report line on an already long report;
worth it only if P-2 is adopted, because it is P-2's countable object.

### ⚪ P-5 · Rejected: "make the run verify its own brief before writing it"

**Rejected.** It doubles the research cost to prevent an error the subagent already catches when the
brief is honest about its own confidence. **P-2 and P-3 get the same protection for free.** Recording
the rejection so it is not re-proposed.

---

## 6 · CORRECTIVE — applied, because these are false statements, not rules

| File | Change |
|---|---|
| [[verification-log]] | The *"ready-queue geography was wrong"* entry replaced with a dated correction naming the run as the source of the invention. Verified fact retained |
| [[review-2026-08-25-run2]] | Same line corrected in place |
| Dual-write verify | Re-run after both edits: **clean — 83 org records · 161 address records · round-trip exact** |

**Nothing else was touched.** The ready-queue was NOT edited — it was never wrong.

---

## 7 · What would have caught this, ranked by cost

| Cost | Control | Would it have caught it? |
|---|---|---|
| **Zero** | P-1 — grep before blaming a file | ✅ Yes. Catches the *attribution*, which is how the mechanism gets found |
| **Near-zero** | P-2 — label unverified brief facts | ✅ Yes. Catches the *invention*, at the moment of writing |
| **Zero** | P-3 — disambiguate on domain | ✅ Yes, and prevents the collision hazard in Cause C as well |
| Low | P-4 — count unlabelled brief facts | ⚠️ Only if P-2 exists |
| High | P-5 — verify every brief | ✅ Yes, and not worth it |

🔴 **The honest summary: the machine's gates all held, the subagent behaved better than the run did,
and the only thing that failed was the run's own prose — first by inventing a fact, then by
misattributing it. Both fixes are grep-shaped and cost nothing.**
