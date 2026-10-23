---
business: Human Skills Training
type: architecture-decision
title: "ADR 2026-08-25 — should the nightly run be rebuilt as deterministic software rather than a prompt?"
status: "PARTLY EXECUTED 2026-09-26 — Chris chose the Cowork-only path (Option A): scripts + config stay the deterministic core, history via bin/snapshot.py (Git needs delete rights Cowork lacks), regression test via bin/replay.py (20/20 recorded runs reproduce), cluster as a settings block (§0.7.3). The three-layer rebuild and Claude Code hosting remain OPEN; see CHANGELOG.md and BUILD-QUEUE.md"
owner: Chris Danilo
opened: 2026-08-25
trigger: "Chris: 'This is getting pretty technical with lots of steps and we may add more steps as well as dependencies or if/then loops. What would be the pros/cons of rebuilding this as a scheduled task, but with Claude Code as software that runs the same way every time?'"
related: ["[[method]]", "[[STATE]]", "[[CAPA-2026-08-25-empty-new-org-queue]]", "[[CAPA-2026-08-20-unreconciled-run-manifest]]", "[[CAPA-2026-08-20-housekeeping-nonatomic]]", "[[PROPOSAL-2026-08-25-pre-send-deliverability-check]]"]
---

# The finding: this is TWO systems with opposite requirements, currently glued together

**The nightly run does two kinds of work and they want opposite things.**

| | **Deterministic work** | **Judgement work** |
|---|---|---|
| Examples | Counting the bounce rate · set-differencing Sent against the ledger · `sent + 7 = due` · the 17 pre-flight booleans · template assembly (copy is frozen) · the manifest identity · report lines | Reading a staff page and deciding who owns PD/training · R4 tiering on **role** not title · departure vs absence in an auto-reply · which of five people is the wedge buyer · noticing something is *odd* |
| Wants | **The same answer every time** | **Interpretation** |
| Fails by | Being wrong quietly | Being rigid |
| Today done by | 🔴 **an LLM reading prose at 3am** | an LLM — correctly |

🔴 **Every defect in this machine's CAPA history is in the LEFT column.**

| CAPA | What actually went wrong | Column |
|---|---|---|
| [[CAPA-2026-08-20-unreconciled-run-manifest]] | A to-do list nobody counted; 4 obligations dropped silently | **Left** |
| [[CAPA-2026-08-20-housekeeping-nonatomic]] | A splice computed by hand, off by ten lines | **Left** |
| [[CAPA-2026-08-25-empty-new-org-queue]] | Queue arithmetic with one-run latency; a streak nobody totalled | **Left** |
| §4c of the same CAPA | 🔴 **The bounce denominator was ESTIMATED, twice, and gated a safety control** | **Left** |
| [[CAPA-2026-08-18-unqueried-tier1-roster]] | Six identified people never submitted — a count that didn't balance | **Left** |

**Not one of them was a bad judgement call about a person, a page, or a recipient.**
**They were all arithmetic, bookkeeping, or a step that quietly didn't run.**

> 🔴 **Stated plainly, and against my own interest: the LLM is the unreliable component in exactly the
> half a program would do perfectly.** Today alone I published a wrong bounce denominator twice —
> once from a `~140` carried forward, once from a name-join that silently dropped two-thirds of the
> rows. **A `bounce_rate()` function cannot make either mistake.**

---

# PROS of rebuilding the deterministic half as code

| # | Pro | Why it matters HERE, specifically |
|---|---|---|
| **1** | **Same input → same output** | A step cannot quietly stop running. **Phase 6 stopped executing on 2026-08-14 and four runs passed before anyone noticed.** Code either executes or raises |
| **2** | 🎯 **Counting becomes reliable** | Kills the single largest defect class in this file's history, permanently |
| **3** | **The 17 pre-flight assertions become unit tests** | They are *already written as booleans*. §0.4 is a test suite in prose. Porting it is transcription, not design |
| **4** | 🎯 **If/then, dependencies and loops — the thing Chris actually asked about** | The T0→T4 cascade, async waterfall polling with backoff, reserve-promotion on an `invalid` verdict. **Trivial in code. Fragile in prose, and prose is where they live today** |
| **5** | **Cheap and fast** | No ~120 KB context load per run. Seconds, not minutes, and no context-rot on a long run |
| **6** | 🎯 **Testable against history** | **11 completed runs exist with full records.** Replay them; the new code must reproduce them. **A regression suite already exists in data we own** |
| **7** | **P7's "diff of deleted obligations" becomes `git diff`** | Automatic, not a discipline someone has to remember |
| **8** | **The manifest identity is enforced, not recalled** | `obligations == completed + skipped + failed` becomes an assertion, not a habit |

---

# CONS — and two of them are serious

| # | Con | Severity |
|---|---|---|
| **1** | 🔴 **Chris can no longer read the rules.** Today he opens [[method]], reads a rule in English, and rules on it. **His rulings ARE the source of truth for this system.** Python is not readable by him | **HIGH — mitigable** |
| **2** | 🔴 **Code only checks what it was told to check.** Several of today's most valuable findings were an LLM *noticing something odd nobody asked about* — the five-day-stale Five County ledger row, Apollo's `current: true` on a departed recipient, the "no human name attached" pattern. **A program finds none of those** | **HIGH — partially mitigable** |
| **3** | **Porting 220 KB of accumulated rules is the P7 failure at 10× scale** | **HIGH.** The 2026-08-18 compression pass dropped four write-obligations from a *list*. A rewrite into code is that risk, multiplied |
| **4** | **Brittleness at the edges** | Medium. An MCP renames a field; Apollo changes a shape. An LLM adapts, code throws. ⚠️ **Though for a safety-critical run, throwing is arguably the correct behaviour** |
| **5** | **It needs somewhere to run** | Medium. Today it is a Cowork scheduled task on Chris's desktop. Code needs a host, stored credentials and a cron — **new infrastructure and a new 3am failure mode** |
| **6** | **It is a hybrid, not a replacement** | Low, but it kills the "one clean system" appeal. The judgement half still needs an LLM |

## Mitigating Con 1 — keep the rules in English

**Three layers, and the top one stays Chris-editable:**

1. **CONFIG — English/YAML, Chris edits directly.** `target_drafts: 10` · `queue_ceiling: 20` ·
   `max_bounce_rate_pct: 3` · `bounce_rate_baseline: 2026-08-18` · the R4 rank list · the Gate 2b
   verdict rule. **Every number and ruling he has ever made lives here and stays readable.**
2. **CORE — code.** Sweeps, counts, ledger reconciliation, due-date maths, the cascade, the 17
   assertions, report generation.
3. **JUDGEMENT — LLM, narrow and typed.** *"Here is a staff page. Return ranked candidates with
   quoted evidence."* Called BY the core, with a defined contract in and out.

🎯 **And the load-bearing rule: the LLM writes the report's PROSE; the CODE produces every NUMBER in it.**

## Mitigating Con 2 — keep an anomaly pass, and give it no authority

**After the deterministic run completes, hand the LLM the run's outputs and ask one open question:
*"what looks wrong here that no rule checked?"*** Output goes in the report as **observations**,
never as actions. **That is how you keep the noticing without letting it act.**

---

# 🎯 THE CHEAPER 80% — available in days, not weeks

**Most of the damage this machine has done is counting. The counting can be fixed without a rebuild.**

**Four small scripts, called by the existing nightly run:**

| Script | Kills |
|---|---|
| `bounce_rate.py` | 🔴 §4c — the estimated denominator that gated a safety control **twice today** |
| `reconcile_ledger.py` | The Five County *"drafted"* row that was wrong for five days |
| `queue_health.py` | The slack and pace lines — the warning that would have prevented this morning |
| `preflight.py` | The 17 booleans, as real assertions |

**Each is tens of lines. Each replaces a place where I have demonstrably been unreliable. None
requires new infrastructure, a host, or porting a single rule.**

⚠️ **This is not an argument against the rebuild. It is an argument about ORDER** — the highest-value
determinism is available first and cheapest, and it de-risks the bigger decision by showing what
code-plus-config actually feels like to operate.

---

# Migration, if the rebuild goes ahead: SHADOW MODE

🔴 **Do not cut over. Run both and diff them.**

1. Build the deterministic core.
2. **Run it alongside the current machine for a week. It writes nothing and sends nothing.**
3. **Diff the two outputs every night.** Where they disagree, **one of them is wrong — find out which.**
4. Cut over only when they agree, and keep the prose [[method]] as the archive of *why* each rule exists.

**This is the same discipline as the suppression control query** — never accept a result from one
source when a second source is cheap. **And it turns the port's biggest risk (silently dropping a
rule) into a visible nightly diff.**

---

# Recommendation

| | |
|---|---|
| **Do now** | **The four scripts.** Highest-value determinism, days of work, no new infrastructure |
| **Then decide** | Whether the full three-layer rebuild is worth it, **with a week of real evidence about how config-plus-code feels** |
| **If yes** | Three layers, shadow mode, anomaly pass retained with no authority |
| **Never** | Port the judgement half. Page-reading, tiering and wedge-buyer selection stay with an LLM — `tier_on_role_not_title` exists **because keyword matching failed** |

🔴 **Declared bias: this recommends removing my own discretion from the half where I have failed
repeatedly, including twice today. I believe that is correct, and Chris should weigh that I am not a
neutral party about my own reliability.**
