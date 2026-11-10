---
business: Human Skills Training
type: phase-purpose
title: Phase 1 — Read the Inbox: what Gmail says happened, before anything else moves
updated: 2026-11-03
---

# 1 · Read the Inbox

**What it does.** The first thing the night run does, every night. It reads every outreach thread in Gmail — every send, every reply, every bounce, every auto-reply — and writes down the state of each thread. Gmail is the truth of what was sent and when; the master list is corrected from it. It also records successors named in auto-replies ("I've left; contact Jane"), and, once the thread states are known, applies the thread-state labels in Gmail (OM-1/…, OM-2/…) and makes the review-hold replies as Gmail *drafts* on their own threads.

**In → out.**
- In: Gmail (read-only searches and thread reads, saved word for word), the master list as it stood yesterday.
- Out: `ledgers/gmail-state.json` (what is known about every thread), `ledgers/successors.jsonl` (+ the saved auto-replies in `ledgers/successors-raw/`), tonight's label orders and the raw Gmail pulls in `runs/<date>/` and `runs/gmail/<date>/`.

**Rulebook it applies.** B (Gmail is the truth) · C8 (fresh thread check) · J (out-of-office, successors) · K (replies) · L (labels) · M.

**How to tell it worked.** The morning report's first lines come from here: replies, bounces, closes. `gmail-state.json` carries tonight's `as_of` date. The night-run state (`_shared/orchestrator/night/runs/<run>/state.json`) shows `inbox` and `labels` as `ok`. If a reply is missing from the report, this phase missed it: check the raw pulls in `runs/gmail/<date>/`.

**Never.** Sends nothing. Creates no draft except the review-hold replies in the REVIEW step (Rulebook I7), which are drafts, never sends.

**Its CAPAs.** 2026-08-26 unlabelled sends · 2026-10-06 duplicate sends (two fires at once) · 2026-11-03 label trees (the builder read no stage from OM labels).

**Programs.** `programfiles/inbox.py` (reads and ingests), `programfiles/successors.py` (successor rules), `programfiles/LAUNCHER-read.md` (the standing orders). The label orders are printed by the send program in 7_Send; the review-hold drafts are made by the sender program in draft-only mode.
