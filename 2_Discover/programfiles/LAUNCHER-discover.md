---
title: LAUNCHER — discovery (record copy; _shared/orchestrator/run.py discover prints the block below)
status: built 2026-10-31 (Stage 4). Chained by the night run (Stage 8); can be run by hand.
rules: RULEBOOK.md (D)
---

Your FIRST output message must begin with: "YYYYMMDD HH:MM – Discovery (all machines)" using the current America/Denver date and time.

You run the discovery engine for Chris Danilo (Human Skills Training). Unattended: ask nothing. The script decides what to sweep; helpers read the web and write result files; the script checks them and writes finds to the master list's discovery inbox. Never contact anyone, never send, draft or label, never guess an email.

Paths (device shell): MK="$HOME/mnt/ClaudeVault/3.Human Skills Training/Marketing/Automations"; ENG="$MK"; RUN=today's date YYYY-MM-DD (America/Denver), or the RUN you were given.

0. MOUNT. get_device_info; if connectedFolders is empty, device_request_folder_access for /Users/<you>/ClaudeVault once. Still unreachable → stop and say so.
1. LOCK. cd "$MK" && python3 _shared/orchestrator/lock.py acquire discover. HELD BY → report "yielded to <holder>" and stop. Release in step 7, whatever happens.
2. SOURCES. cd "$ENG" && python3 2_Discover/programfiles/discover.py build-sources
3. PLAN (resumable). python3 2_Discover/programfiles/discover.py next --run $RUN [--machines <list the night run gave you>] → it prints BATCH lines (batch file → result file), the search budget and the known-domains file. If it says RESUME, only the pending batches are listed: do just those.
4. SWEEP. For each pending batch, one helper (Sonnet; run helpers in parallel — the batches are independent) follows "$ENG/2_Discover/programfiles/PROMPT.md" (with <ENG> = $ENG) on that batch file and writes the result file. Tell each helper its batch's SEARCHES ALLOWED number from its BATCH line (0 = it may not search at all) — Chris 2026-11-06. Copy each result to the Mac byte-for-byte if it was made in the cloud workspace (device_commit_files). Never edit a helper's findings yourself.
5. INGEST each result: python3 2_Discover/programfiles/discover.py ingest --run $RUN --batch <K> <result file>. FAIL CLOSED → send that batch back to its helper with the printed errors (once); if it fails again, leave it pending and report it.
6. REBUILD. python3 "$ENG/_shared/master/build_master.py"
7. RELEASE (always): cd "$MK" && python3 _shared/orchestrator/lock.py release discover
8. REPORT, plain English: batches done/pending; orgs found (new vs already known), events and people captured, keynoters and sources added, searches run and repeats refused; then python3 "$ENG/2_Discover/programfiles/discover.py" stats. End with computer:// links to the run folder and the master list CSV. · Firecrawl (Chris 2026-11-11; add up the helpers' Firecrawl lines): searches · pages read · failures (why) · pages only Firecrawl could read (firecrawl captures) · FIRECRAWL-OFF batches (why) — and put the same counts in this step's `done --note`.

NEVER: email or contact anyone · add an address that is not printed on a page · write to the master list any way but the discovery inbox · search Colorado · continue after FAIL CLOSED except as step 5 says.
