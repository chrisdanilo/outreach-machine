#!/usr/bin/env python3
"""Self-tests for the Stage 3 sender (seqrules.decide + send.plan). Pure fixtures; no Gmail, nothing sent."""
import datetime, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seqrules, send
from seqrules import ET

cal = seqrules.Calendar()
R = []
def check(name, got, want, part=""):
    ok = got["action"] == want and part in got.get("reason", "")
    R.append(ok); print(("PASS " if ok else "FAIL ") + name + " -> " + got["action"] + " · " + got.get("reason", ""))

def th(*dates, to=("person0008@x.org",), cc=("person0269@x.org",), status="open", floor=0):
    return {"status": status, "stage_floor": floor, "sends": [{"date": d, "to": list(to), "cc": list(cc)} for d in dates]}

MON = cal.slot(datetime.date(2026, 11, 2)); TUE = cal.slot(datetime.date(2026, 11, 3))
WED_HOL = datetime.date(2026, 11, 11)   # Veterans Day (Fed holiday)

# 1 holiday delay: Email 1 on 11/4 -> due 11/11 (holiday) -> delayed to Thu 11/12 07:00 ET, never skipped
d = seqrules.decide(th("2026-11-04"), cal.slot(WED_HOL), cal)
R.append(cal.slot(WED_HOL).date() == datetime.date(2026, 11, 12)); print(("PASS" if R[-1] else "FAIL") + " holiday: slot for 11/11 is " + str(cal.slot(WED_HOL)))
check("holiday: Email 2 goes Thu 11/12", seqrules.decide(th("2026-11-04"), cal.slot(datetime.date(2026, 11, 12)), cal), "SEND", "due")
check("holiday: not before (Tue 11/10)", seqrules.decide(th("2026-11-04"), cal.slot(datetime.date(2026, 11, 10)), cal), "WAIT", "2026-11-12")
# 2 weekend: Email 1 Sat? due Sat -> Monday
R.append(cal.due(datetime.date(2026, 10, 24)).date() == datetime.date(2026, 11, 2)); print(("PASS" if R[-1] else "FAIL") + " weekend due rolls to Monday")
# 3 all recipients out -> delayed to the business day after the earliest return
au = [{"sender": "person0008@x.org", "return": "2026-11-02", "after_last_send": True}, {"sender": "person0269@x.org", "return": "2026-11-05", "after_last_send": True}]
d = seqrules.decide(th("2026-10-26"), MON, cal, autos=au); check("all-out OOO delays", d, "DELAYED", "earliest back 2026-11-02")
R.append(d.get("due", "").startswith("2026-11-03T07:00")); print(("PASS" if R[-1] else "FAIL") + " all-out OOO -> Tue 11/3 07:00 ET: " + d.get("due", ""))
# 4 one person out -> send on schedule to everyone
check("one-out OOO sends", seqrules.decide(th("2026-10-26"), MON, cal, autos=au[:1]), "SEND", "due")
# 5 Email 3 waits while an auto-reply is active
check("Email 3 waits for active auto-reply", seqrules.decide(th("2026-10-19", "2026-10-26"), MON, cal, autos=[dict(au[1])]), "DELAYED", "Email 3 waits")
# 6 review hold -> draft plan, not a send; nothing if a review draft exists
check("review hold -> draft", seqrules.decide(th("2026-10-26"), MON, cal, review_hold=True), "REVIEW_DRAFT")
check("review hold + draft exists -> nothing", seqrules.decide(th("2026-10-26"), MON, cal, review_hold=True, drafts=1), "NONE", "review draft already")
check("hold clears once Chris sends (timed from his send)", seqrules.decide(th("2026-10-19", "2026-10-30"), MON, cal, review_hold=False), "WAIT", "2026-11-06")
# 7 R1 stopped -> nothing
check("R1 stopped", seqrules.decide(th("2026-10-19"), MON, cal, stopped="stopped by Chris's R1 ruling"), "STOPPED", "R1")
# 8 bounced Cc dropped; bounced To stops
d = seqrules.decide(th("2026-10-26"), MON, cal, bounced=["person0269@x.org"]); check("bounced Cc dropped", d, "SEND")
R.append(d.get("dropped") == ["person0269@x.org"] and d.get("recipients") == 1); print(("PASS" if R[-1] else "FAIL") + " bounced Cc dropped from recipients: %s" % d.get("dropped"))
check("bounced To stops", seqrules.decide(th("2026-10-26"), MON, cal, bounced=["person0008@x.org"]), "STOPPED", "To bounced")
# 9 overdue -> next slot
check("overdue -> next slot", seqrules.decide(th("2026-10-13"), MON, cal), "SEND", "overdue since 2026-10-20")
# 10 never Email 1
check("never Email 1", seqrules.decide(th(), MON, cal), "NONE", "Email 1")
# 11 never twice: a duplicate copy is not a step; Email 3 sent -> close, never a 4th
d = seqrules.decide(th("2026-10-12", "2026-10-19", "2026-10-19T00:00:01"), MON, cal); check("duplicate copy not counted (Email 3 next)", d, "SEND")
R.append(d.get("email") == 3); print(("PASS" if R[-1] else "FAIL") + " duplicate -> next is Email %s" % d.get("email"))
check("after Email 3 -> close, never a 4th", seqrules.decide(th("2026-10-05", "2026-10-12", "2026-10-19"), MON, cal), "CLOSE")
check("stage never backward (label says E3, dates show 2)", seqrules.decide(th("2026-10-05", "2026-10-12", floor=3), MON, cal), "READ")
# 12 stops: human reply, labels, open draft
check("human reply stops", seqrules.decide(th("2026-10-26"), MON, cal, human=True), "STOPPED", "replied")
for st, part in (("attention⚠", "⚠"), ("hold⏸", "⏸"), ("closed✗", "closed")):
    check("label " + st, seqrules.decide(th("2026-10-26", status=st), MON, cal), "HELD" if "closed" not in st else "NONE", part)
check("open draft holds", seqrules.decide(th("2026-10-26"), MON, cal, drafts=1), "HELD", "draft")
# 13 fail closed beyond the holiday list
check("fail closed in 2028", seqrules.decide(th("2027-12-20"), datetime.datetime(2028, 1, 3, 7, tzinfo=ET), cal), "HELD", "FAIL CLOSED")
# 14 plan(): one org, one thread; never twice in one slot; Email 1-draft never planned
orgs = [{"org_id": "org:x", "name": "X", "owner_machine": "OM-1", "exclusions": {}, "threads": [
    {"thread_id": "t1", "machine": "OM-1", "stage": "E1", "status": "open", "labels": [], "messages_sent": [{"date": "2026-10-26", "to": ["person0008@x.org"], "cc": []}], "gmail": None},
    {"thread_id": "t2", "machine": "OM-1", "stage": "E1", "status": "open", "labels": [], "messages_sent": [{"date": "2026-10-26", "to": ["person0389@x.org"], "cc": []}], "gmail": None},
    {"thread_id": "t3", "machine": "OM-1", "stage": "E1-draft", "status": "open", "labels": [], "messages_sent": [], "gmail": None}]}]
gs = {"threads": {}, "separate_threads_by_domain": {}, "completeness": {"sent_windows": ["2026-10-21..25 both (1)"]}}
_, rows, _ = send.plan(datetime.date(2026, 11, 2), orgs, gs, cal)
acts = sorted((r["thread"], r["action"]) for r in rows)
R.append(acts == [("t1", "SEND"), ("t2", "HELD")]); print(("PASS" if R[-1] else "FAIL") + " plan: one org one thread, Email-1 draft never planned: %s" % acts)
R.append(len({r["thread"] for r in rows}) == len(rows)); print(("PASS" if R[-1] else "FAIL") + " plan: no thread twice")
_, rows2, _ = send.plan(datetime.date(2026, 10, 31), orgs, gs, cal)
R.append(rows2 == []); print(("PASS" if R[-1] else "FAIL") + " plan on Saturday: nothing (sends wait for Monday)")
# 15 J6 successors (Chris 2026-10-30)
import successors as SU
D = datetime.date(2026, 11, 2)
V = {"person2184@x.org": {"result": "valid"}, "person2185@x.org": {"result": "valid"}, "pd@x.org": {"result": "valid"}, "person0270@x.org": {"result": "invalid"}, "person0388@x.org": {"result": "valid"}}
def rec(*succ, sender="person0008@x.org", departed=True):
    return {"sender": sender, "departed_name": "Ann", "departed": departed, "successors": [dict(email=e, name=n, title=t, routing=r, applies=True) for e, n, t, r in succ]}
def j6(name, got, ok):
    R.append(bool(ok)); print(("PASS " if ok else "FAIL ") + "J6 " + name + " -> to=%s cc=%s notes=%s flags=%s needs=%s" % (got["to"], got["cc"], got["notes"], got["flags"], got["needs"]))
g = SU.apply(["person0008@x.org"], ["person0269@x.org"], [rec(("person2184@x.org", "Sue Smith", None, None))], "OM-1", ["x.org"], {}, V, D)
j6("single successor takes the To spot", g, g["to"] == ["person2184@x.org"] and g["cc"] == ["person0269@x.org"] and g["add_names"] == ["Sue"] and g["remove_names"] == ["Ann"])
g = SU.apply(["person0008@x.org"], [], [rec(("person2184@x.org", "Sue", "Finance Manager", "billing and invoices"), ("pd@x.org", "Pat", None, "professional development and training requests"))], "OM-1", ["x.org"], {}, V, D)
j6("routed successor (PD/training routing wins)", g, g["to"] == ["pd@x.org"] and "person2184@x.org" not in g["cc"])
g = SU.apply(["person0008@x.org"], [], [rec(("person2184@x.org", "Sue", None, None), ("person2185@x.org", "Sam", None, None))], "OM-1", ["x.org"], {}, V, D)
j6("two successors, no info -> both", g, g["to"] == ["person2184@x.org"] and g["cc"] == ["person2185@x.org"])
g = SU.apply(["person0008@x.org"], ["person0269@x.org", "person0389@x.org"], [rec(("person2184@x.org", "Sue", None, None), ("person2185@x.org", "Sam", None, None), ("person0388@x.org", "Cy", None, None))], "OM-1", ["x.org"], {}, V, D)
j6("ceiling overflow -> fits 4, flagged", g, len(g["to"]) + len(g["cc"]) == 4 and any("ceiling" in f for f in g["flags"]))
g = SU.apply(["person0008@x.org"], ["person0269@x.org"], [rec(("person0270@x.org", "Bo", None, None))], "OM-1", ["x.org"], {}, V, D)
j6("invalid successor -> not added, flagged", g, "person0270@x.org" not in g["to"] + g["cc"] and any("invalid" in f for f in g["flags"]))
g = SU.apply(["person0008@x.org"], [], [rec(("person1934@x.org", "Nia", None, None))], "OM-1", ["x.org"], {}, V, D)
j6("unvalidated successor -> NEEDS the check first", g, g["needs"] == ["person1934@x.org"] and g["to"] == ["person0008@x.org"])
g = SU.apply(["person0008@x.org"], [], [rec(("person2184@x.org", "Sue", None, None), departed=False)], "OM-1", ["x.org"], {}, V, D)
j6("temporary cover is never added (J5)", g, g["to"] == ["person0008@x.org"] and not g["changed"])
g = SU.apply(["person0008@x.org"], ["person0269@x.org"], [rec(("person1049@y.org", "Jo", None, None))], "OM-1", ["x.org"], {"y.org": {"org_id": "org:y", "name": "Y Org", "has_thread": True, "excluded": False}}, dict(V, **{"person1049@y.org": {"result": "valid"}}), D)
j6("successor at another org with its own thread -> not added, flagged", g, "person1049@y.org" not in g["to"] + g["cc"] and any("one org, one thread" in f for f in g["flags"]))
g = SU.apply(["person0008@x.org"], [], [rec(dict(email="person2184@x.org"), )] if False else [{"sender": "person0008@x.org", "departed": True, "departed_name": "Ann", "successors": [{"email": "person2184@x.org", "name": "Sue", "applies": True, "valid_until": "2026-09-30"}]}], "OM-1", ["x.org"], {}, V, D)
j6("successor named only until a past date is ignored", g, g["to"] == ["person0008@x.org"] and any("only named through" in n for n in g["notes"]))
# 16 J6 inside plan(): the swap reaches the send row; an unvalidated successor holds the thread for the check
orgs = [{"org_id": "org:x", "name": "X", "owner_machine": "OM-1", "domains": ["x.org"], "exclusions": {}, "threads": [
    {"thread_id": "t9", "machine": "OM-1", "stage": "E1", "status": "open", "labels": [], "messages_sent": [{"date": "2026-10-26", "to": ["person0008@x.org"], "cc": ["person0269@x.org"]}], "gmail": None}]}]
send.SUCC_RECS, send.SUCC_VAL, send.PROV_BAD = [rec(("person2184@x.org", "Sue", None, None))], V, []
_, rows, _ = send.plan(datetime.date(2026, 11, 2), orgs, gs, cal)
r = rows[0]; ok = r["action"] == "SEND" and r["to"] == ["person2184@x.org"] and r["j6"] and r["j6"]["add_names"] == ["Sue"]
R.append(ok); print(("PASS" if ok else "FAIL") + " plan: J6 swap reaches the send row: %s %s %s" % (r["action"], r["to"], r.get("j6")))
send.SUCC_RECS = [rec(("person1934@x.org", "Nia", None, None))]
_, rows, _ = send.plan(datetime.date(2026, 11, 2), orgs, gs, cal)
r = rows[0]; ok = r["action"] == "HELD" and "ZeroBounce" in r["reason"] and r["needs"] == ["person1934@x.org"]
R.append(ok); print(("PASS" if ok else "FAIL") + " plan: unvalidated successor holds the thread for the check: %s · %s" % (r["action"], r["reason"]))
send.SUCC_RECS, send.SUCC_VAL, send.PROV_BAD = [], {}, []
print("\n%d/%d PASS" % (sum(R), len(R)))
sys.exit(0 if all(R) else 1)
