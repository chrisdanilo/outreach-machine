---
business: Human Skills Training
type: phase-purpose
title: Phase 4 — People: find up to four people per org and prove every address
updated: 2026-11-03
---

# 4 · People

**What it does.** For every org that is a fit, is owned by a machine, has no email thread yet (and, for OM-2, whose outreach window is open), finds the right people by role — not by title keyword — and checks every address: it must be printed on the org's own live page (or given in the org's own auto-reply), the person must be real and still there (Apollo), and the address must pass the validity check (hold only on a definite "invalid"). Named people without a published address get the H7 lookup (at most 5 per org, most relevant roles first; a looked-up address counts only when Apollo says Verified, the validity check passes, and it is on the org's own domain). A general inbox may be the To only after the staff page was read and the lookup found nobody. Up to 4 people: 1 To + up to 3 Cc — a ceiling, not a target.

**In → out.**
- In: the master list, each org's live pages (captures in `runs/<run>/captures/`), Apollo lookups (credits are recorded per run).
- Out: `ledgers/decisions.jsonl` — the ONE people ledger (since 2026-11-03): each org's recipient set or the reason it is held, what unblocks it, and when to re-check (`retry_after`); `ledgers/sweep-ledger.jsonl` (every H7 lookup ever made, so nobody is paid for twice); `runs/<run>/credits.jsonl`.

**Rulebook it applies.** G (who to email) · H (verification, H7) · C4 (existing clients by every recipient domain).

**How to tell it worked.** The pass line: ready (recipients + greeting) / held (reason + what unblocks it). The roster-resolution line in the morning report. The master list row shows `recipients` or `people_hold`.

**Its CAPAs.** 2026-08-11 extrapolated address · 2026-08-11 wrong address bounce · 2026-08-17 stale page bounce · 2026-08-18 unqueried roster · 2026-08-24 generic-inbox descent · 2026-10-30 NAAEE missed contact · 2026-11-02 Apollo roster sweep dropped.

**Programs.** `programfiles/people.py`, `programfiles/PROMPT.md`, `programfiles/LAUNCHER-people.md`, `programfiles/test_people.py`.

**Also run by the Supply Run** (every day ~1 AM MT, Chris 2026-11-08) with its own caps (settings `supply.caps`), run name `supply-<date>`, so the night finds the shelf stocked. Same program, same rules, same ledgers.
