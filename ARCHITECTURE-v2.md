---
business: Human Skills Training
type: architecture
title: "ARCHITECTURE v2 — the outreach machine, rebuilt around closed loops"
status: PROPOSED — supersedes four docs written 2026-08-25, adds none
owner: Chris Danilo
opened: 2026-08-25
supersedes: ["[[ADR-2026-08-25-rebuild-as-deterministic-software]]", "[[PLAN-2026-08-25-deterministic-core]]", "[[REVIEW-2026-08-25-architecture]]", "[[PROPOSAL-2026-08-25-list-building-rp-loop]]"]
related: ["[[method]]", "[[STATE]]", "[[config.json]]"]
---

# The one-sentence diagnosis

**The machine's autonomy is far to the right; its verifier is an LLM counting by hand.**
Everything below follows from closing that gap — **and the test of success is that
`method.md` gets SMALLER.**

---

# 1 · FOUR LAYERS

| Layer | What it is | Authoritative? |
|---|---|---|
| **0 · Substrate** | `config.json` (every number + ruling, Chris edits) · `*.jsonl` (state as data) · `runs/<date>/*.json` (per-run artifacts) | ✅ **Yes** |
| **1 · Run** | Six phases, ordered by irreversibility | — |
| **2 · Loops** | Three, at three timescales | — |
| **3 · Lanes** | **Cold** (exists) and **Warm** (missing) | — |

🔴 **Markdown is GENERATED from layer 0, never authoritative.** Chris keeps readable files; the
machine gets parseable ones; they cannot drift because one is derived from the other.

---

# 2 · THE RUN — six phases, ordered by what they can destroy

| Phase | Does | Reversible? |
|---|---|---|
| **1 GATHER** | Every API read → `runs/<date>/raw/` | ✅ fully |
| **2 COMPUTE** | Every number, from files only | ✅ fully |
| **3 GATE** | Reads artifacts, emits GO/NO-GO per lane | ✅ fully |
| **4 ACT** | Creates drafts | ⚠️ a draft deletes; a send does not |
| **5 RECORD** | Appends jsonl, generates md, writes the report | ✅ additive |
| **6 ROTATE** | *(mostly disappears — jsonl never rotates)* | 🔴 destructive |

> 🎯 **THE RULE: GATHER and COMPUTE may interleave freely — neither has side effects.
> ACT, RECORD and ROTATE are terminal, ordered, and may never be re-entered.**

**It retro-explains four controls invented separately:** P11 (rotate after the report) · R3 (prefer
the reversible operation) · §0.1 (blast radius beats convenience) · read-binding-instructions-first.
**They were symptoms of never having stated it.**

## The steps

**PHASE 1 — GATHER** *(no computing, no deciding)*
Sent sweep 3d unfiltered · bounce sweep 7d mailbox-wide · auto-reply sweep 60d · draft inventory
unfiltered · suppression delta + control query · meeting sources (Fathom → HubSpot → Calendar) ·
reply scan.

**PHASE 2 — COMPUTE** *(scripts; zero API calls)*
`ledger_reconcile` · `bounce_rate` · `due_schedule` · `queue_health` · `learn_diff` · `rp_detect`
**+ one judgement call: auto-reply A/B/C/D classification (LLM, bounded).**

**PHASE 3 — GATE** *(artifacts only — never a live API)*
Suppression fresh? · rate under ceiling? · breaker clear? · ledger reconciled?
🔴 **Emits GO/NO-GO separately for each lane, each with a named reason.** *(Fixes today's live bug:
§0.3 step 5 says "NO DRAFTING" where steps 4 and 8 correctly carve out follow-ups.)*

**PHASE 4 — ACT**
- **4a Follow-ups** — fully deterministic: inherit as-sent recipients, frozen copy, greeting derived
  from the recipient set.
- **4b New orgs** — the acquisition loop (§3). 🔴 **The old cascade T0 is gone** — "drafts already
  waiting" is now just `needed = aim − waiting`. **T1→T3 survive as the SOURCES `next_candidates()`
  draws from:** `candidates.jsonl` → pool → discovery at the extended caps.
- **4c Warm lane** — hand-off actions (§4).

**PHASE 5 — RECORD** · **PHASE 6 — ROTATE**

---

# 3 · THE THREE LOOPS

## Loop A — Acquisition *(inner; repeats until the FLOOR is met)*

🔴 **The target is DRAFTS OUT, not candidates in.** Ten candidates researched yields fewer than ten
drafts — some hold at validation, some at Gate 1, some have no addressable human. **The loop must
therefore repeat until the floor is met or a named gate stops it.**

| | Value | Meaning |
|---|---|---|
| **Floor** | `target_drafts` = **10** | 🔴 **The run FAILS below this**, absent a named gate. This is the number Chris wants in his outbox |
| **Aim** | `queue_ceiling` = **20** | Where a refill fills to, so one blocked run cannot empty the queue |
| **Trigger** | `waiting < 10` | Refill to 20 |

```
needed = aim − drafts_waiting
pass = 0
while needed > 0 and pass < max_passes and budget_remains:
    batch = next_candidates(needed × yield_factor)     # ordering below
    for each: research (SKIP what is cached and fresh) → rank → validate → pre-flight
    drafted   = those that passed
    needed   -= drafted
    log EVERY outcome with status + reason + retry_after
    if drafted == 0: break("no progress")              # bounded retry
    pass += 1
```

🔴 **Bounded retries, always.** No pass that yields zero repeats — otherwise a dry pool loops
forever at 3am. **A stall exits with a named reason, which is a report line, not a crash.**

### Candidate ordering — cheapest yield first

**1 · `DEFERRED_BUDGET` from previous runs** *(research already paid for — highest yield per credit)*
**2 · `HELD_*` whose `retry_after` has passed** · **3 · Fresh from the pool** · **4 · Discovery** *(T3)*

### 🎯 THE NO-REWORK LEDGER — `candidates.jsonl`, one record per organisation

**A status alone is not enough.** The expensive part is the *research*, not the drafting — so the
record stores **the work itself**, and a retry re-validates rather than re-researches.

```json
{ "org": "...", "domain": "...", "cluster": "TX-workforce-boards",
  "status": "HELD_VALIDATION", "reason": "all 3 candidates returned invalid",
  "retry_after": "2026-11-23", "attempts": 2, "last_worked": "2026-08-25",
  "research": { "named_on_page": 12, "people": [...quoted evidence, titles, URLs...],
                "pages_read": [...], "fetched_at": "2026-08-25" },
  "spent": { "apollo_credits": 4, "validator_calls": 3 } }
```

| Status | Retry when | Why |
|---|---|---|
| `DRAFTED` / `SENT` | 🔴 never — R1 closes the org | — |
| `SUPPRESSED` | 🔴 never | Relationship exists |
| `DEFERRED_BUDGET` | 🎯 **next run, FIRST in queue** | Research is paid for; only the spend ran out |
| `FAILED_FETCH` | next run, bounded | Site was down |
| `HELD_VALIDATION` | +90 days | Mailboxes change |
| `HELD_NO_ADDRESS` | +90 days | Sites change |
| `HELD_BLOCKED_DIRECTORY` | **when an RP finds a route** | 🔴 Event-driven, not time-driven — this is the six-directory backlog |
| `HELD_TIER` | **after the cluster's vocabulary review** | Also event-driven |

🔴 **Two rework rules follow directly:**
1. **Within a run** — pass 2 never re-touches a candidate pass 1 resolved. The status is written the
   moment it is known, not at the end.
2. **Across runs** — a candidate is only re-worked if `retry_after` has passed **or** its blocking
   event has fired. **`last_worked` + `attempts` make a re-work visible in the report.**

### The quality guard — widen the input, never lower the bar

⚠️ **A yield-driven loop creates pressure to descend the tier ladder to hit ten.**
🔴 **When yield is short the correct response is MORE CANDIDATES, never looser gates.** The pre-flight
is unchanged, R4 is unchanged, the roster sweep still precedes any descent.
**The report prints `carded` and `drafted` separately so a thin pass is visible rather than papered over.**

### `yield_factor` is measured, not guessed

⚠️ **We do not yet know the research→draft yield**, and Gate 2b will lower it. **Start at 1.0, record
`carded` and `drafted` every run, and derive the factor after ≥3 runs of data.**
*A threshold picked before the data exists is a fabricated number* — the Night Shift's own rule.

### 🆕 Budget exhaustion is a NAMED GATE

**Added to the §0.8.2 list.** If Apollo or validator budget runs out mid-loop, the run **stops,
marks the remainder `DEFERRED_BUDGET`, and reports it** — it does not FAIL, and it does not lower
the bar to finish. **Tomorrow starts with them, already researched.**

## Loop B — The run *(nightly)*
The six phases. Closed by `preflight.py` and the gate artifacts.

## Loop C — Recurring problems *(across nights)*
**Detection is a script reading counts, not an LLM reading transcripts** — tier-4 descent where the
page named humans · the same blocked asset URL twice · roster identities that don't balance · a
bounce that passed every gate.

🔴 **Rule of three counted PER CLASS PER CLUSTER, never per org.** Three Texas boards at tier 4 is
**one** problem about Texas vocabulary.

**Two closure guards, non-negotiable:** an RP closes only on verified non-recurrence · a verified fix
**replaces** the rule it supersedes rather than sitting beside it.

---

# 4 · THE TWO LANES — and the missing one is the point

| | Cold lane | **Warm lane** |
|---|---|---|
| Trigger | An org in the pool | **A reply** |
| Today | 22 steps, 17 assertions, 13 CAPAs, **283 lines of rules** | 🔴 **2 lines. `stop_on_reply: true`, then nothing** |
| Result | 64 orgs outreached | **9 replies · 4 warm hand-offs unworked · 2 meetings · 0 held** |

🔴 **Four organisations have already named the buyer** — ELC Alachua named the PD owner, ELC Gateway
forwarded to two directors, ELC Palm Beach routed to their PD team, ELC Polk added Chris to a vendor
list. **The machine forgot all four the moment the row flipped to STOPPED.**

**v2 gives the warm lane a queue, an owner and a metric.** Minimum viable: a `warm.jsonl` with one
row per hand-off, a next-action date, and a report line that escalates when it goes stale — the same
forcing function the Night Shift uses so nothing sits gated forever.

⚠️ **And the scoreboard changes.** `Market:` and `National progress:` count **inputs**. v2 reports
**meetings held · proposals · revenue** alongside them. *A system that measures its inputs will
optimise its inputs, which is exactly what happened.*

---

# 5 · THE VERIFIER MAP — who closes each loop

| Decision | Generated by | Verified by | Today | v2 |
|---|---|---|---|---|
| Bounce rate vs ceiling | script | script | ✅ **closed today** | closed |
| Ledger reconciliation | LLM fetch | script | 🔴 open | closed |
| Due-date schedule | LLM | script | 🔴 open | closed |
| Queue slack + pace | — | script | 🔴 **absent** | closed |
| Pre-flight, 17 assertions | LLM draft | `preflight.py` | 🔴 open | **closed** |
| Copy fidelity | frozen template | `learn_diff` | 🔴 open | closed |
| 🆕 **Did the run hit the floor of 10?** | the loop | `queue_health` | 🔴 **absent** | **closed** |
| 🆕 **Was this org already worked?** | — | `candidates.jsonl` | 🔴 **absent — rework is invisible** | **closed** |
| 🆕 Is a held org ready to retry? | — | `retry_after` / blocking event | 🔴 **absent** | closed |
| **Who owns training at this org** | LLM | 🔴 **nothing** | open | **open — correctly** |
| **Is this the right buyer** | LLM | **Chris** | open | open |
| **Send** | Chris | Chris | open | **open — deliberately** |

🎯 **Only the countable half closes. Judgement stays open, and that is the design, not a gap.**
`tier_on_role_not_title` exists *because* keyword matching failed — encoding it would recreate the
defect it was written to fix.

---

# 6 · BUILD ORDER

| # | Do | Why it outranks the next |
|---|---|---|
| **1** | **Warm lane** — queue, owner, metric. Work the four hand-offs | Only change with direct revenue consequence |
| **2** | **Data layer** — `contacted.jsonl` **+ `candidates.jsonl`**, markdown generated from both | Unlocks everything; **kills `archive_rotate.py`, shrinks `ledger_reconcile.py` to ~15 lines, and `candidates.jsonl` is what makes the yield loop possible at all** — without it every pass re-researches |
| **3** | Two live bugs: §0.3 step 5 wording · re-validate `ready-queue` *(last modified 08-12, and §0.8's cascade reads it)* | Both live tonight |
| **4** | `preflight.py`, then the rest — small once #2 lands | Closes the highest-value loop |
| **5** | RP register + `rp_detect.py` | 🔴 **Not before #4.** A register that emits candidates a human must adjudicate is still an open loop — it moves the work, it doesn't close it |

---

# 6b · THE THREE REPORT LINES THE FLOOR NEEDS

```
Floor:  N drafts waiting · floor 10 · aim 20 · MET | MISSED (gate: <named>)
Yield:  N carded → N drafted · N held [by status] · N deferred · passes: N
Rework: N candidates re-touched · N skipped as already-worked · oldest retry_after: <date>
```

🔴 **The third line is the one that proves the no-rework ledger is working.** Without it, silent
re-research looks identical to fresh research — **and costs the same credits.**

---

# 7 · THE FALSIFIABLE PREDICTION

**If this is loop engineering and not framework tourism, the corpus shrinks.**

| | Now | v2 target |
|---|---|---|
| `method.md` | **222 KB** | 🎯 **< 80 KB** |
| §0.4 pre-flight | ~40 lines of prose | **a pointer to `preflight.py`** |
| §0.6 report lines | 18 hand-written lines | **generated from artifacts** |
| Archive-rotation rules (P8–P13) | ~60 lines | 🔴 **deleted — the operation ceases to exist** |

⚠️ **If `method.md` grows instead, we are documenting our way into a bigger machine and should stop.**
**Measure at the end of the first week.**

---

# 8 · IMPLEMENTATION — migrating a machine that runs tonight

🔴 **Constraint that shapes everything: the machine is LIVE.** There is no window to stop and
rebuild. **Every stage must leave a working machine at the end of the night.**
**Strangler pattern: the new layer grows beside the old, and the old stays authoritative until the
new one is PROVEN — not until it is finished.**

## Stage 0 — TONIGHT. Cheap, no dependencies, breaks nothing.

| # | Do | Risk |
|---|---|---|
| **0a** | 🎯 **Warm lane, by hand.** Seed `warm.jsonl` with the four hand-offs (Alachua, Gateway, Palm Beach, Polk), each with a next action and a date. Add one report line that escalates when a row goes stale | **None.** It is a list. **This is the highest-value hour in the whole plan** |
| **0b** | Wire `bounce_rate.py` into Phase 2. Report cites `runs/<date>/bounce_rate.json`, never hand arithmetic. **Add the freshness assertion to §0.4** — artifact missing or not dated today → drafting holds | **Low.** Already built and validated. Worst case it fails loudly and we fall back |
| **0c** | Fix §0.3 step 5: `NO DRAFTING` → **`NO NEW-ORG DRAFTING; follow-ups proceed`** | **None.** A wording bug |
| **0d** | Re-validate [[ready-queue]] *(last modified 08-12)* before §0.8's cascade reads it. Report how many rows survived | **None.** A read |

🎯 **After Stage 0 one loop is fully closed and the warm lane exists. Nothing else has moved.**

## Stage 1 — the data layer, and it VERIFIES ITSELF

🔴 **Do not transcribe by hand. A migration that cannot prove it was lossless is a rewrite.**

1. **`migrate_contacted.py`** parses `contacted.md` → `contacted.jsonl`.
2. **`render_contacted.py`** renders `contacted.jsonl` → markdown.
3. 🎯 **ROUND-TRIP TEST: render the jsonl back and diff against the original.**
   **Empty diff (modulo whitespace) = provably lossless.** A non-empty diff names exactly what was
   dropped, which is the thing a hand migration can never tell you.
4. 🎯 **SECOND, INDEPENDENT CHECK: run `bounce_rate.py` against BOTH.**
   **Same number from both sources = the migration preserved what the machine actually reads.**
   *We already own a verifier for this migration. Use it.*

**Then DUAL-WRITE for 5 runs.** The run appends to **both**; scripts read the jsonl, humans read the
markdown, and the nightly report prints a diff line. 🔴 **The markdown stays authoritative until five
consecutive runs agree.** Only then does it become generated-only.

## Stage 2 — `candidates.jsonl`, seeded not built

**No legacy to migrate — it is new.** But it should be **seeded from knowledge we already have**, and
that seeding is where the immediate value is:

| Seed from | Becomes |
|---|---|
| The six blocked directories | `HELD_BLOCKED_DIRECTORY` + the asset URL + `retry_after: <event>` |
| [[ready-queue]] survivors | researched, not yet drafted |
| [[discovery-pipeline]] pool | fresh candidates |
| Every org already in Ledger A | `SENT` — 🔴 **R1 enforcement becomes a key lookup instead of a prose rule** |

⚠️ **That last row is the quiet win: `one_org_one_thread` stops being a rule someone has to remember
and becomes a `status != null` check.**

## Stage 3 — the yield loop

**Only once `candidates.jsonl` exists** — without it every pass re-researches and the loop is worse
than the level-based refill it replaces. Then: `queue_health.py`, the floor/aim arithmetic, the three
report lines from §6b, and `preflight.py`.

## Stage 4 — measure, then decide

**End of week one, three numbers:**

| Question | Measure |
|---|---|
| Is the floor being hit? | `Floor: MET / MISSED` across 5 runs |
| What is the real yield? | `carded → drafted`, ≥3 runs, **then** set `yield_factor` |
| 🔴 Is the corpus shrinking? | `method.md` bytes, weekly |

**RP register comes after this, not before.** It is the widest autonomy step and it is earned last.

---

## Who does what

| | |
|---|---|
| **Chris** | Sends. Decides. Connects ZeroBounce in Zapier if S4 goes ahead. **Edits `config.json` — every number stays his** |
| **Me** | Fetches, judges, drafts, writes prose. 🔴 **Stops producing numbers** |
| **Scripts** | Every count, every identity, every gate that can be computed |

## Risk register

| Risk | Control |
|---|---|
| Migration silently loses rows | 🎯 **Round-trip diff + independent `bounce_rate.py` cross-check.** Two verifiers, not one |
| A stage half-lands and the 3am run breaks | **Dual-write; old stays authoritative for 5 runs.** Every stage ends with a working machine |
| Scripts disagree with me | 🎯 **That is the point.** Investigate; record which was wrong. *(Score so far: LLM 0, scripts 3.)* |
| The corpus grows anyway | **Weekly byte count. If `method.md` grows, stop and re-plan** |
| The yield loop burns credits chasing ten | **Budget is a named gate. Stop, mark `DEFERRED_BUDGET`, report** |
