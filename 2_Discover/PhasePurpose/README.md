---
business: Human Skills Training
type: phase-purpose
title: Phase 2 — Discover: find the organizations and events we do not know yet
updated: 2026-11-03
---

# 2 · Discover

**What it does.** Looks for new organizations and events that fit the active ICPs, one night at a time, without ever repeating a search. It keeps a list of places to look (state directories, association directories, conference calendars, keynote speakers' pages, and every event page already on the master list), sweeps the ones that are due, and follows what it finds outward: a keynoter → the other events she spoke at; a sponsor → its own events. Every find lands on the master list tagged with the ICPs it fits; nothing is thrown away.

**In → out.**
- In: `ledgers/sources.jsonl` (the one list of places to look, with when each was last swept), `ledgers/keynoters.jsonl`, `ledgers/search-log.jsonl` (every search ever run — never repeated), the master list, the ICP files in `Ops/Reference/ICP/`, OM-1's territory map (`_shared/machines/OM-1/territory.json`).
- Out: `ledgers/finds.jsonl` (every organization, event and person found — the builder reads it into the master list), the sweep ledgers updated, tonight's batches and results in `runs/<run>/`.

**Rulebook it applies.** D (one discovery engine, follow finds outward, no search repeated, sources are never emailed).

**How to tell it worked.** The pass line in the morning report: sources swept, orgs found (new vs already known). `runs/<run>/state.json` lists every batch and whether it was ingested. "Nothing due" is a normal outcome, not a failure.

**Its CAPAs.** 2026-10-29 a sent org came back into the research pool · 2026-10-30 verification throughput (found orgs did not become pitchable events) · 2026-10-30 draft shortfall (supply).

**Programs.** `programfiles/discover.py`, `programfiles/PROMPT.md` (what each research helper is told), `programfiles/LAUNCHER-discover.md`.

**Also run by the Supply Run** (every day ~1 AM MT, Chris 2026-11-08) with its own caps (settings `supply.caps`), run name `supply-<date>`, so the night finds the shelf stocked. Same program, same rules, same ledgers.
