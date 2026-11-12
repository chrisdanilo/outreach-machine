#!/usr/bin/env python3
"""Stage 6 tests: find + verify people (Rulebook C2, C4, G1-G7, H1-H6). Run: python3 test_people.py"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import people as P

ORG = {"org_id": "org:x.org", "name": "Example Org", "domains": ["x.org"]}
def cap(url, emails, lines=("[Person 0811], Executive Director",), chars=2000, title="Staff"):
    return {P.uid(url): {"url": url, "chars": chars, "title": title, "emails": list(emails), "lines": list(lines)}}
def person(name, email, role_key="other_staff", url="https://x.org/staff", **k):
    return dict({"name": name, "email": email, "role_key": role_key, "role": role_key, "evidence_url": url, "quote": name}, **k)
def ingested(p, caps, status=None, thread_dom=None, excl_dom=None, gstate=None):
    ok, why = P.provenance(p, ORG, caps, gstate or {})
    e = P.em(p.get("email")); drop = None
    if ok:
        d = P.dom(e)
        if (status or {}).get(e) in ("bounced", "departed", "do_not_contact"): drop = "status"
        elif d in (excl_dom or {}) and excl_dom[d][0] != ORG["org_id"]: drop = "client domain"
        elif d in (thread_dom or {}) and thread_dom[d] != ORG["org_id"]: drop = "other org thread"
    return dict(p, email=e, generic=P.is_generic(e, p.get("generic")), generic_event_inbox=bool(p.get("generic_event_inbox")),
                gate1="pass" if ok else "fail", gate1_why=why, dropped=drop, source=p.get("source", "page"))
def ap(*emails, validity="valid", identity="confirmed"): return {e: {"identity": identity, "validity": validity} for e in emails}

R = []
def t(name, cond): R.append((name, bool(cond))); print(("PASS " if cond else "FAIL ") + name)

U = "https://x.org/staff"
# 1 ceiling: 6 named -> 1 To + 3 Cc
es = ["person0004@x.org" % i for i in range(6)]
caps = cap(U, es)
ppl = [ingested(person("Name%d Last" % i, e, "executive_director" if i == 3 else "other_staff"), caps) for i, e in enumerate(es)]
r = P.assemble("Example Org", "OM-1", ppl, ap(*es), True, True)
t("ceiling: 6 named people -> 1 To + 3 Cc (4 total)", r["decision"] == "ready" and 1 + len(r["cc"]) == 4)
t("role order: executive director is the To for OM-1", r["to"]["email"] == "person0005@x.org")
t("greeting names every named recipient, no pronouns", r["greeting"].startswith("Hi Name3") and r["greeting"].count(",") >= 2 and " he " not in r["greeting"] and " she " not in r["greeting"])
# 2 OM-2 role order: cfp contact beats ED
caps = cap(U, ["person0901@x.org", "person0447@x.org"])
ppl = [ingested(person("Ed Director", "person0901@x.org", "executive_director"), caps), ingested(person("Cara Call", "person0447@x.org", "cfp_contact"), caps)]
r = P.assemble("Example Org", "OM-2", ppl, ap("person0901@x.org", "person0447@x.org"), True, True)
t("OM-2: call-for-speakers contact is the To", r["to"]["email"] == "person0447@x.org")
# 3 generic inbox rule (G4)
caps = cap(U, ["info@x.org"])
ppl = [ingested(person(None, "info@x.org"), caps)]
r = P.assemble("Example Org", "OM-1", ppl, ap("info@x.org"), False, False)
t("generic inbox only + staff page NOT read -> hold (G4)", r["decision"] == "hold" and "G4" in r["hold_reason"])
r = P.assemble("Example Org", "OM-1", ppl, ap("info@x.org"), True, False)
t("generic inbox only + staff page read but roster not searched -> hold (G3)", r["decision"] == "hold" and "G3" in r["hold_reason"])
r = P.assemble("Example Org", "OM-1", ppl, ap("info@x.org"), True, True)
t("generic inbox only + staff page read + roster searched -> ready, 'Hi <Org> team,'", r["decision"] == "ready" and r["greeting"] == "Hi Example Org team,")
r = P.assemble("Example Org", "OM-1", ppl, ap("info@x.org"), True, True, [{"name": "Pat Lee"}])
t("generic inbox with a named person (no address) -> 'Hi [Person 1490] and team,'", r["greeting"] == "Hi [Person 1490] and team,")
# 4 generic event inbox as Cc when room
caps = cap(U, ["person1356@x.org", "conference@x.org"])
ppl = [ingested(person("Jo Smith", "person1356@x.org", "event_contact"), caps), ingested(person(None, "conference@x.org", generic_event_inbox=True), caps)]
r = P.assemble("Example Org", "OM-2", ppl, ap("person1356@x.org", "conference@x.org"), True, True)
t("generic event inbox printed on the event page -> Cc when there is room", r["to"]["email"] == "person1356@x.org" and [c["email"] for c in r["cc"]] == ["conference@x.org"])
# 5 provenance mismatch -> not used
caps = cap(U, ["person1200@x.org"])
p = ingested(person("[Person 0811]", "person1253@x.org"), caps)
t("provenance: address not on the captured page -> gate 1 fails", p["gate1"] == "fail" and "character match" in p["gate1_why"])
r = P.assemble("Example Org", "OM-1", [p], {}, True, True)
t("provenance mismatch only -> hold", r["decision"] == "hold")
p = ingested(person("[Person 0811]", "person1200@x.org", url="https://x.org/other"), caps)
t("provenance: evidence page not captured -> fail (no guessing)", p["gate1"] == "fail" and "not captured" in p["gate1_why"])
p = ingested(person("[Person 0811]", "person1200@x.org"), caps)
t("provenance: case-insensitive character match passes", p["gate1"] == "pass")
# 6 invalid -> hold; catch-all -> proceed flagged; unknown -> proceed flagged; departed -> dropped
caps = cap(U, ["person1200@x.org"]); p = ingested(person("[Person 0811]", "person1200@x.org"), caps)
r = P.assemble("Example Org", "OM-1", [p], ap("person1200@x.org", validity="invalid"), True, True)
t("printed address, definite invalid -> still used, flagged (Chris 2026-11-09 supersedes the old hold)", r["decision"] == "ready" and any("sent anyway" in f for f in r["flags"]))
r = P.assemble("Example Org", "OM-1", [p], ap("person1200@x.org", validity="catch_all"), True, True)
t("catch-all -> proceeds, flagged", r["decision"] == "ready" and any("catch_all" in f for f in r["flags"]))
r = P.assemble("Example Org", "OM-1", [p], ap("person1200@x.org", validity="unknown", identity="not_in_apollo"), True, True)
t("unknown + not in Apollo -> proceeds, both flagged", r["decision"] == "ready" and any("unknown" in f for f in r["flags"]) and any("not in Apollo" in f for f in r["flags"]))
r = P.assemble("Example Org", "OM-1", [p], ap("person1200@x.org", identity="departed"), True, True)
t("Apollo says departed -> not added, ⚠", r["decision"] == "hold" and any("left" in f for f in r["flags"]))
r = P.assemble("Example Org", "OM-1", [p], {}, True, True)
t("not yet checked in Apollo -> hold until checked", r["decision"] == "hold" and "Apollo" in r["hold_reason"])
# 7 recipient-domain client exclusion (C4)
caps = cap(U, ["person1575@client.org"]); p = ingested(person("Kim Ray", "person1575@client.org"), caps, excl_dom={"client.org": ("org:client.org", ["existing_client"])})
t("recipient domain belongs to an existing client -> dropped (C4)", p["dropped"] == "client domain")
# 8 one thread per org
caps = cap(U, ["person1722@other.org"]); p = ingested(person("Lee Park", "person1722@other.org"), caps, thread_dom={"other.org": "org:other.org"})
t("recipient domain belongs to another org with a thread -> dropped (C2)", p["dropped"] == "other org thread")
# 9 bounced / DNC address anywhere -> dropped
caps = cap(U, ["person2459@x.org"]); p = ingested(person("Sam Fox", "person2459@x.org"), caps, status={"person2459@x.org": "bounced"})
t("address bounced elsewhere in the master list -> dropped", p["dropped"] == "status")
# 10 Colorado never eligible
o = {"org_id": "org:co", "name": "CO Org", "state": "CO", "domains": ["co.org"], "fit": {"status": "fit"}, "owner_machine": "OM-1", "threads": [], "exclusions": {}}
t("Colorado org is never eligible (C5)", not P.eligible(o))
o2 = dict(o, state="NC"); t("same org outside Colorado is eligible", P.eligible(o2))
t("org with a thread is never eligible (people only for orgs without a thread)", not P.eligible(dict(o2, threads=[{"thread_id": "1"}])))
t("OM-2 org with outreach not open is not eligible (Rulebook F)", not P.eligible(dict(o2, owner_machine="OM-2", outreach={"status": "queued_until 2027-01-01"})))
t("OM-2 org with outreach open now is eligible", P.eligible(dict(o2, owner_machine="OM-2", outreach={"status": "open_now"})))
t("excluded org is never eligible", not P.eligible(dict(o2, exclusions={"existing_client": {"why": "x"}})))
# 11 H6: auto-reply provenance
gs = {"threads": {"t1": {"auto": [{"body": "I have retired. Please contact Ann Lee at person0210@x.org"}]}}}
p = ingested(person("Ann Lee", "person0210@x.org", source="autoreply", thread_id="t1", url=None), {}, gstate=gs)
t("H6: address from the org's own auto-reply counts as provenance", p["gate1"] == "pass")
p = ingested(person("Ann Lee", "person0211@y.org", source="autoreply", thread_id="t1", url=None), {}, gstate=gs)
t("H6: auto-reply address must be on the org's own domain and in that auto-reply", p["gate1"] == "fail")
# 12 doubtful fit flagged, duplicates collapsed, no address -> hold
caps = cap(U, ["person0008@x.org"]); p = ingested(person("Al Bee", "person0008@x.org"), caps)
r = P.assemble("Example Org", "OM-1", [p, dict(p)], ap("person0008@x.org"), True, True, fit="doubtful")
t("doubtful fit -> ready but ⚠ flagged (E2); same address twice counted once", r["decision"] == "ready" and not r["cc"] and any("doubtful" in f for f in r["flags"]))
r = P.assemble("Example Org", "OM-1", [], {}, True, True)
t("nobody found -> hold with an unblock step", r["decision"] == "hold" and r["unblock"])
t("generic local parts recognised", P.is_generic("events@x.org") and P.is_generic("info@x.org") and not P.is_generic("person1200@x.org"))
caps = cap(U, ["person0008@x.org", "person0305@x.org"]); pa = ingested(person("Al Bee", "person0008@x.org"), caps); pb = ingested(person("Bo Cee", "person0305@x.org"), caps)
r = P.assemble("Example Org", "OM-1", [pa, pb], ap("person0008@x.org"), True, True)
t("one person not yet checked in Apollo -> whole org waits (no partial recipient set)", r["decision"] == "hold" and "Apollo" in r["hold_reason"])
r = P.assemble("Example Org", "OM-1", [pa, pb], ap("person0008@x.org", "person0305@x.org"), True, True, [], "fit")
t("all checked -> To + Cc, greeting names both", r["decision"] == "ready" and r["greeting"] == "Hi Al and Bo,")
nw = P.assemble("Example Org", "OM-1", [ingested(person(None, "info@x.org"), cap(U, ["info@x.org"]))], ap("info@x.org"), True, True, [{"name": "EMILY F."}, {"name": "Leslie Scrivner"}])
t("generic To greeting names every named person, title-cased", nw["greeting"] == "Hi [Person 0654], Leslie and team,")
# 13 H7 roster sweep (Chris 2026-11-02, CAPA apollo-roster-sweep)
pend = {"org_id": "org:x.org", "name": "Example Org", "machine": "OM-1", "fit": "fit", "staff_page_read": True, "roster_searched": True, "pages_read": [U],
        "people": [ingested(person(None, "info@x.org"), cap(U, ["info@x.org"]))],
        "named_without_email": [{"name": "Curt Holder", "role": "SVP Child Development & Youth Services"}, {"name": "Pat Admin", "role": "Receptionist"},
                                {"name": "A One", "role": "Director of Training"}, {"name": "B Two", "role": "Program Manager"}, {"name": "C Three", "role": "Board Member"},
                                {"name": "D Four", "role": "Volunteer"}, {"name": "E Five", "role": "Intern"}]}
pick, deferred = P.relevant_unpublished(pend, "OM-1")
_cap = min(7, P.SWEEP_MAX)   # fixture has 7 unpublished; cap = settings people.sweep_max_per_org (8 since 2026-11-04)
t("H7: named people without a published address produce sweep items, ≤cap, most relevant roles first", len(pick) == _cap and len(deferred) == 7 - _cap and pick[0]["name"] in ("Curt Holder", "A One"))
t("H7: role words are mapped to the machine's role ranking", P.guess_role_key("Director of Professional Development") == "pd_director" and P.guess_role_key("Executive Director") == "executive_director" and P.guess_role_key("Receptionist") == "other_staff")
ok, res, why, val = P.sweep_verdict({"found": True, "email": "person0692@x.org", "email_status": "verified", "zerobounce": "valid"}, ["x.org"])
t("H7: Apollo Verified + ZeroBounce valid + org domain -> resolved (promoted)", ok and res == "resolved")
ok, res, why, val = P.sweep_verdict({"found": True, "email": "person0692@x.org", "email_status": "extrapolated", "zerobounce": "valid"}, ["x.org"])
t("H7: an Extrapolated Apollo address is a candidate only — never promoted", not ok and res == "held")
ok, res, why, val = P.sweep_verdict({"found": True, "email": "person0692@x.org", "email_status": "verified", "zerobounce": "invalid"}, ["x.org"])
t("H7: ZeroBounce invalid -> held", not ok and res == "held")
ok, res, why, val = P.sweep_verdict({"found": True, "email": "curt@gmail.com", "email_status": "verified", "zerobounce": "valid"}, ["x.org"])
t("H7: an address off the org's own domain -> held", not ok)
ok, res, why, val = P.sweep_verdict({"found": True, "email": "person0692@x.org", "email_status": "verified", "zerobounce": "catch_all"}, ["x.org"])
t("H7: catch-all counts in place of valid, flagged", ok and val == "catch_all")
ok, res, why, val = P.sweep_verdict({"found": False}, ["x.org"])
t("H7: nobody found -> queried-null (recorded so it is never paid for twice)", not ok and res == "queried-null")
rl = P.roster_line(pend, {})
t("H7: roster-resolution line counts named / published / unpublished / submitted / deferred", rl["unpublished"] == 7 and rl["submitted"] == 0 and rl["unswept"] == _cap and rl["deferred"] == 7 - _cap and "unpublished" in P.roster_text(rl))
ok, res, why, val = P.sweep_verdict({"found": True, "email": "person0007@www.example.org", "email_status": "verified", "zerobounce": "valid"}, ["www.example.org"])
t("H7: an org with no domain on file falls back to the domains of its own pages read (www.example.org matches example.org)", ok)
bad = [n for n, ok in R if not ok]
# ENG-R008 (Chris 2026-11-09): a generic inbox on a NON-org domain (vendor / event-management mailbox) is never a recipient
caps = cap(U, ["events@vendor.com", "info@x.org"])
ppl = [ingested(person(None, "events@vendor.com"), caps), ingested(person(None, "info@x.org"), caps)]
r = P.assemble("Example Org", "OM-1", ppl, ap("events@vendor.com", "info@x.org"), True, True, org_domains=["x.org"])
t("vendor inbox dropped, org's own generic inbox kept as To", r["decision"] == "ready" and r["to"]["email"] == "info@x.org" and all(c["email"] != "events@vendor.com" for c in r["cc"]))
t("the drop is recorded in considered + flagged", any(c["email"] == "events@vendor.com" and "ENG-R008" in (c["excluded_because"] or "") for c in r["considered"]) and any("ENG-R008" in f for f in r["flags"]))
ppl = [ingested(person(None, "events@vendor.com"), caps)]
r = P.assemble("Example Org", "OM-1", ppl, ap("events@vendor.com"), True, True, [{"name": "[Person 0213]"}], org_domains=["x.org"])
t("vendor inbox as the only address -> hold, not ready (the LDOE case)", r["decision"] == "hold")
r = P.assemble("Example Org", "OM-1", ppl, ap("events@vendor.com"), True, True)
t("no org domains known -> old behaviour unchanged", r["decision"] == "ready")

# H4 (Chris 2026-11-09): a PRINTED address is used whatever the validator says (flagged); an Apollo-found address that is invalid is skipped
caps = cap(U, ["person0765@x.org"])
ppl = [ingested(person("Dee Dead", "person0765@x.org", "executive_director"), caps)]
r = P.assemble("Example Org", "OM-1", ppl, {"person0765@x.org": {"identity": "confirmed", "validity": "invalid"}}, True, True, org_domains=["x.org"])
t("printed address + validator invalid -> still the To, flagged", r["decision"] == "ready" and r["to"]["email"] == "person0765@x.org" and any("sent anyway" in f for f in r["flags"]))
pp = dict(ppl[0]); pp["source"] = "apollo-verified"
r = P.assemble("Example Org", "OM-1", [pp], {"person0765@x.org": {"identity": "confirmed", "validity": "invalid"}}, True, True, org_domains=["x.org"])
t("Apollo-found address + validator invalid -> skipped", r["decision"] == "hold" and any("skip, keep looking" in (c["excluded_because"] or "") for c in r["considered"]))

# Issue 4 (Chris 2026-11-10): greet by the name the page shows the person goes by; titles never become first names
t("first_name strips 'Very Rev.'", P.first_name("Very Rev. Sean Smith") == "Sean")
t("first_name strips 'Rev.' and 'Dr.'", P.first_name("Rev. Dr. Joel Ames") == "Joel")
t("first_name keeps a plain name", P.first_name("Desiree Lopez") == "Desiree")
t("greeting_name used when it is in the printed name", P.greet_name({"name": "Deborah 'Dee Dee' Jones", "greeting_name": "Dee Dee"}) == ("Dee Dee", True))
t("greeting_name not in the printed name -> fallback, not trusted", P.greet_name({"name": "Very Rev. Sean Smith", "greeting_name": "Bob"}) == ("Sean", False))
t("a title is never a greeting_name", P.greet_name({"name": "Rev. Sean Smith", "greeting_name": "Rev."}) == ("Sean", False))
caps = cap(U, ["person2522@x.org"])
pp = ingested(person("Very Rev. Sean Smith", "person2522@x.org", "executive_director"), caps); pp["greeting_name"] = "Sean"
r = P.assemble("Example Org", "OM-1", [pp], ap("person2522@x.org"), True, True, org_domains=["x.org"])
t("greeting built from greeting_name, no title", r["greeting"] == "Hi [Person 1649],")
caps = cap(U, ["info@x.org"])
g = ingested(person(None, "info@x.org", "other_staff"), caps); g["generic"] = True
nw = [{"name": "Lynn Own", "greeting_name": "Lynn", "evidence_url": "https://x.org/staff"}, {"name": "Donna Other", "greeting_name": "Donna", "evidence_url": "https://otherorg.org/presenters"}]
r = P.assemble("Example Org", "OM-1", [g], ap("info@x.org"), True, True, nw, org_domains=["x.org"])
t("named person from ANOTHER org's page is never greeted", r["greeting"] == "Hi [Person 1240] and team," and any("not on the org's own site" in f for f in r["flags"]))

# Issue 4: the org's own printed name is kept only when the page shows it; short name checked against the web address
caps = cap("https://first3yearstx.org/about", [], lines=("About First3Years", "First 3 Years is a Texas nonprofit"))
sn = P.self_name_of({"self_name": {"short": "First3Years", "short_quote": "About First3Years", "formal": "First 3 Years", "formal_quote": "First 3 Years is a Texas nonprofit", "url": "https://first3yearstx.org/about"}}, {"domains": ["first3yearstx.org"]}, caps)
t("printed short name kept and matched to the web address", sn and sn["short"] == "First3Years" and sn["domain_match"] is True)
sn = P.self_name_of({"self_name": {"short": "Texas", "short_quote": "Serving all of Texas", "url": "https://first3yearstx.org/about"}}, {"domains": ["first3yearstx.org"]}, caps)
t("a short name that is not on the captured page is thrown out", sn is None)

# Issue 1 (Chris 2026-11-10): ENG-R008 keeps vendor inboxes out, but an association's own gmail inbox on its own page, or the parent
# university's domain of the org's own sub-site, is the org's own
t("gmail inbox printed on the org's own page is the org's own", P._own_inbox_domain("mtaeyc@gmail.com", ["mtaeyc.org"], {"gate1": "pass", "evidence_url": "https://mtaeyc.org/contact"}))
t("gmail inbox from another site is not", not P._own_inbox_domain("x@gmail.com", ["mtaeyc.org"], {"gate1": "pass", "evidence_url": "https://vendor.com/x"}))
t("parent university domain of the org's sub-site is the org's own", P._own_inbox_domain("person0107@gsu.edu", ["aimh.gsu.edu"]))
t("a vendor company's inbox is still never the org's", not P._own_inbox_domain("events@emergentmethod.com", ["ldoe.gov"], {"gate1": "pass", "evidence_url": "https://ldoe.gov/conf"}))

print("\n%d/%d pass" % (len(R) - len(bad), len(R)))
sys.exit(1 if bad else 0)

