---
business: Human Skills Training
type: vocabulary
title: Vocabulary — the words the outreach system uses, and the ones it does not
status: rulings of 2026-11-03 (Chris); read with RULEBOOK.md §A
---

# Vocabulary

| Say | Never say | Meaning |
|---|---|---|
| **Machine** (OM-1, OM-2) | lane, pipeline | One outreach machine serving one cluster. Every machine runs the same engine under the same Rulebook; only its block in the one settings file differs. |
| **Method** | — | Reserved for Thought Leaders delivery modes only: Speaker, Author, Trainer, Mentor, Facilitator, Coach. Never the name of a process or a program. |
| **Phase** | step, stage (for folders) | One of the seven numbered folders, in the order the night runs: 1 Read the Inbox → 2 Discover → 3 Qualify → 4 People → 5 Draft → 6 Report → 7 Send. A failed step maps to its folder. |
| **Night run** | nightly, the engine | The Sun–Thu 8:41 PM MT scheduled task. It never sends. |
| **7 AM send** | morning sender | The Mon–Fri 7:00 ET scheduled task — the only thing that sends, and only Emails 2 and 3 from the approved list. |
| **Approved send list** | queue | What the night run wrote for tomorrow after every Rulebook check. Flagged = not approved. Final once written. |
| **Ledger** | log, inbox | A phase's decisions, kept for good (`<phase>/ledgers/`). |
| **Run files** | scratch, temp | A phase's working files and page captures for one night (`<phase>/runs/`), pruned after 3 days. |
| **Master list** | database | `_shared/master/orgs.jsonl` — one row per organization, rebuilt every night from the ledgers. `master-list.csv` is its read-only view. |
| **The one settings file** | config | `_shared/master/settings.json`. Shared sections plus one `machines` block per machine with identical keys. |
| **Ruling** | decision, ticket | A question for Chris and his answer, in the one log `0_Design-and-Purpose/decisions/rulings.jsonl` (`machine` = OM-1, OM-2 or shared). |
| **CAPA** | bug, incident | What went wrong, its containment, correction and prevention — `0_Design-and-Purpose/capa/`. CAPAs propose; Chris disposes. |
| **Seeds** | legacy inputs | Read-only files from the old machines that the master-list builder still reads (`_shared/master/seeds/`). Never archived, or the rebuild drops ~1,600 orgs. |
| **Orchestrator** | runner, scheduler | `_shared/orchestrator/` — the programs that sequence the night, hold the locks, and print the standing orders. |
| **Launcher** | prompt, task text | A `LAUNCHER-*.md` file: the standing orders a scheduled task or a step prints and follows word for word. |

Terms from the Rulebook (§A) still apply unchanged: ICP, Market, Cluster, Source, Business day.

The names people may still use in old records: *engine* (the Oct 26 rebuild folder), *lane* (until 2026-11-03), *Machine 001 / 002*, *CCR&R outreach / Con Outreach* (the old Gmail label trees, retired 2026-11-03).
