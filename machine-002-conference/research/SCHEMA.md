---
business: Human Skills Training
type: reference
tags: [outreach-machine-002, conference, schema]
title: Machine 002 — event record schema (JSONL), used by every event refresh
---

# Event record schema — Machine 002 event database (one JSON object per line)

Write ONE JSON object per line (JSONL). Use null for anything you could not find. NEVER guess.

{
  "event_name": "Official name of the event as the organizer writes it",
  "organization": "Organization that OWNS and RUNS the event",
  "org_type": one of ["head_start_state_assoc","head_start_regional_assoc","head_start_grantee","aeyc_affiliate","ccrr_or_cca","state_system_intermediary","state_agency","education_service_agency","workforce_board","trade_or_provider_assoc","family_child_care_assoc","franchise_or_corporate","nonprofit_network","university_or_college","infant_mental_health_or_ei","afterschool_school_age","national_org","canada","other"],
  "country": "US" or "CA",
  "state": "2-letter state/province code, or MULTI",
  "city": "city or null",
  "event_url": "the event's own page (organizer's site). Required.",
  "org_url": "organizer home page",
  "audience": "who attends, short",
  "attendance": {"value": "number or range as stated", "source_url": "..."} or null,

  "date_2027": {"start": "YYYY-MM-DD or null", "end": "YYYY-MM-DD or null", "month": "YYYY-MM or null",
                "status": "confirmed" | "estimated" | "unknown",
                "source_url": "page that shows the 2027 date (confirmed) or the past date it was estimated from",
                "note": "e.g. 'estimated from 2026 edition held Mar 12-13, 2026'"},
     RULES: "confirmed" = a 2027 date is printed on the ORGANIZER's own page (or an official save-the-date).
            "estimated" = no 2027 date, but you found a DATED past edition (2026, or 2025 if 2026 not found);
                          month = same month in 2027. If the event alternates years (biennial) say so in note.
            "unknown" = you could not find any dated edition. month = null.
            A Nov/Dec 2026 edition still counts: estimate the 2027 edition as the same month in 2027.

  "last_held": {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD or null", "source_url": "..."} or null,

  "owner": {"name": "...", "title": "...", "email": "ONLY if published on the org's own site, else null",
            "source_url": "page where you saw this person tied to the event or to PD/training/events"} or null,
     RULES: prefer the person named as conference chair / events / PD / training lead; else the Executive Director.
            Never construct or pattern-guess an email.

  "call_for_proposals": {"status": "open" | "upcoming" | "closed" | "not_found",
                         "type": "presenters" | "keynote" | "rfp" | "sponsors_exhibitors" | null,
                         "deadline": "YYYY-MM-DD or null", "url": "..." } ,
     "open" = currently accepting (deadline in the future as of 2026-10-22). Only mark open with a URL.

  "keynote_slot": "yes" | "no" | "unknown",   "yes" = past program shows an external keynote speaker
  "keynote_evidence_url": "..." or null,
  "last_keynote": {"name": "...", "source_url": "..."} or null,
  "procurement": "direct" | "rfp" | "unknown",   "rfp" only if a formal bid/RFP is the documented route for speakers
  "sources": ["every URL you used"],
  "notes": "anything Chris should know, short, factual"
}

Hard rules:
- Never fabricate. Every date, owner and keynote claim needs a source_url you actually opened or saw in a search result from the organizer's own domain.
- Prefer the organizer's own domain over third-party listing sites. If only third-party evidence exists, still record it but say so in notes.
- One row per EVENT. If one org runs 3 events, write 3 rows.
- Only events for an ADULT early-childhood workforce audience (teachers, directors, providers, coaches, home visitors, Head Start staff, family child care). Skip events aimed at parents only, or vendor trade shows.
- Do NOT skip Colorado; just record it.
