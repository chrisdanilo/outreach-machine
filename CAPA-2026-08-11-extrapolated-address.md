---
business: Human Skills Training
type: CAPA
title: CAPA — a pattern-guessed address passed Gate 2 because Apollo made the guess
status: CORRECTIVE APPLIED — one decision pending
created: 2026-08-11
severity: HIGH
classification: class of bugs
protocol: capa-protocol.md (Toyota / TPS)
related: ["[[method]]", "[[verification-log]]", "[[CAPA-2026-08-11-wrong-address-bounce]]"]
---

# CAPA — an inferred address reached a live draft

| | |
|---|---|
| **Problem** | `person0052@org0238.example` was Cc'd on a live draft. Apollo returned it as **`Extrapolated`** — a pattern guess, not an observation. Chris caught it by not finding [Person 0026] on the staff page. |
| **Root cause** | Gate 2 treated every Apollo `email_status` as equivalent. The method forbids *me* inferring an address from a pattern — but says nothing about accepting an inference **made by a vendor**. The prohibition was written against the actor, not the act. |
| **Corrective** | Draft rebuilt to [Person 0111] alone; the version carrying [Person 0026] is trashed. |
| **Preventive** | `email_status` is now a gate, not a note. **`Verified` passes. `Extrapolated` is HOLD** unless independently corroborated by a second source. |
| **Verify** | Next batch: no address with `email_status: Extrapolated` appears on a draft without a second corroborating source named in [[verification-log]]. |

## ✅ Resolution applied — Chris, 2026-08-11: *"Apply the best resolution."*

**[Person 0026] is not emailed at a guessed address, and no separate outreach is invented for her.**
The draft goes to [Person 0111], Program Director, and **the template already does the routing** —
its actual ask is *"I'm reaching out to find the right person to talk to about PD and training."*
[Person 0111] is the person who can name [Person 0026].

**Why this beats the alternatives.** Sending to `amanda@` risks a bounce on a domain we have no
error signal for, and would be the exact behavior this CAPA exists to stop. Phoning is fine but it's
Chris's call and a different channel. **Letting the approved copy do the work costs nothing, risks
nothing, and is what that sentence was written for.**

[Person 0026] is recorded in [[ready-queue]] §C as a Tier 1 known-not-contacted with her direct
line, **(555) 010-0138**, available whenever Chris wants a phone approach.

---

## Step 1 — Andon cord

**Symptom.** Chris reviewed the [Org 0357] draft and could not find [Person 0026] on
`org0238.example`. The draft Cc'd `person0052@org0238.example`.

**Two separate findings, and they are not the same problem.** One is a defect on their website. The
other is a defect in this machine. Only the second is ours.

## Step 1.5 — IS / IS-NOT

- **IS:** The *address* `person0052@org0238.example`, and the gate logic that accepted it.
- **IS-NOT:** Not the person — **[Person 0026] is real, is on the page, and the title is correct.** Not the org, not the copy, not [Person 0111]'s address, which is independently sound.
- **When:** 2026-08-11, waterfall run, ~20:46 UTC.
- **What changed right before:** waterfall enrichment was authorized and run for the first time. It returns a **different mix of statuses** than standard match, and the gate wasn't adjusted for it.

## Step 2 — Genchi Genbutsu: what I read

**Re-fetched the staff page today.** [Person 0026] **is** listed:

> **[Person 0026]**
> Professional Development Coordinator
> (555) 010-0138
> *This email address is being protected from spambots. You need JavaScript enabled to view it.*

**But her entry is malformed.** Every other person on that page is a proper list item. Hers is not —
it's raw text appended to the end of [Person 0003]'s block, outside the list:

```
  * **[Person 0003]**
CCQS Specialist
(555) 010-0139
[protected email]
**[Person 0026]**          <-- no list marker
Professional Development Coordinator
(555) 010-0138
```

In a browser this renders with no bullet, visually merged into the entry above it. **Chris scanning
the page and not seeing a separate person is the expected result of that markup.** He is not
missing anything; the page is broken.

**What the page does NOT provide: any address.** Every email on it is JavaScript-protected. So Gate 1
yielded name + title + phone, and nothing else.

**What Apollo returned** (waterfall, `request_id 4877905933138438115`):

| Person | Address | `email_status_cd` | Confidence | ZeroBounce |
|---|---|---|---|---|
| [Person 0111] | `person0171@org0238.example` | **`Verified`** · source `emailer_message_outbound` | — | valid |
| **[Person 0026]** | `person0052@org0238.example` | 🔴 **`Extrapolated`** | **0.7** | valid |

**`Extrapolated` means Apollo derived it from a pattern** — almost certainly `carolyn@` → `amanda@`.
`Verified` with source `emailer_message_outbound` means Apollo has observed real mail on that
address. **These are categorically different kinds of evidence and the gate treated them the same.**

**ZeroBounce does not rescue it.** `valid` confirms the mailbox accepts mail. It does not confirm
**whose** mailbox it is. On a small nonprofit domain `amanda@` could be a shared alias, a different
Amanda, or a forwarder.

## Step 3a — Candidate root causes

| # | Candidate | Verify by | Result |
|---|---|---|---|
| 1 | Gate 2 doesn't discriminate on `email_status` | Read method Gate 2 | ✅ **Confirmed** — the step says read `email_status`, never says *act* on it |
| 2 | ZeroBounce `valid` was over-read as identity proof | Compare what ZeroBounce asserts | ✅ **Contributing** |
| 3 | Waterfall introduced statuses the gate never anticipated | Compare standard vs waterfall output | ✅ **Contributing** — standard match returned mostly `verified`; waterfall returns a wider mix |
| 4 | [Person 0026] isn't real / not at this org | Re-fetch the staff page | ❌ **Ruled out** — real, listed, title correct |
| 5 | The malformed page caused the bad address | Trace provenance | ❌ **Ruled out.** The address came from Apollo. The page defect is why *Chris* couldn't see her — a coincidence, not a cause |

## Step 3b — 5 Whys

| Level | Question | Answer |
|---|---|---|
| Why 1 | Why was a guessed address on a draft? | Apollo returned `person0052@org0238.example` and the machine accepted it |
| Why 2 | Why was it accepted? | It came back inside a successful Gate 2 result, and Gate 2 passes anything Apollo returns |
| Why 3 | Why doesn't Gate 2 discriminate? | The step says *read* `email_status` and record it — it never says any value should **fail** |
| Why 4 | Why was that omitted? | The rule was written as *"never infer an address from a pattern"* — aimed at **me**. Nobody considered that a vendor would hand back an inference labeled as a result |
| Why 5 | Why does that gap exist at all? | **The verification standard was written about actors, not evidence.** It asks *who produced this?* rather than *what kind of claim is this?* An inference doesn't stop being an inference because a vendor made it — and vendor packaging makes it look like an observation |

**Classification: CLASS OF BUGS.** Every enrichment source returns a mix of observed and inferred
values. Any gate keyed on *source* rather than *evidence type* will keep laundering guesses into
facts. This is the same shape as the bounce: an inference (`person0174@org0174.example` from a
brochure) treated as an observation.

## Step 4 — Corrective action

1. ✅ **Draft rebuilt** — [Person 0111] alone. The [Person 0026] version is trashed. Verified via `list_drafts`, re-labeled.
2. ✅ **[Person 0026] reclassified** in [[verification-log]] from ENROLLABLE to `HOLD — extrapolated`.
3. ⏸️ **[Person 0591] was also `Extrapolated` 0.7** — but `person1137@org0389.example` **matches the live staff page character for character**. That is independent corroboration, so it stands. **This is the distinction the new rule turns on.**

## Step 5 — Preventive action — ELIMINATE tier

**`email_status` becomes a gate, not a note:**

| Apollo status | Result |
|---|---|
| `Verified` | ✅ Passes Gate 2 |
| **`Extrapolated`** | 🔴 **HOLD** — unless a second independent source shows the same address. A live staff page counts. A pattern that "looks right" does not |
| `Unavailable` / null | 🔴 HOLD |

**And a broader rule, which is the real fix:**

> **Judge the evidence, not the source.** Ask *what kind of claim is this* — observed or inferred —
> before asking who made it. A vendor's inference is still an inference. This applies to Apollo,
> ZeroBounce, HubSpot, LinkedIn, and any tool added later.

**ZeroBounce is correctly scoped:** it validates that a **mailbox exists**, never that it belongs to
a named person. It can promote confidence in deliverability. It can never satisfy identity.

## Step 5.5 — Bias check

**Anchoring:** the obvious story was "the person doesn't exist." Re-fetching killed it — she does,
and the page is just broken. **Confirmation:** I went looking for evidence the address *was* sound
(ZeroBounce `valid`) and had to reason past it — valid mailbox, unproven owner. **Premature
closure:** stopping at Why 3 would have produced "check `email_status`," which is true but narrow.
Why 5 is the one that generalizes. **Recurrence:** this is the second inference-treated-as-fact
incident today; the preventive is written against the class, not the field.

## Step 6 — Standard work

```
### Judge the evidence, not the source
- Trigger: any fact entering the pipeline from an external tool — address, title, employment, validation
- Action: classify it as OBSERVED or INFERRED before use. Inferred values HOLD until a second
  independent source corroborates. Vendor packaging does not convert an inference into an observation.
- Rationale: "never infer an address from a pattern" was written against Claude; Apollo made the
  same inference, labeled it Extrapolated, and it passed straight through to a live draft.
- First applied: 2026-08-11, CAPA — extrapolated address
```

## Step 7 — Verification

**PASS:** no `Extrapolated` address appears on a draft without a named corroborating source.
**FAIL:** any inferred value used as if observed — even one that turns out to be correct. **The
defect is the reasoning, not the outcome.**
