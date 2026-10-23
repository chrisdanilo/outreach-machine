---
business: Human Skills Training
type: machine-reference
title: Recipient Selection Profile — who belongs on a CCR&R thread
status: active · learning
created: 2026-08-11
related: ["[[method]]", "[[sequence-tracker]]", "[[verification-log]]"]
---

# Recipient Selection Profile

**What the learning loop is actually for.** Chris, 2026-08-11:

> *"The language we don't really want to change unless I explicitly tell you to. But I would like you
> to start learning what kind of other people I'm adding… anybody with a name with like professional
> development or training or coaching in their title, or anyone who seems like they may have a role
> or decision or an influence in how their team gets trained or how their training gets distributed
> among their community or contact list."*

**Two rules, opposite directions:**

| Domain | Rule |
|---|---|
| **Copy / language** | 🔒 **Frozen.** Changes only when Chris explicitly says so. Observe, never infer, never propose from a single edit |
| **Recipients** | 📈 **Actively learned.** Every person Chris adds is a signal about who the machine should have found |

## 🔴 Never assume a pronoun

**Chris, 2026-08-11:** *"Jesse is actually a woman. We should never ever assume a pronoun for
anyone."*

I referred to **[Person 0278]** as "he" on the basis of the name alone. **Refer to every contact by
name and title. Nothing else.** A name is not evidence of gender; neither is a photo or a title.
The only acceptable source is the person stating it themselves, recorded as a quote.

This file is about people, so it's the one most likely to breed the habit. It doesn't get to.

## The selection rule

Include anyone who meets **any** of these:

### Tier 1 — Explicit title match (always include)
`professional development` · `training` · `coaching` · `learning` · `PD`

### Tier 2 — Owns practice quality (include)
Titles governing how practice changes: `quality`, `CQI`, `continuous quality improvement`, `VQB5`,
`program excellence`, `specialist` (early childhood / infant-toddler / behavior), `accreditation`,
`CDA`, `career launch`, `workforce`.
*These people run the coaching and TA that IS the training, whatever the title says.*

### Tier 3 — Distribution and influence (include)
Chris's own words: *"how their training gets distributed among their community or contact list."*
Titles that carry reach rather than delivery: `program communications`, `advocacy`, `community
engagement`, `coalition`, `membership`, `network`, `systems development`, `program innovation`.
*These are the people who forward it to 200 providers.*

### Always the decision-maker (To)
ED / CEO / President / Senior VP of Impact / Program Director. Tiers 1–3 go to **Cc**.

### Exclude
Finance, HR, accounting, IT, data analyst, donor services, office manager, marketing-for-fundraising.
~~Generic inboxes never on the visible thread.~~ 🔴 **REVERSED 2026-08-18 by Chris** — see the preferred ranking in [[method]] and `generic_inbox_usable` in [[STATE]]. A generic inbox is tier 3 (named greeting) or tier 4 (no name), **never an exclusion.**

---

## ✅ RESOLVED — the live-page exception (Chris, 2026-08-11)

**Live web page = sendable on Gate 1 alone. A document = 6 months old at most, and still needs
Gate 2.** Full rule in [[method]]. [Person 0340] is usable again on that basis.

## The finding that produced it

**United Way publishes every staff email in plain text on a current staff page.** So does Five
County. So do many CCR&Rs.

I dropped **[Person 0340]** from the Blue Ridge draft because Apollo returned no match — but her
address is published, in plain text, on United Way's own live staff page. That is the strongest
possible Gate 1 evidence, and I discarded it for failing Gate 2.

**That's an over-correction.** The bounce came from a **2024 brochure on a third party's website** —
not from a current org staff page. Requiring Apollo confirmation of an address the employer
currently publishes adds no safety and costs real contacts.

✅ **RATIFIED by Chris 2026-08-11 and implemented in [[method]]:**

| Gate 1 source | Requirement |
|---|---|
| Address **published in plain text on the org's own current staff page** | ✅ Sendable on Gate 1 alone |
| Address from a directory, brochure, aggregator, portal, or inference | 🔴 Gate 2 required, no exceptions |
| Address not published anywhere | Gate 2 is the only route |

That keeps the guard exactly where the failure was and stops it blocking good contacts.

## How this gets applied

1. **Discovery** reads the staff page and captures **everyone** in Tiers 1–3, not just two names.
2. **Phase 2 roster gate** fails an org whose card has no Tier 1 or 2 person — or an explicit `NO PD ROLE PUBLISHED`.
3. **The dossier** lists every tier-matching person and states plainly who is not on the email and why.
4. **When Chris adds someone,** verify their title on the org's own site, log them here, and check whether their title reveals a pattern not yet covered.

## ✅ Thread size — DECIDED 2026-08-11

> **Chris:** *"Figure out who's most likely to be the decision maker and write them in the 'to'
> field. And then we do 2-3 other people max — any more than that and it feels like a blast.
> Let's agree that it's 1 person in the 'to' field and up to two people in the CC field."*

**1 in To. Maximum 2 in Cc. Three people, never four.**

### 🔴 PRECONDITION — THE ROSTER SWEEP RUNS BEFORE ANY OF THIS. Added 2026-08-18

**Nothing below may be applied until the roster sweep in [[method]] Phase 2 has passed for that
organisation.** Every Tier-1/2 person named on the org's own pages whose address is unpublished goes
to the vendor first, in **one** `people_bulk_match` (≤10 per org). **Then** you select from what came
back.

> **RESOLVE FIRST, NARROW SECOND.** This file owns *who goes on the thread*. It has never owned
> *who gets looked up*, and treating the two as one question is what produced the 2026-08-18 defect:
> at [Org 0539] the run had one resolved address, filled the To with it, and stopped — leaving
> **six untested Tier-1 training-titled people on the same page** and 0 of 25 lookup credits spent.
> **Choosing three people from a pool of one is not a selection.**
> See [[CAPA-2026-08-18-unqueried-tier1-roster]].

**Selection when more than 3 qualify — take the highest tier first, FROM THE RESOLVED SET:**

1. **To** — the single likeliest decision-maker. One name, no hedging.
2. **Cc #1** — the strongest **Tier 1** (explicit PD / training / coaching title, **or role evidence
   per RULE C**). This is the wedge buyer; if one exists, they are always Cc #1.
3. **Cc #2** — next best Tier 1, else the strongest Tier 2, else Tier 3.

**The cap limits the email, not the research — and it does not limit the LOOKUPS either.** Everyone
else who qualifies is recorded in the dossier as *known, not contacted* — available for a later
touch, a referral, or a phone approach. 🔴 **Each of them takes one of the three states** (`📄
PUBLISHED` / `🔍 VENDOR QUERIED — no match` / `⛔ NOT QUERIED — reason: ___`). The phrase
*"identified, address unknown"* is **banned** — it hid the difference between a dead end and an
unasked question. **And the card carries the roster resolution line, or it is invalid.**

### Worked example — United Way of Greater Charlottesville

10 tier-matching people. The thread is:

| Field | Person | Title | Why |
|---|---|---|---|
| **To** | [Person 0479] | Senior Vice President of Impact | Most senior with budget authority over school readiness |
| **Cc** | **[Person 0278]** | Early Childhood Quality and **Coaching** Manager | Tier 1 — and Chris picked [Person 0278] by hand |
| **Cc** | [Person 0375] | Early Learning **Career Launch** Coordinator | Tier 1–2, workforce development |

Recorded but not contacted: [Person 0340], [Person 0094], [Person 0091], [Person 0063], Blair
Davis, [Person 0136], and the three Infant & Toddler Specialists.

---

# 🟢 RULINGS FROM CHRIS, 2026-08-17 — these are DIRECTIVES, not observations

Two of the three items below are **stated rules from Chris and are now in force.** They are recorded
here rather than in [[method]] because [[method]] Phase 5 assigns recipient selection to this file:
*"Recipients — 📈 Learn actively."*

## RULE A — 🔴 At any org with a C-suite, prefer the COO over the CEO

> **Chris, 2026-08-17:** *"For larger or medium sized orgs with a C-suite, if there's a COO and a CEO,
> I'd rather include the COO instead of the CEO. This is more respectful and would likely be more
> successful in following their chain of command and respecting the attention of their C-suite roles.
> I replaced one or two CEO addressees with COOs in this batch."*

**The rule.** Where an organisation has both a Chief Executive Officer and a Chief Operating Officer,
**the COO is the To and the CEO stays off the thread.** Two reasons, both his: it respects the chain of
command, and a COO is likelier to read and act on it than a CEO whose attention is the scarcest in
the building.

**Applies to medium AND large orgs — the trigger is the existence of a C-suite, not a headcount.**
This is broader than the existing org-scale gauge, which only moved the CEO off the thread at
multi-program parent agencies. **It now also fires at single-program organisations that have grown a
C-suite** — which is most Florida coalitions.

**What he actually did tonight:**

| Org | Machine's To | Chris's To | Read |
|---|---|---|---|
| [Org 0565] | [Person 0151], **CEO** | **[Person 0048], Chief Operations Officer** `person0104@org0309.example` | Textbook application: ~18 staff, so a *medium* org with a C-suite. The CEO's address was published and he passed it over |
| ELC Alachua | [Person 0652], **CEO** | **[Person 0617], Chief Programs Officer** `person1236@org0314.example` | **No COO exists at ELC Alachua.** He went to the next senior *programs* executive instead — so the rule generalises: **no COO → the most senior program officer (CPO / Chief Programs Officer), not the CEO** |
| [Org 0563] | [Person 0626], **CEO** | unchanged | 26 staff; **no COO** and no CPO — the only C-suite roles are CEO and CFO. With no operating or program executive to route to, the CEO stands |
| [Org 0803] | [Person 0467], Director | unchanged | Already below the C-suite; CEO and COO both already off-thread |

**Revised To-selection order, for Chris to confirm:**

1. **Chief Operating Officer**, if one exists
2. else **Chief Program(s) Officer** or equivalent senior program executive
3. else **Executive Director / CEO** — only where no operating or program executive exists
4. …with the CCR&R override in Rule B taking precedence over all of the above

🔴 **Where this rule would have changed tonight's batch and did not:** at **ELC of Flagler and
Volusia** the machine used [Person 0018], Chief Program Officer, while **[Person 0230] is the Chief
Operating Officer** (`person0468@org0323.example`, published on the same page). Under Rule A the To should
have been DiRenzo. Chris did not change it, but the rule as stated points at her.

## RULE B — 🔴 A title containing "CCR&R" marks a PREFERRED contact

> **Chris, 2026-08-17:** *"I replaced [Person 0592] with [Person 0087] since her title includes 'CCR&R'
> responsibilities. Since we are reaching out across states and counties, the rules and roles can be
> different, so someone with CCR&R in their title may be the right person to talk to, or may have
> someone on their team who is the right person to talk to. They are a preferred contact for this kind
> of outreach."*

**The rule.** **"CCR&R" (or "[Org 0272] and Referral") anywhere in a published title makes
that person a preferred recipient — strong enough to take the To ahead of the Executive Director.**

**The reasoning is the important part, because it generalises.** Titles are not standardised across
states and counties, so a keyword list will always be behind. **A CCR&R title is a structural
signal rather than a semantic one:** whatever else varies, the CCR&R function is the part of the
organisation that faces providers, so its owner either buys training or knows exactly who does. **A
referral onward is a successful outcome of Email 1** — the copy literally asks to be pointed at the
right person.

**What he did:** at **[Org 0557]** he removed **[Person 0592], Ph.D., Executive
Director** — an address the machine had spent a lookup to resolve — and promoted **[Person 0087],
Supervisor of Family Services and CCR&R** (`person0110@org0336.example`), whom the card had listed as excluded
by the Cc cap. Greeting rewritten to *"Brenda, Melissa, and Dawn,"*.

**Third occurrence of the same underlying issue, and it strengthens the outstanding restructure
question.** Rule B is one more instance of *the tier list reads TITLES, Chris reads ROLES* — following
[Person 0001] (08-14), [Person 0005] and [Person 0549] (08-13), and McKenna Terrill tonight.
🔴 **Recommendation: fold "CCR&R" into Tier 1 immediately as a directive, and treat the wider tier
restructure as still open.** Note it would also have promoted **[Person 0218], [Org 0272]
and Referral Coordinator** at Big Bend — and Chris independently routed that thread through Big Bend's
CCR&R inbox, which is the same instinct.

## ~~OBSERVATION C~~ — ✅ SUPERSEDED 2026-08-18, see the ruling further down this file

> 🔴 **Do not act on the "NOT applied" wording below — Chris ruled on it on 2026-08-18 and generic
> inboxes are now usable.** Kept for the reasoning trail only.

### Original text, as raised: he used department inboxes as a route to named, unreachable people

At **[Org 0564]** the machine's thread was To [Person 0058] (CPO) · Cc [Person 0328]. **He
replaced the To with `ccr@org0315.example` and added `resources@org0315.example` to Cc**, then addressed
the body *"Gabrielle, Kathy, and Melanie,"* — i.e. **[Person 0218] (CCR&R Coordinator) and Melanie
[Person 0650] (Early Care and Education Manager), two people whose personal addresses the
organisation does not publish and whom the vendor could not resolve.**

**He used the org's own department inbox as the delivery route to a named human.** That is a genuinely
better answer than the machine's, which was to drop both people. It is also **the second time he has
put a generic inbox on a visible thread** (after `info@org0334.example` on 08-14) against a standing
rule that says never.

**Candidate rule, NOT applied — needs Chris:** where a named Tier-1 or CCR&R person is identified on
the org's own page and no personal address can be resolved, **the org's own matching department inbox
is an acceptable route, provided the body addresses the person by name.** This would need the
"generic inboxes never on a visible thread" rule amended rather than broken. **Two occurrences; the
threshold for language changes is three, and this is a recipient rule, so it is his call whenever he
wants to make it.**

⚠️ **One caution worth stating: this route bounced tonight.** `ccr@org0315.example` is a typo for the
published `ccrr@org0315.example` (two R's). `resources@org0315.example` delivered fine, so the message
did reach the organisation.

## OBSERVATION D — He preferred two PD practitioners over a senior generalist in Cc

At [Org 0003] the machine had Cc = [Person 0617] (Chief Programs Officer) + [Person 0368]
(Lead Transformative PD Coach). He promoted **Robinson to the To** and made Cc **Woulard +
DeWaynique Barton, Transformative Professional Development Coordinator** — the second Tier-1 PD
person, whose address the machine had resolved and then left off because of the Cc cap.

**Read: with a senior program executive in the To, he wants the Cc spent on the people who would
actually run the training, not on another executive.** Consistent with Rule B's logic. Recorded, not
applied.

## Copy — unchanged, verified by full-body diff

**A full-body diff of the ELCPH send (`<thread-id>`) against its draft shows the body is
byte-identical to v6** — every bold span intact, including `AI-powered world.` with the full stop
inside it and "Human Skills" unbolded in that sentence. **Only the greeting changed**, which is one of
the two fields permitted to vary. **No copy edit to report for the first time in four batches.** Both
attachments were in place.


---

## 📁 The learn-pass history is archived, not deleted

Every run's recipient observations from 2026-08-11 to 2026-08-18 live verbatim in
**[[archive/recipient-profile-archive-through-2026-08-18]]**. Moved 2026-08-18 to cut the nightly
run's setup cost. **The operative rules are all above** — the archive is for tracing why a rule exists.

---

# 🟢 RULINGS IMPLEMENTED 2026-08-18 — Chris: "get all of this implemented"

## RULE C — Tier on the ROLE, not the title keyword ✅ APPLIED

**The oldest open question in the machine, raised five times and now closed.** A person is Tier 1 if
the organisation's own page shows they own training — **whether or not their job title says so**.
Naming someone as the contact for a training programme, a training bonus, a coaching initiative or
provider development is role evidence and it counts.

**Founding cases, all previously excluded or mis-tiered:** [Person 0005] (CACFP Coordinator, 08-13)
· [Person 0549] (trainer in his biography, not his title, 08-13) · **[Person 0001] (ELCHC, 08-14 — named
as the contact for the training achievement bonus on a page that never states her title)** ·
McKenna Terrill and the [Org 0548] roster (08-17, where nobody's title contained a
training word).

🔴 **The evidence bar is unchanged: role evidence must be QUOTED from the org's own page** and
recorded on the card. A role inferred from a job posting, a LinkedIn headline or a vendor department
tag does not qualify. Full rule in [[method]].

## RULE D — Spend the lookup when a key person is named but unreachable ✅ RATIFIED

When a Tier-1 person or decision-maker is named on the org's own page and **no address is published**,
spend the vendor lookup instead of filing them unreachable. *"Not published" is a fact about the
website, not about the person.*

**Evidence: on 2026-08-17 this turned three address-less organisations into three drafts for ten
credits, and ELC Alachua then produced the machine's best reply** — the CEO named the PD owner,
added her to the thread, and committed to a discussion.

🔴 **AMENDED 2026-08-18 — THIS RULE NOW HAS AN OBJECT, AND IT IS A GATE.** As written above it is a
permission with no completeness test, and **on the day it was ratified it fired for two of nine
eligible people at [Org 0539]** — the other seven, five of them Assessment and Training
Specialists, were filed unreachable without being asked. **"Spend the lookup" is not satisfied by
spending one.**

**The obligation is now: every Tier-1/2 person named on the org's own pages whose address is
unpublished, submitted in ONE batched call, capped at 10 per org.** The card proves it with the
roster resolution line — `unpublished = submitted + deferred`, or the card is invalid.

**Cost, since this reads as expensive and is not: null matches are free.** 2026-08-18 — twelve
submitted, four charged. Sweeping seven orgs ≈ 23 credits, inside a nightly budget that has been
closing at zero. Full analysis: [[CAPA-2026-08-18-unqueried-tier1-roster]].

## RULE E — The vendor is usually stale, but NOT always. Check both directions ⚠️ NEW

**Standing rule remains: when the org publishes a title, the org's title wins.** That rule exists
because of four cases of vendor *title decay* (LaTrisha Sims, [Person 0197], [Person 0209],
[Person 0613] — where Apollo returned `CNA`/`nursing` for a CCRR Coordinator).

🎯 **But on 2026-08-18 it ran the other way for the first time.** [Org 0582]'s staff page lists
**[Person 0516]** under Program Quality as *"Quality Specialist."* Apollo has her as **Director of
Programs at [Org 0582] since 2006**, with a LinkedIn headline saying the same. **The vendor claimed the
MORE senior role.**

**What to do when the vendor claims seniority the page does not:**

1. **Keep the org's published title on the card** — the standing rule is unchanged.
2. **Flag the discrepancy beside it**, with both values.
3. **Treat the person as at least as senior as the higher claim for RECIPIENT PURPOSES.** A
   discrepancy in this direction makes them a stronger recipient, not a weaker one — there is no
   downside to addressing someone by the humbler of two titles.
4. **Never print the vendor's title in the email.** The copy has no title field; this affects who is
   chosen, never what is said.

**Applied at [Org 0582] 2026-08-18:** [Person 0516] took the To ahead of CEO [Person 0445], who moved to
Cc. Sent by Chris the same evening.

## OBSERVATION C — department inboxes ✅ NOW SUPERSEDED BY THE PREFERRED RANKING

Logged 2026-08-17 as *"he used department inboxes as a route to two named people"* and marked NOT
applied. **Chris ruled on 2026-08-18 and it is now tier 3 of the preferred ranking in [[method]]:**
a generic inbox carries the mail, and the greeting names the right person from the team page.
First deliberate use: [Org 0539], drafted 2026-08-18.

---

## 2026-08-19 learn-pass — ⏱️ WRITTEN LATE, 2026-08-20

🔴 **This entry is four days' worth of process debt in one line: the 08-19 run put its recipient
learning into [[sequence-tracker]] instead of here, which is what [[method]] Phase 5 forbids
(*"recipient patterns are folded into recipient-profile immediately"*). Backfilled per C5 of
[[CAPA-2026-08-20-unreconciled-run-manifest]].**

**Chris sent nothing on 08-19** — the drafts were still under review — so there are **no
Chris-added recipients to learn from this batch.** Everything below is machine-side observation.

## RULE F — TIER ON THE ROLE produced four Tier-1 people who have NO TITLE AT ALL ✅ WORKING

**First clean confirmation that RULE C is earning its place.** At ELC Broward the org publishes a
"Provider Support Contacts" block on the page selling **"On-Site Training & Technical Assistance"**:

> *"**Provider Support Contacts** / For assistance, please contact your assigned representative: /
> **[Person 0223]** / 📧 person0443@org0318.example"* — and three more the same way.

**None of the four has a published job title.** Under the pre-2026-08-18 title-keyword rule all four
would have been invisible. **Two of them are on the thread.** The rule found people the old rule
could not represent — which is exactly the [Person 0001] case that forced it.

## OBSERVATION E — a vendor TITLE conflict pointing the OPPOSITE way to [Org 0582] ⚠️ RAISED, NOT APPLIED

**Second title conflict in two runs, and the direction reversed.**

| Case | Org's own page | Vendor | Which was more senior |
|---|---|---|---|
| [Org 0582] (08-18) | "Quality Specialist" | Director of Programs since 2006 | **the vendor** |
| ELC Broward (08-19) | **"Chief Operating Officer"** | Information Technology Manager / CIO | **the org's page** |

**RULE E says the org's own page wins, and it did.** But the consequence is worth Chris's eye:
**Rule A ("prefer the COO over the CEO") would have put an IT leader in the To** at an 88-person
coalition. The run overrode it and sent to the VP of Education instead.

🔴 **Candidate refinement, NOT applied: Rule A's COO preference should check that the COO's ROLE is
operational-programmatic, not just that the TITLE says COO.** Two occurrences is not three. Raised.

## OBSERVATION F — the first Tier-4 send in the machine's history, and it has no approved greeting

[Org 0550] publishes **no staff member anywhere in machine-readable form** (the whole
directory is one PDF) and only an org inbox, `person0401@org0321.example`. That is **tier 4 — generic inbox,
nobody nameable** — the first time the ranking has bottomed out above a hold.

**The greeting used is `ELCFH team,`** — built to the Email 1 convention (bare, no salutation word)
using the org's own short brand, with the names removed. **It is a placeholder. The machine does not
write copy and did not settle this.**

Chris's own observed forms are *"Amanda and team,"* (08-14) and *"Daw, Skyey, Angela and team,"*
(08-18) — both name-plus-team. **`ELCFH team,` is that shape with nothing to name.**
🔴 **Awaiting Chris's ruling. Until he rules, use this form and flag it on every Tier-4 card.**

## OBSERVATION G — org-scale gauge fired twice in one batch, both times taking the CEO off ✅

- **ELC Broward** — 88 staff (vendor), multi-tier leadership. CEO [Person 0537] **resolved** to
  `person1056@org0318.example`, `verified`, and deliberately **left off**. Named on the card so Chris can
  add her in one paste.
- **[Org 0203]** — 27+ staff, Head Start + CCMS + two institutes. CEO [Person 0309]
  resolved and left off; the To went to the Executive Director of the Center for the Early Educator.

**Both are the "multi-program parent" row of the gauge, and in both cases the resolved-but-unused
CEO address is on the card.** That is the pattern to keep: **resolve the CEO, then decide** — the
1-To/2-Cc cap limits the email, never the research.

---

## 2026-08-20 learn pass — the CEO-vs-programme-chief pattern reaches THREE, and it is now the oldest live recipient question

> **[[method]] Phase 5: *"When Chris adds a recipient, that is a defect report, not a preference."***
> The same logic applies when he **replaces** one.

### The two To-swaps Chris made on 2026-08-19

| Org | Machine drafted | 🔄 Chris sent to | Own-site title, quoted |
|---|---|---|---|
| **[Org 0561] County** | [Person 0013], **Chief Executive Officer** | **[Person 0343]** | **"Chief Program & Policy Officer"** — 👉 https://[Org 0597]/meet-the-team/ (re-read 2026-08-20) |
| **[Org 0544] County** | [Person 0017], **VP of Education** | **[Person 0647]** | 🔴 **Not confirmable on any machine-readable ELC Broward page.** See [[verification-log]] 2026-08-20 |

**He kept both Cc pairs unchanged in both cases.** The swap was surgical: the To only.

### 🔴 THE PATTERN, AND WHY IT IS DIFFERENT FROM THE ONES ALREADY LOGGED

**Three occurrences, all the same shape — Chris demotes the top of the org chart in favour of the
person who owns programmes or education:**

| # | Date | Org | Machine's To | Chris's To |
|---|---|---|---|---|
| 1 | 2026-08-12 | [Org 0103] | [Person 0142], **CEO** | [Person 0140], **CCRC Director** |
| 2 | 2026-08-19 | [Org 0544] County | [Person 0017], VP of Education | [Person 0647], education/special projects |
| 3 | 2026-08-19 | [Org 0561] County | [Person 0013], **CEO** | [Person 0343], **Chief Program & Policy Officer** |

🔴 **Occurrence 3 is the one that matters, because the existing rule FIRED CORRECTLY and still lost.**
[[method]]'s org-scale gauge says: *standalone CCR&R, staff page ≲ ~15 people → the ED/CEO takes the
To.* **ELC Sarasota publishes exactly 13 staff.** The machine applied the rule as written, picked the
CEO, and Chris overrode it anyway. **This is not a case of the machine misreading org scale — it is
the gauge being wrong about what seniority means in this sector.**

Occurrence 1 was absorbed into the org-scale gauge in 2026-08-12 as a *size* problem (big agency →
programme director). **Occurrence 3 proves it was never a size problem.** At 13 staff there is no
assistant screening the CEO and no "power move" risk — and Chris still wanted the programme chief.
**The variable is FUNCTION, not headcount.**

### 🟡 CANDIDATE RULE — raised, NOT applied

> **A "Chief Programme", "Chief Program & Policy", "Chief Education" or equivalent programme-owning
> C-level title takes the To over a CEO at ANY organisation size — the same standing [[method]]
> already grants a CCR&R title on Chris's 2026-08-18 ruling** (*"It's okay if the CCR&R sits lower in
> a larger org. They are still the most likely to be the most relevant people to talk to."*).
>
> **The CEO does not come off the thread; they move to the Cc.** Both of Chris's 08-19 sends kept the
> Cc pair intact, so no evidence supports removing the CEO — only demoting them.

**Why this should probably be applied and not just watched:** the identical reasoning is already law
for CCR&R titles. Chris's stated principle there — *"the function matters, not the rank"* — reads as a
general rule that was scoped narrowly to one title family because that is the case that arose first.
**Three overrides in eight days suggest the scope was too narrow.**

⚠️ **Counter-consideration, stated because Chris asked for what he might be missing:** at ELC Broward
he chose someone whose title the machine could not read at all. **That is not a title rule — it is
local knowledge or a judgement from the page's context.** So occurrence 2 is weak evidence for a
*title*-based rule and strong evidence only for the direction of travel. **The rule above rests on
occurrences 1 and 3, which are clean.**

### 🎯 Tier-1 people now known at two organisations mid-sequence

Recorded so the Email 2 and Email 3 recipient decisions do not need a fresh page read.

| Org | Person | Title, quoted from the org's own page | Tier | On the thread? |
|---|---|---|---|---|
| ELC Sarasota | [Person 0415] | "Director of Program Quality & Early Learning Innovation" | **1** | ✅ Cc |
| ELC Sarasota | [Person 0070] | "Early Learning Career Development Specialist" | **1** | ✅ Cc |
| ELC Sarasota | [Person 0618]-Fidelman | "Early Learning Provider Support Specialist" | **2** | 📄 published, not on thread — cap reached |
| ELC Sarasota | [Person 0377] | "Early Intervention & Behavior Specialist" | **2** | 📄 published, not on thread — cap reached |
| ELC Broward | [Person 0223] · [Person 0464] | "Provider Support Contacts" *(role evidence, no title)* | **1** | ✅ Cc |
| ELC Broward | Debra Cruz-Betances · [Person 0065] | "Provider Support Contacts" *(role evidence, no title)* | **1** | 📄 published, not on thread — cap reached |

🎯 **ELC Sarasota runs its own "ASPIRE Teacher Training Institute" and a separate physical
"Provider Supports & Teacher Training Institute" site.** An organisation that has built its own
training institute is a training *buyer* with an existing delivery habit — **the strongest positioning
signal on this thread**, and worth using at Email 2 if Chris ever wants that email tailored. *(He does
not — the copy is frozen. Recorded for his use, not the machine's.)*

### ⚪ Not a recipient pattern, but recorded here because it changes who is reachable

**Chris's HubSpot browser extension is re-adding `<HUBSPOT_BCC_ADDRESS>` to every send**, while
`hubspot_bcc` is `disabled` for machine drafts. Confirmed on all 12 of his 2026-08-19 sends.
**Consequence for recipients:** every organisation the machine cold-emails acquires a HubSpot contact
record tagged `BCC_TO_CRM`, which [[method]] calls *"the most reliable relationship signal in this
CRM."* **It is the machine suppressing itself, one send at a time.** Raised on 08-12, again on 08-19,
again tonight. **Still not auto-applied — an exemption rule needs Chris's word.**

### ✅ CLOSED 2026-08-20 — the BCC-to-CRM note above is RETIRED, by Chris's ruling

> ✅ **Chris, 2026-08-20:** *"The hubspot browser extension is working. That means we don't have to
> worry about that part. Update the tasks/method accordingly by removing any need to monitor or act
> on bcc to crm."*

**The observation directly above — that Chris's extension re-adds the BCC on every send and thereby
manufactures `BCC_TO_CRM` suppression records — is correct and is no longer actionable.**
`BCC_TO_CRM` has been removed as a suppression signal in [[method]] and [[hubspot-suppression]].
**The machine no longer monitors or reports it.** `FORM` and `CRM_UI` are unaffected.

**Kept in this file rather than deleted, because it is the reasoning that justified the deletion** —
and per [[method]]'s refactor rule, the last independent statement of *why* a control was removed is
worth more than the space it costs.

---

## 🔄 LEARN PASS — 2026-08-21

**As-sent delta: 14 sends reconciled · 0 recipient changes by Chris.**

🎯 **This is the first run in the machine's history with `M = 0` on the as-sent delta.** Chris sent all fourteen of the 2026-08-20 drafts — 7 Email 1 and 7 Email 2 — **without altering a single recipient.** Against a baseline of *thirteen recipient differences across fifty-four organisations* (roughly one in four sends, per the corrections table in [[contacted]]), fourteen consecutive untouched sends is a real signal.

**What it most likely means, stated as a hypothesis rather than a conclusion:** the 2026-08-19 batch was the first to use the full 1-To/2-Cc cap after the connector regression lifted, **and it was also the first batch where the roster sweep ran before the ranking descended.** The three overrides that preceded it (Jefferson County 08-12, ELC Broward and ELC Sarasota 08-19) were all *"the machine picked the CEO, Chris picked the programme person"* — the exact failure R4's rank list was written to remove. **R4 shipped on 08-20 and the very next batch needed no corrections.** One batch is not proof, but it is the outcome R4 predicted.

⚠️ **One caveat against over-reading it:** Chris cleared fourteen drafts in a single sitting on a Thursday afternoon. **A fast clearance and a careful review are not the same event**, and this data cannot tell them apart. Watch the next two batches before treating R4 as validated.

### 🆕 A recipient pattern worth recording — the ROLE-EVIDENCE tier keeps earning its place

**Two of tonight's ten To recipients have NO job title published anywhere on their employer's site**, and both are Tier 1 purely on quoted role evidence:

| Person | Org | The evidence that tiered them |
|---|---|---|
| **[Person 0131]** | [Org 0609] | *"To register for Infant, Toddler or Preschool CLASS Observer Training, please contact [Person 0131]"* — the only human named on ECS's entire PD page |
| **[Person 0625]** | [Org 1272] | *"Are you a TRS Child Care Center owner? To request corrections to your listing please contact: tony.armadillo@…"* |

**`tier_on_role_not_title` was ratified on 2026-08-18 after going unapplied for five days across five raisings.** It has now produced a recipient in three consecutive runs. **Under the old title-keyword rule both of these people were untierable and both organisations would have dropped to a generic inbox.**

### 🆕 An anti-pattern to watch: the vendor-named ghost roster

**Nine people were returned by the reverse lookup tonight — at Alamo, Capital Area and North Central Texas — in exactly the roles the machine wants** (*Texas Rising Star Mentor/Coach*, *Senior Director Child Care Quality Initiatives*, *Child Care Manager*). **Not one appears on their employer's own website.**

**This is a distinct organisational shape and it is worth naming:** boards that employ a real early-childhood quality bench and **publish none of it**, routing everything through department inboxes. Capital Area names 55 people and not one of them touches child care. North Central Texas names **nobody at all**.

🔴 **The correct handling is the one used tonight — HOLD-G2, draft the inbox, do not greet a vendor-only name** — and the reason is on the record: `person0322@org0314.example` was `Verified` and belonged to someone who had left. **But the right follow-up is cheap and is not yet queued: take the nine role titles back to those three sites and search for them by name.** A name you did not have is a search term you did not have.

---

# 📈 LEARN PASS — 2026-08-24

## 🆕 THE REPLY KEEPS COMING FROM THE Cc, NOT THE To — third occurrence, now a pattern

**Reply #8: [Person 0197], Chief Programs Officer, [Org 0552], 2026-08-21.**
She was in the **Cc**. LaTrisha Sims, the To, did not reply.

| # | Org | Who replied | Their slot | Their rank |
|---|---|---|---|---|
| 1 | ELC Palm Beach | [Person 0209], Chief of Communications & Public Affairs | **Cc** | — |
| 2 | ELC Alachua | [Person 0617] | To | — |
| 3 | ELC Polk | [Person 0499] | **Cc** | — |
| 4 | Child Care Dutchess | [Person 0645], Director of Professional Development | **Cc** 🎯 | **1** |
| 5 | ELC Florida's Gateway | LaShone Surrency, CEO | To | OFF-by-default |
| 6 | **[Org 0552]** | **[Person 0197], Chief Programs Officer** | **Cc** 🆕 | **2** |

🎯 **Four of six identifiable replies came from a Cc recipient.** **The single booked meeting came
from a Cc — a rank-1 Director of Professional Development who was not the To.**

**What this does and does not say.** It does **not** say the To is being chosen wrongly — R4's rank
list is young and the as-sent delta has been zero for two batches. **It says the second and third
slots are doing more work than "redundancy" implies**, and that R2's framing of the cap as a
reliability control understates it: *the Cc is where the answer comes from.*

🔴 **Recorded, NOT applied.** No rule changes on six data points. **The observable prediction, so this
is falsifiable rather than a story:** *if the pattern is real, the next three replies should also
skew Cc.* Re-check at reply #11.

## The Marion reply, read for what it teaches

> *"We appreciate you reaching out. I have looked at your website and you seem like a dynamic speaker.
> I'd like to keep your information on file for the future planning. At this time, we are not searching
> for any professional development, however, these opportunities do come about throughout the year."*

**A soft no with a stated re-entry condition.** Second of this exact shape — [Person 0499] at ELC Polk
wrote *"I am going to add your info to our contact list. When we have Requests for Proposals, I'll be
sure to include you."* **Both name a future procurement event as the opening.**

⚠️ **There is no ledger stage for this.** It is not `replied and dead` and it is not a meeting.
**Candidate stage, raised not applied: `deferred — named re-entry condition`**, with the condition and
a date recorded so it can be worked deliberately rather than lost between "replied" and "closed."
**Two organisations already qualify.** This is a question for Chris, not a change the machine makes.

## Copy observation — logged, frozen, nothing applied

**`Thanks for your hard work, and happy Friday!`** appears in **5 of the 6 follow-ups Chris touched on
2026-08-21** (the 4 sent + the [Org 0546] draft). The approved v4 sign-off is
`Thanks for your hard work,`. **Timestamps place the edit with Chris at review (18:21–18:23Z), not
with the machine (09:10Z drafts are clean).**

🔒 **Copy is frozen. Nothing changed.** Five occurrences is above the 3-occurrence reporting threshold,
so it is **reported for a yes/no** as D2 — with the machine's own read that this looks like a
day-of-week flourish rather than a template change, since every occurrence fell on a Friday.

## Recipient count — no change proposed

**`As-sent delta: 0 recipient changes` for the second consecutive batch.** Nothing to learn from a
clean batch except that the current rules are holding. **The real test is the next Email 1 batch**,
where the judgement actually happens; both zero-delta batches so far were follow-ups or post-R4 sends.

---

# 📈 LEARN PASS — 2026-08-24, LATER (8 sends, 2 recipient changes, reply #9)

## 🔴 THE Cc PATTERN STRENGTHENS TO 5 OF 7 — and the prediction made this morning already held

**This morning this file recorded the Cc pattern at 4 of 6 and wrote a falsifiable prediction:**
*"if the pattern is real, the next three replies should also skew Cc."*

**Reply #9 arrived seven hours later. It came from the Cc.**

| # | Org | Who replied | Slot |
|---|---|---|---|
| 1 | ELC Palm Beach | [Person 0209], Chief of Communications & Public Affairs | **Cc** |
| 2 | ELC Alachua | [Person 0617] | To |
| 3 | ELC Polk | [Person 0499] | **Cc** |
| 4 | Child Care Dutchess | [Person 0645], Director of Professional Development | **Cc** 🎯 booked |
| 5 | ELC Florida's Gateway | LaShone Surrency, CEO | To |
| 6 | [Org 0552] | [Person 0197], Chief Programs Officer | **Cc** |
| 7 | 🆕 **[Org 0548]** | **[Person 0514], Director of Quality Impact** | **Cc** |

**5 of 7. One down, two to go on the stated test.** 🔒 **Still recorded, still NOT applied** — one
confirming instance is what a prediction is supposed to survive, not proof.

⚠️ **The honest counter-reading, stated so this does not harden into a story.** The To is chosen by
R4's rank list as the person most likely to *decide*; the Cc slots take ranks 2 and 3, which in this
sector are the practitioners who *run training*. **A decision-maker forwarding rather than replying
is not the same as a decision-maker ignoring the mail.** The pattern may be about who replies to
strangers, not about who is the right recipient. **Nothing about R4 changes on seven data points.**

## 🎯 REDUNDANCY EARNED ITS KEEP TODAY — the first direct evidence

**[Org 0548] lost one of three recipients to a hard bounce.** The Email 2 repair went
to the two survivors with the approved parenthetical — and **a survivor replied in 28 minutes.**

**Chris's stated reason for the 1-To/2-Cc cap was exactly this:** *"if we're wrong and one email
bounces, we still have 2 recipients on the thread who might keep each other accountable to replying."*
**Until today that was a rationale. It is now an observation.** 🔴 **n = 1** — recorded as evidence
for the cap, not as proof that two recipients beat three.

## Recipient changes — `M = 2`, both instructive, neither a surprise

| Change | Read |
|---|---|
| **`ccrr@org0315.example` dropped** | Chris applied a **bounce-adjacency** judgement the machine did not have a rule for: *a sibling address on a tenant that already rejected us is not worth the risk.* **The machine had verified it correctly and would have sent it.** 🆕 **Candidate rule, raised NOT applied: after a hard bounce at a domain, a second address at that same domain is HOLD-for-Chris rather than auto-draft — especially on a `5.4.1 Access denied` (policy) rather than `5.1.1` (nonexistent).** This is a real gap, and it is Chris's to rule on |
| **`person0560@org0319.example` dropped** | **Closes D3 by action.** The run asked whether a recipient named in no greeting should join the greeting; Chris removed her instead. **Read: the greeting is the source of truth for who is on the email, not the other way round.** Fold into future follow-ups — **if a recipient cannot be named in the greeting, question the recipient, not the greeting** |

🔴 **Two changes in eight sends after two consecutive zero-delta batches.** **Both are recipient
*removals* under a rule the machine did not hold**, not corrections of a wrong pick. **R4's rank list
is still unchallenged** — neither change moved a To to a different person.

---

# 📈 LEARN PASS — 2026-08-25

## Copy: zero divergences across 18 sends. The first fully clean copy run.

Full-body diff of every send since the last run against the approved templates in
[[Cold-Outreach-Sequence-CCR&R]]:

| Cohort | Template | Result |
|---|---|---|
| 10 × Email 1, 2026-08-24 22:13–22:16Z | **v6** | ✅ **byte-identical** except the greeting and the org short-name in the subject |
| 8 × Email 2, 2026-08-24 13:59–14:03Z | **v4** | ✅ **byte-identical** |

**The previous three runs each found something** — a v3/v4 split, a `Hi`→`Hey` change, a recipient
edit. **This is the first run in which Chris changed nothing at all.** `machine_writes_copy: never`
holds; nothing was applied, and there was nothing to apply.

## Recipient behaviour: the send window is a single burst, and that explains the recurring "shortfall"

**The ten Email 1s went out inside a 2½-minute window (22:13:52Z → 22:16:15Z)** — nine hours after
the eight Email 2s cleared in a 4-minute window (13:59:20Z → 14:03:41Z).

🎯 **Chris clears the queue in sittings, not continuously.** This is the mechanism behind the note
that has now appeared in three reports — *"the binding constraint is the send review, not the
machine's capacity."* **The constraint is not a rate. It is the availability of one block of
attention.** Ten drafts and twenty drafts cost him nearly the same; zero and one do not.

**Implication, raised not applied:** if the constraint is a sitting rather than a rate, then
`target_drafts` is tuned against the wrong variable, and **batch size matters far less than batch
regularity.** Worth a conversation before the number is moved again.

## Recipient rank: the reply keeps coming from the Cc

**Unchanged and now at 4 of 9.** [Person 0514] (ELCFV, 08-24) was a **Cc**, on a thread that had lost
a recipient to a hard bounce and went out at `Redundancy: 2 of 3`. **The redundancy control has now
paid for itself in a case where it was degraded.**

## A non-observation, recorded so it is not mistaken for a finding

**Of 18 addresses sent to, exactly one bounced — the only one of the eighteen with no human name
attached to it on its source page.** 🔴 **n = 1.** This is written down so a second instance is
recognisable, and it changes no rule. See [[verification-log]] 2026-08-25.

---

# 🔴 AS-SENT DELTA — 2026-09-02. M = 8 of 11. MEASURED against `runs/2026-09-02/drafts.json`, not recalled.

**19 Email 2 follow-ups: sent 12:14–12:20Z with ZERO recipient changes.** Including [Org 0036], where the
nameless `mconley@` Cc and the `and team` greeting were both accepted as drafted.

**11 Email 1s: Chris attached the files (all now ~12.4 MB), scheduled 9 for 09-02T14:00Z and 2 for
09-03T14:00Z, and edited 8 of them.** Untouched: Del Norte · CCRC · [Org 1026].

| Org | What the machine drafted | What Chris sent | Read |
|---|---|---|---|
| **4Cs of Alameda** | To `takijag@` (CEO, Apollo) · Cc `info@` | To **`reginag@`** · Cc **`ericao@`** · **`barbarak@`** — greeting `Regina, Erica, and Barbara,` | 🔴 **Every recipient replaced.** `barbarak@` is almost certainly [Person 0069], Director of Community Services — the person I named as the right target and could not reach. Their `/about/staff-directory/` served an **empty body** to `web_fetch`; Chris opened it in a real browser and got three addresses |
| **[Org 0377]** | To `michelle.mortenson@` · Cc `john.jones@` (ED) | Cc → **`yvette.white@`** (Director of Operations) | ED dropped for an operating director |
| **[Org 1177]** | Cc `mpegueros@` (QA Manager) | Cc → **`nmunholand@`** ([Person 0509], Child Care Subsidy Program Lead) | Subsidy lead preferred over QA |
| **[Org 0969]** | 1 To + 2 Cc | **+ `person0599@org0608.example`** — greeting `Christina, Tommy, Jenny, and Diana,` | 🔴 I EXCLUDED this person deliberately (visible name "Tommy", address `jgunton-bell@`, two competing domains). Chris wanted the 4th slot and used "Tommy". **Over-caution cost a recipient** |
| **[Org 1071]** | 1 To + 1 Cc (2 of 3) | **+ `person0135@org0668.example`** ([Person 0083], Director Early Education & Instructional Services) — `Rea, Brandy, and team,` | Thin card filled out from names I had but had no address for |
| **NCO / RCCC** | Cc `sperez-torres@` (Sulema, first name only) | Cc → **`childcare@org0536.example`** — `Shana, Teri, and team,` | A first-name-only human is worth less than the role inbox |
| **[Org 0639]** | *"…the right person to talk to about PD and training."* | *"…about PD and training **at FRC**."* | ✏️ COPY CHANGE |
| **4Cs of Alameda** | same sentence | *"…about PD and training **at 4C's of Alameda County**."* | ✏️ Same copy change, second instance |
| **ICOE** | subject *"…at [Org 0708] . . ."* | *"…at ICOE Early Care Education . . ."* | 🔴 **MY DEFECT — see below** |

## 🔴 MY DEFECT: I HTML-ESCAPED A PLAIN-TEXT SUBJECT LINE

I passed `subject: "Question about PD/Training at ICOE Early Care &amp; Education . . ."`. **The
subject field is not HTML.** The `&amp;` was mangled and Chris had to repair it. **`htmlBody` takes
entities; `subject` takes literal characters. Never escape a subject.** Every org with an ampersand
in its name is exposed to this — CCR&R itself is one.

## 🎯 THE PATTERN WORTH RULING ON — R4's CEO/ED default

**Chris removed the chief executive from BOTH large agencies where I had used one** (4Cs CEO from
the To, [Org 0377] ED from the Cc) **and left the ED in place at Del Norte, a ten-person agency.**

🔴 **This runs OPPOSITE to OPEN item E**, which had recorded him promoting the ED *to* the To three
times — every one of those at a tiny agency. **The two observations reconcile if the rule is about
AGENCY SIZE, not seniority:** at a small agency the ED *is* the PD decision-maker; at a large one
the operating and programme directors are, and the chief is noise. R4's blanket CEO/ED exclusion is
right for large orgs and wrong for small ones. **Chris's ruling needed — do not change R4 on this
inference alone.**

## 🎯 THE MECHANISM BEHIND THE 4Cs MISS, AND IT IS FIXABLE

`org0008.example/about/staff-directory/` returns HTTP 200 with an **empty body** to `web_fetch`, so the
run recorded "no reachable named human" and fell back to the CEO. **Chris read the same page in a
browser and found three people.** A real browser was available to this run and was **denied
navigation** — an unattended run has nobody to approve a new site.

🔴 **"Empty body" now means "JS-rendered, a human can read it," NOT "no data."** Twenty organisations
sit on the blocked-directory list under that description, and at least some of them are not blocked
at all. **Proposed: pre-approve the browser for this machine, or route blocked directories to a
short human-in-the-loop queue.** Chris's call.

## Sent-vs-drafted, the honest scoreboard

```
As-sent delta: 8 of 30 drafts edited · 19 of 19 follow-ups untouched · 3 of 11 Email 1s untouched
Recipient changes: 6 orgs · 4 addresses swapped · 2 addresses added · 1 role inbox substituted
Copy changes: 2 (org name inserted into the ask sentence) · 1 subject repair (machine defect)
Attachments: Chris attached the GIF + flyer to all 11, as the dossier asked
Schedule: 9 for 09-02T14:00Z · 2 for 09-03T14:00Z (Placer, NCO)
```


## 2026-09-23 — learn pass
- CA R&R vocabulary (0.7a): "Provider Support Specialist" (named CCIP trainings contact), "CPIN Manager" (state PD network), "[Person 0649] Advisor", "Child Care Services Supervisor (R&R Unit)". Candidates for R4 rank-1 signal words — proposed, not applied.
- As-sent copy: Chris's scheduled 09-16 Email 1s (e.g. [Org 1331]) end the P.S. without the final period ("…educators are used to"). Template has the period. Logged, nothing changed (machine_writes_copy: never).

## 2026-09-24 — learn pass
- WA vocabulary (0.7a): "Professional Development Coordinator" (standard regional title), "PD Administrator", "Early Learning Training Coordinator", "Early Learning Advanced Trainer"; coaching = Early Achievers.
- OK vocabulary (0.7a): "Child Care Consultant", "Infant/Toddler Consultant/Specialist", "Business Consultant"; leads "Regional Director". Proposed R4 rank-1 signal words: Professional Development Coordinator, Child Care Consultant, Infant/Toddler Consultant. Used for ranking tonight; method.md not edited.
- As-sent diff (09-23 E1 batch): body identical to template; Chris inserted the GIF inline. No copy change.
- 🔴 As-sent attachment (09-22 E3, e.g. CDSC `<thread-id>`): Chris attached **`HST_3PackStarterKit.pdf`** (the 7.2 MB file) — the copy file names `HST_3PackStarterKit_email.pdf` (2.7 MB) and warns about exactly this. Logged; nothing changed.


---

# 2026-09-29 — learn pass (operative observations only)

- **Inbox→human mapping, East Central University:** E1 To `person0083@org0299.example`; the human ([Person 0039]) replied from `person0072@org0299.example` and her own mail client quotes her as `angipat@`. The two addresses are the same mailbox to the org. Future mail to that thread: reply, do not add.
- **State-run and county-run CCR&Rs publish addresses more reliably as visible text than as `mailto:`** (CCRC, BCAP, Monmouth, Child Care Connection NJ): a `mailto`-only extractor would have found zero. The extraction that matters is the rendered DOM text.
- **Mail domain ≠ web domain is common in NJ:** Child Care Connection (`org0093.example`), [Org 0410] (`org0099.example`), 4Cs Passaic (`org0014.example`), Rutgers Southern (`org0640.example`). All registered before drafting.
- **Apollo returns personal ymail/yahoo addresses beside the work address** for CCR&R leaders (Daniels, Wright, Wise): always take the org-domain one.


## 2026-09-30 - learn notes (observed, not applied)
- **Massachusetts CCR&Rs sit inside big community-action or nonprofit parents** (Boston ABCD, QCAP, [Org 1068], The Community Group, PACE, CACCI). Program pages name few or no PD roles; the reachable owner is usually a *Program Director* (R4 rank 2). Only Child Care Circuit's parent publishes a named training/workforce chief, and none of the parent's staff pages print addresses.
- **Mail domain = parent-org domain** in Boston (`org0056.example`) and Child Care Circuit (`org0720.example` for people, `org0164.example` for the program inbox). Both pairs declared as aliases before drafting.
- **Staff PDFs are a real source**: [Org 1068] publishes the CCR staff list as a PDF with working mailto annotations; a text-only reader misses them. The PDF also carried two anomalies (domain typo, wrong-person link).
- **A name-address link inferred from a footer** (CACCI: `bethg@` beside the CCN phone number) is weaker than a printed pair; banked rather than drafted.



---
- **Michigan GSQ operators do not publish staff addresses** on their own sites (contact forms, or nothing); addresses live only on state GSQ pages, which are not Gate-1 sources. V1 path works only where Apollo identity is high.
- **ZeroBounce `valid` does not prove current employment** (Clevenger at org0532.example). E1.6 is the check that matters.

- 2026-10-04: Oregon CCR&Rs sit inside ESDs and community colleges; Apollo has no record for most of their staff, so V2 live-page evidence is the norm there. Missouri/CT/MT/WV: statewide-contractor models, not regional networks.
- Titles that recur at these orgs: Quality Improvement Specialist/Facilitator/Coordinator, Training Coordinator, Professional Development Navigator/Coordinator.

- 2026-10-07: rank-1 titles seen: Provider Services Supervisor (CCRC AL), Professional Development Coordinator (CCA NWA), Training Coordinator (A-State; NSU). Small ECE-adjacent university hosts publish named staff pages; state-agency hosts mostly do not.

- 2026-10-08: rank-1 titles seen: Manager Professional Learning / Senior Specialist Professional Development ([Org 0046]), Early Care and Education Trainer & Program Director (FGC AL), Education Director (CRN AL), Early Care & Education Specialist (Dare CYP), Professional Development Coordinator (PFC Johnston), Lead TA/CCR&R Coordinator (Wilson PFC), Director of Partnerships in Child Care (VOA SCLA). NC Smart Start partnerships and LA/AL nonprofits publish named staff more often than AR/MS; role-inbox-only sites are the common hold.

- 2026-10-08 (pass 2): NC Smart Start/PFC sites mostly publish named individual mailtos with program-assistant/coordinator titles; rank-1 To chosen from PD/CCR&R/training roles, ED excluded by default. Small shops (Rockingham, Watauga) publish only a pattern or unbound mailtos - Apollo+ZeroBounce V1 used. ND/SD/ID: single university or cooperative operators; SDSU and UI are public-university units.

- 2026-10-09: AK thread publishes PD-titled staff mailtos; VT Umbrella/VAC expose referral-desk roles rather than PD titles; PATCH publishes named staff on org0590.example.

- 2026-10-09 (pass 2): NC/MD/MN/WI/VA published PD- or quality-titled staff (Quality Child Care Manager, Professional Development Advisor, Early [Person 0124], Training Specialist); RI, FL, NY (NYC), WI Fox Valley, MN [Org 1211] publish only generic or role inboxes; Niagara prints role-titled mailboxes with no names; Ready Region leads (UWVBR, [Org 0841]) publish VQB5 contacts.

- 2026-10-10 drain1: 9 new Email 1 drafts; 8 of 9 to V3 role/department inboxes with a "team" greeting; named recipients only at EdAdvance (3) and VECF (3).

- 2026-10-10 drain2: 66 new Email 1 drafts; named humans on the To for 32 of 66; 34 to V3 role/department inboxes only. Titles skew to PD coordinators/coaches/specialists where published; many public-agency and workforce-board orgs publish no PD role.


## 2026-10-12 nightly — no change
Run 2026-10-12: 0 new drafts, 0 follow-ups due. Retries re-touched: Kern CA, ELRC 19 PA, COAD OH -> CLOSED_R1 (dedup_check); 4C of the UP MI stays HELD, retry 2026-10-26. No new addresses evidenced.

- 2026-10-14 run: no new addresses verified (0 drafts). [Org 0464] info@ bounced 10-13 (550 5.4.1). Replies logged in contacted.md.

- 2026-10-15 nightly: 0 drafts; sent-sweep reconcile 44 E1 (10-14) → /1; replies ★ ECRC Canton, YWCA NW Illinois, Montgomery Co MD CCSS; bounce person0459@org0767.example (Great Start to Quality Kent, 5.1.1).

- 2026-10-22 run: 0 drafts; no change (supply exhausted outside CO). See review-2026-10-22.md.
