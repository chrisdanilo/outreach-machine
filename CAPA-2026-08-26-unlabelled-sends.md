---
business: Human Skills Training
type: capa
title: "CAPA 2026-08-26 — 20 sends went out unlabelled, and the query meant to catch that returns zero"
status: open
owner: Chris Danilo
raised_by: Chris (spotted the missing tag in the Gmail sent list)
related: ["[[method]]", "[[sequence-tracker]]", "[[CAPA-2026-08-26-u8-plaintext-template]]", "[[CAPA-2026-08-20-unreconciled-run-manifest]]"]
---

# CAPA — the label was an obligation, the run skipped it, and no control could have noticed

**Chris spotted it by eye in the Gmail sent list. Two independent faults, both silent.**

---

## 1 · The obligation was NOT missing. The run failed to execute it.

**[[method]] line 1792, Phase 3 draft procedure, step 8 — verbatim:**

> **8. Label the thread `CCR&R outreach` (`Label_2`). One label, drafts and sent alike — state lives
> in [[sequence-tracker]], and Gmail's own `in:draft`/`in:sent` separates the rest.**

**The run labelled nothing.** Twenty drafts created, twenty sent, zero labelled.

## 2 · Why it was missed — §0 SHADOWED the step

**§0.3 step 14 states the whole new-org procedure as a serial chain:**

> `dedup_check.py` → suppression re-check → roster sweep → reverse lookup → rank per R4 → card →
> §0.4 pre-flight → **draft**

**The chain ends at "draft." Labelling is not in it. §0.4's pre-flight carries 17 assertions and not
one of them is "this draft is labelled."** The run executed §0's chain and treated it as complete.

🔴 **§0's own CONFLICT RULE already anticipated exactly this and it still did not save us:**

> *"If §0 is SILENT, the archive binds. **§0 is a program, not a summary — silence is not permission.**"*

**§0 is silent on labelling. The archive therefore binds. The run was obliged and did not comply.**
**The rule was correct, sitting in the file, and load-bearing — and nothing made it fire.**

## 3 · Why P7 did not catch it — this is a NEW failure mode

**The 2026-08-24 change record asserts, under P7:**

> **"DELETED OBLIGATIONS: ZERO. This pass was purely ADDITIVE."**

🔴 **That claim is TRUE.** Phase 3 step 8 is still at line 1792, word for word. Nothing was deleted.

**But the obligation was ORPHANED ANYWAY — by a shadow.** §0.3 step 14 is a *shorter, later,
more authoritative-looking restatement of the same procedure that omits a step.* A reader who follows
the newest, most explicit, most program-shaped instruction gets an incomplete procedure and no signal
that it is incomplete.

> **P7 asks "what did we REMOVE?" It never asks "what did we RESTATE INCOMPLETELY?"**
> **A redundant copy that survives is not protection if the new copy is the one that gets executed.**

## 4 · The label is not cosmetic — two program steps depend on it

**The mailbox holds 6,373 `Apollo Mailwarming` messages against 150 `CCR&R outreach` messages.**
**The label is the only cheap discriminator between the machine's work and 4,704 threads of warm-up noise.**

| Step | Specified as | Effect of an unlabelled send |
|---|---|---|
| **R14 sent sweep** ([[method]] lines 926, 3076) | `in:sent label:Label_2 newer_than:3d` | **The send is invisible. The ledger reconciles clean against nothing** |
| **Orphan recovery** ([[method]] line 2347) | *"`list_drafts` → every thread carrying `CCR&R outreach`"* | **The orphan is invisible** |

**Tonight's 20 sends would have been invisible to tomorrow's R14 sweep.** Tonight's 20 drafts were
invisible to a label-scoped orphan check — **the run got the right answer only because D-SWEEP forced
`list_drafts` UNFILTERED.** D-SWEEP covered for a defect it was not written to cover.

## 5 · 🔴 SECOND DEFECT, found while fixing the first — the specified query returns ZERO

**Tested this session, both forms, same mailbox, same moment:**

| Query | Result |
|---|---|
| `label:Label_2` — **the ID form, what [[method]] specifies in both places** | 🔴 **`{}` — zero threads, no error** |
| `label:"CCR&R outreach"` — the display-name form | ✅ **works, returns the labelled threads** |

**The connector's own tool documentation states the opposite:** *"`label:` — Under a specific label.
**The tool accepts label IDs, not display names.**"* **That is wrong for the search operator.**

🔴 **THERE ARE TWO VOCABULARIES AND THEY ARE INVERTED:**

| Direction | Tool | Takes |
|---|---|---|
| **WRITE** | `label_thread` · `label_message` | the **ID** — `["Label_2"]` |
| **READ** | `search_threads` query | the **display NAME** — `label:"CCR&R outreach"` |

**So even with perfect labelling, R14's specified sweep would still have returned zero.**
**Two independent faults, pointing the same way, each sufficient alone to hide every send.**

⚠️ **Also observed: `resultCountEstimate` is unreliable.** The working query reported `201` against a
label carrying **84 threads**. **Never use the estimate as a count.**

## 6 · The third silent zero in two days

| Date | Zero | Caught by |
|---|---|---|
| Every run | Suppression delta returns 0/0/0 | ✅ A **control query** — the only reason it is trusted |
| **2026-08-26 am** | `ledger_reconcile.py` returned clean 0/0 on **five stale rows** | Chance — the rows were read by eye |
| **2026-08-26 pm** | `label:Label_2` returns 0 threads | Chris's eye |

🔴 **The suppression file solved this problem months ago and the solution was never generalised.**
**Only one sweep in this machine proves its own filter.**

---

# REMEDIATION — DONE

**30 threads labelled at THREAD level** (`label_thread`, not `label_message`).
**`CCR&R outreach` went from 122 messages / 74 threads → 150 messages / 84 threads: +28 messages, +10 threads.**

| Set | N | State before |
|---|---|---|
| Tonight's new-org Email 1 threads | 10 | **no label at all** |
| Tonight's follow-up threads (E2/E3) | 10 | E1 labelled, tonight's message bare |
| This morning's scheduled Email 1 threads | 10 | E1 labelled at message level; replies would not inherit |

🎯 **THREAD level was chosen deliberately, and the evidence is in the mailbox.** `label_thread`
applies to *"all messages currently in the thread **and any future messages added to it**."*
**Message-level labelling is why Suffolk, [Org 0985], Schoharie, ICP Oswego and CCS CNY each show a
labelled Email 1 and a bare Email 2 and Email 3.** Thread-level ends that drift permanently and
catches inbound replies too — the [Org 0188] reply was itself unlabelled until now.

**Shape test recorded per the standing rule** (`labelIds` flipped array→scalar→array in August):
**array form `["Label_2"]` WORKS as at 2026-08-26.**

---

# CORRECTIVE ACTIONS — proposed. Chris rules on C1–C5.

| # | Control | Why it is countable |
|---|---|---|
| **C1** | 🔴 **Add labelling to §0.3 step 14** — the chain becomes `… → §0.4 pre-flight → draft → LABEL THE THREAD`. **And add pre-flight assertion `U11: thread carries Label_2`** | A draft either has the label or it does not |
| **C2** | 🔴 **Correct [[method]] lines 926, 3076 and 2347 to the display-name form** `label:"CCR&R outreach"`, and record the write-ID / read-NAME split beside them | One grep proves it |
| **C3** | **Always `label_thread`, never `label_message`** — the label must survive the whole sequence and catch replies | Sequence stages are countable per thread |
| **C4** | 🆕 **THE SHADOW RULE — the gap P7 leaves open.** *Any compressed restatement of a procedure must be complete, or must name what it omits and point at the full version.* §0.3's steps should each carry a pointer to their archive procedure | A diff of step-vs-procedure is mechanical |
| **C5** | 🔴 **NO GATING OR RECONCILING SWEEP MAY REPORT A ZERO IT HAS NOT PROVED.** Generalise [[hubspot-suppression]]'s control-query discipline to R14, orphan recovery and the bounce sweep: **run one query you KNOW returns rows, in the same session, before trusting a zero** | The control's row count is the proof |

🔴 **C5 is the one that generalises.** C1–C4 fix this defect. **C5 fixes the class** — and this is
the third instance in two days.
