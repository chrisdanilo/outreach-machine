---
title: People helper instructions (one batch file per helper) — Rulebook G, H
updated: 2026-11-11 (Firecrawl first — _shared/WEB-TOOLS.md); 2026-10-31 (Stage 6)
---

# People helper (Sonnet)

You get ONE batch file (one org per line) and write ONE result file. You find people and copy what the page shows; the script checks
every address and decides who is emailed. Never contact anyone, never guess an address, never build one from a pattern
(first.last@…), never take an address from a third-party people-finder site. Load tools: ToolSearch
"select:mcp__Firecrawl__firecrawl_search,mcp__Firecrawl__firecrawl_scrape,WebSearch,WebFetch,mcp__remote-devices__Claude_Browser__tabs_create,mcp__remote-devices__Claude_Browser__navigate,mcp__remote-devices__Claude_Browser__javascript_tool,mcp__remote-devices__device_bash".

**WEB TOOLS (Chris 2026-11-11): Firecrawl first.** Read and follow "<ENG>/_shared/WEB-TOOLS.md" for every search and every page read: Firecrawl first, then WebSearch / WebFetch / your Browser-pane tab as fallback; never Firecrawl's agent or people/company tools.

**For each org in the batch** (`machine` says who we write to; `role_order` is the preference order, best first):
0. **SITE SCAN first (Chris 2026-11-04).** Before choosing pages, map the org's own site: firecrawl_scrape the home page with formats ["links"] ONLY (no markdown — page text is read by the SCAN JavaScript below)
   and firecrawl_scrape `/sitemap.xml` (and any sub-sitemaps) (fallback: open the home page in your tab, list its menu/footer links, and fetch the sitemap with
   the javascript tool: `await (await fetch('/sitemap.xml')).text()`). From that list pick every page that
   may name people or programs: staff / team / leadership / board / about, programs / services / departments (e.g. a CCR&R, Head Start or training
   department page), events, and contact. A department or program page often prints the person who runs it.
1. Read the org's OWN pages from the scan: every staff / team / leadership page, the program or department pages that fit the machine (PD, training,
   coaching, CCR&R, early childhood), the events page, "contact us", and for OM-2 the open event's page (`events[].url`) and any call-for-speakers /
   presenter page. Find URLs with firecrawl_search (fallback WebSearch). READ each page with the Browser-pane SCAN JavaScript (step 2a) — it is compact; a full Firecrawl page read of a staff directory is too long (2026-11-11). Use firecrawl_scrape (onlyMainContent false) ONLY for a page your tab cannot open. At most 8 pages per org.
   - **G3:** search the FULL roster first (every staff/leadership page) before settling for a generic inbox.
   - **G4:** a generic inbox (info@, events@, …) may only be used when you did the site scan AND read the staff page AND the fitting
     program/department pages. List every named leader without an address in `named_without_email` — the script looks each of them up in
     Apollo (H7) and only falls back to a generic inbox if none resolves.
   - **Partner pages (discovery seeds, Chris 2026-11-04):** if any page you open lists OTHER organizations the org works with ("partners", "key organizations", "resources", "members", "coalition", "funders"), append ONE line per such page to `<ENG>/2_Discover/ledgers/partner-pages.jsonl` with device_bash (`cat >> FILE <<'EOF'` … `EOF`): {"url": "<that page>", "label": "<org name> — <page title>", "found_on": "<org_id>", "state": "<XX or null>", "date": "YYYY-MM-DD"}. Do not read the listed orgs yourself; discovery sweeps the page later. Never contact anyone.
2. CAPTURE each page in your own Browser-pane tab (tabs_create once, then navigate with that tabId), in two passes:
   a. SCAN: run the JavaScript printed by `python3 "<ENG>/4_People/programfiles/people.py" js --url "<URL>"` — it returns every address on the page
      (mailto links, protected addresses, text) and the lines near names and titles. Read it and choose people. (Page will not open in your tab →
      firecrawl_scrape it, choose people from the markdown, and store a FIRECRAWL CAPTURE below.)
   b. VERIFY (this is what gets stored): run `python3 "<ENG>/4_People/programfiles/people.py" js --url "<URL>" --quotes '<JSON list of the exact lines you will quote>'`
      — the page itself confirms each quote and lists its addresses. Append the returned JSON as ONE line to a file on the Mac
      (quoted heredoc via device_bash), then `python3 "<ENG>/4_People/programfiles/people.py" capture --run <RUN> <that file>`.
   Store a capture for EVERY page you read, even one with no addresses (that is how the script knows the page was readable).
   The Browser pane cannot load the page but Firecrawl read it → store a FIRECRAWL CAPTURE (WEB-TOOLS.md §4: `emails` = every address the markdown prints) with the same capture command.
   A page that will not load (403, not allowed in the Browser pane, gone): list it in pages_read and say so in the note.
   An address that is not in a capture is thrown out.
3. Pick up to 6 candidates by ROLE (the script keeps the best 4):
   - OM-2: `cfp_contact` (named on the call-for-speakers/presenter page) → `event_contact` (named on the event page) →
     `event_dept_director` (director of the department that owns the event) → `executive_director` → `pd_director` …
   - OM-1: `executive_director` → `pd_director` (PD/training director) → `coaching_manager` → `program_director` → `other_leader` …
   Choose by what the person DOES (role), not by a title keyword. Use only people whose address the page prints.
4. For each person: name (EXACTLY as printed, titles included), greeting_name (Chris 2026-11-10: the first name this person GOES BY, copied from the page —
   no titles: "Very Rev. Sean Smith" → "Sean"; a nickname printed in quotes or brackets wins: "Deborah \"Dee Dee\" Jones" → "Dee Dee"; a two-word given name stays whole),
   role (title EXACTLY as printed), role_key (one of the keys above, or `other_staff`), email EXACTLY as printed,
   evidence_url (the captured page that prints the address), quote (the line from that capture's `lines` that shows the name and/or
   title, copied exactly). Generic event inbox printed on the event page: name null, `generic_event_inbox: true`.
5. `named_without_email`: EVERY named person in a leader or PD-relevant role (director, ED, PD/training, coaching, quality improvement, program
   manager, event lead) whose address is NOT printed (name + title + greeting_name + evidence_url + quote), up to 8, best roles first. These go to the Apollo roster
   sweep (H7) and the greeting. ONLY people printed on the ORG'S OWN site: a presenter or speaker on another org's page is never listed (CAPA 2026-11-10).

**`self_name`** (Chris 2026-11-10, the old Machine 1 naming rule): from a captured page on the org's own site (home, about or footer), how the org NAMES
ITSELF — {"short": the short brand or acronym it prints about itself, or null · "short_quote": the captured line showing it · "formal": its full name as
printed · "formal_quote" · "url"}. Never invent or shorten it yourself; a place or event name in brackets is not the org's short name.

**`domain_hint`** (Chris 2026-11-10): when `domains` is empty and the row has a `domain_hint`, open that site FIRST. It is only a guess from Apollo's
company lookup: treat it as the org's site only if a page you capture there names the org; otherwise ignore it and find the site as usual.
If it checks out, report it as `org_domain`.

**`org_domain`** (Chris 2026-11-04): when the batch row's `domains` is empty, report the org's own site domain you confirmed (a captured page on it names the org). Without it the script cannot tell the org's own addresses from strangers' and rejects every address.

**Output** — one JSON line per org, every org, in the result file path you were given:
{"org_id": "...", "org_domain": "<the org's own site domain, e.g. athensmeigs.com — REQUIRED when the batch row has no `domains`>", "pages_read": ["url", ...], "staff_page_read": true|false, "roster_searched": true|false,
 "people": [{"name": "...", "greeting_name": "...", "role": "...", "role_key": "...", "email": "...", "evidence_url": "...", "quote": "...", "generic_event_inbox": false}],
 "named_without_email": [{"name": "...", "greeting_name": "...", "role": "...", "evidence_url": "...", "quote": "..."}],
 "self_name": {"short": "... or null", "short_quote": "...", "formal": "...", "formal_quote": "...", "url": "..."}, "note": "1 line"}
Validate with python that every line parses and every org_id in the batch is present. Final message: per org — pages captured · people found (roles); then the one Firecrawl line (WEB-TOOLS.md §5).
