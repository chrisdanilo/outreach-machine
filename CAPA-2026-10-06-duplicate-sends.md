---
business: Human Skills Training
type: capa
title: "CAPA 2026-10-06 — Two fires of the follow-up sender ran at once; 8 orgs received Email 2 twice, 7 minutes apart"
status: implemented (L1) 2026-10-06 — containment done (⚠ on 8 threads); verification of effectiveness runs over the next 7 business days (§7)
owner: Chris Danilo
raised_by: Chris ("what went wrong that made the duplicate sends? … duplicate sends are never allowed")
severity: 🔴 external — 8 cold prospects saw the same follow-up twice
related: ["[[method]] §0.16", "[[config]] followup_sender", "[[CAPA-2026-09-30-two-drafts-one-thread]]", "[[ARCHITECTURE-v2]]"]
fires: ["runs/2026-10-06/sender/0929ET", "runs/2026-10-06/sender/0935ET"]
---

# CAPA — the ledger was read once and trusted for 16 minutes

## 0 · In one paragraph

The sender's only duplicate guard is "the Gmail thread is the ledger": count Chris's own messages on the thread at GATHER time, send if the count says the next email is due. That guard holds only if nothing else writes to the thread between GATHER and ACT. On 2026-10-06 two sessions ran the same launcher six minutes apart (one started at 09:29 ET, four minutes before the scheduled 09:30 slot; the scheduled one at 09:34 ET). Both gathered at 13:36Z from the same pre-send state, both planned 8 sends, and both sent — fire 0929ET at 13:41–13:43Z, fire 0935ET at 13:48–13:52Z. Nothing in the program, the launcher, or the scheduler prevents two fires from overlapping, and nothing re-reads a thread in the seconds before it is written to. `--verify` caught the extra message afterwards (8 UNVERIFIED) — the check exists, it just runs on the wrong side of the send.

## 1 · What happened (UTC; every ID read back from Gmail)

| Time | Fire | Event | Evidence |
|---|---|---|---|
| 13:27:51 | — | The scheduled task record `trig_01LCLrvqGpqWjdSL7xjiEKVc` is modified (`updated_at`) | `list_triggers` |
| 13:29:31 | 0929ET | Session A runs `--queries` — **4 min before the 09:30 slot** (the slot's server anchor is :33:57) | `0929ET/queries.json generated` |
| 13:34:05 | 0935ET | Session B starts, fired by the schedule (09:30 ET slot) | fire notice in session B |
| 13:34–13:35 | 0935ET | B finds no connected folder (`connectedFolders: []`), requests `/Users/chrisdanilo/ClaudeVault`, granted (auto mode) | `get_device_info`, `device_request_folder_access` |
| 13:35:41 | 0935ET | B runs `--queries` | `0935ET/queries.json` |
| 13:36:18 / 13:36:34 | both | A and B each save `search_1.json` — **same state: 1 own message on each of the 8 threads** | raw file mtimes; `own_count: 1` in both plans |
| 13:40:54 | 0929ET | A `plan.json`: 8 send | `0929ET/plan.json` |
| 13:41:38 → 13:43:24 | 0929ET | A sends Email 2 to the 8 threads via Zapier | message ids `1a11172c…` … `1a111746…`, label `Label_10` |
| 13:44:41 | 0929ET | A `--verify` OK → `followup_sends.json` (sent 8), label flips Label_9→Label_10 printed and applied | `0929ET/followup_sends.json label_calls` |
| 13:45:11 → 13:47:18 | 0935ET | B performs its 8 `get_message` NEEDS reads and writes `plan.json`: 8 send, **own_count 1 — computed from the 13:36 snapshot, 11 minutes stale** | `0935ET/plan.json generated 13:47:18` |
| 13:48:54 → 13:52:08 | 0935ET | B sends Email 2 to the same 8 threads | message ids `1a111797…` … `1a1117c6…` |
| 13:54:12 | 0935ET | B `--verify`: own messages on each thread = 3, expected 2 → **8 UNVERIFIED**, no label calls printed, none applied | `0935ET/followup_sends.json` |
| 14:35:42 → 14:43:33 | 1035ET | The 10:30 slot runs normally: 78 skip, nothing due in window | `1035ET/followup_sends.json` |
| 15:35:13 → 15:46:26 | 1135ET | The 11:30 slot runs normally: Email 2 to [Org 1160] (NV, PT) sent `<thread-id>` at 15:45:16Z and verified; Trinity and [Org 0175] held (team-form greeting). **CORRECTION 18:50Z:** the first draft of this CAPA said these slots "produced no run folder"; they did — their folders were invisible to this session's mount for over an hour (see C-h). The task's `last_run` "6 s" records the wake delivery, not the session | `runs/2026-10-06/sender/1035ET`, `1135ET` |

**Blast radius (verified against `in:sent newer_than:1d` at 15:55Z):** exactly 8 threads, each with two identical Email 2 messages 7–8 minutes apart; 16 messages, 8 of them duplicates. Nothing else sent by the machine today. Chris's own Email 1 to Montana (15:41Z) is unrelated.

| Org | Thread | 0929ET send | 0935ET send (duplicate) |
|---|---|---|---|
| Oklahoma Partnership for School Readiness (OPSR) | <thread-id> | <thread-id> · 13:41:38 | <thread-id> · 13:48:54 |
| [Org 0679] | <thread-id> | <thread-id> · 13:41:57 | <thread-id> · 13:49:25 |
| [Org 0999] | <thread-id> | <thread-id> · 13:42:11 | <thread-id> · 13:49:54 |
| Southeastern Oklahoma State University CCR&R | <thread-id> | <thread-id> · 13:42:24 | <thread-id> · 13:50:17 |
| [Org 0505] | <thread-id> | <thread-id> · 13:42:44 | <thread-id> · 13:51:00 |
| [Org 0414] | <thread-id> | <thread-id> · 13:42:58 | <thread-id> · 13:51:22 |
| [Org 0603] | <thread-id> | <thread-id> · 13:43:12 | <thread-id> · 13:51:44 |
| [Org 0600] | <thread-id> | <thread-id> · 13:43:24 | <thread-id> · 13:52:08 |

Thread state now: **3 own messages** on each thread (Email 1, Email 2, Email 2 again). Rule 3 reads 3 = `sequence_length`, marks these "stage complete", and **the machine will never send Email 3** to these 8 unless Chris rules otherwise. Stage label is `Label_10` (Email 2 sent), set by 0929ET. Correct as a label; the count is what is off.

## 2 · Root cause

**RC-1 (design) — the idempotency guard is a snapshot, not a check at the moment of writing.** `--plan` computes `own_count` from `raw/search_*.json`, gathered at the start of the fire. ACT happens 12–16 minutes later (today: A 13:36→13:41, B 13:36→13:48) with no re-read of the thread. §0.16 says the sender "never sends twice in one fire"; nothing says, or enforces, "never while another fire is in flight." The ledger rule is correct; it was applied to a stale copy of the ledger.

**RC-2 (operations) — two sessions ran the same launcher at once, and nothing stopped the second.** Session A started 13:29Z, 4–5 minutes before the slot, immediately after the task record was edited at 13:27:51Z. That pattern is consistent with a manual "run now" or an edit-and-run on the task; the task's run history in the Claude app will show which (not visible from inside a session). Session B was the regular 09:30 slot. The program has no fire lock, and the launcher's "NEVER run the fire twice" is addressed to a session that cannot see another session.

## 3 · Contributing causes

| # | Cause | Class |
|---|---|---|
| C-a | GATHER→ACT latency is long: Gmail reads, 8 `get_message` NEEDS reads, verbatim heredoc transcription of every result. 12–16 min per fire. The race window is this latency | design / launcher |
| C-b | Both sessions started with **no connected folder** (`connectedFolders: []`) despite the task's folder binding; B recovered via a folder-access request (auto-granted). The 7-minute lag between A's start (13:29) and A's gather (13:36) suggests A hit the same thing. The delay is what made the two fires interleave instead of one finishing before the other began | platform |
| C-c | The sender is designed to fire 4×/day (8:30/9:30/10:30/11:30 ET) so each time zone gets its 08:30–10:00 window. Four fires a day plus any manual run means overlap needs only one slow fire | design |
| C-d | The freshness check exists only post hoc: `--verify` computes `len(own) == own_count + 1` from a fresh `get_thread` **after** sending. Run before the send it would have blocked all 8 | design |
| C-e | Stage labels (`Label_10` = Email 2 sent) are not consulted by `--plan` as a guard; only `own_count` is. Would not have saved today (A's flips landed after B's snapshot) but is a free second signal once a fresh read exists | design |
| C-f | ~~The 10:30 and 11:30 slots produced no run folder~~ **Withdrawn 18:50Z** — both ran (see timeline); `fires 4/4`. Kept so the correction is on record | — |
| C-h | 🆕 **The Cowork mount caches directory listings per session.** This session listed `runs/2026-10-06/sender/` at 13:35Z and 13:54Z; the 1035ET folder (created 14:35Z by another session) and 1135ET (15:35Z) did not appear in this session's `ls` until this session itself wrote into that directory at 18:43Z. A lock that relies on `ls`/glob alone could miss a sibling created after the listing was cached. **Mitigation built in:** the sibling scan probes every plausible fire folder by exact name (`HHMMET` for the last `fire_lock_minutes` + 5) with `stat()`, which is a fresh lookup; `--queries` scans again *after* writing its own folder (the write invalidates the cached listing) | platform |
| C-g | `config.followup_sender.model` says `sonnet`; the task record says `claude-fable-5-1`. Drift, not a cause; recorded for the config audit | config |

## 4 · What is now KNOWN (do not re-test)

- Two fires sharing one vault **see each other's run folders**: `runs/<date>/sender/<fire>/` is a shared, ordered record. A lock or claim written there is visible to the other session within the same second.
- `get_thread METADATA_ONLY` returns `labelIds`, `sender`, `date`, `messageCount` per message in one call — enough to recompute `own_count`, newest message, stage label and `hidden` without a body read.
- Zapier `reply_to_message` returns `{id, threadId, labelIds:["SENT"]}` synchronously; the sent message is visible to `get_thread` within seconds (B's 13:54 verify saw messages sent at 13:52).
- Folder access requested from inside an auto-mode scheduled run is granted without a human (13:35Z today).

## 5 · Containment — the 8 threads (Chris rules; this represents him externally)

| Option | What | For | Against |
|---|---|---|---|
| A | Do nothing on the threads. Messages are identical; recipients see one repeated follow-up 7 min apart | No third email on a cold thread | Reads as automation; no acknowledgement |
| B | One short human note on each thread from Chris ("sent twice — my mistake, apologies") | Owns it; human | A third message within the hour on a cold thread; costs Chris 8 sends |
| C | Label the 8 threads ⚠ now so the nightly surfaces them for Chris, and decide Email 3 by hand per thread | Prevents compounding; keeps the machine off these threads | Manual Email 3 for 8 orgs |

**✅ Chris ruled option C (2026-10-06 ~17:25Z): "Label ⚠ now, you decide Email 3 by hand." `Label_14` (⚠) applied to all 8 threads at 17:28Z via `label_thread`; read back on `<thread-id>` — every message now carries `Label_14`. The nightly surfaces them; the sender never sends a ⚠ thread.**

Independent of the option: the program now reads 3 own messages on each → it will never send Email 3 here. If Email 3 is still wanted, it is Chris's send (or a one-off `own_count` override that does not exist yet and should not be built for 8 threads).

## 6 · Corrective / preventive actions — **IMPLEMENTED 2026-10-06 (L1, Chris's ruling 17:5xZ: "L1 only")** — see §10 for the evidence

| # | Control | Closes | Cost |
|---|---|---|---|
| **P1 — fire lock at `--queries`** | `--queries` scans `runs/<today>/sender/*/`: any sibling fire with `queries.json` younger than 60 min and **no** `followup_sends.json` ⇒ print `FAIL CLOSED: fire <id> in flight since HH:MM` and exit 1; the launcher's existing ABORT rule stops the session. A fire older than 60 min with no verify is treated as crashed and noted. No new file type; the run folder is the lock. **Today: B's 13:35 `--queries` would have failed closed on A's 13:29 `queries.json`** | RC-2, C-c, any manual "run now" | ~25 lines |
| **P2 — `--arm`: a fresh read in the seconds before each send** | New step between PLAN and ACT. Pass 1 prints `get_thread METADATA_ONLY` for every `send` row → `raw/arm_thread_<id>.json`. Pass 2 recomputes from the fresh read: own_count unchanged · no own message dated today (recipient-local) · stage label for this email absent · `hidden` unchanged · no live draft · thread not in any sibling fire's `plan.json` send rows without a `followup_sends.json` (the **claim** check) · arm file mtime < 180 s old. Only rows that pass print `armed` with their params; `--plan` no longer prints params. **Today: B's arm read at ~13:48 would have shown own_count 2 and `Label_10` → 0 armed** | RC-1, C-a, C-d, C-e | ~80 lines + launcher step |
| **P3 — rule 2b, "sent today"** | In `--plan` and `--arm`: any own message on the thread dated today in the org's zone ⇒ `skip — already sent today`. Cheap, independent of count arithmetic | defence in depth | ~8 lines |
| **P4 — duplicate audit in `--report-yesterday`** | Any thread with ≥2 own messages on the same calendar day ⇒ 🔴 `DUPLICATE SEND` on the nightly's `Sender:` line, with thread ids. Detection with a name, so it is counted, not noticed | closes the loop | ~15 lines |
| **P5 — launcher text** | Step 2b ARM added; step 0: if `connectedFolders` is empty, request `/Users/chrisdanilo/ClaudeVault` once (auto-granted), then proceed — never gather from a stale mount; "run the fire twice" clarified: *a FAIL CLOSED from `--queries` means another fire is in flight — stop, report, send nothing*. Applied with `update_trigger` (prompt change; may need device-side approval) | RC-2 | prompt edit |
| **P6 — operating rule** | No manual "run now" of the sender within 15 minutes of a slot, and never without checking `runs/<today>/sender/` first. P1 enforces it; this is the human half | RC-2 | rule |
| **P7 — selftests** | Add to `--selftest`: (a) sibling fire in flight → `--queries` fails closed; (b) arm read shows own_count+1 → row drops; (c) arm read shows today-dated own message → row drops; (d) stale arm file → row drops; (e) claimed by sibling plan → row drops | regression | tests |

Not proposed: a separate ledger or queue file (would contradict the one design rule), reducing to one fire a day (breaks the per-zone window), or retrying `UNVERIFIED` rows (a retry is exactly how a duplicate compounds).

## 7 · Verification of effectiveness (how we know it worked)

1. `--selftest` passes with the five new cases.
2. Dry run: start fire X (`--queries` only), then start fire Y → Y's `--queries` prints FAIL CLOSED. Delete X's folder → Y proceeds.
3. Dry run on a test thread (Chris→Chris, as BQ-030 used `<thread-id>`): plan → arm → send → immediately run a second fire's plan+arm on the same thread → 0 armed, reason `own_count changed` / `sent today`.
4. Seven business days of `Sender:` lines with `fires 4/4` and no `DUPLICATE SEND`.

## 8 · Open for Chris

- Containment option A / B / C for the 8 threads (§5), and whether Email 3 is still wanted for them.
- Approve P1–P7 as a set, or program-side only (P1–P4, P7) with the launcher (P5) left as is.
- What started session A at 13:29Z — check the task's run history for a manual run at ~09:28 ET.


---

## 9 · DETERMINISM REVIEW (Chris, 2026-10-06: "before I approve anything, think about how this could be more deterministic — less vulnerable to chance or risk from the LLM")

### 9.1 · Where chance enters the sender today — every point where an LLM, not code, decides or copies

| # | Step | What the LLM does | Failure if it slips | Guard today | Fail direction |
|---|---|---|---|---|---|
| 1 | Session start | Decides what to do when the vault mount is absent (today: one session requested access and continued; the 11:30 fire ended in 6 s) | Fire silently skipped, or fires desynchronise and overlap | none | open (overlap) / safe (skip) |
| 2 | GATHER | Retypes every inline Gmail result into a file by hand (today: ~130 KB per fire). Must follow `nextPageToken` to the end | A mistyped id, date or address changes the plan; a dropped page drops threads | JSON parses; recipients must exist in Ledger B | mostly safe — except a wrong `date` or `sender` can turn "sent" into "not sent" |
| 3 | GATHER→ACT gap | Sets the pace. 12–16 min today | Ledger read goes stale; another writer is invisible | none | **open — today's failure** |
| 4 | Concurrency | Cannot see another session | Two fires act on one snapshot | none | **open — today's failure** |
| 5 | ACT | Retypes ~3 KB of params per send (recipients, subject, HTML body, signature HTML) into the Zapier call | A one-character slip sends the wrong body/recipient; invisible until a human reads the thread | none pre-send; `--verify` checks only the message **count** | open (wrong content, right count) |
| 6 | ACT compliance | Must send only `send` rows, resolve two placeholders exactly, call one action | Extra or malformed send | launcher wording | open |
| 7 | VERIFY/LABEL | Runs printed reads, applies printed label flips | Wrong label (cosmetic — `--plan` ignores stage labels) | printed calls | safe |

Points 3 and 4 caused today's duplicates. Points 2, 5 and 6 have not failed yet; nothing would have told us if they had.

### 9.2 · The design principle that removes the chance

**Code decides, code checks, code fails closed; the LLM only moves bytes — and anything the LLM moved is distrusted until code re-derives it from a fresh, structurally validated read.** Concretely: no step may act on data older than the step itself; no two fires may hold the vault at once; nothing the program did not print can be sent, and nothing it cannot verify afterwards counts as sent.

### 9.3 · Three levels — what each removes, what each costs

| Level | Architecture | Removes chance points | Keeps | Infra / setup | Verified feasible? |
|---|---|---|---|---|---|
| **L1 — fail-closed guards in the program** (P1–P7 + the integrity checks below) | Same GATHER/COMPUTE/ACT; the script adds a **lock** (run folder = lock), **claims** (another in-flight fire's plan rows are off limits), an **`--arm` fresh read** seconds before each send with a 180 s TTL, a **sent-today** rule, **structural validation** of every raw file (ids `^[0-9a-f]{16}$`, `threadId` = filename, `messageCount` ≥ listed, dates parse and are monotonic, every address ∈ Ledger B ∪ {Chris, hubspot bcc, DSN}) — any violation fails the whole fire closed — and **post-send reconciliation** (new message's to/cc/bcc/subject must equal the armed row, else 🔴 finding) | 1 (fixed step 0), 3, 4, 6 (no params exist until `--arm`; `--plan` prints none), 2 and 5 become **detected** | LLM still carries bytes; a retyping error is caught, not prevented | None. ~150 lines + launcher text | Yes — same filesystem, same tools, tested today |
| **L2 — program sends via a Zapier webhook** (script POSTs armed params itself) | Would remove 5 and 6 entirely | — | — | **Not feasible in Cowork:** `device_bash` runs in an isolated Linux VM with **no network** (tested 17:30Z: `hooks.zapier.com`, `gmail.googleapis.com`, `imap.gmail.com` all unreachable). Also "Webhooks by Zapier" is a Premium app | **No** |
| **L3 — native program on the Mac, no LLM in the loop** | A standalone Python job (`launchd`, 4 slots/day) on macOS itself: reads Gmail through the **Gmail API** (OAuth, read + send scopes, Chris's account), applies the same decision engine, takes an **OS `flock`**, re-reads each thread **milliseconds** before sending, sends through the Gmail API with the thread's own subject, labels, writes the same `runs/<date>/sender/` artifacts. The Claude scheduled task becomes a **reporter** (reads `followup_sends.json`, prints the one-line-per-row report) or is deleted | **All seven.** No transcription, no retyping, no session timing, OS-level mutual exclusion, read-check-send in one process | Mac must be on and awake at the slots (already true today — the vault must be reachable) | Google Cloud project + OAuth "Desktop" client (Workspace **internal** app so tokens do not expire every 7 days); one browser consent by Chris; `launchd` plist installed by Chris (one `launchctl load`); signature either from Gmail's `sendAs` setting (API returns it) or frozen in config. ~1 day of build, ~30 min of Chris | Network and OS access from macOS itself: yes by construction. Not yet built |

**L1 is not an alternative to L3; it is L3's decision engine with a slower, LLM-driven transport.** Everything in L1 (lock, claims, arm, validation, reconciliation, selftests) carries over unchanged; L3 swaps the transport and the scheduler. Building L1 first removes today's failure class immediately and leaves the L3 cut-over as a transport change.

### 9.4 · What L1 still leaves to chance, honestly

- A retyping error in GATHER that happens to produce a **valid** id for a **different** real thread. Probability is tiny (16 hex chars) and the thread would also have to be a sendable one; reconciliation would then flag a subject mismatch after the fact.
- A retyping error in the **body** of a send. Reconciliation checks recipients and subject from metadata; checking the body needs a `PLAIN_TEXT` read-back of the new message (cheap; can be added: first line must equal the greeting, link must be the approved one, no `google.com/url`).
- The LLM ignoring `FAIL CLOSED` and improvising. Mitigated structurally: with no `queries.json` written (lock refused) `--plan` has nothing to read, prints nothing, and `--arm` has nothing to arm — there are no params to copy.
- The session dawdling between `--arm` pass 2 and the Zapier call. The 180 s TTL is enforced at arm time, not at send time; a session that arms and then waits ten minutes is not stopped. `--verify` records `sent_at` against `armed.json.generated`; a gap over the TTL should be read as a finding (not yet automated).
- Two sessions whose `--queries` run within the same second. The lock is a scan-then-write; the second look after the write catches a sibling that appeared in between, and `--plan`/`--arm` repeat the check, so both would have to collide three times within milliseconds.

### 9.5 · Open for Chris (replaces §8's scope question)

- **Build L1 now** (program + launcher text), **and** schedule L3 as the end state? Or L1 only?
- For L3: is a Google Cloud OAuth client on `chrisdanilo.com` acceptable (one-time consent, tokens stored on the Mac)? If not, L3 is not available and L1 is the ceiling inside Cowork.


---

## 10 · IMPLEMENTATION RECORD — L1 built and verified 2026-10-06 (18:00–19:00Z)

**Chris's ruling:** "L1 only" (containment C already applied). Nothing in L3 was started.

### What changed

| File | Change |
|---|---|
| `bin/followup_send.py` | `--queries` takes the lock (sibling scan by listing **and** by-name probe; second look after writing; same-instant race → the later fire yields with `aborted:true`) · `--plan` repeats the lock, runs `validate_raw` on every raw file (one violation → FAIL CLOSED), writes rows as `armable` with **no params** · new `--arm` (pass 1 prints fresh `get_thread` reads; pass 2 `arm_gate`: same message ids, same own count, no own message today, no stage/stop label, no hidden message, not claimed, read < `arm_ttl_seconds`) writes `armed.json`, the only file with params · rule 5b `already sent today` · `--verify` reads `armed.json`, reconciles To/Cc/Bcc of the new message against the armed row, statuses `sent / UNVERIFIED / SENT-MISMATCH / DUPLICATE / dropped`, `UNARMED SEND` finding for a `zapier_*.json` outside the armed set · `--report-yesterday` prints `dropped at arm`, repeats every fire's 🔴 findings and runs the **DUPLICATE SEND AUDIT** over every thread read back · `FS_NOW_OVERRIDE` honoured only with `FS_RUNS_OVERRIDE` (sandbox replays) · 20 new selftests. Backup of the pre-change file: `runs/2026-10-06/sender/_pre-CAPA/` |
| `config.json` | `followup_sender.fire_lock_minutes: 50`, `arm_ttl_seconds: 180`, each with `_why` |
| `method.md` §0.16 | fire table rows 0, 1, 2, 2b, 3, 5, 6; rule 5b; the "never" paragraph; the nightly touchpoints |
| Scheduled task prompt | step 0 folder recovery · ARM step · ACT from `armed.json` · FAIL CLOSED = stop (see §10.3) |

### 10.1 · Selftest — 45/45 PASS (`python3 bin/followup_send.py --selftest`)

New cases: rule 5b · lock blocks a 6-min-old unverified sibling · verified sibling releases · 62-min-old sibling is stale, not live · aborted sibling never blocks · claims from a live sibling's plan + armed rows · `--queries` fails closed end to end (subprocess, exit 1, no folder) · `validate_raw` catches a non-hex id and an id/filename mismatch, passes a clean transcript · arm gate ×9 (agrees → armed; another fire's send appeared → dropped; a reply appeared → dropped; `Label_10` present → dropped; ⚠ appeared → dropped; hidden message → dropped; read > TTL → re-read; claimed → dropped; wrong thread → dropped).

### 10.2 · Dry run of TODAY's two fires in a sandbox copy (`FS_RUNS_OVERRIDE`, clock pinned with `FS_NOW_OVERRIDE`; no Gmail, no Zapier)

| Step | Pinned clock | Result |
|---|---|---|
| (a) fire B `--queries` while 0929ET has started and not verified | 13:35:41Z | **FAIL CLOSED: fire 0929ET is in flight … exit 1, no folder created.** Today's second fire dies here |
| (b) 0929ET verified (13:44:41); B `--queries`, `--plan` | 13:47:00Z / 13:47:18Z | lock released; PLAN `armable 8 · skip 70`; `plan.json` carries **0** params |
| (b3) B `--arm` pass 1 | 13:48:30Z | NEEDS 8 fresh reads |
| (b4) B `--arm` pass 2 with the real 13:54Z read-backs as the fresh reads (0929ET's sends present) | 13:48:40Z | **dropped 8** — `thread changed since the gather: new message(s) [1a11172c…, 1a111797…]`; with only `Label_10` differing → `stage label Label_10 already on the thread`. Nothing to send |
| (c) fresh reads crafted to equal the gather (pre-0929ET state) → `--arm` | 13:48:40Z | `send 8` with params; then `--verify` against the real read-backs → **DUPLICATE 8**, 8 🔴 findings, **0 label flips** |
| (d) read-backs crafted as clean (2 own) with one retyped Cc and one stray `zapier_` file | 13:54:12Z | `sent 7 · SENT-MISMATCH 1`; findings `UNARMED SEND …`, `SENT-MISMATCH … person0792@org0405.example vs person0793@org0406.example`; label flips for the 7 only |
| (e) `--report-yesterday` on the real `runs/2026-10-06` (what tomorrow's nightly prints) | — | `Sender: yesterday 9 Email 2 … 8 UNVERIFIED … fires 4/4` + `🔴 DUPLICATE SEND AUDIT: 8 threads (2026-10-06: 2 own)` |

Both independent guards (lock, arm) each stop today's failure on their own; the audit names it after the fact.

### 10.3 · Still open

- ~~The scheduled task prompt (P5)~~ **Done 19:02:38Z** — `update_trigger` accepted the new prompt ("re-signed by Claude Desktop"); the stored prompt equals `LAUNCHER-followup-sender.md`. Next fire 2026-10-07 08:33 ET runs the new flow.
- P6 operating rule (no manual run within 15 min of a slot) — a rule for Chris; the lock enforces it anyway.
- Email 3 for the 8 ⚠ threads — Chris's hand send.
- L3 (native Mac job) — not approved; the L1 engine carries over if it ever is.
