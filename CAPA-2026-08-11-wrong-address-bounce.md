---
business: Human Skills Training
type: CAPA
title: CAPA — cold email sent to a wrong address that bounced; correct address was on the org's own site
status: OPEN — corrective actions applied, one decision pending
created: 2026-08-11
severity: CRITICAL
classification: class of bugs
protocol: capa-protocol.md (Toyota / TPS)
related: ["[[method]]", "[[ready-queue]]", "[[sequence-tracker]]", "[[review-dossier-2026-08-11]]", "[[CAPA-2026-08-11-unapproved-copy]]"]
---

# CAPA — wrong address, hard bounce

| | |
|---|---|
| **Problem** | Chris's first live send went to `person0174@org0174.example` and hard-bounced. The Director's real address, `person0301@org0389.example`, was published on the agency's own "Our Team" page — one click from their homepage, linked in the main nav. |
| **Root cause** | Two independent defects both pointed away from the right answer: addresses could enter the queue from third-party directories without ever being checked against the employer's own site, **and** the `.gov` exclusion gate would have discarded all nine correct addresses even if someone had looked. |
| **Corrective** | Five County row rebuilt from the staff page — [Person 0116] `csigler@`, plus [Person 0591], **Professional Development Specialist**. Bad address suppressed. `person0471@org0238.example` (same 2024 brochure) pulled from the queue pending verification. |
| **Preventive** | An address may now only enter the queue if it was **read on the employing organization's own site**. Directories may be used to find an *org*, never to source an *address*. HIGH confidence redefined to mean exactly that. `.gov` gate replaced with a function test. |
| **Verify** | Next batch: every queued row cites an org-own-site URL for its address and a `verified_on` date. Any row citing a directory or brochure as its address source = FAIL. |

## Decision pending

| Decide | Ask | Time |
|---|---|---|
| Replace the `.gov` exclusion with a portal test | "Yes, exclude portals not domains" | 1 min |

---

## Step 1 — Andon cord

**Symptom.** 2026-08-11 18:31 UTC, Chris sent Email 1 to `person0174@org0174.example` (Care About
Childcare @ [Org 0655]). Google returned a hard bounce at 18:31:40 — *"Address not found. Your
message wasn't delivered to person0174@org0174.example because the address couldn't be found, or is
unable to receive mail."*

**Why this is critical rather than annoying.** A hard bounce on a cold send from
`<SENDER_EMAIL>` is a deliverability event on the domain that also carries the newsletter and
both welcome sequences. It is not a wasted email; it is a small tax on every future email.

**Recurrence.** N=1 bounced, but **N=2 exposed** — `person0471@org0238.example` came from the identical
2024 brochure and carries identical risk. It was queued and drafted.

**Containment applied.** Bad address recorded in the bounce log and headed for suppression. The
`person0471@org0238.example` draft is flagged do-not-send pending verification.

## Step 1.5 — IS / IS-NOT

- **IS:** The *address* for the Five County contact, and by extension every address sourced from a directory or brochure rather than the employing org's own site.
- **IS-NOT:** Not the copy — that was Chris's own v2 text and it sent fine. Not the person — [Person 0116] is real, correctly identified, and the right target. Not the org — [Org 0655] is a genuine CCR&R. **Only the address was wrong.**
- **When did it start?** 2026-08-11 seed, when the row was gated from `HST-New-CCRR-Contacts-2026-07-22.xlsx` and scored HIGH.
- **What changed right before?** Nothing. This defect was present from the moment the row was created; the first real send simply exposed it.

## Step 2 — Genchi Genbutsu: what I read

| Source | What it revealed |
|---|---|
| https://org0174.example/our-team/ | **The whole answer.** Nine staff, every address `@org0389.example`. **[Person 0116], Director — `person0301@org0389.example`.** And **[Person 0591], Professional Development Specialist — `person1137@org0389.example`.** |
| https://org0174.example/ | "Our Team" is in the primary nav on every page. Not buried, not a PDF, not gated |
| Gmail message `<thread-id>` + bounce `<thread-id>` | The send and the hard bounce, 17 seconds apart |
| `HST-New-CCRR-Contacts-2026-07-22.xlsx` | Row records `person0174@org0174.example`, Email Confidence **HIGH**, Source URL = the 2024 brochure |
| https://utahvalleydpc.org/…/Care-About-Childcare-Brochure-English.pdf | 2024, hosted on a **third organization's** site. This is where the address came from |
| [[review-dossier-2026-08-11]] | Flagged this exact draft: *"the most likely to bounce or reach the wrong person in the whole batch… I'd hold both."* **The warning was correct and did not stop the send** |
| ZoomInfo — [Person 0116] | Independently corroborates `c***@org0389.example`, Director |

**Three findings that matter beyond this one address:**

1. **`person0174@org0174.example` appears nowhere on the organization's own website.** Not on Our Team, not on Contact Us. It exists only in a two-year-old third-party PDF.
2. **The org's website domain is not its email domain.** The site is `org0174.example`; every single staff address is `@org0389.example`. Inferring an address from a website domain is invalid here — and we did exactly that by trusting a source that had.
3. **The PD lead was on that page all along.** [Person 0591]'s title is literally *Professional Development Specialist*. **Chris found her by hand and added her to the Cc.** The machine had never seen her.

## Step 3a — Candidate root causes

| # | Candidate | Likelihood | Verify by | Result |
|---|---|---|---|---|
| 1 | Address sourced from a directory, never checked against the org's own site | **H** | xlsx Source URL vs Our Team page | ✅ **Confirmed** |
| 2 | "HIGH confidence" measured format/existence, not provenance quality | **H** | Compare a 2026 state directory row and a 2024 brochure row — both HIGH | ✅ **Confirmed** |
| 3 | The `.gov` exclusion would have destroyed the correct answer | **H** | Method Phase 6 gate vs the staff page | ✅ **Confirmed — the compounding defect** |
| 4 | The address was correct once and went stale | M | Site history | ⚠️ **Plausible and irrelevant** — a 2024 source unchecked in 2026 is the defect either way |
| 5 | Copy or send mechanics at fault | L | The send itself | ❌ **Ruled out** — copy sent fine; the Cc at `@org0389.example` delivered |

## Step 3b — 5 Whys

| Level | Question | Answer |
|---|---|---|
| Why 1 | Why did it bounce? | `person0174@org0174.example` is not a live mailbox. The Director is `person0301@org0389.example` |
| Why 2 | Why did we hold the wrong address? | It came from a 2024 brochure PDF hosted on a third organization's website |
| Why 3 | Why was a third-party brochure enough? | Nothing required an address to be verified against the employing organization's own site before queueing |
| Why 4 | Why did that gap survive the gate? | Because "Email Confidence: HIGH" was scoring whether an address *looked valid and was published somewhere* — not *where it came from or how old that was*. A 2026 state directory and a 2024 third-party brochure both scored HIGH, so nothing could distinguish them |
| Why 5 | Why would even a careful pass have failed? | **Because the `.gov` exclusion gate would have thrown away all nine correct addresses.** Discovery was configured to treat government domains as referral portals. [Org 0655] is a council of governments that *operates* the CCR&R — real agency, real staff, `.gov` mail. So one defect let a bad address in, and a second would have rejected every good one. **The correct answer was unreachable by design** |

**Classification: CLASS OF BUGS.** This hits every org where the website domain differs from the
email domain, every government-operated agency, and every row sourced from a directory — which is
most of the queue.

## Step 4 — Corrective action (Jidoka)

1. ✅ **Five County rebuilt from the staff page** — [Person 0116] `person0301@org0389.example` (To), [Person 0591], Professional Development Specialist, `person1137@org0389.example` (Cc). Seven more staff recorded.
2. ✅ **`person0174@org0174.example` → bounce log**, headed for suppression.
3. 🔴 **`person0471@org0238.example` do-not-send** until verified against [Org 0357]'s own site. Same 2024 brochure, same failure mode, currently sitting in Drafts.
4. ⏸️ **Re-verify the remaining 6 unverified orgs** in [[review-dossier-2026-08-11]] before any of those drafts go out.

## Step 5 — Preventive action (Poka-Yoke) — ELIMINATE tier

Applied to [[method]] Phase 6, which the scheduled task reads at runtime.

1. **Source-of-truth rule.** An address may enter `ready-queue.md` **only** if it was read on the employing organization's own website. Directories, brochures, state portals and aggregators may be used to **find an organization** — never to **source an address**. If the org's site publishes no addresses, the row is `MED` and flagged, never HIGH.
2. **HIGH redefined.** HIGH = *read on the org's own site within the last 90 days*. Nothing else qualifies. This alone would have stopped the send.
3. **`.gov` gate replaced with a function test.** Exclude *referral portals* — lookup tools with no named staff. Keep *operating agencies*, including government-run ones, and verify them like any other org. A `.gov` address is no longer disqualifying.
4. **Domain-mismatch tripwire.** If an address's domain ≠ the org's website domain, stop and confirm on the staff page. Here the site was `org0174.example` and every real address was `@org0389.example`.
5. **Alias-shape tripwire.** A first-name-only local part (`carrie@`, `heather@`) is an alias pattern, not a personal mailbox. Flag for verification.
6. **The dossier blocks, it does not advise.** It named this draft as the batch's highest bounce risk and recommended holding it, and the send happened anyway. Any org carrying a 🔴 in the dossier is now a hard stop.

## Step 5.5 — Bias check

**Anchoring:** the tempting stop was "stale address, bad luck." Reading the staff page killed that —
the correct address is published, current, and one click from the homepage. **Confirmation:** I
looked specifically for evidence the address *had* once been valid (candidate #4); it may well have
been, and it doesn't change the defect, so I kept it listed rather than dropped. **Premature
closure:** I nearly stopped at Why 4, which felt clean. Why 5 is the one that matters — without it
the fix would have been "verify against the org's site," which on this org would have surfaced nine
`.gov` addresses that the gate then discards. **Recurrence:** treated as N=2 exposed rather than
N=1 bounced, because a fix scoped to Five County leaves `person0471@org0238.example` live in Drafts.

## Step 6 — Standard work

```
### Address provenance rule
- Trigger: any contact address entering any outreach list
- Action: source the address from the employing org's own website. Directories, brochures,
  portals and aggregators find the ORG, never the ADDRESS. Confidence HIGH requires an
  org-own-site URL plus a verification date inside 90 days.
- Rationale: a 2024 third-party brochure produced a hard bounce on the first live send, while
  the correct address — and the PD lead — sat on the agency's own Our Team page.
- First applied: 2026-08-11, CAPA — wrong address, hard bounce
```

## Step 7 — Verification

**Verify at the next batch.**

- **PASS:** every queued row cites an org-own-site URL for its address, with `verified_on` inside 90 days. Zero bounces.
- **FAIL:** any row citing a directory, brochure or portal as its *address* source — even if it doesn't bounce. The defect is the provenance, not the outcome.
- **A batch with no sends is not a pass.** The check needs live sends.
- **On FAIL, escalate:** verification stops being a discovery step and becomes a pre-send check on every individual address.

---

## The uncomfortable summary

The organization's own website published the Director's correct email address and the Professional
Development Specialist's name, title and address — on a page called "Our Team," linked from the main
nav of a site we already had in the queue.

**We used a two-year-old PDF on somebody else's website instead, and rated it HIGH.**

Chris found [Person 0591] by hand, in the ninety seconds before he hit send, on the page the
machine should have opened at discovery. That is the whole gap in one sentence.
