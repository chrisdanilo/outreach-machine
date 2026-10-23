---
business: Human Skills Training
type: rationale
title: Method — rationale and incident history
status: active
owner: Chris Danilo
created: 2026-08-18
note: "The WHY behind the rules in method.md. The nightly run does NOT need this file. Read it when a rule looks wrong, when proposing a change, or when writing a CAPA."
related: ["[[method]]"]
---

# Method — rationale and incident history

**[[method]] says what to do. This file says why.** Split out 2026-08-18 so the nightly run stops
paying to load justification it does not act on. **If a rule here disagrees with [[method]], the
method wins** — this file is explanation, never instruction.

---

## Why the Gmail multi-recipient limit is a REGRESSION, not a long-standing limit

### 🔴 THIS IS A REGRESSION, NOT A LONG-STANDING LIMIT — the machine could do this yesterday

**The array form is how every batch before 2026-08-18 was built, and it supported multiple Cc
addresses.** Proof from the record: the 2026-08-17 [Org 0548] send carries
`ccRecipients: ["person1000@org0323.example","person0936@org0323.example"]` — **two Cc addresses, machine-created,
not added by Chris.** The 08-14 [Org 0546] send carries three.

**The change happened mid-session on 2026-08-18.** Arrays worked at 09:05–09:06 UTC (eight follow-up
drafts created with `to: [...]`, `cc: [...]`, `bcc: [...]`). By roughly 09:20 the same forms were
rejected. **The connector was updated underneath a running session.**

**Exhaustively re-tested 2026-08-18 21:31 UTC after the batch was drafted. Every one of these FAILS:**

| Attempt | Result |
|---|---|
| `cc: ["a@x.org","b@x.org"]` — the old working form | 🔴 Invalid email address |
| `cc: "a@x.org, b@x.org"` | 🔴 Invalid email address |
| `cc: "a@x.org,b@x.org"` | 🔴 Invalid email address |
| `cc: "a@x.org; b@x.org"` | 🔴 Invalid email address |
| `cc: "a@x.org\nb@x.org"` | 🔴 Invalid email address |
| `cc: "Name One <a@x.org>, Name Two <b@x.org>"` (RFC display-name form) | 🔴 Invalid email address |
| `ccRecipients: [...]` (the response-shape field name) | 🔴 Tool execution failed |
| `update_draft` with a second address, hoping to append | 🔴 **REPLACES, does not append.** Verified on a probe: cc went from `probe2` to `probe3`, not to both |

**Conclusion: there is currently NO syntax that puts two addresses in one field.** The connector
validates each recipient field as exactly one address.

**🔴 OPERATIONAL CONSEQUENCE — the recipient cap is now 1 To + 1 Cc, not 1 To + 2 Cc.**
Until the connector is fixed or changes again:

- **Draft with the single highest-value Cc**, chosen by the tier order in [[recipient-profile]].
- **Name the second Cc on the dossier card as "add at review"** with its address, so Chris can paste
  it in two seconds. **The greeting still names all three people**, because Chris restores the third
  recipient at review — this is the same shape as the human-added recipients he restored on 08-18.
- **Re-test this every few weeks** per the capability-claims rule below. A connector that changed
  shape once can change back.


---

## Why it's built this way

**Why two gates.** Provenance proves the person; Apollo proves the mailbox. On 2026-08-11 an address
that passed neither was rated HIGH and hard-bounced. The 07-22 sweep loaded 94 contacts with *"No
enrichment (creation free)"* — Gate 2 skipped operationally — and the 08-11 CAPA then deleted it
from the design. Both had to be restored.

**Why verification lives in discovery.** It's the only phase with a fetch budget, and the queue
exists so research happens before a row is queued. Finding a missing person while a draft is being
written is too late to change who it goes to.

**Why the machine never writes copy.** The copy is proven. Machine variation dilutes a known result
with an unknown one, and the drift is silent — each generated body looks more authoritative once
it's in a batch file.

**Why learning reports instead of applying.** An automatic rewrite loop is what turned a template
engine into a copywriter.


---


---

## Why the 2026-08-18 CAPA produced counts instead of rules

**The observation that drove the design.** Sort this machine's rules by whether they actually fire:

| Fires reliably | Has failed to fire |
|---|---|
| Gate 1 / Gate 2 | *"Tier on role, not title"* — raised 5× over 5 days before it was applied |
| *"Never assume a pronoun"* | *"Spend the lookup when unpublished"* — fired for 2 of 9 eligible people **on the day it was ratified** |
| `email_status` as a gate | *"Never skip a tier to avoid work"* |
| *"No entry in the verification log, no send"* | *"Everyone who qualifies but doesn't fit goes in the dossier"* |

**The split is not importance, clarity, or how emphatically the rule is written.** Several of the
failed ones are in bold with a 🔴. The split is structural:

> **A rule fires reliably when it is attached to a countable object and blocks an artefact from
> existing. A rule fails when it is a judgement with no object.**

*"Spend the lookup"* has no *for whom*. *"Never skip a tier"* has no *versus what*. Both can be
satisfied by doing the thing once, which is exactly what happened at [Org 0539] — one lookup
spent, eight candidates, rule technically honoured, org reached badly.

**So the CAPA's controls are counts and gates, not guidance.** The roster resolution line
(`unpublished = submitted + deferred`) is arithmetic that cannot be written without having done the
work, and a card that fails it is invalid on its face. That is why it is the load-bearing control
rather than the roster sweep itself: **P1 tells the run what to do; P2 makes it impossible to have
not done it and still produce a valid artefact.**

### 🔵 DEFERRED, deliberately — the method.md size problem

`method.md` is ~80 KB, and the run-efficiency note already records that long runs degrade because
setup consumes most of the useful context. **A rule raised five separate times without being applied
is not a discipline problem; it is a document that exceeds what the run can hold.** The fix is to
move incident narratives and worked examples out of `method.md` into this file, leaving `method.md`
as gates, schemas and phase order.

**Not done now, and the reason is the test.** The next run is the effectiveness check for the four
CAPA controls. Refactoring the document in the same run would change two variables at once and make
a failure uninterpretable. **Queued for after the 2026-08-25 effectiveness window closes.**
