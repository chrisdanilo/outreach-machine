---
business: Human Skills Training
title: Do-not-contact register (shared by every outreach machine)
created: 2026-10-22
---

# Do-not-contact register

**Rule (Chris, 2026-10-13):** anyone who has explicitly said "do not reach out to me again" is never contacted again by any machine. Permanent and absolute.

This folder sits outside every machine on purpose, so a "stop" said to Machine 001 also stops Machine 002 (and any future machine).

| File | What it is | Who writes it |
|---|---|---|
| `register.jsonl` | Confirmed rows, one per person (or domain). Never rotated, archived or deleted. | **Only Chris** adds or removes a row, by name, in writing |
| `candidates.jsonl` | Rows proposed from a reply ("please remove me…"), with the verbatim quote and thread link | Machines / Claude propose; Chris confirms or rejects |
| `dnc_check.py` | The check every machine runs before any draft | — |

**What the check returns:** `CLEAR`; `HOLD`, meaning a pending candidate (blocks until you decide); or `BLOCKED`, meaning confirmed (blocks forever).

**Scope of a row:** `person` (one address) · `thread_addresses` (everyone on that thread) · `domain` (everyone at that organization's email domain). Never a shared domain like a university or org0038.example. Use the addresses there instead.

**To confirm a candidate:** tell Claude "confirm DNC-C-00X" (optionally with a different scope). Claude moves it into `register.jsonl` with your words and the date.

Seeded 2026-10-22 from Machine 001's records plus a Gmail search of replies to 001's emails for removal language: 4 candidates awaiting you.
