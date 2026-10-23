---
business: Human Skills Training
type: template
title: "Dossier — WHOLE-FILE fill-in template (the run does not invent structure)"
status: binding
owner: Chris Danilo
created: 2026-08-11
rewritten: 2026-09-03
rewritten_because: "Chris, 2026-09-03: 'Why does the structure of the dossier keep changing? Build an outline template for the dossier that each scheduled task run will just fill in.' The 2026-08-11 file was a CARD template only — it never described the whole file — so the run reconstructed the file shape from prose in method §0.6a every night, and prose gets re-derived. See CAPA-2026-09-03-dossier-format-drift."
supersedes: "[[archive/dossier-template-2026-08-11-card-only-SUPERSEDED]]"
checked_by: bin/dossier_check.py
related: ["[[method]]", "[[CAPA-2026-09-03-dossier-format-drift]]", "[[verification-log]]"]
---

# Dossier — whole-file fill-in template

🔴 **THE RUN FILLS THIS IN. THE RUN DOES NOT REDESIGN IT.**
Copy this file, replace every `{{token}}`, delete every `<!-- note -->`, keep every heading exactly
as written. **`bin/dossier_check.py` verifies the produced file against the REQUIRED HEADINGS list
below and exits 1 if a heading is missing, renamed, or out of order.**

> **Why this file exists.** method §0.6a pins the section order in prose. Prose has to be *read and
> re-derived* every night by whatever is running, and on 2026-09-02 and again on 2026-09-03 the
> shape moved anyway. **A heading list is a countable object; a paragraph describing a heading list
> is not.** Same reasoning as P9's idempotency grep and `dedup_check.py`'s set intersection.

> ⚠️ **If a rule in method §0 contradicts this template, §0 wins and the run says so in the review.**
> This file is the SHAPE. §0 is the LAW. When §0 changes shape, **this file must be edited in the
> same session** — that is P7b applied to the template.

---

## REQUIRED HEADINGS — in this exact order. `bin/dossier_check.py` reads this block.

```
H1   # 📤 Sending Dossier — {{DAY}} {{YYYY-MM-DD}}
H2   ## ⚠️ READ THESE BEFORE YOU SEND ANYTHING
H1   # 1 · NEW ORGANISATIONS — Email 1 × {{N_E1}}
H1   # 2 · FOLLOW-UPS — Email 2 × {{N_E2}} and Email 3 × {{N_E3}}
H2   ## Email 2 — {{why due}}
H2   ## Email 3 — {{why due}}
H1   # 3 · WHAT ELSE HAPPENED
H1   # 4 · DECISIONS FOR YOU
H1   # 5 · STANDING NUMBERS
```

🔴 **Sections 1 and 2 never swap.** New organisations lead — they carry unverified people and need
Chris's eye. Follow-ups have all delivered once and need far less scrutiny.
🔴 **Inside each section, OLDEST FIRST** — matching his Drafts folder, which reads bottom-to-top.
*(The 2026-09-02 ruling says which SECTION leads. The 2026-08-28 ruling says the order INSIDE one.
They operate on different axes and both bind.)*

---

# FRONTMATTER — copy verbatim, fill the tokens

```yaml
---
business: Human Skills Training
type: dossier
title: CCR&R Outreach — Sending Dossier {{YYYY-MM-DD}}
status: ready to send
owner: Chris Danilo
run: {{YYYY-MM-DD}}
drafts: {{N_TOTAL}}
related: ["[[method]]", "[[review-{{YYYY-MM-DD}}]]", "[[STATE]]", "[[sequence-tracker]]"]
---
```

---

# TOP LINE — before the H1, always, no exceptions

<!-- method §0.3 step 18b + §0.6. Verbatim output of bin/calibration.py. NEVER retyped from memory. -->

```
`{{OUTPUT OF bin/calibration.py}}`
```

---

# H1 — the title block

```markdown
# 📤 Sending Dossier — {{DAY}} {{YYYY-MM-DD}}

**{{N_TOTAL}} drafts waiting: {{N_E1}} new organisations (Email 1) · {{N_E2}} Email 2 · {{N_E3}} Email 3.**
Layout is pinned by [[method]] §0.6a and filled from [[dossier-template]]. New organisations lead;
follow-ups second; oldest first inside each section.
```

---

# H2 — ⚠️ READ THESE BEFORE YOU SEND ANYTHING

<!-- ONLY things that change what Chris does in the next 10 minutes. Attachment gates, a
     compromised domain, a bounce that changes a recipient, a size warning, an address class he
     should personally eyeball. NOT findings. NOT rules. Those live in the review file.
     If there is genuinely nothing, write "Nothing this run." — do not delete the heading. -->

```markdown
## ⚠️ READ THESE BEFORE YOU SEND ANYTHING

| # | What | Which cards |
|---|---|---|
| **1** | {{action, imperative, with the file path and size if it is an attachment}} | {{card refs}} |
| **2** | {{…}} | {{…}} |
```

### 🔴 THIS TABLE IS EXCEPTIONS ONLY — Chris, 2026-09-03

> ✅ **Chris:** *"We want the triggers to be for special cases. If the trigger is running the same
> way every time, it's not a good trigger."*

🔴 **THE TEST: would this line be true of EVERY batch?** If yes, **it does not belong here.** A box
that says the same thing every morning trains Chris to skim past it — and this box exists precisely
to stop him mid-send. **Every routine entry weakens the one entry that matters.**

**BANNED from this table — routine, and homed elsewhere:**

| ❌ Never here | ✅ Where it lives instead |
|---|---|
| The Email 3 Starter Kit attachment gate | **The Email 3 section**, as the verbatim fenced block. §0.4 **E3.1 still binds** — the gate is required on every Email 3, it is simply not duplicated at the top |
| The Email 1 GIF + flyer attachment reminder | Nowhere at the top. 🔄 2026-10-04: each Email 1 card carries one line — `📎 FLYER ATTACHED BY ZAPIER ✅ <draft id> · GIF: drop HST_WorkshopInAction.gif in under the "AI-powered world." line` — the ✅ written only after the `has:attachment filename:HST_Flyer.pdf` read-back returned that draft id; a native-fallback Email 1 reads `📎 ATTACH FLYER + GIF BEFORE SENDING` instead |
| "Recipients are fixed at Email 1 (R5)" | The follow-ups section preamble |
| Anything restating a standing rule Chris wrote | The review file, if anywhere |

**QUALIFIES — true of THIS batch and not the last one:**

| Trigger | Text |
|---|---|
| A domain in the batch is catch-all, compromised, or has a deliverability history | 🔴 {{domain}} — {{what it means for reading a bounce}} |
| An address class Chris has not ruled on appears for the first time | 🔴 {{class}} — {{one line}} + pointer to the matching decision in §4 |
| A bounce or departure changed a recipient set since he last saw the thread | 🔴 {{org}} — {{what changed, and that the greeting was rewritten}} |
| A card is unusually thin, unusually large, or carries a known-stale roster | ⚠️ {{org}} — {{one line}} |
| An attachment differs from the standing one, or a file he uses is the wrong build | 📎 {{the specific deviation}} |
| A draft should probably NOT be sent today | 🔴 {{org}} — {{why, and what would change it}} |

⚠️ **If nothing qualifies, write `Nothing this run.` and keep the heading.** An empty box he can
confirm in one second is worth more than a full box he has learned to ignore.

---

# H1 — 1 · NEW ORGANISATIONS

```markdown
# 1 · NEW ORGANISATIONS — Email 1 × {{N_E1}}

**{{states covered}}.**
Every address below was copied character-for-character from the organisation's own live page. Each
link is the exact page the address came from — **V2** links show the address printed on the page and
you can verify end to end; **V1** links show the person's name and title only.
```

## THE CARD — repeat per organisation, numbered continuously across the whole file

```markdown
## {{N}} · {{Org as it prints its own name}} · {{ST}} · Email 1 · Tier {{1-5}} {{🥇 optional superlative}}

- **Domains** — `website_domain: {{host after redirects}}` · `mail_domain: {{host of the harvested addresses}}` — **{{the same | DIFFERENT}}**
  <!-- E1.8: RECORD BOTH EVEN WHEN IDENTICAL. "These are the same" is a finding.
       If DIFFERENT, state which register handled it: config.domain_aliases (org-owned pair)
       or config.shared_tenant_domains (a host many unrelated orgs mail from — NEVER aliased). -->
- **Thread** `{{threadId}}` · draft `{{draftId}}`{{ · thread carries ⚠ if flagged}}
- **Greeting** `{{exact greeting line}}`
- 🔗 **Roster pages** — [{{staff/team page label}}]({{exact URL}}){{ · [{{second page}}]({{URL}})}}{{ · ⛔ [{{blocked page}}]({{URL}}) — {{what happened}}}}
  <!-- ORG-LEVEL, separate from the per-recipient links below. This is the page Chris opens to size
       up the organisation in one glance: how many staff, what the role structure is, who else is
       there. Include EVERY roster page read, INCLUDING the ones that failed, with what happened
       (JS-only, empty body, PDF, password wall, Cloudflare) — a blocked page he can click is how he
       overrules the machine with a browser session. -->

| | Name | Title (verbatim) | Address | 🔗 Page that evidences it |
|---|---|---|---|---|
| **To** | {{name as printed}} | `{{title verbatim}}` | `{{address}}` | [{{page label}}]({{exact URL of the page THIS address came from}}) |
| Cc | {{…}} | `{{…}}` | `{{…}}` | [{{…}}]({{…}}) |
| Cc | {{…}} | `{{…}}` | `{{…}}` | [{{…}}]({{…}}) |

- **Redundancy** {{N}} of 3 · **Validity** {{V1|V2|V3 per recipient, with the E1.7 wording}}
- {{🎯 the single best reason to believe this card — corroboration, a quoted line, a timing signal}}
- {{📝 anything that would look like tampering later: two titles for one person, odd casing, a stale
   roster field, a title the site does not print}}
- {{⚠️ anything Chris should know but that does not change the send}}
- {{🔴 anything that changes whether he sends at all — ALSO goes in the READ-THESE table at the top}}
```

### Card rules that do not change

| Rule | |
|---|---|
| 🔴 **EVERY URL IS A CLICKABLE MARKDOWN LINK — `[label](url)`. ALWAYS.** — Chris, 2026-09-02 and again 2026-09-03 | **A bare URL, a plain-text hostname, a URL inside a code span, or a page named without a link are ALL DEFECTS.** His stated use is *"immediately go to the staff page you sourced the email addresses from and visually verify"* and *"so I can go to the exact page where the staff/emails were pulled from."* 🔴 **A URL he has to select and copy out of a code span does not serve that.** This applies to the org-level Roster pages line AND to every recipient row |
| 🔴 **TWO LINK LAYERS, BOTH REQUIRED** | **Org level** (`🔗 Roster pages`) = the directory he opens to assess structure and roles at a glance. **Recipient level** (the table's last column) = the exact page THAT PERSON's address came from. They are often different pages, and when they are the same page, still link it in both places — he reads them at different moments and for different reasons |
| 🔴 **Evidence links are PER RECIPIENT, not per org** | Two people found on two pages get two links. The link sits on the row of the person it evidences |
| 🔴 **The exact page the address came from** | Not the home page, not a search result, not an aggregator |
| **Label the link so he knows what he is about to open** | `[org0509.example/professional-development/](…)` or `[staff directory](…)`, never `[link]` or `[here]`. When several rows share one page, `[same page](…)` is correct and readable |
| 🔴 **Say what the page will and will not show him** | A **V2** link shows the address printed — verifiable end to end. A **V1** link shows NAME and TITLE only; the address came from a vendor and **will not appear on that page** — label it `(name + title only — address is vendor-resolved)` so a page lacking the address is never mistaken for a bad citation |
| **A blocked page is still named** | JS-only, PDF, empty body, password wall — link it anyway and say what happened. That is how Chris can overrule with a browser session |
| **Redundancy is reported, never scored** | §0.5. A thin batch is sometimes correct. Never pad a Cc to reach 3 |
| **Never assume a pronoun** | Names and pronouns exactly as the org prints them |

### 🔴 ROSTER RESOLUTION LINE — required on any card where a roster sweep ran

<!-- Carried forward from the 2026-08-11 template. Still binding. Arithmetic, not judgement. -->

```
Roster resolution: N named on page · N Tier-1/2 identified · N published · N unpublished · N submitted · N resolved · N held · N queried-null · N deferred
```

> **Three identities. All three must hold or the card is INVALID:**
> **1 · `identified` = `published` + `unpublished`**
> **2 · `unpublished` = `submitted` + `deferred`**
> **3 · `submitted` = `resolved` + `held` + `queried-null`**

**`named on page` is a RAW HEADCOUNT** — the denominator, so `2 of 36` looks wrong at a glance where
`2 of 3` does not. 🔴 **Unreadable directory → write it `36+`**, card the org
`BLOCKED — DIRECTORY NOT MACHINE-READABLE`, and count it toward `B` in the report.

### 🔴 THE THREE STATES — required wording for anyone NOT on the thread

**`identified, address unknown` is banned** — it collapses a dead end and an unasked question into
one phrase. Use one of these verbatim in the evidence position:

| Situation | Write it as |
|---|---|
| We have the address, chose not to use it | `📄 PUBLISHED — not on this thread ({{reason}})` |
| Looked up, nothing came back | `🔍 VENDOR QUERIED — no match ({{N}} credits, {{date}})` |
| Never looked up | `⛔ NOT QUERIED — reason: {{reason}}` |
| Never looked up, no reason given | **CARD INVALID** |

🔴 **"Enough recipients already" is not a reason.**

---

# H1 — 2 · FOLLOW-UPS

<!-- Follow-ups are a TABLE, not cards. Every recipient has already been delivered to once; they do
     not need an evidence column. Recipients are fixed at Email 1 (R5) — if anything changed, that
     is a 🔴 line, not a quiet edit. -->

```markdown
# 2 · FOLLOW-UPS — Email 2 × {{N_E2}} and Email 3 × {{N_E3}}

**Every recipient below has already been delivered to once.** Recipients are fixed at Email 1 (R5);
{{nothing was added or dropped | name every change and why}}.

## Email 2 — Email 1 went {{YYYY-MM-DD}}, +7 days lands today

| # | Org | ST | To | Cc | Greeting | Thread | Draft |
|---|---|---|---|---|---|---|---|
| {{N}} | {{org}} | {{ST}} | `{{to}}` | `{{cc}}` · `{{cc}}` | `{{greeting}}` | `{{thread}}` | `{{draft}}` |

{{📝 out-of-office notices checked and what was done — §0.14 rule 2: a Cc absence delays nothing,
   a To absence reschedules to return date + 1 working day. State plainly that no To is out, or
   name who is and the new date.}}

## Email 3 — Email 2 went {{YYYY-MM-DD}}, +7 days lands today

```
📎 ATTACHED BY ZAPIER AT CREATION: HST_3PackStarterKit.pdf (7.2 MB)
   verified: list_drafts has:attachment filename:pdf ✅ {{draft ids}}
   🔴 NO ✅ ON THIS LINE = DO NOT SEND — the body promises a gift
```
{{if any Email 3 fell back to the native connector, that row ALSO carries the old block: 📎 ATTACH BEFORE SENDING: HST_3PackStarterKit_email.pdf · _SEND-KIT/3-Classic-Sequence-Email-3/ (2.7 MB)}}

| # | Org | ST | To | Cc | Greeting | Thread | Draft |
|---|---|---|---|---|---|---|---|
| {{N}} | {{…}} | {{…}} | `{{…}}` | `{{…}}` | `{{…}}` | `{{…}}` | `{{…}}` |

{{⚠️ market notes — e.g. live out-of-market sequences finishing under a standing default}}
```

🔴 **Every Email 3 card carries the attachment line verbatim, with the ✅ written only after the read-back (2026-10-03).** §0.4 E3.1. The gate is a block, not
a sentence — Chris scans for the box.

---

# H2 (optional, inside section 2) — ## Scheduled follow-ups — the machine sends these today at 8:30 local

<!-- 🆕 2026-10-04, method §0.16. Printed ONLY when config.followup_sender.enabled_emails is non-empty OR
     the shadow line has rows. Content = the table `python3 bin/followup_send.py --preview` prints,
     pasted verbatim (Email N · org · state · due · To). Not a REQUIRED heading — dossier_check.py ignores it.
     While enabled_emails is [], head it "## Scheduled follow-ups (shadow) — what the sender WOULD send today". -->

# H1 — 3 · WHAT ELSE HAPPENED

<!-- Facts and events. NOT findings about the machine — those are the review file's job.
     Include a subsection only if it has content; do not print empty ones.
     Standing candidates, in this order: -->

```markdown
# 3 · WHAT ELSE HAPPENED

## {{🎯 revenue / pipeline movement — deals, stage changes, anything that moved money}}
## {{🎯 meetings — held / booked / proposed, with the Fathom or invite evidence}}
## {{Bounces — "none new" is a result and is stated}}
## {{Auto-replies — the count, and explicitly whether any TO recipient is out}}
## {{Sequences closed — X closures falling due}}
## {{Suppression news — a domain newly blocked means a relationship formed. That is news}}
```

🔴 **A meeting is an EVENT, not a verdict.** Report that it happened. **Do not characterise a missing
deal as a gap or a miss without having read the meeting summary and being able to quote a line.**
*(Installed 2026-09-03 — the run called a correctly-absent deal a funnel gap because the shape looked
wrong, with the transcript one tool call away. See [[review-2026-09-03]] §2.10.)*

---

# H1 — 4 · DECISIONS FOR YOU

<!-- 🔴 D-TABLE (§0.2): this table carries ONLY items where CHRIS'S PREFERENCE is the input.
     If a rule already determines the answer, EXECUTE IT and report it in the review file.
     A RULE BREACH IS NEVER A DECISION ITEM. -->

```markdown
# 4 · DECISIONS FOR YOU

| # | Decision | Default taken tonight (reversible) |
|---|---|---|
| **D{{N}}** | {{the question, stated so it can be answered in one word}} | {{what the run did, and how to reverse it}} |
```

**Carry forward every open decision from prior runs with its original number** so Chris can see how
long something has been waiting. An item that has been open 3+ runs says so.

---

# H1 — 5 · STANDING NUMBERS

<!-- 🔴 EVERY LINE HERE IS THE VERBATIM OUTPUT OF A SCRIPT. §0.10: a report figure that did not come
     from a script artifact is a defect. Never retype, never round, never recall. -->

```markdown
# 5 · STANDING NUMBERS

```
Address calibration: {{bin/calibration.py}}
Meetings: {{N}} HELD · {{N}} booked · {{N}} proposed — sources: Fathom / Gmail / HubSpot
Bounce rate: {{bin/bounce_rate.py}}
Outreach floor: {{N}} new organisations drafted · target {{target_drafts}} · {{MET | FAILED + named gate}}
Queue: {{bin/queue_health.py line 1}}
Pace: {{bin/queue_health.py line 2}}
Pipeline: {{$ open}} · {{N of N}} open deals machine-sourced
```

**Sources:** evidence URLs are inline on every card · [[review-{{YYYY-MM-DD}}]] for findings, defects
and rule detail · [[method]] §0.6a and [[dossier-template]] for why this file looks the way it does.
```

---

# WHAT DOES **NOT** GO IN THE DOSSIER

🔴 **The split is the point. Chris opens the dossier under time pressure to SEND.** Anything that
does not change what he does in the next ten minutes belongs in `review-{{date}}.md`:

| Belongs in the REVIEW, never here |
|---|
| Findings about the machine's own defects |
| CAPA analysis, root causes, proposed fixes |
| Rule and config changes made this run |
| The full held-organisation table with reasons |
| Mandated report lines beyond the six standing numbers |
| Vocabulary reviews, regional research notes |
| Manifest accounting, owed items, due-next schedules |

⚠️ **One exception:** a finding that changes whether Chris should send a specific draft gets **one
line** in the READ-THESE table with a pointer to the review section. The analysis still lives there.
