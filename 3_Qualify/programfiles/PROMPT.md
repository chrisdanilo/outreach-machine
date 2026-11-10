---
title: Qualify helper instructions (one batch file per helper) — Rulebook C, E, F
updated: 2026-11-10 (whole-calendar read, event kind, past editions, keynote check — Rulebook E3/F)
---

# Qualify helper (Sonnet)

You get ONE batch file (one org per line) and write ONE result file. You read; the script decides. Never contact anyone,
never guess, never summarize a page into a "quote". Load tools: ToolSearch "select:WebSearch,WebFetch,mcp__remote-devices__Claude_Browser__tabs_create,mcp__remote-devices__Claude_Browser__navigate,mcp__remote-devices__Claude_Browser__javascript_tool,mcp__remote-devices__device_bash".

**For each org in the batch:**
1. Find its own pages: home/about, services or programs, staff/team, and (when `check_events` is true) its conference/event page and any call for speakers. Use WebSearch/WebFetch only to FIND the URLs. Prefer the org's own domain (`domains`). At most 4 pages per org.
   **Partner pages (discovery seeds, Chris 2026-11-04):** if any page you open lists OTHER organizations the org works with ("partners", "key organizations", "resources", "members", "coalition", "funders"), append ONE line per such page to `<ENG>/2_Discover/ledgers/partner-pages.jsonl` with device_bash (`cat >> FILE <<'EOF'` … `EOF`): {"url": "<that page>", "label": "<org name> — <page title>", "found_on": "<org_id>", "state": "<XX or null>", "date": "YYYY-MM-DD"}. Do not read the listed orgs yourself; discovery sweeps the page later. Never contact anyone.
2. CAPTURE each page in your own Browser-pane tab (tabs_create once, then navigate with that tabId): run the JavaScript printed by
   `python3 "<ENG>/3_Qualify/programfiles/qualify.py" js --url "<the URL you navigated to>"` and append the returned JSON object as ONE line to a file, then store it:
   `python3 "<ENG>/3_Qualify/programfiles/qualify.py" capture --run <RUN> <that file>`. (Write the file on the Mac with a quoted heredoc via device_bash.)
3. Answer every Must and every disqualifier of every `candidate_icps` entry with "yes" / "no" / "unknown". Every "yes" or "no" needs
   `url` (a captured page) and `quote`: text copied EXACTLY from that capture's `head` or `lines` (8+ characters; shorter is better than paraphrase).
   A quote that is not on the capture is thrown out and the answer becomes "unknown". If the capture doesn't show it, answer "unknown".
   Head Start grantees: the grantee list in the vault counts as evidence for "holds a grant" / "still funded": url
   `vault:Marketing/Lists/conference-pipeline/head-start-grantees/HS_Grantees_by_Size_2026-10-23.csv`, quote = the exact text of its row.
4. Events (only when `check_events`) — READ THE WHOLE CALENDAR (Rulebook E3, F6; Chris 2026-11-10). Open the org's events / conferences / calendar page and
   report EVERY upcoming event it runs itself (up to 6), not the first one you find, plus the most recent past edition of each. For each event give what the
   captured page says, each with its quote:
   name · url (the event's own page) · kind: "conference" (conference, convention, summit, symposium, institute, forum, annual meeting — in person or virtual) |
   "training" (training day, staff training, pre-service / in-service, training or PD series, course, webinar) | "unclear" (retreat, grantee / admin / outcomes
   meeting, gathering, expo, anything you cannot place) ·
   next_edition_date (YYYY-MM-DD, or YYYY-MM) + date_quote · last_edition_date + last_date_quote (the most recent edition's date) ·
   past_editions: every earlier edition date the site shows, e.g. ["2025-03-08", "2024-03-09"] (an archive or "past conferences" page) ·
   cadence "annual"|"biennial" ONLY if the page says so · attendance + attendance_quote (recorded, decides nothing) ·
   keynote_announced "yes" + keynote_announced_quote (ANY keynote, featured or headline speaker already named for the UPCOMING edition) or "no" when you
   opened the event's speakers / keynote / agenda / program page and none is named. FOR ANY EVENT LESS THAN 3 MONTHS AWAY YOU MUST OPEN that page (it does not
   count against the 4-page limit) and answer yes or no; leave it out only if no such page exists ·
   cfp {url, opens, deadline, status:"open"|"closed", quote} — any open call for speakers / proposals / speaker-submission form ·
   keynote_request {url, quote} (a published request for a keynote speaker) · dated_on_own_site yes|no · evidence_url.
   Do NOT decide whether the conference "brings in outside speakers", whether an event is too close, or which machine the org belongs to: you report what
   the pages say; the program applies the Rulebook.
   **Galas, benefits and fundraisers (judgement, Chris 2026-11-04):** a fundraiser is NOT ruled out by being a fundraiser — large, well-funded orgs run
   galas that pay keynote fees. Report it as an event only when BOTH show on the page: (a) the org has resources (a large multi-site/multi-program org,
   a regional or national body, sponsorship tiers, a large venue or stated attendance in the hundreds) AND (b) the format has room for a speaker
   (a program, keynote, featured or guest speaker, a multi-hour agenda). A small org's short reception-plus-program for donors (e.g. doors 5 PM,
   program 7 PM, storytelling, no speaker slot) is not a keynote opportunity: leave it out of `events` and say why in `note`. When unsure, include
   it as an event with a note starting "FUNDRAISER?" (the note travels with the decision so Chris can judge it).

**Output** — one JSON line per org, every org, in the result file path you were given:
{"org_id": "...", "pages_read": ["url", ...],
 "icps": {"ICP-00x": {"musts": [{"criterion": "<exact Must text>", "answer": "yes|no|unknown", "url": "...", "quote": "..."}],
                      "disqualifiers": [{"text": "<exact disqualifier text>", "hit": "yes|no|unknown", "url": "...", "quote": "..."}]}},
 "events": [ {...as above...} ], "note": "1 line"}
Validate with python that every line parses and every org_id in the batch is present. Final message: per org — pages captured · your answers in one line.
