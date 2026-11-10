---
title: LAUNCHER — inbox read (record copy; _shared/orchestrator/run.py read prints the block below)
status: built 2026-10-31 (split, Chris: two tasks for safety). The night run's first step. Taken from the retired morning sender's steps 2–4; read-only toward Gmail (it never sends, drafts or labels).
rules: RULEBOOK.md (B, J6, M)
---

Your FIRST output message must begin with: "YYYYMMDD – Outreach Inbox Read" using today's America/Denver date.

You read every outreach thread in Gmail and rebuild the master list from it, for Chris Danilo (Human Skills Training). Unattended: ask nothing. You run printed Gmail reads and save them VERBATIM, and run the scripts. NEVER SEND EMAIL, never create or change a draft, never change a label in this step.

Paths (device shell): MK="$HOME/mnt/ClaudeVault/3.Human Skills Training/Marketing/Automations"; ENG="$MK"; MASTER="$ENG/_shared/master"; D = the slot date the night run printed (the next business day).
SAVING VERBATIM: a large tool result saved to a file in the cloud workspace → copy it to the Mac byte-for-byte with device_commit_files; an inline result → write it with a quoted heredoc (cat > "<path>" <<'EOF2' … EOF2) unchanged, then python3 -c "import json;json.load(open('<path>'))". Never summarize, reformat or retype.

0. MOUNT. get_device_info; if connectedFolders is empty, device_request_folder_access for /Users/<you>/ClaudeVault once. Still unreachable → stop and say so.
1. LOCK. cd "$MK" && python3 _shared/orchestrator/lock.py acquire night-inbox. HELD BY → report "yielded to <holder>" and stop. You MUST release it in step 5.
2. PLAN FILE. cd "$ENG" && python3 7_Send/programfiles/send.py export --slot $D   (so the thread list for the read exists; a NOT A BUSINESS DAY line is fine — keep going).
3. INBOX READ. python3 1_Read-the-Inbox/programfiles/inbox.py queries — run searches 2–6 for the window since the last read (split any window that returns 50 until each is < 50), save every page verbatim under $ENG/1_Read-the-Inbox/runs/gmail/$D/. Then get_thread (messageFormat MINIMAL) for EVERY thread listed in $ENG/7_Send/runs/$D/master-plan.json rows AND every thread the searches returned, save each verbatim as $ENG/1_Read-the-Inbox/runs/gmail/$D/thread_<id>.json, and run: python3 1_Read-the-Inbox/programfiles/inbox.py ingest $ENG/1_Read-the-Inbox/runs/gmail/$D/thread_*.json
   Successors (Rulebook J6): if an auto-reply says a recipient has LEFT or handed over the role and names new contacts, get_thread PLAIN_TEXT for that message, save it verbatim under $ENG/1_Read-the-Inbox/ledgers/successors-raw/, and append ONE record to $ENG/1_Read-the-Inbox/ledgers/successors.jsonl in the format in 1_Read-the-Inbox/programfiles/successors.py (copy names, addresses, titles and routing text exactly as written; applies=false with the reason when the routing clearly points elsewhere, e.g. another region; departed=false for a temporary cover). Never invent a field.
4. REBUILD. python3 "$MASTER/build_master.py" ; cd "$ENG" && python3 7_Send/programfiles/send.py export --slot $D . If it exits 3 with CHECK lines: for each, call apollo_email_validation_validate with that email, append {"email","result","source":"apollo/zerobounce","date"} to $ENG/1_Read-the-Inbox/ledgers/successor-validation.jsonl, and run export again until it exits 0.
5. RELEASE (always): cd "$MK" && python3 _shared/orchestrator/lock.py release night-inbox

NEVER: send any email · create, change or delete a draft · change a label · ask Chris anything (a question goes only through: python3 "$ENG/_shared/orchestrator/rulings.py" open --machine shared --q "...").
