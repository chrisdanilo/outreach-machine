---
business: Human Skills Training
type: capa
title: "CAPA 2026-08-26 — the HubSpot BCC 'issue' was raised five times after it was already answered"
status: CLOSED — Chris ruled 2026-08-26; item resolved everywhere, preventive rules below
owner: Chris Danilo
opened: 2026-08-26
trigger: "Chris: 'The Hubspot BCC issue is not an issue. Drop it or mark it resolved. The browser extension is working as designed. You've brought this up multiple times since the resolution so run a CAPA on why you keep bringing up this non-issue.'"
related: ["[[STATE]]", "[[OPEN-ITEMS-2026-08-24]]", "[[REVIEW-2026-08-25-second-opinion-alignment]]", "[[IMPLEMENTATION-PLAN-2026-08-25-v2]]"]
---

# What happened, in plain terms

Chris ruled on 2026-08-18 that the machine should put no HubSpot BCC on drafts, because his browser
extension already syncs his sends to HubSpot automatically. That ruling has been in STATE.md the whole
time. The extension adding the BCC at send time is that design WORKING — his sends get logged, which
is the entire point.

Despite that, the review session (me) told Chris the BCC was a problem **five times across two days**:
in the alignment review (Finding 8 + decision table), in the implementation plan (§10, "before 08-31"),
at the close of the Gate 2b turn, at the close of the "what else" turn, and twice in the final punch
list — the last time calling it "overdue."

# Root cause

**I inherited item T4.3 from [[OPEN-ITEMS-2026-08-24]] and treated "open in the docket" as "open in
reality."** The docket framed the extension's behavior as "config drift" (the STATE key says disabled,
the sends carry a BCC). I never reconciled that framing against Chris's own 08-18 ruling sitting in
the same STATE file — which already explains the difference: the KEY governs what the MACHINE does
(no BCC on drafts ✅), and the extension is a separate, intentional layer.

# Contributing factors

1. **I attached a deadline to it** (Email 3's large PDF, "before 08-31"), which made a stale item look
   urgent. I never tested the harm model. Asked plainly — *what breaks if the BCC bounces?* — the
   answer is: nothing. HubSpot misses one logged copy of one email; the extension logs sends anyway.
2. **Each of my summaries copied the previous summary's open-items list.** This is the exact failure
   this machine's own CAPAs keep documenting — *a figure carried forward instead of recounted* — in
   list form. An open-items list is also a number someone stopped counting.
3. **I told Chris five times and never asked him once.** One question ("is this actually a problem?")
   would have killed it on day one.

# Corrective — applied now

| Where | Action |
|---|---|
| [[STATE]] `hubspot_bcc` row | ✅ RESOLVED marker added with Chris's 2026-08-26 ruling |
| [[OPEN-ITEMS-2026-08-24]] T4.3 | ✅ Closed with the ruling |
| Alignment review, implementation plan, outreach report | Left as-is — they are dated snapshots; this CAPA is the record that their BCC flags are void |

# Preventive — binding on this session and future review sessions

1. **Never copy an open-items list forward.** Before repeating any item to Chris, re-verify it against
   the standing rulings in STATE — a docket entry is a claim, not a fact.
2. **Any item raised to Chris more than twice must answer, in one plain sentence, "what breaks if we
   ignore this?"** No concrete answer → drop it.
3. **When Chris rules, the item dies everywhere the same day** — marked resolved at its source, never
   re-listed. (Now also in persistent preferences.)
4. **Plain-language reporting** (Chris's directive, same day — and the same directive he gave the
   machine on 2026-08-12): no internal term in a status report without a one-line plain explanation of
   what it is and whether anything is actually wrong.
