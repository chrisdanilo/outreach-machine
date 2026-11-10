---
title: LAUNCHER — morning report (record copy; _shared/orchestrator/run.py report prints the block below)
status: built 2026-10-31 (Stage 7). The night run's last step (Stage 8); can be run on its own any time.
rules: RULEBOOK.md M5 — one morning report for every machine
---

Your FIRST output message must begin with: "YYYYMMDD – Outreach Morning Report" using today's America/Denver date.

You build Chris Danilo's one morning outreach report. Read-only: you change nothing.
0. MOUNT. get_device_info; if connectedFolders is empty, device_request_folder_access for /Users/<you>/ClaudeVault once. Still unreachable → stop and say so.
1. cd "$HOME/mnt/ClaudeVault/3.Human Skills Training/Marketing/Automations" && python3 6_Report/programfiles/report.py
2. Your reply is the text it printed, unchanged (plain English, one screen first, then details, then the file links).
