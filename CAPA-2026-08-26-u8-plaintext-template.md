---
business: Human Skills Training
type: capa
title: "CAPA 2026-08-26 — U8 passed on all 20 drafts while every body was wrong"
status: open
owner: Chris Danilo
raised_by: Chris (spotted visually in the Gmail compose window)
related: ["[[method]]", "[[sequence-tracker]]", "[[review-2026-08-26]]", "[[golden-references]]"]
---

# CAPA — U8 asserted ✅ on 20 drafts. All 20 bodies were wrong.

**Chris caught this by looking at a draft. No control caught it.**

## 1 · What happened

The run built all 20 bodies by reading the approved template with
`messageFormat: PLAIN_TEXT`, then writing drafts with `body:` only and **no `htmlBody:`**.

**Gmail's plain-text rendering represents `<b>bold</b>` as `*asterisks*` and `<ul><li>` as
space-indented hyphens.** The run read those asterisks as plain-text noise, **deleted them**, and
reproduced the hyphens literally. It never fetched the HTML.

**Compounding error:** Email 1 was sourced from the **ICP Oswego message of 2026-08-12**. The current
v6 copy dates from **2026-08-18**. The run built ten drafts from a superseded version.

## 2 · The defects, by severity

| # | Defect | Class | Drafts |
|---|---|---|---|
| **1** | **Approved sentence MISSING** — *"My thesis is that Human Skills will be most important in an **AI-powered world.**"* | 🔴 **missing copy** | Email 1 × 10 |
| **6** | **Wording CHANGED** — anchor text `<a><b>how to design top notch training that actually changes behavior</b></a>` became a naked URL **with an inserted colon** | 🔴 **machine wrote copy** | Email 2 × 4 |
| 2 | All `<b>` stripped — 10 spans in Email 1, 1 in Email 2 | formatting | 14 |
| 3 | Real `<ul><li>` → literal hyphens | formatting | Email 1 × 10, Email 3 × 6 |
| 4 | Inline GIF `cid:` anchor lost | formatting | Email 1 × 10 |
| 5 | YouTube link display text rendered as the Google redirect string | formatting | Email 1 × 10 |

🔴 **Defect 6 is the serious one.** `machine_writes_copy: never` is a **level-2 hard limit**. The
machine inserted a colon that does not exist in the approved copy and destroyed a hyperlink. **This is
the first copy deviation in the machine's history that originated with the machine rather than with
Chris.** Every prior as-sent delta has been a recipient change.

## 3 · What shipped and what was caught

| | Outcome |
|---|---|
| **Email 1 × 10** (new orgs) | ✅ **CAUGHT IN TIME.** Still drafts. Recast 2026-08-26 15:47–15:49Z against the verified 08-18 HTML |
| **Email 2 × 4** | 🔴 **SENT 15:32–15:34Z** with the colon and the broken P.S. hyperlink. **[Org 0203] · [Org 0684] · ELC Sarasota · ELC Broward.** Cannot be recalled |
| **Email 3 × 6** | 🔴 **SENT 15:35–15:37Z** with flattened bullets. Suffolk · [Org 0985] · Schoharie · CAPC Jefferson · ICP Oswego · CCS CNY |

**Ten organisations received a body the machine altered. Four of those alterations were to the words.**

## 4 · Why no control caught it

**U8 reads: "body byte-identical to the approved template except greeting and `{{company}}`."**
The run asserted **U8 ✅ on all 20** — and §0.4's own rule was followed to the letter: *each assertion
reports the object it checked.* **The object checked was the plain-text rendering. The template is HTML.**

🔴 **§0.4's preamble says "a checklist that reports only verdicts becomes a ritual." This is the next
failure mode along: a checklist that reports the WRONG OBJECT confidently.** Naming the object is
necessary and was not sufficient, because nothing required the object to be the authoritative one.

**Second gap: nothing pins the template version.** `golden-references` names message IDs but the run
picked a source by convenience — the first Email 1 it had already fetched — and that message was six
days and one revision stale. **No control asks "is this the current version?"**

## 5 · Corrective actions — PROPOSED, not applied. Chris rules.

| # | Control | Cost |
|---|---|---|
| **C1** | 🔴 **U8 must be checked against `htmlBody`, never `plaintextBody`.** Fetch the golden with `FULL_CONTENT` and diff the HTML | One extra field on one fetch per run |
| **C2** | 🔴 **Every draft carries `htmlBody`. A `body`-only draft is a defect by definition** — the approved copy contains formatting, so plain text can never be byte-identical to it | None |
| **C3** | **Pin the template version in `config.json`** — `email1_golden_msg_id`, `email2_golden_msg_id`, `email3_golden_msg_id`, each with the date it was ratified. **The run reads the ID; it does not choose a source** | One config block |
| **C4** | **Add U8.1: `htmlBody` contains the expected count of `<b>` spans and `<li>` elements for that template version.** A countable check, not a judgement | Small |
| **C5** | **Log the as-sent copy deviation for the 10 sent bodies** in the learn pass — *log copy changes, change nothing* — so the diff baseline is not silently corrupted | Done below |

## 6 · The forward-master is also suspect

The review file named `<thread-id>` ([Org 0546], **2026-08-14**) as "the golden, v6". **That
message predates the 08-18 revision and may also lack the AI-powered-world line.** Not opened — it
carries the 34 MB GIF. 🔴 **Verify before forwarding it as a master. If it is stale, every
forward-and-edit send since 08-18 has been shipping the older body.**

---

## ✏️ AS-SENT REALITY — Chris, 2026-08-27 (recorded by the review session)

> *"I don't think the drafts it mangled were resolved in the end. I know I manually resolved several
> and sent them out because I need to get these out the door reliably each day. It takes too long to
> resolve these root issues with you each morning so this has become our pattern."*

**Two facts for this CAPA's effectiveness check:** (1) the record above claiming the 10 Email 1 drafts
were machine-recast should NOT be read as "Chris sent machine-corrected copies" — several were fixed
BY HAND before sending, so the as-sent bodies need a full-body diff before any of them is treated as
a template baseline. (2) 🔴 **The pattern Chris names — he manually repairs machine defects each
morning because reliability-by-hand beats waiting for root-cause fixes — is itself a cost this CAPA
should count.** Every morning-repair is unpaid review time; the corrective is only DONE when a batch
ships without Chris touching a body.
