---
business: Human Skills Training
type: charter
title: Outreach system charter — why it exists, the one principle, what it must never become
status: DRAFT 2026-11-02 for Chris's revision (built from his 10/30–11/02 rulings; nothing here is new policy)
owner: Chris Danilo
read_before: [RULEBOOK.md, VOCABULARY.md, ../README.md]
---

# Outreach system charter

Every session, human or machine, reads this page before the Rulebook. The Rulebook says *how*. This page says *why* and *how far*. When a proposed change does not trace back to a line on this page, it is drift, not a feature.

## 1. Purpose
Fill Chris's calendar with first conversations with the right organizations, at the right time — without a second thread to any org, a guessed address, an unapproved send, or a rule only one machine follows.

## 2. The guiding principle
> **One engine, one rulebook, one list. The machines find, verify, and draft email outreach through a thoughtfully and clearly defined process and ruleset; Chris reviews the drafts and sends; and when something does not add up, stop.**

## 3. Non-negotiables (any change to these is a Chris ruling, dated in the Rulebook)
1. **Email 1 is Chris's.** A machine drafts it; only Chris sends it.
2. **One thread per organization.** Sent mail is checked before any draft. An org never hears from two machines.
3. **Do-not-contact is absolute.** Unsubscribes, "don't contact me", the register, existing clients, Colorado.
4. **Zero guessed addresses.** Printed on the org's own page, given in its own auto-reply, or Apollo **Verified** + ZeroBounce + the org's own domain (H7). Nothing else — ever.
5. **Copy is frozen.** Only the greeting and the org's name vary. Templates change only by Chris.
6. **Gmail is the truth** of what was sent and when. HubSpot mirrors; it never decides.
7. **The night never sends.** Only the 7 AM task sends because only Emails 2 and 3 are timed followups, only from the list the night run approved, and only that task has automatic approval. Anything flagged is not approved.
8. **Stop and hold** when something does not add up. A shortfall is reported with its reason, never met by loosening a gate.

## 4. The flow (one line each; the picture is in `diagrams/`; the folder map is `diagrams/2026-11-03-where-everything-lives.png`)
0. **Supply run** (every day, ~1 AM MT; Chris 2026-11-08): discover → qualify → event check → find and verify people → rebuild → measure the shelf. Stocks the list; never drafts, never touches Gmail, never sends; hard stop 4:30 AM.
1. **Night run** (Sun–Thu, 8:41 PM MT): read the inbox → label thread state → write tomorrow's approved send list → draft review-hold replies → loop {discover → qualify & route → find & verify people → draft Email 1} until each machine's minimum (OM-1 10 · OM-2 35) or supply runs out → one morning report.
2. **7 AM send** (Mon–Fri, 7:00 ET, business days; holidays delay, never skip): re-read each listed thread, skip anything that changed, send Emails 2/3 exactly as listed, label, bounce check (>3% stops everything).
3. **Chris, mornings:** sends Email 1 drafts (with the dossier open), answers ★ replies, rules on ⚠ and open questions, reviews review-hold drafts.

## 5. What a machine is
A machine (OM-#) is one cluster: Market × Message × Method, named by launch quarter (CL-Q2-26, CL-Q4-26). A new machine is **a settings block and a template** (the `machines` block of the one settings file, 2026-11-03) — never new code and never its own rules. Every machine runs the same engine under the same Rulebook; only the "Machine settings" table differs. Which machine owns an org is decided by Rulebook E3 — the rule lives there, not here.

## 6. Scope fence — what is out, and how things get in
**Out until the system runs clean unattended for a week** (Chris 2026-10-30): new ICPs or markets · new machines · per-audience timing rules · HubSpot as a decision-maker · any behaviour not traceable to a Rulebook line.

**One source of truth (Chris 2026-11-10).** Rules live only in the Rulebook. This charter, the phase pages, the customer-type files, the helper instructions and the program comments point to a Rulebook section; they never restate a rule.

**The change rule.** A new behaviour enters only as a dated Rulebook line approved by Chris. CAPAs **propose**; Chris **disposes**; the build applies and tests. A rulebook edit that restates an older CAPA quotes that CAPA's own resolution line, never a paraphrase (CAPA 2026-11-02). Questions for Chris go only to the rulings list and the morning report.

**Right tool for the job.** Fixed code does bookkeeping, routing, timing, address checks, template filling, safety gates. The AI reads pages, judges fit, finds people, sorts replies, writes the plain-English report. The AI never writes email copy, never picks who gets an email on its own, never sends anything the code has not cleared.

## 7. Definition of "working"
- The night run completes unattended; minimums met or the shortfall explained.
- The 7 AM sends go out at 7:00 ET from the approved list.
- One morning report, both machines, with the roster-resolution line and open questions.
- Zero invariant failures (one thread per org · send only on GO · DNC absolute · Email 1 drafts-only · no machine overlap).
- Chris can find any dossier, CAPA, instruction set or diagram from `README.md` in one step.

## 8. Where things live
`Marketing/Automations/` is the whole system, laid out as the night runs (2026-11-03): `0_Design-and-Purpose/` (this charter, the Rulebook, the vocabulary, the one rulings log, CAPAs, diagrams) → phases `1_Read-the-Inbox/` … `7_Send/` (each with PhasePurpose/ · programfiles/ · ledgers/ · runs/) → `_shared/` (the master list and THE one settings file, each machine's data under `_shared/machines/`, and the orchestrator that runs the night). `archive/` holds everything not in use. Nothing outside this folder is read at run time except the shared do-not-contact register and the Head Start grantee list.

---
*Revision log — 2026-11-02 draft (Claude, from Chris's rulings). Chris's edits replace this line.*
