---
business: Human Skills Training
type: capa
title: "CAPA 2026-09-30 — Zapier attached the kit correctly; Chris attached it by hand anyway, because two drafts sat on one thread"
status: closed-by-cutover
owner: Chris Danilo
raised_by: Chris ("I had to manually attach the attachment. So I'm not sure what went wrong there")
related: ["[[method]]", "[[CAPA-2026-08-26-google-link-wrapper]]", "[[ATTACHMENT-SIZE-BUDGET]]", "[[STATE]]"]
---

# CAPA — the attachment worked; the handoff failed

## 1 · What happened (all times UTC, all IDs read back from Gmail)

| Time | Event | Evidence |
|---|---|---|
| 09:28 | Nightly run creates the Tri-Valley Email 3 draft, no attachment (native connector, as designed) | draft `r409288506502821325`, message `<thread-id>` |
| 19:53 | Zapier `gmail_create_draft_reply` creates a SECOND draft on the same thread with `HST_3PackStarterKit.pdf` attached, pulled by Zapier "Find Email" from the [Org 0519] send earlier that day | draft `r-5408725743047051353`, message `<thread-id>`, `threadId <thread-id>`, label `Label_2` applied at creation |
| 19:53–19:58 | Verification (raw MIME read-back) and the trash of the old draft do NOT happen: the Gmail read connector's session expired three times in a row on the RAW read | connector error `MCP server "Gmail" session expired` ×3 |
| ~19:58 | Report to Chris says: two drafts on the thread, old one untouched, "delete the 09:28 one yourself" | chat |
| 20:01 | Chris opens the OLD draft, edits the body (removes the Natasha line), drags the kit on, does not send yet | old draft now dated `2026-09-30T20:01:04Z`, new message id `<thread-id>`, `has:attachment` true |
| 20:0x | Confirmed: BOTH drafts carry an attachment. Zapier's did from creation | `list_drafts` query `subject:"[Org 1196]" has:attachment` returns both |
| 20:1x | Attempt to trash the Zapier draft (own message id only) | denied by the session permission classifier ("External System Writes") |

**Net: the Zapier attachment path worked end to end. The human step failed because the thread held two look-alike drafts and the only distinguishing mark (a label, and a 19:53 timestamp) is invisible in Gmail's draft list.**

## 2 · Root cause

The retrofit procedure for an existing reply draft is "create the replacement, THEN trash the old draft's own message" (method Phase 3 🅑). Step 2 depends on a read-back succeeding first. When the read-back path died, the procedure stopped in the unsafe middle state — two sendable drafts on one thread — and handed the choice to Chris with no reliable way to tell them apart.

## 3 · Contributing causes

| # | Cause | Class |
|---|---|---|
| C-a | The Gmail read connector cannot return RAW for a draft carrying a ~7 MB attachment (three consecutive session expiries; a 400 KB attachment read fine earlier the same hour) | tooling limit, undocumented until today |
| C-b | The session classifier blocked two writes today: the first `draft_v2_reply` ("Unrequested Commit in a Connected App") and the `trash_message` cleanup ("External System Writes"). Both were requested by Chris. Behaviour is not predictable per call | tooling limit |
| C-c | Zapier's "Find Email" search can only be enabled from here together with "Send Email"; it was switched on and off twice during the test. Not a cause of this defect, recorded because it is a standing hazard | tooling limit |
| C-d | The report told Chris which draft to delete by time (09:28) rather than by something visible in his Gmail UI | reporting |

## 4 · What is now KNOWN to work (do not re-test these)

- Zapier `gmail_create_draft` / `gmail_create_draft_reply`: clean hrefs (0 `google.com/url`), HTML formatting, `label_ids` at creation, attachment by URL, attachment by Zapier file reference from a Gmail search — all read back from raw MIME or `has:attachment`.
- `thread_id` on the reply action takes the THREAD id. A message id returns "Requested entity was not found" (tested both ways).
- Zapier does NOT write a `Content-ID`; it cannot embed an inline image. `Content-Disposition: attachment`, no CID, read from raw MIME.
- Zapier's auto-generated `text/plain` part drops line breaks between `<li>` items unless the HTML source carries newlines.

## 5 · Corrective actions — PROPOSED, Chris rules

| # | Control | Cost |
|---|---|---|
| **C1** | **Never leave two drafts on one thread at a turn boundary.** If the old draft cannot be trashed in the same step, report BOTH view URLs with the words "SEND THIS ONE" / "DELETE THIS ONE" next to each. Time-of-day is not an identifier | reporting rule |
| **C2** | **Verify large drafts with `has:attachment` + `FULL_CONTENT`, never RAW.** RAW is for bodies under ~1 MB (links, formatting). Attachment presence and size come from the search / metadata read | method Phase 3 |
| **C3** | **The retrofit procedure is temporary.** Once Zapier creates every draft at the nightly run, there is never an old draft to trash and this failure mode disappears. Track under the Zapier cutover plan; do not build more tooling around retrofits | design |
| **C4** | **Enable Zapier "Find Email" once, from the Zapier web UI, without "Send Email."** The MCP toggle cannot separate them. Until then, any session that enables it must disable it in the same turn (done today, twice) | Chris, ~1 min |
| **C5** | **Record classifier denials in the run report as a named gate**: `Classifier: N writes denied (which)`. Two today. This is the open risk for unattended Zapier writes and it needs a count, not an anecdote | reporting rule |

## 6 · Open item for Chris

Two drafts remain on thread `<thread-id>`:
- `r409288506502821325` — YOUR edited draft (20:01, attachment added by hand, Natasha line removed). **Send this one.**
- `r-5408725743047051353` — Zapier's draft (19:53, label `CCR&R outreach`, attachment from Zapier). **Delete this one.** The machine's trash call was denied.

Size note, no recommendation attached: today's 18 sent Email 3s and both Tri-Valley drafts carry the 7.2 MB `HST_3PackStarterKit.pdf` (~9.9 MB encoded). Chris ruled 2026-09-30: fix attaching first, shrink the file later.

---

## 7 · UPDATE 2026-09-30 evening — resolved for Tri-Valley; a second finding about Gmail's web view

**Sequence:** Chris deleted his hand-edited draft (kept Zapier's) → Zapier's draft rebuilt on request without the Natasha line, old Zapier draft trashed by its own message id (classifier allowed it on the explicit ask) → thread held exactly ONE draft, `has:attachment filename:pdf` true → Chris sent it.

**Outcome on the thread:** message `<thread-id>`, To `person0899@org0737.example`, Cc `person1235@org0737.example`, Bcc `<HUBSPOT_BCC_ADDRESS>` (re-added at send by the HubSpot extension, as documented), label `CCR&R outreach`, **9,657,810 bytes**, dated `2026-10-01T12:00:00Z` — i.e. Gmail *Schedule send* for 6:00 AM MDT Oct 1; it carries no `SENT` label until it goes.

### Finding 2 — Gmail's conversation view did not render the Zapier-built reply draft

| Observation | Evidence |
|---|---|
| Gmail's Drafts list DID contain the thread | Screenshot: URL `mail.google.com/mail/u/0/#drafts/FMfcgz…` — Chris reached the thread from the Drafts folder |
| The conversation view showed Email 1, the bounce, Email 2 — and **no draft box** | Screenshot |
| Hard reload (Cmd+Shift+R) did not change that | Chris |
| **The draft's own compose link opened it fine** with body and attachment, and it was sendable | Chris: "used your link and it looks fine" |
| Server-side the draft was well formed | `In-Reply-To` / `References` pointing at Email 2 / Email 1, `Subject: Re: …`, labels `DRAFT` + `Label_2` (read via Zapier "Find Email", which returns headers without the attachment bytes) |

**Not yet isolated — one candidate difference, to be tested before it is believed:** Zapier encoded this draft's `text/html` part as `Content-Transfer-Encoding: base64` (its quoted history exceeds the 998-character line limit), whereas the two new-thread test drafts Chris *could* see were sent 8-bit with no transfer encoding. Whether Gmail's compose view refuses base64 HTML drafts, or refuses API reply drafts in general, is unknown. **Test:** one short Zapier reply draft (no attachment, body under one line) on a test thread → does the conversation view render it? Then the same body padded past 998 chars.

### Corrective actions added

| # | Control | Cost |
|---|---|---|
| **C6** | **Every machine-created draft is reported with its own compose link** (`…#all?compose=thread-f:…%2Bmsg-a:<draftId>`), never just "it's in Drafts." The link opens the draft whether or not the conversation view renders it | reporting rule, zero cost |
| **C7** | Run the base64 / line-length isolation test above before Zapier reply drafts go into the nightly run. If base64 is the cause, the fix is on the builder side (shorter lines or quoted-printable), not in Gmail | one test |

### Tooling facts recorded today (for [[method]] "capability claims expire")

- Native Gmail read connector: `get_draft RAW` fails ("session expired") on drafts carrying a ~7 MB attachment; three tries. Use `list_drafts … has:attachment filename:pdf` for presence and Zapier "Find Email" (`in:drafts …`) for headers.
- Zapier MCP toggle: enabling Gmail "Find Email" also enables "Send Email" and "Reply to Email"; the MCP tool cannot enable the search alone. Switched off after each use (three times today). Chris to enable "Find Email" by itself from the Zapier web UI.
- Session classifier: denied 2 of 4 write calls today (first reply draft, first trash), allowed the same calls on explicit re-request.


---

## 8 · UPDATE 2026-10-03 — C3 executed: Emails 2 and 3 now created by Zapier at the nightly run

- `config.draft_writer` installed (Chris 2026-10-03: "focus on emails two and three first"). Email 2 and Email 3 drafts are Zapier reply drafts from creation; there is no longer an old native draft to retrofit, so the two-drafts-on-one-thread failure mode disappears for follow-ups. C1 (SEND THIS ONE / DELETE THIS ONE) stays as the rule for the one-off cleanup of drafts that already existed before cutover.
- C2 adopted verbatim in `config.draft_writer.zapier.verify` (`has:attachment` read-back, never RAW on a 7 MB draft).
- C4 resolved differently: enabling the Gmail **`attachment`** lookup by its action key alone added exactly one action (total 3). The 09-30 coupling only happens when no action key is passed. "Find Email" is not needed — `attachment` takes a known sent message id + filename and returns the file reference directly.
- C5 and C6 adopted as §0.6 lines (`Classifier:`) and the compose-link rule.
- C7: the 2026-10-03 Email 2 test draft (short body, 8-bit HTML part, no quoted history) — Chris to confirm it renders in the conversation view. Zapier reply drafts carry no quoted history, so the >998-character base64 case does not arise for Email 2; Email 3's HTML is also short.
- Email 1 is untouched (BQ-022).

---

## 9 · UPDATE 2026-10-04 — Finding 2 ROOT CAUSE FOUND; the base64 hypothesis is retired; C7 closed

**Chris's screenshot 2026-10-04:** the 2026-10-03 Email 2 test draft (first draft on its thread) rendered in the conversation view. But every one of the 24 drafts rebuilt via Zapier on 10-03 shows only *"1 deleted message in this conversation"* at the bottom of the thread and no draft box.

**Mechanism, proven on the test thread `<thread-id>` (raw MIME read-back of each draft):**

| Test | Newest thing on the thread at creation | New draft's `In-Reply-To` |
|---|---|---|
| [Org 1333] rebuild (10-03) | the old native E2 draft (trashed seconds later) | the old native draft (`<CACfedjpPz82…>`), not Email 1 (`<CACfedjrL7hf…>`) nor the bounce (`<…person0452@org0000.example>`) |
| RENDER TEST 1 (10-04) | a live draft | that draft |
| RENDER TEST 2 (10-04), created after EVERY draft on the thread was TRASHED | nothing live but trashed drafts | the trashed draft I had just created |

**Zapier's Create Draft Reply attaches the new draft to the newest message on the thread — drafts and trashed messages included.** Gmail's conversation view renders a draft only under a visible parent; a draft whose parent is a trashed draft is hidden behind the *"1 deleted message"* banner (still in the Drafts list, still opens from its compose link, still sendable — Tri-Valley 09-30 was sent that way). Trashing the old draft does not help; only **deleting it forever** removes it from the thread, and the machine cannot do that.

**Encoding was never the cause** — the 10-03 drafts are 8-bit, short, no quoted history, and still hidden.

**Corrective actions (installed 2026-10-04):** `config.draft_writer.zapier.reply_parent_rule`; method §0.3 step 12 (pre-check `hidden > 0` ⇒ `COMPOSE-LINK-ONLY` on the card, counted), §0.4 **Z5**, Phase 3 step 7 ① (rebuild = trash → Chris deletes forever → create); C3's "create replacement, then trash old" procedure is RETIRED. The 24 affected drafts: BUILD-QUEUE **BQ-026**.

### §9 addendum, 2026-10-04 evening — fixed, plus one more inheritance

Chris deleted every trashed draft forever (Gmail search `in:trash subject:"Question about PD/Training"` → Delete forever), then all 36 waiting drafts were rebuilt through Zapier with the signature: 12 Email 1 as new threads, 16 Email 2 and 8 Email 3 as replies whose parent is now Chris's own sent mail. **One more thing a Zapier reply inherits: the SUBJECT of the message it replies to.** YWCA's thread had the Cc bounce as its newest message and the reply came back titled *"Delivery Status Notification (Failure)"*; it was trashed and re-created as a new-thread draft with `Re: Question about PD/Training at [Org 1333] . . .`. Rule installed: `config.draft_writer.zapier.reply_parent_rule.subject_check` + method §0.3 step 12. BQ-026 closed.

