---
business: Human Skills Training
type: method
title: CCR&R Outreach Machine — Method (runtime program)
status: active
owner: Chris Danilo
created: 2026-08-06
rewritten: 2026-08-11
authority: "[[CCRR-Contact-Engine-Spec]] owns the engine design · [[Cold-Outreach-Sequence-CCR&R]] owns the copy · THIS FILE owns the nightly run AND the send rules (the Runbook was merged in and retired 2026-08-12, Chris's D-B ruling)"
related: ["[[CCRR-Contact-Engine-Spec]]", "[[CCRR-Outreach-Runbook]]", "[[Cold-Outreach-Sequence-CCR&R]]", "[[sequence-tracker]]", "[[verification-log]]", "[[ready-queue]]"]
---

# CCR&R Outreach Machine — Method

**This file is the nightly program.** The scheduled task is a thin launcher that reads it at
runtime. Edit here; no reinstall.

---

# §0 · RUNTIME PROGRAM — READ FIRST, EXECUTE IN ORDER

> **Installed 2026-08-24 per [[PROPOSAL-2026-08-24-preflight-and-precedence]], Chris approved.**
> **NOTHING BELOW §0 WAS DELETED.** Everything after §0 is the **ARCHIVE**: reasoning, worked
> examples, quoted origins, CAPA history. **§0 is what the run executes.**
>
> 🔴 **CONFLICT RULE — precise, because a vague one is worse than none:**
> **If §0 SPEAKS to a question, §0 wins and the conflict is named in the report.**
> **If §0 is SILENT, the archive binds.** §0 is a program, not a summary — silence is not permission.

## 🆕 §0.0 · RULINGS 2026-10-09 (Chris) — these supersede any line in this file that disagrees

> ✅ **Chris, 2026-10-09, verbatim:** *"I don't want to exclude TX, GA, IN, or KY anymore · the 51 orgs with no verifiable named staff: if there is a generic inbox for that org, let's include it in our outreach now · Let's include the Fit Doubt groups · Let's include government / school district / county units · Evaluate the dated retries list. If the delay is due to only one person on the thread, let's resume sending to all contacts."*

| # | Ruling | What the run does now | Where it is set |
|---|---|---|---|
| **R1** | **TX, GA, IN, KY are in.** CO stays excluded (Chris works CO personally). | They are appended to `territory.json.order` and walked like any state. **Existing clients are never cold-emailed:** [Org 0054] (GA) and [Org 0130] / UK are `CLOSED_R1` and stay hard-blocked by [[hubspot-suppression]] §A. | `territory.json` `excluded`, `order` |
| **R2** | **Generic inbox when no verifiable named staff.** | If the org's OWN site publishes no verifiable named-staff address but does publish a generic inbox, Email 1 goes **To the generic inbox** with `Hi <Org> team,` (V3, E1.7 + preflight `V3-to-only-when-no-human`). §0.8.3's anti-descent clause no longer holds these. No address of any kind on the org's own site → `HELD_NO_ADDRESS_ANY`. | `config.generic_inbox_policy` |
| **R3** | **Fit-doubt orgs are drafted.** | Card names the doubt; thread carries `⚠`. D-DOUBT still LABELS but no longer BLOCKS on fit. It still blocks on SAFETY (identity/dedup, address provenance, shared-tenant ownership). | `config.fit_doubt_policy` |
| **R4** | **Government, school-district and county units are in MKT-001; so are workforce boards (R1).** | §0.7.2's "named non-markets" row is retired; `config.out_of_market_org_types` is empty. | `config.out_of_market_org_types` |
| **R5** | **One person out never delays a thread.** | An out-of-office from one recipient (To or Cc) → send on schedule to **every** recipient. Delay only when **every** recipient is out (earliest return + 1 working day). Applies to Email 2 and Email 3, nightly and follow-up sender alike. | `config.ooo_return_date` |
| **R6** | **Revisit finished states.** | Every state that gained `REMAINING` rows was set back to `NOT_OPENED` (field `reopened: 2026-10-09`, old hold kept in `prior_hold`). The walk revisits them **in `order`, one at a time**, from NC. | `territory.json` |

🔴 **Unchanged safety gates (Level 1):** R1 contact-once / dedup · Gate 1 provenance · bounce circuit breaker (3.0%) · suppression · fail-closed. Every ruling above sits beneath them.
*Pre-change copies: `history/2026-10-09T1435/` and `runs/2026-10-09/rulings/`.*

## §0.1 · PRECEDENCE — when two rules collide

| Level | Class | Contents |
|---|---|---|
| **1** | **SAFETY GATES** | Gate 1 provenance · Gate 2 verification · suppression freshness · R1 contact-once · R11 two-ledger de-dup · the bounce circuit breaker · fail-closed |
| **2** | **HARD LIMITS SET BY CHRIS** | 1 To + max 2 Cc · no BCC on drafts · copy frozen (`machine_writes_copy: never`) · never assume a pronoun · 🔄 **never send Email 1 (drafts only); Emails 2 and 3 are sent ONLY by the follow-up sender (§0.16, `config.followup_sender`) — Chris 2026-10-04: *"You have my approval to only send emails 2 and 3 and only according to the timeline and instructions outlined in the machine's instructions."* The nightly run itself still never sends** |
| **3** | **SELECTION RULES** | R4 rank list · tier ladder · roster sweep · reverse lookup · R5 recipients fixed at Email 1 |
| **4** | **CONVENIENCE RULES** | `inherit-from-email-1` · skip-if-already-verified · reuse-as-sent |
| **5** | **EFFICIENCY RULES** | what to load · card byte targets · archive rotation · report brevity |

🔴 **A rule at level N never overrides a rule at a lower-numbered level.**
🔴 **When a convenience rule produces a state that violates a hard limit, THE CONVENIENCE YIELDS** —
and the card states what was changed and why.

*Origin: on 2026-08-24 `inherit-from-email-1` (level 4) beat the 1-To/2-Cc cap (level 2) and shipped a
four-recipient draft. Nothing said which won.*

## §0.2 · TWO STANDING DOCTRINES

**D-SWEEP** — **Any sweep looking for something that ESCAPED a category may not be scoped to that
category.** Retrieve unfiltered, filter afterwards. **Binds: drafts · bounces · auto-replies · sent
mail.** *An orphan is by definition an object that fell out of its category.*

🆕 **D-DOUBT** — ✅ **Chris, 2026-08-27: *"When in doubt, label to my attention."*** **Any uncertainty anywhere in the run — an ambiguous reply, an address that will not resolve, a rule that does not obviously apply — resolves to `CCR&R outreach/⚠` and a line in the report. 🔴 The machine never breaks a tie in its own favour.** Binds: reply classification · departure detection · recipient choice · org identity. *Over-closing and over-sending are both invisible from the inside; a flag costs one line.*

🆕 **D-SHIP** — ✅ **Chris, 2026-09-01: *"The primary thing each day is that we learn a little more by always sending email out. So before we can attack an issues list, I must have the dossier and outreach drafts."*** **The sending artifact — the dossier and the drafts Chris mails from — is produced FIRST and unconditionally. A defect list found during the run does not displace it, delay it, or consume the run's budget ahead of it. 🔴 Problems are REPORTED; the deliverable SHIPS.** Binds: step ordering when a run discovers defects mid-run · what a run does with its remaining budget · what a run may skip. *§0.3 step 16b already guarantees the dossier is eventually written; it does not stop a run from spending itself on an issues list first, which is the failure Chris named. This doctrine is the ordering half.*

**D-TABLE** — **The DECISIONS table carries only items where Chris's PREFERENCE is the input.**
If a rule already determines the answer, **execute it and report what was done.**
🔴 **A rule breach is never a decision item.**

## §0.3 · THE RUN — serial. Do these in order. Do not reorder.

| # | Step | Hold condition |
|---|---|---|
| **1** | Read `STATE.last_run_status`. `IN PROGRESS` → previous run died: report it, complete its orphans first | — |
| **2** | Write `last_run_status: IN PROGRESS — began <ts>` | — |
| 🆕 **2b** | 🖥️ **`python3 bin/run_snapshot.py`** — copies the ledgers as they stand NOW into `runs/<date>/*.pre-run.*` (config · contacted.md/.jsonl · candidates · calibration-log · territory · warm · STATE · funnel-conversion · funnel-outcomes · counted record). **Installed 2026-09-26.** This is what makes `bin/replay.py` able to re-test tonight's scripts later; the 09-23 and 09-24 runs did it by habit and replay exactly, the 20 runs before did not and cannot be re-tested. Idempotent — never overwrites | Script missing → say so; continue |
| 🆕 **2c** | 🔴 **PHASE STAMP — RUN START (CI-045 item 3).** Append `phase_stamps.run_start: <ts>` to `STATE.md` | — |
| **3** | 🆕 **`python3 bin/cluster.py check` first (2026-09-26) — print its `Cluster:` line; DRIFT or a missing Green Sheet/copy file is a finding and the profile wins (§0.7.3).** Then `TaskCreate` the full run manifest — every obligation in §0 as an explicit task, **PLUS one task per row of `config.json.expected_outputs`.** 🔴 **Added 2026-09-01 (P7b): the manifest was generated from §0 alone, so the dossier — which §0 never named — was invisible to it for two runs while the manifest reported 22 of 22 and was telling the truth** | — |
| **4** | Refresh [[hubspot-suppression]] (3 delta queries). Set `last_refresh` = today. **Run a control query; three zeroes from one connector is not evidence of zero** | Connector down → **new-org drafting HOLDS**; follow-ups proceed |
| **5** | **R14** — sweep Sent (`newer_than:3d`, unfiltered per **D-SWEEP**, then filter). 🆕 **WRITE `runs/<date>/sent_sweep.json`** *(schema in `bin/ledger_reconcile.py`)* **and run `python3 bin/ledger_reconcile.py`.** 🔴 **This file had never been written on any run, so ledger_reconcile.py — LIVE in §0.10 since 08-25 — had never once executed. Its first run, 2026-09-01, immediately found a corrupted address in Ledger B.** Then set-difference vs [[contacted]] Ledgers A and B. Append what is missing | Ledger stale → **NO NEW-ORG DRAFTING; follow-ups proceed** *(corrected 2026-08-25 — matches steps 4 and 8: a follow-up recipient is already DELIVERED in Ledger B and exposes no new address)* |
| **6** | **R13** — for every thread sent since last run: read as-sent To/Cc verbatim → fan out to [[sequence-tracker]], [[contacted]], [[verification-log]], [[discovery-pipeline]] → append `AS SENT — CORRECTIONS` to that run's review file | — |
| **7** | 🆕 **VALIDATE the as-sent set, do not only record it.** Does it satisfy §0.4 U1? A breach is reported as a finding about the thread | — |
| **8** | **R12.1** — bounce sweep, whole mailbox, `in:anywhere from:mailer-daemon newer_than:7d` | Unresolved hard bounce → **HALT new drafting** |
| **9** | **R17** — auto-reply sweep, whole mailbox, `newer_than:60d`. Classify A/B/C/D **before** applying any delay. 🆕 **2026-10-04 — MAINTAIN THE HOLD LABEL (`config.followup_sender.hold_label`, `Label_15` = `CCR&R outreach/⏸`):** for every open thread whose **To** has an ACTIVE class-A/D absence under §0.14 rules 2–3 (stated return date not yet passed, or class D inside its 7 days), `label_thread` ⏸ if absent; for every thread carrying ⏸ whose hold has lapsed (return date passed, stale notice, or the auto-reply is no longer the governing fact) and which Chris did not label by hand (a ⏸ with no matching auto-reply on the thread is Chris's — leave it), `unlabel_thread` ⏸. The follow-up sender (§0.16) never sends a ⏸ thread; this step is the only clock it has. 🔴 **MANDATORY, every run, over the full 60-day sweep — the 2026-10-05 run scoped the sweep to 3 days and skipped this, and the sender then read a held thread as sendable.** Report `⏸ set N · ⏸ cleared N · ⏸ standing N` on the `Auto-replies:` line; the sender's `Scheduled follow-ups:` line prints `N held ⏸` from the thread labels, so the two must agree | — |
| **10** | Read [[sequence-tracker]]. Mark replies (**a reply stops that sequence**). Compute due follow-ups | — |
| **11** | 🆕 **Read [[sequence-tracker]]'s binding-instruction section for EVERY org about to be touched** | Not read → **U9 fails** |
| 🆕 **11c** | 🔴 **PHASE STAMP — GATHER DONE (CI-045 item 3).** Append `phase_stamps.gather_done: <ts>` to `STATE.md` | — |
| **12** | **Draft every due follow-up.** Uncapped. R2 bounce handler first. 🆕 **2026-10-04 — WHICH FOLLOW-UPS THIS STEP STILL DRAFTS: Email n is drafted here ONLY IF `n` is NOT in `config.followup_sender.enabled_emails`, OR the thread is sender-ineligible — a HUMAN message sits on the thread (the nightly then classifies ★/X and no follow-up is owed anyway), its To has bounced, a bounce newer than the last send is not yet in `config.hard_bounces`, or `subject_param_honored` is false and a bounce/auto-reply is newest. 🔴 **And every follow-up this step HOLDS for a judgment reason gets `⚠` or `⏸` on the thread here — `holds_are_labels` (§0.16).** Everything else is the follow-up sender's (§0.16) and is NOT drafted; the dossier's `Scheduled follow-ups` section (from `python3 bin/followup_send.py --preview`) shows it instead. While `enabled_emails` is `[]` this step is unchanged.** 🆕 **2026-10-03 — Email 2 and Email 3 drafts are created through ZAPIER, not the native connector: `config.draft_writer` (Chris 2026-10-03).** Per follow-up: ① Email 3 only — `execute_zapier_read_action` `attachment` with `config.draft_writer.zapier.email_3_attachment` (`source_message_id` + `filename`) → a fresh file reference · ② `execute_zapier_write_action` `draft_v2_reply` with `thread_id` = the Email 1 THREAD id, `to`/`cc` from Phase 2, `body_type: html`, the approved copy as HTML with a newline between every tag, `label_ids: ["Label_2"]`, 🆕 **`signature` = the one `dynamic_enum_values[].value` from `inspect_zapier_actions(enum_property='signature')` resolved FRESH tonight + `signature_delimiter: false` (Chris 2026-10-04, `config.draft_writer.zapier.signature`)**, and (Email 3) `file: [<reference>]` · 🔴 **BEFORE ② — `config.draft_writer.zapier.reply_parent_rule` (2026-10-04): Zapier attaches the reply to the NEWEST message on the thread, drafts and TRASHED drafts included, and Gmail's conversation view hides a draft whose parent is a trashed draft. `hidden = get_thread.messageCount − messages listed − live drafts`; `hidden > 0` ⇒ the draft will open ONLY from its compose link — create it, write `COMPOSE-LINK-ONLY` on the card, count it. A live draft already on the thread ⇒ do NOT create: carry the existing draft, or (rebuild) trash it, ask Chris to delete it forever, create tomorrow. 🆕 **SUBJECT CHECK (2026-10-04, `reply_parent_rule.subject_check`): the reply also inherits the newest message's SUBJECT — if the newest listed message is a bounce or auto-reply (its subject ≠ the thread's, ignoring `Re:`), create the follow-up as a NEW THREAD with `draft_v2`, subject `Re: <thread subject>`, and write `NEW THREAD <id>` on the card and in the ledger status** · ③ **read it back on the native connector** per `config.draft_writer.zapier.verify` (Email 2: `get_draft FULL_CONTENT`, 0 × `google.com/url`; Email 3: `list_drafts … has:attachment filename:pdf`, never RAW) · ④ exactly one LIVE draft on the thread (`verify.both`) · ⑤ 🆕 **2026-10-04 (BQ-023) — RECORD IT, don't total it: this draft's row in `runs/<date>/drafts.json` carries `writer` (`zapier`\|`native`), `writer_fallback_reason` (ONLY when the path differs from `config.draft_writer.email_<n>`), `attachment_verified` (Email 3: `true` ONLY after the `has:attachment filename:pdf` read-back returned THIS draft id) and `zapier_readback` = {`thread_ok`, `wrapped_hrefs`, `label_ok`, `one_draft_on_thread`} — Z1–Z4 as recorded objects (schema: `bin/preflight.py` docstring). Every permission-classifier denial of a write goes into `runs/<date>/classifier.json` THE MOMENT IT HAPPENS as {`tool`, `target`, `phase`, `outcome`}; the file is written as `[]` at step 19b when there were none. `run_integrity.py` computes the `Draft writer:` and `Classifier:` lines from these two files — the run never totals them by hand.** **A Zapier failure on one draft → create that one natively (`fallback: native`), give its card the old manual-drag gate, record `writer: native` + the reason, and it is counted on the `Draft writer:` line.** Never `update_draft` a Zapier draft (Phase 3 step 7) | Zapier draft not read back → that draft is NOT reported as created |
| 🆕 **12b** | 🔴 **TERRITORY PRE-WORK — ENUMERATE BEFORE YOU DRAFT.** Read [[territory]]. If `active_territory` is SATURATED, advance to the next in `order` and say so. **If the active territory's `enumerated` is `false`, enumerate it NOW — read the state's OWN CCR&R directory and write EVERY lead agency into `territory.json` with `disposition: REMAINING` — BEFORE any Email 1 is drafted.** 🔴 **Enumeration and drafting are SEPARATE ACTS and may not occur in the same pass.** *Origin: on 2026-09-03 three discovery passes enumerated and drafted simultaneously across 23 states; coverage was never visible because no artifact recorded any state's denominator — the machine still cannot say how many CCR&Rs Minnesota has.* | Directory unreadable → the territory is `BLOCKED`, named with its URL and failure mode, and the run advances to the **next in `order`** |
| **13** | 🔴 **THE OUTREACH FLOOR — run the §0.8 CASCADE until `target_drafts` new organisations are drafted or a NAMED safety gate stops it.** Do not stop at "0 owed" | Cascade exhausted with no named gate → **the run FAILS** |
| **14** | Per new org: 🆕 **`python3 bin/dedup_check.py <website_domain> <mail_domain>` — THIS IS R1+R11 NOW, NEVER A GREP** (`CLOSED`→skip · `HOLD`→hold and say why · `CLEAR`→proceed) → suppression re-check → roster sweep → reverse lookup → rank per R4 → card → **§0.4 pre-flight** → draft 🆕 **(2026-10-04: Email 1 is created by Zapier `draft_v2` — new thread, `config.draft_writer.zapier.new_thread_action`: approved v7 HTML with the greeting, clean href, `HST_Flyer.pdf` by fresh `attachment` lookup, `label_ids [Label_2, Label_8]`, signature; read back per `verify.email_1`; record `writer`/`attachment_verified`/`zapier_readback` as in step 12 ⑤; a Zapier failure → native fallback, counted. NO placeholder where the GIF goes — the card says where Chris drops it)**. 🆕 **BEFORE the first draft of the night is created: write `runs/<date>/drafts.json` (schema in `bin/preflight.py` — 🆕 **2026-10-04: every row also carries the `writer` fields of step 12 ⑤; a row without them reads UNEXAMINED on the `Draft writer:` line** — 🆕 **and `recipient_name_evidence` is REQUIRED per draft, one entry per named recipient, each name AS IT APPEARS ON THE SOURCE PAGE. Omitting it does not fail the draft; it makes U2b read UNEXAMINED, which is worse, because an UNEXAMINED verdict on every draft is indistinguishable from a check nobody wrote. Measured 2026-09-02: 0 of 30**) for the full planned batch and run `python3 bin/preflight.py` — SHADOW: print its verdicts beside your own §0.4 pass in the report; a disagreement is a FINDING, and the LLM verdict governs until 3 consecutive runs agree. This is a MANIFEST OBLIGATION — skipping it is a `skipped — reason` line, never silence. *(Added 2026-08-26: the first §0.10 run never wrote the artifact because no step ordered it; the shadow clock starts only when this runs)* | Any pre-flight FALSE, or dedup `CLOSED`/`HOLD` → **HOLD that draft** |
| 🆕 **14c** | 🔴 **PHASE STAMP — DRAFT DONE (CI-045 item 3).** Append `phase_stamps.draft_done: <ts>` to `STATE.md`. **Then compute:** for each adjacent pair (`run_start`→`gather_done`, `gather_done`→`draft_done`), if the wall-clock gap exceeds 20 minutes, append `phase_stamps.suspended_line: Suspended: <H>h<M>m between <PHASE-A> and <PHASE-B>` to `STATE.md`; otherwise append `phase_stamps.suspended_line: Suspended: none`. *20 min is the threshold — the shortest documented suspension (2h30m, 09-08) is 7.5x it; this run's own clean night (09-04) has never been observed to approach it at any phase boundary.* | — |
| **15** | **Orphan recovery** — `list_drafts` **UNFILTERED** per **D-SWEEP**, then classify. 🆕 **Write the read-back to `runs/<date>/drafts_observed.json`** — the same sweep, kept as an artifact so `run_integrity.py` can prove the mailbox holds what `drafts.json` claims. 🆕 **2026-10-04 (BQ-023): read the sweep with `DRAFT_VIEW_FULL` and give each observed row `draft_id` and `wrapped_hrefs` (the count of `google.com/url` in that draft's html body). When present, `run_integrity.py` scores the MAILBOX count, not the run's claim — verify against Gmail, never against memory.** *§0.11 established read-it-back for one draft's links; this is the same principle applied to the whole batch's recipients, which is where a wrong set is expensive* | — |
| **16** | **THE LEARNING ARTIFACT.** Write `review-YYYY-MM-DD.md` — decisions → mandated blocks → header table → findings | — |
| 🆕 **16b** | 🔴 **THE SENDING ARTIFACT — write `dossier-YYYY-MM-DD.md`.** This is the file Chris opens to send from and it is the run's actual deliverable. 🔴 **THE LAYOUT IS FIXED AND IS NOT THE RUN'S TO RESTYLE — Chris, 2026-09-02: *"This dossier keeps changing format for some reason. I want the section of new email threads to be at the top, and I want the URLs clickable so I can immediately go to the staff page you sourced the email addresses from and visually verify."*** See **§0.6a** for the pinned layout. **NEW ORGANISATIONS (Email 1) COME FIRST**, follow-ups second; **oldest-first ordering still applies WITHIN each section** — the 08-28 outbox-order fix was about order inside a section and is unchanged, the 09-02 ruling is about which section leads. Each card carries: org · state · domain(s) · thread id · **every source page URL as a live markdown link** · a To/Cc table of **name · title · address · the clickable page that evidences it** · redundancy · and any warning that belongs at review time. `bin/calibration.py`'s line goes at the TOP (§0.3 step 18b). **Every Email 3 card carries the attachment gate verbatim.** Findings, rules and CAPA detail stay in the review file and are NOT repeated here. 🔴 **Installed 2026-09-01 per [[CAPA-2026-09-01-missing-dossier]]: the split was invented on 08-28 and never entered §0, so the 08-31 run followed §0.3 correctly and the artifact silently disappeared for two mornings** | **Not written → the run FAILS** |
| **17** | Update [[sequence-tracker]] · [[verification-log]] · [[recipient-profile]] · [[contacted]] · [[discovery-pipeline]] · [[CCRR-Outreach-Log]]. 🆕 **2026-09-26: all six are declared in `config.json.expected_outputs`, so `run_integrity.py` (step 19b) reports any one not written today — a skipped ledger is now a counted object, not a sentence (review-2026-09-22 Finding 2).** 🆕 **DUAL-WRITE (Stage 2, from 2026-08-26):** every [[contacted]] append goes to BOTH `contacted.md` AND `contacted.jsonl`; every candidate outcome (drafted/held/deferred, with reason + retry) is appended to `candidates.jsonl` THE MOMENT IT IS KNOWN; then run `python3 bin/migrate_contacted.py verify` and print its one-line result. 🔴 **markdown stays AUTHORITATIVE until 5 consecutive clean verify lines** — count them in the report | verify FAILED → report it; markdown wins |
| **18** | **R16 (revised 2026-08-25, Chris)** — meeting detection, Calendar connector NOT required: ① Fathom `list_meetings` → `meeting HELD` · ② **Gmail invite sweep** — `in:anywhere newer_than:14d` for invite emails (subjects `Invitation:`/`Updated invitation:`/`Accepted:`, or `filename:ics`), unfiltered per D-SWEEP then matched to Ledger A/B → `meeting BOOKED` · ③ **read live reply threads for an explicitly agreed date+time** → also BOOKED (quote the agreement line as evidence) · ④ HubSpot MEETING objects → corroborating · ⑤ reply-scan → `proposed`. **Ask Chris last, never first** | — |
| **18b** | 🆕 **CALIBRATION PASS — `calibration-log.jsonl`.** ① Every address DRAFTED this run gets a row with `predicted`, `predictor` (website-live-page · website-cached · apollo · zerobounce · machine-inference · machine-rule:&lt;rule&gt; · human-transcription) and `outcome: no-signal`. ② Every address HELD gets a row with `predicted: INVALID`, `hold_type` and `outcome: untested`. ③ **Re-score prior rows against tonight's evidence:** a new DSN flips `no-signal → bounced` (**FN — we said safe and it bounced**); a reply, auto-reply or delivery from a mailbox we HELD flips `untested → delivered` (**FP — we said invalid and it was fine**). ④ Run `python3 bin/calibration.py` and put its one line at the **TOP of the dossier**. 🔴 **`hold_type: selection` NEVER scores** — R4 excluding a CEO is a preference, not a claim about the address | — |
| **19** | Learn pass: full-body sent-vs-drafted diff. **Log copy changes, change nothing** | — |
| 🆕 **19c** | 🖥️ **`python3 bin/territory_check.py` and `python3 bin/territory_reconcile.py`.** Print both §0.6 territory lines verbatim. 🔴 **`out-of-order opens` must be 0.** SHADOW until Chris ratifies (§0.10 graduated-gate precedent) | Out-of-order open → the run FAILS once binding |
| 🆕 **19b** | 🖥️ `python3 bin/build_queue.py` (print its line). Then 🔴 **`python3 bin/run_integrity.py` — the last gate before the report.** Existence of every declared output · `drafts.json` vs the mailbox read-back · the as-sent delta vs the previous run's `drafts.json` · 🆕 **2026-10-04 (BQ-023): the `Draft writer:` and `Classifier:` lines, computed from `drafts.json` (writer fields) + `classifier.json`. Write `runs/<date>/classifier.json` (`[]` if no denials) BEFORE running it; absent = NOT RECORDED, a finding.** **Print all three lines verbatim.** SHADOW for the two new lines: exit 2 reports, never fails the run (§0.10 graduated gate) | **Exit 1 → the run FAILS and names the missing deliverable** |
| **20** | **DELIVER THE REPORT** | — |
| 🆕 **20b** | 🖥️ **RENDER THE DASHBOARD — `python3 bin/dashboard_seed.py`.** Runs AFTER the report, so it renders numbers this run has already written. Reads `funnel-conversion.json` and the counted record in `TLP/dashboard-data.json` (one block per quarter; rules in `TLP/TLP-Rules.md`); writes `runs/<date>/dashboard_seed.json`, rewrites **only** the `<script id="data">` block in `TLP/tlp-practice-dashboard.html`, and regenerates the read-only `TLP/TLP-<quarter>.md` view. The dashboard gathers and presents; it does not track posting to TLBS (Chris, 2026-09-28). **Print its line verbatim.** `PROBLEM` means the page can show Chris a figure that is not the counted record — say so plainly; never report `OK` when the script printed `PROBLEM`. 🔴 **It RENDERS, it never RECOUNTS.** `countedThrough` is a judgment call and this step must never advance it | Fails → print `Dashboard: skipped — <reason>` and carry on. **The run does NOT fail** — the dashboard is a convenience, never a gate on outreach |
| **21** | Archive rotation, if and only if the report is delivered and a file exceeds ~35 KB | Report not delivered → `skipped` |
| **22** | Flip `last_run_status: COMPLETE — report delivered <ts>`. **Final act** | — |

## §0.4 · PRE-FLIGHT — every assertion is a boolean. Any FALSE holds that draft.

🔴 **Each assertion reports THE OBJECT IT CHECKED, not just a verdict.**
`U1: 1 To + 2 Cc ✅` — **never** `U1 ✅`. *A checklist that reports only verdicts becomes a ritual.*

### Universal — Email 1, 2 and 3

| # | Assertion |
|---|---|
| **U1** | `count(to) == 1 AND count(cc) <= 3` — 🔄 **RAISED FROM 2 TO 3 CC ON 2026-08-28 (Chris):** *"I think it's okay to have 1 TO and 3 CC. For some orgs, it might be best for us to do this because they're so big and have so many different roles."* **The To is still exactly one.** 🔴 **This is a CEILING, not a target** — R4 still ranks, and the 4th slot is filled only when a genuinely distinct role justifies it at a large multi-function organisation. **It is never a licence to add a weaker recipient to pad `Redundancy`.** §0.8.3 binds: the floor may not be met by widening the Cc. *Origin: [Org 0939] — 750 staff, $182M, with the PD owner, the Chief Program Officer and two published R&R/quality specialists all legitimately distinct.* |
| **U2** | `set(names in greeting) == set(names of NAMED-HUMAN recipients)`. 🆕 **GENERIC-INBOX CARVE-OUT — Chris, 2026-08-25 (D2):** a generic/role inbox carries no name, so it is greeted as **`and team`** — never omitted, never invented. **≥1 named human on the thread → `Hi <Name(s)> and team,`** (humans first, always). **NO human found anywhere, generic inbox only → `Hi <Org> team,`.** 🔴 **The carve-out applies ONLY to addresses classed V3 under E1.7. Every named human still gets their name, and a V3 inbox is still never the To.** *Origin: U2 as originally written forbade Chris's own convention and would have shipped CHCF at 2 of 3 with a usable third address on the table.* |
| **U3** | every address character-matches its quoted evidence string |
| **U4** | no recipient is in Ledger B as `bounced` or `departed` |
| **U5** | `hubspot-suppression.last_refresh == today` |
| **U6** | [[contacted]] reconciled this session |
| **U7** | `bcc` is empty |
| **U8** | body byte-identical to the approved template except greeting and `{{company}}` |
| **U9** | binding instructions in [[sequence-tracker]] read **for this org** this session |
| **U10** | this org's thread checked in **Sent** this session |

### Email 1 only — a new organisation

| # | Assertion |
|---|---|
| **E1.1** | org domain absent from [[contacted]] Ledger A |
| **E1.2** | org domain absent from [[hubspot-suppression]] §A–§D |
| **E1.3** | card carries `Roster resolution:` and **all three identities hold** |
| **E1.4** | if recipient tier > 2 → card carries `Reverse lookup:` |
| **E1.5** | 🎯 if `Tier-1/2 identified == 0` **AND** `named on page >= 1` → card names the **highest-ranked person found** and states why they are not used |
| **E1.6** | To recipient's current employment vendor-checked *(identity — Apollo)* |
| 🆕 **E1.8** | **BOTH domains recorded on the card: `website_domain` (the host AFTER following redirects) and `mail_domain` (the domain of the addresses actually harvested).** 🔴 **Record them EVEN WHEN IDENTICAL** — *"these are the same"* is a finding, and a field populated only when interesting is a field nobody trusts. If they differ and the pair is not already in `config.domain_aliases`, **add it before drafting.** *Origin: [[CAPA-2026-08-25-org-domain-identity]] — three orgs have met this shape (Five County, ICP Oswego, [Org 0462]) and were found three different ways, none of them systematic.* |
| 🆕 **E1.7** | **every recipient carries a VALIDITY line naming its class** — 🔴 SOURCE-MATCHED, Chris's ruling 2026-08-25 evening (no Zapier; ZeroBounce runs inside Apollo — see §0.9 revision block). **V1 vendor-sourced** → `VALIDATED — ZeroBounce via Apollo waterfall (raw_status, date)` read from `emails[].vendor_validation_statuses[]` (shape probe-verified 2026-08-25, [[verification-log]]); `raw_status: invalid` → HOLD that address and take the next rank; verdict absent on a vendor-sourced address → proceed, flagged `VENDOR-RESOLVED — validator verdict unavailable` (hold only on a definitive negative, §0.9). **V2 live-page, named human** → `WAIVED — live-page named-human exception (URL, date)`; no vendor call. **V3 live-page, NO human name attached** → `CC-ONLY — published address, no name`, flagged on the card (the tony.armadillo class). 🔴 **AMENDED 2026-08-25 (Chris, D2) — NAMED CONFLICT, §0 CONFLICT RULE INVOKED:** the original text read *'never the To'*, which forbade Chris's own D2 instruction that an org where **no named human can be found anywhere** is mailed at its generic inbox with the greeting `Hi <Org> team,`. **Chris's instruction is level 2 and governs.** V3 may take the To **ONLY** when ALL of these hold, and the card states each one: ① the **full roster sweep ran** and returned **zero** named humans with a reachable address · ② `evidence_three_states` is recorded for every Tier-1/2 person found-but-unreachable · ③ the greeting uses the `Hi <Org> team,` form · ④ the card carries `Descent: rank 7 — justified by <the sweep result>`. 🔴 **§0.8.3 binds harder here than anywhere else: this is the exact door [[CAPA-2026-08-24-generic-inbox-descent]] was written about. A V3 To is legitimate ONLY as the honest end of a real sweep, NEVER as a shortcut to the floor.** Where ≥1 named human exists, that human takes the To and the V3 inbox rides as a Cc under the `and team` greeting. An address fitting no class → **HOLD** |

### Email 3 only

| # | Assertion |
|---|---|
| **E3.1** | 🔄 **2026-10-03:** card opens with the attachment line `📎 ATTACHED BY ZAPIER AT CREATION: HST_3PackStarterKit.pdf (7.2 MB) · verified has:attachment ✅ <draft id>` — the ✅ is written ONLY after the native `list_drafts … has:attachment filename:pdf` read-back returned that draft id. A native-fallback Email 3 keeps the old `📎 ATTACH BEFORE SENDING` gate instead |

### Email 2 and 3 only — Zapier-written drafts (🆕 2026-10-03, `config.draft_writer`)

| # | Assertion |
|---|---|
| **Z1** | the draft was created by `gmail_create_draft_reply` with `thread_id` = the org's Email 1 thread id (`threadId` on read-back equals it) |
| **Z2** | native read-back `html_body` contains **0** occurrences of `google.com/url` and the approved href(s) verbatim |
| **Z3** | `label_ids` on read-back contains `Label_2` |
| **Z4** | exactly ONE live draft exists on the thread after creation (a pre-existing draft was deleted FOREVER by Chris before creation — trashing it is NOT enough, see Z5 — or both compose links are reported SEND THIS ONE / DELETE THIS ONE) |
| 🆕 **Z5** | **the draft's parent is a visible message** — at creation the newest message on the thread was a sent mail / bounce / auto-reply / reply, NOT a live or trashed draft (`config.draft_writer.zapier.reply_parent_rule`, 2026-10-04). FALSE ⇒ the draft is invisible in Gmail's conversation view (opens only from its compose link): the card reads `COMPOSE-LINK-ONLY` and the `Draft writer:` line counts it. Recorded as `zapier_readback.parent_visible` |

🆕 **2026-10-04 (BQ-023):** Z1–Z4 are written per draft as `zapier_readback` in `runs/<date>/drafts.json` (step 12 ⑤) and scored by the scripts: `preflight.py` prints **W1** (path matches `config.draft_writer`, or a fallback reason is recorded) · **W2** (Email 3: config names the kit file + its source message) · **W3** (Z1–Z4 all hold on read-back; no read-back = UNEXAMINED) · **W4** (Email 3: `attachment_verified`; absent = UNEXAMINED). `run_integrity.py` totals them into the `Draft writer:` line. SHADOW — report beside your own Z pass; disagreement is a finding.

## §0.5 · PASS CONDITION

> **`invalid = 0` AND `M = 0` AND `HELD = 0` AND `preflight_holds = 0`**
> 🆕 **AND `new_orgs_drafted >= target_drafts` OR a NAMED safety gate from §0.8 blocked it.**
> 🆕 **AND `new_orgs_drafted <= max_new_orgs_per_run`.** 🔴 **Installed 2026-09-03. Exceeding the
> ceiling is a FAILED pass condition, not a strong night** — see [[CAPA-2026-09-03-floor-overshoot]].
> *A `>=` in a pass condition describes the minimum a run must clear. It has never authorised anything.*
> 🆕 **AND `bin/territory_check.py` reports `out-of-order opens: 0` and at most one territory
> `IN PROGRESS`** (migration-baseline territories excepted until the debt clears). §0.8.6.
> 🆕 **AND `bin/run_integrity.py` exits 0 or 2 — never 1.** Exit 1 means a `binding: true` declared output is missing or stale, and **`dossier-<date>.md` is the first of them.** *(Installed 2026-09-01, [[CAPA-2026-09-01-missing-dossier]].
> A run that drafts sixteen perfect emails and produces no dossier has not shipped — every other clause here
> measures the QUALITY of the work and none measured whether the thing Chris opens was produced.)*
> **`B` is reported and carried, never scored.**
> **Redundancy is reported and never scored** — a thin batch is sometimes correct, and scoring it
> would make *"don't card the hard org"* the cheapest clean report.

## §0.6 · MANDATORY REPORT LINES

🆕 **OUTPUT FILE LINKS — Chris, 2026-09-30:** *"Remember to show the links to the output files here so I can easily access them when working each morning."* 🔴 **Before the final message, `device_stage_files` the run's `dossier-<date>.md` and `review-<date>.md`, then `SendUserFile` them (display: render)** so they appear as clickable file cards in the chat. ⚠️ **A `computer://` link alone does NOT work** — tested 2026-09-30: the viewer answered *"This file is outside the folders connected to this session"* even though the file was there. The final message may also name the files, but the file cards are the deliverable.

```
Address calibration: N sent & observed · N said-safe-but-BOUNCED · N said-invalid-but-FINE · N held & never tested (unknowable) · send precision X%   ← TOP LINE OF EVERY DOSSIER (Chris, 2026-08-28); computed by bin/calibration.py, never recalled
<phase_stamps.suspended_line, verbatim from STATE.md, or "Suspended: none" if absent>   ← SECOND LINE OF EVERY DOSSIER, directly under Address calibration (CI-045 item 3, added 2026-09-15); read from STATE.md.phase_stamps, never recomputed at dossier-write time
Meetings: N HELD · N booked · N proposed — sources: Fathom / Gmail (invites + threads) / HubSpot   ← HEADLINE METRIC (Chris, 2026-08-25)
Warm lane: N open hand-offs · N actioned this run · oldest next-action: <date>   ← reads warm.jsonl; stale row → say so at the top
Integrity: outputs N/N present · binding outputs ok|BINDING MISSING: <names> · drafts read-back: clean|DIVERGENT(N) · as-sent delta: M = N   ← bin/run_integrity.py. Exit 1 = the run FAILS
Cluster: <id> · <label> · <method> × <market> × <message> · applied settings agree with profile | 🔴 DRIFT   ← bin/cluster.py check (§0.7.3), added 2026-09-26
Build queue: N open (N wait on Chris: …) · N closed in the last 7 days · oldest open: BQ-NNN   ← bin/build_queue.py (counts BUILD-QUEUE.md rows), added 2026-09-26. A gap that needs code is a ticket there, never a prose patch
Dossier: dossier-YYYY-MM-DD.md · N cards · N Email 1 · N Email 2 · N Email 3 · attachments verified N of N (Zapier) · fallback gates: N   ← THE DELIVERABLE (§0.3 step 16b). A run with no dossier FAILS
Run manifest: N obligations · N completed · N skipped (reason each) · N FAILED   [must balance]
Outreach floor: N carded · N drafted · target N · ceiling N · {ON TARGET | 🔴 OVER BY N | FAILED — <named gate>} · cascade tier reached: T0-T4   ← 🔴 NEVER A RATIO. 'OVER BY 5' reads as the defect it is; '150%' reads as a win (CAPA-2026-09-03-floor-overshoot C4)
Yield: N carded → N drafted · N held [by status] · N deferred · passes: N
Rework: N candidates re-touched · N skipped as already-worked (candidates.jsonl) · oldest retry: <date>
Ledger dual-write: <the one-line output of bin/migrate_contacted.py verify> (clean run N of 5)
Queue: N Email 1 drafts waiting · after Chris's sends: M · runs of slack: M ÷ target_drafts
Pace: N orgs outreached over the last 5 working days · target N · X% of pace
File freshness: <file> <date> · … (flag anything >1 run stale)
Org identity: N orgs · N with both domains recorded · N single-domain · N ambiguous   ← bin/dedup_check.py --audit
De-dup: N candidates checked · N CLOSED · N HOLD · N CLEAR   ← bin/dedup_check.py, NEVER a grep
Roster sweep: N carded · N passing · N invalid · N HELD · M = N · B = N
Lookup budget: N of 25 spent · Tier-1/2 left unqueried: M · unreadable rosters: B
Pre-flight: N drafts × N assertions · N holds [name each]
Recipients: N orgs at 3 of 3 · N at 2 of 3 · N at 1 of 3
Bounces: N new · M suppressed open · R repairs owed before <date>
Auto-replies: N swept · A absences (H held — To out, R released) · B departures · P successors promoted (§0.14 r5) · C standing · D no-date · S stale · F flagged · ⏸ set N · ⏸ cleared N · ⏸ standing N   ← the ⏸ counts are the follow-up sender's only OOO clock (§0.3 step 9, §0.16)
Replies: N total · A active (★) · D closed — declined or on-file (X)   ← §0.13
Stage labels: /0 N · /1 N · /2 N · /3 N · /★ N · /X N · /⚠ N — [must sum to the parent label's thread count]   ← §0.12
Doubt: N items flagged to Chris this run (D-DOUBT) — name each
Contacted ledger: N sends found · M newly logged · current as of <ts> (per bin/ledger_reconcile.py)
As-sent delta: N reconciled · M recipient changes by Chris · [org: drafted X → sent Y]
Credits: before → after = spend, itemised (or UNEXPLAINED)
Shape test: to=<form> · cc=<form> · labelIds=<form> · hrefs wrapped: <which>   ← §0.11, first write of every run
Draft writer: zapier N (Email 1 N · Email 2 N · Email 3 N) · native fallback N [name each + why] · attachments verified N of N (Email 1 flyer + Email 3 kit) · hrefs wrapped on Zapier drafts: 0 · compose-link-only N   ← bin/run_integrity.py, computed from runs/<date>/drafts.json writer fields (BQ-023, 2026-10-04; config.draft_writer added 2026-10-03). Any fallback is a finding; a row without writer fields reads ⚪ UNEXAMINED, never clean
Classifier: N writes denied [tool + target each, or "none"]   ← bin/run_integrity.py reads runs/<date>/classifier.json (BQ-023, 2026-10-04); CAPA-2026-09-30 C5. A denied Zapier write is the open risk for unattended runs; count it, never narrate it. File absent = NOT RECORDED, a finding — never zero
Sender: yesterday N Email 2 · N Email 3 sent by the machine · N held [reason each] · N skipped · fires N/4   ← python3 bin/followup_send.py --report-yesterday, computed from runs/<yesterday>/sender/*/followup_sends.json (§0.16, 2026-10-04). While enabled_emails is [] the line reads 'Sender (shadow): N would-send · …'. fires < 4 on a business day = the sender did not run — a finding
Scheduled follow-ups: N today (ET n · CT n · MT n · PT n) · N held ⏸ · Holiday list ends YYYY-MM-DD   ← python3 bin/followup_send.py --preview; under holiday_coverage_warn_days of coverage left → 🔴 REFRESH config.followup_sender.never_send_dates
Territory: <ST> <STATUS> — N of M lead agencies · C contacted · H held · O out-of-market · R remaining · X% · counties N of M · opened <date> · last worked <date>   ← bin/territory_check.py
Territory order: next <ST2> (M agencies, enumerated yes|no) · boundaries crossed this run: N [name each] · out-of-order opens: 0 · SATURATED to date: N of 51   ← 🔴 any value but 0 on out-of-order opens FAILS the run
Territory reconcile: N territories · N hard drift · N states with no row · N rows unassignable (state:null)   ← bin/territory_reconcile.py
Dossier shape: N/N required headings present · matches template|MISSING <names>   ← bin/dossier_check.py, against dossier-template.md
Market: N outreached · ~M remaining · ~W working days of runway
National progress: N orgs outreached of ~667 needed (X%)
```

## 🆕 §0.6a · THE DOSSIER LAYOUT IS PINNED. The run does not restyle it.

> 🔴 **AMENDED 2026-09-03 — THIS SECTION DID NOT HOLD, AND HERE IS THE MEASUREMENT.**
> ✅ **Chris, 2026-09-03:** *"Why does the structure of the dossier keep changing? Build an outline
> template for the dossier that each scheduled task run will just fill in."*
>
> §0.6a was installed 2026-09-02 to stop exactly this, **and the shape moved again the very next
> run.** `bin/dossier_check.py` scores the 09-02 dossier at **3 of 9** required headings and the
> 09-03 dossier at **8 of 9**. **The rule was read and the shape still drifted**, because this
> section describes a heading list in prose and the run re-derives it nightly.
>
> 🔴 **THE SHAPE NOW LIVES IN [[dossier-template]] — a fill-in skeleton with a machine-readable
> `REQUIRED HEADINGS` block — and `bin/dossier_check.py` verifies the produced file against it.**
> **§0.6a remains the LAW (why the order is what it is). The template is the SHAPE (what to type).**
> When §0 changes the dossier's shape, **the template must be edited in the same session** — P7b
> applied to the template.
>
> ⚠️ **A contributing cause worth naming:** `dossier-template.md` already existed, RUN EFFICIENCY
> says *"🔴 now load it EVERY run that cards an org"*, and **the 09-03 run did not load it.** It was
> also a CARD template only — it never described the whole file — and was three weeks stale. **A
> template nobody loads and that covers the wrong scope is not a control.**


> ✅ **Chris, 2026-09-02:** *"This dossier keeps changing format for some reason. I want the section
> of new email threads to be at the top, and I want the URLs clickable so I can immediately go to
> the staff page you sourced the email addresses from and visually verify."*

🔴 **The complaint is not cosmetic. A deliverable whose shape moves every night cannot be scanned
fast, and scanning it fast is the entire point** — it is the one file Chris opens under time
pressure before sending. **Format drift is a defect class, and this section exists so that a future
run reaching for "a clearer layout" is reaching for a rule instead.**

### The order — fixed

| Position | Section |
|---|---|
| **Top line** | `bin/calibration.py`'s one-line stat (§0.3 step 18b) |
| **Then** | Anything that must be read BEFORE sending — attachment gates, size warnings, a bounce that changes a recipient |
| **1** | 🔴 **NEW ORGANISATIONS — Email 1.** These lead. They are the cards that carry unverified people and need Chris's eye |
| **2** | **FOLLOW-UPS — Email 2 and Email 3.** Every recipient already delivered once; they need far less scrutiny |
| **3** | What else happened — replies, bounces, meetings, suppression news |
| **4** | Decisions for Chris |
| **5** | Standing numbers |

⚠️ **This does NOT reverse the 2026-08-28 outbox-order fix.** That ruling was about ordering *within*
a section — **oldest first, matching his Drafts folder read bottom-to-top — and it still binds.**
The two rules operate on different axes: 09-02 says which SECTION leads, 08-28 says the order INSIDE
one. A run that "restores" newest-first inside a section has broken 08-28; a run that buries the new
organisations under the follow-ups has broken this.

### 🔴 EVERY EVIDENCE URL IS A LIVE MARKDOWN LINK

**Bare URLs, plain-text hostnames and page names without a link are all defects.** Chris's stated use
is *"immediately go to the staff page… and visually verify"* — a URL he has to copy out of a code
span does not serve that.

| Rule | |
|---|---|
| **Per recipient, not per org** | The link sits on the row of the person it evidences. Two people found on two pages get two links |
| **The page the address actually came from** | Not the org's home page, not a search result. The exact page read |
| 🔴 **Say what the page will and will not show him** | A **V2** link shows the address printed on the page — he can verify it end to end. A **V1** link shows the person's NAME and TITLE only; the address came from Apollo/ZeroBounce and **will not appear on that page.** Label these `(name + title only — address is vendor-resolved)` so a page that lacks the address is never mistaken for a bad citation |
| **A blocked page is still named** | If a roster was JS-only, a PDF or an empty body, link it anyway and say what happened. That is how Chris can overrule with a browser session |

## 🆕 §0.7 · MARKET DISCIPLINE — the machine serves ONE market, and Chris opens the next one

> ✅ **Chris, 2026-08-31, correcting this file:** *"A new state is not a new market. So, multiple
> CCR&Rs in different states are still part of the same cluster… Workforce solutions groups are a
> different market, so that would be considered a new cluster. School districts would also be
> considered a different market… I want to launch new clusters systematically and not while we're
> outreaching to CCR&Rs. Let's stick with CCR&Rs until I create a new Green Sheet for the next
> cluster, then we'll launch a new one."*

### §0.7.1 · THE VOCABULARY IS TLBS'S, NOT THIS MACHINE'S

🔴 **This file previously used "cluster" to mean a geography. That was invented here and it is
WRONG.** It is the same defect class as the banned word `approach` (§0.6 terminology block): a TLBS
term of art, re-used locally with a different meaning, corrupting the practice numbers Chris reports.

**The authoritative definitions live in [[cluster-pipeline]], [[ClusterChecklist]] and
[[Market-Library]]. This file imports them and never redefines them:**

| Term | TLBS meaning — binding | ❌ What this machine wrongly called it |
|---|---|---|
| **Cluster** | **one Method × one Market × one Message**, identified `CL-YYYY-QN`, launched in a 90-day window, carrying a decision date and a kill condition | a state or a region (`NY-ccrr`, `NC-ccrr`, `CA-ccrr`, `CCRR-core (FL)`) |
| **Market** | the M that changes when a cluster changes. Defined by **function, not geography and not domain** | conflated with geography |
| **Region / sweep** | 🆕 **the correct word for a geography.** A state, a metro, a set of counties — a slice of ONE market's universe | called a "cluster" |

🔴 **THE BOUNDARY TEST IS ALREADY WRITTEN AND IT IS THE ONLY TEST** ([[Market-Library]],
Chris + machine 2026-08-12): **if the standing Message lands on an org type WITHOUT editing the
template, it is the same market. The moment an org type forces a copy rewrite, it is a different
market — and a different cluster.**

### §0.7.2 · 🔴 THE HARD GATE — the machine may not open a market

> 🆕 **WHEN THIS GATE FIRES, THE PROCEDURE ALREADY EXISTS — DO NOT INVENT ONE.** Opening a market
> runs the TLP cluster-launch sequence: `[[ClusterChecklist]]` (the Week 0 → Week 13 playbook),
> `How-Chris-Works-on-HST.md` §Cluster Launch Sequence (the six steps), and
> `cluster-pipeline.md` §In Build. The Green Sheet is **step 2 of that sequence**, not a
> substitute for it. This machine's job at the gate is to STOP and name the sequence; the
> sequence itself is Chris's, and Chris's own 2026-08-31 words are the reason both exist:
> *"I want to launch new clusters systematically and not while we're outreaching to CCR&Rs."*
> *(Added 2026-09-02. Measured, not assumed: a vault-wide search found the sequence in three
> linked documents while a narrower search had reported it missing. Nothing new was written.)*

**The active cluster is `CL-2026-Q3` = MTH-001 Verified Cold Outreach × MKT-001 CCR&Rs and ECE
intermediaries × MSG-001 v3 sequence.** Every organisation the machine drafts must be inside
**MKT-001**, whose definition is owned by [[Market-Library]]:

> *staffed agencies that serve child-care providers rather than operating centers — CCR&Rs,
> community-action child-care programs, councils of government running CCR&Rs, university-embedded
> programs, shared-services alliances. **Function test, not domain test.***

| | Rule |
|---|---|
| **Geography** | ✅ **Free.** Any state, any metro. A new state is a new REGION of MKT-001 and needs no approval — CCR&Rs in NC, CA, NY and FL are one market and one cluster |
| **A different org TYPE** | 🔴 **STOP. This is a new MARKET and therefore a NEW CLUSTER.** The machine does not draft it, does not discover it, does not add it to the pool |
| **Who opens it** | 🔴 **Chris, by writing a GREEN SHEET** — the ⭐ non-negotiable first collateral piece in [[ClusterChecklist]] Phase 1 — and promoting the market into a cluster slot on [[cluster-pipeline]] |
| **Named non-markets** | ~~2026-08-31: workforce boards and school districts are own markets~~ 🔄 **RETIRED 2026-10-09 (Chris, §0.0 R1/R4): workforce boards, government, school-district and county units are drafted under CL-2026-Q3.** |
| **Ambiguous org type** | 🔄 **2026-10-09 (§0.0 R3): drafted and flagged `⚠`, card names the doubt.** *Prior rule, superseded:* 🔴 **HELD, not drafted.** Card it, name the doubt, put it in the report under D-DOUBT. ⚠️ An ambiguity here is the one kind the machine must never break in its own favour, because volume pressure from §0.8's floor points the wrong way |

🔴 **WHY THIS IS A LEVEL-2 HARD LIMIT, NOT A PREFERENCE.** [[ClusterChecklist]]'s single recorded
lesson is Q2 2026: *"Chris built the outreach engine before building the Green Sheet. Result: high
volume of approaches, low conversion. The Green Sheet gives outreach a reason to exist — build it
first next time."* **A market opened by the machine is that exact mistake, committed automatically
and at ten organisations a night.** The floor may never be met by widening the market.

⚠️ **THE FLOOR YIELDS TO THIS GATE.** If MKT-001's universe runs dry, the correct outcome is
**"Outreach floor: FAILED — MKT-001 exhausted, awaiting a Green Sheet for the next market"** under
§0.8.2 as a named gate. **It is NOT a licence to descend into an adjacent org type.** §0.8.3 already
forbids meeting the floor by descending the tier ladder faster; this forbids meeting it by
descending the market.

*Origin: on 2026-08-20 this file recorded that "Texas workforce boards were approved as a cluster"
and treated them as an expansion of the CCR&R work. **21 Workforce Solutions boards were outreached
between 08-19 and 08-26 with no Green Sheet, no cluster slot, no decision date and no kill
condition** — 18% of the machine-era ledger, in a market nobody had defined. It went unnoticed for
eleven days precisely because the machine's own vocabulary made a new market look like a new state.*

### 🆕 §0.7.3 · THE CLUSTER IS A SETTINGS BLOCK — `config.json.cluster_profiles` (installed 2026-09-26)

**What it is.** One profile per cluster (`CL-YYYY-QN`) in `config.json`: method × market × message,
the Green Sheet path, the approved-copy file, the Gmail label parent and stage-label IDs, the
target-list source, and the machine settings that differ between clusters (`target_drafts`,
`max_new_orgs_per_run`, `queue_ceiling`, `sequence_gap_days`, `sequence_length`, `stage_labels`,
`territory_ledger`, `territory_unit`, `active_market`, `out_of_market_org_types`). **The profile is
the source; the top-level keys the scripts read are its applied copy.** `bin/cluster.py check`
(§0.3 step 3) proves they agree.

**What it changes in this file.** Wherever §0 or the archive says *CCR&R*, read *the active
cluster's market* — unless the sentence states a CCR&R-specific fact (a directory, a role title, a
named organisation). The approved copy is **the active profile's `copy_file`**, today
[[Cold-Outreach-Sequence-CCR&R]]. Nothing else in this file's rules is cluster-specific by design;
where a rule turns out to be, that is a finding to record here, not a reason to fork the file.

**How a cluster launches — four steps, and the gate in §0.7.2 is unchanged:**
1. Chris writes the Green Sheet (⭐ ClusterChecklist Phase 1). No sheet, no launch.
2. The profile is filled: `copy_file` (approved copy exists on disk), `gmail_label_parent` +
   `stage_labels` (labels created, IDs recorded), `target_list_source`, a fresh `territory_ledger`.
3. **Chris runs `python3 bin/cluster.py apply CL-YYYY-QN`.** It refuses while any of those is
   missing; it snapshots `config.json` before and after; it never touches a draft.
4. `python3 bin/replay.py --all` still passes — the scripts reproduce every recorded run.

🔴 **Only Chris runs step 3.** The machine may read a profile; it may not apply one, edit one, or
add an org type to one (§0.7.2). `CL-2026-Q4` sits in the file as ON DECK with `copy_file: null`
precisely so that `apply` cannot succeed by accident.

### §0.7a · REGIONAL VOCABULARY REVIEW — kept, renamed, demoted to what it actually is

🔴 **Before the first batch in a NEW REGION of the active market, run a RANK-LIST VOCABULARY
REVIEW.** Read three of that region's own sites, list the titles that actually perform
PD/training/quality there, and **add any missing signal words to R4 rank 1 before drafting.**
Record it on the first card.

⚠️ **This is a RANKING aid inside one market. It is NOT the new-cluster gate and never was** —
the gate is §0.7.2 and only Chris can pass it. Job titles are regional; markets are not.

*Evidence it is worth keeping: NC calls a PD role "Early Learning Workforce Manager" and a coach a
"Quality Enhancement Specialist"; Florida ELC vocabulary contains neither, and R4 under-weighted
both until the 2026-08-31 review added them.*

## §0.8 · THE OUTREACH FLOOR — new outreach ships every run

> **Installed 2026-08-25 on Chris's instruction.** ✅ *"There should always be new outreach going out,
> regardless of the number of followups. If no organizations have been researched or pre-loaded for
> drafts, then that needs to be triggered."*
> **Origin: [[CAPA-2026-08-25-empty-new-org-queue]].** `draft_refill` was a LEVEL control with
> one-run latency and zero buffer, so the single run after Chris emptied the queue was the only
> chance to refill it. **Four of six runs drafted zero new organisations and every one passed.**

🔴 **THE FLOOR: every run drafts `target_drafts` NEW organisations, or FAILS and names the gate.**
**"0 owed" is no longer a valid outcome.** Follow-ups are a separate, uncapped queue and have never
competed for these slots — **follow-up volume is never a reason for zero new organisations.**

### 🆕 §0.8.0 · WHEN §0.8's OWN CLAUSES DISAGREE, THE NARROWEST BINDS

🔴 **Installed 2026-09-03 per [[CAPA-2026-09-03-floor-overshoot]].**

**The cascade loop (§0.8.1a) is the OPERATIVE INSTRUCTION.** The pass condition (§0.5) is a **TEST**,
not a licence: it describes the minimum a run must clear, never the maximum it may do.
**T0's refill arithmetic (§0.8.1) sizes ONE tier, not the night.**

⚠️ **Why this belongs here and not in §0.1.** §0.1 ranks rules by CLASS and is silent when two rules
of the SAME class contradict each other. On 2026-09-03 three clauses of this one section gave three
different answers — 10, 18 and unbounded — and the run followed the loosest one and called it a 150%
success. **Same gap §0.1 was written for, one level down.**

### 🆕 §0.8.0a · THE CEILING, AND THE SURPLUS RULE

> ✅ **Chris, 2026-08-20, setting the number:** *"I was thinking of **10 new outreaches a day**. So
> that would mean 10 new organizations."* **That is a RATE.** §0.8 stored it as a FLOOR and the word
> changed without the intent travelling with it.

> ✅ **Chris, 2026-10-08, raising the number:** *"give me 25 new organizations instead of 10 each
> day."* **The RATE is now 25.** `target_drafts` = 25 · `max_new_orgs_per_run` = 25 · `queue_ceiling`
> = 50, moved together in `config.json` so the 2026-08-25 ratio holds (ceiling = 2 × target; one full
> batch always survives a blocked run). Every "10" quoted below this line is HISTORY — the live number
> is always `config.json`, never a figure recalled from this page.

🔴 **`max_new_orgs_per_run` (25 since 2026-10-08; was 10) is a HARD CEILING.** When it and `queue_ceiling` disagree, **the
ceiling wins** — `queue_ceiling` governs the buffer across runs, the ceiling governs Chris's hands on
one morning, **and hands are the scarcer resource.** Every Email 1 costs him a GIF drag, a PDF attach
and three unfamiliar recipients to eyeball.

⚠️ **Overshoot dilutes as well as enlarges.** The cascade RANKS, so organisations 11–15 are by
construction the weakest five. On 2026-09-03 two of them shipped at Redundancy 1 of 3 and one carried
the first Cloudflare-decoded addresses the machine has ever drafted. **The marginal drafts spend the
scarcest attention on the least-verified cards.**

🔴 **THE SURPLUS RULE — research to the cascade's natural stopping point, draft to the ceiling, and
WRITE THE REMAINDER TO [[ready-queue]] with its evidence intact.**
A researched organisation that is not drafted tonight is **not waste — it is tomorrow's T1**, and T1
is the cheapest tier in the cascade. *Origin: the 09-03 run held ~30 gate-passed organisations and
drafted 15 because it had nowhere to put them, while `ready-queue` — which IS T1 — sat empty and 7
runs stale, which is precisely why every recent run had to descend to T3 and re-research from scratch.*

### §0.8.1 · THE CASCADE — descend only when the tier above is exhausted. Never skip a tier.

| Tier | Source | Action | Exhausted when |
|---|---|---|---|
| **T0** | Email 1 drafts already in Gmail | Count them. **Refill when `waiting < target_drafts`. Draft `min(target_drafts, queue_ceiling − waiting)`.** 🔴 **CORRECTED 2026-09-03:** this row previously read *"top up to `queue_ceiling`"*, which with 2 waiting instructed the run to draft **18**, contradicting §0.8.1a's loop (**10**) and §0.5's `>=` (**unbounded**). Three clauses, three answers, no precedence — and the run followed the loosest. **`queue_ceiling` caps the QUEUE across runs; it is never a per-run instruction.** | `waiting >= queue_ceiling` |
| **T1** | [[ready-queue]] — organisations already researched, both gates passed, never drafted | **Draft them.** No new research needed | ready-queue empty of enrollable orgs |
| **T2** | [[discovery-pipeline]] pool — organisations identified but not yet researched | **Research them now:** roster sweep → reverse lookup → R4 rank → card → §0.4 pre-flight → draft | pool holds no un-researched org |
| **T3** | Below `pool_floor` | 🔴 **RUN DISCOVERY AT THE EXTENDED CAPS** — `discovery_extended_fetch_cap` / `discovery_extended_people_cap`. **This is what those keys were always for and they have never once fired** | discovery returns no new organisation |
| **T4** | Cascade exhausted | 🔴 **THE RUN FAILS.** Report `Outreach floor: FAILED — cascade exhausted at T{n}` and say what ran dry | — |

### 🆕 §0.8.1a · THE FLOOR LOOPS. A SHORTFALL IS NOT AN OUTCOME. — Chris, 2026-08-25 (D3)

> ✅ **Chris, 2026-08-25:** *"If the run delivers fewer than the minimum 10 drafts, then the machine
> needs to loop back and run again until there are 10 quality drafts. If more discovery is required
> first, then more discovery must be done."*

🔴 **The cascade is a LOOP, not a single pass.** After the first descent, re-count `new_orgs_drafted`.

```
while new_orgs_drafted < target_drafts:
    if a NAMED §0.8.2 safety gate is active:  stop, name it, report      # legitimate
    re-enter the cascade at the highest tier that now has work
    if T0..T2 are all empty:  RUN T3 DISCOVERY — that is what it is for
    if T3 returns no new organisation:  T4, the run FAILS and says what ran dry
```

🔴 **"16 of 25, T2 exhausted" is NOT a valid stopping point.** It is a signal to run discovery, not a
result to report. **The ONLY legitimate exits are `target_drafts` met, or a NAMED safety gate.**
Capacity, context length, session budget and lateness are **NOT** gates and must never be reported as
though they were.

⚠️ **§0.8.3 still binds inside the loop, and binds harder.** The loop creates volume pressure and
`score_the_attempt_not_the_yield` is the counterweight: **a loop iteration may not lower the bar.**
Roster sweep still gates the descent, R4 still ranks, §0.4 still holds any draft that fails an
assertion, and a correctly HELD org still counts as work done. 🔴 **`target_drafts` quality drafts
(25 since 2026-10-08), or a named gate. Never `target_drafts` drafts of any quality.**

🔴 **T3 IS THE CLAUSE THAT WAS MISSING.** `discovery_extended_fetch_cap: 20` is documented as
*"Used when the batch is empty"* — **and Phase 6 stopped executing on 2026-08-14 and nobody noticed
for four runs.** The cascade makes discovery a *consequence* of an empty queue rather than an
optional phase that can quietly stop running.

### §0.8.2 · THE NAMED GATES — the only legitimate reasons for zero, and each must be named

**A run producing zero new organisations is a FAILURE unless one of these is named in the report,
with its evidence:**

| Gate | Level | Test |
|---|---|---|
| **Bounce rate over `max_bounce_rate_pct`** | 1 — safety | Print the numerator, the denominator and the baseline date |
| **Suppression list not refreshed today** | 1 — safety | `hubspot-suppression.last_refresh != today` — connector down |
| **Unresolved hard bounce** | 1 — safety | Circuit breaker not yet cleared for a named address |
| **Every candidate failed Gate 1 or Gate 2** | 1 — safety | `fail_closed`. Name the organisations and which gate |
| **R1 — every remaining pool organisation is already contacted** | 1 — safety | Market genuinely exhausted in the active cluster |

🔴 **A safety gate stopping the run is the system WORKING. A dry queue is the system FAILING. The
report must never let those two look the same** — which, before today, it did.

### §0.8.3 · 🔴 SCORE THE ATTEMPT, NOT THE YIELD — the anti-gaming clause

**Every run reports `N carded` and `N drafted` as two separate numbers.** An organisation researched
and correctly **HELD** counts as work done, exactly as one drafted does.

🔴 **This clause exists because a raw drafted-count target creates pressure toward bad recipients.**
*Ten easy role inboxes would satisfy a yield target and satisfy nothing else* — see
[[CAPA-2026-08-24-generic-inbox-descent]], where half the Texas batch fell to a generic inbox.
**The floor may never be met by descending the tier ladder faster.** `roster_sweep` still gates the
descent, R4 still ranks, and §0.4 still holds any draft that fails an assertion.

> **This is the mirror of §0.5's redundancy rule.** Redundancy is unscored so that *"don't card the
> hard org"* can never be the cheapest clean report. **The floor is scored on attempts so that
> *"card ten easy orgs"* can never be either.**

### §0.8.4 · THE SLACK LINE — a forward warning, not a post-mortem

**Every report prints `Queue: N waiting · after Chris's sends: M · runs of slack: M ÷ target_drafts`.**

**On 2026-08-24 this would have printed `runs of slack: 0`** — the machine had every number it needed
to predict the empty outbox and printed no warning, because no line asked the question.
**Below 1 run of slack, the report says so at the top.**

### 🆕 §0.8.6 · TERRITORY DISCIPLINE — one state at a time, in order, to saturation

> ✅ **Chris, 2026-09-03:** *"Why are there 7 new states in this one run? I want this machine to be
> systematic and methodical by going county by county across the United States."*

🔴 **THE GATE — LEVEL 2, a hard limit set by Chris. It sits BESIDE §0.7.2, not under it.**
**The floor is met from the ACTIVE territory first, and from the next territory in
`territory.json.order` only after the active one is SATURATED.**

🎯 **THE TERRITORY GATE CONSTRAINS *ORDER*, NEVER *VOLUME* — and that is the whole design.**
§0.7.2's market gate makes the floor **FAIL**, because the next market does not exist until Chris
writes a Green Sheet. **The next TERRITORY always exists and is free under §0.7.2.** So this gate
does **not** fail the floor and does **not** stall the run: a run short of `target_drafts` in the
active territory **saturates it, closes it, opens the next in `order`, and keeps drafting.**
**Crossing territory boundaries mid-run is LEGAL and is reported** — a small state finishes in under
a day and that is the rule working, not failing.

🔴 **Only two outcomes FAIL, both countable, both printed:**
**① a territory opened OUT OF ORDER · ② two territories `IN PROGRESS` at once.** Either means the
walk stopped being a walk.

**SATURATED is a predicate, not a judgement** — `bin/territory_check.py` evaluates it: the territory
is enumerated, every lead agency carries a disposition in `{CONTACTED, HELD, OUT_OF_MARKET,
CLOSED_R1}`, none is `REMAINING`, every `HELD` has a non-empty reason AND a retry date or
`event:` condition, and **`agencies[]` is itemised — a count with no roster behind it is a recalled
number, which is the exact defect this machine keeps finding in itself.**

| Guard | Rule |
|---|---|
| ⚠️ **Thin saturation is flagged, never hidden** | `held / total > 0.30` → `⚠️ <ST> SATURATED THIN`. A state finished mostly by holding is a finding about the state |
| 🔴 **A saturated state RE-OPENS when a held retry falls due** | It jumps to the front of `order` for that run. This is what makes `HELD` honest: **it defers, it does not discard** |
| 🔴 **Enumerate before you draft** | §0.3 step 12b. Enumeration and drafting are **separate acts** and may not occur in the same pass |
| 🔴 **An enumeration failure permits descent to the NEXT territory IN ORDER** | Never to a territory of the run's choosing, and the failing URL and failure mode are printed. **§0.8.3's logic one level up: the floor may not be met by re-ordering the walk, exactly as it may not be met by descending the tier ladder or the market** |

⚠️ **UNIT IS THE STATE, NOT THE COUNTY.** CCR&Rs are multi-county lead agencies — Iowa is five
employers across 99 counties — so a literal county walk would re-hit the same agency and break R1.
**Counties are kept as the SCOREBOARD** (`counties_covered / counties_total`) so Chris still gets
*"we cover 62 of North Carolina's 100 counties"*; **agencies remain the work.**

*Origin: on 2026-09-03 the run touched 23 states and drafted into 9 in one night. It broke no rule,
because there was none — `method.md` contained **zero** instances of `saturat*`, `territor*`,
`density` or `enumerat*`. §0.8.3 forbids meeting the floor by descending the TIER ladder; §0.7.2
forbids descending the MARKET; **nothing forbade changing the TERRITORY — the cheapest door, and the
only one marked "Free."** Nineteen states were left IN PROGRESS and none had ever been finished.
Design: [[PROPOSAL-2026-09-03-systematic-territory-model]].*

## 🆕 §0.8.5 · A HUMAN REPLY OUTRANKS THE INBOX IT CAME THROUGH — Chris, 2026-08-25 (D1)

> ✅ **Chris, 2026-08-25:** *"If someone new replies to the thread, it's likely that there was a generic
> email inbox used and that it forwards to real people. That would be my guess in this case. If a real
> person is replying on the thread, that's great news and we want to foster that new connection. Note
> that I removed the generic inbox from that thread and replied directly to Lori in that case because we
> are now talking to a real person."*

🔴 **A generic inbox is a ROUTER, not a destination.** When a named human replies from an org we
addressed at a role inbox, that is **the organisation revealing the person the inbox forwards to** —
the single most valuable event a generic-inbox send can produce.

| Action | Rule |
|---|---|
| The replying human | 🎯 **PROMOTE to the To** on the next email in the sequence |
| The generic inbox they replied through | ✅ **DROP it.** It has done its job. Keeping it now CC's a router alongside the person it routed to |
| The greeting | Rewrite to the surviving humans. **Never silently drop a name** — R2's parenthetical rule is unchanged |
| Everyone else on the thread | Unchanged. **R5 still forbids ADDING anyone new** |
| [[recipient-profile]] | Record the inbox→human mapping. It is evidence about how that org routes mail |

🔴 **THIS IS NOT AN EXCEPTION TO R5, IT IS R5's OWN CARVE-OUT BEING EXERCISED.** R5 reads
*"ADDING anyone after Email 1 is not [fine] — **unless the org itself named them in a reply.**"*
**A person replying is that person being named by the org, in the strongest possible form: they named
themselves, on the record, in writing.** No new permission is being created here.

⚠️ **`auto_reply_is_never_a_reply` (R17.1) still binds and binds first.** An autoresponder naming a
substitute is **NOT** this rule — it is `ooo_covering_contacts`, which is `harvest-never-add`.
**The discriminator is the same one R17.1 already uses: `Auto-Submitted` / `X-Autoreply` /
`Precedence: auto_reply` headers first, subject prefix second.** A machine naming a human is not the
organisation introducing anyone; **a human replying is.**

*Worked example, 2026-08-25 — [Org 0539]. Email 1 went to `dengel@` with `ccrr@org0320.example`
(generic) on the Cc. [Person 0413] then engaged from outside the thread. Chris put `lwild@` in the To and
removed `ccrr@`. This section is that judgement, written down.*

---

## §0.9 · TWO GATES, TWO QUESTIONS, TWO VENDORS — and the order they run in

> 🔴 **REVISED 2026-08-25 (evening) — CHRIS'S RULING: NO ZAPIER. ZeroBounce runs INSIDE Apollo, as the
> Waterfall-enrichment validator.** Configured by Chris and probe-verified the same evening
> ([[verification-log]] 2026-08-25): a waterfall email result arrives with `emails[].vendor_validation_statuses[]`
> carrying `third_party_validator_name: "ZeroBounce"`, `raw_status` and a timestamp. Probe ground truth: the
> DSN-delivered `person0266@org0798.example` returned `raw_status: valid` for 1 credit; a null
> fill cost 0.
>
> **OPERATIVE SEQUENCE NOW:** S1 Gate 1 harvest → S2 roster sweep with `run_waterfall_email: true` for every
> unpublished Tier-1/2 person (the validator does its work inside that call; the result is ASYNC — poll
> `apollo_webhook_result_show` with backoff up to ~3 min) → S3 R4 rank → E1.7 source-matched validity line →
> S6 pre-flight → draft. **Steps S4–S5 below (per-address Zapier validation of the shortlist + reserve
> promotion) are SUPERSEDED and retained as archive only.**
>
> 🔴 **The validator only sees addresses the waterfall FINDS. It cannot be pointed at an address we already
> have** — confirmed by Apollo's docs, the MCP contract, and the 08-25 experiment. Live-page addresses are
> governed by E1.7's V2/V3 classes, never by a vendor. The verdict rule (hold only on a definitive negative)
> and FOLLOW-UPS NEVER VALIDATE are unchanged.

> **Installed 2026-08-25 on Chris's instruction.** ✅ *"We must have two clear checks for 'is this the
> email inbox of who it says it is', which I think we'd use Apollo for — and then 'is this inbox
> valid' which is something we'd check via neverbounce."*

| Gate | Question | Vendor | Waived for live-page addresses? |
|---|---|---|---|
| **Gate 2** | *Is this the inbox of **who it says it is**?* | **Apollo** | ✅ Yes — the live-page exception, unchanged |
| 🆕 **Gate 2b** | *Is this inbox **valid**?* | **A deliverability validator** — 🎯 **ZeroBounce recommended** (Apollo-listed; also on Zapier). ⚠️ **NeverBounce is NOT an Apollo-supported validator** — Zapier bridge only | 🔴 **NO. Every address, however it was found** |

🔴 **Gate 2b does NOT reopen the live-page exception.** It asks a different question. Chris's 2026-08-11
reasoning — *Apollo confirming she works there adds nothing when the staff page just said so* — is
about **identity** and still holds. **Nothing was asking about validity, and that is the hole
`tony.armadillo@` went through.**

### 🧪 "Apollo only" was tested on 2026-08-25 and RULED OUT — by experiment, not argument

**Five addresses with DSN-confirmed outcomes, one `bulk_match`, 2 credits** ([[verification-log]]):
**a dead mailbox and a working mailbox on the same domain both returned `null`.**
🔴 **A null means "Apollo has no record," never "this address is invalid."** Apollo's MCP surface
exposes no validation endpoint; **waterfall FILLS a missing address, it does not VALIDATE a supplied
one.** **Two questions genuinely require two vendors.**

### THE SEQUENCE — ordered by each vendor's CALL SHAPE, not by preference

**Apollo is bulk (≤10/call) and costs credits. NeverBounce is one-address-per-call and costs
round-trips.** 🎯 **Batch-capable and expensive → sweep BROAD. Per-call and cheap → validate NARROW,
and last.**

| Step | Action | Set | Vendor |
|---|---|---|---|
| **S1** | **Gate 1** — the org's own site. Harvest every Tier-1/2 name and every published address | broad | free |
| **S2** | **Roster sweep** — ONE `people_bulk_match` for every Tier-1/2 person whose address is unpublished. 🔴 **Unchanged — narrowing this re-opens [[CAPA-2026-08-18-unqueried-tier1-roster]]** | broad | Apollo |
| **S3** | **R4 rank** → 1 To + 2 Cc **+ up to 2 named reserves** | ≤5 | free |
| **S4** | 🆕 **Gate 2b on that shortlist ONLY** — never the whole roster | **≤5** | validator |
| **S5** | `invalid` → drop, **promote a reserve validated in the same pass**, re-check U1 and U2 | — | free |
| **S6** | §0.4 pre-flight incl. **E1.7** → draft | — | free |

**Why shortlist, not roster:** a sweep can resolve 8–10 addresses where R4 will use 3. **Validating
the roster costs roughly double and buys nothing.** Validating the reserves *in the same pass* means a
failure costs **no second round-trip.**

🔴 **FOLLOW-UPS NEVER TOUCH GATE 2b.** A delivered address has already proved itself — **delivery is a
stronger validity signal than any validator.** Only Email 1 to a new organisation spends anything.
**Cache each verdict in [[verification-log]] with its date; do not re-validate inside 90 days.**

### The verdict rule — HOLD ONLY ON A DEFINITIVE NEGATIVE

| Result | Action |
|---|---|
| `invalid` / does not exist | 🔴 **HOLD.** Drop it, promote a reserve |
| `catch-all` | ✅ Proceed, flagged — Chris's 2026-08-11 ruling is unchanged |
| `unknown` / timeout / greylisted | ✅ **Proceed, recorded** |
| `valid` | ✅ Proceed |

🔴 **Over-blocking is invisible and permanent; a bounce is loud. That asymmetry always tempts you to
tighten the rule and never shows you the cost.**
⚠️ **Conflict rule: for VALIDITY the validator wins; for IDENTITY Apollo wins.** Apollo can be right
about who someone is and stale about whether their mailbox still exists — **proven on 2026-08-25,
when it returned a departed, hard-bounced recipient as `current: true`.**

---

## §0.10 · SCRIPTS — every number the report prints is COMPUTED, never recalled

> **Installed 2026-08-25 (evening) per [[IMPLEMENTATION-PLAN-2026-08-25-v2]], Chris's instruction to
> fully implement.** The run's division of labour: **scripts produce every number; the run (LLM) reads
> pages, judges people, writes prose; Chris sends and decides.** A report figure that did not come from
> a script artifact is a defect (the rule from [[CAPA-2026-08-25-empty-new-org-queue]] §9b).

| Script (`bin/`) | Phase | Input | Output / report line | Binding? |
|---|---|---|---|---|
| `bounce_rate.py` | COMPUTE | contacted.md · config.json | `runs/<date>/bounce_rate.json` — THE bounce gate number | ✅ **LIVE — gates new-org drafting.** Artifact missing or not dated today → new-org drafting HOLDS |
| `migrate_contacted.py verify` | RECORD | contacted.md | contacted.jsonl + contacted.generated.md + the `Ledger dual-write:` line (round-trip + bounce cross-check) | ✅ LIVE, report-only. **markdown authoritative until 5 clean runs** |
| `ledger_reconcile.py` | COMPUTE | `runs/<date>/sent_sweep.json` *(the run writes it at GATHER: unfiltered 3-day sent sweep per D-SWEEP)* | the appends owed to both ledger forms | ✅ LIVE, read-only |
| `queue_health.py --waiting N` | COMPUTE | N = Email 1 drafts counted in Gmail · contacted.jsonl | `Queue:` + `Pace:` lines + `runs/<date>/queue_health.json` | ✅ LIVE, report-only |
| `preflight.py` | GATE | `runs/<date>/drafts.json` *(the run writes it before ACT — schema in the script docstring)* · config.draft_writer | per-draft verdicts + `runs/<date>/preflight.json` — 🆕 incl. **W1–W4** writer checks (BQ-023, 2026-10-04; only on rows carrying `writer`, so older nights replay unchanged) | 🔴 **SHADOW for ≥3 runs.** Print its verdicts BESIDE your own §0.4 pass; a disagreement is a FINDING to record, and the LLM's verdict governs until 3 consecutive runs agree |
| 🆕 `dedup_check.py <domains...>` | GATE | contacted.jsonl · config.domain_aliases · hubspot-suppression | `CLOSED`/`HOLD`/`CLEAR` + exit code 1/2/0 | 🔴 **LIVE — binds. This IS R1 and R11.** Set intersection over alias groups, never a substring grep. `--audit` prints the `Org identity:` report line |
| 🆕 `calibration.py [--detail]` | RECORD | calibration-log.jsonl | the `Address calibration:` line + `runs/<date>/calibration.json` | ✅ LIVE, report-only. **Measures whether OUR VERDICTS were right** — how far to trust ZeroBounce, Apollo and the orgs' own pages. 🔴 A held address is never sent, so most holds are CENSORED, not scored: `FP = 0` means *we never found out*, never *we don't over-block* |
| 🆕 `run_integrity.py` | **DELIVER** | config.expected_outputs · `runs/<date>/{drafts,drafts_observed,sent_sweep}.json` · the previous run's `drafts.json` | the `Integrity:` line + `runs/<date>/integrity.json` — **existence · agreement · as-sent delta** · 🆕 **draft writer + classifier** → the `Draft writer:` and `Classifier:` lines (BQ-023, 2026-10-04; SHADOW) | 🔴 **LIVE. BINDING for `binding:true` outputs (dossier, review, bounce_rate); SHADOW for the two diffs for 3 runs.** Answers *did the run DELIVER?* — every other script here answers *was the work any good?* |
| 🆕 `dashboard_seed.py` | **DELIVER (last)** | funnel-conversion.json · TLP/dashboard-data.json (current quarter block) | `runs/<date>/dashboard_seed.json` · the seed block in the dashboard HTML · the `Dashboard:` line | ✅ LIVE, report-only. **Never binds, never fails the run.** 🔴 **THE UNIT IS THE ORGANISATION** (Chris, 2026-09-02) — one org replying twice is one Approach. Checks the funnel is coherent and that no stale figure is hand-written into the markup; `--verify` adds a browser read-back where a browser exists. A field with no source renders `—`, never `0`. A **BOOKED** meeting is pending, not a miss, so it stays out of the held-rate denominator |
| 🆕 `run_snapshot.py` | **GATHER (step 2b)** | the live ledgers | `runs/<date>/*.pre-run.*` — the inputs as they stood when the run began | ✅ LIVE, report-only. **Installed 2026-09-26.** What makes tonight replayable |
| 🆕 `cluster.py check` | **GATHER (step 3)** | config.json | the `Cluster:` line — active cluster, its M×M×M, and whether the applied settings match the profile (§0.7.3) | ✅ LIVE, report-only. DRIFT = finding; the profile wins. `apply` is Chris-only |
| 🆕 `build_queue.py` | **RECORD (step 19b, beside run_integrity)** | BUILD-QUEUE.md | the `Build queue:` line + `runs/<date>/build_queue.json` | ✅ LIVE, report-only. Counts table rows; the run never totals the queue by eye |
| 🆕 `replay.py <date> \| --all` | **BUILD-TIME, not in the run** | `runs/<date>/*.pre-run.*` + the next run's snapshots | re-runs every script above against a recorded night and diffs the result (`history/replay/<date>.json`) | 🔴 **Run BEFORE and AFTER any script or config change.** A DIFF is a bug or a deliberate change, and it names which. All 20 recorded runs pass as of 2026-09-26 |
| 🆕 `snapshot.py "why"` | **BUILD-TIME** | method.md · config.json · dossier-template.md · LAUNCHER-*.md · BUILD-QUEUE.md · bin/*.py | `history/<stamp>/…` + one dated line in `CHANGELOG.md`; `--diff`, `--restore` | 🔴 **Every edit to a rule, setting or script ends with a snapshot.** Replaces the `.pre-YYYY-MM-DD` copies. Git could not run here (no delete rights in the Cowork workspace) |
| `learn_diff.py sent.txt template.txt` | COMPUTE | two body files the run saves | `Copy:` line — full-body diff | ✅ LIVE, log-only |

🔴 **THE NO-REWORK LEDGER — `candidates.jsonl` (seeded 2026-08-25, 91 rows).** Before ANY org is
researched or drafted: look up its domain here. `SENT` → **CLOSED under R1, a key lookup, not a prose
rule** — only Chris reopens. `RESEARCH_OWED_GATE1` (the 7 ready-queue survivors) → cheapest T2 work,
take these first. `HELD_*` → touch only when `retry` has passed or its event fired. Not present →
fresh candidate; **append its row the moment its outcome is known**, with status · reason · retry.
The `Rework:` report line is what proves this ledger is being used.

**Artifacts directory:** `runs/<date>/` holds every input the run writes (sent_sweep.json,
drafts.json) and every output a script computes. **A gate reads artifacts, never live calls** —
the number must already exist when the gate fires.

🔴 **A GAP THAT NEEDS CODE GOES TO `BUILD-QUEUE.md`, NOT INTO PROSE (2026-09-26).** When a run finds
that a rule cannot be kept by a script that exists, or needs a script that does not, it appends ONE
ticket to `BUILD-QUEUE.md` (what · evidence · which run) and reports `Build queue: N open`. It does
not patch a script mid-run and it does not write a paragraph here in its place. Build sessions drain
the queue: change → `replay.py --all` → `snapshot.py "…"` → close the ticket.

## 🆕 §0.13a · `X` CLOSES THE SEQUENCE. IT DOES NOT ERASE A NAMED RE-ENTRY CONDITION.

🔴 **Installed 2026-08-27, the moment §0.13 was applied to history — because applying it nearly
deleted three live conditions.**

Some closures arrive with **an explicit invitation to come back**, in the org's own words:

| Org | The condition they named |
|---|---|
| **ELC Polk** | *"When we have Requests for Proposals, I'll be sure to include you"* |
| **ELC Marion** | *"keep your information on file for the future planning"* |
| **[Org 0548]** | *"if it fits current project needs"* |

**All three are `X` under §0.13 — correct.** The automated sequence is over and no follow-up remains.
🔴 **But `X` is a statement about THIS SEQUENCE, not about the relationship.** These organisations told
us how to return, and `warm.jsonl` already carries them as `deferred-named-re-entry`.

| `X` means | `X` does NOT mean |
|---|---|
| No further automated email on this thread. Ever | The org is dead |
| The org is not re-entered by discovery (R1 already closed it) | The named condition is discarded |
| Nothing is owed by Chris | Chris may never approach again |

🔴 **THE RULE: when a reply is classified `X` AND names a condition for re-contact, the machine
records the condition verbatim in `warm.jsonl` with `status: deferred-named-re-entry`, and the review
file quotes it.** Re-entry is **Chris's decision, on his timing, as a new conversation** — never an
automated fourth email. *This is [[OPEN-ITEMS-2026-08-24]] T1.7, which had been open since 08-24 and
would otherwise have been silently overwritten by the new X rule.*

---

## 🆕 §0.15 · HUBSPOT CLEANUP TAGGING — installed 2026-09-22 (Chris)

**Why:** the HubSpot plan caps contacts at **1,000** (802 on 2026-09-22). Every cold send creates a HubSpot
contact through the browser extension. Dead ones fill the cap. **The vault is the permanent record; HubSpot
only needs people who are still in play.**

> **Chris, 2026-09-22:** *"If a contact/organization says 'no thanks' or 'not now' or 'if we need you, we'll
> reach out' or never replies and exits the outreach sequence without ever responding, then they should be
> removed from the hubspot contact list... We should keep the comprehensive records and logs of everything
> here in the vault."* · *"The goal is not to prevent us from recontacting them, the goal is to stay under the
> 1000 contact limit."* · The no-delete safeguard stays: *"the machine will just label those contacts... so I
> can easily filter and bulk delete."*

🔴 **THE MACHINE NEVER DELETES A HUBSPOT RECORD.** It writes ONE contact property and nothing else.
Chris deletes from a saved view.

| Piece | What it is |
|---|---|
| HubSpot property | `outreach_cleanup` (label "Outreach Cleanup"), single-line text. **One value only: `remove`** (Chris 2026-10-07: "I don't need reasons why — just that they're marked for removal"). The reason (`delete_no_reply` · `delete_declined` · `delete_bounced_left`) is recorded in `hubspot-cleanup.jsonl`, not in HubSpot |
| Chris's delete queue | Saved contacts view: "Outreach cleanup is known" → select all → delete |
| The decision | `bin/hubspot_cleanup.py` — deterministic. It never reads reply text; it uses Gmail thread facts, `funnel-outcomes.json`, `warm.jsonl`, `config.json` |
| The permanent record | `hubspot-cleanup.jsonl` — one line per tagged contact: email, HubSpot id, value, evidence, thread, date. Written before the tag. Never pruned |
| Per-run files | `runs/cleanup/<date>/` — `threads.json` (Gmail snapshot) · `candidates.json` · `hubspot.json` · `tags.json` · `report.md` |
| When | Weekly scheduled task, Monday. Separate from the nightly run so it can never break it |

**Tag rules** (full text in the script's header):

| Value | Who |
|---|---|
| `delete_no_reply` | Everyone who **personally** received all 3 emails (to/cc on each) whose own Email 3 went out ≥ **14 days** ago (`config.hubspot_cleanup.grace_days`, Chris 2026-09-30; was 7) on a thread with no human reply. **Per-person count, not per-thread** (Chris 2026-10-07: someone on email 1 only, or added mid-sequence, is not cleanable yet — 4 such contacts were untagged that day) |
| `delete_declined` | Everyone on the thread of an org Chris's confirmed outcomes mark `declined` or `deferred`. **`forwarded` orgs are KEPT** (Chris 2026-09-30: the forwarder may still be a useful contact) |
| `delete_bounced_left` | One person: in `config.hard_bounces` or `config.cleanup_departed` — those two logs are the **sources of truth** (Chris 2026-09-30); no bounce/auto-reply text is read here |

**Never tagged:** a thread with a ★ reply · a thread or address named in an ACTIVE `warm.jsonl` row · anyone
who also sits on an unfinished thread · orgs whose outcome is `live`, `meeting` or `forwarded` (anyone who talked to or met Chris stays — Chris 2026-09-30) · any HubSpot contact with a
deal, a lead status, or a lifecycle stage beyond lead. **Held and reported (D-DOUBT):** a thread with the ⚠
label, an unclassified non-bounce, non-auto-reply message, or a preview that may be truncated and was not read
in full. **Scope:** only threads with the parent label `CCR&R outreach` or owned by a `contacted.jsonl` org row.

**`threads.json` format** (written by the weekly task from Gmail
`in:sent bcc:<HUBSPOT_BCC_ADDRESS> after:2026/08/10`, every page, metadata view):
`{"generated", "query", "preview_limit": 5, "threads": [{"thread", "labels": [Label_ ids across all
messages], "sends": [{"date", "to", "cc"}] (Chris's messages), "others": [{"sender", "date", "subject"}],
"preview_count", "subject", "complete": true only if the thread was read in full with get_thread}]}`.

**Report line:** `HubSpot cleanup: N to tag {by value} · H held · … · HubSpot contacts: X / 1000`.
**Installed with a first batch of 143 selected on 2026-09-22**; never applied (no property, no task). **First real run 2026-09-30 in Cowork** under the revised rules: 148 selected, 130 tagged, 18 writes blocked by the Cowork permission check (`runs/cleanup/2026-09-30-rev/tags-not-applied.json`), 36 held. HubSpot property is a text field (not a dropdown) — filter "is known". Weekly scheduled task still NOT created (Chris declined the approval prompt 2026-09-30). **2026-10-07 run in Cowork:** per-person email count fixed (4 untagged), 225 tagged, **Chris deleted all 225 the same day → 778 / 1000.**

---

## 🆕 §0.16 · THE FOLLOW-UP SENDER — Emails 2 and 3 are sent by the machine. Installed 2026-10-04 (Chris).

> ✅ **Chris, 2026-10-04:** *"Email one is the hardest and the most manual for me and the most important for a human to interact with because it determines who we send the email to… The second and third emails are just follow-ups on the thread of that organization and with those people. And so that part is just timing."* · *"You have my approval to only send emails 2 and 3 and only according to the timeline and instructions outlined in the machine's instructions."* · *"I want those emails to go out at 8:30 a.m. in the recipient's time zone."*

> ✅ **LIVE from 2026-10-06 08:30 ET — Chris, 2026-10-05:** *"I just looked at the outbox and the drafts look good. I'm ready to fully automate emails 2 and 3 so that they can go out autonomously (with the appropriate checks and parameters like: review by the outreach machine to see if Chris needs to review it, appropriate time zone scheduling, any requisite delays based on OOO replies)."* The staged rollout in the approved plan was waived by this ruling; day 1 of the dry run (2026-10-05) is in `runs/2026-10-05/sender/` and the verification log.

🔴 **This supersedes "never send (drafts only)" for Emails 2 and 3 ONLY.** Email 1 is never sent by any machine. The nightly run itself still sends nothing — the sender is a SEPARATE scheduled task (`CCR&R Follow-up Sender`, `CRON_TZ=America/New_York 30 8,9,10,11 * * 1-5`, model Sonnet) whose only program is `bin/followup_send.py` and `config.followup_sender`. Every number and ruling lives in that config block; this section is the mechanism.

### The one design rule — THE GMAIL THREAD IS THE LEDGER

No new ledger, no queue file. Emails sent so far = the count of Chris's own messages on the thread · last send date = the newest of them · the next email's recipients and greeting names = the previous email's To/Cc and first line, as sent (R13: what Chris SENT, including his hand edits) · a send that happened but was not recorded shows up as an extra own message and is therefore never repeated (idempotency). Stop signals are the labels that already exist (★ X ⚠) plus one new one, ⏸ (§0.12).

### A fire, in order — GATHER → COMPUTE → ACT, like the nightly (ARCHITECTURE-v2 §2)

| # | Who | Does |
|---|---|---|
| 0 | session | 🆕 **2026-10-06 (CAPA duplicate sends):** if `get_device_info.connectedFolders` is empty, request `/Users/chrisdanilo/ClaudeVault` ONCE (auto-granted in a scheduled run) and continue; if still absent, abort and say so. Never gather from a mount that is not there |
| 1 | session | `python3 bin/followup_send.py --queries` 🔴 **first takes the LOCK (CAPA 2026-10-06): the run folder is the lock. If another fire of the day has a `queries.json` younger than `config.followup_sender.fire_lock_minutes` and no `followup_sends.json`, it prints `FAIL CLOSED … in flight` and exits 1 — the session reports "yielded to fire X" and stops. A fire that started in the same instant yields (`queries.json {aborted:true}`) and can never plan.** Otherwise it prints the Gmail reads: `config.followup_sender.due_search`, an UNFILTERED `list_drafts` (D-SWEEP), and per candidate thread the thread read + the newest own message's plain-text body. Run them exactly as printed; save every result VERBATIM under `runs/<date>/sender/<fire>/raw/` |
| 2 | script | `--plan` → `plan.json`: one row per thread, **armable / would-send / hold / skip** with the first failing rule as the reason. 🔴 **`plan.json` carries NO params — nothing is sendable until the fresh read (step 2b).** `--plan` repeats the lock check and validates every raw file structurally (16-hex ids, `threadId` = filename, `messageCount` ≥ listed, dates parse); one violation fails the whole fire closed — a transcript with one error is not trusted anywhere |
| 2b | session + script | 🆕 **`--arm` (CAPA 2026-10-06).** Pass 1 prints one `get_thread METADATA_ONLY` per armable row → `raw/arm_thread_<id>.json`. Pass 2 re-derives each row from that FRESH read and arms it only if ALL hold: same message ids as the gather · same own count · no own message dated today (org local) · no stage label for this email · no stop label · no hidden message · not planned/armed by another in-flight fire (**claims**) · read younger than `arm_ttl_seconds` (180 s; older → re-read). Writes `armed.json` — **the ONLY file with send params** — rows `send` / `dropped (reason)`. *On 2026-10-06 the 13:48Z fresh read would have shown the other fire's send + `Label_10` → 0 of 8 armed* |
| 3 | session | **Within the `arm_ttl_seconds` budget:** resolve `{{SIGNATURE}}` and `{{KIT_FILE}}` exactly per `config.followup_sender.zapier.resolve`; call `execute_zapier_write_action` (`reply_to_message`) with each `armed.json` **send** row's params VERBATIM; save each response as `raw/zapier_<thread>.json`. 🔴 While `enabled_emails` lacks that email number the plan prints `would-send` and NOTHING is called |
| 4 | session | Run the Sent read-back queries `--verify` prints (`get_thread METADATA_ONLY` per sent thread → `raw/verify_thread_<id>.json`; Email 3 adds the `has:attachment filename:HST_3PackStarterKit.pdf` search → `raw/verify_kit.json`) |
| 5 | script | `--verify` → `followup_sends.json`: per sent row **sent** (own count = plan + 1 AND the new message's To/Cc/Bcc equal the armed row) / **UNVERIFIED** / **SENT-MISMATCH** (recipients differ — params not passed verbatim) / **DUPLICATE** (two own messages dated today); **dropped** rows carried through; a `raw/zapier_<thread>.json` for a thread that was never armed is an **UNARMED SEND** 🔴 finding. Label flips (`stage_after_send`) are printed for `sent` rows only |
| 6 | session | Apply the label flips. Report ONE line per row **plus every 🔴 finding verbatim**, then the `computer://` link to `followup_sends.json` |

### The decision rules in `--plan`, in order — the first FALSE is the row's reason

1. Today is a business day and not in `never_send_dates`; the holiday list still covers today (else the whole fire **fails closed**)
2. The thread has NO live draft — a draft means the thread is Chris's → `skip — live draft`
3. Own messages on the thread = 1 or 2 → else `skip — stage complete` / `skip — not ours`
4. **No HUMAN message anywhere on the thread.** A DSN (mailer-daemon/postmaster) or an auto-reply (subject prefix — the same R17.1 cheap test `bin/hubspot_cleanup.py` uses) is not a human; anything else from anyone but Chris → `hold — human message on thread`, whatever the labels say. A non-own message whose subject the gather does not carry is fetched (`get_message MINIMAL`) before the rule is decided. *From the history replay, 2026-10-04: on 12 ★/X threads Chris's own reply to a prospect was the newest message, so by message count alone the thread read 'Email 2 sent, Email 3 due' — the labels were the only guard. Now the thread itself is.* **If the newest message is a DSN or an auto-reply** the reply may still go — Zapier attaches it to that newest message, but the sender ALWAYS passes the thread's own subject explicitly (`config.followup_sender.zapier.subject_param_honored`, proven 2026-10-05, BQ-030), so the recipient never sees 'Delivery Status Notification' or 'Automatic reply:' as the subject. With that flag false the row holds and the nightly drafts it. **A DSN newer than the last send whose bounced address is not yet in `config.hard_bounces`/`cleanup_departed` → `hold`** — the nightly records the bounce first (R2), then the next fire drops it with the parenthetical. OOO timing is NOT the sender's call: §0.14 is applied by the nightly through the ⏸ label (rule 5)
5. No ★ X ⚠ ⏸ label on the thread
5b. 🆕 **2026-10-06** The newest own message is not dated today (org local) → else `skip — already sent today`
6. Due = last own send + `sequence_gap_days`, rolled forward past weekends and holidays; today ≥ due → else `skip — not due`
7. The org's local time (state from its `contacted.jsonl` row → `state_timezones`, or `tz_overrides` by mail domain) is inside `send_local_time`–`send_window_end` → else `skip — not in window` (the next hourly fire retries). No state / unmapped → `hold — no time zone`
8. Recipients = previous email's To/Cc minus `config.hard_bounces` and `config.cleanup_departed`. A bounced **Cc** → dropped, R2 parenthetical inserted (first name from Ledger B). A bounced **To** → `hold — To bounced` (who leads is Chris's call). ≥1 recipient must remain
9. Greeting = the previous email's first line (`Names,` on Email 1 / `Hey Names,` on Email 2), bounced names removed; ≥1 name → else `hold — greeting unparsed`
10. Body = the approved copy (Email 2 v4 · Email 3 v3 with its five bolds) rendered from `Cold-Outreach-Sequence-CCR&R.md` per `config.draft_writer.zapier.html_rules`; `bcc = [hubspot_bcc]`; `label_ids [Label_2]`; Email 3 carries `{{KIT_FILE}}`

🔴 **The sender never ADDS a recipient, never edits copy, never calls `update_draft`, never sends Email 1, never sends twice in one fire, 🆕 never runs while another fire is in flight (the run folder is the lock), never sends from a read older than `arm_ttl_seconds`, never trusts a transcript that fails structural validation, and never applies ⚠ — it reports; the nightly judges.** *Why (CAPA-2026-10-06-duplicate-sends): two sessions ran the launcher 6 minutes apart; both planned from a 13:36Z snapshot, both sent, 8 orgs received Email 2 twice. "The thread is the ledger" is only true at the instant it is read — so the sender now reads it twice: once to plan, once, seconds before the send, to arm. The Cowork mount also caches directory listings per session (a sibling's folder was invisible for over an hour), so the lock probes sibling folders by exact name, never by listing alone.* A DSN addressed to `hubspot_bcc` is ignored on read-back. A Zapier failure on one row → that row is `unverified`, reported, and retried by the next fire (rule 3 still protects against a double send).

### What the NIGHTLY does for the sender — three touchpoints, nothing else

§0.3 step 9 maintains ⏸ from auto-replies · step 12 drafts only what the sender cannot send · §0.6 prints `Sender:` and `Scheduled follow-ups:` from `followup_send.py --report-yesterday` / `--preview`. 🆕 **2026-10-06:** `--report-yesterday` also runs the **DUPLICATE SEND AUDIT** over every thread read back yesterday (two own messages on one day = 🔴 line) and repeats every fire's 🔴 findings (UNARMED SEND, SENT-MISMATCH, DUPLICATE, FAILED CLOSED). A 🔴 on the `Sender:` line is a finding for Chris, not a note. The dossier gains a **Scheduled follow-ups** section (the `--preview` table) below the follow-up cards.

🔴 **EVERY HOLD IS A LABEL (`config.followup_sender.holds_are_labels`, 2026-10-05).** A follow-up the nightly holds for ANY reason — an open decision, D-DOUBT, an OOO with no date, a To that bounced, a pre-flight failure — gets `⚠` (needs Chris) or `⏸` (timed OOO hold) on its THREAD in the same step, before the dossier is written. A hold that lives only in the dossier prose does not exist for the sender: on 2026-10-05 both due follow-ups (Bear River USU — D2/D14; SW Iowa — 'until further notice') were held in prose and carried no label, and the sender read both as would-send. Chris clears `⚠` when he rules; the nightly clears `⏸` when the return date passes.

### Rollback

`enabled_emails: []` and disable the task. Step 12 resumes drafting every follow-up the same night because it reads that key. Nothing to undo.

---

## 🆕 §0.14 · OUT-OF-OFFICE — the five rules. RATIFIED BY CHRIS 2026-08-27, in his words.

🔴 **An out-of-office is information, not an invitation.** It tells us three true things: this person
is away, they return on a date, and the org routes urgent work elsewhere. **Two of those are ours.**

🔴 **These five supersede `ooo_return_date`, `ooo_covering_contacts` and the Email-3 timing of R17.
The four-class A/B/C/D triage, `auto_reply_is_never_a_reply`, `ooo_stale_notice`, `ooo_no_date` and
`ooo_departure_sniff_test` are UNCHANGED and still run first.**

### 1 · Never contact a covering contact about a live thread

> ✅ **Chris:** *"Our email is not urgent enough to loop in a covering colleague. We want to respect
> their time and attention, especially because we're reaching out cold."*

No timer, no exception. **Harvest and record; do not use.** They stay an ordinary Gate-1 candidate for
a *first* email at an org never contacted — which R1 makes rare.

### 2 · Wait for the person the email is actually for

🔄 **CHANGED. Supersedes `ooo_return_date: soonest-of-anyone-on-the-thread` (Chris, 08-21).**

🔄 **SUPERSEDED 2026-10-09 (§0.0 R5): one person out never delays — send to everyone on schedule; delay only when EVERY recipient is out.** *Prior text:* **Delay when the To is out.** Reschedule to **their stated return date + 1 working day**.
🔴 **A Cc absence delays nothing.** The To is the wedge buyer; the Cc slots are R2 redundancy.

*Evidence for the change: the old rule required EVERY recipient to be out and therefore **fired zero
times** between 2026-08-21 and 2026-08-27, including a 20-message sweep.*

### 3 · Email 3 waits while the auto-reply is still active

🔄 **CHRIS OVERRULED THE PROPOSAL.** It recommended *"Email 3 never waits"* on the grounds that
delaying a goodbye serves nobody. **His ruling governs: Email 3 delays too, on the same terms as
Email 2 — while the To's out-of-office is still active.**

**"Still active" = the stated return date has not yet passed.** A stale notice is ignored under
`ooo_stale_notice` exactly as before. **A closing gift landing in an inbox nobody is reading is a
wasted goodbye** — which is the better reading, and the proposal had it wrong.

### 4 · Never mention the absence when the follow-up resumes

No *"hope you had a good break"*, no *"circling back now you're returned."* **We know only because a
machine told us. Referencing it turns a considerate delay into a surveilled one.** Send the approved
copy on the new date and say nothing about why.

### 5 · A named successor after a departure CLAIMS the To

> ✅ **Chris:** *"We want to follow their org's instructions, if given, on who to contact in this case."*

🔄 **STRONGER THAN PROPOSED — the proposal said *may* take the To; Chris ruled *should*.**
🔴 **This is a deliberate carve-out from R5 and from `ooo_covering_contacts: harvest-never-add`.**

**Trigger:** an unambiguous **Class B** departure (*"no longer with"*, *"no longer working at"*,
*"inactive mailbox"*) that **names a replacement**. Then:

| | Action |
|---|---|
| The departed address | Suppressed |
| The named successor | **Takes the departed person's slot.** 🔴 **If the departed person held the To, the successor takes the To** |
| The greeting | Rewritten to the surviving recipients. **Never silently drop a name** — the approved R2 parenthetical carries it |
| Everyone else | Unchanged. R5 still forbids adding anyone the org did not name |

⚠️ **INTERPRETATION, FLAGGED FOR CHRIS.** The rule says the successor *claims the To*. Read literally
that would demote a live To when the person who departed was only a **Cc**. **Implemented as: the
successor claims the DEPARTED PERSON'S slot** — the To if the To departed, otherwise the vacated Cc.
**Following the org's instruction should not cost a working recipient their place.** Overrule this and
I will take it literally.

🔴 **Why this is not the R5 problem R5 was written about.** R5 bans adding people because *"it would
look like we are intentionally going around the non-responders."* **There is no non-responder here —
there is a vacancy, and the organisation filled it in writing.** Same logic as §0.8.5.

**Config:** `ooo_return_date: to-recipient-only` · `ooo_email_3_waits_while_active: true` ·
`ooo_departure_successor: claims-the-vacated-slot` · `ooo_covering_contacts: harvest-never-add` *(unchanged)*.

**Report line:** `Auto-replies: … · H held (To out) · S successors promoted`.

---

## 🆕 §0.13 · REPLY CLASSIFICATION — every human reply is sorted into ★ or X. Installed 2026-08-27 (Chris).

> ✅ **Chris, 2026-08-27:** *"If, at any stage of communication, someone replies with a rejection or a
> 'we'll keep you on file' I'd like that to immediately be stored as X closed. There is no more
> followup left for them. If we still have an active conversation or they need a reply from me, then
> mark it ★ replied."*

🔴 **`stop_on_reply` was never enough.** It stopped the sequence but left every reply in one bucket, so
a decline and a live negotiation looked identical. **A reply is now CLASSIFIED, not just detected.**

### The discriminator — one question

🎯 **Does the ball sit with THEM, on THEIR timetable, with nothing owed by Chris?**
**Yes → `X`. No → `★`.**

| → `X` **CLOSED. No follow-up remains. Immediately.** | → `★` **ACTIVE** |
|---|---|
| An explicit no — *"not interested"*, *"no need at this time"*, *"we're already engaged with someone"* | A question, or anything needing Chris to write back |
| **A soft no / keep-on-file** — *"I'll add you to our contact list"*, *"we'll keep your information on file"*, *"we'll reach out if/when we have a need"*, *"I'll include you when we have RFPs"* | A **named hand-off** — *"looping in X, she oversees PD"* — the org has introduced a person (§0.8.5) |
| A **forward with no commitment** — *"I've passed it to the team, they'll contact you if it's a fit"* | A meeting proposed, booked or held |
| | A live back-and-forth still in motion |

🔴 **X IS TERMINAL AND IMMEDIATE.** It fires at whatever stage the reply arrives — Email 1, 2 or 3 —
and **cancels every remaining email in that sequence on the spot.** It does not wait for Email 3 and
it does not wait for the 7-day window. **The org is never re-entered.**

⚠️ **`X` is also reached the quiet way:** Email 3 sent, 7 days elapsed, no reply. Same label, same
finality. **Two roads in, no road out.**

### Why the soft no counts as a no

*"We'll keep you on file"* is a real answer, and the polite thing is to believe it. Following up after
it asks the person to repeat a decision they already made — which is the one thing this sequence is
built not to do. 🔴 **A follow-up sent after a keep-on-file is not persistence, it is not listening.**

⚠️ **The forward-with-no-commitment case is the judgement call, and it is called as `X` deliberately.**
*"They'll reach out if it's a fit"* leaves nothing to follow up on: the ask is already in front of the
decision-maker, and chasing it pressures the forwarder rather than the buyer. **If a forwarded lead
goes cold it is a new conversation later, not a fourth email now.**

### What the run does

| Step | Action |
|---|---|
| Reply detected (human, per R17.1 headers) | Classify `★` / `X` against the table above |
| `X` | Remove the stage label, add `Label_13`. **Cancel every remaining follow-up.** Ledger A status → `🔴 CLOSED — declined / keep-on-file (date, quoted line)`. Quote the sentence that decided it |
| `★` | Remove the stage label, add `Label_12`. Hand off to the warm lane. **Chris writes the reply** |
| Ambiguous | 🔴 **`★` plus `⚠`, and ask Chris.** Never guess a no — over-closing loses a real lead silently, and silence is the one failure mode this machine cannot see |

**Report line gains:** `Replies: N total · A active (★) · D closed — declined or on-file (X)`.

---

## 🆕 §0.12 · FUNNEL STAGE LABELS — installed 2026-08-27 on Chris's instruction

🔴 **Every CCR&R thread carries EXACTLY ONE stage label at all times, plus `⚠` when it needs a human.**

| Label | ID | Meaning |
|---|---|---|
| `CCR&R outreach/0` | `Label_8` | **Draft waiting** — created, not yet sent |
| `CCR&R outreach/1` | `Label_9` | Email 1 sent, no follow-up yet |
| `CCR&R outreach/2` | `Label_10` | Email 2 sent |
| `CCR&R outreach/3` | `Label_11` | Email 3 sent, still inside the reply window |
| `CCR&R outreach/★` | `Label_12` | **A human replied.** Sequence STOPPED |
| `CCR&R outreach/X` | `Label_13` | Closed — no reply. Email 3 + 7 days elapsed |
| `CCR&R outreach/⚠` | `Label_14` | **Needs Chris.** Repair owed, departed recipient, domain question, defect |
| 🆕 `CCR&R outreach/⏸` | `Label_15` | **Hold** — the follow-up sender (§0.16) will not send this thread. Set by the nightly while the To is out of office (§0.3 step 9); Chris may set it by hand as a veto. Not a stage: rides alongside like ⚠ (added 2026-10-04) |

**The parent `CCR&R outreach` (`Label_2`) stays on every thread — it is the umbrella, not a stage.**

### The three mechanics that make it work

1. 🔴 **STAGES ARE MUTUALLY EXCLUSIVE.** Advancing means `unlabel_thread(old)` **then**
   `label_thread(new)`. Skip the unlabel and a thread accumulates 1, 2 and 3 and every count is wrong.
   **`⚠` is NOT a stage** — it rides alongside and is removed only when the underlying issue closes.
2. 🔴 **LABEL AFTER THE MESSAGE EXISTS, NEVER BEFORE.** `label_thread` documents itself as covering
   *"any future messages added to it."* **PROVEN FALSE 2026-08-27:** all 12 follow-ups sent that day
   landed unlabelled at message level on threads that already carried `Label_2`. The parent label went
   +10 for 22 sends. **A thread label buys the messages that exist when you apply it and nothing after.**
3. 🔴 **THE SEARCH OPERATOR TAKES THE DISPLAY NAME, NOT THE ID.** `label:Label_9` returns `{}` with no
   error. `label:"CCR&R outreach/1"` works. **Write tools take the ID; search takes the name.** Getting
   this backwards produces a silent zero — see [[CAPA-2026-08-26-unlabelled-sends]].

### When the run flips them

| Moment | Action |
|---|---|
| Draft created | add `/0` |
| R14 reconciliation finds the send | remove `/0`, add `/1` `/2` or `/3` by position |
| 🆕 R14 finds Chris's send (or scheduled send) of an Email 1 that carried `/⚠` | **remove `/⚠` in the same step.** Chris 2026-10-12: *"if I send an email, it no longer needs the little warning symbol tag. Consider it approved/reviewed."* A ⚠ set at draft time is a pre-send review flag and his send IS the review. A ⚠ raised AFTER his send (bounce, departure, repair owed, duplicate send) is a new issue and stays until it closes. Applied by hand 2026-10-12 to the 12 E1s sent that morning and the 57 scheduled for 10-13/10-14 |
| A human reply is detected | remove the stage, add `/★` |
| Email 3 + 7 days, no reply | remove `/3`, add `/X` |
| Bounce, departure, repair owed, open question | add `/⚠` — and remove it when closed |

⚠️ **Timing choice, Chris 2026-08-27: option C.** `/0` at draft time, the numbered stage at
reconciliation. **A stage label therefore always describes something that was actually SENT** — the
count is never inflated by a draft that has not gone out.

⚠️ **Gmail's sidebar shows UNREAD counts, and sent threads are read — so no number appears next to
these labels.** They give grouping and one-click filtered views; the count shows when the label is
opened. Stated so nobody reports the absent number as a defect.

**Backfilled 2026-08-27 from Ledger A: 54 at `/1` · 17 at `/2` · 13 at `/3` · 10 at `/★` · 0 at `/X` ·
13 at `/⚠` · 0 at `/0`. 54+17+13+10 = 94 = every thread on the parent label. The identity balances.**

## §0.11 · THE FIRST-WRITE SHAPE TEST — now covers LINKS as well as parameters

> **Installed 2026-08-26 per [[CAPA-2026-08-26-google-link-wrapper]].** The shape-test rule already
> existed for `to` / `cc` / `labelIds` and lives in the archive. 🔴 **It is restated HERE, in §0,
> because today proved that an obligation living only in the archive gets SHADOWED by §0.3's shorter
> chain — see [[CAPA-2026-08-26-unlabelled-sends]] §3.**

🔴 **Before drafting, the run performs ONE shape test and prints its result on the `Shape test:` line.**

| Step | Action |
|---|---|
| 1 | Create a throwaway draft to `<SENDER_EMAIL>` carrying three hrefs written CLEAN: `https://www.youtube.com/watch?v=iNCItCda-8g` · `https://chrisdanilo.com/what-hst-looks-like` · one neutral non-Google third-party URL |
| 2 | Read it back with `get_draft` / **`FULL_CONTENT`** |
| 3 | **Record which hrefs came back wrapped in `https://www.google.com/url?q=…`** → [[verification-log]], dated |
| 4 | **Trash the draft** |
| 5 | Print `Shape test:` in the report |

🆕 **2026-10-03 — for Emails 2 and 3 the shape test is the first Zapier draft of the night, read back per `config.draft_writer.zapier.verify`.** The throwaway native draft above still covers Email 1. Report both on the `Shape test:` / `Draft writer:` lines.

**Why the read-back is not optional:** on 2026-08-26 the run wrote
`href="https://www.youtube.com/watch?v=iNCItCda-8g"` and **Gmail returned it already wrapped, before
any send.** A clean href written by the machine does not stay clean. **The only way to know what a
draft contains is to read it back.**

🔴 **DIAGNOSTIC ONLY. This test writes no outreach copy and touches no safety gate.**
**The video link is APPROVED COPY — `machine_writes_copy: never` (level 2) binds, and the fix in
[[CAPA-2026-08-26-google-link-wrapper]] §5 requires Chris's ruling, not the machine's judgement.**

### 🆕 And the free audit channel nobody was using

🎯 **VERIFY RENDERING FROM THE RECIPIENT'S COPY, NOT OURS. On every reply, read the QUOTE BLOCK.**
A recipient's client quotes **what it received** — it is the only view of our email that is not our
own. **This entire CAPA exists because one Outlook user quoted us back and the href in her copy was
wrapped.** Eleven replies have arrived and not one had been read this way.

## Plain language — the rule, and the glossary (added 2026-08-12, Chris's directive)

### 🔴 TERMINOLOGY — "OUTREACHED", NEVER "APPROACHED" (Chris, 2026-08-19)

> ✅ **Chris:** *"Since the TLBS uses the word 'approach' differently, I don't want to use it here.
> Instead let's say 'orgs outreached'. That implies cold."*

**`approach` / `approached` is BANNED in this machine and everything it writes.** It is a
Thought Leaders Business School term with a different meaning, and using it here corrupts the
practice numbers Chris reports to TLBS.

| ❌ Never | ✅ Always |
|---|---|
| orgs approached · approaches · we approached them | **orgs outreached** · **outreached** |
| "N orgs approached of ~667 needed" | **"N orgs outreached of ~667 needed"** |

**Applies to:** the national progress line, [[discovery-pipeline]] §6 funnel and conversion ledger,
[[STATE]] run entries, every review file, and every report. **This file owns the term** — if another
file uses `approached`, that file is wrong.


> **Chris, 2026-08-12:** *"The language being developed and used for this task internally makes it
> sound like it's colloquial but it's invented... I don't have time to read through all the files
> we've generated, I just need this to make sense immediately and be easy to read and understand."*

**Rule: every report must be readable cold, with zero prior context.** Any term of art gets a
plain-English definition in the same sentence, every time it's used — no exceptions, no "see the
docs." Prefer the plain phrase over the shorthand wherever possible.

**The glossary — the shorthand this machine has been using, translated once and for all:**

| Term used in these files | What it actually means |
|---|---|
| **"Golden" / golden reference** | A real email Chris already sent that has the GIF and PDF attached correctly. Forwarding it in Gmail carries the attachments along for free, so Chris can forward-and-edit instead of re-attaching files. Better name, used from now on: **forward-master** |
| **"OBSERVED"** | A fact somebody actually *saw* at a named source — e.g. an address printed on the org's own staff page, or returned by Apollo as verified |
| **"INFERRED"** | A *guess* — e.g. an address constructed from a pattern like "first initial + last name." Guesses never get emailed, no matter who made the guess |
| **"Vendor inference"** | A guess made by Apollo (our data vendor) rather than by us. Apollo labels these "Extrapolated." Still a guess; still never emailed |
| **Gate 1 / "provenance"** | Check 1: did we see this person, title and address on the org's OWN current website? |
| **Gate 2** | Check 2: does Apollo confirm a working mailbox at this address? |
| **ENROLLABLE** | Passed the checks — allowed to be drafted |
| **HOLD** | One check still missing — not allowed to be drafted yet |
| **"Waterfall"** | Apollo's deeper, costlier lookup that checks partner databases when the standard lookup finds nothing. ~2 credits per address vs 1 |
| **"Catch-all domain"** | A mail server that accepts mail to ANY address, so a wrong address never bounces back. We still send (Chris's call), but silence from these proves nothing |
| **"Wedge buyer"** | The person whose job title contains professional development / training / coaching / quality — the person most likely to actually buy training |
| **CAPA** | Corrective And Preventive Action — a short root-cause write-up after something goes wrong, so it can't happen the same way twice |
| **The movement gate** | RETIRED 2026-08-12. Old rule that stopped all drafting if yesterday's drafts hadn't been touched. Replaced by top-up-to-7 (below) |
| **The roster sweep** | Added 2026-08-18. Before picking who goes on an email, ask the vendor about EVERY relevant person at the org whose address the website doesn't publish — in one batched call. Resolve first, narrow second |
| **The roster resolution line** | The counting line every card carries, proving the sweep happened. Nine numbers and three subtractions; if they don't balance, the card is thrown out |
| **`named on page`** | A plain headcount of everyone named on the org's own website. Written `36+` when a staff directory couldn't be read, because the real number is unknown |
| **`resolved` / `held` / `queried-null`** | Three ways a vendor lookup ends. **Resolved** = a usable address. **Held** = the vendor answered but the answer can't be emailed (a guess, or no mailbox). **Queried-null** = the vendor has never heard of them |
| **`deferred`** | Over the 10-people-per-organisation lookup cap tonight. Not forgotten — named on the card and picked up next time |

Reports written after 2026-08-12 use the plain phrases. The old terms remain in historical files;
this table is the decoder.

**It does not re-specify the engine.** Discovery, people-finding, Apollo load and suppression are
defined in [[CCRR-Contact-Engine-Spec]] (2026-06-05, validated on CO/GA/KY, 29 states swept). This
file says what happens on a given night and what may not happen at all.

**Scheduling is handled by Cowork's task settings, not by this file.** Chris, 2026-08-11: *"I don't
think we need the weekday guard because Cowork has that option of choosing when this thing runs in
the automated settings."* Currently `0 3 * * 1-5` — weekdays only, enforced by the scheduler. **The
machine no longer checks the day itself**; a duplicate guard is one more thing that can drift out of
sync with the actual schedule.

---

## ⚡ RUN EFFICIENCY — read this before loading anything (added 2026-08-18)

**The nightly run was reading 490 KB of vault files before doing any work — roughly 120,000 tokens
of pure setup.** That is why long runs degraded: the machine started most of the way through its
useful context before drafting a single email. Refactored 2026-08-18 on Chris's instruction.

### What to load, and when

| Load EVERY run (~150 KB) | Load ONLY when the phase needs it |
|---|---|
| `method.md` (this file) · `STATE.md` · `sequence-tracker.md` · `discovery-pipeline.md` · `Cold-Outreach-Sequence-CCR&R.md` · `contacted.md` · `hubspot-suppression.md` · `recipient-profile.md` | **`CCRR-Contact-Engine-Spec.md`** — discovery only (Phase 6) · **`verification-log.md`** — when writing evidence or checking a prior address · **`golden-references.md`** — only when an Email 1 is drafted · **`dossier-template.md`** — 🔴 **now load it EVERY run that cards an org** — it holds the mandatory roster-resolution line · **`method-rationale.md`** — only when a rule looks wrong · **`CAPA-*.md`** — only to trace a specific past defect |

🔴 **Never load an `archive/` file in a normal run.** The archives hold complete history —
`STATE`, `sequence-tracker`, `verification-log` and `recipient-profile` all have one. Read them only
to trace a specific past event.

### Keep the live files small — this is now part of Phase 4

**The three append-only logs are what grew out of control.** When writing a run's records:

- **Append to the live file, then check its size.** Above ~35 KB, move everything older than the
  last three runs into its `archive/` companion with a verbatim copy and a pointer. **Never delete.**
- **`STATE.md` holds config plus the two most recent runs.** Older run-status entries go to archive.
- **`recipient-profile.md` holds the operative rules only.** Learn-pass observations older than the
  last two runs go to archive once folded into a rule.

🔴 **DO THIS AFTER THE REPORT, NOT BEFORE — P5, added 2026-08-20.** Archive rotation, launcher edits
and dashboard polish all run **after** the report. **The report is the deliverable.** On 2026-08-19
the run put both ahead of the report, the launcher edit threw a permission error, and the report died
with it. **A short report on a partial run beats a complete run nobody sees.**

### 🔴 DESTRUCTIVE — ARCHIVE ROTATION. Read this before touching an archive (P8–P12, added 2026-08-20)

> 🔴 **STOP CALLING THIS HOUSEKEEPING. The word licensed running the run's only data-destroying
> operation at the point of least attention, and on 2026-08-19 it came one obvious retry away from
> silently double-appending 12 KB into an archive.** Full analysis:
> [[CAPA-2026-08-20-housekeeping-nonatomic]].
>
> **Every other step in this run is ADDITIVE** — append a log, create a draft. **Archive rotation is
> the only operation that REMOVES content from a live file.** Treat it with the care given to a send.

#### P8 · WRITE IN PLACE. The filesystem constraints, reproduced 2026-08-20 — dated, re-testable

| Operation | Result | Why |
|---|---|---|
| `cp /tmp/x.md <vault>/file.md` | ✅ **works** | truncates and rewrites in place; no unlink |
| `mv /tmp/x.md <vault>/file.md` | 🔴 **FAILS** — *"inter-device move failed … unable to remove target: Operation not permitted"* | `/tmp` is the sandbox; the vault is a mounted host filesystem. Cross-device `mv` = copy + **unlink of target**, and unlink is refused on the mount |
| `mv <vault>/a.md <vault>/b.md` | ✅ works | same device |
| `rm <vault>/file.md` | 🔴 **NEVER works** | *"Operation not permitted"* |

🔴 **Always `cp` to overwrite a vault file from `/tmp`. Never `mv` across that boundary.**
🔴 **When a delete is genuinely needed, ask via the delete-permission tool — do NOT report it as
impossible.** If Chris declines, **overwrite the file's contents with a tombstone note explaining
what it is and that it is safe to delete, and say so in the report.** Never leave unexplained litter.

#### P9 · ONE IDEMPOTENT TRANSACTION, with a countable idempotency key

**Build the new live file first and verify it. Then do the two writes back to back, with no other
work between them.**

> 🔴 **BEFORE any archive append, `grep -c` the archive for that run's roll-in header
> (`ROLLED IN FROM … <date>`). If it is already present, the append HAS happened — skip it and do
> only the overwrite.**

**That grep is the idempotency key** — a countable object that answers *"did this already happen?"*
without judgement. **If the archive append succeeds and the live overwrite fails, DO NOT RETRY THE
BLOCK.** Re-do only the overwrite. On 08-19 exactly that half-state occurred and the vault survived
on a judgement call, not a control.

#### P11 · Rotation has a floor: it may not fire on a run that has not reported

**Rotate only when BOTH are true: the file is over ~35 KB AND the report has already been delivered.**
Otherwise the manifest records `skipped — report not yet delivered` and it happens tomorrow.
**A file being 40 KB for one extra day costs nothing. A corrupted archive costs history that cannot
be reconstructed.**

#### 🆕 P13 · CUT BY DATED SECTION HEADING, NEVER BY LINE NUMBER — approved by Chris 2026-08-20

> 🔴 **THIS REPLACES LINE-RANGE ROTATION ENTIRELY.** P12 below exists because *"the arithmetic is
> done by hand."* **P13 removes the arithmetic, so most of P12's risk disappears with it.**

**All five rotating files are already organised into dated sections** — `## 2026-08-13 — …`,
`# 🔄 PIPELINE UPDATE — 2026-08-19`, `### 2026-08-20 — …`. **That heading is the cut boundary.**

**The procedure:**

1. **Decide the keep-window:** the last three runs' dated sections plus everything undated
   (frontmatter, config, standing rules, glossaries). **Undated content NEVER rotates** — it is the
   part the nightly run actually needs.
2. **Select by heading, not by offset.** Everything under a dated heading older than the window moves.
3. **`grep -c` the roll-in header in the archive first** — the idempotency key from P9. Already
   present → the append happened; skip it and do only the overwrite.
4. **Build the new live file in `/tmp`, verify it, then two writes back to back** — `cp` to the
   archive, `cp` to the live file. **Never `mv` across the sandbox/vault boundary** (P8).
5. **Verify by heading, not by counting** (see P12, now much cheaper): the roll-in header appears
   **exactly once** · every rotated heading is **present in the archive and absent from the live
   file** · the live file's frontmatter and first heading are intact.

**Why this is safer, stated plainly:** a line range is a claim about a file that cannot be checked
after the fact without recomputing it. **A heading is a string — `grep` answers "did this move?" with
a yes or a no.** The 2026-08-19 splice rolled out lines 56–187 while cutting the live file at 56–177,
**a ten-line overlap that duplicated a section**, and nothing could have caught it except redoing the
subtraction. **Under P13 that error is not possible to make**: a heading is either in one file or the
other.

⚠️ **P13 does not relax P11.** Rotation still runs **only after the report is delivered**, and still
never on a run that has not reported.

#### P12 · Verify the splice — three greps, because the arithmetic is done by hand

**After any rotation, before reporting it complete:**

1. `grep -c` the roll-in header in the archive → **must be exactly 1**
2. Spot-check **3 distinct strings** from the rolled-out range → **must be present in the archive**
3. Confirm the live file's frontmatter and first heading are intact

**The 08-19 splice rolled out lines 56–187 while cutting the live file at 56–177 — a ten-line
overlap, so one section now appears twice in the archive.** Harmless, and entirely because the
boundaries were computed by hand and never checked. **Three greps would have caught it.**

### 🔴 THE REFACTOR RULE — a compression pass must not silently drop an obligation (P7, added 2026-08-20)

> **This section is itself the thing that caused the defect it now guards against.** The 2026-08-18
> efficiency pass rewrote the launcher's file list — which had been grouped by PURPOSE — into a
> two-column table grouped by WHEN TO LOAD. Full analysis:
> [[CAPA-2026-08-20-unreconciled-run-manifest]] §2b.

**Four obligations were deleted as collateral, and every one of them was a WRITE:**

| Deleted phrase | What it obliged |
|---|---|
| **`(refresh as a delta at discovery)`** | 🔴 the suppression list must be **written**, not just read — **the launcher's only independent statement of the refresh obligation** |
| `Update every run` (discovery-pipeline) | the dashboard must be **written** |
| `Name the master you used in every Email 1 report line` | golden-references must be **opened** per Email 1 |
| `SUPPRESSION — all four checked before any draft exists` | the group's purpose, visible at a glance |

**The mechanism, stated generally, because it will recur:** *a list that said what each file is FOR
became a list of what to OPEN.* **The new table has no grammar for "write this," so every write
obligation stated only in the launcher vanished without anyone noticing.** The token saving was real
and the efficiency work was right. **The cost was that a compression pass ran over a document
containing safety controls and nothing checked what fell out.**

**THE RULE:**

0. 🔴🔴 **EVERY SURVIVING OWNER IN THE DIFF MUST BE GREPPED, NOT ASSERTED — added 2026-08-19 after
   the diff got one wrong.** The thin-launcher diff named *"[[method]] Phase 3"* as the owner of the
   Tier-4 greeting rule. **That copy did not exist**, and the rule was orphaned the moment the
   launcher was thinned. **A diff row is not evidence; a grep hit is.** Run the search, paste the
   line number, and if it returns nothing the obligation is an ORPHAN and must be rehomed BEFORE the
   cut — never after.
1. 🔴 **Any pass that shortens, restructures or de-duplicates the launcher, this file, or any program
   file must produce a DIFF OF DELETED OBLIGATIONS and put it in that run's report.** An obligation
   is any instruction to **write, refresh, update, record, or verify** — as distinct from *read*.
2. 🔴 **Redundancy between the launcher and the program files is a CONTROL, not waste.** The deleted
   parenthetical was redundant with Phase 6 — right up until Phase 6 stopped executing, at which
   point it was the only remaining copy. **It was deleted as duplication two days before it was
   needed.**
3. 🔴 **Never remove the last independent statement of an obligation in the name of efficiency.**
   Before deleting any instruction, search for a second live statement of it. If there isn't one,
   the deletion is not a de-duplication.

### 🔴 P7b · THE MIRROR — an ADDED deliverable must be declared in the same session it is invented (added 2026-09-01)

> **P7 guards the DELETION of an obligation. This guards the ADDITION of one, and the machine needed
> both.** Full analysis: [[CAPA-2026-09-01-missing-dossier]].

**On 2026-08-28 a run invented the dossier/review split, executed it well, and never installed it into
§0. The very next run followed §0.3 correctly and the dossier silently disappeared for two mornings.**
Chris found it. **No control could have**, for one structural reason:

🔴 **THE RUN MANIFEST IS GENERATED FROM §0. An artifact that lives only as a habit is invisible to it,
and therefore un-auditable.** The manifest reported 22 of 22 and was telling the truth — *a step that
does not exist cannot be skipped.*

**THE RULE:**

1. 🔴 **Any pass that ADDS a deliverable, an artifact, a file or a recurring output must declare it in
   `config.json.expected_outputs` IN THE SAME SESSION THAT INVENTS IT** — and say so in that run's
   report. **Inventing it without declaring it is not an improvement, it is an orphan.**
2. 🔴 **The declaration is DATA, not prose.** `expected_outputs` is read by `bin/run_integrity.py`,
   which checks existence and freshness. **A rule written in prose depends on the next run reading it;
   a row in a list is checked whether anyone remembers or not.** Same reasoning as P9's idempotency
   grep and `dedup_check.py`'s set intersection: *a countable object beats a judgement.*
3. 🔴 **An artifact can fail three ways and the machine must check all three.** Existence is only the
   first. On 2026-09-01 all three were live simultaneously:

   | Failure | Instance found 2026-09-01 |
   |---|---|
   | **EXISTENCE** — never written | the dossier, missing 08-31 and 09-01 |
   | **EXECUTION** — written nowhere, so its consumer never runs | `runs/<date>/sent_sweep.json` had **never been written on any run**, so `ledger_reconcile.py` — listed **LIVE** in §0.10 since 08-25 — **had never once executed** |
   | **AGREEMENT** — written correctly and never read back | `runs/2026-08-31/drafts.json` was perfect; nothing diffed it against the sent mail, so `As-sent delta` was recalled from memory and printed **M = 0 when M = 5** |

4. ⚠️ **A new output starts `binding: false`** and earns its teeth over three runs, exactly as
   `preflight.py` does in §0.10. **Declaring it is mandatory on day one; blocking on it is not.**

*Origin: three artifacts, three different failure modes, one night, every metric green.*

### Batch the vendor calls

**Use `people_bulk_match` (≤10 per call), not one `people_match` per person.** On 2026-08-18 the run
made 11 individual calls where two batched calls would have done — same credit cost, a fraction of
the round-trips and latency.

### Delegate the research, keep the judgement

🎯 **Discovery and page-reading belong in a subagent; drafting and recipient judgement stay in the
main run.** On 2026-08-18 a delegated pass researched nine organisations at ~190,000 tokens **without
consuming the main run's context** and returned quoted evidence per contact. That is now the default
for Phase 6 and for any batch of Check-1 page reads.

**Brief the subagent with the hard rules verbatim** — own-site pages only, no aggregators, no
search-snippet citations, extract literal `mailto:` strings, never guess a pattern, never assume a
pronoun, report failed reads as failures. **Require quoted lines and exact URLs back.** The main run
still owns tiering, the To/Cc decision, the dossier card and every draft.

## The two gates

**Nothing is drafted to an address that has not passed both.** This is the original design
([[CCRR-Contact-Engine-Spec]] §5.9, D-13), the WA-pilot rule, and the control whose absence produced
the 2026-08-11 hard bounce.

| Gate | Requirement | Owner | Evidence recorded |
|---|---|---|---|
| **1 — Provenance** | Name, title and address read on the **employing org's own site** | Claude | URL · exact quoted line · date (≤90 days) |
| **2 — Verification** | Apollo returns a verified work email on the **org's own domain** | Apollo | `person_id` · `email_status` · enrichment date |

| Gates passed | Tier | May be drafted? |
|---|---|---|
| Both | **ENROLLABLE** | Yes |
| One | **HOLD** | No — verify first |
| Neither | **NOT IN PIPELINE** | No |

### The live-page exception — Chris, 2026-08-11

> *"I want to see their email address on a live website. I also would say that unless the plain text
> document that you pulled is recent within the last six months, then I don't want to use it and we
> need to go and verify."*

**The source medium decides whether Gate 2 is required:**

| Gate 1 source | Gate 2 required? |
|---|---|
| **Live web page** on the org's own site, address in plain text, read within 90 days | ❌ **No — sendable on Gate 1 alone** |
| **Live web page, address inside a `mailto:` link** (e.g. behind a "Send Email" button) | ❌ **No — counts the same as printed text.** ✅ **Chris, 2026-08-12:** *"Yes, it counts, just be sure to pull out the actual email string for use in gmail."* Extract the literal address from the link's `mailto:` target — never retype it, never guess at it — and record it as the quoted evidence |
| **A document** (PDF, brochure, flyer, directory export) — even on the org's own site | ✅ Only usable if **dated within 6 months**, and still needs Gate 2 |
| Document older than 6 months | 🔴 **Unusable.** Re-verify from a live page or Apollo. No exceptions |
| Directory, aggregator, portal, third-party host, or inferred | ✅ Gate 2 required, always |

**A live page is self-updating; a document is a snapshot.** The bounce came from a PDF published in
2024 and hosted on a *third* organization's website — two years stale and twice removed. A staff
page the org maintains today is different evidence, and [Person 0340] is the proof: that address is
published in plain text on United Way's live staff page, and requiring Apollo to confirm it guarded
nothing.

**Record the medium** on every queue row — `live_page` or `document` + its date. That's what makes
this rule enforceable rather than a judgment call.

> **D-13, Chris, 2026-06-05:** *"lets have Claude do the discovery step, and then also the followup
> step where it looks past generic emails and finds specific people on each domain. From there, we
> can hand that list of results to Apollo for enrichment."*
> **Spec §5.9:** *"Claude finds the people, Apollo verifies and sends."*

### Gate 1 — provenance

Four things, together, or it fails:

1. The **URL** of the employing org's own page
2. The **exact quoted line** showing name, title and address
3. A **date** inside 90 days
4. The address domain matches the org's **recorded mail domain**

**If you cannot quote the line, it is not verified.** No inference, no address-pattern guessing, no
directory, no brochure, no "probably."

**Record the org's mail domain once, then enforce it.** Five County's site is `org0174.example`;
every staff address is `@org0389.example`. Anything outside the recorded domain is rejected.

**Organization names are verified too** — from the org's own masthead or About page, never a
directory's label. Unconfirmable → use the template's `your organization` fallback. Never guess a
name into a subject line.

> **Many CCR&R sites publish no addresses at all.** [Org 0163], [Org 0652] and
> [Org 0357] all JavaScript-protect them; several publish phones instead. Of five
> orgs verified 2026-08-11, one published plain-text addresses. When Gate 1 can't be satisfied the
> honest outcome is **"no email address exists for this org"** — route to phone/LinkedIn, never fall
> back to a directory. The name and role are still verified and still valuable.

### Gate 2 — Apollo verification

Per the Pacific/West run (2026-06-06: 39 verified emails written, 81 credits):

1. **Create contacts in Apollo first — creation is free.** Check-before-create; Apollo does not
   dedupe by email on create but does merge by person identity. Role-tag via `label_names`.
2. **D-15 pre-check.** A non-null `person_id` at creation reliably predicts a successful 1-credit
   enrichment. **Enrich only those.** This turns enrichment from a guess into a targeted spend.
3. `people_bulk_match`, batches ≤10, `reveal_personal_emails=false`.

   **If a contact returns no match, run waterfall on it** — `run_waterfall_email: true`. It is
   async: poll `apollo_webhook_result_show` with the top-level `request_id`, backing off up to ~3
   minutes. **This closed 9 of 9 no-match contacts on 2026-08-11 for 17 credits** — including every
   contact at `.gov` and JavaScript-protected orgs that Gate 1 could name but never reach.

   Waterfall returns **ZeroBounce** third-party validation alongside Apollo's own status. **Treat
   `valid` as the strongest signal available and `unknown` as a caution flag** — it is the only
   independent check in the stack. Cost is variable (~1.9 credits/address observed vs 1.0 standard),
   so confirm with Chris before large batches.
4. **`email_status` is a GATE, not a note.** Read it and act on it:

   | Status | Result |
   |---|---|
   | `Verified` | ✅ Passes Gate 2 |
   | **`Extrapolated`** | 🔴 **HOLD.** This is Apollo *guessing from a pattern.* Only passes if a second independent source shows the same address — a live staff page counts; "the pattern looks right" does not |
   | `Unavailable` / null | 🔴 HOLD |

   > **Judge the evidence, not the source.** Ask *what kind of claim is this* — observed or
   > inferred — before asking who made it. **A vendor's inference is still an inference.**
   > On 2026-08-11 `person0052@org0238.example` came back `Extrapolated` (0.7) and reached a live draft,
   > because the rule *"never infer an address from a pattern"* was written against Claude and said
   > nothing about accepting an inference Apollo had already made.
   > Full analysis: [[CAPA-2026-08-11-extrapolated-address]].

   **ZeroBounce `valid` does not satisfy this.** It confirms a mailbox **exists**; it never confirms
   **whose** mailbox it is. It can raise deliverability confidence. It can never establish identity.

   Write verified results back with `contacts_update`.
5. **Reject wrong-org matches.** Apollo matched a CCA-of-WA CEO to a federal agency. Do not write; flag.
6. **Reject domain mismatches.** A [Org 0672] contact returned a Butte College address. Not written.
7. **Flag catch-all domains — but send anyway.** ✅ **Chris, 2026-08-11:** *"The catch-all domains we
   should include even though we lose the error signal. We still want to take that chance."*

   A catch-all domain accepts mail to *any* address, so a wrong address never bounces. **You lose the
   error signal, not the delivery.** Flag it in the dossier and in [[verification-log]] so the
   silence is interpretable — but do not exclude the contact.

   > ⚠️ **The real cost is to the feedback loop, not the send.** On a catch-all domain, *no reply and
   > no bounce* means nothing — it does not confirm the address was good. Never count a catch-all
   > non-bounce as evidence of delivery, and never let one contaminate the bounce-rate calculation
   > in either direction. First flagged on `org0579.example`, 2026-06-06: *"catch-all status means bounces
   > are harder to detect."*
   >
   > **Protocol deferred by Chris** — a proper handling rule (a phone or LinkedIn confirmation step
   > for catch-all sends, or a separate deliverability metric) is a later piece of work, not a
   > blocker now.
8. **Credit accounting — the only valid method** (per [[CAPA-2026-08-12-credit-accounting]]):
   read `num_credits_remaining` immediately **before and after** any spend, in the same run; spend
   = the difference; record both numbers. **Never use `num_lead_credits_used`** — it read 17
   against a delta-verified spend of 46 and appears to count only waterfall charges. **If itemized
   spends don't sum to the balance change, report the gap as "UNEXPLAINED — needs investigation."
   Never invent a category to reconcile it** — that's how a phantom "21 batch overhead" entered
   the records on 2026-08-11.

Every result — pass or fail — is written to [[verification-log]]. No entry, no send.

---

## Fail closed

Every ambiguity resolves toward **not drafting**:

- Gate 1 unsatisfiable → no email address for this org. Route to phone/LinkedIn
- Gate 2 not run, or returns unverified/catch-all → HOLD
- Org name unconfirmed → fallback, or don't draft
- Verification older than 90 days → re-verify
- Queue empty → **draft nothing and say so.** Never "draft what's there"

**A short verified batch beats a full batch with one bad address.** A hard bounce is charged against
`<SENDER_EMAIL>` — the domain that also carries the newsletter and both welcome sequences.

## Bounce circuit breaker

Any hard bounce **halts new drafting**. Then: suppress the address → identify the source that
produced it → **re-verify every other address from that same source** before anything drafts again.

One 2024 brochure produced two addresses on 2026-08-11. The first bounced; the second was still in
Drafts with nothing stopping it. Above `max_bounce_rate_pct` (3%), the machine stops entirely.

---

## Approved copy

**[[Cold-Outreach-Sequence-CCR&R]] only.** The machine never writes body copy — not subject lines,
not openers, not "one tailored sentence." If nothing fits, that is a question for Chris.

> 🔴 **THIS FILE DOES NOT OWN TEMPLATE VERSIONS OR ATTACHMENT FILENAMES. [[Cold-Outreach-Sequence-CCR&R]]
> DOES. Read them there, every run.**
> **Corrected 2026-08-20:** the table below used to name *"Email 1 — v2, Chris's rewrite 2026-08-11"*
> and the attachments `HST_InAction.gif` / `HST_Details.pdf`. **Email 1 was on v6 and the files had
> been renamed to `HST_WorkshopInAction.gif` / `HST_Flyer.pdf` on 2026-08-12 — a rename this very
> file documents two sections further down.** Four revisions stale, inside the program file, while a
> launcher was being rewritten for being one revision stale. **Single ownership, or this recurs.**

| # | Section | Timing | Attachments | Thread |
|---|---|---|---|---|
| 1 | Email 1 — Introduction + Value Prop | Day 0 | inline GIF + flyer PDF — **filenames per the copy file** | New |
| 2 | Email 2 — Short Follow-Up | +7d, no reply | none | Reply on Email 1 |
| 3 | Email 3 — Value Gift + Graceful Close | +7d after #2 | starter-kit PDF — **filename per the copy file** | Reply on Email 1 |

**Only two fields vary:** the greeting (first names, no "Hi" — `Carrie and Stephanie,`) and the
`{{company}}` merge field. Everything else is a literal copy, **including the bold** — the bold is
part of the copy. No handlebars ever survive into a draft.

🔄 **2026-10-04: the Email 3 kit AND the Email 1 flyer are attached by Zapier (`config.draft_writer`); only Email 1's inline GIF remains manual (Chris, 2026-10-04).** ~~2026-10-03: only Email 1's GIF + flyer remain manual.~~ ~~**Attachments are manual.**~~ Content must be passed as base64 inside the tool call (~1.9 MB for the
GIF, per draft) — unusable at this volume. The report names the files and folder every run. Hosting
the GIF at a public URL would remove half this step.

---

## 🔴 NEVER ASSUME A PRONOUN

**Chris, 2026-08-11:** *"Jesse is actually a woman. One thing we're learning is that we should never
ever assume a pronoun for anyone."*

I wrote "he" about **[Person 0278]** based on nothing but the name. It was wrong, and it would have
been wrong even if it had happened to land right — the name was never evidence.

**The rule: refer to people by name and title. Full stop.**

| ❌ Never | ✅ Always |
|---|---|
| "he is not listed on the staff page" | "[Person 0285] is not listed on the staff page" |
| "her org publishes no emails" | "[Org 0163] publishes no emails" |
| "she is not the buyer" | "[Person 0139] is not the buyer — entry-level shared services" |

A name is not evidence of gender. Neither is a photo, a title, or a voice. **The only acceptable
source is the person stating it themselves** — a pronoun line in their own bio or signature — and
even then it goes in the record as a quoted fact, never an inference.

**This is not only a courtesy problem, it's an accuracy problem.** The machine's entire discipline
is "cite it or don't claim it." A pronoun guessed from a name is exactly the same failure as an
address guessed from a pattern — and that one hard-bounced.

*Existing vault files still contain pronouns assumed this way. They are wrong by this rule and get
rewritten to name-and-title as they're touched.*

## PHASE 0 — GATE

1. `STATE.md` → `enabled: false` stops here.

1a. 🔴 **READ `last_run_status` FIRST — P4, added 2026-08-20.**
   If it reads **`IN PROGRESS`**, the previous run **died before finishing.** Do not treat its
   records as complete: **report that it failed, name what it left unfinished, and complete any
   orphaned obligation before starting tonight's.** If it reads `COMPLETE`, proceed.
   **Then immediately write `last_run_status: IN PROGRESS — began <ISO timestamp>` into `STATE.md`.**
   It is flipped to `COMPLETE — report delivered <timestamp>` as the run's **final act**, after the
   report. *Before this existed, a dead run and a clean run left identical records — which is how a
   four-run suppression gap survived four chances to be caught.*

1b. 🔴 **BUILD THE RUN MANIFEST — P1, added 2026-08-20. Before any work.**
   **Materialise every obligation in this file and the launcher as an explicit task** via
   `TaskCreate` — not as prose, not as intention. Roughly 20 items: the two reconciliations, the
   suppression refresh, each phase, each file write, the report.
   **Every task ends in exactly one of three states: `completed` · `skipped — <stated reason>` ·
   `FAILED — <what broke>`. A blank state is not permitted.**
   *Why a task list and not "remember carefully": this machine has five documented cases of a
   remembered rule failing to fire and zero of a counted one. On 2026-08-19 the run created ONE task,
   never updated it, ignored five reminders, and dropped four obligations.*

1c. 🔴 **REFRESH [[hubspot-suppression]] — P6, added 2026-08-20. MOVED HERE FROM PHASE 6.**
   Run the incremental delta (3 filtered queries on records modified since `last_refresh`), then
   **update `last_refresh` in the frontmatter** and log the delta.
   🔴 **This is a GATE: no organisation passes Phase 2 unless `last_refresh` is TODAY.**
   **If the connector is unreachable, that is a REPORTED FAILURE and new-org drafting HOLDS.**
   It is never a reason to draft against a stale list. Due follow-ups still draft — their recipients
   were vetted at Email 1 and are on live threads.

   > **Why it moved.** It lived at line ~1391 inside **Phase 6 — Discovery Increment**, which is
   > optional, bounded and second-to-last. From 2026-08-14 the batch stopped being filled by Phase 6
   > and started being filled by Phase 1 (Florida arrived as one list; Texas the same), so **Phase 6
   > stopped executing and the rebuild inside it stopped with it — four runs, seven days, on a
   > SAFETY control**, while every one of those runs reported its suppression check "clean."
   > **A safety control must never be conditional on an optimisation.**
   > Full analysis: [[CAPA-2026-08-20-unreconciled-run-manifest]] §2b.

1d. 🔴 **THE CONTACT-ONCE GATE — R1, Chris 2026-08-20. THE FIRST QUESTION ASKED ABOUT ANY ORGANISATION.**
   > **Has ANY address at this org's domain ever been on an email we sent?**
   > **Yes → the organisation is CLOSED to new threads. Stop. Do not verify it, do not card it, do
   > not draft it.** Continue on the EXISTING thread or not at all.

   **Checked against [[contacted]] Ledger A.** A bounced To does **not** reopen an org if any other
   recipient was delivered — that is the Five County failure exactly. **"We found someone better" is
   the reasoning this gate exists to refuse.** Only Chris reopens an org; the re-approach route and
   its four conditions are in R1/[[sequence-tracker]]. Full rule: **R1**.

1e. 🔴 **CONTACTED-LEDGER FRESHNESS — R14. A GATE, same standing as suppression freshness.**
   **No organisation is drafted until [[contacted]] contains every send Gmail knows about.**
   1. `in:sent label:Label_2 newer_than:3d` — **3 days, not 1**, so a Friday send survives the weekend
   2. For each thread: org · as-sent To/Cc · date · sequence position · did a bounce follow
   3. Set-difference against **Ledger A (orgs)** and **Ledger B (addresses)**
   4. **Append what is missing.** Never rewrite a row — append a correction line. Re-processing an
      already-logged send is a no-op, which is what makes this safe to run nightly
   5. **Print:** `Contacted ledger: N sends found · M newly logged · current as of <timestamp>`

   🔴 **This is what failed on 2026-08-20** — the ledger was two runs stale and 13 sends made that
   afternoon were invisible to every file.

2. 🔴 **SEND-STATE RECONCILIATION — BEFORE ANY PLANNING. Added 2026-08-18.**
   🆕 **UPGRADED 2026-08-20 TO A FAN-OUT (R13). It is no longer a tracker-only update.**
   **For every thread found in Sent since the last run:** read the as-sent To/Cc **verbatim from
   Gmail** → diff against what the machine drafted → **write the as-sent set to ALL FOUR stores in
   the same pass** ([[sequence-tracker]], [[contacted]] both ledgers, [[verification-log]] marking
   human-confirmed recipients, [[discovery-pipeline]] counts) → **append an `AS SENT — CORRECTIONS`
   block to the ORIGINAL run's review file** (append, never rewrite — the machine's error is the
   learn data) → **print `As-sent delta: N reconciled · M recipient changes by Chris · [org: drafted X → sent Y]`.**
   🔴 **`M > 0` is the LEARN SIGNAL, not a defect** — Phase 5 already calls a Chris-added recipient a
   defect report. **Six such changes went unanalysed in one week because nothing collected them.**
   Read `list_drafts` and reconcile it against [[sequence-tracker]] **before deciding anything about
   tonight's batch.**

   > **Why this moved to the front.** Phase 4 already runs an orphan recovery, and it is correct —
   > but it runs at the *end* of a run. **Chris sends between runs.** On 2026-08-18 the tracker
   > recorded *"Still in Drafts: 3"* and was accurate when written; thirty-four minutes after the run
   > closed, Chris sent two of the three. **The tracker was not violated, it was stale** — nothing
   > reconciles in the window between runs, which is exactly the window in which every send happens.

   | Finding | Action |
   |---|---|
   | Tracked as DRAFTED, **not in `list_drafts`** | Check Sent. Found → mark **SENT**, record the **as-sent To/Cc verbatim**, set `next_due` = sent + 7 days, **and append the org + every as-sent address to [[contacted.md]]** |
   | In `list_drafts`, **not tracked** | Orphan. Record with a `RECOVERED` note, or trash if it duplicates |
   | Tracked and present | No change |

   🔴 **Record the as-sent recipients, not the as-drafted ones.** Chris edits recipients at review —
   on 2026-08-18 he added `dengel@` and `slindsey@` to the Escambia thread by hand. Those are
   human-confirmed and the follow-ups inherit them, so a tracker holding the drafted set would send
   Email 2 to the wrong people.

   **Gmail is the authority on what exists. The tracker is the authority on what it means.**
3. 🔴 **THE MAILBOX-WIDE BOUNCE SWEEP — R12.1, 2026-08-20. ONE SEARCH, NOT A PER-THREAD LOOP.**

   **`in:anywhere from:mailer-daemon newer_than:7d`** — whole mailbox, every run, no sampling.

   > 🔴 **The old wording said "check each open sequence's thread," and in practice every run checked
   > only the threads with follow-ups due that night.** Two hard bounces from 2026-08-17
   > (`ccr@org0315.example`, `person0936@org0323.example`) sat outside that sample, and **three consecutive
   > runs reported "Bounces: 0 new, breaker clear"** against a mailbox holding them. **A sample is not
   > a sweep.** One call costs nothing and needs zero judgement.

   🔴 **AND THE BOUNCE LINE REPORTS OUTSTANDING STATE, NOT NOVELTY — R12.2:**
   **`Bounces: N new · M suppressed addresses open · R repairs owed before <date>`**
   **"Breaker clear" means NOTHING OUTSTANDING.** It may never mean "nothing new since yesterday."

   🔴 **A DSN NAMES EXACTLY ONE ADDRESS. Record the outcome PER ADDRESS in Ledger B**, never as
   "the org bounced." A send with one dead recipient and two live ones has two people who received it
   — **that is the fact Five County lost.**

3a. Read [[sequence-tracker]]. For each open sequence, check its Gmail thread:
   - **Reply** → `REPLIED`. **Stop that sequence immediately** and flag it. A reply is the point.
   - **Sent** → `next_due` = sent + 7 days.
4. **Any unresolved hard bounce → stop.** See the circuit breaker.

### ~~The movement gate~~ → TOP UP TO 7 — Chris, 2026-08-12 (set at 5, raised to 7 the same day)

**RETIRED:** the movement gate (stop drafting if yesterday's drafts weren't touched).
**REPLACED by a simple refill rule:** *"I want it to top up to 5 drafts."*

### 🔴 REVISED 2026-08-18 — TWO SEPARATE QUEUES. FOLLOW-UPS NEVER CONSUME THE NEW-ORG TARGET.

> ✅ **Chris, 2026-08-18:** *"Let's adjust the rules here so that 7 new emails can go out while
> followups are going out simultaneously. Since all the manual human work for me is done at the
> first email (checking names/organizations/domains/etc.) the followups are much easier to send."*

**What broke.** On 2026-08-18 eight Email 2 follow-ups came due. The old rule counted them toward
`target_drafts`, they filled the queue, and the "7 or more waiting → draft nothing new" line then
barred every new organization. **Zero organizations were approached.** Because Email 2 and Email 3
come due on a rolling basis forever, that outcome would have repeated every night from then on —
making the ~667-organization goal, whose whole arithmetic assumes **7 NEW organizations per working
day**, mathematically unreachable.

**The fix: follow-ups and new approaches are counted separately, and never compete for a slot.**

| Queue | Rule | Cap |
|---|---|---|
| **Follow-ups** (Email 2 · Email 3) | **Every due follow-up is drafted, every run, unconditionally.** They are obligations with dates on them, not discretionary fill | **No cap.** 8 due → 8 drafted |
| **New organizations** (Email 1) | **`target_drafts` (7) minus the number of Email 1 drafts already waiting.** Only *Email 1* drafts count against this | 7 |

**A night's output is therefore `(all due follow-ups) + (up to 7 new organizations)`.** On 08-18
that would have been 8 + 7 = 15 drafts, not 8.

**Why the asymmetry is correct, in Chris's own reasoning:** the expensive human work — checking
names, organizations, domains, deciding who belongs on the thread — **all happens once, at Email 1.**
A follow-up inherits every one of those decisions. So a follow-up costs Chris seconds at review and
costs the machine no verification at all, while a new organization costs both. **They are not the
same unit of work and must not share a budget.**

🔴 **The old shortfall test still applies, but only to the new-organization queue.** "5 of 7 — the
other two died at [org] (page unreadable), [org] (contact left)" is a valid night. **Under-filling
the new-org target while budget sits unspent is a defect and the report must say so.** Follow-ups
never count toward that 7 and can never mask a shortfall in it again.

### 🔴 FOLLOW-UPS INHERIT THE EMAIL 1 THREAD'S RECIPIENTS — including Chris's own additions

**Ratified 2026-08-18 by the same instruction:** *"all the manual human work for me is done at the
first email."* **The vetting that licenses a recipient happens at Email 1, and Chris's review is
part of that vetting.** So:

- **A follow-up reuses the recipient list of its Email 1 thread as sent**, including every person
  Chris added by hand at review.
- **A recipient Chris personally put on a live thread is HUMAN-CONFIRMED** and is recorded that way
  in [[verification-log]]. It is not pulled again on later emails in that sequence.
- **This does NOT loosen the gates for new organizations.** Email 1 recipients still require both
  checks. The exception is scoped to follow-ups on threads a human already approved.

**Why this rule exists.** On 2026-08-18 the machine pulled four human-added recipients from the
follow-up drafts because they had no verification-log entry. Chris then sent the Blue Ridge
follow-up greeting **"Hi [Person 0478] and Jesse,"** — with [Person 0278] not on the email, because the
machine had removed the address. **A greeting naming someone who is not a recipient is a visible
defect in front of a prospect**, and it was caused by the machine second-guessing a decision a human
had already made and already sent on.

| Situation | Action |
|---|---|
| Any follow-up due today | ✅ **Draft it. Always. No cap, no competition with the new-org target** |
| N Email 1 drafts waiting (0 ≤ N ≤ 7) | ✅ **Draft (7 − N) new orgs** |
| 7 or more **Email 1** drafts waiting | ✅ Draft no new orgs; still draft every due follow-up |

A waiting draft is never re-created and its org is never re-drafted.
Replies and bounces still stop their own sequences regardless of any count.

## PHASE 1 — FILL THE BATCH TO 7. THIS IS THE RUN'S JOB.

> 🔴 **Root cause of the 2026-08-11 one-draft night, so it never recurs:** the old phase order
> treated "run discovery" as a valid destination for a night. The run enriched 24 contacts in bulk,
> read only 3 staff pages, found 1 fully-verified org, drafted it, and declared success — because
> nothing said *the number of drafts is the goal*. Discovery is a means. **The draft target is the goal — 7 as of 2026-08-12.** Chris's pacing math: ~96 working days remain in 2026 (101 weekdays minus 5 federal holidays); 7 drafts/working day ≈ 670 orgs ≈ the ~667 the 2027 goal requires. Expect this to rise as process and habit consistency improve.

🔴 **No draft without its dossier card, ever — including top-up and daytime runs.** The 8/12
daytime batch drafted six orgs with the evidence in the verification log but no dossier; Chris
reached his send review and the dossier wasn't there. The per-org loop is **verify → dossier card
(per the evidence protocol in Phase 2) → draft** — the card is written the moment the org clears
the checks, appended to `review-YYYY-MM-DD.md`, never back-filled after drafting.

**The target is `target_drafts` (7) minus drafts already waiting. The run works this loop, org by
org, until the target is met or every source and budget is exhausted:**

1. **Due follow-ups first** (oldest `next_due`) — these cost nothing to verify, they're already
   verified orgs mid-sequence.

   🔴 **BEFORE BUILDING EACH FOLLOW-UP, RUN THE R2 BOUNCE HANDLER.** `followup_recipients` inherits
   the Email 1 set **as sent** — including anyone who bounced. **Check every inherited address against
   Ledger B's `bounced` state first.** If one bounced: drop it · rewrite the greeting to the survivors
   · **insert the approved bounce parenthetical from [[Cold-Outreach-Sequence-CCR&R]]** — Chris's own
   wording, never improvised · print `Redundancy: N of 3`.
   **Never let a name silently disappear between emails** — the remaining recipients read that as
   concealment. Full rule: **R2**.

   ⚠️ 🆕 **A `HELD` org with a LIVE thread and at least one delivered recipient still appears in this
   due list**, flagged rather than skipped. **Five County's Email 2 was two days late because a HELD
   org was excluded from the sweep entirely.**
2. **Ready-to-draft orgs** (both checks passed) from [[discovery-pipeline]] Stage A.
3. **One-check-away orgs, cheapest conversion first** ([[discovery-pipeline]] Stage C):
   - **C-1 — vendor-verified, needs a staff-page read.** Read the org's own staff page (~1 fetch).
     This satisfies Check 1 AND finds the PD/training person for the Cc. **Verify → write the org's
     dossier card → draft → immediately move to the next org.** Never batch all the reads first and draft later —
     per-org completion is what guarantees drafts exist even if the run dies midway.
   - **C-2 — seen on their site, needs vendor verification.** Standard Apollo match (1 credit), and
     if no match, **waterfall it** within the standing budget (below).
   - **C-3 — loaded but never verified.** Free pre-check, then match the promising ones.
4. **Only if the target still isn't met:** new-state discovery per the order in
   [[discovery-pipeline]] §3, spending up to the extended caps.

**A short batch must name its shortfall.** "5 of 7 — the other slots died at: [org] (page
unreadable), [org] (contact left the org)" is a valid night. "1 of 5" with budget left unspent is
a defect, and the report must say which budget went unspent and why.

### 🔴 UNSPENT LOOKUP BUDGET IS A DEFECT SIGNAL, NOT THRIFT — added 2026-08-18

**The 2026-08-18 report recorded *"deeper-lookup budget: 0 of 25 used"* twice, as a clean line item.
It was the symptom.** That same run left six named, unpublished Tier-1 people at one organisation
unqueried. **The report presented the cause as good housekeeping.**

**Every report must now compute and print this pairing, in this shape:**

> `Lookup budget: N of 25 spent · Tier-1/2 people left unqueried across the batch: M`

🔴 **If `M > 0` while budget remains, the report states it as a DEFECT and names the orgs.** Not as
a saving, not as an efficiency. The only clean version of that line has `M = 0`.

**Thrift is never the goal here.** A credit is ~1/1000th of the per-run cap and the budget has been
closing at zero for a week. The scarce resource is organisations, not credits — and every unqueried
Tier-1 person is an organisation reached less well than the evidence allowed.

### Standing waterfall budget — Chris, 2026-08-12

**Up to 25 credits per night on waterfall lookups, no per-run approval needed.** (~12 addresses at
the observed ~2 credits each.) Spend it on Stage C-2 no-matches, highest-tier contacts first.
Verify the spend by balance delta and itemize it in the report. Beyond 25, hold and ask.

## 🥇 THE PREFERRED RANKING — how to decide WHO an email is addressed to

> ✅ **Chris, 2026-08-18, and this is the governing principle for the whole section:**
> *"This field is too fractured and inconsistent to have a super predictable method that works the
> same every time. We're going to need to rely on my judgement and discernment as we bump into new
> edge cases and situations. That said, we need a 'preferred ranking' system that we use to help
> decide when and how to write drafts."*

**Read this before the roster gate.** The old rules were pass/fail: an organization either produced
a verified named person or it was held. **That threw away reachable organizations** — three were
held on 08-17 and two on 08-18 for "no address published," when a worse-but-real option existed.

**The ranking replaces pass/fail with descend-until-you-can-send.** Work down the tiers. **Take the
highest tier the organization actually supports, draft it, and record which tier fired on the
dossier card.** Only the bottom of the ladder is a hold.

| Tier | What it looks like | Draft it? |
|---|---|---|
| **1 · BEST — multiple named people, personal addresses** | 1 To + up to 2 Cc, every address personal and verified. The decision-maker plus the training/PD buyer | ✅ Always. This is the target |
| **2 · One named person, personal address** | Only one person at the org is reachable. Address them by name | ✅ Yes. A one-recipient thread is a good thread |
| **3 · Generic inbox, addressed to a NAMED person** | The org publishes only `info@` / `ccrr@` / `training@`, **but its team page names the people.** Send to the generic inbox and **open the email with the right person's name** | ✅ Yes — see the generic-inbox rules below |
| **4 · Generic inbox, nobody nameable** | No staff page, no names anywhere. A human still reads that inbox | ✅ Yes, with a non-specific greeting |
| **5 · HOLD** | No address of any kind, generic or personal, that passes verification | 🔴 No. Route to phone/LinkedIn and record why |

🔴 **Never skip a tier to avoid work.** If tier 1 is achievable with one vendor lookup inside budget,
tier 2 is not an acceptable answer. The ranking is a fallback ladder, **not a menu.**

🔴 **AND YOU MAY NOT DESCEND UNTIL THE ROSTER SWEEP HAS RUN — 2026-08-18.** *"Descend until you can
send"* was read as *"stop as soon as you can send."* On 08-18 that produced a tier-3 generic inbox at
[Org 0539] while **six untested Tier-1 candidates sat on the same page.** The ladder measures what
the organisation **supports**, and you cannot know that until every Tier-1/2 candidate with an
unpublished address has been submitted to the vendor. **Sweep, then descend.** See Phase 2.

**Record the tier on every dossier card** — `Recipient tier: 3 (generic inbox, named greeting)` —
so the ranking's real-world distribution becomes visible over time and Chris can retune it.

### 🟢 TIER ON THE ROLE, NOT THE TITLE KEYWORD — APPLIED 2026-08-18

**This closes the oldest open question in the machine.** It was raised five times — [Person 0005]
and [Person 0549] (08-13), [Person 0001] (08-14), McKenna Terrill and the whole ELC of Flagler and
Volusia roster (08-17) — each time as *"the tier list reads TITLES, Chris reads ROLES."* Each time
the rule was to raise it and not apply it. **Applied now, under Chris's 2026-08-18 instruction to
implement the outstanding decisions.**

**The old rule:** a person was Tier 1 only if their *job title* contained professional development,
training, coaching or quality.

**The new rule: tier on evidence of the role from ANY part of the organisation's own page.**

| Signal on the org's own page | Tier |
|---|---|
| Title contains PD / training / coaching / quality / **CCR&R** | **1** *(unchanged)* |
| **The page names this person as the contact for a training programme, a bonus, a calendar, a coaching initiative or provider development — even if their title says none of it** | **1** 🆕 |
| Their biography on the org's site describes them delivering or designing training | **1** 🆕 |
| Practice-quality roles without a training word | 2 |
| Distribution / communications | 3 |

**Worked example — the case that forced it.** [Person 0001] at ELCHC: her address is published on the
leadership page and the page names her as the contact for the **training achievement bonus** — an
unambiguous training job — but **the page never states her title**, so under the old rule she could
not be tiered and was excluded. Under this rule she is Tier 1 on role evidence.

🔴 **The evidence discipline does not loosen.** Role evidence must be **quoted from the org's own
page**, exactly like an address, and recorded on the card: *"named on the leadership page as the
contact for the training achievement bonus."* **An inferred role is not evidence.** A person whose
training role rests only on a job-board posting, a LinkedIn headline, or a vendor's department
tag stays at their title-based tier.

**Reversal is one line** if Chris finds it puts the wrong people on threads.

### 🟢 SPEND THE LOOKUP WHEN A KEY PERSON IS NAMED BUT UNREACHABLE — RATIFIED 2026-08-18

> **The candidate rule raised after [Person 0176] (08-13) and [Person 0237] (08-14), applied
> deliberately on 08-17, and ratified now.**

**When a Tier-1 person or a decision-maker is named on the organisation's own page and no address is
published for them, spend the vendor lookup rather than filing them as unreachable.**
*"Not published" is a fact about the website, not about whether the person is reachable.*

**The evidence this works is the strongest in the machine's record.** On 2026-08-17 that rule turned
three organisations that publish no usable addresses — ELC Alachua, [Org 0564], [Org 0803]
— into three of seven drafts for ten credits. **ELC Alachua then produced the best reply the system
has had**: the CEO named the professional-development owner, put her on the thread, and committed to
a discussion.

**Budget discipline:** highest-tier contacts first, inside the standing 25-credit nightly allowance,
spend verified by balance delta and itemised in the report. **The deeper-lookup budget has gone
almost entirely unspent on recent runs** — 0 of 25 on 08-18 — so the constraint is not money.

⚠️ **A lookup that returns nothing is still a valid outcome**, and it happened twice on 08-18
([Person 0583], [Person 0352]). Record the person as `🔍 VENDOR QUERIED — no match`, take the ranking's
next tier, and never guess a pattern from a colleague's address.

🔴 **THIS RULE HAS AN OBJECT NOW — see THE ROSTER SWEEP in Phase 2.** As written above it is a
permission with no completeness test, and on the day it was ratified it fired for two of nine
eligible people at [Org 0539]. **It is not satisfied by spending one lookup.** The sweep names
exactly who must be submitted and the card carries the count.
Full analysis: [[CAPA-2026-08-18-unqueried-tier1-roster]].

🔴 **The old phrase `identified, address unknown` is retired** — it hid the difference between a
dead end and an unasked question. Use the three states in Phase 2.

### 🔴 GENERIC INBOXES — the rules, Chris 2026-08-18

> ✅ **Chris:** *"One of the things I've realized is that the turnover is so high in this field and
> the processes are so basic that some of these generic email inboxes are actually monitored more
> closely than I initially thought. So, I would always prefer to send to a real human being, but if
> there are no alternatives, it's still worth running the generic email inbox through Apollo for
> verification and then drafting an email. Also, just because the email address is generic doesn't
> mean that the correct people aren't listed on the team's website. We may still address to a
> specific person even when the email address looks generic."*

**This reverses the standing prohibition.** The old rule — *"Generic `info@` inboxes never on the
visible thread"* — was written when the assumption was that nobody reads them. **In this sector that
assumption is wrong**, and the reasoning is structural: high turnover plus basic processes means the
shared inbox is often the most reliably-monitored address at the organization, precisely because no
individual owns it long enough to matter.

**The four rules:**

1. **A real human always beats a generic inbox.** Tier 3 is a fallback, never a shortcut. If a
   personal address is obtainable — published, or resolvable with a lookup inside budget — get it.
2. **A generic inbox still needs verification.** Run it through the vendor like any other address.
   Chris: *"it's still worth running the generic email inbox through Apollo for verification."*
   **A generic address is not exempt from Check 2 just because it is obviously real-looking.**
   ⚠️ Expect vendor coverage of role inboxes to be patchy. **If the vendor returns nothing but the
   address is published as plain text or a `mailto:` on the org's own live page, Check 1 stands on
   its own** — same as any other live-page address. Record which check carried it.
3. 🔴 **A generic address does NOT mean an anonymous greeting.** This is the rule that gets missed.
   **Check the team page for names even when the only address is generic**, and address the email to
   the right person by name. `To: ccrr@org0320.example` with the greeting `Skyey,` is a tier-3 send
   and it is *far* better than `Hi there,`. The address routes the mail; **the greeting aims it.**
4. **Only when nobody is nameable does the greeting go generic** (tier 4). Even then, send.

> ## ✅ THE TIER-4 GREETING — RATIFIED BY CHRIS 2026-08-19
>
> **Form: `<ORG'S OWN SHORT BRAND> team,`** — e.g. `ELCFH team,`
> The Email 1 convention (bare, **no salutation word**) using the organisation's **self-used short
> brand**, with no names because none are obtainable. First used at [Org 0550] on
> 2026-08-19; **Chris ruled the same day: *"keep the tier 4 greeting ruling."***
> **It is the standard for every tier-4 send and is no longer flagged as a placeholder.**
>
> 🔴 **A settled greeting is NOT permission to reach tier 4 cheaply.** A tier-4 send still requires a
> completed **reverse lookup** (Phase 2) and a `Reverse lookup:` line on the card. **ELCFH itself
> stopped being tier 4 within a day of that lookup being run** — it now goes to a named director.
>
> 🔴 **PROVENANCE NOTE, recorded because it matters more than the rule.** This ruling lived ONLY in
> the launcher. The 2026-08-19 thin-launcher obligation diff named *"[[method]] Phase 3"* as its
> surviving owner — **and that copy did not exist.** The diff asserted an owner instead of verifying
> one, and the rule was orphaned for roughly an hour until it was caught by trying to edit it.
> **The lesson is now law: an obligation diff must GREP for each surviving owner, never assert it.**
> See the amendment in [[LAUNCHER-thin-PROPOSED]] §2.

**Never put a generic inbox and a personal address on the same visible thread without a reason** —
if a personal address exists, the generic one is redundant. The exception is Chris's own ELC of the
Big Bend pattern (2026-08-17), where two department inboxes were used *as the route to two named
people whose addresses were unpublished*. That is tier 3 done deliberately.

### 🔎 ADJUDICATING A CONFLICTING OR MISSPELLED ADDRESS — Chris, 2026-08-18

> ✅ **Chris:** *"Refer to the actual spelling of the contact's name and compare to what is most
> likely the correct spelling of the email address. If this happens, one effective way to confirm or
> verify is first by reviewing the rest of the website to see if there are other instances of the
> email address or the name. If there are 4 listed instances of the email address and they're all
> consistent but only one is different, then we have a high degree of certainty that it's a typo and
> we should feel confident moving forward. If the misspelling is genuinely confusing or if it feels
> too close to call, try running it through Apollo for verification. That's a worthy token spend."*

**This is now the standard handler when one organization publishes two spellings of one address.**
It replaces the previous reflex, which was to hold both values. **Holding both is still correct when
the two addresses point at two different *people*** (the Schoharie case). This procedure is for when
they point at the *same* person and one is simply mistyped.

**Run these in order and stop as soon as you have an answer:**

1. **Compare each spelling against the person's printed NAME.** `[Person 0516]` → `phouston@` is a
   name; `phoutson@` is not a word. **Usually decisive on its own.**
2. **Count instances across the whole site.** Four consistent occurrences and one outlier is a typo,
   with high confidence. Consistency across *pages* counts for more than repetition on one page.
3. **Check the org's own naming convention.** If every other address is first-initial + surname, an
   address that breaks the pattern is the suspect one.
4. **If it is still close to call, spend the vendor lookup.** Chris: *"That's a worthy token spend."*
   ~1 credit to avoid a bounce on a domain we may only get one shot at is a good trade — and it is
   cheap next to the 25-credit nightly budget that routinely goes unspent.
5. **Record the adjudication in [[verification-log]]** — both spellings, which won, and on which of
   the four grounds. **Suppress the loser** before it can be used by a later run.

**Worked example (2026-08-18, [Org 0582]).** The org's own site published `person0997@org0326.example` in the
Program Quality table and `person0998@org0326.example` in the Okeechobee County Office table, for one
person. Step 1 settled it — the printed name is *[Person 0516]*. Step 4 was run anyway because the
address was already in a draft-ready card: Apollo returned `person0997@org0326.example`, `verified`.
**Cost: 1 credit. Outcome: a coin-flip became a certainty, and the run also discovered the title was
wrong** (see below).

## PHASE 2 — ROSTER & DOSSIER (before any draft exists)

**No web research here** — this reads verified queue data. If writing a card needs a lookup, that
org wasn't ready.

### 🔴 THE ROSTER SWEEP — a GATE, added 2026-08-18 after the [Org 0539] defect

> **Read the diagnosis before the rule, because it explains why this one is a gate and not guidance.**
> [[CAPA-2026-08-18-unqueried-tier1-roster]]: [Org 0539] publishes five Assessment and Training
> Specialists plus a Coaching and Training Specialist. The run read all six, wrote all six onto the
> card, and named the concentration as the org's Pain Hypothesis — then submitted **two** of that
> org's nine Tier-1/2 candidates (eight of them Tier 1) to the vendor and filed the other six as *"address unknown"* without
> ever asking. It closed with **0 of 25** nightly lookup credits spent.
> `spend_lookup_when_unpublished` had been ratified **the same day.**
>
> **The rule was correct and did not fire, because it had no object and no completeness test.**
> *"Spend the lookup"* is satisfied by spending one. This section gives it both.

**RESOLVE FIRST, NARROW SECOND. That is the whole rule.**

The 1-To/max-2-Cc cap governs **who goes on the email.** It has never governed **who gets looked
up**, and conflating the two is what produced the defect: the run stopped resolving the moment it had
enough addresses to fill three slots. **A thread that carries three people is a reason to choose
well, not a reason to stop resolving at three.**

**The gate — an org does not pass Phase 2 until this is true:**

> **Every person named on the organisation's own pages whose title or role evidence puts them at
> Tier 1 or Tier 2, and whose address is not published, has been submitted to the vendor.**

**How to run it:**

0. 🆕 **Count every human named on the org's own pages, whatever their role.** This is
   `named on page`, the coverage denominator. **If any directory could not be read, write it with a
   `+`.** Do this first — every later count is judged against it.
1. **List every Tier-1/2 candidate** from the Check-1 page read. Tier on **role**, not title keyword —
   see the preferred ranking above.
2. **Subtract anyone whose address is already published.** Those need no lookup.
3. **Submit the remainder in ONE `people_bulk_match` call** (≤10 per call). Never one call per
   person — same credit cost, a fraction of the round-trips.
4. **Choose the To and Cc from what comes back.** The org-scale gauge and the right-size-the-To rule
   apply to the **resolved** set, never to the set the run happened to look up.
5. **Write the resolution line on the card** — evidence protocol ruling 6 below. **No line, no card.**

**Cap: 10 candidates per org per run** — one batched call. Beyond ten, take the highest-tier ten and
**state the number deferred on the card.** Silent truncation reads as *"we covered everyone."*

### 🔴 THE REVERSE LOOKUP — a generic inbox is a STARTING POINT, not a destination (Chris, 2026-08-20)

> ✅ **Chris, 2026-08-20:** *"Now that we're allowing generic inboxes, that doesn't mean we can just
> send to one email address and add the relevant names. I want to use tools like apollo and your web
> scraping skills to go find those people."*

**THE LOOPHOLE THIS CLOSES.** The roster sweep's workload comes from the page read — it submits the
names the site publishes. **So a site that publishes NO names produces a sweep with zero workload,
`Tier-1/2 identified: 0`, three identities that trivially balance, and a card that passes on its
face while nobody was ever looked for.** The org then descends to tier 3 or 4 and the run reports it
as a clean result. **A gate whose input can be empty is not a gate.**

**Proved on 2026-08-19 at [Org 0550].** The staff directory is a PDF, so the run
recorded `0 Tier-1/2 identified`, drafted to `person0401@org0321.example` at tier 4, and invented a greeting.
**One domain query on 2026-08-20 returned [Person 0080], "Director, Child Development and Education
Services," at that organisation since 2012, `person0141@org0321.example`, `email_status: verified`.**
**The Tier-1 buyer was one call away and the card said nobody was nameable.**

**THE RULE — before descending to tier 3 or tier 4, run the reverse lookup:**

1. 🔴 **Query the vendor BY DOMAIN, not by name** — `apollo_mixed_people_api_search` with
   `q_organization_domains_list`. **This is a different operation from the roster sweep and it is
   mandatory whenever `Tier-1/2 identified` is 0, or the directory is blocked, or the ranking is
   about to descend below tier 2.** The sweep asks *"what is this person's address?"*; the reverse
   lookup asks *"who works here?"*
2. **Take the names it returns and go back to the org's own site looking for them** — site search,
   newsroom, programme pages, board minutes, the CMS REST API, the alt-text. **A name you did not
   have is a search term you did not have.**
3. **If the org's own site confirms the person → both gates pass → draft to them.**
4. **If it does not, the person is `HOLD-G2`** — vendor-verified, own-site-unconfirmed. **Do not
   draft to them, and do not put their name in a greeting.** Name them on the card with the exact
   evidence that is missing and what would close it. *(Chris opening one PDF is often the whole gap.)*
5. **Only after all four steps may the ranking descend.** Record the reverse lookup on the card —
   including a null result, which is a real and valuable outcome.

**Cost is trivial and the search itself is free** — `apollo_mixed_people_api_search` returns names
and titles at no credit cost; only enrichment charges. ELCFH cost **2 credits** and turned a tier-4
shared inbox into a named Tier-1 director.

⚠️ **This does NOT loosen Gate 1.** Vendor names still cannot be drafted to on the vendor's word
alone — that is the `person0322@org0314.example` failure, where a `Verified` address belonged to someone
who had left. **The reverse lookup tells you WHO TO LOOK FOR. The org's own site still decides.**

🔴 **A tier-3 or tier-4 card is INVALID unless it carries a `Reverse lookup:` line.**
`Reverse lookup: N returned by domain query · N confirmed on own site · N HOLD-G2 · N null`

**On cost, because this sounds expensive and is not: null matches are free.** On 2026-08-18 twelve
people were submitted and four were charged — a ~33% hit rate. Seven orgs × ten candidates ≈ **23
credits**, inside a standing nightly budget that has been closing at zero.

🔴 **A run that reports unspent lookup budget while any org carries an unqueried Tier-1 person has
failed this gate**, whatever else it produced. See Phase 1.

**Roster gate.** Each org must carry: a verified decision-maker · a verified training/PD lead **or**
an explicit `NO PD ROLE PUBLISHED` · staff-page URL · `verified_on` ≤90 days · Gate 2 result ·
**a passing roster sweep**. Any gap → `HELD`, named in the report, verified next run.

### 🔴 THE TWO-LEDGER DE-DUP CHECK — R11, Chris 2026-08-20. Runs on EVERY org and EVERY recipient.

> ✅ **Chris:** *"I want to track who we've emailed by org and by person."*

**[[contacted]] holds two ledgers and BOTH are queried, in this order:**

| # | Ledger | Question | Hit → |
|---|---|---|---|
| **1** | **A — organisations** (one row per org) | *Has this org's domain ever been on a sent email?* | 🔴 **CLOSED under R1.** Stop. Do not proceed to check 2 |
| **2** | **B — people** (one row per ADDRESS, with `delivered / bounced / replied / never-emailed`) | *Has this specific address ever been sent to?* | **Remove that person from the draft and record why** |

🔴 **BOTH ARE REQUIRED AND NEITHER IS SUFFICIENT.** Ledger A cannot tell you whether a human already
heard from you when they move organisations or appear on two orgs' pages. **Ledger B cannot enforce
one-org-one-thread**, because a brand-new person at an already-contacted org passes it cleanly.
**The Five County failure passed the org check by looking bounced and had no person check at all.**

**🔴 Re-check suppression here, not just at discovery.** Every org in tonight's batch gets its domain
re-checked against [[hubspot-suppression]] **as refreshed today**.

> 🔴 **"AS REFRESHED TODAY" IS NOW A GATE, NOT A FIGURE OF SPEECH — P6, 2026-08-20.**
> **Read `last_refresh` in [[hubspot-suppression]]'s frontmatter before checking a single domain.
> If it is not today's date, NO ORGANISATION PASSES THIS PHASE.** Go back and run Phase 0 step 1c.
> **This sentence asserted a freshness that was false on four consecutive runs** (08-14, 08-17,
> 08-18, 08-19 — the list was last refreshed 08-13) and every one of those runs reported its
> suppression check clean. **The check ran; the list was stale; nothing could tell the difference.**
> Either the assertion is enforced or it is a lie in a safety control.

> **Why the discovery-time check isn't enough.** A row can sit in the queue for weeks. In that time
> an org can become a customer, open a deal, or receive an email from Chris — and the row would
> still be marked ENROLLABLE from whenever it was gated. **The gate that matters is the one closest
> to the send.** This is cheap: a handful of domains against a list already in memory.

Any org that has become suppressed since queueing → **drop it from the batch, report it as a
relationship formed.** That is good news, not a failure.

*Three consecutive orgs on 2026-08-11 had a PD lead on their own staff page that we never saw:
[Person 0381] (PD Manager), [Person 0501] (trainer), [Person 0026] (PD Coordinator). This gate exists
for them.*

**Recipients — hard cap: 1 in To, maximum 2 in Cc.** Chris, 2026-08-11:
> *"Let's agree that it's 1 person in the 'to' field and up to two people in the CC field."*

**Three people on a thread, never four.** More than that reads as a blast rather than a note.

- **To** — the single person most likely to be the decision-maker. Pick one; don't hedge.
- **Cc** — the **best 2** from [[recipient-profile]], selected by tier: **Tier 1 first** (explicit PD/training/coaching titles), then Tier 2 (practice quality), then Tier 3 (distribution).
- ~~Generic `info@` inboxes never on the visible thread.~~ 🔴 **REVERSED 2026-08-18 by Chris.**
  Generic inboxes ARE usable — in this sector they are often monitored more closely than personal
  ones, because turnover is high and processes are basic. See **the preferred ranking** above:
  a generic inbox is tier 3 (with a named greeting) or tier 4 (without), never a hold.

**Everyone who qualifies but doesn't fit goes in the dossier, not the email.** United Way has 10
tier-matching people; 3 go on the thread and the other 7 are recorded as known-but-not-contacted.
They stay available for a later touch or a referral — the cap limits the *email*, not the research.
**If the PD lead has no verified address, do not guess it.** Email 1 already asks to be pointed at
the right person.

### 🔴 THE THREE STATES — "address unknown" is retired, 2026-08-18

**The old phrase `identified, address unknown` is banned, because it collapsed two completely
different facts into one.** On the 2026-08-18 Escambia card, [Person 0583] (a credit spent, no
result) and [Person 0331] (never queried) both read *"no — address unknown"* with `—` in the
Evidence column. **One of those is a dead end. The other was a verified address one batched call
away.** The card made them look identical, which is why the defect survived Chris's review.

**Every unreached person on a Power Map now takes exactly one of these three states, verbatim:**

| State | Write it as | Means |
|---|---|---|
| Address published, unused | `📄 PUBLISHED — not on this thread (reason)` | We have it; the cap or the tier decided against it |
| Looked up, nothing came back | `🔍 VENDOR QUERIED — no match (N credits, YYYY-MM-DD)` | A real dead end. Route to phone/LinkedIn |
| Never looked up | `⛔ NOT QUERIED — reason: ______` | Must carry a stated reason |
| Never looked up, no reason given | **CARD INVALID** | The roster sweep did not run. Hold the org |

🔴 **`⛔ NOT QUERIED` with a blank reason is not a formatting problem, it is a failed gate.** The
only reasons that survive review are: *above the 10-candidate cap this run* · *Tier 3 or below* ·
*address already published* · *vendor unavailable* · *directory not machine-readable (asset URL on
the card)*. **"Enough recipients already" is not a reason** — that is the defect this rule exists
to stop.

🔴 **WHERE THE STATE GOES: in the Power Map's `Evidence` column.** The `On this email?` column stays
`To / Cc / no`. Do not invent a new column, and never leave `Evidence` as `—` for a person who is
not on the thread — a dash is exactly the ambiguity these three states replace.

### 🔴 BLOCKED — DIRECTORY NOT MACHINE-READABLE. A standing handler, added 2026-08-18

**Three organisations are now blocked on a file format, not on a fact:** [Org 0549]
(the whole staff directory is one JPEG), [Org 0550] (PDF-only), ELC of the Nature
Coast (no fetchable own-site page). Each was filed as a *failed read* and left.

**"Failed read" is a verdict on the run. It is not a verdict on the organisation.** Same logic as
the address rule: *"not published" is a fact about the website.* **A directory published as an image
means the org is reachable and the file is not.**

**When an org's staff directory is an image, a PDF, or otherwise unreadable:**

1. **Card it as `🔴 BLOCKED — DIRECTORY NOT MACHINE-READABLE`.** Never as a failed read, never as a
   hold, and never silently dropped from the batch.
2. **Put the direct asset URL on the card** — the actual `.jpg`/`.pdf`, not the page that embeds it.
   That is what a human or a browser session needs.
3. **Exhaust the cheap own-site routes first, and record each one tried.** In order:
   the CMS REST API (`/wp-json/wp/v2/pages?search=staff`, `/wp-json/wp/v2/media?search=directory`) —
   this is still the org's own site, so anything it returns satisfies Check 1 · the image's
   `alt_text` and caption · every other own-site page (contact, providers, programme, hours).
   **On 2026-08-18 that route found [Person 0588] at ELC Gateway on the CCR&R page** — a Tier-1
   role contact who appears on no staff listing at all.
4. **Draft the org anyway from whoever IS readable**, at whatever tier the ranking supports. Blocked
   directory ≠ blocked organisation.
5. **Queue the asset URL for a human screenshot or browser session** and carry it forward on the card
   until it is read. **Do not re-discover the same blocker every run.**

⚠️ **A vendor roster is not a substitute.** Apollo's roster for `[Org 0579]` returns ten people
and contains neither of the two the org's own pages name. **Vendor-only names cannot pass Check 1
and are never drafted** — they can only tell you who to look for in the unreadable file.

**Write the dossier before drafting** — `review-YYYY-MM-DD.md`, built from
**[[dossier-template]]**, one card per org, in the 5-section shape Chris asked for: **Org Snapshot →
Power Map → Pain Hypothesis → Positioning Hook → Draft**. Plus website (one field, the live URL),
staff page, every person's verified title and bio URL, both gates' evidence, everyone relevant we
are *not* emailing and why.

🔴 **A dossier flag is a hard stop.** On 2026-08-11 it named the batch's highest bounce risk and the
draft was sent anyway. An advisory that gets overtaken by the send is not a control.

### 🔴 Dossier evidence protocol — Chris, 2026-08-12 onward (six rulings, all mandatory)

1. **One line per person.** The evidence section is a scannable list titled "Where each address was
   found," never a prose block. Chris: *"Make it one line for each URL/record."*
2. **The 👉 pointer sits DIRECTLY IN FRONT OF THE URL** — not the name. Line shape:
   `- **First Last** — how it was found on 👉 https://exact-page-url (date) · also Apollo-verified`
   Recipients verified on the same page as the line above may say `— 👉 same page (date)`.
3. **Same page → one link. Different pages → every link.** Chris: *"If the contacts' emails come
   from the same page, then it's fine to show me that one link. If the contacts' emails were found
   on different sites, please share both or all of them."* Never compress two sources into one URL —
   that sent Chris hunting for [Person 0426] on the wrong page at send time.
4. 🔽 **CARD ORDER IS GMAIL ORDER — NEWEST DRAFT FIRST.** ✅ **Chris, 2026-08-13:** *"The list from
   1-5 is not how the drafts are displayed in my inbox. Since you create #1 first, it actually shows
   up at the bottom of my drafts list. Can you invert this for future dossiers so that the top draft
   in my inbox is listed as #1?"* Gmail sorts drafts newest-first, so **card 1 is the LAST draft
   created** and the numbering runs in reverse creation order. Build the drafts in whatever order the
   loop produces, then **write the cards out reversed** so card N matches the Nth draft from the top
   of his Drafts folder. Reconfirm the order against `list_drafts` (which also returns newest-first)
   before finalising the dossier.
5. 🔴 **CITE ONLY PAGES THIS RUN OPENED.** ✅ **Chris, 2026-08-13**, after catching a card that
   pointed at a URL the named person was not on. **A 👉 URL is a promise that this run fetched that
   page and read that line on it.** Three hard consequences:
   - **Never inherit a citation from a previous run's log and re-print it as this run's evidence.**
     Either re-open the page (cheap — one fetch) or write *"per the 2026-08-12 run, not re-read
     tonight"* in plain words on the card.
   - **A search-engine result summary is NEVER a citation.** It is an aggregator by definition, which
     [[method]] already excludes. If the only place a name and title appear is a search snippet, the
     person is `HOLD`, not a recipient.
   - **If a page returns an empty body, that is a FAILED read, not a silent fall-through to whatever
     else is on hand.** Record the failure and hold the org.

   Full root cause: [[CAPA-2026-08-13-false-citation]].

6. 🔴 **THE ROSTER RESOLUTION LINE — mandatory on every card, added 2026-08-18.** This is the
   control that makes an unqueried person **visible** instead of invisible. It is arithmetic, not
   judgement, and it cannot be written without having run the roster sweep.

   **Every card carries this line, in this exact shape, directly under the Power Map:**

   ```
   Roster resolution: N named on page · N Tier-1/2 identified · N published · N unpublished · N submitted · N resolved · N held · N queried-null · N deferred
   ```

   **The three identities. All three must hold or the CARD IS INVALID:**

   > 🔴 **1 · `identified` = `published` + `unpublished`**
   > 🔴 **2 · `unpublished` = `submitted` + `deferred`**
   > 🔴 **3 · `submitted` = `resolved` + `held` + `queried-null`**

   **Identity 2 is the one that catches the [Org 0539] defect.** Identities 1 and 3 exist so it
   cannot be satisfied by moving people into the other fields — without identity 1 a run could
   reclassify six people as *published* and pass; without identity 3 a `held` vendor return could be
   quietly counted as `resolved`.

   **`named on page` is the denominator, and it is a RAW HEADCOUNT, not a judgement.** Count every
   human named on the organisation's own pages, whatever their role. It exists so that
   `2 of 36` looks wrong at a glance while `2 of 3` does not. **A run cannot shrink its way to a
   clean card without the ratio giving it away.**

   🔴 **`+` MEANS "A DIRECTORY WAS UNREADABLE." IT NEVER MEANS "ABOUT."** Do not reach for it
   because counting was tedious or the pages were scattered — if the pages were readable, count what
   you can see and write a bare number. **A stray `+` falsely cards a healthy organisation as
   BLOCKED, and `B` is meaningless if it drifts into meaning "roughly."**

   🔴 **If ANY of the org's directories could not be read, `named on page` is written with a `+`** —
   `36+`, `3+` — because the true headcount is unknown. **A `+` in that field means:** the org is
   carded `BLOCKED — DIRECTORY NOT MACHINE-READABLE` **and it counts toward `B`, the blocked-roster
   backlog. It does NOT count toward `M`.**

   > ✅ **CORRECTED 2026-08-24 — D5 resolved, Phase 7 wins.** This paragraph previously read *"it
   > counts toward `M`,"* which contradicted Phase 7's M/B table and left a scored safety control
   > ambiguous for three runs. **Phase 7's reasoning is correct and governs: folding `B` into `M`
   > makes P4 unpassable, because P4 orders the run to card a blocked org and draft it anyway — which
   > would then register as a failure. That makes "don't card the blocked org" the cheapest clean
   > report, which is the pre-CAPA behaviour P4 exists to end.**
   > **`M` counts PEOPLE left unqueried. `B` counts ORGS whose roster could not be read. They mean
   > opposite things and are never merged.** Under §0.1 both statements are level-3 descriptions of a
   > level-1 control; the one that protects the control wins.

   **Field definitions — these are terms of art, so they are defined here and in the glossary:**

   | Field | Means |
   |---|---|
   | `named on page` | Every human named on the org's own pages. Raw count, **exact**. `N+` ONLY if a directory was unreadable — never as shorthand for "about" |
   | `Tier-1/2 identified` | Of those, the ones at Tier 1 or 2 by title **or role evidence** |
   | `published` | Their address is printed or `mailto:`-linked on the org's own page. No lookup needed |
   | `unpublished` | Named and tiered, but no address on the site. **These are the sweep's workload** |
   | `submitted` | Actually sent to the vendor this run |
   | `resolved` | Vendor returned an address that passes BOTH gates — i.e. `email_status: verified` |
   | `held` | Vendor returned a record but the address is unusable: `extrapolated`, `unavailable`, wrong-org, or domain mismatch. **`Extrapolated` is `held`, NEVER `resolved`** |
   | `queried-null` | Vendor returned no match at all. Costs nothing. A real dead end |
   | `deferred` | Over the 10-per-org cap. **Name who was deferred on the card** |

   **Worked example 1 — what the 2026-08-18 Escambia card actually said, scored:**

   ```
   Roster resolution: 36 named on page · 9 Tier-1/2 identified · 0 published · 9 unpublished · 2 submitted · 1 resolved · 0 held · 1 queried-null · 0 deferred
   ```

   *(`36` is an exact count of the named humans on https://[Org 0576]/about/team/, re-read
   2026-08-18 — 4 Executive + 15 Operations + 5 Community Impact + 4 Finance + 8 Eligibility, with
   one row reading "Vacant" excluded. **No `+`: that page reads fine.** The card's own prose says
   "roughly 29 staff" and "40+ people" — both loose, which is exactly why this field is a count and
   not an adjective.)*

   Identity 1: 9 = 0 + 9 ✅ · Identity 3: 2 = 1 + 0 + 1 ✅ · **Identity 2: 9 ≠ 2 + 0 🔴 INVALID.**
   **The card would have failed on its face**, at a glance, before Chris read a single evidence line.
   That is the entire point: the defect was never hard to see, it was *unrepresented*.

   **Worked example 2 — the same org after the sweep was run for real on 2026-08-18:**

   ```
   Roster resolution: 36 named on page · 9 Tier-1/2 identified · 0 published · 9 unpublished · 9 submitted · 2 resolved · 2 held · 5 queried-null · 0 deferred
   ```

   9 = 0 + 9 ✅ · 9 = 9 + 0 ✅ · 9 = 2 + 2 + 5 ✅ — **valid.** `resolved` = [Person 0044] and
   **[Person 0331]** (`person0720@org0320.example`, the Assessment and Training Specialist the
   original run never asked about). `held` = [Person 0392]-Otto (`extrapolated`) and Al Henderson
   (`unavailable`). `queried-null` = [Person 0583], [Person 0413], [Person 0066], [Person 0100], Misty
   Lambeth. Full analysis: [[CAPA-2026-08-18-unqueried-tier1-roster]].

   **Why a count and not a rule.** Every rule in this file that fires reliably is attached to a
   countable object and blocks an artefact from existing — the two gates, `email_status`, the pronoun
   ban. Every rule that has failed to fire is a judgement with no object: *tier on role* went unapplied
   for five days across five raisings; *spend the lookup* fired for two people out of nine on the day
   it was ratified. **A count cannot be satisfied by doing the thing once.**

Commentary, quotes, and corrections live in the Watch-out line — never wrapped around a URL.
Worked example: [[review-dossier-2026-08-12]]. Format spec also in [[dossier-template]].

## PHASE 3 — DRAFT

1. Sequence position from [[sequence-tracker]]. New org → Email 1.
2. Copy that email **verbatim**. Resolve greeting and `{{company}}`. Nothing else.

   **`{{company}}` = the name the org itself uses** (✅ ratified by Chris 2026-08-12). During the
   Check-1 staff-page read, record the org's **self-used display name** — how its own masthead, logo,
   domain, social handles or site text refer to it — as `display_name` on the queue row and dossier
   card.

   🔴 **REVISED 2026-08-14 — the 08-13 two-branch rule is REPLACED. Chris chose the one-branch
   rule at review on 2026-08-14; the wording of that choice is not on record (it was made in a
   multiple-choice prompt, which the transcript does not capture). The rule rests on his ACT, not
   on a quote: six consecutive hand-shortenings across six batches.** He had hand-shortened the subject in all six batches, including once where the
   08-13 rule was followed correctly and still produced a subject he cut down at review
   (`Early Learning Coalition of Osceola County` → `[Org 0567]`).

   **One branch now: ALWAYS shorten, ALWAYS end with ` . . .`** (space dot space dot space dot).

   | Case | What to use | Examples |
   |---|---|---|
   | Org uses a short brand about itself | that short form + ` . . .` | `at ACCORD . . .` · `at DCCNY . . .` · `at ELCOC . . .` · `at ELCHC . . .` |
   | Org uses no short brand | a plain shortening of its own formal name + ` . . .` — keep the distinguishing words, drop boilerplate (`Early Learning Coalition of`, `Child Care Council of`, `, Inc.`) | `at [Org 0567] . . .` · `at [Org 0552] . . .` · `at Child Care Dutchess . . .` |

   **Shortening ≠ inventing.** Never invent an *acronym* the org does not use about itself — but
   trimming the org's own formal name to its distinguishing words is now expected. Record **both**
   the self-used short brand and the formal name as `display_name` at the Check-1 read, so the
   shortening needs no second lookup. Unconfirmable org name at all → the template's
   `your organization` fallback.
3. Recipients from Phase 2. Do not re-derive.
4. 🔴 **NO BCC ON ANY DRAFT — the HubSpot BCC is DISABLED (Chris, 2026-08-18).** His browser
   extension already syncs these sends, and the BCC was failing loudly while duplicating it — it
   bounced on 6 of 7 attachment-bearing sends on 08-17 ("Message too large"). See `hubspot_bcc` in
   [[STATE]]. The address, if he ever re-enables it: `<HUBSPOT_BCC_ADDRESS>` — **do not put
   it on a draft on the strength of this line alone.**
5. Emails 2 and 3 are **replies on Email 1's thread** (`replyToMessageId`).
6. Send `body` and `htmlBody`. Bold is copy.
7. 🆕 **2026-10-03 — EMAILS 2 AND 3 ARE WRITTEN BY ZAPIER (`config.draft_writer`; procedure in §0.3 step 12).** Three consequences: ① **never call `update_draft` on a Zapier-created draft** — the native connector rebuilds the message, strips the attachment and re-wraps every href; an edit means: trash the old draft → **Chris deletes it forever** (Trash alone leaves it as the thread's newest message, and the new Zapier draft would attach to it and vanish from the conversation view — found 2026-10-04, `config.draft_writer.zapier.reply_parent_rule`) → THEN create the new Zapier draft; if it cannot wait, create it and mark the card `COMPOSE-LINK-ONLY` ② Zapier reply drafts carry **no quoted history** and **no `Re:` prefix** (the thread subject is reused verbatim); both seen and accepted by Chris 2026-10-03 — do not "fix" either ③ a Zapier draft that cannot be read back on the native connector is not a created draft; create it natively and count the fallback. Email 1 stays on the native connector until BQ-022 is ruled.

### 📎 ATTACHMENTS — which path applies to which email. Ruled 2026-08-20.

> ✅ **Chris, 2026-08-20:** *"Just like the first email, you write the draft and I attach the files.
> let's use that method for email #3 as well."*

| Email | Attachments | Path |
|---|---|---|
| **1** | GIF inline + flyer PDF | 🔄 **2026-10-04 — FLYER ATTACHED BY ZAPIER AT CREATION** (`config.draft_writer.email_1 = zapier`, `email_1_attachment`: `HST_Flyer.pdf` 3.5 MB from Chris's sent Email 1 `<thread-id>`); clean YouTube href; signature appended. **The GIF stays manual** — Zapier cannot embed an inline image — Chris drops `HST_WorkshopInAction.gif` in directly under the *AI-powered world.* line (proven 2026-10-04: a hand-inserted GIF leaves the href clean and the flyer attached). ~~Forward-master preferred, manual drag as fallback~~ survives only as the native-fallback procedure. Section below |
| **2** | 🚫 none | **Nothing to do.** The draft is complete and sendable as-is. 🔄 2026-10-03: written by Zapier, so the YouTube href is clean and the Email 1 GIF no longer rides along as an attachment (Zapier replies carry no quoted history) |
| **3** | Starter Kit PDF | 🔄 **2026-10-03 — ATTACHED BY ZAPIER AT CREATION** (`config.draft_writer.zapier.email_3_attachment`: `HST_3PackStarterKit.pdf`, 7.2 MB, pulled from Chris's own sent Email 3 `<thread-id>`). Chris sends as-is. ~~MANUAL DRAG ONLY (ruled 2026-08-20)~~ survives only as the **native-fallback** procedure when the Zapier call fails for a draft |

🔴 **THE DEFAULT FOR ANY ATTACHMENT-BEARING EMAIL: THE DRAFT IS THE GUARANTEE, THE FORWARD IS THE
UPGRADE.** The machine drafts complete and Chris drags the file. No forward-master is required, and
no machine-side attachment is attempted. A forward-master, where one exists, is an *optimisation on
top of a working path* — never the path itself, and never a blocker. **If you find yourself hunting
for a master that does not exist, stop: you have mistaken a missing optimisation for a missing
capability.** That exact mistake cost an afternoon on 2026-08-20.
⚠️ **STATUS OF THIS DEFAULT — READ IT BEFORE CITING IT.** Chris ruled this for **Email 1 and Email 3
by name** (2026-08-20, *"Just like the first email… let's use that method for email #3 as well"*).
The extension to *any future* attachment-bearing asset is **the machine's inference from his own
analogy, not his instruction** — he was not asked about the general case. Act on it as the default;
do **not** quote it back to him as a rule he set. One word from him moves it.
🔴 **AND EVERY NEW ASSET MUST BE CLASSIFIED ON ONE QUESTION BEFORE THE DEFAULT IS APPLIED:** *does
the body still make sense if the file never gets attached?* Email 1 → yes. Email 3 → no. That answer,
not the default, decides whether the card gets a footnote or a gate.

🔴 **EMAIL 3 HAS NO SEND-AS-IS FALLBACK, AND EMAIL 1 DOES. THIS IS THE ONE ASYMMETRY TO REMEMBER.**
Email 1's P.S. merely *mentions* a flyer — the email stands alone without it. **Email 3's body IS the
delivery of the attachment:** *"Instead, I'll leave you with this Human Skills Starter Kit… It's
yours."* **Sent without the PDF it promises a gift and delivers nothing, on the last touch of a
sequence, to someone who never replied. That is worse than not sending.**

🔴 **So every Email 3 card carries the attachment gate at the TOP, not in a footnote:**

```
📎 ATTACHED BY ZAPIER AT CREATION: HST_3PackStarterKit.pdf (7.2 MB)
   verified: list_drafts has:attachment filename:pdf ✅ <draft id>
   🔴 NO ✅ ON THIS LINE = DO NOT SEND — the body promises a gift
```

🔄 **2026-10-03 — the gate changed from "Chris attaches" to "the machine verified the attachment is there."** The block above is the current form (§0.4 E3.1). The retired form, kept for the native-fallback case only:

```
📎 ATTACH BEFORE SENDING: HST_3PackStarterKit_email.pdf
   _SEND-KIT/3-Classic-Sequence-Email-3/  (2.7 MB)
   🔴 THIS EMAIL IS INCOHERENT WITHOUT IT — there is no send-as-is option
```

**And the run reports `Dossier: … attachments verified N of N`.**
~~**The machine cannot attach the file; making the step impossible to miss is the only control it has.**~~ **Since 2026-10-03 it can (Zapier `file`), and the read-back is the control.**
⚠️ **Take the copy inside `_SEND-KIT/` — `HST_3PackStarterKit.pdf` in `Collateral/` is 7.2 MB**, the
same near-identical-twin trap as the Email 1 assets.

### 🔴 Attachments for EMAIL 1 — the golden-forward path

**The machine cannot attach files.** Measured, not assumed: the bytes must pass through the tool
call as base64. 🔴 **CORRECTED 2026-08-20 — the old figure understated it by ~4×.** The file actually sent is **`HST_InAction.gif`, 5,559,398 bytes (5.4 MB) ≈ 1.85 MILLION tokens** as base64, plus the flyer. *(The retired "1.4 MB → ~461k" figure belongs to `HST_video_preview.gif`, a different, shorter animation sitting in the same folder.)* Not "several
times a context window, per email. Attachment-by-ID was tested 2026-08-11 and produced a **0 KB
file**, because `content` is still required.

**So every draft's report line names its golden reference from [[golden-references]].** Gmail's
**Forward** preserves attachments and inline images exactly — unlike Reply, unlike Templates — so
Chris forwards a golden and swaps two fields instead of dragging two files.

> **The draft is the guarantee. The forward is the upgrade.**
>
> **Always create the complete, sendable draft first** — correct recipients, correct subject,
> approved copy, label applied, **and NO BCC** (`hubspot_bcc` is `disabled`). *Then* point at the golden.
>
> **Never make a draft conditional on a golden existing.** If the golden is missing, stale, or Chris
> skips it, **the draft still works** — that is exactly the workflow that produced the nine sends on
> 2026-08-11. Report all three fallbacks per draft:
>
> 1. Forward the golden, swap greeting + recipients → pixel-perfect, attachments ride along
> 2. Send the draft and drag both files from `Collateral/_SEND-KIT/2-Classic-Sequence-Email-1/`
> 3. Send the draft as-is → text-perfect, no image or attachment
>
> **All three are acceptable sends.** Only the first is free.

**When Chris hand-sends an email with the assets correctly in place, that becomes the new golden** —
record its message ID in [[golden-references]]. A golden is valid only while its body matches the
current template; a copy revision invalidates it.
7. **No placeholder or instruction lines in the body, ever.**
8. Label the thread **`CCR&R outreach`** (`Label_2`). One label, drafts and sent alike — state lives
   in [[sequence-tracker]], and Gmail's own `in:draft`/`in:sent` separates the rest. Do not recreate
   sublabels.

> 🔴 **Two `update_draft` behaviours that both caused live defects on 2026-08-11. Read before editing
> any draft.**
>
> **1 — `update_draft` cannot REMOVE a recipient.** Passing `cc: []` is ignored, not applied. Three
> drafts kept unverified Cc recipients ([Person 0288], [Person 0458], [Person 0340]) after an edit
> that was supposed to drop them — and `list_drafts` showed them still attached.
> **→ To remove any recipient, CREATE A NEW DRAFT and have Chris delete the old one.** Adding or
> changing a recipient is fine; removing one is not.
>
> **2 — `update_draft` replaces the thread, which DROPS the label.** Every edited draft loses
> `CCR&R outreach` and gets a new `threadId`.
> **→ After any edit or re-create: re-read `list_drafts`, then re-apply `Label_2` and update the
> thread ID in [[sequence-tracker]].** Never reuse a thread ID recorded before an edit.
>
> **Always verify recipients against `list_drafts` after editing.** The tool reports success on the
> call while silently ignoring the removal.
>
> **3 — Drafts CAN be deleted.** Use `apply_sensitive_thread_label` with `labelOption: TRASH`.
> Verified working 2026-08-11. The runbook's *"❌ no delete"* was stale — the same sentence that
> also wrongly claimed *"❌ no attachments."*
>
> 🔴 **4 — NEVER `trash_thread` A THREAD THAT CONTAINS SENT MAIL. Added 2026-08-18 after doing it.**
> Trashing a thread trashes **every message on it, including sent mail** — not just the draft you
> meant to remove. On 2026-08-18 a probe draft was created on the [Org 0546] thread and the thread
> was then trashed to clean up, **which trashed the sent Email 1 that is the current forward-master**
> (`<thread-id>`). Nothing was unsent and the message survives in Trash, but **`untrash_thread`
> returns "The caller does not have permission," so the machine cannot undo it** — only Chris can,
> from Gmail's Trash, within 30 days.
>
> ✅ **RESOLVED THE SAME DAY, and the recovery procedure matters as much as the prevention.**
> `untrash_thread` and `untrash_message` BOTH return *"The caller does not have permission"* —
> but **`unlabel_message` with `labelIds: TRASH` restores the message immediately**, with its
> `CCR&R outreach` label intact. **Trash is a LABEL in Gmail**, so label manipulation reaches states
> the dedicated untrash verbs cannot. Verified 2026-08-18 on `<thread-id>`.
>
> 🔴 **This is also a self-recovery failure, and it is written up separately in
> [[rule-exhaust-self-recovery]].** The run hit the first permission error and handed Chris a manual
> restore procedure without trying the message-level endpoint or the label route. **One call would
> have avoided asking him for anything.** That rule is global, not specific to this machine.
>
> **The rules that follow:**
> - **Probe only on threads this run created itself**, never on a client thread.
> - **Before any `trash_thread`, check the thread for a `SENT` label.** If one is present, do not
>   trash the thread — leave the draft and report it instead. A stray draft is a smaller problem than
>   destroyed sent mail.
> - **A trash operation the machine cannot reverse is not a cleanup, it is a deletion.** Treat it
>   with the same care as a send.

### The mandatory sequence for changing a draft's recipients

> 🔴🔴 **REWRITTEN 2026-08-20 ON CHRIS'S INSTRUCTION.** *"Instead of trashing the message, can we
> simply edit it? Figure out how to make this lower risk and still get the output we want."*
> **The old procedure ended in `apply_sensitive_thread_label` → `TRASH`, which trashes EVERY message
> in the thread including SENT MAIL.** That is what destroyed the forward-master on 2026-08-18.
> **It is now banned outright. There are two procedures, chosen by what kind of draft it is.**

### 🅐 EMAIL 1 DRAFT (a new thread, no sent mail on it) → **EDIT IT IN PLACE**

**`update_draft` is SAFE here and is now the default.** It keeps the same `draftId`, so **no duplicate
is ever created** — the failure mode the old three-step procedure existed to prevent cannot occur.

1. **`update_draft`** with the corrected `to` / `cc` / `body` / `htmlBody`
2. **Re-apply `Label_2`** — the edit moves the draft to a new `threadId` and the label does not follow
3. **`list_drafts`** → confirm exactly one draft for that org, exact recipients, label present
4. Update the thread ID in [[sequence-tracker]] — **the old one is dead**

⚠️ **`update_draft` cannot REMOVE a recipient by passing an empty array** — omitted/empty fields are
*preserved*, not cleared. **To drop someone, pass the full corrected list explicitly.** Verify in
step 3; the call reports success while silently keeping the recipient.

### 🅑 FOLLOW-UP DRAFT (Email 2 or 3, a reply on a thread that holds sent mail) → **CREATE, THEN `trash_message`**

🔴 **NEVER `update_draft` a reply.** Re-tested 2026-08-20: it **detaches the draft from its thread**,
drops the label, and discards the quoted history. The follow-up would arrive as a cold standalone
email with no conversation attached.

1. **CREATE** the replacement with `replyToMessageId` pointing at the Email 1 message
2. **`trash_message`** on the OLD DRAFT'S OWN `messageId` — 🎯 **this removes only that draft.
   Verified 2026-08-20 on thread `<thread-id>`: the sent Email 1 and its `Label_2` survived
   untouched.** **Never `trash_thread` — it takes the sent mail with it**
3. **VERIFY** with `list_drafts`, re-apply `Label_2` to the thread

**Create before trashing, always**, so the organisation is never without a draft if a call fails.

### The safety rule underneath both

> 🔴 **The blast radius of a cleanup must never exceed the thing being cleaned up.**
> A draft is one message. **Use a verb scoped to one message (`trash_message` / `update_draft`),
> never one scoped to a thread (`trash_thread`).** If the only available verb is thread-scoped,
> **leave the stray draft and report it** — a duplicate draft is a smaller problem than deleted
> client mail, and it is reversible.

⚠️ **Both procedures are dated 2026-08-20 and carry a re-test obligation** per *"capability claims
expire."* The connector's behaviour has changed three times in five days.

### MULTI-RECIPIENT DRAFTS — the options, honestly ranked (2026-08-18)

🔴 **There is no way to put two addresses in one field using the native Gmail connector.** This was
established exhaustively, not assumed — ~15 approaches tested and documented below: arrays, four
separator styles, RFC display-name form, angle brackets, renamed parameters, the Gmail API's native
`raw` MIME field, `update_draft` append, and reply-thread recipient inheritance. **The MCP registry
also has no alternative Gmail connector** (searched 2026-08-18, zero results).

**So the choice is between four options, and the default is deliberately the boring one:**

| # | Option | Cost | Verdict |
|---|---|---|---|
| **1** ~~🎯~~ | ~~**Draft 1 To + 1 Cc; name the second Cc on the card as "add at review"**~~ | — | 🔴 **RETIRED 2026-08-19 — the connector takes arrays again and two Cc addresses land.** See the parameter-format section below. Use the full 1-To/2-Cc cap. This row is kept only so the option is recognisable if the shape regresses again |
| 2 | Put the third person in `bcc` | Free | 🔴 **Not recommended.** They receive it but are invisible to the others and get dropped from replies — which breaks the referral mechanic the Cc exists for |
| 3 | Zapier's Gmail action (`draft_v2` / `draft_v2_reply`) | One-time auth + a standing dependency | ⚪ **Available, not required.** Full list support for to/cc/bcc/label_ids, plus a `file` parameter that takes a public URL |
| 4 | Report the regression and wait | Free | ⚪ Worth doing alongside any of the above — this worked on 2026-08-17 and broke mid-session on 08-18 |

**Option 1 is the standing behaviour. Do not treat the connector limit as a blocker** — it costs
seconds at a review step Chris performs anyway, and the card names exactly who to add.

### If Chris authorises Zapier — the reference

**Not required. Kept because it is the only route that also solves attachments.**

**Setup — ONE TIME, Chris only, ~2 minutes:**
👉 **https://mcp.zapier.com/mcp/servers/025d31da-1454-4e10-b69c-7c29cd141028/app-auth/GoogleMailV2CLIAPI**
Both actions are already enabled on the server; only the Gmail account connection is missing.

**The two actions, both called via `execute_zapier_write_action`:**

| Action | Use for | Key parameter |
|---|---|---|
| **`draft_v2`** | **Email 1** — a new draft on a new thread | — |
| **`draft_v2_reply`** | **Email 2 and Email 3** — a draft as a reply on an existing thread | `thread_id` (required) |

**Parameters (identical on both, except `thread_id`):**

| Param | Type | Notes |
|---|---|---|
| `to` | **list** | *"Separate multiple addresses with commas or add them individually"* |
| `cc` | **list** | 🎯 **THE FIX — multiple Cc addresses supported** |
| `bcc` | **list** | Leave empty; the HubSpot BCC is off |
| `subject` | required | |
| `body` | required | |
| `body_type` | `plain` \| `html` | Use `html` so the template's **bold** survives |
| `label_ids` | **list** | 🎯 **Applies `CCR&R outreach` at creation** — no separate labelling call, and no risk of the label being dropped by an edit |
| `file` | **list** | 🎯 **Attachments — "Add files or paste a public URL."** See below |
| `from` · `from_name` · `signature` | | Leave at defaults |

🎯 **`file` may end the attachment problem entirely — TEST IT, DO NOT ASSUME.** The machine has never
been able to attach the GIF and flyer, because the bytes would have to pass through the tool call as
base64 (~780,000 tokens per draft). **Zapier's action accepts a public URL instead of bytes.** If
`HST_WorkshopInAction.gif` and `HST_Flyer.pdf` are hosted at public URLs, drafts could arrive
complete — which would retire the forward-master procedure, retire the manual drag, and remove the
inline-image workaround in one move. **This is the single highest-value thing to test after auth.**
It is a hypothesis until a real draft is inspected in Gmail.

**Order of preference IF authorised:**
1. **Zapier `draft_v2` / `draft_v2_reply`** — full recipients, label at creation, possible attachments
2. **Native connector `create_draft`** — 1 To + 1 Cc, third named on the card. **This is the default
   while Zapier is unauthorised, and it is a perfectly acceptable steady state — not a degraded mode**
3. Reads (`list_drafts`, `search_threads`, `get_thread`, `list_labels`) stay on the **native
   connector** — they work fine and are cheaper

🔴 **Verify every Zapier-created draft against the native `list_drafts`** before reporting it. Two
systems writing to one mailbox is exactly where orphans appear.

### 🔴 GMAIL CONNECTOR PARAMETER FORMAT — 🔴 **THIS HAS CHANGED TWICE IN 24 HOURS. TEST THE SHAPE, DO NOT TRUST THIS SECTION.**

> ## ✅ CURRENT AS OF 2026-08-19 — ARRAYS WORK AND MULTI-Cc WORKS. THE 1-To/1-Cc LIMIT IS RETIRED.
>
> **Verified by creating a real draft and reading both Cc addresses back from `list_drafts`**
> ([Org 0253] follow-up, `r8609358546540752072`, 2026-08-19 09:19 UTC):
>
> | Parameter | ✅ Works 2026-08-19 |
> |---|---|
> | `to` | `to: ["person@org.org"]` |
> | `cc` | `cc: ["a@org.org", "b@org.org"]` — **two addresses, both attached** |
> | `labelIds` | `labelIds: ["Label_2"]` |
>
> **What this retires:** the "add at review" workaround (option 1 in the table above) · the
> practical case for authorising Zapier **for recipients**. The full **1 To + max 2 Cc** cap Chris
> set on 2026-08-11 is available again and five drafts used it on 2026-08-19.
> **Zapier's remaining value is the `file` parameter** (attachments by public URL) — still untested,
> still worth having.
>
> 🔴 **FIRST WRITE OF EVERY RUN IS A SHAPE TEST.** Make it a real draft you needed anyway, read it
> back with `list_drafts`, and record which shape worked in the report. **The shape went
> array → scalar mid-session on 08-18 and back to array within 24 hours.** Neither state is safe to
> assume.

**The 2026-08-18 state, kept because the diagnostic trap below is the durable lesson:**
on that day the connector took **SINGLE STRINGS, not arrays, and accepted only ONE address per
field.** That cost a full working day and produced a wrong diagnosis, so it is written down
precisely. **If an array errors, try the scalar form before concluding anything.**

| Parameter | ✅ Correct | 🔴 Fails |
|---|---|---|
| `to` | `to: "person@org.org"` | `to: ["person@org.org"]` |
| `cc` | `cc: "person@org.org"` | `cc: ["a@org.org","b@org.org"]` · `cc: "a@org.org, b@org.org"` · `cc: "a@org.org;b@org.org"` |
| `labelIds` | `labelIds: "Label_2"` | `labelIds: ["Label_2"]` |

**Every wrong form returns a misleading error that names the wrong thing:**
- Array or multi-address `to`/`cc` → *"Invalid email address. Please provide a raw email address in
  the format 'user@example.com'"* — **on addresses that are perfectly valid.**
- Array `labelIds` → *"Invalid label: [Label_2]"* — **on a label that demonstrably exists** and that
  `list_labels` returns in the same session.

🔴 **THE DIAGNOSTIC TRAP, recorded so it is not repeated.** On 2026-08-18 both errors were read as
evidence of a revoked write scope, because reads all worked and both messages were provably false on
their own terms. **That reasoning was wrong.** Chris disconnected and reconnected the Gmail connector
on that advice and it changed nothing — which is the observation that should have arrived much
sooner. **The array form worked earlier the same morning and stopped working mid-session, so the
connector's expected shape changed under us.**

**The lesson is general: when a tool's schema is opaque (`{"type":"object"}`), a validation error
naming a data problem may be a SHAPE problem.** Before concluding anything about permissions, try
the scalar form of every array parameter. It costs one call.

> 📖 **Why this is a regression rather than a long-standing limit, and the full table of the
> 12 syntaxes tested — see [[method-rationale]].**

### Capability claims expire

Every "the connector can't do X" note carries a **date and a re-test**. Two such claims were
believed and both were false on the day they were tested: *no attachments* (partly true — the API
accepts them, the payload size doesn't) and *no delete* (simply wrong). A stale capability note
doesn't just block a feature — it silently reshapes the workflow around a limit that no longer
exists, and that workaround generates garbage every time it runs.

### 🔴 PRE-DRAFT GATES — R6, Chris 2026-08-20. Both run BEFORE the draft is created.

> ✅ **Chris:** *"its our failure of verifying email addresses. Let's fix this verification issue."*

#### 6a · THE CHARACTER-MATCH CHECK — every address, every draft

**Put the address about to be drafted directly beside its quoted evidence line and compare them
CHARACTER BY CHARACTER.** One character different → **HOLD the recipient and report it.**
**Print both on the card** so a human sees the comparison too:

`To: ccrr@org0315.example ⟷ source: "CCR&R Department — ccrr@org0315.example" ✅ exact match`

🔴 **And re-run the same check at Phase 0 against the AS-SENT address.** That is the only place a
hand-edit at review can be caught. **Origin: `ccr@org0315.example` went out against a published
`ccrr@org0315.example` — one character, introduced at review, and nothing in the pipeline compared
the draft to the evidence.**

#### 6b · THE EMPLOYMENT CHECK — the **To** recipient only

**Cross-check current employment against the vendor before drafting.** A vendor record showing a
departure — or **no record at all where the rest of the roster resolves cleanly** — is a **HOLD**, and
the next-ranked person takes the To. **~1 credit against a budget that closes at zero.**

⚠️ **Record the page's own publish/modified date where the CMS exposes it** (`article:modified_time`,
`Last-Modified`). **A page whose own metadata is over 12 months old gets the same check.**
**Origin: `person0936@org0323.example` — McKenna Terrill had left and the staff-page fetch returned a cached
copy. The source was right; the cache was stale.**

### 🔴 PRE-SEND SELF-CHECK — the last gate before Chris's outbox

**For every recipient on every draft, answer two questions in the report:**

1. **What source OBSERVED this address?** Name it — a URL, or Apollo `Verified` with its status.
2. **On what date?**

**If the answer is any of these, pull the recipient:**

- *"a pattern"* / *"it looked right"* / *"consistent with a colleague's address"*
- *"Apollo returned it"* — where the status was `Extrapolated`
- *"ZeroBounce said valid"* — that proves a mailbox exists, never whose
- *"I'm not sure"*

**One line per draft in the report.** This check costs seconds and it is the only thing standing
between an inference and a live send. `person0052@org0238.example` would have failed it on the first
question — nothing ever observed that address; Apollo derived it from `carolyn@`.

**The general form of the rule, which is what actually prevents recurrence:**

> **Classify every fact as OBSERVED or INFERRED before using it — address, title, employment,
> validation, anything.** An inferred value HOLDS until a second independent source shows the same
> thing. **Who produced it is irrelevant.** A vendor's inference is still an inference, and vendor
> packaging is what makes it look like an observation.

Both failures today were this same mistake wearing different clothes: a brochure's address treated
as observed, and Apollo's pattern guess treated as observed.

### 🔎 OPEN LEADS — R15 GOVERNS. Standing permission to investigate and close. (Chris, 2026-08-20)

🔴 **R15 REPLACES the handler below.** The old version said *"spot it and follow through"* without
saying how, and produced leads that sat open for six runs. **R15 gives it a budget, a method and
three terminal states.**

**In brief — full protocol in R15:**
- **Trigger:** malformed `mailto:` · printed text disagreeing with its `mailto:` target · doubled or
  misspelled domain · two spellings of one address · an orphan address matching nobody · a named
  Tier-1/2 person with no obtainable address · vendor contradicting the org's own page · an
  auto-reply naming someone absent from the site
- **Standing permission: 5 credits and 5 fetches per lead, no approval needed.** *Cost is never a
  reason to leave a lead open*
- **Method, in order, stop at a terminal state:** ① **write the hypothesis down first** ② test it
  across the org's own site, counting occurrences ③ test the org's naming convention ④ vendor by
  name ⑤ **vendor by domain** — the free query that turned ELCFH from a shared inbox into a named
  Tier-1 director
- **Terminal states:** ✅ `RESOLVED — VALID` *(if the org is CLOSED under R1, record as
  known-but-not-contacted — do NOT open a thread)* · ✅ `RESOLVED — INVALID` *(suppress, state the
  reason, close permanently)* · 🔴 `BLOCKED` *(name the exact question a human must answer)*
- 🔴 **A lead ending a run without a terminal state is reported `OPEN — N runs`.** **The count is the
  control.** `dgarvey@` ran 6, `ryanlasal@` 6 — both with no number beside them.

#### The original 2026-08-12 handler, kept for its reasoning

> *"You were able to look behind the visual and get a new email address and infer. Let's get the
> scheduled task to follow through on those kinds of instincts and research that person/address to
> learn more. This exact thing is going to keep happening."*

**When the visible text and the underlying data disagree — a printed address vs its `mailto:`
target, a staff name missing from one page but present on another, any behind-the-visual anomaly —
BOTH values become RESEARCH LEADS, never just a hold.** The same run (or the next nightly run, if
budget is spent) must:

1. **Identify the mailto-target's owner.** Search the org's own site for the handle's likely name
   (e.g. `dgarvey` → a Garvey on any program page), and run an Apollo person lookup on the org.
2. **Check whether the printed person is still current** — staff-page presence, Apollo employment.
3. **Resolve and record** in [[verification-log]]: which address belongs to a real, current person;
   which is stale. A stale printed address gets suppressed BEFORE it can bounce.
4. **Surface the resolved contact on the org's dossier card** before its next sequence email.

**Why this exists:** on 2026-08-12 the machine spotted that `mbevins@` (printed) conflicted with
`dgarvey@` (mailto), held both — and stopped there. The bounce proved the printed text stale, and
`dgarvey@` was left unresearched. Spotting the anomaly is half the job; the follow-through is the
other half. **Open leads from that day, to be worked by the next run:** `person0347@org0654.example`
(Schoharie — likely the current Program Coordinator) · `person0887@org0572.example` (Oswego —
target of [Person 0216]'s mis-wired link).

### 🥇 RECIPIENT SELECTION IS GOVERNED BY THE RANK LIST — R4, Chris 2026-08-20

🔴 **READ R4 BEFORE THE ORG-SCALE GAUGE BELOW. The gauge's "≲15 staff → the ED takes the To" branch
is RETIRED.** It fired *correctly* at ELC Sarasota (13 staff) and still produced the wrong answer —
Chris moved the To from the CEO to the Chief Program & Policy Officer. **Third override in eight days.
The variable was never headcount; it is function.**

**Sort everyone the org publishes into the seven ranks in R4, take the top 3, highest rank takes the
To.** Ranks in brief: **1** PD/training/coaching/CCR&R owners (by title *or* quoted role evidence) ·
**2** programme leadership (Chief Program/[Person 0194], Director of Early Learning/Programs) ·
**3** practice-quality specialists · **4** COO/Ops · **5** 🆕 **assistants and receptionists — the
CEO substitute** · **6** department inbox · **7** generic inbox ·
🔴 **CEO/ED/President OFF by default at any org size.**

**Record the rank of every recipient on the card, and print `Redundancy: N of 3`** — three recipients
is a reliability control, not just reach (R2).

**What survives from the gauge below:** the CCR&R-at-any-seniority ruling, and its reasoning about
not making a cold email to a large agency's CEO read as a power move. **What does not: the headcount
threshold.**

### 🎯 Right-size the To — Chris, 2026-08-12 (org-scale gauge) — ⚠️ SUPERSEDED IN PART BY R4 ABOVE

> *"In some of these organizations, the CEO is the wrong person to email. If the organization is
> big, then there are likely to be assistants, or other directors who will be more likely to open
> and reply… if you email the CEO directly, it looks like a power move, which isn't what I want to
> communicate."*

**The To is the most senior person who plausibly reads their own inbox about PD.** Gauge the org's
scale during the Gate 1 read and choose accordingly:

| Org shape | Signals (record which fired on the dossier card) | To | CEO/ED on thread? |
|---|---|---|---|
| **Standalone CCR&R** — child care IS the org | Staff page ≲ ~15 people · ED appears on program pages · single-program site | ED/Executive Director (as before) | ✅ To |
| **Multi-program parent** — child care is one division of many | Community-action agency / umbrella nonprofit · site lists several program domains · a program/CCRC **director layer exists between the CEO and the training staff** · staff ≳ ~25 · CEO absent from program pages | **The child-care/CCRC program director** | 🔴 **Off the thread entirely** — a cold email to the CEO of a large agency reads as a power move or gets screened by an assistant |

> ✅ **CONFIRMED 2026-08-18 — seniority does NOT limit the CCR&R rule, and Chris was asked
> explicitly.** On 08-18 the CCR&R-title rule put a Coordinator or Specialist ahead of a CEO at five
> of seven Florida coalitions, and that was raised as possibly over-applying it. **Chris:** *"It's
> okay if the CCR&R sits lower in a larger org. They are still the most likely to be the most
> relevant people to talk to. Let's continue with that method and I'll adapt as we go."*
> **So: a CCR&R title takes the To at ANY seniority — Coordinator, Specialist, Director alike.**
> Do not raise this again as an exception; it is the rule working as designed. The function matters,
> not the rank.
| Ambiguous | Mixed signals | Program director, and say so on the card | Chris can add the CEO at review |

**Origin:** Chris's first-ever To-removal (Jefferson County, 2026-08-12) — CEO [Person 0142] cut,
CCRC Director [Person 0140] promoted to To — plus his standing question about [Org 0473]'s $32.7M parent.
Applied to the sequence, not just Email 1: follow-ups inherit the corrected thread.

## PHASE 4 — RECORD

### 🔴🔴 CONCISE IS A PROPERTY OF THE REPORT. NEVER OF THE RESEARCH. — Chris, 2026-08-19

> ✅ **Chris, 2026-08-19, and this governs every efficiency rule in this file:**
> *"I know that I've asked to be more efficient and concise in some parts of this project, but the
> contact research must be comprehensive and thoughtful. It's mission critical that we get as many
> verified contacts as possible and that we verify them effectively. **This is worth extra time and
> cost to get this right.**"*

**READ THIS BEFORE APPLYING ANY EFFICIENCY RULE IN THIS FILE.** The RUN EFFICIENCY section, the
900-byte card target, the archive rotation and the thin launcher are all about **what the machine
WRITES**. They say nothing about how hard it looks.

| Make this shorter | Never make this shorter |
|---|---|
| The review file · the cards · the report · the launcher · the program's own prose | **Page reads · the roster sweep · the reverse lookup · vendor spend · adjudications · the evidence written to [[verification-log]]** |

🔴 **THE FAILURE THIS RULE EXISTS TO STOP, and it is on the record.** On 2026-08-19 ELC of Florida's
Heartland published its staff directory as a PDF. The run recorded `0 Tier-1/2 identified`, dropped
to a tier-4 shared inbox, and moved on — **an efficiency behaviour applied to the one part of the job
where thoroughness IS the job.** One free domain query found **[Person 0080], "Director, Child
Development and Education Services," at that organisation since 2012.** The buyer was one call away.

**The operating principles that follow:**

1. 🔴 **Cost is not a reason to stop looking.** The nightly lookup budget is a floor to spend, not a
   ceiling to protect. **Unspent budget with a reachable person unfound is a defect** — already law
   in Phase 1, and it applies to the reverse lookup too.
2. 🔴 **"Not published" is never a conclusion.** It is a fact about a website. Exhaust: the org's own
   pages · the CMS REST API · the vendor by name · **the vendor by domain** · every other own-site
   page · the org's own auto-replies.
3. 🔴 **Descending the tier ladder is a LAST resort and must be earned in writing.** A tier-3 or
   tier-4 card is invalid without a `Reverse lookup:` line showing the hunt actually happened.
4. 🔴 **A short card is not permission for a short search.** If the research was thin, the card says
   so plainly rather than reading clean.

**Where the depth goes: [[verification-log]].** It is uncapped and always has been. **The card is a
review surface for Chris; the log is the evidence record.** Cutting the card must never cut the log.

### 🔴 THE REVIEW FILE FORMAT — REVISED 2026-08-19 ON CHRIS'S INSTRUCTION

> ✅ **Chris, 2026-08-20:** *"This needs to be more concise, overall. I need the 'here's where I found
> all the staff names' page to be at the top of each Card and as a url I can click for verification."*

**The 2026-08-19 review file was 36,892 bytes for 13 drafts — roughly 2,800 bytes per card, most of
it prose Chris does not need at his review step.** He is checking names, titles, organisations and
domains against a source. **Everything else is audit trail and belongs below the fold or in
[[verification-log]].**

> ✅ **Chris, 2026-08-19 — the header table STAYS and becomes the primary surface:**
> *"I think the header table is the actual format I want to see. It's short, concise, and shows the
> information I want to see in a structured way."* · *"I like the reordering so that the actions are
> first. This is exactly how I will use the document. Right now, I've been digging through the file
> to find the links I need to verify the contacts you show."*

**FILE ORDER — action first, audit last. This is how Chris reads it, beside his Drafts folder.**

| # | Section |
|---|---|
| **1** | 🔴 **DECISIONS — only what needs Chris.** Nothing above it. *(Was at the BOTTOM of a 37 KB file)* |
| **2** | The three mandated blocks, one line each: run manifest · file freshness · roster sweep |
| **3** | 🔗 **THE HEADER TABLE — the primary review surface, WITH THE VERIFY LINKS IN IT** |
| **4** | The cards — evidence layer, Gmail order |
| **5** | HELD orgs — one line each |
| **6** | *below the fold:* pre-send self-check · attachments · Power Map of people NOT on any email |

#### 🔗 THE HEADER TABLE — verify links live HERE

```
| # | Org | To | Cc | Tier | 🔗 Verify | Draft | Thread |
```

🔴 **The `🔗 Verify` column holds the raw clickable URL of the page where the staff names were
found.** Chris scans one table and clicks straight through. **He should never have to open a card to
find a link** — that was the whole complaint.
**Two source pages → two URLs in the cell.** Never compress two sources into one link.

#### The card — the evidence layer beneath the table

```
## N · <Org> · <ST> · Email <1|2|3> · Tier <1-5>
🔗 VERIFY: <same URL as the table row — repeated so the card stands alone>

**To** <address> — <Name>, "<title quoted from that page>"
**Cc** <address> — <Name>, "<title quoted>"

Roster resolution: <line>
Reverse lookup: <line — REQUIRED on any tier-3 or tier-4 card>

⚠️ <one line each, only if it changes what Chris does>
```

🔴 **The card does NOT restate subject, draft ID, thread ID or template version — the table owns
those.** Single ownership, inside the file. **[[CAPA-2026-08-17-dossier-draft-divergence]] was caused
by exactly that duplication**: the dossier said someone was off the thread while the draft had them
in the To. One fact, [Org 0934].

**Cut from the card, and where each goes:**

| Cut | Goes to |
|---|---|
| Org Snapshot (mission, address, headcount, revenue) | [[verification-log]] |
| Pain Hypothesis · Positioning Hook | [[verification-log]] — written to convince a reader who does not need convincing |
| Power Map rows for people **on** the email | The To/Cc lines |
| Power Map rows for people **not** on the email | Below the fold, once, for all orgs |
| Evidence prose | The 🔗 URL, plus the 👉-pointer protocol in [[verification-log]] |
| Non-actionable watch-outs (malformed footers, broken hrefs) | [[verification-log]] |

🔴 **TARGET: ≤ 900 bytes per card; the run reports the average.**
🔴 **AND READ THE SECTION ABOVE BEFORE APPLYING IT — a short card is not permission for a short
search.** The evidence discipline does not loosen, it moves.

### 🔴 ONE REVIEW FILE PER RUN — the dossier and the batch file are MERGED (2026-08-18)

**They were ~70% duplicate content.** The dossier held org snapshot, power map, evidence and
watch-outs; the batch file held recipients, draft IDs, subjects and `template_source` — restating
the same recipients and the same reasoning in a second place. **Two files describing one batch is
also how they drift apart**, which is exactly the 2026-08-17 defect where a dossier card said a
person was off the thread while the draft had them in the To.

**Write ONE file per run: `review-YYYY-MM-DD.md`.** It carries everything Chris needs beside his
Drafts folder *and* everything the audit trail needs:

- **A header table** — org · To · Cc · recipient tier · draft ID · thread ID · `template_source`
  (this is the old batch file, and **a run with no `template_source` is invalid**)
- **One card per org**, in Gmail order, newest first — Org Snapshot → Power Map → Pain Hypothesis →
  Positioning Hook → Draft, with the 👉-pointed evidence line per recipient
- 🆕 **The `Roster resolution:` line on every card**, directly under the Power Map, with
  `unpublished = submitted + deferred` satisfied. **A card without it is invalid and its org holds**
- 🆕 **The roster-sweep block** at the top of the file, matching the one in the Phase 7 report:
  orgs carded / passing / invalid · lookup budget spent vs Tier-1/2 left unqueried · blocked
  directories carried forward with their asset URLs
- **The pre-send self-check**, one line per draft
- **Attachments**: forward-master + the two manual fallbacks, per Email 1 draft
- **Anything held**, with the reason and what would unblock it

*(`batches/` is retained read-only for history. Do not write new files into it.)*

### Then update state

[[sequence-tracker]]: position, draft ID, thread ID, dates, next due.
[[verification-log]]: both gates' evidence per address.
[[recipient-profile]]: 🔴 **the recipient learn-pass goes HERE, not into the tracker** — Phase 5 says
*"recipient patterns are folded into recipient-profile immediately,"* and the 2026-08-19 run put them
in [[sequence-tracker]] instead.
Then `contacted.md` (only when something was SENT) and a dated line in [[CCRR-Outreach-Log]].

🔴 **[[discovery-pipeline]] — UPDATE IT EVERY RUN. MOVED HERE FROM PHASE 6 ON 2026-08-20.**
Funnel counts (§4), stage lists (§5), the state map when a state is swept (§3), §6 national progress
and the conversion ledger, and the `updated:` date. **The criteria (§1–2) change only when Chris
changes a rule.** It sat in Phase 6, which is conditional and skippable, while claiming to run every
run — the same unreachable-obligation trap that hid the suppression gap for four runs.
**A run that touches the pipeline without updating the dashboard has not finished Phase 4.**

**Check the live-file sizes as you go** — see the run-efficiency section at the top of this file.
Above ~35 KB, roll older entries into `archive/` verbatim and leave a pointer.

### Orphan recovery — run this at the START of Phase 4, every time

> 🆕 **This is the SECOND of two reconciliations, not the only one. See Phase 0 step 2.** This pass
> catches drafts the *run itself* orphaned. It cannot catch what Chris sends **after** the run closes
> — which on 2026-08-18 was two of three drafts, thirty-four minutes later, leaving the tracker
> stale until the CAPA found it. **Phase 0 reconciles what happened since last time; Phase 4
> reconciles what happened tonight.** Both run, every run.

**A run that dies between Phase 3 and Phase 4 leaves drafts in Gmail that no vault file knows
about.** They carry the label, they look legitimate, and nothing tracks them. The next run's gate
reads [[sequence-tracker]], sees no record, and can draft the same org twice.

**Before writing anything, reconcile:**

1. `list_drafts` → every thread carrying `CCR&R outreach`
2. Compare against [[sequence-tracker]]
3. **In Gmail but not tracked → an orphan.** Record it in the tracker with a `RECOVERED` note, or trash it if it duplicates a tracked draft
4. **Tracked but not in Gmail → sent or deleted.** Check Sent; update status accordingly

**Gmail is the authority on what exists. The tracker is the authority on what it means.** When they
disagree, Gmail wins on existence and the tracker gets corrected — never the reverse.

## PHASE 5 — LEARN AND REPORT (never auto-apply)

> **Chris, 2026-08-11:** *"I want the learning to happen, but I don't want it to automatically
> rewrite anything. I want it to notice, learn, and report to me what it's learning."*

**The loop has two halves and they behave differently.** Chris, 2026-08-11:
*"The language we don't really want to change unless I explicitly tell you to. But I would like you
to start learning what kind of other people I'm adding."*

| What changed | Response |
|---|---|
| **Copy / language** | 🔒 **Frozen.** Log it, change nothing, don't even propose from one edit. The template changes only when Chris says the words. Do not count occurrences toward a rule |
| **Recipients** | 📈 **Learn actively.** Every person Chris adds is a person the machine should have found. Look them up on the org's own site, record title and tier in [[recipient-profile]], and check whether the pattern is already covered |

**When Chris adds a recipient, that is a defect report, not a preference.** Two for two so far —
[Person 0591] (Professional Development Specialist) and [Person 0278] (Early Childhood Quality
and Coaching Manager). Both Tier 1 by title, both on their employer's own staff page, both missed
because the roster step didn't run.

Diff sent-vs-drafted **FULL-BODY — snippets are not a diff.** Retrieve the complete sent message and compare it against the complete draft, character for character; a Gmail snippet truncates before the paragraph most template edits land in, and a template-changing line was missed exactly that way on 2026-08-12. Then **log it, change nothing.** No template edits, no rules that graduate
themselves. Language patterns are reported at 3+ occurrences and Chris answers yes or no; recipient
patterns are folded into [[recipient-profile]] immediately.

**Replies are the prize** — captured verbatim, never paraphrased, top of the report. A reply stops
that org's sequence.

### Conversion tracking — every run, no exceptions (Chris, 2026-08-12)

**The machine maintains the conversion ledger in [[discovery-pipeline]] §6.** Counted per
organization, cumulatively: approached → replied → meeting proposed → meeting booked → meeting held →
offer made → days booked.

> 🔴 **REWRITTEN 2026-08-20 — R16. The old sentence here said meetings *"can only come from Chris or
> his calendar/CRM,"* and the machine only ever acted on the first half.** ✅ **Chris:** *"The machine
> should not need me to tell it the outcome. It should know to look in hubspot and fathom for
> conversation records."*
>
> **Run the R16 detection BEFORE printing the ledger, every run:**
> **① Fathom `list_meetings`** → match `calendar_invitees` against Ledger B addresses and Ledger A
> domains → 🎯 **`meeting held`.** A recording cannot exist for a call that did not happen, and it
> works retroactively · **② Google Calendar** → `meeting booked` 🔴 *connector needs reconnecting* ·
> **③ HubSpot `MEETING` objects** → corroborating only, **partial by design** — it records only
> meetings booked through HubSpot, and the 2026-08-20 Dutchess booking is **not** in it ·
> **④ reply-scanning** → `meeting proposed`.
>
> 🔴 **Asking Chris is step 5, not step 1**, and only `offer made` and `days booked` genuinely require
> him — no connector observes those. **`meeting held` sat at zero for ten days while three reports
> asked him for a fact that was sitting in Fathom.**

Replies and bounces the machine counts itself from Gmail. Rates are recalculated and
the 667-org requirement re-derived every time a stage count changes. The current 3% offer rate is
n=1 and says so wherever it's printed.

## PHASE 6 — DISCOVERY INCREMENT (bounded)

Per [[CCRR-Contact-Engine-Spec]] §5 and §8. **The only phase with a fetch budget.** Caps in
`STATE.md`. Coverage-greedy CCAoA parameter sweep; a county counts as covered only if it appears in
a returned agency's Areas Served. **Never follow a "Secret Link" or `/<hex>` path** — WP Defender
honeypot, bans the IP.

People-find on each org's own site for the decision-maker **and** the training/PD lead, then the
full gate stack:

- 🔴 **Not in [[contacted]] Ledger A — the org has never been on a sent email (R1 contact-once gate)**
- 🔴 **No proposed recipient is in [[contacted]] Ledger B (R11 person check)**
- ~~Not in `CCRR-Suppression-Already-Contacted.md`~~ → 🆕 **folded into Ledgers A and B, 2026-08-20.**
  That file had been frozen since 2026-06-16; **one list to check, not two, one of them stale**
- **Not in [[hubspot-suppression]]** §A domains, §B addresses, §C internal, or §D needs-Chris
- No prior sequence history at that domain in Apollo
- Kit — **READ-ONLY** (`list_subscribers`, `filter_subscribers`, `get_subscriber` only)

### HubSpot suppression — 🔴 MOVED TO PHASE 0 STEP 1c ON 2026-08-20. DO NOT RELY ON THIS COPY.

> 🔴 **THE REFRESH NO LONGER LIVES IN PHASE 6, AND THAT IS THE WHOLE POINT.** Nesting a safety
> control inside an optional, bounded, second-to-last phase meant it stopped firing the moment the
> batch started being filled by Phase 1 instead of Phase 6 — **four runs, seven days, undetected.**
> **It now runs unconditionally at Phase 0 step 1c and gates Phase 2.** The reasoning below is kept
> because it is correct and load-bearing; only its position changed.
> See [[CAPA-2026-08-20-unreconciled-run-manifest]].

**Rebuild [[hubspot-suppression]] at Phase 0 of EVERY run — not every *discovery* run**, before
gating anything.
HubSpot changes daily: a prospect becomes a customer, a deal opens, Chris BCCs someone new. **A
cached suppression list is a stale suppression list** — the same failure class as the 2024 brochure
that caused the bounce.

**Suppress relationships, not CRM presence.** This is the correction the live data forced on the
June spec, which said to *"exclude existing HubSpot contacts entirely."* HubSpot holds 308 contacts
across 169 domains — but **283 arrived via the browser extension in list-building bursts.** They are
prospects Chris saved, not people he knows. **Blanket domain suppression would block most of the
addressable market to protect ~25 real relationships.**

| Signal | Suppress? |
|---|---|
| A deal at **any** stage, including `closedlost` | 🔴 Yes — he pitched them |
| `lifecyclestage` is **anything other than `lead`** | 🔴 Yes. Match on *not-lead*, **never on the strings `customer`/`opportunity`** — 7 records carry a raw enum `957610056` and would slip past a name match |
| `hs_lead_status` set to any value | 🔴 Yes — a human touched it |
| `hs_object_source_label` ∈ `FORM` / `CRM_UI` | 🔴 Yes → §D. **The most reliable relationship signal in this CRM**, better than lifecycle stage |
| ~~`hs_object_source_label` = `BCC_TO_CRM`~~ | ✅ **NO — RETIRED 2026-08-20 (Chris).** *"The hubspot browser extension is working. That means we don't have to worry about that part. Update the tasks/method accordingly by removing any need to monitor or act on bcc to crm."* **Neither suppress on it nor report on it.** See the ruling in [[hubspot-suppression]] |

> 🔴 **WHY `BCC_TO_CRM` WAS RETIRED, because deleting a suppression signal deserves a reason on the record.**
> It was never wrong about what it measured — it measured *"an email passed between Chris and this
> address."* **It became useless because the machine started generating it.** Chris's browser
> extension BCCs HubSpot on every send, including every cold Email 1 this machine drafts, so within
> minutes of an approach the recipient acquires a `BCC_TO_CRM` record. **The signal can no longer
> distinguish a relationship Chris built from an approach the machine just made** — and left in
> place it would suppress the machine's own in-flight organisations, blocking Email 2 and Email 3 on
> live sequences. **`FORM` and `CRM_UI` are unaffected and remain hard signals: the machine cannot
> manufacture an inbound form fill or a hand-created CRM record.**
| `lead` + `EXTENSION` + no deal | ✅ No — this is the target market |

⚠️ **Never block `org0038.example`.** A company record carries it as a domain, scraped from one contact's
DoD work address. Blocking it would suppress the United States Army. **Block that individual
address.** Full trap list in [[hubspot-suppression]].
- Not in CO, KY or GA → Review Queue
- **Not a referral portal — judged by function, not domain** (D-16: *"online-only, no address/phone"*).
  **A `.gov` address is not disqualifying.** [Org 0655] is a council of governments that
  operates its CCR&R: real agency, real staff, `.gov` mail. The old TLD rule would have discarded
  all nine of its correct addresses
- **Both gates passed** → ENROLLABLE. One → HOLD

**Intel is part of the job.** Record who runs PD, when their planning window is, what they just
published. Each approach should get smarter, not just more numerous.

**If discovery fails, log it and continue.** It never takes down drafting.

### 🔴 ~~Update [[discovery-pipeline]] every run~~ — MOVED TO PHASE 4 ON 2026-08-20. DO NOT RELY ON THIS COPY.

> 🔴 **Same trap as the suppression refresh, caught before it fired.** This obligation says *"every
> run"* while living inside **Phase 6, which is conditional** — Phase 1 step 4 runs discovery *"only
> if the target still isn't met,"* `pool_ceiling` skips it, and *"if discovery fails, log it and
> continue."* **An unconditional obligation inside a conditional phase is unreachable and nobody can
> tell.** That is exactly how the suppression refresh went four runs unnoticed.
> **It now lives in PHASE 4 — RECORD, which runs every time.** The reasoning below is kept because it
> is correct; only its position changed. Found by the Stage-2 owner check in [[ROADMAP-thin-launcher]].

#### The original text, kept for the reasoning — Chris, 2026-08-12

> *"I can't tell how discovery is working, in what order it is searching through various states...
> I can't see a current list that shows here are the organizations discovered in the scraping, here
> are the orgs with valid email addresses that fit our criteria, here is the list of criteria
> itself."*

**[[discovery-pipeline]] is the answer to that, and it is only an answer if it's current.** Every
run updates: the funnel counts (§4), the stage lists (§5), the state map when a state is swept
(§3), and the `updated:` date. The criteria (§1–2) change only when Chris changes a rule. A run
that touches the pipeline without updating the dashboard has not finished Phase 6.

## PHASE 7 — REPORT

**Written for a reader with zero context, per the plain-language rule at the top of this file.**
Any shorthand gets defined in the sentence that uses it. The credit line always shows: balance
before → after → spend → itemized causes (or "UNEXPLAINED" if they don't sum).

**Every report ends with the national progress line**, pulled from [[discovery-pipeline]] §6 after
updating it — one sentence in this shape: *"National progress: N orgs approached of ~667 needed
(X%), M orgs discovered and waiting, universe estimate ~550–750."* Progress is counted in
**organizations, never states or counties** (a state is one org in Kentucky and thirty in Florida).
The funnel numbers (meetings, offers) revise the 667 as real data accumulates — the current 3%
offer rate rests on a single offer and must not be treated as settled.

Rewrite `STATE.md` Config and Run Status, then report: replies verbatim first · drafts by org and
sequence position · ENROLLABLE vs HOLD counts · **the golden reference message ID to forward, per
draft, plus the two manual fallbacks** · what was noticed (never
applied) · contacts held for Chris · discovery results and pool depth · anything that failed.

### 🔴 WHAT A REPORT MAY ASSERT — R12.6, added 2026-08-20

> 🔴 **A CLAIM THAT SOMETHING DOES NOT EXIST MUST NAME EVERY STORE THAT WAS SEARCHED — or be written
> `"not found in X"` rather than `"does not exist."`**

**On 2026-08-20 this run made THREE false absence-claims in one session:** that nothing was attached
to the follow-ups (Chris had stripped it by hand), that the Five County draft had no provenance (it
was in [[verification-log]]), and that two bounces were never recorded (they were, with a CAPA, in
`CCRR-Suppression-Already-Contacted.md`). **All three were the same error — search [Org 0934], find
nothing, report absence as fact.**

**[[method]] already forbids asserting an unverified address — *"if you cannot quote the line, it is
not verified."* This extends the identical discipline to asserting an absence.** An unsearched store
is not evidence of nothing being there.

🔴 **Two more report lines are mandatory from 2026-08-20:**

> `Contacted ledger: N sends found · M newly logged · current as of <timestamp>` **(R14)**
> `As-sent delta: N reconciled · M recipient changes by Chris · [org: drafted X → sent Y]` **(R13)**
> `Market: N outreached · ~M remaining · ~W working days of runway` **(R9)**

🔴 **When runway drops below 20 working days the report RECOMMENDS a pace change.** At 10 orgs/day the
~580–790 universe is exhausted mid-November to mid-December. **Running out of market with weeks left
in the year is a worse outcome than pacing slower.**

### 🔴 THE RUN MANIFEST BLOCK — mandatory in every report from 2026-08-20 (P2 + P3)

**Two lines, printed every run, no exceptions. A REPORT WITHOUT THEM IS INVALID** — same standing as
a card without its `Roster resolution:` line.

> `Run manifest: N obligations · N completed · N skipped (reason each) · N FAILED`
> `File freshness: <file> <YYYY-MM-DD> · <file> <YYYY-MM-DD> · …  (flag anything >1 run stale)`

#### P2 · The completion line — it is arithmetic, not a summary

> 🔴 **IDENTITY: `obligations = completed + skipped + FAILED`.**
> **If it does not balance, the run is reported as INCOMPLETE regardless of how many drafts it
> produced.** Name every `skipped` item with its reason and every `FAILED` item with what broke.

**This is the countable object the manifest needs.** P1 without P2 regresses the first time a run
gets busy — exactly as `spend_lookup_when_unpublished` did on the day it was ratified.
**A skipped item with a stated reason is a perfectly good outcome. A skipped item nobody counted is
the defect.**

⚠️ **`skipped` is NOT scored as a failure.** If it were, the cheapest route to a clean report would
be to leave the obligation off the manifest — which is the pre-CAPA behaviour. **Same trap as
folding `B` into `M`.** Only `FAILED > 0` and an unbalanced identity are defects.

#### P3 · The file-freshness line — let arithmetic do the catching

**Print the last-modified date of every file the run is obliged to WRITE**, with the run-count gap:

```
File freshness: hubspot-suppression 2026-08-13 🔴 4 RUNS STALE · recipient-profile 2026-08-18 ·
sequence-tracker 2026-08-19 ✅ · verification-log 2026-08-19 ✅ · discovery-pipeline 2026-08-19 ✅ ·
contacted 2026-08-18 (correct — nothing sent)
```

🔴 **Anything more than one run stale is a DEFECT and the report names it.** It costs one directory
listing and requires **no judgement at all** — which is precisely why it works. **This line would
have caught the suppression gap on 2026-08-14, the morning after it first happened, instead of seven
days and four runs later.**

**Files in scope:** `hubspot-suppression` · `recipient-profile` · `sequence-tracker` ·
`verification-log` · `discovery-pipeline` · `contacted` · `STATE` · the run's `review-YYYY-MM-DD`.
**`contacted` is exempt from the stale flag on nights when nothing was sent — say so on the line.**

### 🔴 THE ROSTER SWEEP BLOCK — mandatory in every report from 2026-08-18

**Three lines, printed every run, no exceptions. They are the effectiveness check for
[[CAPA-2026-08-18-unqueried-tier1-roster]] and they are how Chris knows the fix is holding.**

> `Roster sweep: N orgs carded · N passing (all three identities hold) · N invalid`
> `Orgs HELD at the roster gate: N — [org (n Tier-1/2 unqueried)], …`
> `Lookup budget: N of 25 spent · Tier-1/2 people left unqueried: M · orgs with unreadable rosters: B`
> `Blocked directories carried forward: [org — asset URL or "URL not yet captured"]`

**`M` counts PEOPLE. `B` counts ORGS. They mean opposite things — keep them apart.**

| Term | Counts | Verdict |
|---|---|---|
| `M` | People in `unpublished` who were neither `submitted` nor `deferred`, summed across carded orgs | 🔴 **`M > 0` with budget remaining is a DEFECT.** Name the orgs |
| `B` | Orgs whose `named on page` carries a `+` — a directory nobody could read | ✅ **NEVER a defect. Reporting `B` is the run doing its job** — a backlog figure, not a failure |
| `HELD` | Orgs that failed the roster gate and produced no card | 🔴 **`HELD > 0` disqualifies a clean block.** A held org appears in none of the other lines — say it here or it vanishes |

🔴 **`B` IS NOT A DEFECT, AND THIS IS DELIBERATE.** An earlier draft folded `B` into `M`, which made
P4 unpassable: P4 orders the run to card a blocked org and draft it anyway, and doing so would then
have registered as a failure. **That makes the cheapest route to a clean report "don't card the
blocked org" — exactly the pre-CAPA behaviour P4 exists to end.** Honesty about an unreadable roster
must never cost the run its clean block.

**Pass condition: `invalid = 0` AND `M = 0` AND `HELD = 0`. `B` is reported and carried, never scored.**

**Rules for reading them:**

- 🔴 **`invalid > 0` is a failed run**, regardless of draft count. Name the orgs and what was missing.
- 🔴 **`M > 0` with budget remaining is a DEFECT**, not a saving. Name the orgs.
- **A clean block is `invalid = 0`, `M = 0`, `HELD = 0`. `B` is reported, never scored.**

**Effectiveness check, running through 2026-08-25.** The next three runs are the test of this CAPA.
One question against each: **for every org carded, does `unpublished` equal `submitted` + `deferred`?**
Any gap without a stated per-person reason is a repeat, and the CAPA reopens.
**First test run: the next scheduled run after 2026-08-18.**

---

## Failure modes

> 🆕 **The rows marked §0 are enforced by the PRE-FLIGHT BLOCK at the top of this file, not by
> memory.** They hold the draft before it exists. Added 2026-08-24.

| If | Then |
|---|---|
| 🆕 **A draft has more than 1 To or more than 2 Cc** | 🔴 **HOLD — §0.4 U1.** Drop the lowest-ranked recipient under R4 and name the drop on the card. **The cap is level 2; `inherit-from-email-1` is level 4. The convenience yields** |
| 🆕 **The greeting names someone who is not a recipient, OR a recipient is named in no greeting** | 🔴 **HOLD — §0.4 U2.** Both directions. Never a decision item — fix it and report |
| 🆕 **The binding-instruction section of [[sequence-tracker]] was not read for this org this session** | 🔴 **HOLD — §0.4 U9.** The general rule may not be applied while a specific one is unread |
| 🆕 **This org's thread was not checked in Sent this session** | 🔴 **HOLD — §0.4 U10.** Chris acts between runs; Phase 0's reconciliation is not sufficient at the moment of a draft |
| 🆕 **`Tier-1/2 identified == 0` while `named on page >= 1`** | 🔴 **HOLD — §0.4 E1.5.** The card must name the highest-ranked person found and why they are not used. **Ranks 4 and 5 exist; do not skip to 6–7** |
| 🆕 **A sweep was run with a filter in the query** | 🔴 **Invalid — D-SWEEP (§0.2).** Retrieve unfiltered, filter afterwards. Binds drafts, bounces, auto-replies, sent mail |
| 🆕 **A rule breach was placed in the DECISIONS table** | 🔴 **Invalid — D-TABLE (§0.2).** If a rule determines the answer, execute and report. The table is for Chris's preferences only |
| 🆕 **A new cluster's first batch was drafted with no rank-list vocabulary review** | 🔴 **HOLD the batch — §0.7.** Read three of the cluster's own sites and add the missing rank-1 signal words first |
| 🆕 **Any address at this org's domain was ever sent to** | 🔴 **ORG CLOSED — R1.** No new thread, at all. Not for a better contact, not after a bounce. **Only Chris reopens it** |
| 🆕 **A proposed recipient's address is in Ledger B** | **Remove that person from the draft** and record why. **This is the Five County check** |
| 🆕 **[[contacted]] does not contain every send Gmail knows about** | 🔴 **NO DRAFTING — R14.** Same standing as stale suppression. Run the 3-day sent sweep first |
| 🆕 **A follow-up inherits an address marked `bounced`** | **Drop it · rewrite the greeting · insert the approved bounce parenthetical · print `Redundancy: N of 3`.** Never let a name vanish silently — **R2** |
| 🆕 **Someone not on Email 1 is proposed for Email 2 or 3** | 🔴 **REFUSE — R5.** *"It would look like we are intentionally going around the non-responders."* Only the org introducing them, or Chris, permits it |
| 🆕 **The drafted address does not match its quoted source character-for-character** | **HOLD the recipient — R6a.** Print both on the card |
| 🆕 **The To recipient's employment is unconfirmed or contradicted by the vendor** | **HOLD — R6b.** The next-ranked person takes the To |
| 🆕 **The CEO/ED is proposed while ranks 1–6 can still fill 3 slots** | **Wrong recipient set — R4.** Re-sort. **Prefer their assistant over them** |
| 🆕 **A card has no `Redundancy: N of 3` line** | Incomplete. Three recipients is a **reliability** control, not just reach |
| 🆕 **An open lead ends the run with no terminal state** | Report it `OPEN — N runs` with the count — **R15.** A lead without a number gets carried forever |
| 🆕 **A report asserts something does not exist** | **It must name the stores searched, or say "not found in X" — R12.6.** Three false absence-claims on 2026-08-20 |
| 🆕 **An auto-reply lands on a thread** | 🔴 **It is NEVER a reply — R17.1.** Do not trigger `stop_on_reply`. **Classify first** (absence / departure / standing autoresponder / no-date), then act. A HUMAN reply that mentions an absence IS a reply and DOES stop the sequence |
| 🆕 **An auto-reply's return date is in the past** | **IGNORE IT ENTIRELY — R17.2.** They forgot to switch it off. Proceed as if it never arrived. A date of TODAY counts as present |
| 🆕 **Some but not all recipients are out** | **No delay — R17.2.** A non-responder's implicit return date is today, and the rule is soonest-of-anyone. **The hold fires only when EVERY recipient is out** |
| 🆕 **An auto-reply gives no return date** | **7-day delay, then proceed — R17.3.** Same for any stated return beyond the 14-day ceiling |
| 🆕 **An auto-reply says the person has left** *(unambiguous)* | **AUTO-SUPPRESS + run the R2 thread repair — R17.4.** Drop · rewrite the greeting · insert the approved parenthetical · `Redundancy: N of 3`. 🔴 **Excluded from the bounce rate** — an auto-reply is not a DSN |
| 🆕 **An auto-reply merely HINTS the person may have left** | 🔴 **FLAG FOR CHRIS — R17.3. Do not delay, do not suppress, do not guess.** Quote the line and hold that recipient. *A wrong suppression is invisible and permanent* |
| 🆕 **An auto-reply names a covering colleague** | **Harvest to [[verification-log]] as known-but-not-contacted — R17.5. NEVER add them to a live thread.** R5 is unchanged: an autoresponder is not the organisation introducing someone |
| 🆕 **An auto-reply arrives from a DIFFERENT domain than the one emailed** | **R15 open lead — possible domain migration.** Origin: `person0177@org0341.example` emailed, reply from `person0178@org0664.example` |
| 🆕 **A follow-up is held for an OOO and the report does not say so** | **DEFECT.** A silent missing follow-up reads as a shortfall. The `Auto-replies:` line is mandatory — R17.7 |
| **Gate 2 not run for an org** | HOLD. Never draft on Gate 1 alone |
| **Gate 1 unsatisfiable** | No email address exists. Phone/LinkedIn. Never a directory fallback |
| 🆕 **Roster sweep not run** | HOLD the org. A Tier-1/2 person whose address is unpublished and who was never submitted to the vendor is a failed gate, not a judgement call |
| 🆕 **Card has no `Roster resolution:` line** | **CARD INVALID.** Do not draft. The line is arithmetic — its absence means the sweep did not happen |
| 🆕 **`unpublished ≠ submitted + deferred`** | **CARD INVALID.** Hold the org and name the gap per person |
| 🆕 **`⛔ NOT QUERIED` with a blank reason** | **CARD INVALID.** "Enough recipients already" is never a reason |
| 🆕 **Any of the three identities fails** | **CARD INVALID.** `identified = published + unpublished` · `unpublished = submitted + deferred` · `submitted = resolved + held + queried-null` |
| 🆕 **`named on page` written with a `+`** | The org is **BLOCKED** and **counts toward `B`, never `M`** — corrected 2026-08-24, D5. `M` counts PEOPLE, `B` counts ORGS; `B` is reported and carried, never scored |
| 🆕 **Vendor returned `Extrapolated`** | Counts as **`held`**, never `resolved`, and never goes on the email. See [[CAPA-2026-08-11-extrapolated-address]] |
| 🆕 **Staff directory is an image or PDF** | **NOT a failed read.** Card as `BLOCKED — DIRECTORY NOT MACHINE-READABLE`, put the direct asset URL on the card, try the CMS REST API and every other own-site page, **draft the org anyway** from whoever is readable, queue the asset for a screenshot |
| 🆕 **Lookup budget unspent while Tier-1 people sit unqueried** | Report it as a **DEFECT** and name the orgs. Never as thrift or efficiency |
| 🆕 **Tracker says DRAFTED, Gmail has no such draft** | Check Sent. Mark SENT and record the **as-sent** To/Cc verbatim — Chris edits recipients at review and the follow-ups inherit them |
| 🆕 **`hubspot-suppression` `last_refresh` is not today** | 🔴 **NO ORG PASSES PHASE 2.** Run Phase 0 step 1c. If the connector is unreachable, report the failure and **HOLD new-org drafting** — due follow-ups still draft. Never draft a new org against a stale list |
| 🆕 **Report has no `Run manifest:` line** | **REPORT INVALID.** The line is arithmetic — its absence means the manifest was never built |
| 🆕 **`obligations ≠ completed + skipped + FAILED`** | **RUN REPORTED AS INCOMPLETE**, whatever the draft count. Name the gap |
| 🆕 **A manifest item has a blank state** | **REPORT INVALID.** Every item is `completed`, `skipped — reason`, or `FAILED — what broke` |
| 🆕 **Any obliged file >1 run stale on the freshness line** | **DEFECT.** Name it and say why. `contacted` on a no-send night is the one exemption, and it must be stated |
| 🆕 **`last_run_status` reads `IN PROGRESS` at Phase 0** | The previous run **died.** Report it, name what it left unfinished, complete the orphaned obligations before starting tonight's |
| 🆕 **A refactor/compression pass touched a program file** | The report must carry a **DIFF OF DELETED OBLIGATIONS** (write/refresh/update/record/verify). No diff → the pass is not complete |
| 🆕 **`mv` from `/tmp` to a vault file fails** | Expected — cross-device unlink is refused. **Use `cp`.** Not an error to diagnose |
| 🆕 **`rm` on a vault file fails** | Expected. **Ask via the delete-permission tool.** If declined, overwrite the file with a tombstone note and report it. Never leave unexplained litter, never call it impossible |
| 🆕 **Archive append succeeded, live overwrite failed** | 🔴 **DO NOT RETRY THE BLOCK — it double-appends.** Re-do only the overwrite. Check with `grep -c` on the roll-in header first |
| 🆕 **Roll-in header appears more than once in an archive** | **Double-append.** Remove the duplicate range, verify with the three P12 greps, and report it |
| 🆕 **Archive rotation triggered but the report has not gone out** | `skipped — report not yet delivered`. Rotate tomorrow. **A destructive step never runs on an unreported run** |
| **Catch-all domain** | ✅ **Send anyway** (Chris, 2026-08-11). Flag it; excluded from the bounce rate because silence there proves nothing |
| **Unresolved hard bounce** | Halt drafting. Audit the source, re-verify its siblings. **A bounce is "resolved" once its source is audited and its siblings re-verified — not when a replacement is sent.** Record the resolution in [[verification-log]] so the breaker clears |
| Roster unverified or incomplete | Don't draft. Hold and name it |
| Template file unreadable | Abort drafting. Never reconstruct copy from memory or a batch file |
| Org doesn't fit the template | Skip, flag. Never adapt the copy |
| Vault or Gmail unavailable | Abort. Never run blind — suppression lives in the vault |
| Apollo unavailable | **Draft only orgs already Gate-2 verified.** Do not proceed on Gate 1 alone |
| Queue empty | Draft the due follow-ups, flag loudly, let discovery refill |

> 📖 **Why the machine is built this way — the reasoning behind two gates, verification-in-discovery,
> never-writes-copy, and report-don't-apply — see [[method-rationale]].**

## Send rules — MERGED FROM THE RUNBOOK, 2026-08-12 (Chris's D-B ruling)

The `CCRR-Outreach-Runbook.md` is retired; these are the rules it held that lived nowhere else.
Everything else it said is already in this file or superseded (its cadence figures are superseded
by `target_drafts`; its "To = all partners" grouping is superseded by the 1-To/max-2-Cc cap).

1. **Org-level dedup — the "someone else at their org" check.** Before drafting to a NEWLY found
   person, check whether anyone else at the same domain was ever touched in ANY channel: Apollo
   (contacts/sequence history), HubSpot (activity or deal), Kit (newsletter subscriber at that
   domain). A prior touch at the org → **FLAG to Chris, never auto-draft** — a second cold email
   into an org that's already been approached needs a human call, and a warm intro may beat it.
2. **Suppression list upkeep.** Repliers and unsubscribers get appended to
   `CCRR-Suppression-Already-Contacted.md` §B (date + reason) and mirrored to Apollo's
   Do Not Contact list.
3. ~~**HubSpot BCC is a standing rule for ALL client-related email.**~~ 🔴 **DISABLED 2026-08-18
   (Chris).** No BCC goes on any draft this machine creates until he says otherwise — the browser
   extension already logs the sync, and the BCC bounced on 6 of 7 attachment-bearing sends. See
   `hubspot_bcc` in [[STATE]].
4. **Kit connector — read-only allowlist for outreach work.** Allowed: `list_subscribers`,
   `filter_subscribers`, `get_subscriber`, `list_tags`, `list_tags_for_a_subscriber`,
   `list_subscribers_for_tag/form/sequence`, `get_current_account`, `get_creator_profile`.
   **Never call** any `create_*`, `update_*`, `delete_*`, `bulk_*`, `tag_*`, `unsubscribe`,
   `add_subscriber_to_*`, `*_broadcast`, `*_sequence*`, `*_webhook` — especially
   `create_broadcast`, which can email the entire newsletter list.
5. **Independent accounting.** [[CCRR-Outreach-Log]] keeps the human-readable record of every run,
   batch and flag decision, independent of Apollo — the debuggable record if vendor data changes.
6. **The Apollo "v1" sequence stays PARKED** — kept, never used. Gmail drafts are the send layer.
7. **`outreach-writing-guide` stays disconnected from this machine** (Chris, 2026-08-11: "We
   should only be working from the templates"). It exists solely for the separate
   outreach-brief-builder skill.

*The runbook's decision log (2026-06-16 → 2026-08-11) is preserved verbatim in the tombstoned
file for history.*

---

# 🔴 CHRIS'S RULINGS — 2026-08-20. These supersede anything above that conflicts.

---

## R1 · ONE ORGANISATION, ONE THREAD, EVER. The contact-once rule.

> ✅ **Chris:** *"I only want to reach out to an org once. I don't want to reach out to different
> groups of people at the same org, unless I explicitly instruct you to do this. The machine should
> default to picking the best, highest quality people… and draft one email with the right people for
> each org. That's it."*

**THE GATE — this is now the FIRST question asked about any organisation, before verification, before
the roster sweep, before anything:**

> **Has any address at this organisation's domain ever been on an email we sent?**
> **If yes → the organisation is CLOSED to new threads. Full stop.**

| Situation | Old behaviour | 🔴 NEW |
|---|---|---|
| Org's Email 1 bounced at the To, a Cc delivered | Org read as "not reached," re-entered the queue | **CLOSED. It was reached.** Continue on the EXISTING thread |
| Org replied and routed us elsewhere | Sequence stopped, org sometimes re-queued later | **CLOSED.** No second thread |
| A re-read finds better people at an org already emailed | Recipients rebuilt, new draft | **CLOSED.** Record them on the card as known-but-not-contacted |
| Org's whole send bounced, nobody received anything | Re-draft | ✅ **Re-draft is permitted** — but as a **repair on the same thread** wherever possible |

🔴 **The only key that opens a closed organisation is Chris saying so explicitly.** Not a better
contact, not a stale address, not a new state sweep. **"We found someone better" is the exact
reasoning this rule exists to refuse.**

**Why — the case that produced it.** [Org 0655], 2026-08-11: To `person0174@org0174.example`
bounced, Cc `person1137@org0389.example` **delivered**. The org was filed `BOUNCED`, a 2026-08-19
re-read rebuilt the recipient list from the staff page, and **[Person 0591] was put back on a
brand-new thread** — she would have received the identical cold intro twice, nine days apart. Caught
by Chris, not by any control.

**The social reasoning, which is the real point.** ✅ **Chris, on a related case:** *"it would be
socially inappropriate… Internally, it would look like we are intentionally going around the
non-responders."* **A second thread at one organisation looks like working around the people who did
not answer.** That damage is invisible to the machine and permanent to the relationship.

---

## R2 · WHEN A RECIPIENT BOUNCES ON A LIVE THREAD — repair, name it, keep the other two

> ✅ **Chris:** *"if we have 3 recipients on the thread but one bounces, we need to adjust by just
> removing that bounced email and readdressing the followup to the two valid recipients."*

**🎯 THE REASON THREE PEOPLE ARE ON A THREAD, IN CHRIS'S WORDS, AND IT REFRAMES THE CAP:**

> *"One of the reasons it's best to have 3 people on a draft is because if we're wrong and one email
> bounces, we still have 2 recipients on the thread who might keep each other accountable to replying."*

**The 1-To/2-Cc cap is not just about reach — it is REDUNDANCY.** A bounce is survivable precisely
because two others are still on the thread. **This makes filling all three slots a reliability
requirement, not a nice-to-have.** An org drafted with one recipient has no redundancy at all.

**THE HANDLER — run it the moment a hard bounce is detected on a thread with an open sequence:**

1. **Drop the bounced address** from the next follow-up. Everyone else stays.
2. **Rewrite the greeting** to the surviving names — `Jackie and Ryan,` → `Hey [Person 0245],`
3. 🆕 **Insert the approved bounce parenthetical**, directly under the greeting. **The exact copy is
   in [[Cold-Outreach-Sequence-CCR&R]]** — it is Chris's own wording from the [Org 0102] send
   (`<thread-id>`) and is the only sanctioned addition to Email 2 or Email 3:
   `(I think I got <First Name>'s email address wrong, so I'm not including him/her on this)`
   🔴 **The pronoun rule still binds — if it is not stated by the person, write `them`.**
4. **Suppress the address** in [[verification-log]] and the person ledger.
5. **Do NOT substitute a replacement person onto the thread** unless Chris says so — see R5.

⚠️ **Below two surviving recipients the redundancy is gone.** Say so on the card:
`Redundancy: 1 of 3 — no accountability effect if this person does not reply.`

---

## R3 · Draft editing — see the rewritten Phase 3 procedure

**Chris's instruction — *"instead of trashing the message, can we simply edit it?"* — is implemented
in Phase 3 above.** Summary: **Email 1 drafts are EDITED IN PLACE** (`update_draft`, same draft ID,
no duplicate possible). **Follow-ups are CREATED then the old draft removed with `trash_message`**,
which touches only that one message. **`trash_thread` is banned.**

---

## R4 · 🥇 THE RANKED RECIPIENT LIST — the CEO is OFF the thread by default

> ✅ **Chris:** *"Let's have a default rule that the CEO should be off the thread unless there are not
> enough other recipients who fit the role descriptions we've set… The solution here may be a rank
> list of the preferred roles and titles so that the machine can order the right recipients until it
> gets to 3 total."*

**HOW TO USE IT: sort every person the org publishes into the ranks below, take the top 3, highest
rank takes the To. Stop at 3. Record the rank of each on the card.**

| Rank | Who | Signals |
|---|---|---|
| **1** | 🎯 **Training / PD owners — the wedge buyer** | Title contains *Professional Development · Training · Coaching · Staff Development · Quality Improvement · Instructional* · **any CCR&R title at any seniority** · **or role evidence quoted from the org's own page**: named as contact for a training programme, bonus, calendar, institute or coaching initiative, even with no title |
| **2** | **Early-learning / programme leadership** | *Chief Program Officer · Chief Program & Policy Officer · Chief [Person 0194] · VP of Education · Director of Early Learning · Director of Programs · Director of Program Quality · Provider Services / Provider Relations Director* |
| **3** | **Practice-quality specialists** | *Quality Specialist · Infant-Toddler Specialist · Inclusion or Behavior Specialist · TRS Mentor · Coach · Assessor · Career Development Specialist · CCQS Specialist* |
| **4** | **Operations leadership with programme proximity** | *COO · Director of Operations.* ✅ Chris: *"At worst, if there are no staff like that, we may have to reach out to the COO"* |
| **5** | 🆕 **Routing roles — the CEO substitute** | *Executive Assistant · Assistant to the CEO/ED · Office Manager · Receptionist · Administrative Coordinator.* ✅ Chris: *"Sometimes these higher ranking roles have assistants or receptionists. Their jobs are to route incoming mail and messages, so it's appropriate to address them instead of the CEO"* |
| **6** | **Department inboxes** | `ccrr@` · `training@` · `providerservices@` — addressed to a named person where the team page names one |
| **7** | **Generic inbox** | `info@` — last resort, non-specific greeting |
| 🔴 **OFF** | **CEO · Executive Director · President** | **Excluded by default at ANY org size.** Included **only** if ranks 1–6 yield fewer than 3 people **and** no rank-5 router exists. **Prefer their assistant over them.** |

🔴 **THIS RETIRES THE ORG-SCALE GAUGE'S "≲15 staff → the ED takes the To" BRANCH.** That rule fired
*correctly* at ELC Sarasota (13 staff) and still produced the wrong answer — Chris moved the To from
[Person 0013], CEO to **[Person 0343], "Chief Program & Policy Officer."** Third override in eight
days (Jefferson County 08-12, ELC Broward and ELC Sarasota 08-19). **The variable was never headcount.
It is function.**

**Two things the ranking does NOT change:** the 1-To/max-2-Cc cap, and the evidence discipline —
**a rank must be justified by a line quoted from the organisation's own page**, exactly like an
address. An inferred rank is not a rank.

⚠️ **If ranks 1–7 cannot produce 3 people, that is a finding, not a failure.** Draft what exists and
record `Redundancy: N of 3` on the card so the thinness is visible before Chris sends.

---

## R5 · Do NOT quietly add people to a thread after the fact

> ✅ **Chris, on adding a recommended contact to an existing sequence:** *"Since we've already sent
> out that email, it would be socially inappropriate to add her to the cc. Internally, it would look
> like we are intentionally going around the non-responders. I don't want that. It's a miss and a
> mistake. We can let it go and maybe come back to it later."*

**RULE: recipients are fixed at Email 1. A person not on Email 1 is never added at Email 2 or 3.**

| Case | Action |
|---|---|
| Better contact found after Email 1 went out | ❌ **Do not add.** Record on the card as known-but-not-contacted. **Stop re-recommending it every run** |
| A recipient **bounced** | ✅ Remove them + the parenthetical (R2). Removing is fine; **adding is not** |
| The org itself names someone in a reply | ✅ Add — **the organisation introduced them.** This is how ELC Alachua's PD owner joined |
| Chris says add them | ✅ Add |

🔴 **CLOSED AS A RESULT — stop raising these:** Schoharie / [Person 0162] (recommended 4 runs) and
[Org 0102] / [Person 0609] + [Person 0515]. **Both are now "let it go."** [Org 0102] proceeds with one recipient.

---

## R6 · Address verification hardening — the two real failure modes

> ✅ **Chris:** *"its our failure of verifying email addresses… Let's fix this verification issue for
> next time."*

**Neither failure was a bad source. Both are now handled directly:**

### 6a · A typo introduced between the source and the draft

**`ccr@org0315.example` vs the org's published `ccrr@org0315.example` — one character, introduced at
review.** Nothing in the pipeline compared the address in the draft against the address in the
evidence.

🔴 **NEW CONTROL — the character-match check, at Phase 3 before every draft is created:**
**Put the address about to be drafted directly beside the quoted evidence line, and compare them
character by character.** If they differ by even one character, **HOLD the recipient and report it.**
**Print both on the card** so a human sees the comparison too:
`To: ccrr@org0315.example ⟷ source: "CCR&R Department — ccrr@org0315.example" ✅ exact match`

**And at Phase 0, re-run the same check against the AS-SENT address** — that is where a hand-edit at
review would show up, and it is the only place Chris's own typos can be caught.

### 6b · A stale cached page naming someone who has left

**`person0936@org0323.example` — McKenna Terrill had left; the staff-page fetch returned a cached copy.**

🔴 **NEW CONTROL — for the **To** recipient only** (the one whose failure costs the most):
**cross-check current employment against the vendor before drafting.** A vendor record showing a
departure, or no record at all where the rest of the roster resolves cleanly, is a **HOLD** and the
next-ranked person takes the To. **Cost is ~1 credit against a nightly budget that closes at zero.**

⚠️ **Also record the page's own publish/modified date when the CMS exposes it** (`article:modified_time`,
`Last-Modified`). A page whose own metadata is older than 12 months gets the same employment check.

---

## R7 · [Org 0554] → retarget to [Org 0609] ✅ APPROVED

> ✅ **Chris:** *"I think it's fair to reach out to the [Org 0609] based on the ELC
> of North Florida site."*

**Their own staff page shows PD is contracted to ECS and publishes two `@org0303.example` addresses.**
Target `org0303.example` as its own organisation. **[Org 0554] is not approached** — and under
R1, approaching ECS does not open the ELC.

---

## R8 · Texas ✅ APPROVED — and it is logged as a new market

> ✅ **Chris:** *"Let's move forward with the new org type in Texas… since this whole outreach machine
> is still a bit of an experiment, we may learn about a new market. Technically, this might be
> considered a new market and thus a new cluster (by TLBS terms). But that's okay."*

**The ~25 remaining Texas workforce boards and CCMS operators are IN SCOPE.** No further approval
needed. 🆕 **Tag every Texas organisation `cluster: TX-workforce-boards`** in
[[discovery-pipeline]] so its conversion rate can be measured separately — **if it converts
differently from the CCR&R cluster, that is a finding about a new market, and it is only visible if
the tag exists from the first send.**

---

## R9 · The target is 10 NEW ORGANISATIONS per working day

> ✅ **Chris:** *"I was thinking of 10 new outreaches a day. So that would mean 10 new organizations."*

**`target_drafts` 7 → 10, counting Email 1 drafts only.** Follow-ups remain uncapped and separate.

🔴 **AND THE MACHINE MUST NOW REPORT MARKET DEPLETION, because at this rate it becomes the binding
constraint inside 90 days.** Universe ≈ 580–790 organisations; 92 are done. At 10/day the remaining
~490–700 are exhausted in **49–70 working days — mid-November to mid-December.**
**Every report carries:** `Market: N outreached · ~M remaining · ~W working days of runway left.`
**When runway drops under 20 working days, the report says so and recommends a pace change** —
running out of market with weeks left in the year is a worse outcome than pacing slower.

---

## R10 · The hosted-GIF change is PARKED

> ✅ **Chris:** *"let's ignore this problem for now since we don't have a workaround for outlook, yet."*

**No change to Email 1.** The attachment chip on follow-ups is cosmetic and expected — **do not
re-raise it.** Revisit only if an Outlook-safe route appears. *(The 5.4 MB size still costs the
HubSpot BCC and its open-tracking; recorded, not actioned.)*

---

## R11 · Track BY ORGANISATION **AND** BY PERSON — both, not either

> ✅ **Chris:** *"I want to track who we've emailed by org and by person."*

**[[contacted.md]] is restructured into two ledgers, and BOTH are checked before any draft:**

### Ledger A — ORGANISATIONS (one row per org, and under R1 there is only ever one thread)
`org · domain · state · first contacted · thread ID · sequence position · status · outcome`

### Ledger B — PEOPLE (one row per ADDRESS)
`address · person · org · first emailed · which emails (1/2/3) · outcome: delivered | bounced | replied | never-emailed`

**The de-dup check at Phase 2 now runs BOTH, in this order:**

1. 🔴 **Ledger A — is this org's domain present?** → **CLOSED under R1.** Stop.
2. 🔴 **Ledger B — is any proposed recipient's address present?** → remove that person from the draft
   and record why. **This is the check that did not exist and that Five County needed.**

**Why both and not just one.** Ledger A alone cannot answer *"has this human already heard from us"*
when they move organisations or sit on two orgs' pages. **Ledger B alone cannot enforce
one-org-one-thread**, because a brand-new person at an already-contacted org passes it cleanly.
**The Five County failure passed the org check by looking bounced and had no person check at all.**

**`outcome` is per address, from the bounce DSN, which names exactly one address.** A send with one
dead recipient and two live ones must never again be recorded as "the org bounced."

⚠️ **The 38 pre-machine organisations and 61 addresses in
`Lists/CCRR-Suppression-Already-Contacted.md` fold into both ledgers** so there is [Org 0934] to check
instead of two, one of which has been frozen since 2026-06-16.

---

## R12 · Reliability batch — APPROVED 2026-08-20, all nine

| # | Rule |
|---|---|
| 1 | **Bounce detection sweeps the whole mailbox every run** — `in:anywhere from:mailer-daemon newer_than:7d`, ONE search. **Never sample only the threads with follow-ups due** — that is what produced a wrong bounce report on 08-18, 08-19 and 08-20 |
| 2 | **`Bounces:` line reports outstanding state, not novelty** — `N new · M suppressed addresses open · R repairs owed before <date>`. **"Breaker clear" means NOTHING OUTSTANDING**, never "nothing new since yesterday" |
| 3 | **`update_draft` must never touch a follow-up draft** — it detaches the reply from its thread. See Phase 3 |
| 4 | **Phase 0 checks [[verification-log]] before calling a draft an orphan.** Report `RECOVERED — evidenced in verification-log, missing from tracker` as a **distinct state** from `RECOVERED — no evidence found`. They are different defects |
| 5 | **The run manifest counts per NIGHT, not per run.** Two runs on 2026-08-19 meant five organisations never reached [[sequence-tracker]] |
| 6 | 🔴 **A CLAIM THAT SOMETHING DOES NOT EXIST MUST NAME EVERY STORE SEARCHED** — or be written *"not found in X"* rather than *"does not exist."* **Three false absence-claims were made on 2026-08-20** (attachments, the Five County provenance, the two bounces). [[method]] already forbids asserting an unverified address; **this extends the same discipline to asserting an absence** |
| 7 | **HubSpot's `hs_lastmodifieddate` on DEAL is not a change signal** — it moves on portal-wide recalculation (25 deals in 16 seconds, 2026-08-20). **Use `createdate` to detect what is new** |
| 8 | **Fix [[method]]'s attachment arithmetic** — it says the GIF is 1.4 MB / ~461k tokens. **`HST_InAction.gif` is 5,559,398 bytes (5.4 MB)** ≈ 1.85M tokens as base64. The 1.4 MB figure belongs to a different file in the same folder |
| 9 | **Reconcile the send-kit folder with the sent filenames** — disk has `HST_InAction.gif` and `HST_Details.pdf` (19.3 MB); the emails carry `HST_WorkshopInAction.gif` and `HST_Flyer.pdf`. A rename recorded 2026-08-12 never reached the folder |

---

## R13 · THE AS-SENT RECONCILIATION — the logs must record what CHRIS SENT, not what the machine drafted

> ✅ **Chris, 2026-08-20:** *"There will continue to be a 'what was drafted' and a 'what Chris actually
> sent' differential… what it seems like is not happening, is that the logs are not being updated with
> what actually happened, only what was drafted. Is my assumption true?"*

### 🔴 HIS ASSUMPTION IS **MOSTLY** TRUE, AND THE PRECISE ANSWER MATTERS

**The as-sent capture EXISTS.** Phase 0 step 2 has recorded as-sent To/Cc since 2026-08-18.
**What is missing is PROPAGATION and PERMANENCE:**

| Store | Records as-drafted? | Records as-sent? | Reality |
|---|---|---|---|
| [[sequence-tracker]] | yes | **yes** | ✅ The one store that works |
| [[contacted]] | yes | **inconsistently** | 🔴 Two runs stale on 2026-08-20; today's 13 sends absent |
| `review-YYYY-MM-DD.md` | **yes** | 🔴 **never** | **Frozen at draft time. Never corrected.** Every card is a permanent record of an intention |
| [[verification-log]] | yes | rarely | Evidence is captured at verification, before any send |
| [[discovery-pipeline]] | counts drafts | 🔴 lagging | Said 85 orgs while 92 had been sent |

**So the honest diagnosis is not "the machine only logs drafts." It is: ONE store gets corrected and
four do not, and the correction happens up to 24 hours late.** Between Chris sending and the next 3am
run, **every file except Gmail is knowingly wrong** — and that window is where every surprise in this
project has come from.

**The evidence is unambiguous.** On 2026-08-19 and 2026-08-20 Chris changed the recipients on at
least six sends — a new To at [Org 1207], WSST, ELC Sarasota and ELC Broward; added Cc at Rural Capital
and ELCFH. **None of those changes is in any review file.** The cards still name the machine's picks.

### 🎯 THE FIX — one pass, all stores, and a visible delta

**Phase 0 step 2 is upgraded from a tracker update to a FAN-OUT RECONCILIATION. For every thread
found in Sent since the last run:**

1. **Read the as-sent To / Cc / Bcc verbatim from Gmail.** Gmail is the authority.
2. **Diff it against what the machine drafted**, from that run's review file.
3. 🆕 **Write the as-sent set to ALL FOUR stores in the same pass** — [[sequence-tracker]],
   [[contacted]] (both ledgers, per R11), [[verification-log]] (marking human-confirmed recipients),
   and [[discovery-pipeline]]'s counts.
4. 🆕 **Append an `AS SENT — CORRECTIONS` block to the ORIGINAL run's review file**, so the card that
   named the wrong person carries its own correction. **Never rewrite the card — append.** The record
   of what the machine got wrong is the learn-pass data.
5. 🆕 **Print the delta in tonight's report:**
   `As-sent delta: N sends reconciled · M recipient changes by Chris · [org: drafted X → sent Y]`

🔴 **`M > 0` is NOT a defect — it is the learn signal.** [[method]] Phase 5 already says *"when Chris
adds a recipient, that is a defect report, not a preference."* **This makes that data reliable
instead of accidental.** Six recipient changes went unanalysed this week because nothing collected
them in [Org 0934].

### The residual gap, stated honestly rather than solved

**Nothing can close the window between Chris sending and the next run** — the machine is not running
when he sends. **What this fix guarantees is that the window is closed COMPLETELY at the next run,
across every store, with the difference printed.** The alternative — a live watcher — is not worth
building for a 24-hour lag on a queue Chris clears in bursts.

---

## R14 · CONTACTED-LIST FRESHNESS — every run reconciles yesterday's sends before anything else

> ✅ **Chris, 2026-08-20:** *"Provide a solution that allows each run to update the 'sent to' list so
> that today/yesterday's emails are found and added to the appropriate list."*

**This is R13's step 3 made unconditional and countable.** The rule:

> 🔴 **NO ORGANISATION IS DRAFTED UNTIL [[contacted]] CONTAINS EVERY SEND FOUND IN GMAIL.**
> Same standing as the suppression freshness gate.

**How the run does it — one search, then a set difference:**

1. `in:sent label:Label_2 newer_than:3d` *(3 days, not 1 — it must survive a weekend and a skipped run)*
2. For each thread: extract org, as-sent To/Cc, date, sequence position, and whether a bounce followed
3. **Compare against Ledger A (orgs) and Ledger B (addresses)** from R11
4. **Append anything missing.** Never rewrite an existing row — append a correction line
5. **Print the count:** `Contacted ledger: N sends found · M newly logged · ledger current as of <timestamp>`

⚠️ **Use `newer_than:3d`, not `1d`.** The run is weekday-only, so a Friday send is not seen until
Monday. A 1-day window would silently drop every Friday and Saturday send. **The 3-day window with an
append-only, de-duplicated write is safe to re-run** — re-processing a send that is already logged is
a no-op, which is exactly the property that makes this reliable.

🔴 **This is what failed on 2026-08-20.** `contacted.md` was two runs stale, and the 13 sends made
that afternoon were invisible to every file. **Under this rule the next run finds them without being
asked.**

---

## R15 · OPEN LEADS — the machine now has standing permission to investigate and close them

> ✅ **Chris, 2026-08-20:** *"I want a solution so that whenever a lead is open like this, the machine
> has the permission to go problem solve, research, and validate with apollo. It should know to look
> through the site for typos, patterns, and then make some hypotheses about why the lead is open.
> Based on that, it should take a structured approach to resolving it so that we can either confirm
> it's not a valid lead to approach and we can move on, or that it's valid and we can put it in the
> outreach queue."*

**This replaces the old conflict-lead handler, which said *"spot it and follow through"* without
saying how — and consequently produced leads that sat open for eight days.**

### What counts as an OPEN LEAD — the trigger list

Any of these, spotted anywhere: a malformed `mailto:` target · a `mailto:` whose target disagrees with
the printed text · a doubled or misspelled domain · two spellings of one address · an orphan address
matching nobody named on the page · a named Tier-1/2 person with no obtainable address · a vendor
record that contradicts the org's own page · an auto-reply naming someone not on the site.

### 🔴 STANDING PERMISSION — no per-lead approval needed

**The machine may spend up to 5 vendor credits and 5 page fetches per lead, inside the existing
nightly budgets, without asking.** Beyond that, it stops and reports. **Cost is not a reason to leave
a lead open** — the nightly budget has closed at or near zero all week.

### The structured investigation — run in order, stop as soon as a terminal state is reached

**Step 1 · State a hypothesis, in writing, before looking.** *"`info@org0317.example` is a typo of
`info@org0318.example` — the `.org` migrated into the local part."* A named hypothesis is what makes
steps 2–5 targeted instead of a wander.

**Step 2 · Test it against the org's own site.** Search every other page for the same handle or
domain. **Count occurrences.** Four consistent instances and one outlier is a typo with high
confidence — the adjudication procedure already in this file.

**Step 3 · Test the org's naming convention.** If every other address is first-initial + surname, an
address breaking the pattern is the suspect one.

**Step 4 · Ask the vendor by NAME.** `people_match` on the person, if there is a name.

**Step 5 · Ask the vendor by DOMAIN.** `apollo_mixed_people_api_search` with
`q_organization_domains_list` — free, and it answers *"who actually works here."* **This is the step
that turned ELCFH from a tier-4 shared inbox into a named Tier-1 director.**

### The three terminal states — every lead must reach one

| State | Meaning | Action |
|---|---|---|
| ✅ **RESOLVED — VALID** | A real, current person with a verified address | Record in [[verification-log]] with full evidence. **If the org is CLOSED under R1, record as known-but-not-contacted — do NOT open a thread.** If the org is unapproached, add to the outreach queue |
| ✅ **RESOLVED — INVALID** | Typo, departed, wrong org, or nobody there | **Suppress the address**, write the reason, **and CLOSE the lead permanently.** It never reappears |
| 🔴 **BLOCKED** | Cannot be settled inside the budget | **State the exact question a human must answer and what would close it** — *"open this PDF and confirm the name"* — not *"needs a human look"* |

🔴 **A lead that ends a run without a terminal state must be reported as `OPEN — N runs`, with its
run count.** *(`dgarvey@` sat 6 runs, `ryanlasal@` 6, `Carl.Salazar@` 2.)* **The count is the
control** — an open lead with a number beside it gets closed; one without a number gets carried
forever, which is exactly what happened.

**Currently open, to be worked under this rule:**
`person0169@org0807.example` (Gulf Coast — doubled domain in a published `mailto:`) ·
`person0302@org0329.example` (orphan `mailto:` behind an empty anchor; **may resolve itself now that
[Org 0554] is retargeted to `org0303.example` under R7**).
✅ **CLOSED 2026-08-20:** `info@org0317.example` — confirmed malformed on the org's own live page,
re-read this run. Neither string is a recipient.

---

## R16 · THE MACHINE DETECTS MEETINGS ITSELF. It never asks Chris for an outcome it can look up.

> ✅ **Chris, 2026-08-20:** *"The machine should not need me to tell it the outcome. It should know to
> look in hubspot and fathom for conversation records."*

🔴 **THIS RETIRES THE STANDING "TELL THE RUN" LINE.** Phase 5's conversion tracking has said since
2026-08-12 that *"meetings, offers, and bookings can only come from Chris or his calendar/CRM."*
**The second half of that sentence was always the answer and the machine never acted on it.**
`meeting held` sat at zero for ten days and **three consecutive reports asked Chris to supply a fact
that was sitting in a connector.**

**Every report now runs the detection below BEFORE printing the conversion ledger. Asking Chris is
the last resort, not the first.**

### The three signals, ranked by how much they prove

| Signal | Proves | Reliability | Status |
|---|---|---|---|
| **1 · Fathom recording** | 🎯 **MEETING HELD** | **Highest available.** A recording cannot exist for a call that did not happen. **And it works retroactively** — every past meeting is already in there | ✅ **WORKING** |
| **2 · Google Calendar event** | **MEETING BOOKED** | Direct and complete — it is how Chris actually books | 🔴 **BLOCKED — connector needs reconnecting** |
| **3 · HubSpot `MEETING` object** | MEETING BOOKED | ⚠️ **Partial.** Only exists when booked *through* HubSpot | ✅ Working, **incomplete** |
| **4 · Gmail reply with scheduling language** | MEETING PROPOSED | Weakest — an intention, not an event | ✅ Working |

### How to run it — every run, before the ledger is printed

**Step 1 · Pull Fathom.** `list_meetings` with `created_after` = last run. **Match `calendar_invitees`
against [[contacted]] Ledger B addresses and Ledger A domains.** Any hit → **`meeting held`**,
recorded with the recording ID and URL as evidence.

⚠️ **`calendar_invitees` is inconsistent — sometimes emails, sometimes display names.** Observed
2026-08-20: one meeting returned `person0457@org0734.example`, another returned
`[Person 0113], [Person 0556]`. **So match on email where present, and on NAME against Ledger B where
not.** Fathom's `find_person` resolves the ambiguous ones. **Never conclude "no meeting" from a
name-only list without checking names too.**

**Step 2 · Pull HubSpot `MEETING` objects** created since the last run, and associate to contacts.
**Corroborating only — see the limitation below.**

**Step 3 · Scan replies for scheduling language** — *"schedule," "availability," "calendar," "Zoom,"*
a proposed date. → **`meeting proposed`**, which is a *distinct stage* from booked and from held.

**Step 4 · Only if all three are silent and a reply clearly implied a call, ask Chris** — naming the
org, the reply and the date, so it is one word to answer.

### 🔴 THE LIMITATION THAT MATTERS, FOUND BY TESTING RATHER THAN ASSUMED

**The Dutchess meeting booked on 2026-08-20 does NOT appear as a HubSpot `MEETING` object.**
Queried directly: zero meeting objects created after 2026-08-18. **Chris booked it by emailing a Zoom
link, not through HubSpot's scheduler — so HubSpot never learned about it.**

> **HubSpot only records meetings it brokered.** For a workflow where the booking happens in a Gmail
> reply, **HubSpot is close to useless as a "booked" signal.** ✅ **Fathom will still catch it on
> 08-25, because the call will be recorded.** **So the machine may be blind to a booking for five days
> and then certain about it the moment it happens.** That asymmetry is acceptable — *held* is the
> stage that matters — but it must not be mistaken for "no meeting exists."

🔴 **THEREFORE: the absence of a HubSpot meeting object is NOT evidence that no meeting is booked.**
Per R12.6, any report saying so must name which stores were searched.

### 🔴 ONE THING CHRIS MUST DO — reconnect Google Calendar

**`list_events` returns *"This connector requires additional permissions."*** Calendar is **the**
direct answer to *"is a meeting booked"* and it is the only one of the four signals that is both
complete and forward-looking. **Until it is reconnected, `meeting booked` rests on HubSpot (partial)
and reply-scanning (weak), while `meeting held` is fully covered by Fathom.**

### The ledger stages, now that they can be distinguished

| Stage | Detected by | Meaning |
|---|---|---|
| `meeting proposed` | Gmail reply | They said yes in principle |
| `meeting booked` | Calendar *(blocked)* · HubSpot *(partial)* | A specific time exists |
| 🎯 `meeting held` | **Fathom recording** | **It happened.** The stage the 667 arithmetic depends on |
| `offer made` · `days booked` | 🔴 **Still human-supplied** | No connector observes these. **These are the only outcomes worth asking Chris about** |

**Report line, every run:**
`Meetings: N proposed · N booked · N held (Fathom-verified) · sources checked: Fathom ✅ HubSpot ✅ Calendar 🔴`

---

## R17 · AUTO-REPLIES — classify first, delay second. Ruled by Chris 2026-08-21.

> ✅ **Chris, 2026-08-21:** *"If I get an auto-reply from someone on any of the emails I send, I want that thread to wait until the day they say they'll be back before you queue up the next followup… If we have a thread of multiple people and one or more of them have an OOO responder on, we will followup on the soonest date of return from any of the people on the list."*
>
> ✅ **And on stale notices:** *"some people don't turn their OOO notice off when they return… If that happens, I want to just ignore it, assume that person just forgot to turn their autoresponder off, and move forward as if we never received it."*

### 🔴 STEP 1 IS CLASSIFICATION, NOT DELAY. Four things arrive looking identical.

**Built from the 12 real auto-replies in the mailbox on 2026-08-21, not from imagination. Only 7 of the 12 are absences.**

| Class | Tell | Action |
|---|---|---|
| **A · TEMPORARY ABSENCE** | Names a return date, or a date range, or says "out of the office" with an end | Feed to the date rule below |
| **B · PERMANENT DEPARTURE** | *"no longer with"* · *"inactive mailbox"* · *"no longer monitored"* · *"has left the organization"* | 🔴 **AUTO-SUPPRESS + REPAIR THE THREAD.** See §R17.4 |
| **C · STANDING DEPARTMENTAL AUTORESPONDER** | Fires at every inbound message. No person, no absence, no date — a portal notice, a ticket number, an SLA statement | **IGNORE ENTIRELY.** Not an absence, not a departure, not a reply |
| **D · INDEFINITE ABSENCE** | An absence with **no return date at all** — medical, leave, *"limited access"* | **7-day delay, then proceed.** See §R17.3 |

**Why this is step 1: 3 of 12 — 25% — were class B.** `person0322@org0314.example` · `person1074@org0077.example` · `person1169@org0572.example`. **A delay rule applied to a dead mailbox parks it forever.**

### 🔴 R17.1 · AN AUTO-REPLY IS NEVER A REPLY. This carve-out is load-bearing.

**`stop_on_reply: true` is absolute and an auto-reply must NOT trigger it.** Stopping a sequence permanently is far worse than a mistimed follow-up, and it is silent.

🔴 **AND THE INVERSE BINDS EQUALLY.** A **human** reply that happens to mention an absence — *"I'm out next week, ping me after"* — **is a REPLY. It stops the sequence.** It is not an OOO and must never be silently deferred.

**The discriminator is the message, not the words.** Prefer, in order: the `Auto-Submitted: auto-replied` header · `X-Autoreply` / `X-Autorespond` · `Precedence: auto_reply` · **then** a subject beginning `Automatic reply:` / `Out of Office:` / `Autoreply:`. **All 12 observed on 2026-08-21 carried the `Automatic reply:` subject prefix**, so the cheap test works on this dataset — but headers are the authority where the connector exposes them (`get_message` with `RAW`).

### R17.2 · THE DATE RULE — soonest return of anyone on the thread

> ✅ **Chris chose the soonest-of-anyone form deliberately, over a To-weighted alternative, on 2026-08-21.**

1. **A recipient who did NOT auto-reply has an implicit return date of TODAY.** They are present.
2. **The follow-up is due on the SOONEST return date across every recipient on the thread.**
3. 🔴 **Therefore the delay fires ONLY when EVERY recipient is out.** One live human on the thread means the follow-up goes on schedule. **This is intended:** the point of three recipients is that someone is there to read it.

**Worked example, 2026-08-21 — both live cases, and neither delays:**

| Thread | Out | Present | Soonest | Result |
|---|---|---|---|---|
| ELCHC | `sfrancois@` (**the To**) until Aug 25 | `rsalgado@` · `aperez@` | today | ✅ **Send on schedule** |
| [Org 0562] | `castle@` until Aug 24 | `tschadle@` · `lbutler@` | today | ✅ **Send on schedule** |

⚠️ **Stated honestly so it is not mistaken for an oversight: at ELCHC this sends while the decision-maker is away.** Chris weighed that and chose reach over timing. **Revisit only if follow-ups start landing in backlogs unanswered.**

#### 🔴 Parsing — every trap below is from a real message in this mailbox

| Rule | Why |
|---|---|
| **Anchor every date to the AUTO-REPLY'S OWN received timestamp, never to today** | *"out of the office until Monday, the 17th"* (`jvirkus@`, no month, no year) · *"out of the office 8/10 - 8/16"* (`ccole@`, range, no year) · *"until 8/17"* (`rossmanl@`). **Parsed against today, "the 17th" reads as next month** |
| **Use the MOST RECENT auto-reply per address, never the first** | `person1111@org0325.example` fired twice on one thread: Aug 14 said *"until August 17th"*, Aug 21 said *"until August 25th"*. **The stale one is still sitting in that thread** |
| **Prefer an explicit *"returning on"* over an inferred one** | `castle@` gave both: *"out… August 19 through August 21, returning on Monday, August 24."* Take the stated return, not `end + 1` |
| **"until X" = back ON X · "through X" = back on X+1** | A one-day convention. Cheap to get wrong, cheap to be wrong about |
| 🔴 **QUOTE THE RETURN LINE VERBATIM on the card, with the message ID** | Same discipline as an address. **An inferred date is not a date.** If it cannot be parsed with confidence, treat it as class D and say so |
| **Ignore any auto-reply older than 30 days** | Beyond that the notice says nothing about now |

#### 🔴 THE STALE-NOTICE RULE — Chris's own words

**If the stated return date is in the PAST, IGNORE THE AUTO-REPLY ENTIRELY and proceed as if it never arrived.** Assume the person forgot to switch it off. **A return date of TODAY counts as present.**

**On the 2026-08-21 data this fires 5 times of 7** — `lhicks@` (Aug 17) · `hpandya@` (Aug 18) · `jvirkus@` (Aug 17) · `ccole@` (Aug 16) · `rossmanl@` (Aug 17). **The rule earns its place immediately.**

### R17.3 · NO RETURN DATE, OR A DATE BEYOND THE CEILING

> ✅ **Chris, 2026-08-21:** *"If no return date, proceed with 7 day delay. If there is any indication that the recipient may not work at the organization anymore, please flag for me."*

- **No date given → delay 7 days (one sequence gap), then proceed.** Self-correcting: the next run re-reads the thread anyway.
- **Ceiling: 14 days.** A stated return further out than that is treated as no-date — **delay 7 days and proceed.** *"Back in March"* must never park a thread for months.
- 🔴 **BUT FIRST, THE DEPARTURE SNIFF TEST — and this is Chris's addition, not a default.** **If ANYTHING in the auto-reply hints the person may no longer work there — and it is not unambiguous enough for class B — do NOT delay and do NOT suppress. FLAG IT FOR CHRIS**, quoting the line, and hold that recipient pending his call.

  **Ambiguous phrasings that trigger the flag:** *"I am no longer in this role"* · *"this position is currently vacant"* · *"I have transitioned"* · *"please direct future correspondence to…"* with no return date · an auto-reply from a **different domain** than the one emailed · a signature block naming a different employer.

  **The distinction that matters:** class B is *unambiguous* (*"no longer with"*, *"inactive mailbox"*) and acts automatically. **Anything short of unambiguous is a question for Chris, never a guess.** *A wrong suppression is invisible and permanent; a flag costs one line in the report.*

**Class D, live example:** `person0653@org0309.example` — *"currently out of the office due to an unexpected medical situation and will have limited access to email while I recover."* **No date, no departure hint → 7-day delay.** *(Moot on that thread — two recipients are present — but it is the canonical class-D shape.)*

### 🔴 R17.4 · CLASS B — PERMANENT DEPARTURE. Suppress and repair, exactly like a bounce.

> ✅ **Chris, 2026-08-21:** auto-suppress and repair the thread.

**Run the R2 handler, unchanged:**

1. **Suppress the address** in [[verification-log]] and **Ledger B**, outcome `departed`
2. **Drop it from every future email on that thread**
3. **Rewrite the greeting** to the surviving names
4. **Insert the approved bounce parenthetical** from [[Cold-Outreach-Sequence-CCR&R]] — 🔴 **Chris's own wording, never improvised**, and **the pronoun rule still binds: write `them` unless the person states one**
5. **Print `Redundancy: N of 3`**
6. 🔴 **EXCLUDED FROM THE BOUNCE RATE.** An auto-reply is not a DSN. `person1074@org0077.example` is already recorded this way and that precedent governs

**Never let a name vanish silently between emails** — the remaining recipients read it as concealment. That is the whole reason the parenthetical exists.

### R17.5 · COVERING CONTACTS — harvest them, never add them

**7 of the 12 auto-replies name a substitute with a live address.** They are org-published, self-identified and current — **the best Gate-1-equivalent evidence the machine ever gets for free.**

- ✅ **Record every one in [[verification-log]] as known-but-not-contacted**, with the quoting message ID
- 🔴 **NEVER add them to a live thread. R5 governs and it is unchanged** — *"it would look like we are intentionally going around the non-responders."* Chris ruled exactly this on [Org 0102]/[Person 0609]. **An autoresponder is not the organisation introducing someone; a human reply is**
- ✅ **They ARE usable at Email 1 for an organisation not yet contacted** — subject to R1

### R17.6 · Everything else the rule touches

| Interaction | Ruling |
|---|---|
| **Queue slots** | **An OOO hold costs nothing.** Follow-ups are uncapped and separate from the new-org target. A deferred follow-up never suppresses a new organisation |
| **Sequence cascade** | `next_due` already runs from the **actual send date**, so a delay shifts the rest of the sequence naturally. **Do not also shift the original schedule** |
| **Delivery evidence** | 🎯 **An auto-reply PROVES delivery.** On a catch-all domain, where silence proves nothing, it is the only positive delivery signal available. Record it |
| **Detection** | 🔴 **ONE MAILBOX-WIDE SWEEP PER RUN, never a per-thread sample** — the R12.1 lesson. `in:anywhere newer_than:60d subject:("automatic reply" OR "out of office" OR "autoreply" OR "auto-reply" OR "away from")` |
| **Domain drift** | An auto-reply arriving **from a different domain than the one emailed** is an R15 open lead. *Origin: `person0177@org0341.example` was emailed; the reply came from `person0178@org0664.example`* |

### 🔴 R17.7 · THE REPORT LINE — mandatory, and it is the control

> `Auto-replies: N swept · A absences (H held, R released) · B departures suppressed · C standing autoresponders ignored · D no-date (7d delay) · S stale-ignored · F flagged for Chris`

🔴 **A follow-up that silently fails to appear reads as a SHORTFALL under Phase 1's own rule.** Without this line, an OOO hold is indistinguishable from the machine failing to draft.

**And the reason it is a count, not a rule:** every rule in this file that fires reliably is attached to a countable object. *"Watch for auto-replies"* is a judgement with no object, and this file documents five of those failing to fire.

### R17.8 · THE GENERAL FORM — the machine's default for the NEXT automated-signal class

🔴 **This section is the MACHINE'S default, not a rule Chris stated.** Chris ruled on auto-replies
and bounded his own instruction to this machine: *"I want to add a feature/rule to the outreach
draft machine."* He then asked *"what other considerations should we take"* — and R17.1–R17.7 are
the answer to that question. R17.8 generalises the answer so the next signal class costs one
reading instead of one design session. **Do not cite R17.8 to Chris as something he decided.**

**When it applies.** Any automated, non-human message arriving on a live sequence thread — a
delivery deferral, a ticketing robot, a shared-mailbox autoresponder, a calendar bot, a
policy-notice bounce that is not a DSN. Three rules, in order.

| # | Rule | Why, and what it cost when it was absent |
|---|---|---|
| **1** | 🔴 **CLASSIFY BEFORE YOU ACT. An automated message is not one thing.** Sort it first — *temporary, with a stated end* · *permanent* · *standing/structural* · *indefinite, no end stated* — and only then choose an action. **Never let a single action be the whole rule.** | On 2026-08-21, **7 of 12** auto-replies were temporary absences. The other 5 were 3 permanent departures, 1 standing departmental autoresponder and 1 indefinite medical absence. A delay-only rule would have been the wrong action **5 times in 12** — and on the 3 departures it would have parked a dead mailbox forever, silently |
| **2** | 🔴 **A SIGNAL WHOSE OWN VALIDITY WINDOW HAS CLOSED IS NOT A SIGNAL.** If the message asserts a condition that has already expired — a return date in the past, a coverage window that ended, a deferral until a time now gone — treat it as **never received**. Today counts as present, not past | Chris, verbatim: *"assume that person just forgot to turn their autoresponder off, and move forward as if we never received it."* On the 08-21 data this fires **5 times of 7** in class A. Without it, the commonest single input to the rule is a false one |
| **3** | 🔴 **ON A MULTI-PARTY THREAD THE BINDING CONSTRAINT IS THE SOONEST RELEASE, NOT THE LATEST.** A party who sent no signal is **unconstrained** — treat their release as today. So a hold fires **only when every party is constrained** | Chris, verbatim: *"we will followup on the soonest date of return from any of the people on the list."* ⚠️ **He chose reach over timing knowingly.** At ELCHC on 08-21 that means sending while the person in the To line is away. That is the accepted cost, not an oversight — revisit only if follow-ups start landing unanswered in backlogs |

**The gate on generalising at all — run it before you reuse this.** These three hold for signals
that are *about the recipient's availability*. They do **not** transfer to a signal about the
**message** (a hard bounce, a rejection, a spam verdict) — those are R2/R15 objects and R17 has no
jurisdiction. If you cannot tell which kind you have, that is a class-1 failure, not a class-2 one:
**classify, then act.**

**And the standing carve-out survives generalisation:** an automated message is never a reply
(R17.1). Killing a sequence on a robot's say-so is permanent and silent; a mistimed follow-up is
neither.

---

# 📋 CHANGE RECORD — 2026-08-24 · §0 RUNTIME PROGRAM INSTALLED

**Authority:** Chris, 2026-08-24: *"tighten this up and implement your solutions. I specifically like
your exchange of prose for clear rules and serial process."*
**Design:** [[PROPOSAL-2026-08-24-preflight-and-precedence]] · **Diagnosis:**
[[CAPA-2026-08-24-generic-inbox-descent]] · [[CAPA-2026-08-24-probe-orphan-and-recipient-cap]]

## 🔴 DIFF OF DELETED OBLIGATIONS — P7 compliance

> **REQUIRED BY P7 of any pass that shortens, restructures or de-duplicates a program file.**

**DELETED OBLIGATIONS: ZERO. This pass was purely ADDITIVE.**

**Proof, not assertion — P7 rule 0 requires a grep, never a claim:**

| Check | Result |
|---|---|
| Lines removed from the archive | **0** — §0 was inserted before existing content; nothing after it was cut |
| File size | **203 KB → 215 KB.** It grew. A compression pass would shrink it; this did not compress |
| Text rewritten in place | **2 passages only**, both the D5 correction — `named on page` `+` now counts toward `B`, never `M`. **Nothing was removed; a wrong statement was corrected and the correction explains itself** |
| Write-obligations (`write`/`refresh`/`update`/`record`/`verify`) still present in the archive | **All. None was touched** |

⚠️ **This is deliberately NOT the method split proposed in §6 of the proposal.** That split MOVES
content and therefore carries real P7 risk. **This pass front-loads the executable program and leaves
the archive entirely intact — the benefit of the split with none of its deletion surface.**
**The full split remains open, to run on a non-batch day, with the four P7 controls.**

## What was added

| § | Content | Status |
|---|---|---|
| **§0.1** | Rule precedence — 5 levels, safety first | 🆕 new |
| **§0.2** | D-SWEEP and D-TABLE doctrines | 🆕 new |
| **§0.3** | The run as 22 serial steps | ⚪ **restatement** of Phases 0–7 in execution order |
| **§0.4** | Pre-flight — 17 boolean assertions | **12 relocated · 5 new** (U2, U9, U10, E1.5, B1) |
| **§0.5** | Pass condition + `preflight_holds = 0` | ⚪ extended |
| **§0.6** | Mandatory report lines, consolidated | ⚪ **restatement** |
| **§0.7** | New-cluster vocabulary review | 🆕 new |
| Failure modes | 8 new rows, each pointing at its §0 assertion | 🆕 new |
| D5 | Resolved — Phase 7 wins | ✅ closed |

## The five NEW assertions and what each is made of

| ID | Assertion | Origin | n |
|---|---|---|---|
| **U2** | greeting name set == recipient name set | [Org 0546] 4-vs-3 (08-24) + *"Hi [Person 0478] and Jesse"* (08-18) | 2 |
| **U9** | binding instructions read for this org | [Org 0564], 08-24 morning | 1 |
| **U10** | this org's thread checked in Sent this session | duplicate draft, 08-24 afternoon | 1 |
| **E1.5** | tiering yield — 0 tiered while ≥1 named must name the top-ranked person and why not | WS Capital Area 55→0 · WS Alamo 29→0 | 2 |
| **B1** | redundancy reported (never scored) | Texas batch, 4 of 10 at `1 of 3`, reported clean | 1 |

⚠️ **Three of the five rest on a single day's evidence.** Recorded here so a future run can retire one
that never fires rather than assuming all five earned their place.

## 🔴 The failure mode this change is betting against

**A checklist becomes a ritual.** If a run prints `Pre-flight: 17/17 ✅` without evaluating each
assertion, we have swapped an unread rule set for an unread checklist and gained nothing.

**The control: §0.4 requires each assertion to report THE OBJECT IT CHECKED, not its verdict.**
`U1: 1 To + 2 Cc ✅` — never `U1 ✅`. **A verdict can be fabricated from nothing; an object cannot.**
**Effectiveness check: the next three runs. If any prints bare verdicts, this control has failed and
the CAPA reopens.**
