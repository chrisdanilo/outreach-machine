# The Outreach Machine

**An AI-run cold-outreach system for a one-person consulting business — the method, the scheduled-task instructions, and the scripts, shared so you can copy it.**

Built by Chris Danilo for [Human Skills Training](https://chrisdanilo.com), run with Claude (Anthropic's Cowork / Claude Code), Gmail, HubSpot, Apollo and Zapier. Everything in this repo is the live system as of the sync date below, with identifying information removed (see *Redaction*).

| | |
|---|---|
| **Last synced from the live system** | 2026-10-23 |
| **What changed since the previous sync** | [`CHANGES-SINCE-LAST-SYNC.md`](CHANGES-SINCE-LAST-SYNC.md) |
| **Questions** | chris@chrisdanilo.com |

---

## 1. What it is, in one paragraph

Every night a scheduled task wakes up Claude, which reads one file — `method.md` — and executes it top to bottom. The run checks the mailbox (what was sent, what bounced, who auto-replied, who replied), decides which follow-ups are due, researches a fixed number of new organizations in one state at a time, finds the right person at each one from the organization's own website, writes a three-email sequence to that person, and leaves the drafts in Gmail. Chris reviews the drafts and sends Email 1 himself; Emails 2 and 3 are sent by the machine on schedule. Every number the run reports is computed by a Python script from files on disk, never recalled from memory, and every run writes a review file and a dossier so the next run — and a human — can check its work.

The target market is [Org 0272] & Referral agencies (CCR&Rs) across the United States, sold a professional-development workshop. Swap the market, the copy, and the directory sources and the machine runs for something else. A second, smaller machine (`machine-002-conference/`) uses the same pattern to keep a database of conferences and their organizers.

## 2. Why it looks the way it does

This started in mid-2026 as "Claude, go find CCR&Rs and draft emails," run entirely by a language model. It failed in the ways you'd expect: it extrapolated an email address and bounced it, it changed approved copy on its own, it cited a page that didn't say what it claimed, it drafted to four people when the limit was three. Each failure got a written CAPA (corrective and preventive action — the `CAPA-*.md` files) and a rule.

By late August the rules had outgrown what a prompt can hold reliably, so the architecture was rebuilt around one idea (`ARCHITECTURE-v2.md`): **the model's job is judgment; everything countable is a script.** The run is split into phases ordered by what they can destroy (gather → compute → gate → act → record), the state lives in JSON ledgers that Markdown is generated from, and scripts in `bin/` do the counting, the de-duplication, the gate checks, and the integrity check at the end. The method file is still the program the model executes — but it is being made smaller, not larger, as each rule moves into code.

The design principles, each of which was learned the hard way:

- **Fail closed.** Any uncertainty — an address that won't verify, a rule that doesn't obviously apply, an ambiguous reply — holds the draft and labels it for Chris. The machine never breaks a tie in its own favor.
- **Contact an organization once.** One org, one thread, forever. Enforced in code (`bin/dedup_check.py`), checked against two ledgers.
- **Provenance before verification.** An address is only used if it appears on the organization's own website. Vendor lookups (Apollo, a validator) confirm; they never originate.
- **Copy is frozen.** The machine never edits the approved email text. Changes Chris makes by hand are logged (`bin/learn_diff.py`) and surfaced, never auto-applied.
- **A floor, not a cap.** Each run must draft a fixed number of *new* organizations (`config.target_drafts`) or name the safety gate that stopped it. "Zero owed" is not a reason to draft nothing.
- **One territory at a time.** States are worked in a declared order to saturation (`territory.json`, `bin/territory_check.py`), so coverage is systematic and auditable.
- **Every number is computed.** Bounce rate, funnel conversion, queue health, run integrity — all scripts, all reading files, all printed verbatim into the report.
- **Bounded retries.** No loop runs forever at 3 a.m. A stall exits with a named reason, which is a report line, not a crash.

## 3. How a night runs

The authoritative version is `method.md` §0.3 (a 22-step table). In plain language:

| Phase | What happens | Reversible? |
|---|---|---|
| **Gather** | Snapshot the ledgers (`bin/run_snapshot.py`). Refresh the HubSpot suppression list (existing relationships are never cold-emailed). Sweep Gmail: sent mail (3 days), bounces (7 days, whole mailbox), auto-replies (60 days), open drafts — always *unfiltered first, then filtered*, so nothing that escaped a label is missed. Read every reply and classify it (★ interested / ✕ decline). | Yes |
| **Compute** | Scripts only, no API calls: reconcile the sent sweep against the contacted ledger (`bin/ledger_reconcile.py`), bounce rate (`bin/bounce_rate.py`), which follow-ups are due, queue health. | Yes |
| **Gate** | Is the suppression list fresh? Is the bounce rate under the circuit breaker (3%)? Is the ledger reconciled? Each lane (follow-ups, new orgs) gets its own GO / NO-GO with a named reason. | Yes |
| **Act — follow-ups** | Emails 2 and 3 are fully deterministic: same recipients as Email 1, frozen copy, sent by `bin/followup_send.py` on the +7 / +7 day schedule unless a human has replied, a bounce landed, or an out-of-office is active (five explicit rules in `method.md` §0.14). | Sends are not reversible — hence the gates |
| **Act — new organizations** | Loop until the floor is met: take the next organizations in the active state → check both ledgers (`bin/dedup_check.py`) → read the org's own staff page → pick recipients by role using the rank list in `recipient-profile.md` (1 To, up to 3 Cc) → verify the address → run the pre-flight assertions (`method.md` §0.4, mirrored in `bin/preflight.py`) → create the Email 1 draft via Zapier with the flyer attached. Anything that fails a check is held with a reason and a retry date in `candidates.jsonl`, so research is never repeated. | Drafts are deletable |
| **Record** | Append to the JSON ledgers, regenerate the Markdown views, write `review-<date>.md` (what was decided and why) and `dossier-<date>.md` (the file Chris opens to send from — fixed layout, every evidence URL a live link). | Additive |
| **Check** | `bin/run_integrity.py` proves the run delivered what it claims: every declared output exists, the drafts recorded match what the mailbox actually holds, the territory walk is in order. Then the report, then the dashboard render. | — |

A weekly task (`LAUNCHER-hubspot-cleanup-weekly.md`, `bin/hubspot_cleanup.py`) tags bounced and departed contacts in HubSpot for deletion. A replay harness (`bin/replay.py`) re-runs every script against recorded runs so a change to a script can be regression-tested before it goes live.

## 4. The stack

| Tool | Role |
|---|---|
| **Claude (Cowork scheduled tasks)** | Runs the nightly program; makes the judgment calls (which person, is this reply a yes, does this rule apply) |
| **Claude Code / Python 3** | The deterministic parts: every script in `bin/` |
| **Gmail** (via connector) | The ledger of record for what was actually sent; drafts live here for human review |
| **Zapier** | Writes the drafts and sends follow-ups (the Gmail connector could not reliably create multi-recipient drafts with attachments) |
| **HubSpot** | CRM; its contact list is the suppression list (never cold-email an existing relationship) |
| **Apollo** + an email validator | Address verification only — never the source of an address |
| **Fathom** | Meeting detection (did an outreach turn into a booked call?) |
| **Obsidian vault** | Where every file in this repo lives on Chris's machine; Markdown views are generated from the JSON |

## 5. What's in this repo

```
README.md                      ← you are here
CHANGES-SINCE-LAST-SYNC.md     ← diff of this sync vs. the previous one
method.md                      ← THE PROGRAM. §0 is what runs; everything after §0 is the reasoning archive
method-rationale.md            ← why the method is shaped this way
ARCHITECTURE-v2.md             ← the rebuild: four layers, six phases, three loops
ADR-2026-08-25-*.md            ← the decision record for the rebuild
ROADMAP-thin-launcher.md       ← the plan for shrinking the launcher to a pointer
CHANGELOG.md                   ← one line per change to rules, settings or scripts
config.json                    ← every number and ruling (targets, caps, labels, policies). Data lists redacted
territory.json                 ← the state-by-state walk: order, status, what's left
discovery-pipeline.md          ← how organizations are found: directory sources, what blocked, what worked
recipient-profile.md           ← who belongs on a thread: the rank list and the learning loop behind it
dossier-template.md            ← the fixed layout of the nightly send file
decline-reply-templates.md     ← how declines are answered
LAUNCHER-*.md                  ← the scheduled-task prompts, verbatim (the thin one is live; the fat one is the rollback)
CAPA-*.md                      ← every failure, its root cause, and the rule it produced (25 of them)
handoffs/                      ← prompts written for delegated sub-tasks
bin/                           ← the scripts (23). Each one's docstring says what it computes and why it exists
machine-002-conference/        ← the second machine: conference and organizer research, same pattern
shared/                        ← the email sequences (the actual copy) and the do-not-contact register's README
MANIFEST.txt                   ← the list of files that belong in this export
```

Not included, by design: the ledgers themselves (`contacted.jsonl`, `candidates.jsonl`, the HubSpot suppression list), the nightly run folders, dossiers and review files — they are data about real organizations and people.

## 6. How to copy it

1. **Read `method.md` §0 first.** That is the entire runtime program. The rest of the file is the archive of why each rule exists; read it when a rule surprises you.
2. **Read `ARCHITECTURE-v2.md`** for the shape: phases, loops, lanes, and the rule that Markdown is generated from JSON, never the other way round.
3. **Set up the ledgers empty:** `contacted.jsonl`, `candidates.jsonl`, `warm.jsonl`, a `territory.json` with your geography, and a `config.json` with your own targets. The scripts in `bin/` read these paths relative to the machine folder (see the `ROOT` line at the top of each script).
4. **Write your own copy** into `shared/Cold-Outreach-Sequence-*.md` format — three emails, Day 0 / +7 / +7 — and freeze it. The machine must never edit it.
5. **Install the thin launcher** (`LAUNCHER-thin-PROPOSED.md` §3) as a scheduled task. It is ~250 words and states no rule; it points at `method.md` so there is [Org 0934] to edit.
6. **Run in shadow first.** Several scripts (`preflight.py`, `territory_check.py`) were installed in *shadow mode* — printing verdicts beside the model's own for three runs before their holds became binding. Do the same.
7. **Expect to write CAPAs.** The 25 here are the real curriculum. Each one is short: what happened, the root cause, the rule, how the rule is verified.

## 7. Redaction

This is a public copy of a private system. Before publishing, a script replaced every identifying item with a stable placeholder:

- Real people → `[Person 0123]`; organizations → `[Org 0456]`; their web domains → `org0456.example`
- Email addresses → `person0123@org0456.example` (generic inboxes keep their local part, e.g. `info@org0456.example`)
- Phone numbers → `(555) 010-0142`; Gmail thread IDs → `<thread-id>`; HubSpot portal and owner IDs, sender addresses, webhook and Drive URLs → named placeholders
- `config.json` lists that hold real addresses or domains (bounce lists, domain aliases, shared-tenant domains, never-contact lists) → one-line notes saying how many entries were removed

The same placeholder always stands for the same real item, so cross-references inside the documents still hold. The method, the rules, the copy, the prospecting criteria and the code are unchanged. If you spot something that slipped through, email chris@chrisdanilo.com and it will be fixed in the next sync.

---

*Instructed by Chris Danilo, written by Claude. Set up like this for speed and your convenience. If you want to speak directly to Chris, you can email him here: chris@chrisdanilo.com.*
