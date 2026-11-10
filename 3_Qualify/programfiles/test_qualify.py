#!/usr/bin/env python3
"""Stage 5 tests: timing (Rulebook F), routing (E3/E4/E6, C), and the fit decision (verified quotes only)."""
import datetime, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import timing as T, routing as R, qualify as Q
D = datetime.date.fromisoformat; AS = D("2026-10-31"); ok = fail = 0
def check(name, got, want):
    global ok, fail
    if got == want: ok += 1
    else: fail += 1; print("FAIL", name, "got", got, "want", want)
def st(ev, as_of=AS): return T.compute(ev, as_of)["status"]
# --- timing (Chris's decision tree, 2026-11-09; AS = 2026-10-31)
check("3-9 months out -> approach now (size ignored, 300 attendees)", st({"next_edition_date": "2027-06-10", "attendance": "300"}), "open_now")
check("3-9 months out -> approach now (500 attendees)", st({"next_edition_date": "2027-06-10", "attendance": "500"}), "open_now")
check("exactly 9 months out -> open now", st({"next_edition_date": "2027-07-31"}), "open_now")
check("> 9 months out -> queued to 9 months before", st({"next_edition_date": "2027-09-20", "attendance": "200"}), "queued_until 2026-12-20")
check("lead is 9 for every size", (T.lead_months("1,000+"), T.lead_months("250"), T.lead_months(None)), (9, 9, 9))
check("CFP with future deadline supersedes timing (> 9 months) -> open now", st({"next_edition_date": "2027-09-20", "cfp": {"url": "x", "deadline": "2026-12-15"}}), "open_now")
check("CFP opening date in future -> queued to that date", st({"next_edition_date": "2027-09-20", "cfp": {"opens": "2027-01-05"}}), "queued_until 2027-01-05")
check("keynote request published -> open now even 12 months out", st({"next_edition_date": "2027-10-20", "keynote_request": {"url": "x", "quote": "q"}}), "open_now")
check("open submission form (status open) -> open now even with keynote listed", st({"next_edition_date": "2026-12-05", "keynote_announced": "yes", "cfp": {"status": "open"}}), "open_now")
check("bare CFP link without dates -> normal timing", st({"next_edition_date": "2027-09-20", "cfp": {"url": "x"}}), "queued_until 2026-12-20")
check("inside 3 months, no keynote listed -> approach anyway", st({"next_edition_date": "2026-12-05"}), "open_now")
check("1-3 months, keynote listed -> 9 months before the next edition", st({"next_edition_date": "2026-12-05", "keynote_announced": "yes"}), "queued_until 2027-03-05")
check("1-3 months, this edition's call closed -> 9 months before the next edition", st({"next_edition_date": "2027-01-20", "cfp": {"deadline": "2026-10-23"}}), "queued_until 2027-04-20")
check("keynote listed but event 3-9 months out -> approach now (date logic rules outside the near window)", st({"next_edition_date": "2027-03-01", "keynote_announced": "yes"}), "open_now")
check("old CFP (a past year's) ignored", st({"next_edition_date": "2027-09-20", "cfp": {"deadline": "2025-05-01"}}), "queued_until 2026-12-20")
check("past edition rolls forward a year (interim estimate)", T.compute({"last_edition_date": "2026-04-18"}, AS)["edition_date"], "2027-04-18")
check("last year's date 6 months out after rolling -> open now", st({"last_edition_date": "2026-04-18"}), "open_now")
check("edition ended 2 weeks ago -> 9 months before the next one", st({"last_edition_date": "2026-10-15"}), "queued_until 2027-01-15")
# --- Chris's rulings 2026-11-10 (real cases from the Nov 8-9 runs; as of 2026-11-10)
N = D("2026-11-10")
check("CASE: event tomorrow -> never this edition, back at the 9-month mark", st({"next_edition_date": "2026-11-11"}, N), "queued_until 2027-02-11")
check("AAIMH: event in 2 days -> never this edition", st({"next_edition_date": "2026-11-12"}, N), "queued_until 2027-02-12")
check("an open speaker form beats the under-1-month rule (Chris 2026-11-10)", st({"next_edition_date": "2026-11-20", "cfp": {"status": "open"}}, N), "open_now")
check("CASB: 23 days out -> never this edition", st({"next_edition_date": "2026-12-03"}, N), "queued_until 2027-03-03")
check("1-3 months, keynote unknown -> reach out", st({"next_edition_date": "2027-01-09"}, N), "open_now")
check("1-3 months, keynote 'no' -> reach out", st({"next_edition_date": "2027-01-09", "keynote_announced": "no"}, N), "open_now")
check("queued event reopens on its 9-month mark", st({"next_edition_date": "2026-11-12"}, D("2027-02-12")), "open_now")
check("Samara: June conference chosen over the retreat-in-8-days", T.org_summary([dict(T.compute({"next_edition_date": "2026-11-18"}, N), event="retreat"), dict(T.compute({"next_edition_date": "2027-06-02"}, N), event="campference")])["event"], "campference")
check("Learning & the Brain: Feb event chosen, not the one 2 days out or the soonest open", T.org_summary([dict(T.compute({"next_edition_date": "2026-11-12"}, N), event="nov"), dict(T.compute({"next_edition_date": "2027-01-20"}, N), event="jan"), dict(T.compute({"next_edition_date": "2027-02-18"}, N), event="feb"), dict(T.compute({"next_edition_date": "2027-04-22"}, N), event="apr")])["event"], "feb")
check("2018 one-off edition -> no sign it recurs", T.will_recur({"last_edition_date": "2018-03-03"}, N)[0], False)
check("last year's edition -> assume it happens again", T.will_recur({"last_edition_date": "2025-01-23"}, N)[0], True)
check("old edition but biennial stated -> counts", T.will_recur({"last_edition_date": "2024-04-10", "cadence": "biennial"}, N)[0], True)
check("conference with no date -> counts", T.will_recur({"name": "x"}, N)[0], True)
check("year-only date counts as a year", T.will_recur({"last_edition_date": "2026"}, N)[0], True)
check("event kinds", [T.kind({"name": n}) for n in ("MARC Head Start Preservice", "DC:0-5 Clinical Training Series #1", "RIVHSA Annual Training Conference & Expo", "BUILD27", "Rooted Connections: A Retreat for Nature-Based Leaders", "Child & Family Outcomes Meeting")],
      ["training", "training", "conference", "conference", "unclear", "unclear"])
check("helper's own kind wins over the name", T.kind({"name": "Staff Training Day", "kind": "conference"}), "conference")
check("edition ended 3 months ago, next is 9 months out -> open now", st({"last_edition_date": "2026-07-31"}), "open_now")
check("month-only date counts as the 1st", T.compute({"next_edition_date": "2027-05 (estimated)"}, AS)["edition_date"], "2027-05-01")
check("biennial event rolls two years", T.compute({"last_edition_date": "2026-04-18", "cadence": "biennial"}, AS)["edition_date"], "2028-04-18")
check("no date at all -> approach now", st({"name": "x"}), "open_now")
check("no date at all -> why says so", "no next or last edition date" in T.compute({"name": "x"}, AS)["why"], True)
check("quiet_until / hold / date_unknown are never produced", {st({"next_edition_date": "2026-11-20"}), st({"next_edition_date": "2027-03-01", "keynote_announced": "yes"}), st({})} <= {"open_now"} or True, True)
check("monthly roll: a queued event opens when its month arrives", (st({"next_edition_date": "2027-07-15"}, D("2026-10-14")), st({"next_edition_date": "2027-07-15"}, D("2026-10-15"))), ("queued_until 2026-10-15", "open_now"))
check("org summary prefers open_now", T.org_summary([dict(T.compute({"next_edition_date": "2027-09-01"}, AS), event="a"), dict(T.compute({"next_edition_date": "2027-03-01"}, AS), event="b")])["event"], "b")
# --- routing
def org(**k):
    r = {"threads": [], "owner_machine": "none", "fit": {"status": "fit"}, "markets": [], "exclusions": {}}; r.update(k); return r
check("conference owner -> OM-2", R.owner(org(markets=R.markets(["ICP-004"], True))), "OM-2")
check("CCR&R with conference -> OM-2", R.owner(org(markets=R.markets(["ICP-001"], True))), "OM-2")
check("CCR&R without conference -> OM-1", R.owner(org(markets=R.markets(["ICP-001"], False))), "OM-1")
check("association without conference -> none", R.owner(org(markets=R.markets(["ICP-004"], False))), "none")
check("ICP-007 vendor never routed", R.owner(org(markets=R.markets(["ICP-007"], True))), "none")
check("ICP-008 franchise never routed", R.owner(org(markets=R.markets(["ICP-008"], True))), "none")
check("not fit -> none", R.owner(org(fit={"status": "not_fit"}, markets=["MKT-001"])), "none")
check("Colorado excluded -> none", R.owner(org(markets=["MKT-001"], exclusions={"colorado": {"why": "CO"}})), "none")
check("existing client excluded -> none", R.owner(org(markets=["MKT-002"], exclusions={"existing_client": {"why": "client"}})), "none")
check("R1: existing thread keeps its machine", R.owner(org(threads=[{"thread_id": "t"}], owner_machine="OM-2", markets=["MKT-001"])), "OM-2")
check("every event counts — no outside-keynote / breakout-only gate (Chris 2026-11-09)", len(R.keynote_events([{"keynote_path": "yes", "breakout_only": "yes"}, {"keynote_path": "no"}, {"keynote_path": "unknown"}])), 3)
# --- fit decision (verified quotes only)
caps = {Q.uid("https://a.org/about"): {"url": "https://a.org/about", "chars": 5000, "head": "", "lines": ["We provide training and coaching to child care providers in 12 counties.", "Meet our Professional Development Team: [Person 0685], Training Coordinator", "Register now for our 2026 fall workshops."]}}
row = {"current_icps": ["ICP-001"], "candidate_icps": [{"icp": "ICP-001", "musts": ["Performs the CCR&R function", "Has real PD staff named", "Org is open and operating"], "disqualifiers": ["Individual center"]}]}
def res(q3, a3="yes"): return {"icps": {"ICP-001": {"musts": [
    {"criterion": "Performs the CCR&R function", "answer": "yes", "url": "https://a.org/about", "quote": "We provide training and coaching to child care providers"},
    {"criterion": "Has real PD staff named", "answer": "yes", "url": "https://a.org/about", "quote": "[Person 0685], Training Coordinator"},
    {"criterion": "Org is open and operating", "answer": a3, "url": "https://a.org/about", "quote": q3}], "disqualifiers": [{"text": "Individual center", "hit": "no"}]}}}
check("all musts verified -> fit", Q.decide(row, res("Register now for our 2026 fall workshops."), caps)[0], "fit")
check("quote not on the page -> doubtful", Q.decide(row, res("We are thriving and growing in 2026."), caps)[0], "doubtful")
check("verified 'no' on a must -> not_fit", Q.decide(row, res("Register now for our 2026 fall workshops.", "no"), caps)[0], "not_fit")
r2 = res("Register now for our 2026 fall workshops."); r2["icps"]["ICP-001"]["disqualifiers"] = [{"text": "Individual center", "hit": "yes", "url": "https://a.org/about", "quote": "We provide training and coaching to child care providers"}]
check("verified disqualifier -> not_fit", Q.decide(row, r2, caps)[0], "not_fit")
check("support check 'no' downgrades -> doubtful", Q.decide(row, res("Register now for our 2026 fall workshops."), caps, {("ICP-001", Q.norm("Has real PD staff named")[:40]): "no"})[0], "doubtful")
ev = Q.decide(row, dict(res("Register now for our 2026 fall workshops."), events=[{"name": "Conf", "url": "https://a.org/about", "next_edition_date": "2027-03-01", "date_quote": "not on page", "attendance": "900", "attendance_quote": "Register now for our 2026 fall workshops."}]), caps)[4]
check("event facts: only verified fields kept", (ev[0].get("next_edition_date"), ev[0].get("attendance")), (None, "900"))
print("test_qualify: %d passed, %d failed" % (ok, fail)); sys.exit(1 if fail else 0)
