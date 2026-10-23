---
business: Human Skills Training
type: CAPA
title: "CAPA 2026-08-17 — FIRST machine-passed hard bounce: a fetch returned a stale version of a live staff page"
status: open-needs-chris
owner: Chris Danilo
date: 2026-08-17
severity: critical
related: ["[[method]]", "[[verification-log]]", "[[STATE]]", "[[batches/2026-08-17]]"]
---

# CAPA — the first hard bounce from an address the machine passed

## The headline, stated plainly

**`person0936@org0323.example` hard-bounced — "Address not found" — and the machine put it there.**

Both previous bounces (`person0174@org0174.example` 08-11, `person0866@org0654.example` 08-12) were
human-override addresses. **The "machine-passed addresses: 0 bounces" record, printed in every report
since 08-11, is now broken and must stop being printed.** It is 1 bounce in 31 machine-passed
addresses across the machine era.

## What happened

McKenna Terrill, "Workforce Coordinator," was placed in Cc at [Org 0548]. The
evidence recorded on her dossier card was that her name, title, direct phone and plain-text address
were read in the Employee Directory at `https://www.[Org 0578]/contact` during this run. Chris sent at
15:22 UTC; Google returned "Address not found" 16 seconds later.

## Root cause — the fetch returned content that was not the live page

The same URL was fetched twice today, about 3.5 hours apart. **The two responses return materially
different staff rosters.** This is the decisive evidence:

| | First read (~12:04 UTC, used for the draft) | Re-read (~15:4x UTC, after the bounce) |
|---|---|---|
| McKenna Terrill, Workforce Coordinator, `person0936@org0323.example`, phone (555) 010-0140 | **Present** | 🔴 **ABSENT — the role does not exist on the page at all** |
| Phone (555) 010-0140 | McKenna Terrill | **[Person 0292], Marketing and Resource Development Coordinator, `person0593@org0323.example`** |
| Director of Community Engagement | [Person 0471] | **[Person 0544]** |
| Supervisor of Developmental Health | [Person 0634] | **role gone; [Person 0199] is now Director of Developmental Health** |
| Director of Financial Services | [Person 0383] | **role gone; [Person 0461] is Director of Administrative and Financial Services (Interim)** |
| Offices listed | Daytona Beach, DeLand, Deltona, Palm Coast | **Daytona Beach, DeLand, Palm Coast** |
| Page structure | Flat text, no site navigation, no "Employee Anniversaries" section | Full render with navigation folders and an Employee Anniversaries section |

**An organisation does not reassign a direct-dial number, replace two directors and close an office in
three and a half hours.** The only consistent explanation is that **the first fetch served a stale
cached copy**, and the second is the live page. The bounce independently corroborates the second: her
mailbox no longer exists because she no longer works there, and her phone number has been reissued.

**So the failure is not "we trusted a directory" or "we guessed a pattern." It is subtler and more
dangerous: the machine believed it had read a live page this run, and the 08-13 rule
("cite only pages this run opened") was satisfied in letter while being false in substance.**

## Why every existing control passed

| Control | Why it missed |
|---|---|
| Check 1, live-page exception | The address was printed as plain text on what appeared to be the employer's own live staff page — the strongest evidence class the method recognises, sendable on Check 1 alone |
| "Cite only pages this run opened" (08-13) | The page **was** opened this run. The rule assumes a fetch returns current content. It has no freshness test |
| Printed-text vs `mailto:` conflict check | No conflict — the stale page was internally consistent |
| Check 2 / vendor verification | **Never run for her.** She passed on Check 1 alone, which the method explicitly permits |
| Pre-send self-check | Asked "what source saw this address, and when" — answered with a URL and today's date. Both true of the cached copy |

## The uncomfortable finding

**Check 1 alone is weaker than the method assumes, because "live page" is an assumption about the
transport, not an observed property of the content.** Three of tonight's seven orgs had pages carrying
`article:modified_time` metadata that could be read and reported (ELCPH: 2026-08-06; Big Bend:
2026-05-21). **ELCFV's page carries no modification date at all** — and that is precisely the page
that was stale.

## Corrective action — taken now

- **`person0936@org0323.example` added to the suppression list** with date and reason.
- **Circuit-breaker re-verification of every other address from the same source, COMPLETED:**
  - **[Person 0018], Chief Program Officer, `person0059@org0323.example` (To)** — ✅ **re-confirmed on the
    live page**, same title, same address, same phone. Also named in that page's 15-year service list.
  - **[Person 0514], Director of Quality Impact, `person1000@org0323.example` (Cc)** — ✅ **re-confirmed on
    the live page**, same title, same address, same phone. Named in the 10-year service list.
  - **Conclusion: the live ELCFV thread is sound. No further action needed on that send.**
- Bounce source audited and siblings re-verified, so **the breaker is CLEAR** and drafting may
  continue.

## Preventive action — proposed, NOT self-applied

**P1 — Report a freshness date for every Check-1 page, or say there isn't one.** Where a page exposes
`article:modified_time` or similar, record it on the dossier card (already done tonight for ELCPH and
Big Bend). **Where a page exposes no modification date, say so on the card** — that is a materially
weaker citation and the card should show it.

**P2 — Require Check 2 for any Check-1 page with no verifiable freshness date.** This is the narrow
version of the fix and the one I would recommend: it does not weaken the live-page exception
generally, it only removes it for pages that cannot demonstrate currency. A single vendor match would
have flagged Terrill as absent for ~1 credit, against a 25-credit nightly budget of which 15 went
unspent tonight.

**P3 — Fetch twice for a first-contact page, or check one corroborating signal.** Cheaper variant:
where a directory publishes direct phone numbers, a reassigned number is a strong departure signal —
Terrill's number appearing against a different person is exactly what exposed this.

**P4 — Stop printing "machine-passed addresses: 0 bounces."** It is no longer true, and a metric that
flatters the machine is worse than no metric. Replace with the honest form: **1 bounce in 31
machine-passed addresses (~3.2%)**, which sits **at the `max_bounce_rate_pct` of 3** and therefore
deserves watching, not celebrating.

## Second bounce the same hour — Chris's own, and easily fixed

`ccr@org0315.example` also hard-bounced ("Address not found"). That address was **added by Chris at
review**, not by the machine. **The organisation's own staff directory publishes `ccrr@org0315.example`
— with two R's, for [Org 0272] and Referral.** A single missing letter. The intended
recipient is reachable at the correct spelling, and `resources@org0315.example` in Cc did not bounce,
so that thread did reach the organisation.
