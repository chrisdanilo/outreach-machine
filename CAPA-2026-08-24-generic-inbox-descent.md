---
business: Human Skills Training
type: capa
title: CAPA 2026-08-24 — why half the Texas batch reached only a generic inbox
status: DIAGNOSIS ONLY — no corrective action applied
owner: Chris Danilo
opened: 2026-08-24
trigger: "Chris, after sending: 'many of them only had a single generic inbox in the to field. And there were no other addresses… I want you to diagnose only'"
related: ["[[method]]", "[[review-2026-08-21]]", "[[STATE]]", "[[discovery-pipeline]]", "[[CAPA-2026-08-18-unqueried-tier1-roster]]"]
---

# Why half the Texas batch reached only a generic inbox

🔴 **DIAGNOSIS ONLY. Nothing here is applied.** Chris asked for a diagnosis and tabled the fixes.
**No rule was changed, no draft was touched, no method file was edited.**

---

## 1 · What actually went out — the facts first

**All 10 Email 1 drafts were sent 2026-08-24 22:13–22:16Z, exactly as drafted. Zero recipient
changes.** *(That is itself a finding: Chris changed nothing, so every choice below is the machine's.)*

| # | Org | To | Cc | Redundancy | Generic-only? |
|---|---|---|---|---|---|
| 1 | **WS North Central Texas** | `person0197@org0260.example` | — | 🔴 **1 of 3** | ✅ **yes** |
| 2 | **WS Permian Basin** | `person0988@org0795.example` | — | 🔴 **1 of 3** | ✅ **yes** |
| 3 | **WS Capital Area** | `person0106@org0781.example` | `ccsregistration@` | 2 of 3 | ✅ **yes** |
| 4 | **WS Alamo** | `person1238@org0809.example` | `person0216@org0809.example` | 2 of 3 | ✅ **yes** |
| 5 | **WS East Texas** | `person1009@org0284.example` | `customer@` | 2 of 3 | ✅ yes *(but greeted `Kristti,`)* |
| 6 | **WS Cameron** | `person0812@org0780.example` | — | 🔴 **1 of 3** | no — personal |
| 7 | **[Org 0609]** | `person0267@org0303.example` | — | 🔴 **1 of 3** | no — personal |
| 8 | WS Heart of Texas | `Tamera.Carter@` | `julie.talbert@` | 2 of 3 | no |
| 9 | WS Deep East Texas | `person1105@org0257.example` | `mmorgan@` · `smilligan@` | 3 of 3 ✅ | no |
| 10 | WS Coastal Bend | `valerie.ann.delacruz@` | `tony.armadillo@` · `christina.gonzalez@` | 3 of 3 ✅ | no |

**5 of 10 reached only role inboxes. 4 of 10 went to a single address with no second recipient.**
**Only 2 of 10 hit the full 1-To/2-Cc cap.**

---

## 2 · The causes — there are FOUR, and they are not the same failure

**This matters because a single fix will not close it.** Treating "generic inbox" as one problem is
what would produce a wrong correction.

### 🔴 CAUSE A — The run skipped ranks 4 and 5 and jumped to ranks 6–7. **This is a rule violation.**

**R4 is explicit:** *"sort every person the org publishes into the ranks below, take the top 3,
highest rank takes the To."* Rank 4 = COO/Ops · **Rank 5 = assistants, receptionists, routing
roles** · Rank 6 = department inbox · Rank 7 = generic inbox.
[[method]] also states: 🔴 *"Never skip a tier to avoid work."*

**[Org 1290], from its own card:**

> *"Known but not contacted: [Person 0004] (CEO — rank OFF by default), **[Person 0611] (COO — rank 4)**,
> **[Person 0253] `person0634@org0809.example` (Board of Directors Coordinator — rank 5, routing role)**."*

**The card names a rank-4 person and a rank-5 person with a published address — and puts neither on
the thread**, descending instead to two rank-6/7 inboxes. **Under R4 the correct recipient set was
`jsantos@` (rank 5) plus the two department inboxes**, or `jsantos@` in the To with `trs_mentors@`
Cc'd. [Person 0253] exists precisely to route incoming mail; Chris ruled on exactly this:
*"their jobs are to route incoming mail and messages, so it's appropriate to address them instead of
the CEO."*

⚠️ **The same question applies to Capital Area**, whose card says the leadership team is *"six
strictly-executive titles"* — at least some of which are rank 4, and none of which were used.

🔴 **This is the one unambiguous defect in the batch.** The others below are policy costs or genuine
dead ends. **This one is the rule not firing.**

### 🟡 CAUSE B — The rank list speaks Florida ELC, not Texas workforce board

| Org | `named on page` | `Tier-1/2 identified` |
|---|---|---|
| WS Capital Area | **55** | **0** |
| WS Alamo | **29** | **0** |

**84 humans read off the organisations' own pages. Zero tiered.**

**Is zero defensible?** Partly. The Capital Area card documents real looking:
*"55 people named and not one of them touches child care… every reference to quality/coaching is
unnamed (`a professional staff person`, `An Inclusion Specialist`)."* That is a finding, not laziness.

**But R4's rank-1 signals are early-childhood vocabulary** — *Professional Development · Training ·
Coaching · Staff Development · Quality Improvement · CCR&R*. **Texas workforce boards use workforce
vocabulary**: *Texas Rising Star mentor · TRS · Child Care Services · Child Development Specialist ·
Quality Assurance*. **`TRS` and `Texas Rising Star` appear nowhere in R4's signal list**, and TRS
mentoring *is* the PD function at these organisations — Alamo's own page says so:
*"quality mentoring, training, and education… priority for professional development opportunities."*

> 🔴 **R8 approved Texas workforce boards as a new market and a new cluster on 2026-08-20, explicitly
> to learn whether it behaves differently. Nobody re-tuned the rank list for that market's language.**
> **This is the finding R8 was created to surface — and it arrived as a reachability finding rather
> than a conversion one.**

### 🟡 CAUSE C — Gate 1 turned nine correct vendor answers into unusable ones

**The reverse lookup ran, and it worked.** Three organisations each got three real people back:

| Org | Vendor returned | Outcome |
|---|---|---|
| WSNCT | Child Development Specialist · Early Childhood Education Specialist · Child Care Manager | **3 HOLD-G2** |
| WS Capital Area | 3 people | **3 HOLD-G2** |
| WS Alamo | Assistant Director of Child Care Services · Child Care Quality Manager · +1 | **3 HOLD-G2** |

**Nine people, exactly the right titles, all unusable** — because `HOLD-G2` means vendor-verified but
**not confirmable on the organisation's own site**, and these organisations publish no staff.
Gate 1 requires the org's own page. **So the machine knew who to talk to and was forbidden to.**

🔴 **This is not a bug. It is Gate 1 working as designed, and this is the first time its price is
visible in a batch.** The rule exists because `person0322@org0314.example` came back `Verified` from the
vendor and belonged to someone who had left. **The question Chris now has data for: is
own-site confirmation the right gate for organisations that publish no staff at all?**
*(Not answered here. Tabled.)*

### 🟡 CAUSE D — Two orgs were genuine dead ends, and the record says so honestly

- **WS Permian Basin** — bot wall. `/contact-us/`, `/site-map/`, the TRS page and For-Providers all
  return *"Javascript is required."* **And the vendor returned nothing** — a genuine blank, not a
  Gate-1 block. `0+ named`. **There was nothing to find.** Untried route carried forward:
  `https://org0795.example/wp-json/wp/v2/pages?search=staff` (the site is WordPress).
- **WSNCT** — *"This site names ZERO humans anywhere"* — an exact count, not a blocked directory.
  Board members sit behind a login portal.

**For these two, a single generic inbox was the correct outcome.** Redundancy `1 of 3` was printed on
both cards. **The machine did not hide it.**

### ➕ The two single-address orgs that are NOT generic

- **WS Cameron** — `1 Tier-1/2 identified · 1 published`. One real, correctly-titled person
  (*Child Care Program Supervisor*). `/staff/` was a **failed read** (empty body, two attempts).
  ⚠️ Also: the board **subcontracts** delivery to [Org 1118], so its own bench is genuinely thin.
- **[Org 0609]** — **this one Chris already ruled on and it is D4 from 08-21.**
  ECS publishes zero addresses on its own domain. Three `@org0303.example` addresses exist — **on ELC of
  North Florida's site**, a client's site, which Gate 1 excludes. **The machine flagged them and asked.
  The question went unanswered and the send went out at 1 of 3.**

---

## 3 · 🔴 THE STRUCTURAL FINDING — the scorecard said CLEAN through all of this

**[[STATE]], 2026-08-21:**

> `Roster sweep: 10 orgs carded · 10 passing · 0 invalid · 0 HELD at the gate · M = 0 · B = 4`

**Every number is true. The block is clean. And half the batch reached a role inbox.**

**Why `M = 0` could not see it.** `M` counts *"Tier-1/2 people who were identified but never
submitted to the vendor."* At Capital Area and Alamo, **zero were identified**, so zero could go
unsubmitted. **The control measures whether identified people were queried. It is blind to
identification returning zero.**

> 🔴 **This is the SAME structural flaw [[method]] already documented one step downstream.**
> The reverse lookup exists because *"a site that publishes NO names produces a sweep with zero
> workload… and a card that passes on its face while nobody was ever looked for. **A gate whose input
> can be empty is not a gate.**"*
> **The identical hole exists one step further upstream, at TIERING — and it is not covered**, because
> the reverse lookup fires on `Tier-1/2 identified = 0` **but its results then die at Gate 1** (Cause C).

**And the thinness WAS disclosed — on the cards, as `Redundancy: 1 of 3` and `2 of 3`.**
🔴 **It simply is not in the pass condition.** [[method]] Phase 7: *"Pass condition: `invalid = 0`
AND `M = 0` AND `HELD = 0`."* **Redundancy appears nowhere in it.** A batch can score a perfect
roster-sweep block while eight of thirty possible recipient slots are empty.

---

## 4 · Candidate controls — NOT APPLIED, listed for Chris

**Ordered by ratio of value to risk. Each is one line to accept or reject.**

| # | Candidate | Closes | Cost |
|---|---|---|---|
| **1** | 🎯 **Put redundancy in the mandated block:** `Recipients: N of 30 slots filled · N orgs at 1 of 3 · N at 2 of 3`. **Scored, like `M`** | The blindness in §3. Makes a thin batch impossible to report as clean | One report line. **No judgement required — it is arithmetic** |
| **2** | 🎯 **A rank-list check before descending below rank 5.** If `Tier-1/2 identified = 0` **but the page named ≥1 human**, the card must name the highest-ranked person found and state why they were not used | Cause A — the Alamo violation. **This is the actual rule break** | One line per card |
| **3** | **Add workforce-board vocabulary to R4 rank 1**: *Texas Rising Star · TRS mentor · Child Care Services · Child Development Specialist · Quality Assurance* | Cause B. **Cluster-specific, so it needs Chris's call on scope** | One edit to R4's signal column |
| **4** | **Decide the Gate-1 question for staff-less orgs**: does a vendor-verified person at an org that publishes NO staff stay `HOLD-G2` forever, or is there a second acceptable confirmation route? | Cause C — nine real people currently unreachable | 🔴 **A real policy decision. Not a tweak** |
| **5** | **Answer D4 (ECS4Kids)** — the three `@org0303.example` addresses on [Org 0554]'s site | One org at 1 of 3, already sent | One word |

⚠️ **Candidate 4 is the one with teeth and the one to be most careful about.** Gate 1 exists because a
vendor's `Verified` belonged to someone who had left, and that produced a bounce.
**Loosening it to solve a reachability problem would trade a known failure mode for a solved one.**

---

## 5 · What this says about the Texas cluster, stated carefully

**Texas workforce boards publish materially fewer named early-childhood staff than Florida ELCs.**
5 of 10 reachable only by role inbox, versus roughly 1 in 10 across the Florida cohorts.

🔴 **`n = 10`. This is an observation about ten organisations, not an established cluster property.**
It is exactly what `cluster: TX-workforce-boards` was created to measure, and it should be re-checked
against the remaining ~16 Texas boards before it is treated as settled.

⚠️ **And the reachability finding does not predict the conversion finding.** A TRS mentor inbox may
convert *better* than a named ELC director — Chris's own 2026-08-18 ruling was that in this sector
*"some of these generic email inboxes are actually monitored more closely than I initially thought."*
**The right measure is the reply rate on this cohort, due from 2026-08-31.** Do not conclude before
then.
