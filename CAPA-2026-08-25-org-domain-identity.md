---
business: Human Skills Training
type: capa
title: CAPA 2026-08-25 — an organisation has two domains and nothing records that they are the same organisation
status: DIAGNOSIS ONLY — no rule changed, no config edited. One live risk is unmitigated and named below.
owner: Chris Danilo
opened: 2026-08-25
trigger: "Chris, after the run 2 report: 'Run a CAPA for the org0253.example problem. From that, propose a thoughtful solution.'"
related: ["[[method]]", "[[review-2026-08-25-run2]]", "[[contacted]]", "[[ready-queue]]", "[[CAPA-2026-08-11-wrong-address-bounce]]", "[[CAPA-2026-08-20-unreconciled-run-manifest]]"]
---

# `org0253.example` and `org0251.example` are one organisation, and no file says so

🔴 **DIAGNOSIS ONLY.** Nothing applied. `config.json` is Chris's file and the one change this CAPA
recommends touches a safety-gate denominator, so it is proposed, not made.

🔴 **THERE IS A LIVE, UNMITIGATED RISK RIGHT NOW.** [Org 0462] is sitting in Drafts under
`org0253.example`. Details in §5. It is small, it is real, and it is one line to close.

---

## 1 · What was observed

| Fact | Value | Source |
|---|---|---|
| Website the org publishes | `org0251.example` | `org0253.example` issues a **301 redirect** to it |
| Domain on every human mailbox | `org0253.example` | `person0647@org0253.example`, `person0839@org0253.example`, `person1211@org0253.example`, `person0321@org0253.example` — all read off their own pages |
| Domain Apollo returns as `primary_domain` | `org0251.example` | `apollo_people_bulk_match`, 2026-08-25 |
| Domain the run ledgered under | `org0253.example` | `candidates.jsonl`, this run |
| Domain in [[ready-queue]] | `org0253.example` | ready-queue line 28 and line 192 |
| Domain in `config.json.domain_aliases` | **absent** | Only entry is `org0572.example → org0434.example` |
| Their own site footer | 🔴 a **malformed mailto** whose href is `person0337@org0251.example` — *double p* | Every page. Not used |

**So the organisation presents FOUR distinct strings** — `org0253.example`, `org0251.example`,
`www.org0253.example`, and a typo'd `person0337@org0251.example` — **and the system stores one.**

---

## 2 · This is not new. It is the third instance of the same shape.

| Org | Website | Mail | How it was handled |
|---|---|---|---|
| [Org 0007] | `org0174.example` | `@org0389.example` | Caught by hand. [[ready-queue]] gained a `mail_domain` field *because of it* |
| **ICP Oswego** | `org0434.example` | two recipients `@org0572.example` | Caught **only when `bounce_rate.py` refused to score an unmapped domain**, 2026-08-25. Fixed reactively via `domain_aliases` |
| **[Org 0462]** | `org0251.example` | `@org0253.example` | 🔴 **Not handled. Found by reading, not by a control** |

🔴 **Three instances, three different discovery mechanisms, zero of them systematic.** Five County was
found by a human, ICP Oswego by a script refusing to divide, [Org 0462] by a research
subagent mentioning a redirect in passing. **A defect found three ways and prevented none.**

---

## 3 · Root cause

### 🔴 CAUSE A — Three subsystems key on "the domain" and each means something different by it

| Subsystem | What it needs the domain for | Which domain is correct for it |
|---|---|---|
| **R1** one-org-one-thread | *"has this ORG been contacted?"* | **all of them** — any match must close the org |
| **R11** two-ledger de-dup | *"has this PERSON been emailed?"* | the **mail** domain |
| **Gate 1** provenance | *"is this the org's OWN site?"* | the **website** domain, post-redirect |
| **`bounce_rate.py`** | *"which send does this bounced address belong to?"* | the **mail** domain, mapped back to the org |

**There is no single artefact that says "these strings denote one organisation."** What exists instead:

- `ready-queue.mail_domain` — a **queue** field. 🔴 **Orgs leave the queue when they are drafted.** The
  fact is discarded exactly when the org becomes permanently interesting.
- `config.domain_aliases` — a **1:1 map**, added reactively for a bounce-rate division, documented in
  its own `_why` as being about the rate. It is not presented as an identity register and is not
  consulted by R1 or R11.
- `contacted.jsonl.domains` — 🎯 **already an ARRAY.** Schema-verified this session: every org record
  carries `"domains": [...]`. **The container for the right answer already exists and nothing has ever
  put two values in it.**

### 🔴 CAUSE B — R1's de-dup is a substring search, and a substring search cannot fail loudly

Tonight's R1/R11 check for all seven T2 candidates was, literally, `grep -ci "<domain>" contacted.md
contacted.jsonl hubspot-suppression.md` → `0 hits` → proceed.

**A zero-hit grep is indistinguishable between:**

- *"this organisation has never been contacted"* ✅ — the intended reading, and correct tonight
- *"this organisation has been contacted, under its other domain"* 🔴 — **returns exactly the same zero**

🔴 **This is the Five County failure mode restated.** [[method]] records it: *"Five County, where a
bounced To made a reached org look unreached and nearly re-emailed a Cc recipient nine days later."*
R1 was written to close that door. **R1 keys on a string, so it closes the door only for orgs that
use one string.**

### 🟡 CAUSE C — The redirect direction is the opposite of intuition, so the "obvious" key is wrong

`org0253.example` → 301 → `org0251.example`. **Canonical-URL logic says the redirect TARGET is the
identity**, and Apollo agrees — its `primary_domain` is `org0251.example`. **But every human
mailbox is on the SOURCE domain.** Any rule of the form *"use the canonical host"* picks the domain
that appears in **zero** of this org's email addresses.

---

## 4 · Scope — how bad is it across the book?

Measured this session, not estimated:

```
named orgs in contacted.jsonl:                                    65
orgs whose address-domains fall outside their recorded org domain: 0
orgs with more than one domain recorded:                           0
config.domain_aliases entries:                                     1
```

**Reading, stated carefully:** the ledger is **currently self-consistent** — no org is presently
mis-keyed. **That is not reassurance.** It means every org so far happened to use one domain for both
purposes, **or** used two and only one was ever recorded, in which case the inconsistency is invisible
by construction. **`0 orgs with >1 domain recorded` across 65 orgs is the finding**, not the all-clear:
Five County and ICP Oswego are both known two-domain orgs and neither shows up in that count.

---

## 5 · 🔴 THE LIVE RISK, named precisely

**[Org 0462] is in Drafts tonight, keyed `org0253.example`.** When Chris sends it, that string
enters [[contacted]] Ledger A and the org is R1-CLOSED **under `org0253.example` only**.

**The concrete path to a duplicate cold email:**

1. A future T3 discovery pass runs. Discovery reads CCAoA listings and vendor records.
2. **Apollo returns this org as `org0251.example`** — verified this session.
3. R11 greps `org0251.example` against [[contacted]] → **0 hits**.
4. The org reads as never-contacted. It is researched, carded, and drafted **a second time**.
5. Because it is a *new* thread, `recipients_fixed_at_email_1` and `stop_on_reply` offer no protection —
   they are scoped to a sequence, and this is a fresh one.

**Probability: low but not negligible** — it requires discovery to surface the org under its canonical
host, which is precisely what its canonical host is for. **Consequence if it fires:** Chris cold-emails
an organisation twice, which is the single outcome R1 exists to prevent and which he stated in his own
words: *"I only want to reach out to an org once."*

---

## 6 · PREVENTIVE — proposals, with trade-offs. None applied.

### 🎯 P-1 · Put both domains in the array that already exists. **Recommended first — no schema change.**

`contacted.jsonl.domains` is already `["org0748.example"]`. Make it
`["org0253.example", "org0251.example"]`. **De-dup becomes set intersection instead of substring
search:**

```
R11 passes only if:  set(candidate_domains) ∩ set(all_recorded_domains) == ∅
```

**Why this first:** the field exists, the writer exists, `migrate_contacted.py` already round-trips it,
and it turns a string search into a set operation — **which is the difference between a check that can
be wrong and a check that can be complete.**
Trade-off: `contacted.md` is the authoritative form until 5 clean verify runs, so the markdown table
needs a second domain rendered too. That is a column, not a redesign.

### 🎯 P-2 · Capture both domains at Gate 1, where they are both visible for free

The researcher already fetches the site. Two extra strings, zero extra calls:

| Field | Definition |
|---|---|
| `website_domain` | the host **after** following redirects |
| `mail_domain` | the domain of the published addresses actually harvested |

🔴 **And record them even when they are identical** — because *"these are the same"* is a finding, and
a field that is only populated when interesting is a field nobody trusts. **This is the fix for the
`ready-queue.mail_domain` design flaw: capture it at Gate 1, where it is permanent, not in the queue,
where it evaporates on draft.**
Trade-off: one more line per card. Real, small.

### 🎯 P-3 · Make R11 HOLD on a partial match, not pass

Today a partial match is invisible. Make it loud:

| Candidate state | Action |
|---|---|
| No recorded domain intersects | ✅ proceed — genuinely new |
| **Any** recorded domain intersects | 🔴 **R1-CLOSED.** Only Chris reopens |
| Website matches but mail domain unknown, **or vice versa** | 🔴 **HOLD and say so** — this is the ambiguous case, and it is currently the silent one |

**This is the load-bearing proposal.** P-1 and P-2 supply the data; **P-3 is the only one that changes
what the machine does when the data disagrees.** Trade-off: it will HOLD some orgs that turn out fine.
Per [[method]]'s own asymmetry rule — *"over-blocking is invisible and permanent; a bounce is loud"* —
that trade needs Chris's eyes, which is exactly why this is a proposal.

### 🟡 P-4 · Retire `config.domain_aliases` as a separate concept, or make it derived

Two registers of the same fact will drift; that is what [[method]] P7 is about. **Either** make
`domain_aliases` the single canonical org-identity register **and** have R1/R11 read it, **or** derive
it from `contacted.jsonl.domains` at run time so there is one writer. 🔴 **What must not persist is the
current state: a bounce-rate patch that R1 does not consult, and an array R1 does not consult either.**
Trade-off: `bounce_rate.py` reads `config.json` today; deriving means touching a live gate script.
**Lowest-risk order: P-1 and P-2 first, leave `domain_aliases` alone, revisit once the array is populated.**

### 🟡 P-5 · A countable check, because P7 warns write-obligations get dropped silently

Report line: `Org identity: N orgs · N with both domains recorded · N single-domain · N ambiguous`.
**Single-domain is not an error** — most orgs genuinely have one. **The number to watch is `ambiguous`.**
Trade-off: another report line. Only worth it with P-2.

### ⚪ P-6 · Rejected: resolve the redirect at de-dup time

Fetching each candidate domain to see where it redirects, at check time. **Rejected:** it spends a
network call on every candidate on every run to rediscover a fact that never changes, and it fails
closed in the wrong direction when a site is down. **P-2 captures the same fact once, for free, at the
moment the page is already open.**

---

## 7 · The one thing worth doing tonight, if Chris wants it

**Add `org0253.example ↔ org0251.example` to `config.json.domain_aliases`.**

- **One line.** Closes the §5 path completely for this org.
- **No effect on any number:** [Org 0462] has never been sent to, so it is in no bounce
  denominator. Verified: `grep -c org0253.example contacted.jsonl` → `0`.
- **Not applied** because `config.json` is Chris's file and `domain_aliases` feeds `bounce_rate.py`,
  a live safety gate. **Say the word and it is one line.**

Same question stands for the two known historical cases — **Five County (`org0174.example` ↔
`org0389.example`)** — which has the identical exposure and is already SENT.

---

## 8 · What would have caught this, ranked by cost

| Cost | Control | Would it have caught it? |
|---|---|---|
| **Zero** | P-2 — record both domains at Gate 1 | ✅ Yes, and would have caught Five County and ICP Oswego too |
| **Near-zero** | P-1 — populate the array that already exists | ✅ Yes, at de-dup time |
| Low | P-3 — HOLD on partial match | ✅ Yes, and it is the only one that stops the *send* |
| Low | P-5 — count ambiguous orgs | ⚠️ Surfaces the population; does not stop anything |
| Medium | P-4 — one identity register | ✅ Yes, but it touches a live gate. Not first |
| High | P-6 — resolve redirects at check time | ✅ Yes, and wasteful |

🔴 **The honest summary: nothing is broken today and the ledger is self-consistent. What is missing is
the ability to NOTICE when it stops being — and the system has now met this defect three times without
building that ability once.**
