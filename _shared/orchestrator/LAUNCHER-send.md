---
title: LAUNCHER — the 7 AM send task (record copy; _shared/orchestrator/run.py send prints the block below)
status: built 2026-10-31 (split, Chris: "a separate task that sends the mail at the right time … solely to send the mail that has been approved"). Mon–Fri ~06:52 America/New_York. The ONLY outreach task with automatic approval.
rules: RULEBOOK.md (C, I, J, L, M). Approved = put on the list by the night run's rulebook checks; flagged = not approved.
---

Your FIRST output message must begin with: "YYYYMMDD HH:MM – Outreach 7 AM Send (approved list only)" using the current America/Denver date and time.

You send Emails 2 and 3 for Chris Danilo (Human Skills Training) — ONLY the rows on today's FINAL approved send list that the night run wrote. Nothing else. Unattended: ask nothing, decide nothing. You run printed Gmail reads and save them VERBATIM, run the scripts, and make only the tool calls the scripts print. If any step prints FAIL CLOSED, REFUSED or NO SEND, obey it.

Paths (device shell): MK="$HOME/mnt/ClaudeVault/3.Human Skills Training/Marketing/Automations"; ENG="$MK"; D=today's date YYYY-MM-DD (America/New_York); LIST="$ENG/7_Send/ledgers/send-lists/$D.json".
SAVING VERBATIM: a large tool result saved to a file in the cloud workspace → copy it to the Mac byte-for-byte with device_commit_files; an inline result → write it with a quoted heredoc (cat > "<path>" <<'EOF2' … EOF2) unchanged, then python3 -c "import json;json.load(open('<path>'))". Never summarize, reformat or retype.

0. MOUNT. get_device_info; if connectedFolders is empty, device_request_folder_access for /Users/<you>/ClaudeVault once. Still unreachable → stop and say so (nothing sent).
1. LOCK. cd "$MK" && python3 _shared/orchestrator/lock.py acquire send --exclusive   (the send machine — its own lock; the night run never blocks it). HELD BY → report "yielded to <holder>" and stop. You MUST release it in step 8.
2. THE LIST. cd "$ENG" && python3 7_Send/programfiles/sendlist.py check   → LIST OK: continue. Anything else (no list · not final · not a business day): send nothing, go to step 7 (report) and step 8.
3. WAIT FOR 07:00 ET. Repeat  python3 7_Send/programfiles/sendlist.py wait  until it prints WAKE (each call sleeps ≤ 170 s). Never send before 07:00 ET. Never create or schedule anything to wait.
4. GATHER + PLAN, per machine, OM-2 first then OM-1 (OM-2 = "$MK/_shared/machines/OM-2", OM-1 = "$MK/_shared/machines/OM-1"), from "$ENG" with
   export FS_MASTER_PLAN="$LIST" FS_MODE=send
   a. python3 7_Send/programfiles/followup_send.py --machine <folder> --queries → it prints a get_thread for every list thread of that machine plus list_drafts: run them, save verbatim as named.
   b. python3 7_Send/programfiles/followup_send.py --machine <folder> --plan --fire <id> → do any NEEDS reads (saved verbatim), rerun until it stops asking. A thread that changed since the list was made (a reply, an auto-reply, a bounce, a stop label, an open draft, a different stage) is held here — it is not sent; tonight's run decides again.
5. SEND, per machine, same env and fire id:
   c. python3 7_Send/programfiles/followup_send.py --machine <folder> --arm --fire <id> → do the printed get_thread reads, save verbatim, rerun --arm IMMEDIATELY (reads expire after 180 s).
   d. For each armed.json row of THIS batch with action "send" and no raw/zapier_<thread>.json: resolve {{SIGNATURE}} and {{KIT_FILE}} (Email 3 only) exactly as _shared/master/settings.json machines.<OM>.followup_sender.zapier.resolve says, FRESH; then python3 7_Send/programfiles/followup_send.py --machine <folder> --intent --fire <id> --thread <thread> ; ONLY on GO call execute_zapier_write_action (selected_api GoogleMailV2CLIAPI, action reply_to_message, tool_name gmail_reply_to_email) with the row's params VERBATIM; save the response verbatim as raw/zapier_<thread>.json. REFUSED → do not call Zapier for that row. Never call Zapier twice for one thread. Back to c until --arm says no rows remain.
   e. python3 7_Send/programfiles/followup_send.py --machine <folder> --verify --fire <id> → do the read-backs (saved verbatim), rerun --verify, then apply ONLY the label changes it prints, in order.
6. Any list row the engine held or dropped: it is listed in the report with the engine's reason. Never send it another way.
7. REPORT. cd "$ENG" && python3 7_Send/programfiles/sendlist.py report   — it writes the "7 AM send" section into this morning's report. Your last message is its text, plus every 🔴 FINDING line the engine printed.
8. RELEASE (always — after NO SEND, FAIL CLOSED, REFUSED or an abort too): cd "$MK" && python3 _shared/orchestrator/lock.py release send

NEVER: send anything that is not a row of today's FINAL approved list · send Email 1 · send anything --intent did not GO · send before 07:00 ET or on a non-business day · change copy, recipients or subject · create, change or delete a draft · call any Zapier action other than reply_to_message, attachment and the signature lookup · apply a label no script printed · create, change or fire any scheduled task · delete anything · ask Chris anything (a question goes only through: python3 "$ENG/_shared/orchestrator/rulings.py" open --machine shared --q "...").
