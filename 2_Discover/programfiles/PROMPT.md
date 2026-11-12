---
title: Discovery helper instructions (one batch file per helper) — Rulebook D
updated: 2026-11-11 (Firecrawl first — _shared/WEB-TOOLS.md); 2026-10-31 (Stage 4; adapted from Machine 2's sweep prompts)
---

# Discovery helper

You get ONE batch file (one JSON source row per line) and write ONE result file. Load tools first: ToolSearch "select:mcp__Firecrawl__firecrawl_search,mcp__Firecrawl__firecrawl_scrape,WebSearch,WebFetch".
**WEB TOOLS (Chris 2026-11-11): Firecrawl first.** Read and follow "<ENG>/_shared/WEB-TOOLS.md" for every search and every page read: Firecrawl first, then WebSearch / WebFetch / your Browser-pane tab as fallback; never Firecrawl's agent or people/company tools. A Firecrawl search counts against SEARCHES ALLOWED and is logged in `searches` like any search.
Never contact anyone, never guess an email, never fabricate. Every find needs the URL of the page where you saw it.

**Who we look for** (only these — each source row lists the ICPs it serves in `icps`):
- ICP-001 CCR&Rs and Child Care Aware affiliates — trains, coaches or refers child-care providers in a set area.
- ICP-002 Other ECE intermediaries — supports ECE providers or the workforce without running centers itself (state/county ECE units, shared services, PD registries, education service agencies, workforce boards).
- ICP-003 Head Start / Early Head Start grantees — holds a federal Head Start or EHS grant and runs programs.
- ICP-004 ECE associations and networks — a membership or network body for ECE professionals (AEYC affiliates, Head Start associations, family child care associations, statewide networks).
- ICP-005 Early learning center owners/directors — owns or runs an early learning center (only list these when a row asks for ICP-005).
- ICP-006 ECE-adjacent event owners — main mission is outside early childhood, but runs its own recurring conference/institute/strand whose stated audience is early-childhood educators, providers or leaders (higher-ed EC conferences, infant mental health associations, school associations with an EC strand, unions/special-ed bodies with an EC conference). NOT library associations, state nonprofit associations, diocese school offices, independent-school associations without an EC strand, or curriculum/product vendors.
US + Canada. Colorado: still list (the master list excludes it), but never spend searches on Colorado.

**By row `type`:**
- keynoter — open the speaker's speaking / past-events page. List every conference they spoke at or are booked for whose organizer fits an ICP above. Add every OTHER keynote/featured speaker named on those event pages to `keynoters` (name + site). Speakers are never finds.
- calendar / venue — read the listing; list every organizer of a fitting event; add other calendars it links to as `new_sources`.
- hs_region — the association's events page and member/program directory: its own conferences and every member program that runs a training conference or pre-service/all-staff day.
- directory (`region` = state/province, `org_type`) and state_directory — find that kind of organization in that state/province (national umbrella directories first: NAEYC affiliates, NHSA state associations, Child Care Aware state network, Alliance for the Advancement of IMH, NAFCC, state agency lists, the state's CCR&R lead-agency list) and list every one that fits an ICP (events optional for ICP-001/002/003; required for ICP-006). Searches come ONLY from your batch's allowance (SEARCHES ALLOWED, given to you with the batch; 0 = no searches): open the national umbrella directory pages by URL first (no search needed).
- branch — open the event page `url`; read its sponsors, exhibitors, partners, planning committee and keynote/speaker pages, and the organizer's parent/partner/member orgs. List every organization there that fits an ICP; add speakers to `keynoters`.
- partners — a page on an org's own site that lists the organizations it works with (partners, "key organizations", resources, members, coalition).
  Open `url`; list every listed organization that fits an ICP above, with its own site. No searches needed; follow the page's links.
- list (Chris 2026-11-06) — a national or umbrella page that lists many organizations of one kind (e.g. NAFCC affiliates, NAEYC affiliates, NHSA state associations, the IMH Alliance members). Open `url` with firecrawl_scrape (fallback WebFetch); if the list does not appear (it is drawn by JavaScript), open it in the built-in browser (ToolSearch "mcp__remote-devices__Claude_Browser__", your OWN tab: tabs_create once, close it when done) and read it there. List EVERY organization on it that fits the row's ICPs, each with its own site as linked on the page (if the page gives names only, open the org's site from the name only when you can do so without a search; otherwise list it with domain null). No searches unless your batch has an allowance.
- search — web search fallback for the ICP in the row (its function test and "where to find them" are in the row). Before EVERY search run:  python3 "<ENG>/2_Discover/programfiles/discover.py" checkq --q "<your query>"  and skip it if it prints REPEAT. Stay within YOUR BATCH's allowance (SEARCHES ALLOWED); a result that logs more searches than its allowance is rejected whole. List what you find.
Check `known-domains.txt` in the run folder: an org already there is still worth listing ONLY if you found a new event or a named person with a published email; otherwise skip it.

**Output** — one JSON line per batch row, every row, in the result file path you were given:
{"id": "<row id>", "status": "swept"|"not_found", "note": "what you looked at (1 line)",
 "finds": [{"organization": "...", "domain": "org.org"|null, "org_url": url|null, "state": "TX"|null, "country": "US"|"CA",
            "icps": ["ICP-00x"], "icp_why": "1 line: which function test it passes",
            "evidence_url": "page where you saw this org",
            "events": [{"name", "url", "last_edition_date", "next_edition_date", "cadence": "annual"|"biennial"|null, "attendance", "cfp": {"url","opens","deadline","status"}, "keynote_announced": "yes"|null, "evidence_url"}],
            "people": [{"name", "role", "email": "only if printed on the page, else null", "evidence_url"}],
            "note": null}],
 "keynoters": [{"name", "site", "speaking_url", "focus", "found_on"}],
 "new_sources": [{"type": "calendar"|"venue"|"directory"|"partners", "label", "url", "region"}],
 "searches": [{"q": "exact query you ran", "domains_seen": ["..."]}]}
Events: a gala/benefit/fundraiser counts only when the org clearly has resources AND the format has a speaker slot (same rule as the qualify prompt);
a small org's short donor reception is not an event for us. Any page you read that lists partner organizations → add it to `new_sources` as type "partners".
Use null for anything not on the page (dates as YYYY-MM-DD or YYYY-MM when only the month is printed). Validate with python that every line parses and every row id is present. Final message: per row — finds · keynoters added · new sources · searches run; then the one Firecrawl line (WEB-TOOLS.md §5).
