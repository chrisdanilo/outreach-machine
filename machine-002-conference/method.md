---
business: Human Skills Training
title: Machine 002 — Conference organizers — method (the program)
cluster: CL-2026-Q4-Conf (TLP Cluster 002)
status: RESEARCH SIDE LIVE · DRAFTING NOT BUILT (waits on the 3-email sequence)
updated: 2026-10-22
---

# Machine 002: Conference organizers (the method)

**What it sells:** The Human Conference Design. Chris co-designs and MCs an organization's own annual early-childhood conference for $6,000 flat.
**Who it targets:** any organization that owns and runs a recurring event for an adult early-childhood workforce audience, all organization types in one bucket.
**What it tracks:** each **event** is one record, not each organization.
**Separate from Machine 001:** it has its own folder, files and scheduled tasks, and shares no writable file with Machine 001. The one shared piece is the do-not-contact register in `../do-not-contact/`.

## Rulings this program carries (Chris)

| Date | Ruling |
|---|---|
| 2026-10-13 | One machine per cluster, each with its own scheduled task that can be turned on and off independently. The event, not the organization, is the unit of work. |
| 2026-10-13 | Anyone who explicitly said "do not reach out to me again" is never contacted by any machine. This is permanent. |
| 2026-10-19 | Conferences that only take breakout presenters, with no external keynote path, are not targets (from the NAA27 pass). |
| 2026-10-20 | All organization types go in one bucket, worked in order of event date rather than by state or type. Each event's 2027 month comes from the confirmed date if one is posted, otherwise the same month as its last dated edition. Outreach goes about 6 months ahead. Start now with events in January–May 2027. Nothing in 2026; October 2027 is fair game. |
| 2026-10-20 | The refresh runs the same way whether started by a button or a schedule. It finds new events, re-checks every listed event's website for a 2027 date, fills gaps, and flags open calls for proposals or RFPs. |

## Files

| File | What it is |
|---|---|
| `events.jsonl` | **The event database, the single source of truth.** One event per line, with the fields defined in `research/SCHEMA.md` plus the computed fields below. |
| `events-changes.jsonl` | History log: every field that changed, on which run, from what to what, and why. It is only ever added to. |
| `events-retired.jsonl` | Events taken out of the database (duplicates, vendor-run events, non-events), each with the reason. Nothing is ever deleted: `python3 bin/events.py retire <id> --why "..."`. |
| `events-calendar.generated.md` | A read-only view of the database for review, regenerated on every refresh. Never edit it by hand. |
| `config.json` | Every setting and ruling the scripts use. |
| `bin/events.py` | The scripts that merge research, compute waves, validate and write reports. No web access, no judgment. |
| `research/SCHEMA.md`, `research/SEGMENT-PROMPTS.md` | The research instructions the refresh uses. |
| `runs/<date>/` | Each refresh's raw research files, the database as it stood before the merge, and the refresh report. |
| `LAUNCHER-event-refresh.md` | Record copy of the instructions stored in the refresh scheduled task. |

## Fields the scripts compute (never set by research)

| Field | How it's set |
|---|---|
| `event_month` | Taken from `date_2027`. |
| `wave` | `wave_1`: event in January–May 2027, outreach open now. `rolling_open`: the window opened 6 months before the event and has already passed. `rolling_later`: the window opens later. `date_unknown`: no dated edition found. `skip_before_2027`. |
| `outreach_opens` | Event month minus 6 months; for Wave 1, the current month. |
| `notice_months` | Months between today and the event. |
| `machine_001_status` | Whether Machine 001 already emailed this organization, and its status there, matched on the website domain. Read-only lookup in `../outreach-machine/contacted.jsonl`. |
| `colorado` | True for Colorado events. Machine 001 reserves Colorado for Chris; that ruling is still open for Machine 002. |
| `dnc` | True if the person in charge's email or the organization's domain is on the do-not-contact register. |

## THE REFRESH: the same steps every time

1. **Mount.** If the vault isn't reachable, stop and say so.
2. **Run folder.** `RUN=YYYY-MM-DD`. If a folder for today exists, add `-2`, `-3` and so on.
3. **Re-check lists.** Write `python3 bin/events.py worklist --segment <segment>` for each segment in `config.refresh.research_segments` to `runs/$RUN/recheck_<segment>.jsonl`.
4. **Research.** 🔴 One run gets **200 web searches in total, shared by every agent** (learned 2026-10-22, when the first build ran out halfway). Each agent re-checks its known events by opening their pages, which costs no searches, and spends its share of about 20 searches on finding new events. Launch one Sonnet research agent per segment, all at once. Each gets the common block and its segment block from `research/SEGMENT-PROMPTS.md`, the path to `SCHEMA.md`, its re-check list, and its output path `runs/$RUN/<segment>.jsonl`. The agents work in the cloud, so their output files are copied into the run folder unchanged.
5. **Merge.** Run `python3 bin/events.py merge runs/$RUN/*.jsonl --run $RUN`. It keeps a copy of the database as it stood before the merge, then applies these rules:
   - A confirmed date beats an estimate, which beats unknown. A newer confirmed date replaces an older one.
   - The newest reading of a call for proposals wins.
   - Empty fields get filled. Sources are combined.
   - Every change is logged in `events-changes.jsonl`.
6. **Waves.** `python3 bin/events.py waves`. This step also marks any open call whose deadline has passed as closed.
7. **Validate.** `python3 bin/events.py validate`. Any FAIL is reported and fixed before the report.
8. **Report.** `python3 bin/events.py report --run $RUN` writes `runs/$RUN/refresh-report.md` and `events-calendar.generated.md`. In chat, Chris gets:
   - open calls, soonest deadline first
   - new events
   - dates newly confirmed or moved
   - the gaps left
   - links to the two files

**The refresh never** sends or drafts email, edits Machine 001's files, guesses an email address, or writes a date without a source URL.

## Drafting (Email 1, then Emails 2 and 3): NOT BUILT YET

This waits on Chris's three-email sequence. When it arrives, the build will:
- copy Machine 001's verify, check and draft steps, adapted to events
- add the event-specific gates:
  - the event must have a keynote path
  - if the keynote is already announced, the event waits for the following cycle
  - events that buy by RFP go to a separate bid lane
  - the do-not-contact check runs first
- set up its own nightly drafter task and its own follow-up sender task, so it never shares a task with Machine 001

Rulings still open are listed in `config.json → drafting.open_rulings`.

## Recipients — the thread rule (Chris 2026-10-23)

Machine 001's rule carries over: **1 in To, at most 2 in Cc, three people never four.** The greeting names every first name on the thread (Email 1 bare names; Emails 2–3 `Hey …,`). The Cc is insurance: if one address bounces, two people remain who can hold each other to replying.

| Slot | Who |
|---|---|
| **To** | The person who owns the event — conference chair, Director of Events / Conferences / Professional Learning, or the ED when the ED runs it |
| **Cc #1** | The budget-holder (ED / CEO / President / Superintendent / Head of School / Dean) when not already the To |
| **Cc #2** | The second person the org's own pages tie to the event — program/events coordinator, committee chair, PD director, division director |

Selection pool = everyone named on the **event page** plus the staff/leadership page; the event page outranks the staff page. Every address passes Check 1 (named on the org's own site) and Check 2 (Apollo/validator); unpublished addresses for qualifying people are looked up before the thread is built. Generic inboxes are tier 4, never an exclusion. Bounces on Email 1 get the parenthetical line on Email 2/3, as in Machine 001.

Round 0 (2026-10-23) was first drafted single-recipient; Chris chose to rebuild the nine threads with Cc recipients before sending.
