---
business: Human Skills Training
type: phase-purpose
title: Phase 7 — Send: tomorrow's approved list tonight, and the 7 AM send of Emails 2 and 3
updated: 2026-11-03
---

# 7 · Send

**What it does.** Two halves. **Tonight**, the night run decides for every open thread whether Email 2 or 3 is due (7 days after the previous one actually went out, business days only, delayed past weekends and holidays, never skipped; stopped by any reply, any stop label, any open draft, or a bounced To) and writes tomorrow's **approved send list** — every row passed every Rulebook check; anything flagged is NOT approved and waits for Chris. The list is final once written. **At 7:00 AM Eastern**, the separate send task — the only thing in the system allowed to send — re-reads each listed thread (a read older than 180 seconds is stale), skips anything that changed overnight, sends exactly the listed email through Zapier, verifies it, and moves the stage label. A bounce rate above 3% stops everything.

**In → out.**
- In: the master list and `1_Read-the-Inbox/ledgers/gmail-state.json`; the machine's data (`_shared/machines/<OM>/contacted.jsonl` — Ledger B, every address ever contacted; a send is refused to an address not in it); the templates; the one settings file (holidays, slot, breaker, machine labels and starter-kit attachment).
- Out: `ledgers/send-lists/<date>.json` + `.md` (the approved list) and `<date>-review.json` (review-hold drafts for the night); `runs/<date>/master-plan.json` (the night's full plan, every thread with its reason); `runs/<OM>/<date>/sender/<fire>/` (every read, the armed rows, every Zapier reply, `followup_sends.json`). These sender files are never pruned: the sender re-reads every past fire for an uncleared DUPLICATE finding (full stop on a duplicate).

**Rulebook it applies.** C (safety, every line) · I (the sequence) · J (out-of-office) · K1 (a reply stops the sequence) · L3 (a stage label moves only after a confirmed send) · M1(b).

**How to tell it worked.** `sendlist.py check` prints LIST OK in the morning. The report's "7 AM send" section: approved N · sent N · not sent N with the engine's reason for each. `--intent` printed GO exactly once per thread, and `raw/zapier_<thread>.json` exists for each send.

**Its CAPAs.** 2026-10-06 duplicate sends · 2026-10-27 existing client in the send list · 2026-10-31 night run blocked by the permission check (the live blocker: 0 of 132 sent on 11/03) · 2026-11-03 the OM-2 fire selected OM-1 rows (fixed in the migration; test added).

**Programs.** `programfiles/seqrules.py` (the calendar and the due/stop rules — also used by the master-list builder), `programfiles/send.py` (plans and exports the night's plan; prints the label orders), `programfiles/sendlist.py` (builds, checks, waits for 07:00, reports), `programfiles/followup_send.py` (the sender: gather → plan → arm → intent → verify), the tests `test_send.py`, `test_split.py`, `test_gapfix.py`. The task's standing orders are `_shared/orchestrator/LAUNCHER-send.md`.
