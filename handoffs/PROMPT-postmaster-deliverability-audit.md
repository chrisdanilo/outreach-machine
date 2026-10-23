---
business: Human Skills Training
type: session-handoff-prompt
title: Google Postmaster Tools + sender-reputation audit for chrisdanilo.com
created: 2026-08-25
owner: Chris Danilo
purpose: "Paste the block below into a NEW Cowork session. Self-contained — it assumes no memory of tonight's run."
---

# How to use this

Open a **new** Cowork session and paste everything between the lines. It is written to stand alone.
Nothing in it requires the outreach machine's context.

---

## PASTE FROM HERE

I need help auditing and fixing the sender reputation of my sending domain, **chrisdanilo.com**.
I am not a developer. Translate anything technical into plain language, and when you need me to
click something, tell me exactly where to click.

### My situation, so you don't have to ask

- I send **cold outreach** from `<SENDER_EMAIL>` — about **10 real emails per working day**
  to [Org 0272] & referral agencies and early-childhood nonprofits across the US. These
  are researched, individually addressed, 1 To + up to 2 Cc, no BCC, three emails a week apart,
  and I stop the moment anyone replies.
- I ALSO have **Apollo.io's Email Warmup** running on the same mailbox. Apollo runs it through a
  third-party provider called **Warmbox.ai** — Apollo's own help doc says so. It sends roughly
  **40 automated messages per day** to a private network of seed inboxes, which open and reply to
  them. Every one carries **`wbx`** in the subject line. So **roughly 80% of my domain's outbound
  volume is synthetic warmup traffic and 20% is real outreach.**
- My hard-bounce rate on the real outreach is **1.49%** (1 bounce in 67 sends since 2026-08-18).
  My own ceiling is 3%.
- I use Gmail / Google Workspace.
- I have **no idea** what my actual spam-complaint rate or domain reputation is. I have never
  opened Google Postmaster Tools.

### What I want out of this session, in priority order

**1. Get me actually looking at my own data.**
Walk me through setting up **Google Postmaster Tools** for `chrisdanilo.com` end to end — including
the DNS TXT verification step, which is the part I expect to get stuck on. Tell me exactly what
record to add and where. Then tell me what each dashboard means in plain language:
Domain Reputation, IP Reputation, Spam Rate, Feedback Loop, Authentication (SPF/DKIM/DMARC),
Encryption, and Delivery Errors.
⚠️ **Check first whether Google has changed or replaced Postmaster Tools** — search before you
explain, don't answer from memory. If there is a newer version or a successor product, use that.

**2. Tell me the numbers that matter and where mine need to be.**
Specifically: Google's published **spam-rate threshold** for bulk senders, what counts as a "bulk
sender" and whether I qualify at ~50 total emails/day, and what domain reputation rating I should
be aiming for. Cite the official Google source with a URL for each number.

**3. Settle the warmup question with evidence, not vibes.**
This is the real reason I'm here. I want a clear answer to:
   a. Is running ~40/day of synthetic warmup traffic alongside ~10/day of real cold outreach
      **helping me, doing nothing, or actively hurting me** in 2026?
   b. **Apollo's own documentation says: "Allow warmup to finish before sending automated or manual
      emails."** I have been ignoring that and sending campaigns concurrently. How much does that
      matter and what specifically goes wrong?
   c. Apollo's warmup has a **configurable end date** — it's designed as a finite ramp, not a
      permanent background process. Should I set an end date, and what should it be?
   d. What ratio of warmup-to-real is sensible? Is 4:1 synthetic-to-real a red flag?
   e. Can Google actually **detect** peer-to-peer warmup networks, and what happens if it does?
      I want to know whether the engagement signals are being **credited, ignored, or penalised**.
   🔴 Be skeptical of your sources here. Most articles about "is Apollo's warmup any good" are
   published by companies that **sell competing warmup tools**. I got burned on this already —
   I was told Apollo discontinued warmup in 2024, which competitor blogs claim and Apollo's own
   help centre contradicts. **Prefer primary sources: Google's own docs, Apollo's own help centre,
   Warmbox's own docs, and email-standards bodies like M3AAWG.** When you cite a vendor blog, say
   so and say what they sell.

**4. Check the fundamentals, since they matter more than warmup.**
Verify my SPF, DKIM and DMARC are correctly configured for `chrisdanilo.com` and tell me if
anything is weak or missing. I am currently receiving **DMARC aggregate reports** at this mailbox
(from `esa1.hc5371-39.iphmx.com` and similar) which suggests DMARC reporting is on — help me
confirm that and actually read what those reports are telling me.

**5. Give me a decision, not a menu.**
End with a short, concrete recommendation: what to change, what to leave alone, and what to
measure in 30 days to know whether it worked. If the honest answer is "your fundamentals are fine,
change nothing, just watch this one number," say that — I would rather hear that than a checklist.

### How I like to work

- Be concise and direct. Lead with the answer, then support it.
- Give me options with trade-offs on judgement calls, and flag things I might be missing.
- **Never fabricate.** Distinguish confirmed facts from assumptions, cite sources with URLs, and
  search before answering anything about the current state of the world. If solid sourced
  information isn't available, say so and tell me where to look instead of filling the gap.
- Don't ask me clarifying questions you can answer by searching. Make a reasonable assumption,
  proceed, and tell me what you assumed.

### 🔴 DO THIS FIRST — a faster measurement exists inside Apollo, use it before Postmaster Tools

Postmaster Tools needs DNS verification and then **days of data** before it says anything. Apollo
already ships two tests that run **from my own mailbox** and return in under an hour, and they work
even though I never send campaigns through Apollo. Walk me through both before anything else:

1. **Blocklist check** — Settings → Email setup and health → Mailboxes → **Run check** beside my
   mailbox. Checks 50+ blocklist databases. Tell me what a `Caution` result means versus `Blocklisted`.
2. **Inbox placement test** — same page → **Run test**. Apollo sends five non-promotional seed emails
   per provider from my mailbox and reports whether they land in **inbox, spam, or promotions**.
   This is the single most direct answer to "is my domain OK right now."

Also check **Settings → Email setup and health → Domains**, which reports whether SPF, DKIM and DMARC
are actually authenticated for `chrisdanilo.com`. Apollo is currently showing me a suggestion card
that says "Configure DKIM, DMARC, and SPF" — **I do not know whether that is a real detected problem
or a generic tip.** The Domains tab is a verdict; the suggestion card is not. Settle it.

**Then** do the Postmaster Tools setup as the long-run monitoring layer.

### 🔴 Context you need about my Apollo setup, because it changes what the numbers mean

**Apollo's deliverability dashboard shows "0 emails delivered" and a deliverability score of `N/A`
for my mailbox. That is CORRECT, not a bug.** Apollo counts only mail sent *through Apollo*. I send
everything from Gmail, and warmup traffic is system-generated and doesn't count either. Roughly 350
messages left that mailbox in a recent week and Apollo reported zero.

🔴 **So Apollo's deliverability score is permanently meaningless for me, in both directions — a good
score would tell me nothing and the `N/A` tells me nothing.** Do not use that number, and tell me if
any other number you find has the same blind spot. **The tool managing my warmup cannot see my real
email.** I want your view on whether that alone is a reason to move warmup somewhere else.

### Things I am NOT asking for

- Don't rewrite my outreach copy — it's approved and settled.
- Don't recommend I switch email providers or buy new domains unless the evidence genuinely
  points there, in which case say so plainly.
- Don't touch my Apollo or Gmail settings yourself. **Tell me what to change and I'll do it.**

## PASTE TO HERE
