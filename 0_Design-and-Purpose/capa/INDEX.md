---
business: Human Skills Training
type: index
title: CAPA index — every corrective/preventive action record for the outreach machines, one list
updated: 2026-11-02
---

# CAPA index

A CAPA is written when something went wrong: what happened, impact, root cause, the fix, and what prevents it next time. All 34 live here now (OM-1's 25 from Aug–Oct, OM-2's 8 from late Oct, the engine's 1). Status is copied from each file's own `status:` line — treat 'open' as 'not marked closed', and re-check the file before acting on it.

| File | Title | Status (from the file) |
|---|---|---|
| [[CAPA-2026-08-11-extrapolated-address]] | CAPA — a pattern-guessed address passed Gate 2 because Apollo made the guess | 🔴 CORRECTIVE APPLIED — one decision pending |
| [[CAPA-2026-08-11-unapproved-copy]] | CAPA — outreach machine drafted copy Chris never wrote or approved | ✅ CLOSED 2026-08-11 — Transfer-Audit copy retired by Chris; all 15 drafts deleted |
| [[CAPA-2026-08-11-wrong-address-bounce]] | CAPA — cold email sent to a wrong address that bounced; correct address was on the org's own site | 🔴 OPEN — corrective actions applied, one decision pending |
| [[CAPA-2026-08-12-credit-accounting]] | CAPA — Apollo credit accounting error (2026-08-12) | ✅ closed — corrective actions implemented |
| [[CAPA-2026-08-13-false-citation]] | "CAPA 2026-08-13 — a dossier card cited a page the person was not on" | ✅ closed — corrective action applied |
| [[CAPA-2026-08-17-dossier-draft-divergence]] | "CAPA 2026-08-17 — the dossier card said a person was OFF the thread while the draft had him in the To" | ✅ closed-with-actions |
| [[CAPA-2026-08-17-stale-page-bounce]] | "CAPA 2026-08-17 — FIRST machine-passed hard bounce: a fetch returned a stale version of a live staff page" | 🔴 open-needs-chris |
| [[CAPA-2026-08-18-unqueried-tier1-roster]] | "CAPA 2026-08-18 — six training-titled people were identified, recorded on the card, and never submitted to the vendor" | 🔴 controls-installed-awaiting-effectiveness-check |
| [[CAPA-2026-08-20-housekeeping-nonatomic]] | "CAPA 2026-08-20 — the run's only destructive operation is non-atomic, non-idempotent, undocumented, and scheduled last" | 🔴 controls-installed-awaiting-effectiveness-check |
| [[CAPA-2026-08-20-unreconciled-run-manifest]] | "CAPA 2026-08-20 — the run has a to-do list nobody counts, so items have been dropping silently for four runs" | 🔴 controls-installed-awaiting-effectiveness-check |
| [[CAPA-2026-08-24-generic-inbox-descent]] | CAPA 2026-08-24 — why half the Texas batch reached only a generic inbox | 🔴 DIAGNOSIS ONLY — no corrective action applied |
| [[CAPA-2026-08-24-probe-orphan-and-recipient-cap]] | CAPA 2026-08-24 — an orphaned probe draft, and a 4-recipient draft that broke the cap | 🔴 DIAGNOSED — one cleanup executed, no rules applied |
| [[CAPA-2026-08-25-advice-about-unobserved-systems]] | CAPA 2026-08-25 — the run gave operational advice about a third-party tool it had never opened | 🔴 DIAGNOSIS ONLY — no rule changed. Proposals listed, none applied. |
| [[CAPA-2026-08-25-empty-new-org-queue]] | "CAPA 2026-08-25 — the new-org queue has a one-run refill latency and no buffer, so a single blocked run empties the outbox" | ✅ CLOSED — Chris ruled 2026-08-25; §0.8 installed, bounce rate re-based, corrections applied |
| [[CAPA-2026-08-25-org-domain-identity]] | CAPA 2026-08-25 — an organisation has two domains and nothing records that they are the same organisation | 🔴 DIAGNOSIS ONLY — no rule changed, no config edited. One live risk is unmitigated and named below. |
| [[CAPA-2026-08-25-unsourced-brief-fact]] | CAPA 2026-08-25 — an unsourced fact entered a research brief, and was then blamed on a vault file | 🔴 DIAGNOSIS ONLY — no rule changed. Two factual corrections to run records WERE applied. |
| [[CAPA-2026-08-26-bcc-nonissue-repetition]] | "CAPA 2026-08-26 — the HubSpot BCC 'issue' was raised five times after it was already answered" | ✅ CLOSED — Chris ruled 2026-08-26; item resolved everywhere, preventive rules below |
| [[CAPA-2026-08-26-google-link-wrapper]] | "CAPA 2026-08-26 — every video link ships wrapped in a Google redirect, and it survives delivery" | 🔴 open |
| [[CAPA-2026-08-26-u8-plaintext-template]] | "CAPA 2026-08-26 — U8 passed on all 20 drafts while every body was wrong" | 🔴 open |
| [[CAPA-2026-08-26-unlabelled-sends]] | "CAPA 2026-08-26 — 20 sends went out unlabelled, and the query meant to catch that returns zero" | 🔴 open |
| [[CAPA-2026-09-01-missing-dossier]] | "CAPA 2026-09-01 — the dossier stopped being produced after one run, and nothing noticed" | 🔴 control applied, awaiting Chris's ratification |
| [[CAPA-2026-09-03-floor-overshoot]] | "CAPA 2026-09-03 — the run drafted 15 new organisations against a prescribed 10, and no rule said stop" | 🔴 proposed — awaiting Chris's ratification |
| [[CAPA-2026-09-30-two-drafts-one-thread]] | "CAPA 2026-09-30 — Zapier attached the kit correctly; Chris attached it by hand anyway, because two drafts sat on one thread" | ✅ closed-by-cutover |
| [[CAPA-2026-10-06-duplicate-sends]] | "CAPA 2026-10-06 — Two fires of the follow-up sender ran at once; 8 orgs received Email 2 twice, 7 minutes apart" | ✅ implemented (L1) 2026-10-06 — containment done (⚠ on 8 threads); verification of effectiveness runs over the next 7 business days (§7) |
| [[CAPA-2026-10-26-missing-attachment-report]] | CAPA 2026-10-26 — "Many outbound drafts don't have the proper attachment" | ✅ CLOSED 2026-10-26 — not a defect (Gmail list view does not show attachment chips on API/Zapier-created drafts until opened); Gate 7 stays in force |
| [[CAPA-2026-10-27-existing-client-in-send-list]] | CAPA 2026-10-27 — existing client (Child Care Aware of Kentucky) reached the Con Outreach send list | 🔴 OPEN — containment done 2026-10-27; corrective code in force; two items need Chris (see "Decisions") |
| [[CAPA-2026-10-28-no-conference-vcoe]] | CAPA 2026-10-28 — "We are not preparing for a conference" (VCOE / [Person 0041]) | 🔴 corrective done · preventive in code · 3 sent threads to watch |
| [[CAPA-2026-10-29-sent-org-retargeted]] | CAPA 2026-10-29 — an org already emailed came back into the research pool (NTI / NCPMI) | 🔴 OPEN — finding recorded by the night run; no code changed |
| [[CAPA-2026-10-30-35-floor]] | CAPA 2026-10-30 (d) — 23 Email 1s today, not 35; how Machine 002 reaches 35 every weekday | 🔴 OPEN — diagnosis done; fixes proposed; two decisions for Chris |
| [[CAPA-2026-10-30-draft-shortfall]] | CAPA 2026-10-30 — The Con Outreach outbox is empty or thin most mornings (target 35) | 🔴 PARTLY BUILT 2026-10-30 — E (night order, timing log) and F (create-failure stall, dossier row) built; supply fixes now flow through THE TAIL verify queue (1,640 rows). A, B, C, D open. |
| [[CAPA-2026-10-30-naaee-missed-contact]] | CAPA 2026-10-30 (c) — NAAEE draft went to info@ while the Event Specialist is on the org's staff page | 🔴 PREVENTIVE BUILT 2026-10-30 · corrective (rebuild the NAAEE draft) waiting for Chris |
| [[CAPA-2026-10-30-verification-throughput]] | CAPA 2026-10-30 — Verification throughput (found orgs don't become pitchable events) | 🔴 CORRECTIVE BUILT 2026-10-30 (V1 queue · V3 two-stage · V4 grantee playbook + no-date → Machine 001 · V5 re-check due-only · V8 stats). V2 changed by Chris: verification runs at night in THE TAIL after the drafts, not by day. V6/V7 open. |
| [[CAPA-2026-10-31-night-run-blocked-by-permission-check]] | CAPA — Night run blocked at step 1 by the scheduled session's permission check | 🔴 open — corrective action awaiting Chris's choice |
| [[CAPA-2026-11-02-apollo-roster-sweep-dropped]] | CAPA — The rebuild dropped the Apollo roster sweep; named people without a published address are never looked up | 🟡 APPLIED 2026-11-02 — verification open (first night run must show submitted > 0) |
| [[CAPA-2026-11-09-weekend-runs-died]] | CAPA 2026-11-09 — Sunday night run and Monday 7 AM send never ran; scheduled tasks died within 4 seconds (usage limit); slot bug R2-4 fixed | 🔴 OPEN — slot fix applied + tested; routing/scheduling changes await Chris |

## Reading order
- Newest first: the 2026-10-31 permission-check CAPA is the live blocker.
- Rules that came out of CAPAs are cited inside `../RULEBOOK.md` by date, e.g. `(CAPA 2026-10-06)`. The rulebook is the rule; the CAPA is the story behind it.

## Writing a new one
`capa/CAPA-YYYY-MM-DD-short-name.md` with the frontmatter fields `status:` and `title:` filled. Nothing else is needed for it to appear here when the index is regenerated.
