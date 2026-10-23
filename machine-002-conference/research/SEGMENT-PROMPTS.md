---
business: Human Skills Training
title: Machine 002 — research prompts (one per segment), used by every event refresh
updated: 2026-10-22
---

# Research prompts — one research agent per segment

The refresh launches one research agent per segment below, all at once, each with model **Sonnet**. Every agent gets the **common block** + its **segment block** + its **re-check list** (the events it already owns, from `python3 bin/events.py worklist --segment <name>`).

Edit these to change what the refresh looks for. The scripts don't read this file; the refresh session does.

---

## Common block (goes first in every agent's prompt)

> You are refreshing part of an EVENT DATABASE for Human Skills Training (Chris Danilo). Chris sells "The Human Conference Design": he co-designs and MCs an organization's own annual early-childhood conference (opening + closing keynote, breakouts, follow-ups) for a $6,000 flat fee. The buyer is an organization that OWNS and RUNS a recurring event for an adult early-childhood workforce audience. Today is {TODAY}.
>
> Read `SCHEMA.md` (path given below) first: it is the exact record format and the hard rules (never fabricate; every fact needs a source URL; never guess emails).
>
> Do four things:
> 1. **RE-CHECK every event in your re-check list.** Open its event page. Has a 2027 date been posted? (Then status "confirmed", with the URL.) Has a newer past edition appeared? Is a call for presenters / proposals / keynotes / RFP open, and what is the deadline? Has the person in charge changed? Write one row per re-checked event, even if nothing changed. Keep `event_name` and `organization` EXACTLY as given, so the merge matches it.
> 2. **FILL GAPS** on re-checked events: if person in charge, date, event page or keynote evidence is missing, search specifically for that piece.
> 3. **FIND NEW events** in your segment that are not in the re-check list (searches below).
> 4. Write all rows to the output file given, one valid JSON object per line.
>
> 🔴 **SEARCH BUDGET (learned 2026-10-22):** one run gets **200 WebSearch calls in total, shared by every agent in it**. The first build ran out halfway with 9 agents searching freely. So: **re-check events by opening their known event_url with WebFetch, never by searching** (WebFetch does not use the search budget). Spend searches only on finding NEW events and on gaps a fetch can't fill. Your share is **{SEARCH_SHARE} searches**: stop searching at that number and say so.
>
> Use WebSearch (mode "standard"; "extended" only when standard is thin) and WebFetch to confirm. On HTTP 429, wait and retry later instead of skipping. Reply with: rows written; searches used; counts by date status; every open call (event, deadline, url); and what you could not reach.

## Segment blocks

### headstart_assoc
All state Head Start associations (~51 incl. DC/PR), all regional associations (Regions I–XII incl. XI AIAN and XII Migrant & Seasonal), Head Start WEST, NHSA national events (note them as national flagships). One row per event: many associations run several (annual, health institute, directors' institute).
Starting files: `Marketing/Lists/conference-pipeline/Head-Start-Conference-Master-List.md`, `Research/Head-Start-Market-National-Report-2026-10-10.md`.

### headstart_grantees
Head Start / Early Head Start grantee agencies that run their own pre-service week, in-service day, all-staff rally or staff institute with an outside keynote (mostly July–August). Evidence is usually agency news posts and local TV/newspaper stories, not event pages. Best queries (2026-10-22): "Head Start pre-service week keynote speaker {YEAR}", "Head Start \"pre-service\" staff keynote August {YEAR} community action agency", "Head Start staff kickoff school year keynote employees gathered {YEAR}", "Head Start \"Back to School Rally\" OR \"convocation\" staff keynote", "Head Start teachers receive back-to-school training". Strongest season to re-search: July–September, when the stories are published.

### aeyc
NAEYC state affiliates and local chapters that run an annual conference, institute or summit; Southern Early Childhood Association (SECA) and its state affiliates. Sources: NAEYC affiliate directory https://my.naeyc.org/s/searchdirectory?id=a2FWQ0000020Yuz2AE and affiliate events calendar https://app.smartsheet.com/b/publish?EQBCT=ec55eecdcb904f5d954133c9812a2c2e. Exclude NAEYC's own national conference (franchise_network segment has it).

### ccrr_ne / ccrr_south / ccrr_mw_west
CCR&Rs, Child Care Aware state networks and affiliates, statewide CCR&R networks; plus Smart Start partnerships and Florida Early Learning Coalitions (south); Colorado Early Childhood Councils and California First 5 / R&R agencies (mw_west). States — ne: ME NH VT MA RI CT NY NJ PA DE MD DC VA WV · south: NC SC GA FL AL MS TN KY LA AR TX OK · mw_west: everything else. Known agency list: Machine 001's `outreach-machine/territory.json` (agencies by state, with website domain). Search per state, check statewide networks and larger agencies directly.

### state_system
State-agency ECE conferences (state early learning offices, QRIS, workforce registries, PDG B-5 summits — mark `procurement: rfp` where speakers are bought by bid); state-system intermediaries (PA ELRCs, VA Ready Regions, MI Great Start, IA ECI, OR Early Learning Hubs, IL Gateways/[Org 0730]…); Texas Workforce Solutions boards' child care conferences; education service agencies (TX ESCs, NY BOCES, PA IUs, OH ESCs, MI ISDs, IA AEAs, Sourcewell); university / community-college ECE conferences open to the workforce.

### trade_assoc
State child care / licensed-provider associations; family child care associations (NAFCC state affiliates); state Montessori and faith-based preschool associations; infant mental health associations; Early Intervention / Part C and DEC state conferences; home-visiting / Parents as Teachers state conferences; afterschool networks only where child care staff are a main audience.

### franchise_network
Franchise & corporate child care operators (25+ sites): franchisee conventions, leadership summits, all-staff training days. Large nonprofit networks (YMCA child care, Educare, Catholic Charities, JCC, military child care, tribal CCDF). National ECE orgs' own conferences (for completeness; keynotes usually curated in-house). Canada: provincial ECE associations.
