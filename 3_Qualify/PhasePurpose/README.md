---
business: Human Skills Training
type: phase-purpose
title: Phase 3 — Qualify: is this org a fit, which machine owns it, and when does outreach open
updated: 2026-11-03
---

# 3 · Qualify

**What it does.** For every organization not yet judged, reads its own web pages and decides three things: **fit** (does it pass its ICP's function test — every answer must be a quote the program finds on the live page), **routing** (which machine owns the org — Rulebook E3), and **timing** (when outreach about an OM-2 event opens — Rulebook F). What happens to a doubtful fit is Rulebook E2. The rules live only in the Rulebook. Excluded organizations (existing clients, Colorado, do-not-contact) are never a fit.

**In → out.**
- In: the master list, the ICP files, the Head Start grantee list, each org's live pages (captured in `runs/<run>/captures/`).
- Out: `ledgers/decisions.jsonl` (the fit decision with its evidence — the builder applies it), `ledgers/ledger.jsonl` (which orgs were checked, which were unreadable, and when to look again), tonight's batches in `runs/<run>/`. Routing and timing are recomputed on every rebuild of the master list as of tonight's date.

**Rulebook it applies.** C (exclusions) · E (qualify and route) · F (timing).

**How to tell it worked.** The pass line: orgs read, fit / doubtful / not fit / unreadable. The master list's `fit` column carries a reason and its source page. OM-2 orgs show `outreach_status` (open now / queued until / quiet until / hold).

**Its CAPAs.** 2026-10-27 an existing client reached a send list · 2026-10-28 "we are not preparing for a conference" (VCOE) · 2026-11-03 Trying Together (same class).

**Programs.** `programfiles/qualify.py` (fit), `programfiles/routing.py` (who owns it), `programfiles/timing.py` (when outreach opens), `programfiles/PROMPT.md`, `programfiles/LAUNCHER-qualify.md`, `programfiles/test_qualify.py`.

**Also run by the Supply Run** (every day ~1 AM MT, Chris 2026-11-08) with its own caps (settings `supply.caps`), run name `supply-<date>`, so the night finds the shelf stocked. Same program, same rules, same ledgers.
