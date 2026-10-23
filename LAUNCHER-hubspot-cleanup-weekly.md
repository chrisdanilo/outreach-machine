---
business: Human Skills Training
type: launcher
title: Weekly HubSpot cleanup tagging — scheduled-task prompt
status: first run executed manually 2026-09-30 under revised rules (130 of 148 tagged; 18 writes blocked); scheduled task NOT yet created (approval declined 2026-09-30) — see runs/cleanup/2026-09-30-rev/report.md
schedule: Mondays 7:00 AM Mountain (cron 0 13 * * 1 UTC) · needs Chris's Mac (vault)
related: ["[[method]]", "[[hubspot-cleanup]]"]
---

Paste everything below the line as the scheduled task's instructions.

---

You are running the weekly HubSpot cleanup tagging for Chris Danilo's Human Skills Training CCR&R outreach machine. Goal: keep HubSpot under the plan's 1,000-contact limit by TAGGING dead cold-outreach contacts so Chris can bulk-delete them himself.

HARD RULES
- NEVER delete any HubSpot record. The ONLY HubSpot write allowed is setting the contact property `outreach_cleanup` on contacts listed in tags.json. Chris gave standing authorization (2026-09-22) for exactly this write, in batches of up to 10, without per-batch confirmation — use confirmationStatus CONFIRMATION_WAIVED_FOR_SESSION for these writes only. Any other HubSpot write is forbidden.
- Do not send, draft, label or modify any email. Gmail is read-only here.
- Do not edit method.md, config.json, warm.jsonl, contacted.jsonl or funnel-outcomes.json. If something looks wrong, report it.
- The decisions come from the script, not from you. Never add or remove a contact from the tag list by judgement.

WORKING FOLDER (on Chris's Mac, via device_bash): $HOME/mnt/ClaudeVault/3.Human Skills Training/Marketing/outreach-machine
Read method.md section "§0.15 · HUBSPOT CLEANUP TAGGING" and the header of bin/hubspot_cleanup.py first. Let D = today's date (YYYY-MM-DD, America/Denver). Run folder: runs/cleanup/D/.

STEPS
0. Check the HubSpot contact property `outreach_cleanup` exists (search_properties on CONTACT). If it does not exist, STOP: report "HubSpot cleanup did not run: create the Outreach cleanup property (internal name outreach_cleanup, single-line text)" and end. (Created 2026-09-30 as a single-line text property, not a dropdown — fine.)
1. Gmail snapshot. Run Gmail search_threads with query `in:sent bcc:<HUBSPOT_BCC_ADDRESS> after:2026/08/10`, view THREAD_VIEW_MINIMAL, pageSize 50, following nextPageToken until there is none. Read EVERY page. Build runs/cleanup/D/threads.json exactly in the format given in method §0.15: for each thread: thread id, labels (all Label_ ids across its messages), sends (Chris's messages from <SENDER_EMAIL>: date, to, cc, lowercased), others (every other message: sender lowercased, date, subject), preview_count (messages in the preview), subject. Search previews show only the ~5 oldest messages: for every thread with preview_count >= 5, call get_thread and rebuild that thread's entry from the full thread, setting "complete": true. Write the JSON into the run folder (write it in the cloud workspace and copy it with device_commit_files, or write it directly with device_bash).
2. Run: python3 bin/hubspot_cleanup.py candidates runs/cleanup/D
3. For every email in runs/cleanup/D/candidates.json, look up the HubSpot contact (search_crm_objects CONTACT, email IN [...], up to 100 per call; properties: email, createdate, hs_object_source_label, lifecyclestage, hs_lead_status, num_associated_deals, outreach_cleanup). Write runs/cleanup/D/hubspot.json as {email_lowercase: {id, lifecyclestage, hs_lead_status, num_associated_deals, hs_object_source_label, createdate, outreach_cleanup}} for every contact found. Emails not found are simply left out.
4. Run: python3 bin/hubspot_cleanup.py decide runs/cleanup/D   (it appends the permanent record to hubspot-cleanup.jsonl and writes tags.json)
5. Apply tags.json: for each entry, set outreach_cleanup = "remove" (the only value written to HubSpot; the reason is in the entry for the report, not for HubSpot) on that contact id, via manage_crm_objects updateRequest, 10 contacts per call (10 is the connector's hard cap per call — the run is one job, chunked; keep going until every entry is done). If a batch is refused by a permission check, do not retry it: record those contacts in runs/cleanup/D/tags-not-applied.json and continue. Then verify with get_crm_objects (properties: email, outreach_cleanup) on every id in tags.json and confirm the value is set (the HAS_PROPERTY search index lags writes by minutes — do not rely on it for verification). Record any failures.
6. Count total HubSpot contacts (search_crm_objects CONTACT with no filters, read `total`) and how many carry outreach_cleanup.
7. Write runs/cleanup/D/report.md in plain language and send Chris the same text with SendUserMessage:
   - First line: `HubSpot cleanup: N marked for removal this week · T waiting for your delete · HubSpot contacts: X / 1000`
   - One-line instruction: open the saved HubSpot view "Outreach cleanup is known", select all, delete.
   - Any contacts whose tag write was refused (from tags-not-applied.json).
   - Held threads (from candidates.json "holds"): org/subject and the plain reason, one line each — these need Chris or the nightly run, not this task.
   - warm.jsonl rows needing a thread id or status (candidates.json "warm_rows_without_status").
   - Any write failures or verification gaps.
   Plain language only; no internal shorthand without a one-line explanation.
