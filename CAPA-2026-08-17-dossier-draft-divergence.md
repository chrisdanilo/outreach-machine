---
business: Human Skills Training
type: CAPA
title: "CAPA 2026-08-17 — the dossier card said a person was OFF the thread while the draft had him in the To"
status: closed-with-actions
owner: Chris Danilo
raised_by: Chris Danilo
date: 2026-08-17
severity: high
related: ["[[method]]", "[[dossier-template]]", "[[review-dossier-2026-08-17]]", "[[batches/2026-08-17]]"]
---

# CAPA — the dossier contradicted the draft it was supposed to describe

## What Chris saw

> *"Your dossier said that [Person 0592] was deliberately left off the email draft, but he was included
> in the TO field and was the first addressed in the email body."*

He is exactly right, and it is worse than a typo: **the card gave a reason for a decision that the
draft had already reversed.** Card 7 ([Org 0557]) read:

> *"**[Person 0592], Ph.D.** | **Executive Director** | Decision-maker | 🔴 **OFF the thread — no
> address published anywhere on the org's own site.**"*

…while draft `r4791836354633155556` had `person1075@org0336.example` in the To and opened *"Steve, Melissa,
and Dawn,"*.

**Impact.** Chris reviews sends against the dossier. A card that misdescribes its own draft destroys
the point of the card — it means the review gate is reading fiction. **This is the same class of
harm as [[CAPA-2026-08-13-false-citation]]** (a card asserting something untrue at the moment of
review), arrived at by a different route. No wrong address was sent; the damage is to trust in the
artefact.

## Root cause — not carelessness, a missing step in the transaction

The per-org loop in [[method]] Phase 1 is **verify → dossier card → draft**, and it was followed. The
sequence was:

1. Read ELCPH's staff page. **The Executive Director's address is not published there.** True at that
   moment.
2. **Wrote the card**, correctly recording him as off-thread with that reason, and correctly flagging
   it as a gap rather than a preference.
3. **Drafted** To the Provider Services Director.
4. **Later in the run**, a vendor lookup returned `person1075@org0336.example` as `verified`. The
   standalone-CCR&R rule names the Executive Director as the correct To, so the draft was rebuilt.
5. **Performed the three-step recipient transaction** — create new, trash old thread, verify against
   `list_drafts`, re-apply the label. All four steps done correctly.
6. 🔴 **Never went back to the card.**

**The root cause is that the recipient-change transaction in [[method]] Phase 3 is defined purely as
a Gmail operation.** Its three steps are CREATE, TRASH, VERIFY — all about the mail client. Nothing
in it mentions the dossier. So a run can execute the transaction perfectly and still leave the
review artefact describing the draft that no longer exists.

**Contributing cause — a sequencing error.** The decision-maker lookup ran *after* the card and draft
were built for that org. Had it run before, no rebuild and no divergence. The lookup was triggered
opportunistically (a batch of missing addresses across several orgs) rather than as a step in the
per-org loop.

## Why the existing controls did not catch it

| Control | Why it missed |
|---|---|
| "No draft without its dossier card" | Satisfied — a card existed. The rule tests **existence**, never **agreement** |
| Three-step recipient transaction | Satisfied — all three Gmail steps done. The rule's scope is Gmail only |
| Pre-send self-check | It asks *"what source saw each address, and on what date"* per recipient. **Knobl's address had a real, verifiable source, so he passed.** The check never asks whether the card and the draft name the same people |
| Card-order-is-Gmail-order rule (08-13) | Concerns ordering, not content |

**Every control passed. The defect lives in the gap between them.**

## Corrective action — taken now

- Card 7 of [[review-dossier-2026-08-17]] has been **rewritten** to describe the draft that was
  actually sent, with the change history stated on the card rather than silently overwritten.

## Preventive action — proposed for [[method]], NOT self-applied

Per the standing rule that the machine reports and Chris decides, these are proposals.

**P1 — Make the recipient transaction FOUR steps, not three.** Add to [[method]] Phase 3:

> 4. **RE-WRITE THE DOSSIER CARD.** A recipient change is not complete until the org's card names the
>    same To and Cc as the live draft. State the change on the card — what it was, what it became,
>    and why — rather than overwriting it silently.

**P2 — Add one line to the pre-send self-check.** It currently verifies addresses per recipient. Add:

> **Does the card's To and Cc match `list_drafts` for this org, name for name?** A card that
> disagrees with its draft fails the check exactly as a guessed address does.

**P3 — Move the decision-maker lookup INSIDE the per-org loop, before the card is written.**
The loop becomes **verify → *resolve missing decision-maker/Tier-1 addresses* → dossier card →
draft.** This removes the whole failure mode rather than catching it downstream: if the address
arrives before the card, the card is right the first time and no recipient transaction is needed.
It also avoids spending a Gmail transaction on avoidable work — tonight's ELCPH rebuild was pure
waste.

**P4 — Cheap structural check.** Because both the card and the batch file record recipients, a
one-line comparison of the batch table against `list_drafts` at the end of every run would catch any
future divergence mechanically. Worth building into Phase 4's orphan-recovery step, which already
reads `list_drafts`.

## Note on what did work

The gate that mattered still held: **Knobl's address was genuinely verified** (vendor `verified`,
employment current since 2017-12, title corroborated by the org's own page) before it reached a
draft. This was a documentation failure, not a verification failure. Chris then replaced him anyway
on judgement grounds — see the CCR&R-title ruling in [[recipient-profile]].
