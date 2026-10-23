---
business: Human Skills Training
type: machine-dashboard
title: Discovery Pipeline — what we're looking for, where we've looked, and what we found
status: active
owner: Chris Danilo
updated: 2026-08-20
related: ["[[method]]", "[[STATE]]", "[[verification-log]]", "[[sequence-tracker]]"]
---

# Discovery Pipeline

**This is the one file to open when you want to know how lead-finding is going.** The nightly run
updates it every time. Everything here is written to be readable without opening any other file.

---

## 1 · What counts as a lead — the criteria

An organization qualifies when ALL of these are true:

1. **It's a real CCR&R or equivalent** — a staffed agency doing child-care resource & referral,
   training, or quality improvement. Judged by function, not by web address: a `.gov` agency with
   real staff qualifies; a lookup-tool website with no staff does not.
2. **It's not in CO, KY, or GA** — those states are Chris's to work personally, never auto-drafted.
3. **Chris has no existing relationship** — checked against four lists: past manual outreach, past
   machine outreach, HubSpot (customers, open/lost deals, real correspondence), and Apollo history.
4. **We can name the right people** — a decision-maker (ED/CEO/President) for the To line, and
   ideally a training/PD/coaching/quality person for the Cc (that's the person who actually buys
   training — the "wedge buyer").

A **person** on a thread additionally needs a **verified email address**, which means passing the
two checks below.

## 2 · The two checks every address must pass

Plain-English version (the formal rules live in [[method]]):

| Check | Question it answers | What passes |
|---|---|---|
| **Check 1 — "Did we see it?"** | Is this person, with this title and this address, on the org's OWN current website? | A live staff page showing name + title + address (printed text or a mailto: link — Chris's ruling, 2026-08-12). We record the URL, the exact quoted line, and the date |
| **Check 2 — "Does the mailbox work?"** | Does Apollo (our data vendor) confirm a working mailbox at that address? | Apollo returns the address with status "verified" |

**Passing rules:** a live staff page alone is enough to draft (Check 1 solo). Apollo alone is NOT
enough to draft — we won't email someone we can't see on their employer's own site, because vendor
data goes stale (~8% of a year-old list had left their jobs). An address that appears nowhere and
was guessed from a pattern — by us OR by the vendor — never sends. That's what hard-bounced on
Aug 11.

## 3 · Where we've looked — the state-by-state map

**Search order logic — VALUE-ORDERED (Chris's ruling, 2026-08-12).** New territory is worked in
order of expected business value, not ease of scraping. This restores the ordering the engine spec
originally proposed (§13.6), which had drifted into "easiest states first" during the sweeps. Value
means, in priority order: (1) states where HST already has customers or open deals — warm ground;
(2) biggest child-care markets — more orgs, bigger budgets; (3) everything else, cheapest first as
a tiebreaker. CO/KY/GA excluded (Chris works those personally), IN excluded (state sunset its
CCR&R network Oct 2025).

### Swept (31 states) — initial discovery done, orgs identified

CO* · GA* · KY* · CA · WA · OR · NV · AK · HI · SC · ME · NM · MS · UT · AZ · **NY** · NJ · PA ·
IL · OH · MI · TN · WI · MA · AL · VA · WV · VT · KS · **FL (opened 2026-08-14)**
&nbsp;&nbsp;*(\* = found but reserved for Chris)*

> 🆕 **FLORIDA OPENED 2026-08-14 — and it is the best-publishing state found so far.** The
> statewide association publishes all 30 coalitions with their own websites, so the org list came
> free in one fetch. **9 coalitions were read on night one; 7 produced sendable drafts.** That is a
> ~78% conversion from page-read to draft, against roughly 1-in-5 in New York. **Reason: Florida
> coalitions publish staff directories with plain-text addresses** — Orange County publishes ~50
> addresses with direct phone numbers, Seminole publishes ~20, Duval publishes 19. **21 FL
> coalitions remain unread. On tonight's rate that is roughly 15 more drafts, or two more nights.**

### Up next, in VALUE order

**Standing rule first: new-territory discovery only runs after the night's 7-draft target is met
or the almost-ready queue (Stage C) is exhausted.** Converting already-found orgs into drafts
always outranks finding new ones.

| # | Territory | Why it's ranked here (the value case) | Est. nights |
|---|---|---|---|
| 1 | ⚠️ **PA — return pass** (19 ELRCs) — **smaller than it looks, see below** | 🔥 Warm ground on paper: 1 paying customer ([Org 0106] IU) + 2 open deals already in PA. **But a 2026-08-13 check found most of the network is already spoken for** — the CSC-operated regions (11–16, `org0237.example`) sit on Chris's own do-not-contact list from his 2026 manual outreach, and PHMC (Regions 18/19) plus Community [Org 0434] (Regions 9/10) were both drafted in the batch that was later deleted, so the org-level dedup rule flags them for a human call rather than an auto-draft. **Realistic yield: 2–4 orgs, not 13** | 1 |
| 2 | 🔺 **FL** (30 Early Learning Coalitions) — **recommend promoting to #1** | Biggest single prize on the board: 30 staffed regional orgs, 3rd-largest child-care market, and on the revised PA math above it is the largest genuinely-untouched block anywhere | 4–5 |
| 3 | **TX** | 2nd-largest market. Probe first (3 agencies in 8 fetches), then full sweep if the shape is real | 1 + follow-up |
| 4 | **CA — return pass: Los Angeles County** | Largest single county child-care market in the country; [Org 0444], [Org 0963], CCRC-LA, MAOF never surfaced in the CCAoA sweep — source from org0637.example / CDE's directory | 1–2 |
| 5 | **NC** | Large, rich, fragmented network | 3–4 |
| 6 | **MN · MD · MO** | Mid-size regional networks | 2 each |
| 7 | **IA · OK · AR · LA · MT · ID** | Small regional networks | 1–2 each |
| 8 | **CT · DE · NH · RI · DC · NE · ND · SD · WY** | One statewide org each — low value, near-zero cost. Filler only. ⚠️ CT first needs a 1-fetch check: its R&R function may run through United Way's 211 portal (no staff = disqualified by function) | 1 each |

*(NY isn't in this queue because its return pass is already underway as Stage C below — that IS
the current work.)*

**Note — this changed on 2026-08-13.** The line that used to sit here said the highest-yield work was
finishing the 17 NY orgs in Stage C. **That work is now done.** All 17 pages have been read, Stage A
is empty, and what remains in Stage C is blocked on human judgement rather than machine effort. **The
highest-yield work is now a new state**, and on the revised Pennsylvania math that state is Florida.

## 4 · The funnel — live counts

```
  Orgs discovered in sweeps ................ ~210+ (across 31 states; 30 FL coalitions confirmed)
       │
       ▼  named a real contact
  Contacts loaded into Apollo ............... 348+
       │
       ▼  passed Check 2 (vendor-verified mailbox)
  Verified mailboxes on file ................ 55   (45 prior + 10 resolved 8/17)
       │
       ▼  passed Check 1 too (seen on the org's own site)
  FULLY VERIFIED → allowed to draft ......... 17 people at 7 FL orgs  (all drafted 8/17)
       │
       ▼
  Drafts waiting for Chris .................. 8    ⚠️ ALL EMAIL 2 FOLLOW-UPS — zero new orgs outreached 8/18
  Sequences live (sent, awaiting reply) ..... 34   (8 drafted for 08-18 · 7 due 08-19 · 6 due 08-20 · 6 due 08-21 · 6 due 08-24 — Alachua removed on reply)
  Replies ................................... 2    🟢 ELCPBC 8/14 (routing) · 🟢 ELC ALACHUA 8/18 (named the PD owner, committed to a discussion). Both sequences STOPPED
  Bounces ................................... 4    🔴 Five County 8/11 · mbevins@ 8/12 · person0936@org0323.example 8/17 (FIRST machine-passed) · ccr@org0315.example 8/17 (Chris's typo). Machine-passed rate: 1 in 31 (~3.2%)
```

**The supply bottleneck from 2026-08-13 is cleared, and the fix was geography, not effort.**
Stage A had emptied because New York's remaining orgs were blocked on human judgement. Opening
Florida refilled the batch to target in a single night, because Florida coalitions publish staff
directories that New York coalitions mostly do not. **The lesson to carry: when page-reads stop
converting in a state, the cheapest move is a new state, not another read of the same one.**

> 🔴 **But two of tonight's holds turned out to be premature, and both were cleared cheaply. Read
> this before holding an org again.**
>
> **1 · ACCORD was held for "no staff names on the page" — and its child-care division kept its own
> staff directory one link away.** The agency-wide leadership page publishes titles, phones and
> addresses but no names. The [Org 0283]'s *program* page has its own sub-navigation
> containing a full directory with names, titles and plain-text addresses. **Candidate rule: before
> holding a large agency for a missing roster, follow the CCR&R program page's own sub-navigation.**
> A division inside a community-action agency often maintains a staff list the agency page does not.
>
> **2 · Five Tier-1 people at [Org 0452] were recorded as "address not published"
> while the nightly lookup budget sat unspent.** Chris asked for one of them — [Person 0176], Child
> Care Business and Training Specialist — and a deep lookup resolved her in a single call for 2
> credits. **Candidate rule: when a Tier-1 person is identified on an org's own page and no address
> is published, spend the lookup rather than filing them as unreachable.** "Not published" is a fact
> about the website, not about whether the person is reachable.
>
> ✅ **BOTH APPLIED 2026-08-18.** #2 is now **THE ROSTER SWEEP**, a hard gate in [[method]] Phase 2:
> every Tier-1/2 person named on the org's own pages whose address is unpublished goes to the vendor
> in one batched call, and the card proves it with the roster resolution line. It was promoted from
> candidate to gate after it failed to fire at [Org 0539] on the day it was ratified — six
> training-titled people filed unreachable without being asked.
> See [[CAPA-2026-08-18-unqueried-tier1-roster]].

## 5 · Current org lists by stage

### Stage A — READY TO DRAFT (both checks passed, not yet drafted)

**Empty as of 2026-08-17, for the good reason again.** All seven organisations that cleared both
checks tonight were drafted the same night. Nothing verified is sitting unused.

**Florida progress: 17 of 30 coalitions have now been read. 13 remain unread.** Tonight's
page-read-to-draft rate was **7 of 13 orgs attempted (~54%)** — down from night one's ~78%, and the
reason is worth recording: **the coalitions that publish a full staff directory with plain-text
addresses were largely picked off on night one.** What is left skews toward orgs that publish names
and titles but no addresses, which is a **deeper-lookup problem rather than a page-read problem** —
and that is now a solved problem, see the note below.

> 🟢 **THE BIGGEST OPERATIONAL LESSON OF THE NIGHT: "no address published" is not a dead end, and
> three of tonight's seven drafts prove it.** ELC Alachua, [Org 0564] and [Org 0803] all
> publish staff names and titles on their own sites and publish **no usable addresses for the people
> worth emailing**. Under the old habit all three would have been filed as unreachable. **Ten
> credits turned them into three drafts, including the best-targeted org of the week** (Alachua,
> which publishes three explicit "Transformative Professional Development" job titles and not one
> address). The candidate rule raised on 08-13 after [Person 0176] and again on 08-14 after Heather
> Mooney was applied deliberately tonight and it worked. **Chris — this is the rule worth ratifying:
> when a Tier-1 or decision-maker person is named on an org's own page and no address is published,
> spend the lookup instead of filing them as unreachable.** "Not published" is a fact about the
> website, not about whether the person is reachable.

**Read tonight and HELD, with the reason (do not re-read without a new angle):**

| Org | Hold reason | What would unblock it |
|---|---|---|
| [Org 0544] County | Leadership page publishes names and titles but no addresses; staff addresses sit behind PDFs, and the Education & Inclusion PDF is dated **September 2024** — over the 6-month document limit | A vendor lookup on [Person 0537] (CEO) or [Person 0017] (VP of Education). ⚠️ Also carries a pre-machine unsent draft — needs Chris's call |
| [Org 0554] | Provider services and training are **contracted out to [Org 0609]** — the training buyer may not sit at the coalition | Chris's scope call. ⚠️ Also carries a pre-machine unsent draft |
| [Org 0561] County | 🔴 **FAILED READ** — the contact page returned an empty body. Recorded as a failure, not a fall-through | Retry, try `[Org 0597]`, or a browser session |
| ELC of Miami-Dade/Monroe | Contact page publishes offices and one phone number; no individual addresses | A leadership-page read, then a lookup |
| ELC of Polk · ELC of Lake · [Org 0555] | No staff page with names surfaced inside the night's budget | One page read each |

🔴 **CORRECTED 2026-08-19 — this list was six orgs out of date and would have caused re-approaches.**
Escambia · IRMO · Santa Rosa · Polk · Lake · Northwest were all **APPROACHED 2026-08-18** (see
[[contacted.md]] and [[sequence-tracker]]) — they belong to **Stage B**, not here. Florida's Gateway
is drafted but unsent.

**Still completely unread in Florida (6):** Florida's Heartland (🔴 BLOCKED — directory is PDF-only) ·
Nature Coast (🔴 failed read, no fetchable own-site page) · Sarasota (🔴 failed read) ·
Miami-Dade/Monroe · Broward (held) · North Florida (held).
**Drafted, not yet sent (1):** Florida's Gateway — 🔴 BLOCKED, directory is a JPEG:
`https://www.[Org 0579]/wp-content/uploads/2026/07/directory.jpg`

### Stage B — DRAFTED / IN SEQUENCE (see [[sequence-tracker]] for full detail)

| Org | State | Status |
|---|---|---|
| **ELC of Alachua** | **FL** | 🟢 **REPLIED 2026-08-18 — sequence STOPPED.** [Person 0617], CEO, named [Person 0581] (Provider Services and Quality Manager, owns all PD), added her to the thread, and committed that the two of them will discuss the training and come back. **The best outcome the machine has produced. No Email 2** |
| **[Org 0557] · [Org 0548] · [Org 0564] · [Org 0565] · [Org 0563] · [Org 0803]** | **FL** | ✅ **ALL SENT 2026-08-17** — Email 2 due 2026-08-24 |
| **[Org 1003] · [Org 0357] · [Org 0652] · Thrive B5 · [Org 0658] · CFES · [Org 0473] · [Org 1164]** | VA/UT/TN/KS | 📝 **EMAIL 2 DRAFTED 2026-08-18 — waiting for Chris to send.** First follow-up batch in the machine's history |
| [Org 0006] | FL | 🟢 **REPLIED 2026-08-14 — sequence STOPPED.** [Person 0209], Chief of Communications and Community Impact, forwarded it to their PD team; Chris answered the same morning. **No Email 2** |
| **[Org 0546] · [Org 0580] · [Org 0552] · ELCPBC (Palm Beach) · [Org 0589] · [Org 0562] · ELC of Osceola County** | **FL** | 🆕 **DRAFTED 2026-08-14 — waiting for Chris to send** |
| **ACCORD · [Org 0131] · [Org 1140] · [Org 0452] · [Org 0392]** | NY | ✅ **ALL SENT 2026-08-13** — follow-ups due 08-20. ⚠️ `person1074@org0077.example` ([Org 0102] Cc) is a **dead mailbox** — remove before Email 2 |
| [Org 0250] | NY | ✅ **SENT 08-13** — follow-up due 08-20 |
| Suffolk · [Org 0985] · Schoharie CAP · CAPC Jefferson · CCC Orange County · ICP Oswego · Child Care Solutions CNY | NY | ✅ **All 7 SENT 08-12** — follow-ups due 08-19 |
| United Way Cville (Blue Ridge) · CSS Utah · [Org 0652] · Thrive B5 · [Org 0658] · CFES · [Org 0473] · Family Conservancy | VA/UT/TN/KS | Sent Aug 11 — follow-up due Aug 18 |
| [Org 0655] | UT | Bounced; corrected address verified 3 ways, ready to re-draft on Chris's word |

### Stage C — ONE CHECK DONE, ONE TO GO (the refill queue — worked top-down each night)

**C-1 · Vendor-verified, need a staff-page look — CLEARED 2026-08-12.** All 17 pages have been read.
What remains here is a set of blocks that page reads and credits cannot clear:

| Org | Hold reason | What would actually unblock it |
|---|---|---|
| [Org 0359] | Not a CCR&R — operates centers directly | Chris's in-scope ruling |
| Adirondack CAP | [Person 0006] verifiable only via a 2012 post; no current staff page | A phone call |
| [Org 0188] | [Person 0299] absent from the org's own site | A phone call |
| [Org 0462] | No ED named anywhere on the site; [Person 0576] unconfirmed | A phone call |
| [Org 0308] | Pages unreadable by fetch | A browser session |
| [Org 0292] (Buffalo) | No staff roster exists on the site; only `info@` published. [Person 0359] has a vendor-verified address | A browser session or a phone call |
| **The [Org 0389]** | 🆕 08-13. Multi-program umbrella → the org-scale rule puts CEO [Person 0531] off the thread; the correct recipient, **[Person 0182], Director of Early Care & Education**, publishes no address and the deep lookup returned a different person of that name (left CHCF 2009, now at ICF) | Chris's call to email the CEO anyway, or a phone call to get [Person 0182]'s address |
| ~~**ACCORD**~~ | ✅ **RESOLVED 08-13 — drafted.** The agency leadership page publishes addresses but not names; **the [Org 0283] keeps its own staff directory** with names, titles and plain-text addresses, one link away in the CCRC program page's sub-navigation. Zero credits | — |
| **[Org 0316]** (Brooklyn) | 🆕 08-13. Publishes only `info@org0125.example`; no roster on the pages read | One more page read (`/about-us-1`) or a deep lookup |

**C-2 · Seen on their own site, need vendor verification — 3 of 4 resolved 2026-08-13:**
✅ [Person 0260] (Dutchess & Putnam) → resolved and then **rejected: she retired in 2025**; her
successor [Person 0241] was found on the org's own staff directory and drafted instead.
🔴 [Person 0385]-Christman (ACCORD) → deep lookup returned nothing.
⏳ [Person 0135] (NY ECPDI) · [Person 0424] Riddick (CDSC) → still unworked; both need Check 1
first, which is the blocker, not the vendor lookup.

**C-3 · Loaded in Apollo, never verified at all:** the 94-contact national sweep from Jul 22 and
6 MA administrators. Free to pre-check, ~1 credit each to verify the promising ones.

### Stage D — NEEDS A HUMAN DECISION

| Org | Why |
|---|---|
| The 15 orgs whose stale drafts were deleted (SC, ME, UT, NJ, PA, VA, TN...) | Eligible again but predate the verification system — each needs both checks fresh |

### Stage E — REMOVED, with reasons (so we don't re-add them by accident)

| Org / person | Reason | Date |
|---|---|---|
| Jeff Pier @ Child Care Council, Inc. | Left the org 2026-03 (now at a child advocacy center) — org needs a new contact | 08-11 |
| [Person 0326] @ CCC of Westchester | Left 2025-01, now independent — org needs a new contact | 08-11 |
| `person0174@org0174.example` | Hard bounce; address came from a stale 2024 PDF | 08-11 |
| `person0052@org0238.example` as an auto-send | Vendor pattern-guess, no source ever saw it *(Chris later sent it manually — his call)* | 08-11 |
| [Org 0498] · careaboutchildcare.org0755.example | Lookup portals, no staff | earlier |
| Indiana (whole state) | CCR&R network sunset Oct 2025 | earlier |


## 6 · National progress toward the 2027 goal — "how much country is left?"

**The goal this machine serves (Chris, 2026-08-12):** 20 booked in-person workshop days in 2027.
Test-batch math: 33 cold emails → 4 meetings (12%) → 1 offer (~3%). At 3%, 20 wins needs outreach
to **~667 organizations**. This section answers: does the country hold 667, and how far along are we?

### Is the market big enough? Yes — with a caveat.

Child Care Aware of America's national network counts **more than 500 CCR&R agencies** (sources
range 400–700 depending on how state vs. local offices are counted — the machine's own sweeps will
replace this estimate with an exact count as coverage completes). On top of CCR&Rs sit the adjacent
segments this machine already touches: FL's 30 Early Learning Coalitions, university-hosted
programs, shared-services alliances, and NAEYC affiliates. **Realistic addressable universe:
roughly 550–750 organizations.** So: the approach does NOT exhaust at 300 — but the universe is
only about the size of the 667 target, not 10× it. That means (a) every org burned by sloppy
outreach is a real loss, and (b) the conversion rate matters as much as coverage. Both are why the
verification gates exist.

### How progress is measured — organizations, not geography

States and counties are wildly different sizes (KY = 1 statewide org; FL = 30). So **the unit of
progress is the organization, never the state or the county.** A state is "done" when its orgs are
counted; the country is X% done when X% of known orgs have been fully approached. "Fully
approached" = the complete 3-email sequence ran (or got a reply/bounce earlier).

### The scoreboard (nightly run keeps this current)

| Metric | Count | Notes |
|---|---|---|
| Estimated national universe | **~550–750 orgs** | Replaced by exact count as sweeps complete |
| States swept for orgs | **31 of 48 in scope** | +DC; CO/KY/GA found but reserved for Chris; IN excluded. **FL added 2026-08-14; 17 of its 30 coalitions now read** |
| Orgs discovered & identified so far | **~210** | ⚠️ still approximate for the pre-FL cohort — but the Florida figure is exact: **30 coalitions**, published by their own statewide association. The reconciliation of the older ~180 is still owed |
| Orgs outreached (Email 1 sent) | **74** | 38 pre-machine (Apr–Jul) + 9 Aug 11 + 7 Aug 12 + 6 Aug 13 + 7 Aug 14 (FL) + **7 Aug 17 (FL — all sent same day)** |
| Orgs drafted, awaiting Chris's send | **0** | The 2026-08-17 Florida batch cycled the same day — sent 13:44–15:22 UTC |
| Orgs fully sequenced (all 3 emails) | **~38** | The pre-machine cohort; machine-era sequences complete ~Sep 1 |
| **Progress vs. the 667 target** | **~11.1%** | 74 of 667 sent |
| **Required pace** | **7 drafts per working day** | Chris, 2026-08-12: ~96 working days left in 2026 × 7 ≈ 670 ≈ the target. `target_drafts` raised 5 → 7 accordingly |
| Meetings → offers so far | 4 → 1 | From the 33-email test batch |

### Read the funnel, not just the total — the honest caveats on the 3%

1. **The 3% rests on ONE offer.** With n=1, the true rate could plausibly sit anywhere from under
   1% to ~15% — meaning the real requirement is somewhere between ~130 and ~2,000 orgs. The
   **meeting rate (12%, n=4)** is the sturdier early signal; track meetings-per-100-emails as the
   leading indicator and let the 667 revise itself as real numbers accumulate.
2. **An offer is not a booked day** — the test's one offer died on dates. Some cushion above 667
   is needed for that.
3. **Pulling the other way: one win can be worth multiple days.** The CCR&R of Southwest Georgia
   engagement ran 4+ sessions. If a typical win averages 2 days, 10 wins covers the goal and the
   required outreach halves.
4. **The machine may beat the test batch.** The test was manual Email 1s; the machine runs the full
   3-email sequence with the PD/training buyer Cc'd — both should lift, not lower, the rate.

### The conversion ledger — updated every run

Counted per organization, cumulative. Replies/bounces counted automatically from Gmail; meetings,
offers and bookings confirmed by Chris (the report asks when it spots a likely meeting in a reply).

| Stage | Test batch (Apr–Jul, manual) | Machine era (Aug 11 →) | Combined | Rate (combined) |
|---|---|---|---|---|
| Orgs outreached | 38 | 36 | 74 | — |
| Replied | — *(not tracked then)* | **3** | **3 known** | **~4.1% of outreached** 🟢 tripled in four days |
| — of which: routing / hand-off | — | 2 | 2 | ELCPBC · **ELC Alachua (named the PD owner)** |
| — of which: explicit decline | — | **1** | **1** | 🔴 **Thrive B5 — incumbent provider.** The first competitive signal in 74 approaches |
| Meeting held | 4 | 0 | 4 | ~5.4% of outreached |
| Offer made | 1 | 0 | 1 | ~1.4% of outreached *(n=1 — unstable)* |
| Days booked | 0 | 0 | 0 | — |

**Re-derived 2026-08-18 at close of run. ONE STAGE COUNT MOVED — replies 1 → 2.**
🟢 **[Person 0617], Chief Executive Officer of the Early Learning Coalition of Alachua County,
answered Email 1 on 2026-08-18, about eleven hours after Chris's 08-17 send.** Verbatim: *"Thank you
for reaching out. I am looping [Person 0581] in this email, she is the Provider Services
and Quality Manager, and oversees all Professional Development here at ELCAC. She and I will discuss
your training, and she will get back with you."* That organisation's sequence is **STOPPED**.

**How to read this one honestly — it is stronger than the first reply, and the difference matters.**
The ELCPBC reply on 08-14 was a *routing with a condition*: forward to the PD team, *"if it's a fit,
they will connect."* This one **names the professional-development owner, puts her on the thread
with her address, and commits to a specific next step** — two named people at the organisation have
undertaken to discuss the product and come back. **It is still not a meeting**, and it does not move
*meeting held*, *offer made* or *days booked*. But it is the closest the machine has come.

**Two replies in 74 approaches (~2.7%) is still far too small a base to forecast from.** What it
does say: **both replies came from Florida, both from batches on v6 copy, and both within 26 minutes
to 11 hours of the send.** That is now a pattern worth two more batches of watching.

🔴 **Orgs outreached did NOT move tonight, and unlike previous nights that is NOT correct — it is
the finding.** No new organisation was approached, because eight Email 2 follow-ups came due and
filled the nightly target. See the structural conflict written up in [[sequence-tracker]]: on the
current rule, follow-ups will consume the target from here on and the 667-organisation goal becomes
unreachable. **Awaiting Chris's ruling on whether `target_drafts` counts new organisations only.**

**Re-derived 2026-08-17 at close of run. ONE STAGE COUNT MOVED, AND IT IS THE FIRST TIME.**
🟢 **Replied moves 0 → 1.** [Person 0209], Chief of Communications and Community Impact at the
**Early Learning Coalition of Palm Beach County**, answered Email 1 on 2026-08-14, **26 minutes
after Chris sent it**. Verbatim: *"Hello Chris, Thank you for reaching out. I will forward this to
our PD team for review and if it's a fit, they will connect. Thank you, [Person 0208]."* Chris replied the
same morning. **That organisation's sequence is stopped per `stop_on_reply`.**

**How to read this honestly.** It is a **routing reply, not a meeting and not a decline** — she is
handing it to the people who would buy. It does not move *meeting held*, *offer made* or *days
booked*, and it must not be counted as though it did. What it does establish is that **the machine's
approaches can produce a same-day human response from a senior person**, which was previously
unproven across 21 sends. **One reply in 67 approaches (~1.5%) is far too small a number to forecast
from** — but the first one arriving from the *first Florida batch*, inside half an hour, is a signal
about Florida and about v6 copy worth watching over the next two batches.

**Orgs outreached did NOT move tonight, and that is correct.** The seven new drafts are waiting in
Gmail; an organisation counts as approached only once Email 1 goes out. **Send all seven and
approached moves 67 → 74, or ~11.1% of the ~667 target.**

🔴 **Chris — the machine still cannot see meetings, offers or booked days.** 29 machine-era
approaches now sit unreadable to it. If the ELCPBC hand-off, or any other, has produced a call, tell
the run and these numbers change materially.

**Earlier note, kept for the record — re-derived 2026-08-14 at close of run. No stage count moved tonight, and that is correct, not a
miss.** The seven Florida drafts are waiting in Gmail; an organisation is only counted as
*approached* once Email 1 actually goes out. **Send all seven and approached moves 60 → 67, or
~10.0% of the ~667 target.** Replies remain 0 across 21 sends — six auto-responders to date
(two out-of-office at ACCORD, one at Dutchess, one at [Org 0985], one decommissioned mailbox at
Oswego, one inactive mailbox at [Org 0102]), none of them an answer. 🔴 **Chris — the machine still
cannot see meetings, offers or booked days.** If any of the 22 machine-era approaches has produced
a call, tell the run and these numbers change materially.

**Earlier note, kept for the record — re-derived 2026-08-13 at close of run.** All six of that
day's drafts were sent, so **approached moved 54 → 60** — the machine's single biggest day. No later stage moved, so the rates dilute
slightly on the same numerator; that is expected and not a signal. **Requirement stays ~667 orgs**
on the n=1 offer rate. 🔴 **Chris — the machine cannot see meetings, offers or booked days.** 22
machine-era approaches now sit unreadable to it. If any has produced a call, tell the run and these
numbers change materially. Nothing in the replies suggests one yet: across 21 sends there are zero
human replies, two auto-responders, and two bounces (both human-override addresses) and the rates fall slightly again on the
same numerator. **Requirement stays at ~667 organizations** on the n=1 offer rate. 🔴 **Chris — the
machine cannot see meetings, offers or booked days.** If any of the 16 machine-era approaches has
produced a call, tell the run and these numbers change materially. Nothing in the last two days'
replies suggested one: the only two responses were an out-of-office and a decommissioned mailbox.

**Each time a stage count changes, re-derive the requirement:** orgs needed = 20 ÷ (offer rate ×
avg days per win). Today that's 667 on the n=1 rate; expect it to move a lot as real data lands.

**Decision rule this scoreboard exists for:** if, by ~150 fully-sequenced orgs, the offer rate is
tracking under ~1.5%, the universe math stops working and the play changes (warmer channels,
conference-led, referral loops) BEFORE the remaining market burns. That checkpoint lands around
October at current pace.


---

*Updated by the nightly run. If a count here disagrees with [[verification-log]], the log wins and
this file gets corrected.*

---

# 🔄 PIPELINE UPDATE — 2026-08-19

## Funnel (§4) — live counts, restated

| Metric | Count | Change tonight |
|---|---|---|
| Estimated national universe | **~580–790 orgs** | ⬆️ **REVISED UP.** Texas adds ~30–40 researchable orgs that the old estimate did not contain — see the state map below |
| States swept for orgs | **32 of 48 in scope** | ⬆️ **+TX (probe complete, model established)** |
| Orgs discovered & identified | **~245** | ⬆️ +~35: the Texas set (9 organisations read in detail, ~30–40 implied) |
| Orgs outreached (Email 1 SENT) | **80** | 74 through 08-17 + **6 sent by Chris on 08-18** (Santa Rosa · [Org 0582] · Polk · Lake · Escambia · [Org 0587]) |
| Orgs drafted, awaiting Chris's send | **7** | 6 new tonight + ELC Florida's Gateway carried from 08-18 |
| **Progress vs. the 667 target** | **~12.0%** | 80 of 667 |
| Required pace | **7 NEW orgs per working day** | Unchanged. Tonight: **6 of 6 achievable** (7 minus 1 Email 1 already waiting) — target met |

## State map (§3) — TEXAS IS NOW SWEPT, and the shape is different

🆕 **Texas has NO standalone CCR&R network.** CCR&R, scholarship and quality functions are devolved
to the **28 Local Workforce Development Boards** under the Texas Workforce Commission. TWC's own page:
*"In Texas, there are 28 Local Workforce Development Boards (Boards) that operate more than 170 local
Workforce Solutions Offices."* The boards split into three models, and **the tell is fast: if the
board's child-care page names an outside CCMS contractor, or its provider portal points at a
third-party domain, it is Model B.**

| Model | What it looks like | The target | Confirmed at |
|---|---|---|---|
| **A — in-house** | The board itself employs the Texas Rising Star mentors and the early-education quality / PD managers | **the board** | Gulf Coast · Borderplex · South Texas · Rural Capital Area |
| **B — sub-contracted** | The board buys child care services from a separate nonprofit operator with its own domain, staff and training institutes | **the operator** | Tarrant County → **[Org 0203]** · Greater Dallas → **[Org 0329]** |
| **C — partnership / opaque** | Quality mentoring published, nobody named, routed through a shared mailbox and CLI Engage | needs a second pass | Alamo |

**Implied Texas set: ~15–18 Model-A boards + ~8–12 Model-B operators + 3–5 standalone statewide/metro
training agencies = 30–40 researchable organisations.** Larger than any single-state CCR&R network
worked so far, and **the Model-B operators are the highest-value targets in the whole list** because
they are pure-play training organisations with named institutes.

⚠️ **Address availability is the binding constraint in Texas, not people.** Seven of the nine orgs
probed publish named Tier-1 staff and **zero email addresses.** Gulf Coast is the lone exception.
Budget the roster sweep accordingly — but note [Org 0203] resolved 9 of 10 for 10 credits,
so the vendor covers this sector well.

🔴 **SCOPE FLAG FOR CHRIS: these are workforce boards and CCMS operators, not organisations that call
themselves CCR&Rs.** By [[method]]'s D-16 test — *judge by function, not domain* — they qualify: they
employ named coaching and PD staff serving child care providers, and Texas Rising Star mentors are
precisely the ECE workforce-development people HST sells to. **Three were drafted tonight to prove
the model. Confirm before the machine works the remaining ~30.**

### Texas — read in detail 2026-08-19 (9 orgs)

| Org | Own domain | Model | Tier-1 people named | Addresses published? | Status |
|---|---|---|---|---|---|
| **[Org 0684]** | org0805.example (mail `org0806.example`) | A | 5 | ✅ **all published** | 📝 **DRAFTED 08-19** |
| **[Org 0203]** | org0157.example | B (Tarrant + NCTX) | 4 | ❌ none — 9 resolved by sweep | 📝 **DRAFTED 08-19** |
| **[Org 1300]** | org0688.example | A | 6 | ❌ none; `ccs@` dept inbox published | 📝 **DRAFTED 08-19** (Tier 3) |
| [Org 1291] | org0055.example | A | **10** (TRS mentors + Provider Services Director) | ❌ none, phone only | 🟡 **Stage C-2 — needs a sweep.** Deepest in-house early-childhood bench of any board probed |
| [Org 0329] | [Org 0329].org | B (Dallas + SE Texas + Heart of Texas) | 1 ([Person 0213], "Director, Child Care Quality") | ❌ none | 🟡 **Stage C-2.** Multi-region operator, founded 1901, *"trains early childhood professionals"* |
| [Org 1314] | org0800.example | A | 2 | ❌ none | 🟡 **Stage C-2.** Only the child-care team page was read; `/about/staff` unread |
| [Org 0381] | org0218.example | standalone (Houston) | 0 published — leadership page shows only 4 executives | ❌ none | 🟡 **Stage C-1.** The training leadership is not on the leadership page; try `/wp-json/wp/v2/pages?search=staff` (WordPress) |
| [Org 1304] | org0782.example | B → [Org 0329] | 0 | ❌ none | 🔴 **NOT A TARGET.** Zero child-care people among 15 named key staff |
| [Org 1290] | org0797.example (mail `org0809.example`) | C | 0 named | `person1238@org0809.example` published | 🟡 Tier 4 candidate; `/about/who-we-are/` unread |
| [Org 1207] | org0715.example | standalone statewide | 0 | ❌ **Cloudflare-obfuscated**, no plaintext address anywhere | 🟡 3 staff only; needs a sweep |

**Next Texas pass, recommended order:** Borderplex (10 Tier-1, one sweep) → [Org 0329] →
Rural Capital Area → [Org 0381] (REST API) → then enumerate the remaining ~19 boards.
**AVANCE and Early Matters were NOT researched** — no claims made about them.

## Florida — Stage A corrections (two hold reasons were WRONG)

| Org | Old status | 🔄 Corrected 2026-08-19 |
|---|---|---|
| **[Org 0561] County** | 🔴 "FAILED READ — contact page returned an empty body" | ✅ **It was a WRONG-DOMAIN failure.** `earlylearningcoalitionsarasota.org` is empty; **`[Org 0597]`** serves the full current site and is its own canonical. 13 named staff, **every address published**. 📝 **DRAFTED 08-19** |
| **[Org 0566]** | 🔴 "no fetchable own-site page" | ✅ **DOMAIN CORRECTED — `org0313.example`, with a hyphen.** Site is live. **Still HELD**, on evidence quality: the only page naming humans dates to June 2021 and truncates the addresses (`swoodard` with no domain) |
| **[Org 0544] County** | HELD — "needs a vendor lookup on [Person 0537] or [Person 0017]" | ✅ **UNBLOCKED — the lookup was spent.** 6 of 6 resolved, `verified`. 📝 **DRAFTED 08-19.** Also found 4 Tier-1 role contacts with published addresses on the CLASS page that no leadership read would have surfaced |
| **[Org 0550]** | 🔴 BLOCKED — PDF-only directory | ✅ **DRAFTED ANYWAY at Tier 4** to `person0401@org0321.example`, per the blocked-directory handler. PDF URL carried forward (revision-dated 2026-07-30) |
| **ELC of Miami-Dade/Monroe** | HELD — "no individual addresses" | 🔴 **Still HELD, and now precisely diagnosed: the whole site is an Apptegy JS shell.** 🎯 **But the nav proves an in-house "Professional Development Institute" with its own page.** One JS-capable browser session turns this into a Tier-1 draft — **the single highest-value browser session available anywhere in this pipeline** |
| **[Org 0554]** | HELD — "training contracted out to [Org 0609]; Chris's scope call" | ✅ **CONFIRMED by their own site, repeatedly.** Zero of seven named staff hold a PD/training/quality/CCR&R title; two publish `@org0303.example` addresses on the ELC's own staff page. **Recommendation: close this hold and retarget to [Org 0609] (`org0303.example`).** Chris's call |

**Florida standing: 23 of 30 coalitions now read.** Remaining unread/blocked: Gateway (JPEG directory,
drafted 08-18) · Heartland (PDF, drafted 08-19) · Nature Coast (stale) · Miami-Dade/Monroe (JS shell) ·
North Florida (retarget recommended). **Florida is effectively worked out** — which is why Texas
matters.

## Conversion ledger (§6) — re-derived 2026-08-19

| Stage | Test batch (Apr–Jul, manual) | Machine era (Aug 11 →) | Combined | Rate (combined) |
|---|---|---|---|---|
| Orgs outreached | 38 | **42** | **80** | — |
| Replied | — *(not tracked then)* | **3** | **3 known** | **~3.8% of outreached** |
| — routing / hand-off | — | 2 | 2 | ELCPBC · ELC Alachua (named the PD owner) |
| — explicit decline | — | 1 | 1 | Thrive B5 — incumbent provider |
| Meeting held | 4 | **0** | 4 | ~5.0% of outreached |
| Offer made | 1 | **0** | 1 | ~1.3% *(n=1 — unstable, do not forecast from it)* |
| Days booked | 0 | 0 | **0** | — |

**NO STAGE COUNT MOVED TONIGHT except *approached* (74 → 80).** No new replies, no new bounces.
🔴 **The machine still cannot see meetings, offers or bookings.** If the ELC Alachua hand-off
([Person 0581]) or the ELCPBC routing has produced a call, **tell the run** — it would move
*meeting held* off zero for the first time in the machine era and materially revise the 667.

**`updated: 2026-08-19`**

---

# 🔄 PIPELINE UPDATE — 2026-08-20

> ⚠️ **The 2026-08-19 block above was written by run 1 and never corrected by run 2 or by Chris's
> sends.** It reported *"80 outreached · 7 drafted awaiting send"* — but Chris sent five of those
> drafts at 12:57–13:13 UTC the same day, and run 2 then drafted five more organisations. **The
> figures below supersede it.** Root cause is the same one that left [[sequence-tracker]] stale: two
> runs in one night, one dashboard.

## Funnel (§4) — live counts

| Metric | Count | Change since 08-19 |
|---|---|---|
| Estimated national universe | **~580–790 orgs** | unchanged |
| States swept for orgs | **32 of 48 in scope** | unchanged — no discovery ran tonight |
| Orgs discovered & identified | **~245** | unchanged |
| **Orgs outreached (Email 1 SENT)** | **85** | ⬆️ **+5** — [Org 0203] · ELC Florida's Gateway · [Org 0684] · ELC Sarasota · ELC Broward, all sent by Chris 2026-08-19 |
| Orgs drafted, awaiting Chris's send — **Email 1** | **8** | 7 new organisations + the Five County re-draft *(Five County was already counted as outreached on 08-11, so it does not move the 85)* |
| Orgs drafted, awaiting Chris's send — **Email 2** | **6** | 🆕 tonight's follow-up batch |
| **Progress vs. the 667 target** | **~12.7%** | 85 of 667 |
| Required pace | **7 NEW orgs per working day** | 🔴 **Tonight: 0 owed and 0 drafted.** 7 − 8 already waiting = 0. **Not a shortfall — the queue is full** |

🔴 **THE BINDING CONSTRAINT HAS MOVED, AND THE DASHBOARD SHOULD SAY SO.** For the first two weeks the
limiting factor was *finding verified organisations*. It is now **Chris's send review**: eight Email 1
drafts have sat since 2026-08-19, and until they clear the machine is barred from approaching anyone
new. **Discovery, verification and lookup budget are all idle for the same reason.** At the required
pace of 7/working day, each day the queue does not clear costs one full day of the 667.

## State map (§3)

**No change.** Phase 6 did not run — [[method]] Phase 1 step 4 funds discovery only when the new-org
target is unmet, and tonight's target was zero. Texas remains **swept but unauthorised**: 8 of an
estimated 30–40 organisations approached or drafted, **~25 awaiting Chris's scope nod for a third run.**

## Conversion ledger (§6) — re-derived 2026-08-20

| Stage | Test batch (Apr–Jul, manual) | Machine era (Aug 11 →) | Combined | Rate (combined) |
|---|---|---|---|---|
| Orgs outreached | 38 | **47** | **85** | — |
| **Replied** | — *(not tracked then)* | **6** | **6 known** | **~7.1% of outreached** 🟢 **doubled since 08-19** |
| — routing / hand-off | — | 3 | 3 | ELCPBC · ELC Alachua *(named the PD owner)* · 🆕 **ELC Florida's Gateway** *(CEO forwarded to two lead directors)* |
| — added to vendor list / RFP pipeline | — | 1 | 1 | 🆕 **ELC Polk** — [Person 0499] |
| — **agreed to a call** | — | **1** | **1** | 🟢 **[Org 0253] — [Person 0306], ED** |
| — explicit decline | — | 1 | 1 | Thrive B5 — incumbent provider |
| Meeting held | 4 | **0** | 4 | ~4.7% of outreached |
| Offer made | 1 | **0** | 1 | ~1.2% *(n=1 — unstable, do not forecast from it)* |
| Days booked | 0 | 0 | **0** | — |

**Machine-era outreach recount, because the old figure was carrying two runs of drift:**
9 (08-11) + 7 (08-12) + 6 (08-13) + 7 (08-14) + 7 (08-17) + 6 (08-18) + **5 (08-19)** = **47.**
38 + 47 = **85.** ✅ Reconciles.

### 🟢 THE REPLY RATE IS THE REAL NEWS, AND IT IS BETTER THAN THE HEADLINE SUGGESTS

**Replies went 3 → 6 while outreach went 80 → 85.** Three of the new ones (Gateway, Polk, Orange
County) were sitting uncounted in earlier runs' notes and are consolidated here for the first time.
**~7.1% reply rate across 85 organisations** — against a *"not tracked then"* baseline, so the honest
comparison is machine-era only: **6 replies in 47 approaches = ~12.8%.**

🔴 **BUT `meeting held` IS STILL ZERO AND THAT IS ALMOST CERTAINLY A MEASUREMENT FAILURE, NOT A
RESULT.** [Person 0306] wrote *"We can def schedule a chat. I'll be available tomorrow to schedule"* on
2026-08-19 and Chris replied the same day. **The machine cannot see a calendar or a CRM meeting
object, so an agreed call is invisible to it until Chris says so.** Every rate below the reply line
should be read as a floor, not a measurement. **The 667 target cannot be honestly revised while the
middle of the funnel is unobservable** — and the 3% offer rate it rests on is still n=1.

**`updated: 2026-08-20`**

---

# 🔄 PIPELINE UPDATE — 2026-08-20, end of day. **FIRST MEETING BOOKED.**

**Rebuilt from Gmail + HubSpot engagement objects, not from the vault.** Supersedes the 2026-08-20
morning block above, which was written before Chris sent 13 more emails.

## 🟢 THE HEADLINE — `meeting held` comes off ZERO for the first time in the machine era

**[Person 0645], "Director of Professional Development," [Org 0250],
replied 2026-08-20 at 17:00:59Z — 43 MINUTES after Email 2 landed:**

> *"Thank you for your patience. I would love to connect and share more about what we do and see if
> there is a way to collaborate. I have availability next week: Tuesday, August 25, 2026 @ 1:…"*

**Chris sent a Zoom invite at 17:13:35Z. This is a BOOKED CALL, not a request.**

🎯 **Three things about this one are worth more than the meeting itself:**
1. **It came from the FOLLOW-UP, not the first email.** Email 1 went 2026-08-13 and got no reply.
   **The entire case for the 3-email sequence rests on exactly this**, and this is the first hard
   evidence for it in the machine's own data.
2. **It came from a Cc, not the To.** The To was [Person 0241], ED. **[Person 0645] was a Cc the
   machine put on the thread because her title contains "Professional Development"** — the wedge-buyer
   rule working precisely as designed.
3. **Her Email 2 shows 4 opens in HubSpot** — the highest of any follow-up sent.

## Emails sent — machine era, 2026-08-11 → 2026-08-20

| | Count |
|---|---|
| Email 1 | **54** |
| Email 2 | **21** (8 on 08-18 · 7 on 08-19 · 6 on 08-20) |
| Email 3 | **0** — first tranche due 2026-08-25 |
| **Total campaign emails** | **75** |
| Chris's own conversational replies | ~9 |
| **Sent TODAY** | **13** (7 Email 1 + 6 Email 2) — the machine's biggest send day |

## Orgs outreached

| | Orgs |
|---|---|
| Pre-machine (Apr–Jul, full sequence) | 38 |
| Machine era | **54** |
| **Total** | **92** |
| **Progress vs. the 667 target** | **13.8%** |

## Stage distribution — where the 54 machine-era orgs actually are

| Stage | Orgs | Next action |
|---|---|---|
| **Email 1 sent, Email 2 due** | **28** | 6 on 08-21 · 6 on 08-24 · 5 on 08-25 · 4 on 08-26 · 7 on 08-27 |
| **Email 2 sent, Email 3 due** | **18** | 7 on 08-25 · 6 on 08-26 · 5 on 08-27 |
| **STOPPED — replied** | **7** | No further email |
| **HELD** | **1** | Five County — partial send, see [[AUDIT-2026-08-20-who-have-we-contacted]] |
| **Total** | **54** | |

⚠️ **The Email 3 wave starts 2026-08-25 and 18 orgs are queued into it over three days.** Combined
with the Email 2 wave, **the machine has 46 follow-ups owed in the next seven working days** — all
uncapped, all on top of the 7-new-orgs target.

## 📊 OPEN RATE — real data, and it is good

**Source: HubSpot `hs_email_open_count` on EMAIL engagement objects, logged by Chris's browser
extension's tracking pixel.**

| Cohort | Email 1 sent | Opened | Rate |
|---|---|---|---|
| 08-12 (NY) | 7 | **7** | **100%** |
| 08-13 (NY) | 6 | 3 | 50% |
| 08-14 (FL) | 7 | 3 | 43% |
| 08-18 (FL) | 6 | 5 | 83% |
| 08-19 (FL/TX) | 5 | 4 | 80% |
| 08-20 (TX/FL) | 7 | 2 | 29% *(sent ~4h ago — too early)* |
| **Tracked total** | **38** | **24** | **63%** |
| **Excluding today** | **31** | **22** | **71%** |

🔴 **TWO CAVEATS, AND THEY BOTH MATTER MORE THAN THE HEADLINE NUMBER.**

**1 · The open rate is a FLOOR, not a measurement — and this run has proof.** [Person 0306] replied to
her Email 2 within 70 minutes. **That email records ZERO opens.** She demonstrably read it. Image
blocking suppresses the pixel, so **every open figure here undercounts by an unknown margin.**
Treat 63% as "at least 63%."

**2 · 🔴 THE 08-17 BATCH HAS NO TRACKING AT ALL — 7 organisations invisible.** Not one of
Flagler & Volusia, Pasco & Hernando, Alachua, Big Bend, Emerald Coast, St. Lucie or Manatee appears
in HubSpot. **Cause: the HubSpot BCC bounced "Message too large" on 6 of 7 of those sends** — the
5.4 MB GIF. **The attachment size did not just annoy the BCC; it deleted a week of engagement data
for an entire cohort.** That is a second, previously unpriced cost of the un-hosted GIF.

## Conversion ledger — re-derived 2026-08-20 end of day

| Stage | Test batch (manual) | Machine era | Combined | Rate (machine era) |
|---|---|---|---|---|
| Orgs outreached | 38 | **54** | **92** | — |
| Opened (tracked only) | — | **24 of 38** | — | **≥63%** |
| **Replied** | — | **7** | **7** | **13.0%** |
| — **meeting BOOKED** | 4 | **1** 🟢 | **5** | **1.9%** |
| — meeting proposed, not confirmed | — | 1 | 1 | 1.9% |
| — routing hand-off | — | 3 | 3 | 5.6% |
| — added to vendor/RFP list | — | 1 | 1 | 1.9% |
| — **explicit rejection** | — | **1** | **1** | **1.9%** |
| Offer made | 1 | 0 | 1 | — |
| Days booked | 0 | 0 | **0** | — |

**The seven machine-era replies, in full:**

| Date | Org | Person | Type |
|---|---|---|---|
| 08-14 | ELCPBC | [Person 0209], Chief of Communications | routing → PD team |
| 08-18 | ELC Alachua | [Person 0617], CEO | routing → named the PD owner and Cc'd her |
| 08-18 | Ready Region Central (Thrive B5) | [Person 0049], CEO | 🔴 **rejection — incumbent provider** |
| 08-19 | CCC Orange County | [Person 0306], ED | 🟡 meeting agreed, times sent 08-20, awaiting confirmation |
| 08-19 | ELC Polk | [Person 0499] | added HST to vendor list, will include in RFPs |
| 08-19 | ELC Florida's Gateway | LaShone T. Surrency, CEO | routing → two lead directors |
| **08-20** | **CCC Dutchess and Putnam** | **[Person 0645], Dir. of PD** | 🟢 **MEETING BOOKED — Zoom invite sent** |

⚠️ **Also today, not a reply but the only other engagement signal the stack can see:** [Person 0413]
(`person0830@org0320.example`) **reacted to the [Org 0539] Email 1 twice** at 15:40Z — an Outlook
reaction, not a message. **Recorded as engagement, NOT as a reply.**

## Read the rates honestly

- **13.0% reply rate on 54 cold organisations is strong** for cold outreach into this sector, and it
  is **up from 3 replies in 47 approaches** as recently as this morning — because three of today's
  came in within hours.
- **1.9% rejection is the number nobody should over-read.** One decline, and its stated reason was an
  **incumbent provider**, not price, fit or timing. **A single competitive loss is not a pattern.**
- 🔴 **`days booked` is still ZERO and the 667 target still rests on ONE offer from the manual test
  batch.** The meeting on 2026-08-25 is the first chance in the machine era to move the stage that
  actually validates the arithmetic. **Do not revise the 667 until it does.**

**`updated: 2026-08-20`**

---

# 🔄 2026-08-20 — QUEUE AND SCOPE CHANGES (Chris's rulings, plan Phase 6)

## 🆕 Cluster tagging — Texas is a SEPARATE MARKET and must be measured as one

> ✅ **Chris, R8:** *"Technically, this might be considered a new market and thus a new cluster (by
> TLBS terms). But that's okay."*

**Every organisation now carries a `cluster:` tag from its first send.**

| Cluster | What it is | Orgs contacted | Status |
|---|---|---|---|
| `CCRR-core` | CCR&Rs, ELCs, shared-services alliances, NAEYC affiliates | **46** | The original market |
| 🆕 `TX-workforce-boards` | Texas Local Workforce Development Boards + their CCMS operators | **8** | ✅ **IN SCOPE — ~25 remain** |

🔴 **WHY THE TAG MATTERS MORE THAN IT LOOKS.** Texas is not a new geography, it is a **different
organisational species** — workforce boards under TWC, some employing Texas Rising Star mentors
in-house (Model A), some sub-contracting to nonprofit operators with their own domains (Model B).
**If it converts at a different rate from the CCR&R core, that is a finding about a new market — and
it is only visible if the tag exists from the FIRST send.** Retro-fitting it later means guessing.

**Contacted so far under `TX-workforce-boards`:** [Org 0203] · Gulf Coast WFS ·
[Org 1268] · [Org 1276] · [Org 1264] · [Org 0329] · Collaborative for
Children · [Org 1207]. **~25 remain and need no further approval.**

⚠️ **Address availability, not people, is the binding constraint in Texas** — 7 of 9 orgs probed
publish named Tier-1 staff and zero addresses. **Budget the roster sweep accordingly.**

## 🆕 [Org 0609] — ADDED, and [Org 0554] is NOT approached

> ✅ **Chris, R7:** *"I think it's fair to reach out to the [Org 0609] based on the
> [Org 0554] site."*

| | |
|---|---|
| **Target** | `org0303.example` — [Org 0609] |
| **Evidence** | [Org 0554]'s **own staff page** states PD is contracted to ECS, and publishes two `@org0303.example` addresses on it |
| **Cluster** | `CCRR-core` |
| 🔴 **[Org 0554]** | **NOT approached.** Zero of seven named staff hold a PD/training/quality/CCR&R title — **they cannot buy training because they do not deliver it** |
| ⚠️ **R1 note** | Approaching ECS does **not** open the ELC. They are separate organisations and both are governed by contact-once independently |

## Funnel — corrected

| Metric | Count | Correction |
|---|---|---|
| **Orgs outreached** | **92** | ⬆️ from the 85 recorded this morning — **+7 sent by Chris on 08-20 after the run closed** |
| **Progress vs. 667** | **13.8%** | was 12.7% |
| Machine era | 54 | 46 `CCRR-core` + 8 `TX-workforce-boards` |
| Pre-machine | 38 | full 3-email sequence, Apr–Jul |

## 🆕 MARKET RUNWAY — mandatory report line from 2026-08-20 (R9)

**`target_drafts` is now 10 new organisations per working day.** At that rate depletion, not capacity,
becomes the binding constraint.

> **`Market: 92 outreached · ~490–700 remaining · ~49–70 working days of runway`**

| | |
|---|---|
| Universe estimate | **~580–790 organisations** |
| Remaining | **~490–700** |
| Runway at 10/day | **49–70 working days — mid-November to mid-December** |
| Working days left in 2026 | **90** (28 in Q3 · 62 in Q4) |

🔴 **THE MACHINE WILL EXHAUST THE NATIONAL MARKET BEFORE THE YEAR ENDS.** Every report now prints the
runway line, and **when runway drops below 20 working days the report RECOMMENDS a pace change.**
**Running out of market with weeks left in the year is a worse outcome than pacing slower** — and the
constraint has already moved off send volume onto conversion.

## Carried forward with dates

| Item | Date | Note |
|---|---|---|
| **[Org 0655] — earliest re-approach** | **~2026-09-22** | Email 3 lands ~09-01, then *"a few weeks"* (≥21 days). 🔴 **Requires Chris's authorisation** — the machine may propose, never start. R1's only exception |
| [Org 0548] · [Org 0564] | **2026-08-24** | Email 2 repairs — binding instructions in [[sequence-tracker]] |
| First Email 3 tranche | **2026-08-25** | 7 orgs, then 6 on 08-26 and 5 on 08-27 |

**`updated: 2026-08-20`**

---

# 🔄 PIPELINE UPDATE — 2026-08-21

## Funnel (§4) — live counts

| Metric | Count | Change |
|---|---|---|
| **Orgs outreached** | **92** | unchanged — **nothing was SENT tonight; 10 are drafted and waiting** |
| Orgs drafted, unsent | **10** | ⬆️ from 0 |
| Machine-era orgs | 54 | → **64 once tonight's 10 send** |
| Progress vs. 667 | **13.8%** | → 15.3% on send |
| Replied (machine era) | **7** | ⬆️ from 6 — Child Care Dutchess |
| Reply rate | **7 / 54 = 13.0%** | ⬆️ from 12.8% |
| 🎯 **Meeting booked** | **1** | ⬆️ **from 0 — the first machine-era booking** |
| Meeting held | 0 machine-era (4 pre-machine) | Dutchess call is 2026-08-25 |

## Cluster tags (§3)

| Cluster | Orgs contacted | Drafted tonight | Status |
|---|---|---|---|
| `CCRR-core` | 46 | **1** — [Org 0609] | R7 executed |
| `TX-workforce-boards` | 8 | **9** | ⬆️ **17 on send.** ~16 boards remain |

**Added tonight under `TX-workforce-boards`:** [Org 1272] · [Org 1267] · WFS for the Heart of Texas · [Org 1265] · WFS East Texas · WFS Alamo · [Org 1266] · [Org 1275] · WFS for North Central Texas.
**Added under `CCRR-core`:** [Org 0609] (`org0303.example`).

## State map (§3) — Texas, 12 more boards read in detail 2026-08-21

| Org | Own domain | Model | Tier-1/2 named | Addresses published? | Status |
|---|---|---|---|---|---|
| [Org 1272] | org0798.example | A | 4 | ✅ 3 of 4 | 📝 **DRAFTED — Tier 1** |
| [Org 1267] | org0257.example | A | 4 | ❌ none — 3 resolved by sweep | 📝 **DRAFTED — Tier 1** |
| WFS for the Heart of Texas | org0425.example | A | 5 | ✅ 1 of 5 — 1 more by sweep | 📝 **DRAFTED — Tier 1** |
| [Org 1265] | org0780.example | **B → [Org 1118] Workforce Development, LLC** | 1 | ✅ 1 | 📝 **DRAFTED — Tier 2** |
| WFS East Texas | org0284.example | A (via ETCOG) | **9** | ❌ **none — 8 null, 1 held** | 📝 **DRAFTED — Tier 3** |
| WFS Alamo | org0809.example | C → partnership | 0 | `trs_mentors@` · `ccs@` | 📝 **DRAFTED — Tier 4** |
| [Org 1266] | org0781.example | A | 0 (55 named, none in child care) | `austinccs@` · `ccsregistration@` | 📝 **DRAFTED — Tier 4** |
| [Org 1275] | org0795.example | A | 0 | `pbccs@` | 📝 **DRAFTED — Tier 4** |
| WFS for North Central Texas | org0260.example | A | **0 named at all** | `ccproviders@` | 📝 **DRAFTED — Tier 4** |
| WFS Brazos Valley | org0071.example | A (via BVCOG) | 1 | ⚠️ **broken mailto** | 🔴 **HELD — R15 open lead** |
| WFS Lower Rio Grande Valley | org0784.example | B — operator unnamed | 0 | ❌ JS-walled | 🔴 **HELD — Tier 5** |
| [Org 0609] | org0303.example | standalone (FL) | 1 | ❌ **zero on own domain** — 1 by sweep | 📝 **DRAFTED — Tier 1** |

### 🔴 TWO PRIOR MODEL-B CLAIMS ARE REFUTED — correcting the 2026-08-19 entry

**The 2026-08-19 sweep recorded that Heart of Texas routes to [Org 0329] and North Central Texas routes to [Org 0203]. Both were checked against the boards' own sites tonight and NEITHER IS SUPPORTED.**

| Claim | Verdict | Evidence |
|---|---|---|
| Heart of Texas → [Org 0329] | 🔴 **REFUTED** | `[Org 0329].org` appears on none of 5 pages read. Their early-education partner is **McLennan Community College**; their own child-care sub-brand is **ChildOne** (`childonetexas.com`) |
| North Central Texas → [Org 0203] | 🔴 **REFUTED** | `org0157.example` appears on none of 8 pages read. Their own training page is first-person. **[Org 0203] is the *Tarrant County* board's operator — a different board** |

**Both are Model A and both were drafted as themselves.** ⚠️ **The lesson is the one already in [[method]]: a claim about who operates a board is only worth what its source is.** Those two rows came from inference across boards rather than from each board's own site.

### Texas standing: 21 of ~28 boards now assessed

**Remaining unassessed (~7 boards):** Panhandle · South Plains · North Texas (Wichita Falls) · Northeast Texas · West Central Texas · Concho Valley · Golden Crescent · Texoma · Central Texas · Middle Rio Grande. **Plus AVANCE and Early Matters, still not researched — no claims made about them.**

## Florida standing — effectively closed

**With [Org 0609] drafted, every reachable Florida organisation has now been approached or held with a stated reason.** Remaining: **ELC of Miami-Dade/Monroe** (Apptegy JS shell — 🎯 *still the single highest-value browser session in the pipeline; the nav proves an in-house "Professional Development Institute" with its own page*) · **[Org 0566]** (only page naming humans dates to June 2021 and truncates the addresses) · **[Org 0554]** (not approached under R7 — zero of seven named staff hold a PD/training/quality title).

## Conversion ledger (§6) — re-derived 2026-08-21

| Stage | Pre-machine | Machine era | Combined | Rate |
|---|---|---|---|---|
| Orgs outreached | 38 | **54** | **92** | — |
| Replied | not tracked | **7** | **7 known** | **13.0% of machine era** |
| — routing / hand-off | — | 4 | 4 | ELCPBC · ELC Alachua · ELC Gateway · ELC Polk |
| — explicit decline | — | 1 | 1 | Thrive B5 — incumbent provider |
| — 🎯 **wants to talk** | — | **2** | **2** | **CCC Orange County · Child Care Dutchess** |
| Meeting proposed | — | **2** | 2 | CCC Orange County (3 times offered 08-20, unanswered) |
| 🎯 **Meeting booked** | — | **1** | 1 | **Child Care Dutchess — 2026-08-25** |
| Meeting held | 4 | **0** | 4 | Dutchess will move this on 08-25 |
| Offer made | 1 | 0 | 1 | n=1 — **do not treat the 3% offer rate as settled** |

**Meeting detection sources checked this run: Fathom ✅ (`list_meetings` since 2026-08-20T09:15Z → 0 new) · HubSpot ⚠️ partial by design · Google Calendar 🔴 connector still blocked.** The Dutchess booking is evidenced from **Gmail**, not from any of the three — exactly the gap R16 documents, and the reason Calendar needs reconnecting.

## 🆕 MARKET RUNWAY (R9)

> **`Market: 92 outreached · ~490–700 remaining · ~49–70 working days of runway`**

**Unchanged — nothing sent tonight.** On send it becomes 102 outreached, ~480–690 remaining, ~48–69 days. **Runway is well above the 20-day threshold; no pace change is recommended.**

⚠️ **But the constraint is visibly shifting.** Texas has ~16 boards left and Florida is closed. **At 10/day the machine has roughly a week and a half of *pre-researched* market before every night requires a fresh state sweep.** The next states in VALUE order should be queued now rather than at the point of exhaustion.

## Carried forward with dates

| Item | Date | Note |
|---|---|---|
| **[Org 0548] · [Org 0564]** | **2026-08-24** | 🔴 Email 2 bounce repairs — both need the parenthetical |
| First Email 3 tranche | **2026-08-25** | 7 orgs, then 6 on 08-26 and 5 on 08-27 |
| **Child Care Dutchess — MEETING** | **2026-08-25** | Fathom will register `meeting held` automatically |
| [Org 0655] — earliest re-approach | ~2026-09-22 | 🔴 Requires Chris's authorisation. R1's only exception |
| Blocked directories carried forward | — | ELC Gateway (JPEG) · ELC Heartland (PDF) · [Org 0541] · **WSET board roster (JPG)** · **Coastal Bend staff directory (SharePoint XLSX)** · **Permian Basin (bot wall — try `/wp-json/wp/v2/pages?search=staff`)** |

**`updated: 2026-08-24`**

---

# 🔄 PIPELINE UPDATE — 2026-08-24

## §4 · Funnel counts

| Field | Value | Note |
|---|---|---|
| **Orgs outreached (Email 1 SENT)** | **92** | ⏸ **unchanged.** The four sends on 2026-08-21 were all **Email 2 on existing threads** — follow-ups do not move this number |
| Orgs drafted, awaiting send — **Email 1** | **10** | The 08-21 Texas/ECS batch. Untouched over the weekend |
| Orgs drafted, awaiting send — **Email 2** | **8** | 7 created tonight + `ELCOC` carried from 08-21 |
| **Replied** | **8** ⬆️ +1 | 🆕 **[Org 0552]** — [Person 0197], Chief Programs Officer, 2026-08-21 |
| Meeting proposed | 1 | Child Care Dutchess |
| **Meeting booked** | **1** | Child Care Dutchess, **tomorrow 2026-08-25** |
| Meeting held | 4 pre-machine · **0 machine-era** | Fathom will register the Dutchess call automatically |
| Offer made | 1 pre-machine · 0 machine-era | *(n=1 — unstable, says so wherever printed)* |

## §6 · Conversion ledger

| Stage | Pre-machine | Machine-era | Total | Rate |
|---|---|---|---|---|
| Orgs outreached | 38 | **54** | **92** | — |
| **Replied** | — *(not tracked then)* | **8** ⬆️ | **8 known** | **~8.7% of all outreached · 14.8% machine-era** |
| Meeting proposed | — | 1 | 1 | ~1.9% machine-era |
| Meeting booked | — | **1** | 1 | ~1.9% machine-era |
| Meeting held | 4 | 0 | 4 | ~4.3% of outreached |
| Offer made | 1 | 0 | 1 | ~1.1% of outreached *(n=1)* |

🟢 **The machine-era reply rate crosses 14%.** Eight replies in fifty-four organisations. **Six of the
eight are identifiable by person, and four of those six came from a Cc recipient rather than the To**
— see [[recipient-profile]], where it is recorded as a pattern to watch, not a rule.

## §5 · Stage lists — no movement

**No organisation entered or left a stage tonight.** No discovery ran: the new-organisation target was
0 (10 Email 1 drafts already waiting), so Phase 6 had nothing to feed.

## 🆕 MARKET RUNWAY (R9)

> **`Market: 92 outreached · ~490–700 remaining · ~49–70 working days of runway`**

**Unchanged — nothing newly outreached tonight.** On send of the 10 waiting drafts it becomes
102 outreached, ~480–690 remaining, ~48–69 days. **Well above the 20-day threshold; no pace change
is recommended.**

⚠️ **The supply warning from 08-21 stands and is one working day closer.** Texas has ~16 boards left,
Florida is closed. **At 10/day there is roughly a week and a half of pre-researched market before
every night needs a fresh state sweep.** The next states in VALUE order should be queued now.

🔴 **AND THE REAL CONSTRAINT TONIGHT IS NEITHER SUPPLY NOR CAPACITY — IT IS THE SEND REVIEW.**
Ten Email 1 drafts have sat since Friday. At a required pace of 10 organisations per working day,
**Friday and today are both days the 667 arithmetic has not been paid.** That is [[method]] working
as designed — the machine may not draft past the cap — but it is worth naming plainly: *the drafts
are not the bottleneck.*

## ✏️ CORRECTION to the 08-21 carried-forward line

**The 08-21 entry recorded both 2026-08-24 repairs as *"both need the parenthetical."* That is wrong
for [Org 0564]** and contradicts the detailed binding instruction in [[sequence-tracker]],
which says explicitly: **no parenthetical — an inbox address was corrected, not a person dropped.**
**The tracker's instruction was followed.** Recorded so the summary line does not get trusted over the
instruction it summarised.

## Carried forward with dates

| Item | Date | Note |
|---|---|---|
| ~~[Org 0548] · [Org 0564] — Email 2 repairs~~ | ~~2026-08-24~~ | ✅ **DONE.** Both executed today, on schedule, as written |
| **First Email 3 tranche** | **2026-08-25** | 7 orgs. 🔴 **Every card carries the attachment gate — `HST_3PackStarterKit_email.pdf`, 2.7 MB, no send-as-is fallback** |
| **Child Care Dutchess — MEETING** | **2026-08-25** | Fathom will register `meeting held` automatically |
| [Org 0562] — domain drift | before ~2026-08-28 | R15 open lead, **`OPEN — 2 runs`**. Read `org0664.example` before Email 3 |
| Open leads | — | `person0169@org0807.example` **`OPEN — 4 runs`** · `person0302@org0329.example` **`OPEN — 4 runs`** *(may dissolve under R7)* |
| [Org 0655] — earliest re-approach | ~2026-09-22 | 🔴 Requires Chris's authorisation. R1's only exception |
| Blocked directories carried forward | — | ELC Gateway (JPEG) · ELC Heartland (PDF) · [Org 0541] · WSET board roster (JPG) · Coastal Bend (SharePoint XLSX) · Permian Basin (bot wall) — **asset URLs still not captured** |
| **Queue the next states in VALUE order** | before ~2026-09-03 | Texas ~16 left; no pre-researched market behind it |

---

# 🔄 PIPELINE UPDATE — 2026-08-24, LATER (8 Email 2 sends · reply #9)

## §4 · Funnel counts

| Field | Value | Note |
|---|---|---|
| **Orgs outreached (Email 1 SENT)** | **92** | ⏸ **unchanged.** All eight of today's sends were **Email 2 on existing threads** |
| Orgs drafted, awaiting send — Email 1 | **10** | The 08-21 Texas/ECS batch. Still untouched |
| Orgs drafted, awaiting send — Email 2 | **0** | 🟢 **Queue cleared.** All 8 sent ~14:00Z |
| **Replied** | **9** ⬆️ +1 | 🆕 **[Org 0548]** — [Person 0514], Director of Quality Impact, 28 minutes after send |
| Meeting proposed | 1 | Child Care Dutchess |
| **Meeting booked** | **1** | Child Care Dutchess, **tomorrow 2026-08-25** |
| Meeting held | 4 pre-machine · 0 machine-era | Fathom will register the Dutchess call automatically |

## §6 · Conversion ledger

| Stage | Pre-machine | Machine-era | Total | Rate |
|---|---|---|---|---|
| Orgs outreached | 38 | **54** | **92** | — |
| **Replied** | — *(not tracked then)* | **9** ⬆️ | **9 known** | **~9.8% of all outreached · 16.7% machine-era** |
| Meeting proposed | — | 1 | 1 | ~1.9% machine-era |
| Meeting booked | — | 1 | 1 | ~1.9% machine-era |
| Meeting held | 4 | 0 | 4 | ~4.3% of outreached |
| Offer made | 1 | 0 | 1 | ~1.1% of outreached *(n=1 — unstable)* |

🟢 **Machine-era reply rate crosses 16%** — nine replies in fifty-four organisations, up from 13.0%
on Friday. **Two of today's eight Email 2 sends produced a reply within the day.**

⚠️ **Both of today's replies are soft noes with an open door** (*"I will review your YouTube video and
will get back to you if it fits"*; *"keep your information on file… these opportunities do come about
throughout the year"*). **The reply rate is rising faster than the meeting rate.** Email 2 is very
good at getting an answer and has produced **one meeting in nine replies.** Recorded as the number to
watch, not as a problem to solve on n=9.

⚠️ **STILL NO LEDGER STAGE FOR "SOFT NO WITH A NAMED RE-ENTRY CONDITION."** **Three organisations now
qualify** — ELC Polk (RFPs), [Org 0552] (future planning), [Org 0548]
(current project needs). **Candidate stage `deferred — named re-entry condition`, raised this morning
and now backed by three cases.** A question for Chris.

## 🔴 SUPPRESSION — one address added by ruling

**`ccrr@org0315.example`** — removed from the outreach by Chris, 2026-08-24. **Never sent, never
bounced; excluded from the bounce rate.** [Org 0564] remains an active, reached organisation
via `kdouglas@` and `resources@`. **The org is not suppressed; one address is.**

## 🆕 MARKET RUNWAY (R9)

> **`Market: 92 outreached · ~490–700 remaining · ~49–70 working days of runway`**

**Unchanged — nothing newly outreached.** On send of the 10 waiting Email 1 drafts it becomes
102 outreached. **Well above the 20-day threshold; no pace change recommended.**

## Carried forward with dates

| Item | Date | Note |
|---|---|---|
| **Child Care Dutchess — MEETING** | **2026-08-25** | Fathom registers `meeting held` automatically |
| **Email 3 tranche — 7 orgs** | **2026-08-31** | Big Bend · Duval · Manatee · St. Lucie · Emerald Coast · Pasco & Hernando · ELCOC. 🔴 **Attachment gate on every card — `HST_3PackStarterKit_email.pdf`, 2.7 MB, no send-as-is fallback** |
| Earlier Email 3 tranches | 08-26 · 08-27 · 08-28 | Per prior cohorts, minus the 9 stopped sequences |
| [Org 0562] — domain drift | before ~2026-08-28 | R15 open lead, **`OPEN — 2 runs`** |
| Open leads | — | `person0169@org0807.example` **`OPEN — 4 runs`** · `person0302@org0329.example` **`OPEN — 4 runs`** |
| **Queue the next states in VALUE order** | before ~2026-09-03 | Texas ~16 left; no pre-researched market behind it |
| Blocked directories | — | ELC Gateway (JPEG) · ELC Heartland (PDF) · [Org 0541] · WSET (JPG) · Coastal Bend (SharePoint XLSX) · Permian Basin (bot wall) |

## ⏸️ PARKED — no due date, surfaces without nagging (Chris, 2026-08-24)

| Item | Status |
|---|---|
| **`ccrr@org0315.example` — deliverability verification** | 🟡 **HOLD-verify, NOT suppressed.** Needs a real mailbox check before reuse. **Tool not yet chosen.** ⏸️ **TABLED** |
| **D7 — bounce-adjacency rule** | *After a hard bounce at a domain, does a second address at that domain auto-draft or hold?* ⏸️ **TABLED** |

> ✅ **Chris:** *"I need to get these drafts out the door, so let's table that for now and come back
> to it to resolve later."* **Neither item is worked until he reopens it.**

---

# 🔄 PIPELINE UPDATE — 2026-08-25

## Funnel

| Stage | Machine era | Change tonight |
|---|---|---|
| **Orgs outreached** | **64** | **+10** — the Texas/Florida Email 1 batch was SENT 2026-08-24 22:13–22:16Z |
| Email 1 sent, Email 2 due | 33 | +10 due 08-31 · −5 drafted tonight |
| Email 2 sent, Email 3 due | 18 | −7 drafted tonight (**the first Email 3 tranche**) |
| **Email 3 drafted** | **7** | 🎯 **+7 — the machine's first ever.** All carry the attachment gate |
| Replies | **9** | **0 new** |
| Meeting booked | 1 | Child Care Dutchess — **TODAY, 2026-08-25** |
| Meeting held | 0 machine-era (4 pre-machine) | **Fathom will register it automatically after the call** |
| Hard bounces | **5** | **+1** — `person1226@org0798.example` |

**National progress: 64 orgs outreached of ~667 needed (9.6%).** ✏️ *corrected from 63 — counted from Ledger A rather than carried forward.*
**Market: 64 outreached · ~517–727 remaining · ~52–73 working days of runway** at 10/day.
**Runway is well above the 20-day line; no pace change is recommended on supply grounds.**
🔴 **The binding constraint tonight was not supply and not review — it was the bounce ceiling.**

## Due schedule, corrected

| Date | Owed |
|---|---|
| **2026-08-26** | ICP Oswego **Email 3** (repair instruction binding) · Suffolk · [Org 0985] · Schoharie · CAPC Jefferson · CCS CNY **Email 3** · [Org 0203] · Gulf Coast · ELC Sarasota · ELC Broward **Email 2** |
| **2026-08-27** | ACCORD · Sullivan · CCC North Country · DCCNY · [Org 0102] **Email 3** · **[Org 0655] Email 3** 🆕 *(ledger corrected 08-25 — Email 2 was sent 08-20, not left in drafts)* · [Org 1278] · WFS Rural Capital · [Org 1207] · [Org 0381] · [Org 0329] · ELC Florida's Heartland · [Org 1264] **Email 2** |
| **2026-08-28** | **[Org 0562] Email 3** 🔴 *the domain-drift question has to be settled first* |
| **2026-08-31** | The ten 08-24 organisations **Email 2**, including **WFS Coastal Bend with the R2 repair** |

⚠️ **2026-08-26 and 08-27 are the heaviest days the machine has faced** — roughly 10 and 13
follow-ups, most of them Email 3s carrying the attachment gate. **Chris attaches the PDF by hand on
every one of them.**

## 🔴 New-org drafting is STOPPED

**0 organisations carded. 10 were owed.** The machine-era bounce rate crossed the `max_bounce_rate_pct`
ceiling of 3% and stands at **3.36%** of non-catch-all addresses (3.18% raw). **This is a control
firing correctly, not a discovery shortage** — the pool is not the constraint and `pool_ceiling` was
never approached. **Three options are put to Chris in [[review-2026-08-25]] §3.**

## Blocked directories carried forward — unchanged, still uncaptured

ELC Gateway (JPEG) · ELC Heartland (PDF) · [Org 0541] · WSET board roster (JPG) ·
**Coastal Bend (SharePoint XLSX)** · Permian Basin (bot wall).
⚠️ **Coastal Bend is now the organisation with a bounced address AND an unreadable staff directory.**
Its three usable addresses all came from a machine-readable substitute page. **If the R2 repair on
08-31 leaves it at 2 of 3, the SharePoint file is the only remaining route to a third recipient.**

---

# 🔄 PIPELINE UPDATE — 2026-08-26

## Funnel

| Stage | Machine era | Change tonight |
|---|---|---|
| **Orgs outreached** | **64** | **0** — nothing was SENT. The 10 Email 1s from 08-25 are **scheduled**, firing 08-26 13:00Z/14:00Z |
| Email 1 drafted, awaiting send | **20** | **+10** — and the 10 already queued were miscounted as 0 by `list_drafts`. See below |
| Email 1 sent, Email 2 due | 33 | −4 drafted tonight |
| Email 2 sent, Email 3 due | 18 | −6 drafted tonight · −1 **CANCELLED** (ELCHC declined) |
| **Email 3 drafted** | **13** | **+6** — all carry the attachment gate |
| Replies | **10** | **+1** — ELCHC, a decline |
| Meeting booked | **2** | Child Care Dutchess (08-25) · CCC Orange County |
| Meeting held | **0 machine-era** (4 pre-machine) | ⚠️ **The 08-25 Dutchess call produced no Fathom recording** |
| Hard bounces | **5** | **0 new** |
| **Orgs HELD with a stated reason** | — | **+2** — WFS North Texas, WFS Northeast Texas (both WAF-walled) |

**National progress: 64 orgs outreached of ~667 needed (9.6%).** Unchanged — **outreach is counted on
SEND, not on draft, and nothing sent today.** That will read 74 (11.1%) once today's scheduled batch fires.
**Market: 64 outreached · ~517–727 remaining · ~52–73 working days of runway** at 10/day.

## 🔴 THE COUNT THAT WAS WRONG, AND WHY IT MATTERS TO THIS DASHBOARD

**`list_drafts` returned zero. Ten Email 1s were committed to send four hours later.** Gmail scheduled
sends carry neither the `DRAFT` nor the `SENT` label, so **every draft-based count in this file is
blind to them.** Tonight the error was caught because HubSpot showed 26 contacts created against ten
domains with no matching Sent mail and no matching draft.

**The queue line is the one that breaks first:** `Queue: 20 waiting · runs of slack: 2.0` is correct
only because this run counted the scheduled batch by hand. **A run that trusts `list_drafts` reads
`waiting: 0`, `runs of slack: 0`, and over-drafts.** Candidate control for Chris in
[[review-2026-08-26]] §DECISIONS.

## Cluster tags (§3)

| Cluster | Orgs contacted | Drafted tonight | Held tonight | Status |
|---|---|---|---|---|
| `CCRR-core` | 46 | **0** | 0 | — |
| `TX-workforce-boards` | 17 | **8** | **2** | ⬆️ **25 on send.** ~1 board remains unassessed |
| `NY-ccrr` | 20 | **2** | 0 | ⬆️ Westchester + [Org 0085]. **The state is far from exhausted** |

## State map (§3) — Texas, the last 10 boards assessed 2026-08-26

| Org | Own domain | Mail domain | Model | Tier-1/2 named | Addresses published? | Status |
|---|---|---|---|---|---|---|
| [Org 1274] | org0810.example | org0810.example | A | **38** | ❌ **none — all Contact Form 7 modals** · 3 by sweep | 📝 **DRAFTED — Tier 1** |
| [Org 1277] | org0802.example | **org0692.example** | **UNKNOWN — unnamed "CCS Contractor"** | **0** | `childcareservices@` only | 📝 **DRAFTED — Tier 7** |
| [Org 1273] | org0786.example | org0786.example + **org0803.example** | A (leaning) | 6 | ✅ 1 of 6 · 1 more by sweep | 📝 **DRAFTED — Tier 1** |
| Concho Valley WFS | org0243.example | org0243.example | UNKNOWN — unnamed contractor | 2 | ✅ **2 of 2** | 📝 **DRAFTED — Tier 1** |
| [Org 1269] | org0399.example | org0399.example | A | 1 | ❌ none — **sweep returned Extrapolated, rejected** | 📝 **DRAFTED — Tier 3** |
| WFS Texoma | org0801.example | **org0785.example** | A | 2 | ✅ 1 of 2 · 1 more by sweep | 📝 **DRAFTED — Tier 1** |
| [Org 1271] | org0799.example | org0799.example | A | 1 | ❌ **own site is a "Coming Soon" placeholder** · 1 by sweep | 📝 **DRAFTED — Tier 1** |
| [Org 1270] | org0783.example | org0783.example | A | **3** | ✅ **3 of 3** | 📝 **DRAFTED — Tier 1** |
| WFS North Texas | org0561.example | UNKNOWN | UNKNOWN | UNKNOWN | 🔴 **9 URLs, all 200-empty-body** | 🔴 **HELD — WAF wall** |
| WFS Northeast Texas | org0546.example | UNKNOWN | UNKNOWN | UNKNOWN | 🔴 **10 URLs, all 200-empty-body** | 🔴 **HELD — WAF wall** |

### Texas standing: 27 of ~28 boards now assessed

**Remaining: WFS Brazos Valley** (HELD, broken mailto, R15 open lead) · **WFS Lower Rio Grande Valley**
(HELD, JS-walled) · **plus AVANCE and Early Matters, still not researched — no claims made about them.**
🔴 **TEXAS AS A DISCOVERY SOURCE IS ESSENTIALLY EXHAUSTED.** After today's sends the cluster stands at
25 of ~28 boards, with the three unreachable ones needing a browser session rather than more discovery.
**The next cluster has to come from somewhere else, and tonight's loop already pointed at it: NY-ccrr.**

## 🆕 THE SUPPLY QUESTION, RAISED EARLY RATHER THAN AT ZERO

**§0.8.4 exists because the machine had every number it needed to predict an empty outbox and printed
no warning.** The same shape is forming one level up:

| Cluster | Runway at 10 orgs/day |
|---|---|
| `TX-workforce-boards` | **~0 days — exhausted** |
| `CCRR-core` (FL) | **~0 days — Florida closed 08-21** |
| `NY-ccrr` | **unknown, and it is now the only live source** |

🔴 **Two of three clusters are at zero and nothing has been counted for the third.** New York has
roughly 35 CCR&R agencies; 20 have been contacted; **the remaining pool has never been enumerated.**
**Recommendation, not an assumption: enumerate the NY CCR&R roster before the pool becomes the
constraint.** Tonight's two NY orgs were found by naming them from knowledge, not from a pipeline —
**which works twice and does not work ten times.**

## Blocked directories carried forward

ELC Gateway (JPEG) · ELC Heartland (PDF) · [Org 0541] · WSET board roster (JPG) ·
Coastal Bend (SharePoint XLSX) · Permian Basin (bot wall) · [Org 0308]
(empty-body staff page) · 🆕 **WFS North Texas** · 🆕 **WFS Northeast Texas**.

**Nine organisations are now held behind an unreadable page.** 🔴 **Six of the nine would be solved by
one browser session.** That is no longer an occasional edge case — **it is the single largest category
of held organisations in the pipeline.**

## Due schedule

| Date | Owed |
|---|---|
| **2026-08-27** | ACCORD · Sullivan · CCC North Country · DCCNY · [Org 0102] **Email 3** · **[Org 0655] Email 3** · [Org 1278] · WFS Rural Capital · [Org 1207] · [Org 0381] · [Org 0329] · ELC Florida's Heartland · [Org 1264] **Email 2** — **13 follow-ups, the heaviest day yet** |
| **2026-08-28** | **[Org 0562] Email 3** 🔴 *the domain-drift question must be settled first — R15 open 4 runs* |
| **2026-08-31** | The ten 08-24 organisations **Email 2**, including **WFS Coastal Bend with the R2 repair** |
| **2026-09-01** | [Org 0539] · [Org 0587] · [Org 0584] · [Org 0582] · [Org 0568] **Email 3** *(ledger corrected tonight — Email 2 was SENT 08-25, not left in drafts)* · [Org 0308] **retry** |
| **2026-09-02** | ELC Sarasota · ELC Broward · [Org 0203] · Gulf Coast **Email 3** · **WFS North Texas + Northeast Texas retry** |

**ELCHC Email 3, previously due 08-28, is CANCELLED — the sequence stopped on a decline.**

---

# 🔄 PIPELINE UPDATE — 2026-08-27

## 🎯 THE NY CCR&R MARKET IS ENUMERATED — the open question from 08-26 is closed

08-26 recorded: *"New York has roughly 35 CCR&R agencies; 20 have been contacted; the remaining pool has
never been enumerated."*

**Source: Early Care & Learning Council statewide membership directory —
`https://org0190.example/Uploads/CCRCDirectory2024.pdf`. 35 members, with counties served.**
Corroborated by CUNY PDI (*"There are 34 CCR&Rs across New York State"*) and by ECLC's own members page.

⚠️ **Dated 2024 — over the six-month `source_medium` limit. Used to ENUMERATE ORGANISATIONS ONLY.
No address or title from it was used as Gate 1 evidence.**

| NY-ccrr disposition | N |
|---|---|
| Contacted before 2026-08-27 | 23 |
| Drafted 2026-08-27 | 8 |
| Held 2026-08-27 with a named reason | 4 |
| **Total** | **35** |

🔴 **`NY-ccrr` RUNWAY: ~0 days. All three worked clusters are now at zero** —
`TX-workforce-boards` exhausted, `CCRR-core (FL)` closed 08-21, `NY-ccrr` exhausted tonight.
**This is now the binding constraint on the outreach floor, exactly as the 08-26 supply note predicted.**

🎯 **RECOMMENDATION — open a new cluster before the 2026-09-01 run.** The shape that worked tonight is
*a statewide CCR&R association that publishes a member directory*. PA, OH, NC and MI all have one.
**§0.7's rank-list vocabulary review fires before the first batch of whichever is chosen.**

## Blocked / anonymised directories carried forward — now TEN

ELC Gateway (JPEG) · ELC Heartland (PDF) · [Org 0541] · WSET board roster (JPG) ·
Coastal Bend (SharePoint XLSX) · Permian Basin (bot wall) · [Org 0308] ·
WFS North Texas · WFS Northeast Texas · 🆕 **[Org 0125]**
(5 empty-body URLs + 3 non-extractable PDFs; child-care staff block prints titles with zero names).

🆕 **A new sub-class worth separating: DELIBERATELY ANONYMISED directories.** [Org 0180]
and Niagara CAP both render fine — they simply publish no personal names, or publish mailboxes with no
names attached. **That is not a broken page, it is an editorial choice, and no browser session fixes it.**
Chautauqua was drafted at its role inbox under E1.7's justified-descent clause; Niagara was held because
one named human there IS reachable, which closes that clause.

## 🔴 NEW ORG-IDENTITY CLASS: SHARED INSTITUTIONAL MAIL TENANTS

Three of tonight's thirteen mail from a domain the organisation does not own:
`org0572.example` (St. Lawrence — **already aliased to ICP Oswego**), `org0227.example` (CCE Oneida — shared
across every CCE association in NY), `org0553.example` (St. Lawrence, in `mailto:` targets only).

**`config.domain_aliases` has no concept for this.** An alias would merge unrelated organisations under
R1; no alias leaves `dedup_check.py` returning HOLD forever. **Both orgs held pending Chris's ruling —
see [[review-2026-08-27]] D2.**

---

# 🔄 2026-08-31 — CALIFORNIA OPENS PROPERLY · NORTH CAROLINA ENUMERATED · 20 orgs assessed

**The 08-27 entry closed with `NY-ccrr` RUNWAY ~0 days and all three worked clusters exhausted.
The 08-28 run opened NC and CA without recording either here. This entry catches both up.**

## §3 · Cluster tags — two new clusters, both now recorded

| Cluster | Universe | Contacted | Remaining | Source of the enumeration |
|---|---|---|---|---|
| `CCRR-core (FL)` | ~30 | 30 | **0** | closed 08-21 |
| `TX-workforce-boards` | ~28 | 27 | ~1 | 27 of 28 assessed 08-26 |
| `NY-ccrr` | 35 | 35 | **0** | Early Care & Learning Council directory, closed 08-27 |
| 🆕 `NC-ccrr` | **14 regional lead agencies** | **9** | **5** | 🔴 **AUTHORITATIVE: the CCR&R Council of NC's own regions page — https://www.childcarerrnc.org/about/regions/** |
| 🆕 `CA-ccrr` | **~58 member agencies** (CA Child Care R&R Network) | **11** | **~47** | CA R&R Network membership + CDE county R&R pages |

## 🔴 NC IS ENUMERATED AND NEARLY CLOSED — 14 lead agencies, 9 contacted

| Region | Lead agency | Domain | Status |
|---|---|---|---|
| 1 | [Org 0057] | org0017.example | HELD 08-28 (Wix layout, name-to-title reconstructed not read) |
| 2 | **[Org 0439]** | org0232.example | 🎯 **AVAILABLE** — board page returned an empty body; retry 09-07 |
| 3 | [Org 0808] | org0526.example | HELD 08-28, retry 09-04 |
| 4 | [Org 0511] (formerly Child Care Services Association) | org0279.example | contacted 08-28 |
| 5 | Cumberland County Partnership for Children | [Org 0135].org | contacted 08-28 |
| 6 | [Org 0298] | org0187.example | HELD 08-28 — only named human is the CEO |
| 7 | [Org 0241] | org0098.example | contacted 08-28 · 🟢 **REPLIED in 36 min** |
| 8 | [Org 1119] | org0701.example | contacted 08-28 · 1 bounce |
| 9 | **[Org 0745]** | org0448.example / org0435.example | 🆕 **DRAFTED 08-31** |
| 10 | [Org 0283] | org0185.example | contacted 08-28 |
| 11 | [Org 0671] | org0401.example | contacted 08-28 |
| 12 | [Org 0511] | (same entity as Region 4) | contacted 08-28 |
| 13 | **[Org 0178]** | org0144.example | 🆕 **DRAFTED 08-31** |
| 14 | [Org 0472] | org0256.example | contacted 08-28 |

⚠️ **`childcareservices.org` 301-redirects to `org0279.example`.** Same legal entity, rebranded. It is not a
fresh domain and must never be treated as one.
⚠️ **[Org 1252] is NOT a CCR&R** — Region 12 is [Org 0511]. It was assessed and rejected on
both grounds (not a CCR&R, and zero published addresses).

## §0.7 · NC RANK-LIST VOCABULARY REVIEW — delivered, three sites read

🔴 **In North Carolina, "Early Education Specialist" and "Early Care & Education Manager" are PD/technical-
assistance roles, not classroom roles.** A ranker tuned on Florida ELC vocabulary under-weights both.

**Add to R4 rank 1:** `Workforce` · `Quality Enhancement` · `Professional Development Specialist` ·
`Early Education Specialist` · `Early Care & Education Manager` · `Technical Assistance` ·
`Practice-Based Coaching` · `Star Rated License` · `Healthy Social Behaviors` · `Infant Toddler Specialist`.

*Chatham County's entire PD department is called **Workforce Development**; Smart Start's standard title for
a coach is **Quality Enhancement Specialist**. Neither word appears in R4's Florida-derived rank-1 list.*

## 🆕 CA — 11 of ~58, and the region has a structural characteristic worth planning around

**Contacted / drafted:** org0637.example (statewide umbrella) · org0089.example · org0580.example ·
org0134.example · org0185.example · 🆕 org0045.example · org0592.example · org0235.example ·
org0236.example · org0819.example · org0242.example · org0459.example · org0151.example.

🔴 **CALIFORNIA PUBLISHES FEWER NAMED-HUMAN ADDRESSES THAN ANY CLUSTER WORKED SO FAR.** Of 20 CA agencies
assessed tonight, **7 publish zero individual addresses anywhere on their own domain** and route everything
through department inboxes and web forms. Los Angeles County is the extreme case: neither [Org 0444]
(520 staff) nor [Org 0963] (64 staff) publishes a single one.

🎯 **The consequence is a planning fact, not a research failure: California costs Apollo credits.** [Org 0962]
LA went from a one-generic-inbox send at Redundancy 1 to three named humans at Redundancy 3 for ~3 credits.
**Budget the roster sweep for CA rather than treating a thin card as an exhausted org.**

## Blocked / anonymised directories carried forward — now FOURTEEN

ELC Gateway (JPEG) · ELC Heartland (PDF) · [Org 0541] · WSET board roster (JPG) ·
Coastal Bend (SharePoint XLSX) · Permian Basin (bot wall) · [Org 0308] ·
WFS North Texas · WFS Northeast Texas · [Org 0125] ·
🆕 **[Org 0377]** (staff directory **password protected** — a new sub-class again) ·
🆕 **Kern County Superintendent of Schools** (`/directory/` renders headers with zero rows, JS-injected) ·
🆕 **[Org 0439]** (empty body) · 🆕 **Pomona USD Child Development** (no addresses, forms only).

## §4 · Funnel

| Stage | N |
|---|---|
| Identified (all clusters) | ~700 |
| Assessed | 152 |
| Outreached (org-level, R1-closed) | **132** |
| Held with a named reason | 20 |
| Replied | 15 |
| Meetings held | **3** |

## 🆕 MARKET RUNWAY (R9)

```
Market: 132 outreached · ~535 remaining · ~13 working days of runway
```

🔴 **UNDER 20 DAYS. R9 fires: the report recommends a pace change.** ~47 CA agencies and 5 NC lead agencies
are the whole of the confirmed near-term supply, and at 10/day that is ~5 working days before the cascade
reaches T3 with nothing in front of it again. **The next cluster should be chosen and vocabulary-reviewed
before it is needed, not after.** The shape that has worked three times is *a statewide CCR&R association
that publishes a member directory* — **PA, OH, MI and WA all have one and none has been touched.**

---

# 🔴 CORRECTION 2026-08-31 (later) — THE CLUSTER TAGS IN THIS FILE ARE RETIRED

> ✅ **Chris, 2026-08-31:** *"A new state is not a new market. So, multiple CCR&Rs in different states
> are still part of the same cluster… Workforce solutions groups are a different market… School
> districts would also be considered a different market… Let's stick with CCR&Rs until I create a new
> Green Sheet for the next cluster."*

**Everything above in this file that says "cluster" and means a geography is wrong.** The entry written
earlier tonight is the worst offender — it added `NC-ccrr` and `CA-ccrr` to a §3 table of five
"clusters", four of which were states.

## The correct structure

**One cluster = one Method × one Market × one Message** (`CL-YYYY-QN`), per [[cluster-pipeline]] and
[[ClusterChecklist]]. **This machine serves exactly one:**

**`CL-2026-Q3` = MTH-001 Verified Cold Outreach × MKT-001 CCR&Rs and ECE intermediaries × MSG-001 v3.**

**A geography is a REGION, not a cluster.** Re-tagged:

| ❌ Retired tag | ✅ Correct reading | Orgs |
|---|---|---|
| `CCRR-core (FL)` | **MKT-001 · region: Florida** — closed 08-21 | 30 |
| `NY-ccrr` | **MKT-001 · region: New York** — closed 08-27 | 35 |
| `NC-ccrr` | **MKT-001 · region: North Carolina** — 9 of 14 lead agencies | 14 |
| `CA-ccrr` | **MKT-001 · region: California** — 11 of ~58 | ~58 |
| 🔴 `TX-workforce-boards` | **NOT MKT-001 AT ALL. A separate market — now [[Market-Library]] MKT-006** | 21 sent, 2 held |

🔴 **MKT-001's universe is therefore ONE pool of ~550–750 organisations, not five.** The runway line
below is a single number for a single market, and it always should have been.

## What this changes about the runway

```
Market: 111 MKT-001 organisations outreached · ~535 remaining · ~13 working days of runway
Out-of-market, already sent (MKT-006 workforce boards): 21 — sequences finish, no new boards drafted
```

⚠️ **The earlier entry tonight said "132 outreached."** That number silently mixed two markets. **111
is the MKT-001 figure** and it is the one the cluster's kill condition is scored against
(*offer rate <1.5% at 150 fully-sequenced orgs*). **21 workforce boards were never part of that
denominator and must be lifted out of it** before CL-2026-Q3's decision date on 2026-10-15.

## The supply question, restated honestly

**MKT-001 remaining, confirmed:** ~47 California member agencies · 5 North Carolina lead agencies ·
scattered singles elsewhere. **The ~535 national figure is an estimate; the confirmed near-term
supply is ~52 organisations, or about five working days at ten a night.**

🔴 **AND THE MACHINE MAY NOT SOLVE THIS BY ITSELF ANY MORE.** [[method]] §0.7.2: when MKT-001 is
exhausted the run reports `Outreach floor: FAILED — MKT-001 exhausted, awaiting a Green Sheet for the
next market` as a **named safety gate**. Widening into an adjacent org type is now forbidden, and the
floor yields.

**The right next moves are Chris's, not the machine's:**
1. **Enumerate the rest of MKT-001 properly.** The national universe has never been listed — only
   estimated. Four states have been enumerated from a directory; ~45 have not. **This is machine work
   and it is the cheapest runway available.**
2. **Green Sheet for the next market.** [[ClusterChecklist]] Phase 1 ⭐. MKT-006 is warmest — 21
   accidental sends already de-risked it and proved the copy needs a rewrite.

---

# 🔄 PIPELINE UPDATE — 2026-09-01 · 19 CALIFORNIA AGENCIES ASSESSED, 11 DRAFTED

## §4 · Funnel

| Stage | N | Δ vs 08-31 |
|---|---|---|
| Identified (all markets) | ~700 | — |
| Assessed | 171 | +19 |
| Outreached — MKT-001 only, org-level, R1-closed | **122** | +11 |
| Outreached — MKT-006 workforce boards (frozen, no new orgs) | 21 | — |
| Held with a named reason | 27 | +7 |
| Replied | 16 | +0 |
| Meetings held | 3 | — |
| **Meetings BOOKED** | **1** | 🎯 **+1 — Cleveland County, Wed 2026-09-02 11:00 MDT** |

## 🆕 CA — 30 of ~58 assessed. The structural fact is now confirmed twice.

**Drafted 2026-09-01 (11):** org0686.example · org0494.example · org0687.example · org0648.example ·
cc.org0706.example · org0377.example · org0049.example · org0233.example · org0430.example · org0455.example · org0481.example.

🔴 **11 of tonight's 19 agencies publish NAMES but ZERO individual addresses** — the same finding as
08-31, on a fresh sample. **Six were recovered by roster sweep for 14 Apollo credits; five were not
recoverable at all.** California is a credit-cost region, not a thin-yield region, and a thin card here
is a budget decision rather than an exhausted organisation.

## Blocked / anonymised / address-free directories carried forward — now TWENTY

ELC Gateway (JPEG) · ELC Heartland (PDF) · [Org 0541] · WSET board roster (JPG) ·
Coastal Bend (SharePoint XLSX) · Permian Basin (bot wall) · [Org 0308] ·
WFS North Texas · WFS Northeast Texas · [Org 0125] ·
[Org 0377] (password-protected) · Kern County Sup. of Schools (JS-injected directory) ·
[Org 0439] (empty body) · Pomona USD Child Development ·
🆕 **CAPSLO** (three pages return HTTP 200 with an EMPTY BODY) ·
🆕 **[Org 1080]** (JS-only, no server-side HTML) ·
🆕 **[Org 1233]** (JS contact form, phone/fax only) ·
🆕 **[Org 1129] / org0381.example** (no named person, no programme address) ·
🆕 **[Org 0176]** (names ZERO humans anywhere on its own site) ·
🆕 **CDRC Santa Cruz COE** (script-populated staff directory served no CDRC rows).

## 🔴 OUT OF MARKET — recorded so no future run re-researches them

| Domain | Org | Why |
|---|---|---|
| `org0121.example` | [Org 0169] (PA) | Not a CCR&R and not in California — youth services, shelter, court-referred programmes. **Checked because Chris saved `person0057@org0121.example` to HubSpot at 2026-09-01T01:35Z** |
| `org0404.example` | [Org 0677] | Operates licensed centers rather than serving providers — fails the function test |
| `org0522.example` | Monterey County portal | A partner-coalition information site, not a staffed agency; routes its R&R to MAOF |

## 🆕 MARKET RUNWAY (R9) — WORSE THAN FRIDAY

```
MKT-001: 122 outreached · confirmed near-term supply ~34 orgs · ~3.4 working days
```

🔴 **Down from ~5 working days on 08-31.** ~33 un-assessed California agencies plus Craven County (NC,
retry 09-07) are the whole of the confirmed supply. **The cheapest machine-side extension — enumerating
the ~45 never-touched states of MKT-001, starting with the four statewide CCR&R associations that
publish member directories (PA, OH, MI, WA) — has still never been run, and §0.7.2 makes it free: a new
state is a new REGION, not a new market.** Proposed as a bounded T3 discovery increment for the next run.


## 2026-09-23 — California ENUMERATED (step 12b) from the CA Child Care R&R Network directory
57 employers, 58/58 counties ([Jan 2026 directory PDF](https://org0637.example/assets/general-files/Jan-26-directory.pdf)). CDSS cites 69 R&R programs; its contractor PDFs are encrypted and did not read, so a non-member contractor could be missing. Dispositions: 41 contacted (32 already + 9 tonight), 14 held, 2 remaining (surplus in ready-queue), 1 out-of-market. Detail: `territory.json` CA · `runs/2026-09-23/ca_enumeration.json`.


## 2026-09-24 — DE, NV, WA, OK ENUMERATED (step 12b) · CA SATURATED
- **CA** saturated 09-24 (T1 drew HRN Trinity + [Org 0175]).
- **DE** — [MyChildDE provider supports](https://mychildde.org/providers/provider-supports/): 1 statewide CCR&R ([Org 0332]), 3/3 counties. HELD (no own-site personal addresses; referral-only fit doubt).
- **NV** — [DSS child care resources](https://www.dss.nv.gov/programs/child-care/childcare-resources/): [Org 1160], 17/17 counties → drafted. Las Vegas [Org 1230] unverified (held).
- **WA** — [CCA-WA Regional Partners](https://org0161.example/about/regional-partnership/): network + 6 regions, 39/39 counties. 1 drafted · 2 CLOSED_R1 ([Org 0087]/org0153.example, CCA NW/org0579.example — pre-machine cohort) · 4 held.
- **OK** — [OPSR Local Agencies PDF](https://www.org0575.example/_files/ugd/739cfc_2b8bec74938b443fad17a09904329135.pdf): 7 agencies / 8 contracts, 77/77 counties. 5 drafted · Ivy to ready-queue · NW CDSA held (alias).
- DE and NV had each carried `held: 1` since 09-03 from MIS-ASSIGNED orgs (Catholic Charities Delaware County NY; [Org 1080] CA). Corrected.

## 2026-09-28 — PA territory opened, 13 employers enumerated from state open-data

Pennsylvania's 19 ELRC regions collapse to ~13 distinct operating employers (`data.pa.gov/resource/fn8n-rgds.csv`
+ `org0588.example/elrcs/`). 4 drafted (Early Learning Connections/ELRC3, Community Connections for
Children/ELRC10, ELRC5 Allegheny County, ELRC18 Philadelphia/PHMC), 9 held with reasons (see
`territory.json` PA row and `candidates.jsonl`). Michigan's GSQ system found mid-operator-transition
(new operators effective 2026-10-01) and deliberately not researched further — see review-2026-09-28.


---

# 🔄 PIPELINE UPDATE — 2026-09-29

**T3 discovery ran at territory level, not people level.** OH enumerated (12 SDAs = 7 employers; 88/88 counties by count; source = OCCRRA, NOT the state DCY page, which returned no list) and saturated in one night: 5 drafted, 2 held. NJ enumerated (childcarenj.gov/CCRR: 14 employers, 21/21 counties by count) and opened: 3 drafted, 2 held, 1 CLOSED_R1, 8 remaining — **of the 8, 6 already carry Gate-1 evidence in `ready-queue.md`**. PA saturated THIN (6 of 13 held).
**Funnel this run:** 28 carded → 10 drafted · 10 held (PA 6, OH 2, NJ 2) · 2 CLOSED_R1 by de-dup (Community Services for Children, Programs for Parents) · 8 NJ organisations researched to Gate 1 and not drafted (6 banked in ready-queue as T1, 2 weaker).


## 2026-09-30 - territory walk: NJ saturated, MA opened, enumerated, 4 drafted
NJ: 6 drafted from T1 (banked 09-29); Bergen County and [Org 1230] HELD (D-DOUBT) -> NJ SATURATED (9 contacted, 1 CLOSED_R1, 4 held = 29%, under the thin-saturation guard). MA: enumerated from https://www.mass.gov/info-details/2024-eec-ccrr-region-changes (5 EEC regions = 6 employers; [Org 1068] runs Central + Western), enumeration written to territory.json BEFORE any MA draft. 4 drafted ([Org 1068], QCAP, Child Care Choices of Boston, Child Care Circuit), 1 HELD (PACE), 1 banked (CACCI, Gate-1 done). `counties_covered: 0` is unverified, not zero - the state directory publishes no county map. Next after MA in `territory.json.order`: NE, DE (saturated), CT.



---
## 2026-10-02 - territory walk: MA saturated, MI enumerated and worked
MA: CACCI drafted from the bank (Apollo identity high); PACE held retry 10-14 -> MA SATURATED. MI: 7 operators / 10 regions enumerated before drafting; Saginaw ISD drafted; COOR ISD, [Org 1240], Child Care Network MI, 4C of the UP, [Org 0887] held (D-DOUBT, retries 10-09/10-16); Leaps and Bounds R1-closed via org0794.example. Next territory is Chris's to open (D23). Floor 2 of 10.

## 2026-10-04 (extra) - territory walk after the cap raise
NE held (state-run); CT worked ([Org 0447] drafted; TEAM/211/RESCs held, Shine out of market); NM closed (UNM R1, CNM held); MO worked (CCAMO, U4C drafted); OR worked (Clackamas, Douglas, SOESD, CGCC, SOCC drafted; [Org 0885] R1; Harney + 7 Gate-1 holds); MT worked (MT ECP drafted; 2 CCR&Rs R1-closed; SPARK/MCCBC held); WV worked (WVECTCR drafted; RVCDS siblings, CCRC, MountainHeart held). Next territory in order: MS. 10 drafts on a 10-ask.

- 2026-10-07: MS saturated thin (5 of 5 held). AR/LA/AL opened but NOT enumerated. Held: MSU MS LIFT, [Org 0464], NPC CCA WCA, Fort Payne CRN, TCR CCC, Children's Coalition NE LA.

- 2026-10-08: AR saturated thin (2 contacted / 3 held). LA: AFC, VOA SCLA, CCNELA drafted; PCECC held (role inboxes). AL: FGC, CRN drafted; GRECS, [Org 0327] Birmingham, TCR Corp held. NC reopened for 5 drafts (Dare, Wayne, Johnston, Wilson, Buncombe); Alamance, Carteret held. Unvisited NC with staff pages worth reading next: Stanly (/staff/), Brunswick (/about/staff/), FGV (/about/our-team/).

- 2026-10-08 (pass 2): NC saturated (20 drafted, 17 held, 2 CLOSED_R1 aliases: org0599.example=[Org 0934], org0199.example=[Org 0671]). AL: [Org 1144]/South drafted. ID (University of Idaho, one org), ND (1), SD (2 of 6; 4 held on generic inboxes) saturated. Next in order: LA. Held for follow-up research: Caswell, Pamlico, Richmond, Montgomery (fit); Blue Ridge, Harnett, Albemarle, Martin-Pitt, Puzzles (Gate 1); [Org 0327] (org0107.example), Gulf Regional (org0410.example), CDR/UA (mismatch).

- 2026-10-09: territory walk exhausted. LA, AL, WY, AK, HI, VT, DC worked: 4 drafted (AK 1, VT 2, HI 1), 15 held (school-district and government non-markets, partner.vermont.gov shared domain, no published addresses, D-DOUBT). Retry 2026-10-23. Next territory is Chris's to open.

- 2026-10-09 (pass 2): R6 reopen walk NC, MD, RI, MN, WI, FL, NY, VA: 25 drafted (NC 12, MD 2, RI 1, MN 2, WI 3, FL 1, NY 2, VA 2), 7 held (Carteret, Jones, Montgomery NC, Promise Resource Center domain hijacked, Pine *AT*, 4C Florida, Seminole). VA Fairfax + VECF remain REMAINING (next up). Retry 2026-10-23.
- 2026-10-10 (drain1): 9 of 118 non-CO REMAINING orgs drafted (CT 1, VA 2, KS 1, IL 1, CA 1, WA 1, PA 2). 109 remain REMAINING. 60 orgs researched; research blocked by WebFetch proxy 429, so drafting used live browser reads only. Not drafted though researched: Bergen NJ idx40/44 duplicate, Delco redirect, [Org 0746] href mismatch, ULOHC typo address.

- 2026-10-10 (drain2): 66 of 109 remaining non-CO orgs drafted (AK 1, AL 2, AR 2, CA 4, CT 5, DC 1, DE 1, GA 3, IL 1, IN 2, LA 3, MA 1, MI 3, MO 3, MS 2, MT 1, NE 1, NJ 3, OH 2, OK 2, OR 3, PA 2, SD 3, TX 5, VT 6, WA 2, WV 1, WY 1); 4 CLOSED_R1 (Iowa statewide entry, Mid-Willamette, Bergen duplicate, [Org 1053] Falls duplicate); 39 HELD with reasons (no published address, hijacked/parked/expired domains, different org, portal or parent-facing only, site down). Non-CO REMAINING = 0. Colorado 35 left for Chris.


## 2026-10-12 nightly — no change
Run 2026-10-12: 0 new drafts, 0 follow-ups due. Retries re-touched: Kern CA, ELRC 19 PA, COAD OH -> CLOSED_R1 (dedup_check); 4C of the UP MI stays HELD, retry 2026-10-26. No new addresses evidenced.

- 2026-10-14 run: no new addresses verified (0 drafts). [Org 0464] info@ bounced 10-13 (550 5.4.1). Replies logged in contacted.md.

- 2026-10-15 nightly: 0 drafts; sent-sweep reconcile 44 E1 (10-14) → /1; replies ★ ECRC Canton, YWCA NW Illinois, Montgomery Co MD CCSS; bounce person0459@org0767.example (Great Start to Quality Kent, 5.1.1).

- 2026-10-22 run: 0 drafts; no change (supply exhausted outside CO). See review-2026-10-22.md.
