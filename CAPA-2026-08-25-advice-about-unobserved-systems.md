---
business: Human Skills Training
type: capa
title: CAPA 2026-08-25 — the run gave operational advice about a third-party tool it had never opened
status: DIAGNOSIS ONLY — no rule changed. Proposals listed, none applied.
owner: Chris Danilo
opened: 2026-08-25
trigger: "Chris: 'Let's fix the apollo issue. I don't see any place to stop mailwarming and when I look at the email tab, it has no deliverability metrics for me because it says I haven't sent anything. Use the tech support skill to figure this out and run a CAPA on it.'"
related: ["[[method]]", "[[review-2026-08-25-run2]]", "[[CAPA-2026-08-25-unsourced-brief-fact]]", "[[CAPA-2026-08-13-false-citation]]"]
---

# I told Chris to change a setting without checking whether the setting was findable

🔴 **DIAGNOSIS ONLY.** No rule changed, no config edited, no draft touched.

---

## 1 · The technical answer first, because Chris asked a question and deserves it before the analysis

**Both observations are explained, and neither is a fault.**

### 1a · The warmup control exists. It is one tab away from where Chris was looking.

Chris's URL: `app.apollo.io/#/emails/users/…/mailboxes/69cd8b2618a58a0021b488f5/**deliverability**`

Per Apollo's own documentation ([Manage Mailboxes and Domains on Apollo](https://knowledge.apollo.io/hc/en-us/articles/39530186410125-Manage-Mailboxes-and-Domains-on-Apollo), updated **2026-08-17**), on a mailbox detail page:

> **"11. Click Overview** to view detailed deliverability information, including deliverability score, tracking subdomain, email sending limits, unsubscribe link, and email signature, **or to enable or disable email warmup**.
> **12. Click Deliverability** to view detailed deliverability statistics and reports…"

🔴 **The toggle is on the `Overview` tab. Chris was on the `Deliverability` tab.** Step 11 versus step 12 of the same list.

The second documented route ([Use Email Warmup to Improve Deliverability](https://knowledge.apollo.io/hc/en-us/articles/26772718460045-Use-Email-Warmup-to-Improve-Deliverability), updated **2026-07-29**): *"If you need to stop email warmup, click **…** > **Stop warm up**."* from **Settings → Email setup and health → Mailboxes** — a link that is visible in the bottom-left of Chris's own screenshot.

### 1b · "0 emails delivered" is the correct number, and it is the important finding

Apollo's deliverability suite counts **emails sent through Apollo** — its widgets are *Top performing sequences*, sequence-scoped bounce logs, and open/click tracking that only works *"if you have enabled open tracking or click tracking"* (same article).

**Chris sends none of his outreach through Apollo.** The machine writes Gmail drafts and Chris sends them from Gmail. And warmup traffic does not count either — per Apollo's warmup article, *"it sends system-generated test messages"*, explicitly not sequence mail.

**The arithmetic settles it, and this is his own data, not a document:** roughly **40 warmup + 10 real ≈ 350 messages** left that mailbox during 16–22 Aug. Apollo reports **0**. A dashboard that counted mailbox-level sending could not report 0.

🔴 **THE REAL FINDING, AND IT IS BIGGER THAN THE MISSING BUTTON: Apollo's deliverability suite is structurally blind to 100% of Chris's actual sending.** The tool that *manages* his warmup **cannot observe the thing warmup is supposed to protect.** The feedback loop is not weak, it is absent. His deliverability score will read `N/A` forever under this usage pattern, and that is not a bug to fix — it is a permanent property of using Apollo for warmup while sending from Gmail.

**Consequence that matters:** every deliverability number in that dashboard is unusable for Chris, in both directions. A green score would mean nothing. The `N/A` also means nothing. **Zero of his decisions should be informed by that page.**

### 1c · Two things in the screenshot that ARE worth acting on

| Observation | What it means | Verify how |
|---|---|---|
| **"Configure DKIM, DMARC, and SPF"** with a `Fix` button, 1 of **8** suggestions | ⚠️ **UNRESOLVED.** This may be a real detected gap or a generic always-on card. **I am not asserting his authentication is broken** — the run has never inspected his DNS | **Settings → Email setup and health → Domains.** Apollo's docs: it shows *"how many of each of your domains have authenticated SPF, DKIM, and DMARC records."* That is a verdict; the suggestion card is not |
| **"Inbox Ramp-Up is no longer available. Please use Mailwarming instead."** | Confirms the retirement first-hand. `Adjust ramp up` is greyed for that reason, not because of a fault | — |

🎯 **And an asset the run did not know existed:** Apollo ships a **Blocklist check** (50+ databases) and an **Inbox placement test** (seeds five non-promotional emails per provider *from Chris's own mailbox*). **Both work regardless of whether he ever sends through Apollo**, because Apollo generates the test mail itself. **These measure the actual mailbox, today, for free — no waiting for Postmaster Tools data to accumulate.** Source: the Manage Mailboxes article, *Run Mailbox Diagnostic Test*.

---

## 2 · Root cause of the DEFECT — which is mine, not Apollo's

### 🔴 CAUSE A — The run issued operational advice about a system it had never opened

In the 23:30Z report I told Chris to *"consider dialling Warmbox volume down toward parity"* and *"check Google Postmaster Tools."* Both were framed as actions he could take.

**I had never looked at the tool.** I inferred the entire warmup configuration from **email traffic observed in his Gmail** — 40/day, `wbx` subjects, templated replies — which was sound observation. **But I then recommended changing a setting without establishing that the setting was findable, who owned it, or what its controls were called.** The advice was un-actionable at the moment it was delivered, and Chris hit exactly that wall.

**The general shape:** *the run reads one system (Gmail), infers the behaviour of a second system (Apollo/Warmbox), and issues instructions for operating the second system — with evidence only from the first.*

Compare how this machine treats every other claim. An address needs a URL, a quoted line and a date. A person's employment needs a vendor check. A mailbox's validity needs a validator verdict. **A recommendation to reconfigure a third-party product needs nothing.**

### 🔴 CAUSE B — Source-quality failure, and it is now a PATTERN, not an incident

**Twice in one evening** I stated facts about Apollo sourced from **Mailreach** and **Litemail** — companies that **sell competing warmup products**.

| # | What I said | Source | Truth |
|---|---|---|---|
| 1 | *"Apollo shut down its warmup pool in 2024… no longer offers a real reputation-building layer"* | mailreach.co, litemail.ai — competitors | 🔴 **False.** Apollo's KB, updated 2026-07-29, documents a live feature |
| 2 | *"You're running Warmbox, not an Apollo feature"* | inference from the `wbx` token | 🔴 **Wrong framing.** Apollo runs warmup *through* Warmbox. Chris correctly said he has no Warmbox account |

🔴 **Both were corrected by Chris, not by me.** The second correction only happened because he knew his own account. **Had he not, the error would have stood in the vault as fact.**

**The rule that would have prevented both already exists in his vault, in another skill.** `tech-support` cardinal rule 5:

> **"Manufacturer first, always.** For any specific product, the maker's official manual, support page, and spec sheet are the source of truth. Start there. Community sources (forums, subreddits, YouTube, repair sites) come **only after**, and are clearly labeled as such."

**That rule was written for broken appliances. It is exactly as true for SaaS.** It was not applied because nothing said it applied outside `tech-support`, and the outreach machine never invoked `tech-support` — the skill only fired tonight because **Chris invoked it by name.**

### 🟡 CAUSE C — The run never asked what the tool could see

The 23:30Z report asserted *"roughly 80% of your domain's outbound volume is synthetic."* **That number is sound** — it comes from counting his Sent folder, the one system the run genuinely observed.

**What was never asked is whether any tool could confirm or refute it.** One look at Apollo's dashboard would have produced the far more useful finding in §1b: *the tool managing your warmup cannot see your real mail at all.* **That is a more important thing to tell Chris than the ratio, and it was one click away.**

---

## 3 · What is NOT the cause — ruled out with evidence

| Ruled out | Evidence |
|---|---|
| **Apollo is broken / the button is missing** | Documented at Overview tab and at Settings → Email setup and health. Two routes, both current |
| **Warmup isn't actually running** | ~40 `wbx` messages/day with replies in Chris's Sent folder. Apollo's Mailboxes list has a **Warmup** column (*"active, recommended, or completed"*) that confirms in one glance |
| **Credits ran out and paused it** | Apollo pauses warmup on zero credits. Screenshot shows **3.8K credits** |
| **Wrong mailbox / wrong account** | URL user id `69c43aeff69beb0015928938` matches `apollo_users_api_profile` exactly. Mailbox dropdown shows `<SENDER_EMAIL>` |
| **The 0 is a reporting bug** | It is the correct count of Apollo-originated sends, which is zero |

---

## 4 · PREVENTIVE — proposals, with trade-offs. None applied.

### 🎯 P-1 · Adopt `tech-support`'s source hierarchy as a machine-wide rule. **Recommended first — it is already written.**

> **For any claim about a third-party product's features, behaviour, pricing or configuration:
> the vendor's own documentation is the source of truth. Competitor blogs, "alternatives to X"
> listicles and review sites are COMMUNITY sources — usable, but labelled as such, and never
> the basis of a factual assertion. 🔴 When a source SELLS A COMPETING PRODUCT, say so inline.**

**Why first:** costs one fetch, the rule already exists in his vault, and it would have caught **both** of tonight's errors. The "alternatives to X" genre is structurally adversarial and the run walked into it twice.
Trade-off: none I can find.

### 🎯 P-2 · An advice gate: *"have I opened this?"* **Recommended — this is the structural fix.**

Before recommending any change to a system the run does not control, one of these must be true and stated:

| Basis | Form |
|---|---|
| **Inspected** | I read the vendor's current doc for this control — URL + date |
| **Observed** | I can see the system's output directly (e.g. his Sent folder) — and I say what I did NOT see |
| 🔴 **Neither** | *"I have not looked at <tool>. This is an inference from <what I did observe>. Check <where> before acting."* |

**Applied to the 23:30Z report** it would have read: *"I have not opened Apollo. I'm inferring warmup config from your Sent folder. The control is documented at Settings → Email setup and health."* **Chris would have gone to the right page the first time.**
Trade-off: one sentence per recommendation. That is the whole cost.

### 🟡 P-3 · Prefer measurement the run can actually obtain

Tonight's advice was *"go set up Google Postmaster Tools"* — real, but slow: DNS verification, then days of data accumulation. **Apollo's blocklist check and inbox placement test were sitting in the same product, run from his own mailbox, free, ~30–60 minutes.**
🔴 **General form: when recommending a measurement, prefer one the person can get TODAY over one that requires setup plus a waiting period — and if recommending the slow one, say why the fast one won't do.** Postmaster Tools is still right for the long run; it should not have been the *only* thing offered.
Trade-off: needs the run to know what the tool offers, which is P-2 again.

### ⚪ P-4 · Rejected: have the machine drive third-party UIs itself

Computer-use could open Apollo and read the settings directly. **Rejected for now.** It puts a machine inside a live account holding sending controls, to solve a problem two sentences of honesty solve. **Revisit only if "I can't find the setting" recurs.**

---

## 5 · What would have caught this, ranked by cost

| Cost | Control | Would it have caught it? |
|---|---|---|
| **One fetch** | P-1 — vendor doc first, label competitors | ✅ Both errors, including the one Chris had to correct |
| **One sentence** | P-2 — declare inspected / observed / neither | ✅ The un-actionable advice, and it surfaces §1b's real finding |
| Low | P-3 — prefer obtainable measurement | ⚠️ Improves the advice; doesn't catch the sourcing error |
| High | P-4 — drive the UI | ✅ And disproportionate |

🔴 **Honest summary: Apollo is behaving correctly, Chris's setup is not broken, and the one genuine
problem in this whole thread is that his warmup tool cannot see his email. I missed that not because
it was subtle but because I gave advice about a product I had never opened — and sourced what I did
say from the people who sell against it.**

---

# 🔄 ADDENDUM — Chris opened the page. The answer is better than the question.

**Chris navigated to Settings → Email setup and health → Mailboxes and asked: *"but how can this be?
It's been warming up for months now."***

## 6 · What the page actually shows

| Field | Value | Reading |
|---|---|---|
| Mailboxes **warmed up** | **1 of 1 · 100%** | Warmup is enrolled and running. Confirmed |
| Warmup status | *"Mailbox is continuing to warm up"* + a **`Manage`** link | 🎯 **`Manage` is the control Chris couldn't find.** Also `...` under ACTIONS |
| Mailboxes **completed and ready for use** | 🔴 **0 of 1 · "1 Partial"** | **A SETUP gap, not a warmup gap.** Different card, different thing |
| Setup | **80% Completed** + `See details` | One checklist item outstanding |
| Needs Attention | **0** | ⚠️ **Apollo does NOT classify this as broken.** Incomplete ≠ failing. Do not alarm |
| **Daily limit** | 🔴 **0 / 50** | **Zero sends through Apollo, against a 50/day allowance.** Independent confirmation of §1b |

## 7 · 🔴 THE ANSWER TO "HOW CAN THIS BE" — and it reframes the whole thread

**Two facts, and together they settle it.**

### 7a · Warmup has no finish line. It is a mode, not a task.

Per Apollo's [warmup article](https://knowledge.apollo.io/hc/en-us/articles/26772718460045-Use-Email-Warmup-to-Improve-Deliverability): *"Select a warmup **end date**."* Warmup runs until **that date**, until **credits run out**, or until **you click Stop**. There is no state where the product decides you are warm and stops itself.

**So "months" is not a malfunction — it is the configured end date doing exactly what it was set to do.** The `Manage` panel holds that date, and it is the single observation that closes this question.

### 7b · 🔴 THE REAL FINDING: warmup is a NEW-mailbox remedy, running on an ESTABLISHED mailbox.

Apollo's own framing throughout: *"Running cold email campaigns **without preparing your mailbox** can be risky"* · *"**New mailbox**: If your mailbox has little to no prior sending history…"* · *"**Established mailbox**: If your mailbox has **significant send history**, you typically don't need to pause warmup for minor fluctuations."* **The feature is scoped to mailboxes with no history.**

**`<SENDER_EMAIL>` is not that mailbox.** It carries years of genuine human correspondence — 38 organisations contacted Apr–Jul 2026 before the machine existed, 308 HubSpot contacts, live client relationships (Morgan County Partnership workshops booked for Nov 2026 and Mar 2027), recorded Fathom calls, and real inbound replies. **It has the send history warmup exists to manufacture.**

🎯 **Stated plainly: Chris has been running a remedy for a problem his mailbox does not have, for months, at ~40 synthetic messages a day — and the thing warmup is supposed to unlock, sending through Apollo, has never once happened. `Daily limit 0 / 50`.**

**He has been warming up for a journey he takes in a different vehicle.**

## 8 · What this changes about the earlier advice — a correction to my own correction

In the 23:30Z report I framed the risk as **volume/ratio** — *"80% of your outbound is synthetic, consider dialling toward parity."* **With the page open, that framing is wrong on the numbers:**

- Apollo **recommends max 40/day** and caps at 50. Chris is **at the recommended maximum**, not above it.
- ~40 warmup + ~10 real ≈ **50/day total from one Google Workspace mailbox**, which is an unremarkable volume.

🔴 **Volume was never the problem. FIT is the problem.** The correct objection is not *"that's too much warmup"* — it is ***"warmup is the wrong tool for this mailbox, and it has no exit condition."***

⚠️ **This is the third time in one evening that a confident framing about Apollo needed correcting, and the second time the correction came from Chris looking at his own account.** Cause A of this CAPA — *advice about a system the run never opened* — is not a historical observation. It kept producing wrong answers right up until the page was on screen.

## 9 · The 80% setup gap — flagged, NOT diagnosed

Per [Configure Your Mailbox on Apollo](https://knowledge.apollo.io/hc/en-us/articles/44268354251021-Configure-Your-Mailbox-on-Apollo) the checklist is: **signature · sending limits · unsubscribe link · custom tracking subdomain · authenticated domain (SPF/DKIM/DMARC)**. Five items; 80% ≈ four done, one outstanding.

🔴 **I am NOT asserting which one.** The prior screenshot surfaced *"Configure DKIM, DMARC, and SPF"* as a suggestion, which makes **domain authentication** the leading candidate — but a suggestion card is not a verdict, and `See details` is. **Chris clicks, I don't guess.** Consistent with P-2.

**This item likely matters more than the warmup question.** Authentication is the fundamental that Google's bulk-sender rules actually enforce; warmup is a reputation nudge on top of it.
