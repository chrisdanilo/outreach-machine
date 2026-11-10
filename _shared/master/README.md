---
business: Human Skills Training
title: The master list — one row per organization, for every outreach machine
status: Stage 2 built 2026-10-31 (rebuild); not yet read by any machine
---

# The master list

**What it is.** One list of every organization the outreach work has ever found, researched, emailed or ruled out: one row per organization, shared by every machine (OM-1, OM-2, and any future one). Each row holds the organization's ICPs, markets, owning machine, fit verdict, exclusions, its events (with links), its contacts, its email threads and where each stands, verbatim notes, and history.

**Which file is the truth.**
- `orgs.jsonl` is the master list. One organization per line.
- `master-list.csv` is a read-only spreadsheet view of it, regenerated on every build. Edits made there are lost.
- **Gmail outranks the list** for what was sent and when (Rulebook B1). Where the list and Gmail disagree, the list is corrected from Gmail on the next build.

**Where it lives.** `settings.json → storage_root`. That is one setting, so the list can move to GitHub or Supabase later without touching the code.

**How to rebuild.** `python3 build_master.py` from this folder. It reads the old machines' files (read-only), the do-not-contact register, the Head Start grantee list, the national CCR&R list, and the Gmail pull saved under `raw/gmail/<date>/`, then rewrites `orgs.jsonl`, `master-list.csv` and `build-report.md`. Same inputs always give byte-identical outputs.

**Fields (per organization).**
| Field | Meaning |
|---|---|
| org_id | Stable id from the organization's main web domain (or name + state when it has none) |
| name, aliases, domains, state, country | Who it is |
| icps, icp_basis | Which ICP(s) it fits and why ("draft" = assigned by a name rule, still to be confirmed) |
| markets | MKT-001 and/or MKT-002 |
| owner_machine | OM-1, OM-2 or none. An existing email thread decides; with no thread, the routing rule decides |
| fit | fit · doubtful · not_fit · unreviewed, with the reason and its source |
| exclusions | existing_client · do_not_contact · colorado · prior_relationship · other, each with its source |
| events | Each event: name, link, last and next edition, attendance, call for speakers, keynote path, when outreach opens |
| contacts | Each address: name, role, evidence page, verification, status (active · bounced · departed · do_not_contact) |
| threads | Each Gmail thread: machine, labels, stage (E1-draft · E1 · E2 · E3), every email sent with date and recipients, status (open · replied★ · closed✗ · hold⏸ · attention⚠), next due |
| notes | Verbatim per-organization instructions carried over from the old machines |
| referrer | true = a warm referrer or source only. Never emailed |
| history, sources | What happened, and which old files contributed |

## Discovery inbox (Stage 4, 2026-10-31)
New organizations and updates found by the discovery engine arrive in `discovery-inbox.jsonl` (append-only; written only by the engine after it checks each helper's results). The builder reads it in order: a find becomes a new org or updates the matching one (same identity rules as everything else), gets first-pass ICP tags with fit "unreviewed" (Stage 5 qualifies), and its events are added — or, when the org already has that event, only the missing facts (exact date, call-for-speakers link/deadline, attendance) are filled in. People with an email printed on a page become contacts (Stage 6 verifies); people without one are kept as notes. Two rows attached to the same Gmail thread are merged automatically (one thread = one org).

## Stage 5 — qualify, route, time (2026-10-31)
- **Fit** comes from the qualify step: helpers read each org's own pages in the Browser pane; every answer must be a quote the script finds on that live page (or, for Head Start grants, in the OHS grantee list in the vault). Decisions land in `qualify-inbox.jsonl` (latest per org wins); the rebuild applies them before Chris's overrides. Excluded orgs (Rulebook C) are not a fit.
- **Routing** (who owns an org) and **timing** (when outreach about an event opens) are computed on every rebuild as of `settings.as_of`: each event gets `outreach_opens` + `outreach_status` (open_now / queued_until / quiet_until / hold / date_unknown); OM-2 orgs get `outreach` (their best event). The night run advances `as_of` each night, so newly due events open on their own.
- Run it: `bin/run.py qualify` prints the standing orders (Stage 8 chains it).

## People (Stage 6, 2026-10-31)
Each org that is a fit, owned by a machine, has no thread yet (and, for Machine 2, whose outreach window is open) gets a people check: up to 4 people chosen by role on the org's own pages, each address checked (on the live page or in the org's own auto-reply · Apollo identity · validity — hold only on a definite invalid). The result lands on the org's row: `recipients` (To, Cc, greeting) when ready, or `people_hold` (why, and what unblocks it). Source: people-inbox.jsonl (latest decision per org wins).
