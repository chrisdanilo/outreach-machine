---
title: People helper instructions (one batch file per helper) — Rulebook G, H
updated: 2026-10-31 (Stage 6)
---

# People helper (Sonnet)

You get ONE batch file (one org per line) and write ONE result file. You find people and copy what the page shows; the script checks
every address and decides who is emailed. Never contact anyone, never guess an address, never build one from a pattern
(first.last@…), never take an address from a third-party people-finder site. Load tools: ToolSearch
"select:WebSearch,WebFetch,mcp__remote-devices__Claude_Browser__tabs_create,mcp__remote-devices__Claude_Browser__navigate,mcp__remote-devices__Claude_Browser__javascript_tool,mcp__remote-devices__device_bash".

**For each org in the batch** (`machine` says who we write to; `role_order` is the preference order, best first):
0. **SITE SCAN first (Chris 2026-11-04).** Before choosing pages, map the org's own site: open the home page in your tab and list its menu/footer links, and
   fetch `/sitemap.xml` (and any sub-sitemaps) with the javascript tool (`await (await fetch('/sitemap.xml')).text()`). From that list pick every page that
   may name people or programs: staff / team / leadership / board / about, programs / services / departments (e.g. a CCR&R, Head Start or training
   department page), events, and contact. A department or program page often prints the person who runs it.
1. Read the org's OWN pages from the scan: every staff / team / leadership page, the program or department pages that fit the machine (PD, training,
   coaching, CCR&R, early childhood), the events page, "contact us", and for OM-2 the open event's page (`events[].url`) and any call-for-speakers /
   presenter page. Use WebSearch/WebFetch only to FIND URLs. At most 8 pages per org.
   - **G3:** search the FULL roster first (every staff/leadership page) before settling for a generic inbox.
   - **G4:** a generic inbox (info@, events@, …) may only be used when you did the site scan AND read the staff page AND the fitting
     program/department pages. List every named leader without an address in `named_without_email` — the script looks each of them up in
     Apollo (H7) and only falls back to a generic inbox if none resolves.
   - **Partner pages (discovery seeds, Chris 2026-11-04):** if any page you open lists OTHER organizations the org works with ("partners", "key organizations", "resources", "members", "coalition", "funders"), append ONE line per such page to `<ENG>/2_Discover/ledgers/partner-pages.jsonl` with device_bash (`cat >> FILE <<'EOF'` … `EOF`): {"url": "<that page>", "label": "<org name> — <page title>", "found_on": "<org_id>", "state": "<XX or null>", "date": "YYYY-MM-DD"}. Do not read the listed orgs yourself; discovery sweeps the page later. Never contact anyone.
2. CAPTURE each page in your own Browser-pane tab (tabs_create once, then navigate with that tabId), in two passes:
   a. SCAN: run the JavaScript printed by `python3 "<ENG>/4_People/programfiles/people.py" js --url "<URL>"` — it returns every address on the page
      (mailto links, protected addresses, text) and the lines near names and titles. Read it and choose people.
   b. VERIFY (this is what gets stored): run `python3 "<ENG>/4_People/programfiles/people.py" js --url "<URL>" --quotes '<JSON list of the exact lines you will quote>'`
      — the page itself confirms each quote and lists its addresses. Append the returned JSON as ONE line to a file on the Mac
      (quoted heredoc via device_bash), then `python3 "<ENG>/4_People/programfiles/people.py" capture --run <RUN> <that file>`.
   Store a capture for EVERY page you read, even one with no addresses (that is how the script knows the page was readable).
   A page that will not load (403, not allowed in the Browser pane, gone): list it in pages_read and say so in the note.
   An address that is not in a capture is thrown out.
3. Pick up to 6 candidates by ROLE (the script keeps the best 4):
   - OM-2: `cfp_contact` (named on the call-for-speakers/presenter page) → `event_contact` (named on the event page) →
     `event_dept_director` (director of the department that owns the event) → `executive_director` → `pd_director` …
   - OM-1: `executive_director` → `pd_director` (PD/training director) → `coaching_manager` → `program_director` → `other_leader` …
   Choose by what the person DOES (role), not by a title keyword. Use only people whose address the page prints.
4. For each person: name, role (title EXACTLY as printed), role_key (one of the keys above, or `other_staff`), email EXACTLY as printed,
   evidence_url (the captured page that prints the address), quote (the line from that capture's `lines` that shows the name and/or
   title, copied exactly). Generic event inbox printed on the event page: name null, `generic_event_inbox: true`.
5. `named_without_email`: EVERY named person in a leader or PD-relevant role (director, ED, PD/training, coaching, quality improvement, program
   manager, event lead) whose address is NOT printed (name + title), up to 8, best roles first. These go to the Apollo roster sweep (H7) and the greeting.

**`org_domain`** (Chris 2026-11-04): when the batch row's `domains` is empty, report the org's own site domain you confirmed (a captured page on it names the org). Without it the script cannot tell the org's own addresses from strangers' and rejects every address.

**Output** — one JSON line per org, every org, in the result file path you were given:
{"org_id": "...", "org_domain": "<the org's own site domain, e.g. athensmeigs.com — REQUIRED when the batch row has no `domains`>", "pages_read": ["url", ...], "staff_page_read": true|false, "roster_searched": true|false,
 "people": [{"name": "...", "role": "...", "role_key": "...", "email": "...", "evidence_url": "...", "quote": "...", "generic_event_inbox": false}],
 "named_without_email": [{"name": "...", "role": "..."}], "note": "1 line"}
Validate with python that every line parses and every org_id in the batch is present. Final message: per org — pages captured · people found (roles).
