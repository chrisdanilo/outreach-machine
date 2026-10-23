---
business: Human Skills Training
type: launcher
title: LAUNCHER — Machine 002 event refresh (record copy of the instructions stored in the scheduled task)
schedule: none — started with "Run now" (Chris 2026-10-20: button or schedule, undecided; a schedule can be added later without changing this)
updated: 2026-10-22
---

The block below is the scheduled task's instructions, verbatim.

---

Your FIRST output message must begin with: "YYYYMMDD – Conference Event Refresh (Machine 002)" using today's America/Denver date.

You run the event refresh for Chris Danilo's Machine 002 (Human Skills Training, conference organizers). Unattended: ask nothing, never fabricate, never send or draft email, never touch Machine 001's files.

THE PROGRAM is method.md, section "THE REFRESH", in the Machine 002 folder on Chris's connected computer:
  OM2="$HOME/mnt/ClaudeVault/3.Human Skills Training/Marketing/outreach-machine-002-conference"   (device shell)
  Mac path for staging/commit: /Users/chrisdanilo/ClaudeVault/3.Human Skills Training/Marketing/outreach-machine-002-conference
If this launcher and method.md disagree, method.md wins.

0. MOUNT. Call get_device_info. If connectedFolders is empty, call device_request_folder_access for /Users/chrisdanilo/ClaudeVault once. If still unreachable, abort and say so.
1. Read method.md (section THE REFRESH), config.json, research/SCHEMA.md and research/SEGMENT-PROMPTS.md.
2. RUN=today (YYYY-MM-DD, America/Denver); if runs/$RUN exists use $RUN-2, -3… On the device shell: mkdir -p runs/$RUN and, for each segment in config.refresh.research_segments, python3 bin/events.py worklist --segment <segment> > runs/$RUN/recheck_<segment>.jsonl
3. Stage SCHEMA.md and every recheck file into the cloud workspace with device_stage_files.
4. Launch one research agent per segment, ALL IN ONE MESSAGE (parallel), model sonnet, subagent general-purpose. Prompt = the common block (fill {TODAY}/{YEAR}, and {SEARCH_SHARE} = config.refresh.search_budget.per_segment_share) + that segment's block + the staged SCHEMA.md path + the staged recheck file path + output path /mnt/user-data/outputs/om2-refresh/$RUN/<segment>.jsonl. Wait for all of them.
5. For each output file: validate it is JSON-per-line (python3 -c to load every line; drop and report any bad line — never retype content), then copy it to the Mac byte-for-byte with device_commit_files (stagedPath = the outputs file, devicePath = .../runs/$RUN/<segment>.jsonl).
6. On the device shell, in order: python3 bin/events.py merge runs/$RUN/<each segment>.jsonl --run $RUN · python3 bin/events.py waves · python3 bin/events.py validate · python3 bin/events.py report --run $RUN. If validate prints FAIL lines, fix only what the FAIL names (by editing that event's line with a short python read-modify-write), re-run validate, and list every fix in the report.
7. REPORT in chat, plain language: open calls (soonest deadline first, with links) · new events · dates newly confirmed or moved · gaps left · agents that failed or could not reach sites. End with computer:// links to runs/$RUN/refresh-report.md and events-calendar.generated.md.

NEVER: send, draft or label any email · edit anything outside the Machine 002 folder · write a date, owner or email without a source URL · guess an email address · delete files.
