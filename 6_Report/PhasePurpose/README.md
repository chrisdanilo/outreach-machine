---
business: Human Skills Training
type: phase-purpose
title: Phase 6 — Report: the one morning report, both machines, one screen
updated: 2026-11-03
---

# 6 · Report

**What it does.** The last step of the night run writes the ONE morning report: an executive summary (what sent, what replied, what was drafted, what waits for Chris), then ONE prioritized issues list with CAPA for each (P1 wrong or unwanted contact or a rule broken · P2 lost output · P3 process), then links. No reply list, no step-by-step status (Chris 2026-11-03). Everything else goes to a details file beside it. The 7 AM send task adds its "7 AM send" section to the same report after it runs.

**In → out.**
- In: the master list, the night-run state and timing, the drafts ledger, the send list, the sender's results, the open rulings, the Apollo credit records, the issue seeds the night run collected (every partial or failed step).
- Out: `ledgers/reports/<date>.md` (the report), `<date>-details.md`, `<date>-capa.md` (the issues list the orchestrator writes before the report is rendered), `<date>-timing.md`.

**Rulebook it applies.** B3 and M5 (one report, every machine; questions for Chris go only through the rulings list and this report).

**How to tell it worked.** The report exists for the date, starts with the executive summary, and its links open. The "Open questions" section lists every open ruling once.

**Its CAPAs.** 2026-08-26 HubSpot Bcc non-issue repeated five times · 2026-11-03 report format (fire 1's drafts shown instead of fire 2's).

**Programs.** `programfiles/report.py`, `programfiles/LAUNCHER-report.md`.
