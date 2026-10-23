---
business: Human Skills Training
title: Outreach Machine 002 — Conference organizers (The Human Conference Design)
status: research side live · drafting waits on the email sequence
created: 2026-10-22
---

# Outreach Machine 002: Conference organizers

A separate machine from the CCR&R machine (`../outreach-machine/`). It has its own files and its own scheduled tasks.

**Today it does one job: keep a database of every early-childhood workforce event, with its 2027 date, the person who runs it, and any open call for proposals.** Drafting emails gets built once you send the three-email sequence.

| Want to… | Do this |
|---|---|
| Refresh the event list | Scheduled tasks → **Conference event refresh (Machine 002)** → *Run now*. Or tell Claude "refresh the event list". |
| See the calendar | Open `events-calendar.generated.md` (regenerated every refresh) |
| See what changed | `runs/<date>/refresh-report.md`; full history in `events-changes.jsonl` |
| Change a rule or setting | `config.json` (settings) · `method.md` (the steps) · `research/SEGMENT-PROMPTS.md` (what research looks for) |

Shared with every machine: `../do-not-contact/` (the permanent do-not-contact register).
