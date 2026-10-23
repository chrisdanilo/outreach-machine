---
business: Human Skills Training
type: launcher-proposal
title: "Thin launcher — proposed text + P7 obligation diff, awaiting Chris's approval"
status: INSTALLED-2026-08-20
owner: Chris Danilo
date: 2026-08-19  # corrected: this work was done 2026-08-19; filenames retain "08-20" to avoid breaking wikilinks
related: ["[[ROADMAP-thin-launcher]]", "[[method]]", "[[LAUNCHER-outreach-draft-machine]]"]
---

> ⏱️ **DATE CORRECTION, 2026-08-19.** This document and its filename were originally dated
> **2026-08-20**. That was wrong — all of this work was done on **2026-08-19**. Filenames are left
> as-is because several program files link to them by name and renaming would break those links.
> **Where the text says "2026-08-20" about work that was DONE, read 2026-08-19. Forward-looking dates
> ([Org 0102] Email 2 due 2026-08-20, effectiveness windows) are correct as written.**

# Thin launcher — ✅ APPROVED BY CHRIS AND INSTALLED 2026-08-20

> The text in §3 is now live in the `outreach-draft-machine` scheduled task, verbatim.
> This file is the permanent record of the obligation diff that licensed it.

**Stage 4 of [[ROADMAP-thin-launcher]]. The roadmap's own gate says: *"Chris approves the obligation
diff. Nothing installs without it."* This is that diff.**

| Measure | Before | After |
|---|---|---|
| Launcher length | ~9,900 words / ~90 lines of rules | **~250 words** |
| Drift surface (facts owned by another file) | **27** | **0** |
| Statements that can go stale | every version, ID, cap, budget, rule | **none** |

---

## 1 · What Stage 2 had to fix first — and it caught a live trap

**Nothing could be deleted until every obligation's owner was verified to sit on a path that runs
EVERY time.** Three problems surfaced, all now fixed:

| Found | Problem | Fix |
|---|---|---|
| 🔴 **`Update discovery-pipeline every run` lived inside PHASE 6** | Phase 6 is **conditional** — skipped when the target is met, when `pool_ceiling` is hit, and it *"never takes down drafting"* if it fails. **An obligation claiming "every run" from inside a skippable phase is unreachable and nobody can tell.** This is the identical trap that hid the suppression gap for four runs | **Moved to PHASE 4 — RECORD**, which is unconditional |
| 🔴 [[method]] "Approved copy" table | Named *"Email 1 — v2"* (actual: **v6**) and the pre-08-12 attachment filenames — **a rename the same file documents two sections later** | Versions and filenames **removed**; replaced with a pointer. [[method]] no longer owns them |
| 🔴 [[Cold-Outreach-Sequence-CCR&R]] header | Said *"Email 2 is now v2"*; its own body 250 lines later says *"v3 is the form"* | Header now **declares ownership** and states all three current versions in [Org 0934] |

⚠️ **Had the launcher been thinned without Stage 2, the dashboard update would have become
unreachable on any night discovery was skipped.** The owner check is not ceremony.

---

## 2 · THE P7 OBLIGATION DIFF — every instruction being removed, and where it survives

**P7: never remove the last independent statement of an obligation. Every row below names a
surviving owner ON AN UNCONDITIONAL PATH.**

| # | Removed from the launcher | Surviving owner | Path |
|---|---|---|---|
| 1 | The goal / two-queue rule (follow-ups uncapped + 7 new) | [[method]] Phase 0 + Phase 1 | unconditional |
| 2 | Report-before-housekeeping (P5) | [[method]] RUN EFFICIENCY | unconditional |
| 3 | The file load list + per-file obligations | [[method]] RUN EFFICIENCY *(restored to purpose-grouped form 08-20)* | unconditional |
| 4 | Subagent delegation · `people_bulk_match` ≤10 · 35 KB rotation | [[method]] RUN EFFICIENCY | unconditional |
| 5 | **The refactor rule (P7)** | [[method]] RUN EFFICIENCY | unconditional |
| 6 | Phase 0's four openers (status · manifest · **suppression refresh** · reconciliation) | [[method]] Phase 0 steps 1a–1d | unconditional ✅ *moved there 08-20* |
| 7 | The preferred ranking, tiers 1–5 | [[method]] Phase 1 | unconditional |
| 8 | Ratified recipient rules (CCR&R title · COO chain · tier-on-role · spend-the-lookup · inheritance · adjudication) | [[method]] Phase 1 + Phase 2 | unconditional |
| 9 | **The roster sweep gate + the reverse lookup** | [[method]] Phase 2 | unconditional |
| 10 | Template versions (v6 / v3 / v1) | **[[Cold-Outreach-Sequence-CCR&R]]** — the owner | read every run |
| 11 | The Tier-4 greeting placeholder | [[method]] Phase 3 *(added 08-20)* | unconditional |
| 12 | Rules 2–14 of the override list | [[method]] — gates, Phase 3, Failure modes | unconditional |
| 13 | Gmail connector parameter shape | [[method]] Phase 3 | unconditional |
| 14 | Forward-master message IDs | **[[golden-references]]** — the owner | read on every Email 1 |
| 15 | Phase 4 output spec + card format | [[method]] Phase 4 | unconditional |
| 16 | Pre-send self-check | [[method]] Phase 3 | unconditional |
| 17 | Self-recovery | [[method]] + `0.ChrisDanilo/rule-exhaust-self-recovery.md` | unconditional |
| 18 | Report order + manifest / freshness / roster blocks + national progress line | [[method]] Phase 7 | unconditional |
| 19 | `last_run_status` final act | [[method]] Phase 0 + Phase 7 | unconditional |

**19 obligations removed. 19 owners named. 0 orphans.**

🔴 **ONE DELIBERATE EXCEPTION TO SINGLE OWNERSHIP — rule 1, "never send email."**
It stays in the launcher **on purpose**, duplicated, because it is the only rule whose failure is
irreversible and it must survive [[method]] being unreadable. **Everything else can wait for the
next run; a sent email cannot be unsent.** This is a considered exception, not an oversight.

---

## 3 · THE PROPOSED LAUNCHER — full text

```
Your FIRST output message must begin with: "YYYYMMDD – CCR&R Draft Queue" using today's date.

You are running the HST CCR&R Nightly Draft Queue for Chris Danilo (Human Skills Training).
This is an unattended run: make reasonable choices, never ask questions, note the choices in your report.

🔴 NEVER SEND EMAIL. Gmail drafts only. This rule is repeated here deliberately because it is the
only one whose failure cannot be undone — it must survive even a total failure to read the program.

THE PROGRAM lives in the vault at ~/ClaudeVault, under
"3.Human Skills Training/Marketing/outreach-machine/method.md".

READ IT AND FOLLOW ITS PHASES IN ORDER, 0 THROUGH 7. It owns everything: which files to load and
what to write to each, the two-queue draft rule, the two verification gates, the roster sweep, the
reverse lookup, the recipient ranking, the copy pointers, the report format, and every ruling Chris
has made. Its RUN EFFICIENCY section tells you what to load — read that first.

🔴 ABORT AND SAY SO if the vault is unreachable, or if method.md cannot be read. The do-not-contact
lists and every safety gate live there; a run without them is not a degraded run, it is an unsafe one.

🔴 THIS LAUNCHER IS A POINTER, NOT A PROGRAM. It deliberately states no template version, no message
ID, no cap, no budget and no rule, because each of those is owned by a file in the vault and a second
copy here would go stale. If this launcher and the program files ever disagree, THE PROGRAM FILES WIN.

You may edit this scheduled task yourself via mcp__scheduled-tasks__update_scheduled_task. Never ask
Chris to paste a prompt by hand. If a self-edit fails, write the correction into method.md instead
and say so in your report — the program files win, so the fix still lands.
```

**Drift surface: 0.** Every fact it states is about itself.

---

## 4 · Before this installs — Stage 4's remaining gate

- [x] Owner check complete; three problems found and fixed
- [x] P7 obligation diff written — 19 removed, 19 owners named, 0 orphans
- [x] Drift surface computed: **27 → 0**
- [x] 🔴 **Chris approved this diff — 2026-08-20**
- [x] Installed via `update_scheduled_task` 2026-08-20; this file is the mirror
- [ ] Effectiveness check across three runs — every manifest balances, every mandatory report block present

## 5 · Rollback

**One call.** [[LAUNCHER-outreach-draft-machine]] holds the fat launcher verbatim and can be
reinstalled in under a minute. No vault data is touched by installing this.

## 6 · The honest risk

**[[method]] becomes genuinely load-bearing.** Today the launcher is a partial safety net for a
program file that fails to load or is read carelessly. After this there is no net — which is the
point, because a net that silently goes stale is worse than none, and this one had drifted four times
in six days. **But it means the three-run effectiveness check is not optional.** If any obligation
goes missing, it gets restored **to its owner file**, never back into the launcher.
