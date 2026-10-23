---
business: Human Skills Training
type: CAPA
title: CAPA — outreach machine drafted copy Chris never wrote or approved
status: CLOSED 2026-08-11 — Transfer-Audit copy retired by Chris; all 15 drafts deleted
created: 2026-08-11
classification: class of bugs
protocol: capa-protocol.md (Toyota / TPS)
related: ["[[method]]", "[[Cold-Outreach-Sequence-CCR&R]]", "[[CCRR-Outreach-Runbook]]", "[[2026-08-11]]", "[[2026-07-22-backlog]]", "[[HST-Wedge-Decision-2026-07-23]]"]
---

# CAPA — the machine wrote its own copy

| | |
|---|---|
| **Problem** | The 10 drafts created 2026-08-11 use body copy Chris never wrote, approved, or tested — plus greetings and a subject-line A/B invented at draft time. |
| **Root cause** | `method.md` supplies the drafter a *topic* and *voice rules* instead of an *approved template file*, so composing copy is the designed behavior, not a deviation. |
| **Corrective** | All 10 drafts pulled out of `CCR&R outreach/Queued` and flagged `HOLD — unapproved copy` in Gmail. None can be sent from the queue by accident. |
| **Preventive** | `method.md` Phase 2 rewritten: body copy must be pasted verbatim from a named approved template; the machine may vary the greeting only, and must stop and report if no template fits. |
| **Verify** | Next run's batch file names a `template_source:` and its body diffs to the named template with greeting-only differences. Fail = any other delta. |

## Decisions for Chris

| Decide | Ask | Time |
|---|---|---|
| What happens to the 10 held drafts | "Delete them" **or** "rewrite to Email 1" | 1 min |
| Which copy the machine is allowed to use | "Only `Cold-Outreach-Sequence-CCR&R`" **or** name another file | 1 min |
| Whether the 5 drafts from 07-22 also get pulled | "Pull them too" **or** "leave them" | 1 min |

**Recommendation:** delete all 10, restrict the machine to `Cold-Outreach-Sequence-CCR&R.md` Email 1, and pull the 07-22 five as well — they carry the same unapproved body. That resets the machine to your tested copy with nothing lost but 19 addresses returning to the queue.

---

## Step 1 — Andon cord

**Symptom.** Ten Gmail drafts to 19 recipients across 10 CCR&R organizations, created 2026-08-11, carrying body copy that did not come from any approved template file. Chris identified it on inspection: *"it looks like you generated these by yourself… When we initially designed this, it was based on the proven email templates I wrote myself and tested. I only want to use those."*

**First detection.** 2026-08-11, by Chris, on visual inspection of Gmail — not by any machine check. There is no check that would have caught it.

**Recurrence.** N=1 as a detected incident, but the same copy was already staged once before (5 drafts, 2026-07-22) and sat unexamined for 20 days. Counting the 07-22 staging, this is the **second** propagation of the same unapproved body — the first went unflagged only because Chris never opened them.

**Containment applied.** New Gmail label `CCR&R outreach/HOLD — unapproved copy` (`Label_5`, red) applied to all ten threads, and `CCR&R outreach/Queued` (`Label_3`) removed from all ten. "Queued" now means "cleared to send" again. **The Gmail connector cannot delete drafts** (runbook §, verified 2026-06-17: ❌ no send, ❌ no delete) — deletion is manual.

## Step 1.5 — IS / IS-NOT

- **IS:** Body copy in all 10 drafts of batch `2026-08-11`; greeting lines in all 10; the 5/5 subject-line A/B split. Also the same body in the 5 drafts of batch `2026-07-22-backlog`.
- **IS-NOT:** The *targeting* is not defective — gating, suppression, org-dedup, ranking and the HubSpot BCC all ran correctly and are unaffected. The *wedge* is not defective — training transfer was genuinely decided by Chris (see Step 2). The recipients are not wrong. No email was sent, so there is no external exposure.
- **When did it start?** 2026-07-22 (copy first staged), hardened into the machine 2026-08-06 (`method.md` created), first propagated at scale 2026-08-11.
- **What changed right before?** The machine was built on 2026-08-06 and *adopted* the 07-22 hand-staged drafts as its prior batch. That adoption silently promoted staged-pending-review copy into the position of "the baseline."

## Step 2 — Genchi Genbutsu: what I read

| File | What it revealed |
|---|---|
| `outreach-machine/method.md` (Phase 2, step 4) | The drafting instruction: *"Read the Active Rules from `outreach-writing-guide.md`… The live wedge is training transfer… Lead with the problem they live."* A topic and a voice — **no template file is named anywhere in the method.** This is an instruction to compose. |
| `outreach-machine/method.md` frontmatter (line 8) | `related:` lists Runbook, Contact-Engine-Spec, outreach-writing-guide. **`Cold-Outreach-Sequence-CCR&R` is absent.** The approved copy is not reachable from the machine's own file. |
| `Cold-Outreach-Sequence-CCR&R.md` (created 2026-04-08, status Active) | The real templates — a 3-email sequence, Chris's voice, with the flyer, the video link, the Starter Kit. Email 1 subject: *"Quick question about PD at {{company}}."* Nothing resembling the transfer-audit body. |
| `CCRR-Outreach-Log.md` line 40 | *"61 unique addresses across 38 organizations, **all sent the full 3-email sequence** pre-v1."* This is the "proven and tested" copy Chris means — n=61 sends. |
| `CCRR-Outreach-Runbook.md` frontmatter | `related:` **does** list `Cold-Outreach-Sequence-CCR&R` first. The runbook knows where the copy lives; the method doesn't. |
| `batches/2026-07-22-backlog.md` | Describes its body as *"Drafted by hand in the 07-22 wedge session, before the machine existed."* "By hand" = "not by the machine" — **not** "by Chris." I read it as Chris's. |
| `Strategy/HST-Wedge-Decision-2026-07-23.md` | Decisive. Footer: *"Prepared by Claude, 2026-07-23."* Body: *"outreach copy drafted (A/B/C variants)"* and *"Five Gmail drafts are sitting in your drafts folder… read, tweak if you like, human-send."* The copy was **Claude-written and staged for review**, never approved. |
| `1.SkillRef/ceo-time/CEO-TIME-STATE.md` lines 22, 87, 391 | *"Chris held a real (partial) strategy session on 07-22 that decided **Binary #1 (the wedge)**."* The **wedge is legitimately ratified.** Only the copy is not. |
| `1.SkillRef/vault-librarian/references/capa-protocol.md` | Protocol + the Chris-facing summary standard used at the top of this file. |
| Gmail `list_drafts` (live, 2026-08-11) | All 15 drafts present and unsent. **Nothing has ever been sent by this machine** — the transfer-audit body has n=0 sends. |

## Step 3a — Candidate root causes

| # | Candidate | Likelihood | Ease | Verify by | Result |
|---|---|---|---|---|---|
| 1 | `method.md` names no copy source, so composing is the designed behavior | **H** | E | Read Phase 2 step 4 + frontmatter | ✅ **Confirmed** |
| 2 | Staged-but-unapproved copy was promoted to "baseline" by being written into a batch file | **H** | E | Read 07-22 batch + wedge memo | ✅ **Confirmed — the mechanism** |
| 3 | The drafter ignored an existing instruction to use the template | M | E | Search method + runbook for a template rule | ❌ **Ruled out** — no such instruction exists in `method.md` |
| 4 | The wedge itself was never ratified, so all downstream copy is unauthorized | M | M | CEO-TIME-STATE Binary #1 | ❌ **Ruled out** — Chris decided the wedge 07-22 |
| 5 | `outreach-writing-guide.md` is calibrated on the wrong genre | M | E | Read its calibration notes | ⚠️ **True but contributory** — all four calibrations (Carla, Colleen, Nicole, Gail) are *collaboration* outreach, not cold CCR&R. Following it cannot reproduce the sequence. |

## Step 3b — 5 Whys

| Level | Question | Answer |
|---|---|---|
| Why 1 | Why did the drafts contain copy Chris didn't write? | The body was carried from the 07-22 batch file, and the greetings and subject A/B were composed at draft time. |
| Why 2 | Why was anything composed at all? | `method.md` Phase 2 step 4 hands the drafter a wedge topic and voice rules. That is a writing brief, not a copy instruction. |
| Why 3 | Why does the method brief instead of supply? | When the machine was built on 08-06 it inherited its body from the previous batch record, so "last batch's body" became the de facto template — and a batch record is an *output*, not an approved asset. |
| Why 4 | Why could an output stand in for an approved asset? | The machine has no concept of approved copy. Copy is modeled purely as something the machine produces and then refines — nothing in the data model distinguishes "Chris wrote and tested this" from "a prior run emitted this." |
| Why 5 | Why was it built that way, and why has nothing caught it? | Because the machine's design assumes it will **converge on** Chris's voice through the learning loop (diff sent-vs-drafted) rather than **start from** it. That loop's only input is a send — and in three runs nothing has ever been sent. **With no send there is no correction signal, so generated copy propagates unchecked and looks more authoritative each time it's written into another batch file.** |

**Classification: CLASS OF BUGS.** Not a one-off drafting slip. Any outreach machine built on this pattern — start from a topic, converge via sends — emits unapproved copy indefinitely whenever sends don't happen. The keynote pipeline (`Cold-Outreach-Sequence-Keynotes.md`, `Conference-Pipeline-Runbook.md`) has the same shape and should be checked.

**Adjacency worth naming:** this is the same failure the vault already guards against elsewhere — *"Silence refreshed the stack; silence did not ratify the positioning. The Night Shift does not get to pick the wedge by default."* That rule exists for CEO-TIME because unratified machine output hardening into fact is a known pattern here. The outreach machine had no equivalent guard.

## Step 4 — Corrective action (Jidoka)

1. ✅ **Containment (done).** All 10 threads labeled `CCR&R outreach/HOLD — unapproved copy`; `Queued` removed from all 10.
2. ✅ **`method.md` Phase 2 rewritten (done)** — see Step 5.
3. ⏸️ **Disposition of the 10 drafts — needs Chris.** Recommend delete (connector cannot delete; manual).
4. ⏸️ **The 07-22 five carry the same body — needs Chris.** Same recommendation.
5. ✅ **`batches/2026-07-22-backlog.md` corrected (done)** — the misleading "drafted by hand" line now states the copy was Claude-drafted and staged for review, citing the wedge memo.

## Step 5 — Preventive action (Poka-Yoke) — **ELIMINATE tier**

Applied to `method.md`, which the scheduled task **reads at runtime** (`method.md` lines 13–14: *"This file is the program. The installed scheduled task is a thin launcher that reads this at runtime"*). This is a verified discoverability hook: every future run loads the rule before drafting. Not a passive reference.

1. **Named copy source, required.** Phase 2 now requires the body be pasted **verbatim** from an approved template file named in the new Approved Copy Register. Only the greeting may vary.
2. **No-compose rule.** *The machine never writes body copy.* If no approved template fits, it stops and reports rather than composing one.
3. **No promotion by side effect.** A batch file's `body_queued` block is explicitly a record, never a template. Copy is promoted only by Chris.
4. **`template_source:` is a required batch field.** A batch that doesn't name its template is invalid on its face.
5. **`Cold-Outreach-Sequence-CCR&R` added to `method.md` frontmatter `related:`** — closing the discoverability gap that started this.
6. **Subject lines are part of the template.** No inventing or A/B-ing subject lines without Chris naming both arms.

## Step 5.5 — Bias check

**Anchoring:** I did not stop at the first cause. The obvious answer was "the drafter went off-script," and Step 3a ruled it out by reading the method — there was no script to go off. **Confirmation:** the evidence that would have changed my mind was whether Chris authored the transfer-audit copy; I went looking specifically for that and found the opposite (`HST-Wedge-Decision-2026-07-23.md` footer, "Prepared by Claude"). **Premature closure:** I nearly filed a materially wrong CAPA — my working theory through Step 2 was that the *wedge* was unratified. CEO-TIME-STATE lines 22/87/391 disproved it. That correction is why candidate #4 is listed and ruled out rather than quietly dropped. **Recurrence blindness:** N=1 detected, but I've counted the 07-22 staging as a prior undetected propagation rather than treating this as fresh, because a fix scoped to "tonight's drafts" would leave the same body in five other drafts.

## Step 6 — Standard work

Proposed registry entry for `1.SkillRef/vault-librarian/references/standard-work-registry.md`:

```
### Approved-copy-only rule for outbound machines
- Trigger: any machine or skill that drafts external-facing email, DMs, or applications on Chris's behalf
- Action: the body must be pasted verbatim from a named, Chris-approved template file. Vary merge
  fields and greeting only. If no approved template fits the case, STOP and report — never compose.
  A prior batch record is never a template.
- Rationale: outreach machines that start from a topic and "converge via the learning loop" emit
  unapproved copy indefinitely whenever sends don't happen — and the learning loop's only input is a send.
- First applied: 2026-08-11, CAPA — outreach machine drafted its own copy
- Reused: 0
```

**Sibling machines to audit against this rule:** the keynote/conference pipeline (`Cold-Outreach-Sequence-Keynotes.md`, `Conference-Pipeline-Runbook.md`, `Conference-Lead-Engine-Spec.md`) — same architecture, not yet checked.

## Step 7 — Verification plan

**Verify date: next weekday run after Chris names the approved template.**

- **PASS:** the batch file names a `template_source:`, and the drafted body diffs against that template with **greeting-only** differences. Subject line matches the template exactly.
- **FAIL:** any other delta — reworded sentence, new subject line, invented CTA, or a missing `template_source` field.
- **A run that drafts nothing is NOT a pass** — that's the instrument not firing. The check requires at least one draft produced against a named template.
- **On FAIL, escalate UP:** do not re-issue the rule. Move to generation-from-file — the drafter reads the template file at runtime and performs a literal string substitution, with no opportunity to compose.
