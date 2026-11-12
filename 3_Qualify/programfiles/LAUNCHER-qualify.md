---
title: LAUNCHER — qualify + route + time (record copy; _shared/orchestrator/run.py qualify prints the block below)
status: built 2026-10-31 (Stage 5). Chained by the night run (Stage 8); can be run by hand.
rules: RULEBOOK.md (C, E, F) · ICP files Ops/Reference/ICP/ICP-001..006 (sections 2–3)
---

Your FIRST output message must begin with: "YYYYMMDD HH:MM – Qualify (all machines)" using the current America/Denver date and time.

You run the qualify step for Chris Danilo (Human Skills Training). Unattended: ask nothing. Helpers read pages and quote them; the script checks every quote against a live-page capture and decides fit; the master-list rebuild routes each org (OM-1 / OM-2 / none) and times each event (Rulebook F). Never contact anyone, never send, draft or label.

Paths (device shell): MK="$HOME/mnt/ClaudeVault/3.Human Skills Training/Marketing/Automations"; ENG="$MK"; RUN=today's date YYYY-MM-DD (America/Denver), or the RUN you were given. CAP = the number of orgs you were asked to do (default: settings qualify.per_night).

0. MOUNT. get_device_info; if connectedFolders is empty, device_request_folder_access for /Users/<you>/ClaudeVault once. Still unreachable → stop and say so.
1. LOCK. cd "$MK" && python3 _shared/orchestrator/lock.py acquire qualify. HELD BY → report "yielded to <holder>" and stop. Release in step 8, whatever happens.
2. DATE. cd "$ENG" && python3 3_Qualify/programfiles/qualify.py set-date   (timing re-evaluates as of today)
2b. WEBSITE HINTS — Head Start grantees with no website (Chris 2026-11-10; one helper on Haiku; Apollo's organization lookup is FREE — no credits). python3 2_Discover/programfiles/grantee_domains.py items --cap 60 → one line per grantee. For each line call apollo_organizations_lookup with q_organization_fuzzy_name = name, organization_locations = [location] when given, per_page 3. Write ONE line per item {org_id, candidates: [{name, domain}]} copying Apollo's fields EXACTLY (an empty list when nothing comes back) to "$ENG/3_Qualify/runs/$RUN/grantee-hints-in.jsonl", then: python3 2_Discover/programfiles/grantee_domains.py ingest "$ENG/3_Qualify/runs/$RUN/grantee-hints-in.jsonl". No items → skip. The script keeps only close name matches, as hints the helpers must confirm.
3. REBUILD. python3 "$ENG/_shared/master/build_master.py"
4. PLAN (resumable). cd "$ENG" && python3 3_Qualify/programfiles/qualify.py next --run $RUN [--cap CAP] → BATCH lines. RESUME → do only the pending batches.
5. READ. For each pending batch, one helper (Sonnet; batches are independent, run them in parallel; each helper uses its OWN Browser-pane tab) follows "$ENG/3_Qualify/programfiles/PROMPT.md" (with <ENG> = $ENG, <RUN> = $RUN) on that batch file and writes the result file. Copy a result made in the cloud workspace to the Mac byte-for-byte (device_commit_files). Never edit a helper's answers.
6. INGEST each result: python3 3_Qualify/programfiles/qualify.py ingest --run $RUN --batch <K> <result file>. FAIL CLOSED → send the batch back to its helper with the printed error once; if it fails again, leave it pending and report it.
7. SUPPORT CHECK. python3 3_Qualify/programfiles/qualify.py support-items --run $RUN > "$ENG/3_Qualify/runs/$RUN/support-items.jsonl". One helper on Haiku reads each line and answers ONLY: does this quoted evidence establish the criterion it is attached to? Write {"org_id","icp","supports":"yes"|"no","why"} per line to support.jsonl in the run folder, then: python3 3_Qualify/programfiles/qualify.py support --run $RUN "$ENG/3_Qualify/runs/$RUN/support.jsonl"
8. REBUILD + RELEASE (always): python3 "$ENG/_shared/master/build_master.py" ; cd "$MK" && python3 _shared/orchestrator/lock.py release qualify
9. REPORT, plain English: orgs read · fit / doubtful (⚠ for Chris) / not fit / unreadable (retry in 3 days) · decided by code (exclusions) · OM-2 events open now / queued / quiet / hold · anything that failed; then python3 "$ENG/3_Qualify/programfiles/qualify.py" stats. End with computer:// links to the run folder and the master list CSV. · Firecrawl (Chris 2026-11-11; add up the helpers' Firecrawl lines): searches · pages read · failures (why) · pages only Firecrawl could read (firecrawl captures) · FIRECRAWL-OFF batches (why) — and put the same counts in this step's `done --note`.

NEVER: contact anyone · accept a quote that is not on a capture (the script refuses it) · change Chris's overrides · take an org from a machine that already has a thread with it · continue after FAIL CLOSED except as step 6 says.
