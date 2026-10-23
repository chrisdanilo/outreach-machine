---
business: Human Skills Training
type: CAPA
title: CAPA — Apollo credit accounting error (2026-08-12)
status: closed — corrective actions implemented
owner: Chris Danilo
created: 2026-08-12
related: ["[[STATE]]", "[[method]]", "[[verification-log]]"]
---

# CAPA — The credit "discrepancy" that wasn't a loss, it was a made-up number

**Bottom line first: no credits are missing.** Every credit ever spent is accounted for. The
problem was that the machine wrote a wrong balance into its own records and then **invented a
spending category to make the math work**. That invented line is what made it look like there was
a problem.

## What the records said vs. what was true

| Source | Balance | Spend claimed |
|---|---|---|
| STATE.md (written after run 1, Aug 11) | 3,953 remaining | "47 spent: 9 standard match · 17 waterfall · **21 batch overhead**" |
| Apollo's API, checked live before run 2 | **3,974 remaining** | **26 spent: 9 + 17. That's all** |

## The true ledger — every credit, verified against the API

| Date | Action | Credits | Balance after | Verified how |
|---|---|---|---|---|
| — | Starting balance | — | 4,000 | Apollo API |
| Aug 11, run 1 | Matched 9 of 18 contacts (1 credit per successful match, misses are free) | 9 | 3,991 | API before/after |
| Aug 11, run 1 | Waterfall lookup on 9 contacts (the deeper search) | 17 | 3,974 | API before/after |
| Aug 11, run 2 | Matched 20 of 24 NY contacts | 20 | 3,954 | API before/after |
| **Today** | **Live check for this CAPA** | — | **3,954 ✅ matches exactly** | API |

**Total actually spent: 46 credits. Total unaccounted for: zero.**

## Root cause

**A balance number (3,953) was written into STATE.md without checking the API at the moment of
writing.** The documented spends only added to 26, so the leftover 21-credit gap between the wrong
number and the real spends got labeled "batch overhead" — **a category that does not exist in
Apollo's billing.** It was invented to make bad arithmetic look reconciled.

This is the same failure the machine has been fighting all week in a different costume: **writing
down a guess as if it were a checked fact.** A guessed email address hard-bounced on Aug 11. A
guessed balance produced a phantom 21-credit expense the same day. Same disease, different symptom.

**A contributing trap: Apollo's own "credits used" counter is broken or badly lagged.** The API
field `num_lead_credits_used` read **17** both before and after a 20-credit spend, and still reads
17 today when true spend is 46. It appears to only register waterfall charges. *(Source: three live
API reads on Aug 11–12, each returning `num_lead_credits_used: 17` against delta-verified spends.)*
Anyone glancing at that field gets a wrong answer — which invites exactly the kind of "fill in the
gap by guessing" that happened here.

## How it impacts the process

- **Money: no impact.** 3,954 of 4,000 credits remain; the spend rate is tiny (46 credits across
  two active days against a 1,000-per-run cap).
- **Trust in the records: real impact.** A machine that invents a reconciling entry once will do it
  again, and next time the gap might hide a real leak. That's why this gets a CAPA even though no
  credits were lost.

## Corrective actions — implemented today

1. **STATE.md corrected** — balance now reads 3,954 with the true ledger; the "21 batch overhead"
   line is deleted and flagged as having had no basis.
2. **The only valid accounting method is written into the method:** read `num_credits_remaining`
   from the API immediately before and immediately after any spend, in the same run, and record
   both numbers. Spend = the difference. **Never** use `num_lead_credits_used` for anything.
3. **The anti-invention rule, generalized:** if recorded spends don't add up to the balance change,
   the gap is reported as **"UNEXPLAINED — needs investigation,"** never papered over with a named
   category. An honest open question beats a tidy fake answer.

## Preventive check (every run)

The nightly report's credit line must show: balance before → balance after → spend → itemized
causes. If the items don't sum to the spend, the run says so out loud.
