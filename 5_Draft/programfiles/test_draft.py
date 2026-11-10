#!/usr/bin/env python3
"""test_draft.py -- Stage 7 tests (Email 1 drafter + Gate 7). Offline; touches no real run folder."""
import base64, copy, json, os, sys, tempfile
from email.message import EmailMessage
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import draft, gate7

R = []
def ok(name, cond): R.append((name, bool(cond))); print(("PASS " if cond else "FAIL ") + name)

def org(**kw):
    o = {"org_id": "org:x.org", "name": "Example Child Care Council", "aliases": [], "domains": ["x.org"], "state": "NC", "owner_machine": "OM-1",
         "referrer": False, "threads": [], "fit": {"status": "fit"}, "exclusions": {}, "icps": ["ICP-001"], "flags": [], "outreach": None,
         "recipients": {"to": {"email": "person0188@x.org", "name": "Ann Lee"}, "cc": [{"email": "person0334@x.org", "name": "Bo Tam"}], "greeting": "Hi [Person 0128] and Bo,"}}
    o.update(kw); return o
IDX = (set(), {}, {})

# verbatim copy: the rendered body's text equals the template text for both machines
for m in ("OM-1", "OM-2"):
    ok("verbatim copy %s" % m, draft.text_of_html(draft.e1_template(m)) == draft.text_of_md(draft.e1_markdown(m)))
    b = draft.body_for(m, "Ann and Bo")
    ok("only the greeting varies %s" % m, draft.text_of_html(b) == draft.text_of_md(draft.e1_markdown(m)).replace("{Names}", "Ann and Bo"))
    ok("no GIF placeholder ships %s" % m, "▶" not in b and "WorkshopInAction" not in b)
    ok("clean video link %s" % m, 'href="https://www.youtube.com/watch?v=iNCItCda-8g"' in b and "google.com/url" not in b)

# greeting naming (G7): bare names on Email 1, every named person, no salutation word
ok("greeting bare names", draft.e1_greeting("OM-1", "Hi [Person 0175], Megan and Cait,", "CCPPNS") == "Barbara, Megan and Cait")
ok("greeting named + team", draft.e1_greeting("OM-2", "Hi [Person 0820] and team,", "First 8") == "Kandace and team")
ok("greeting no names OM-2", draft.e1_greeting("OM-2", "Hi First 8 Memphis team,", "First 8") == "First 8 conference team")
ok("greeting no names OM-1", draft.e1_greeting("OM-1", "Hi Foo team,", "Foo") == "Hi Foo team")
ok("short name from acronym", draft.short_name(org(name="California Council of Parent Participation Nursery Schools", aliases=["California Council of Parent Participation Nursery Schools (CCPPNS)"]), {})[0] == "CCPPNS")
ok("short name trimmed", draft.short_name(org(name="Early Learning Coalition of Osceola County"), {})[0] == "ELC Osceola County")

# eligibility blocks (C2/C3/C4/C5)
ok("eligible base", draft.why_not(org(), IDX) is None)
ok("CO blocked", "Colorado" in draft.why_not(org(state="CO"), IDX))
ok("existing thread blocked", "thread" in draft.why_not(org(threads=[{"thread_id": "t"}]), IDX))
ok("client exclusion blocked", "excluded" in draft.why_not(org(exclusions={"existing_client": {"why": "client"}}), IDX))
ok("recipient domain = client blocked", "client" in draft.why_not(org(recipients={"to": {"email": "person0006@client.org"}, "cc": [], "greeting": "Hi A,"}), ({"client.org"}, {}, {})))
ok("recipient domain DNC blocked", "do-not-contact" in draft.why_not(org(), ({("dnc", "x.org")}, {}, {})))
ok("To on DNC list blocked", "do_not_contact" in draft.why_not(org(), (set(), {"person0188@x.org": "do_not_contact"}, {})))
ok("other org's thread domain blocked", "another org" in draft.why_not(org(recipients={"to": {"email": "person0009@y.org"}, "cc": [], "greeting": "Hi A,"}), (set(), {}, {"y.org": "org:y.org"})))
ok("OM-2 not open blocked", "not open" in draft.why_not(org(owner_machine="OM-2", outreach={"status": "queued_until 2027-01-01"}), IDX))
ok("referrer blocked", "referrer" in draft.why_not(org(referrer=True), IDX))
ok("doubtful fit is never drafted — it waits in the dossier for Chris (Rulebook E2, 2026-11-10)", "doubtful" in (draft.why_not(org(fit={"status": "doubtful", "reason": "x"}), IDX) or ""))
to, cc, fl = draft.recipients_of(org(), (set(), {"person0334@x.org": "bounced"}, {}))
ok("bounced Cc dropped + flagged", cc == [] and fl and "dropped" in fl[0])

# Sent-check blocks a duplicate; ceiling makes spares; create order reverse priority; labels at creation
d = tempfile.mkdtemp(); os.makedirs(os.path.join(d, "raw"))
cands = []
for i in range(1, 5):
    c = {"n": i, "org_id": "org:o%d.org" % i, "org_name": "Org %d" % i, "org_domain": "o%d.org" % i, "domains": [], "state": "NC", "machine": "OM-1",
         "to": {"email": "a@o%d.org" % i}, "cc": [], "greeting": "A", "short": "O%d" % i, "short_how": "x", "subject": "Question about PD/Training at O%d . . ." % i, "flags": []}
    cands.append(c)
    json.dump({"threads": [{"id": "t"}]} if i == 1 else {}, open(os.path.join(d, "raw", "sent_%d.json" % i), "w"))
    json.dump({"drafts": [{"id": "r"}]} if i == 2 else {}, open(os.path.join(d, "raw", "drafts_%d.json" % i), "w"))
keep = dict(draft.M["max_per_night"]); draft.M["max_per_night"] = {"OM-1": 1, "OM-2": 1}
params, held = draft.step_gate(d, {}, cands, {"OM-1": "L1", "OM-1/0": "L10", "OM-2": "L2", "OM-2/0": "L20"})
draft.M["max_per_night"] = keep
hs = {h["org_id"]: h["status"] for h in held}
ok("sent-check blocks prior contact", hs.get("org:o1.org") == "HELD")
ok("drafts check blocks a second draft", hs.get("org:o2.org") == "HELD")
ok("ceiling -> spare, never more", len(params) == 1 and hs.get("org:o4.org") == "SPARE")
ok("label OM-1 + OM-1/0 at creation", params[0]["params"]["label_ids"] == ["L1", "L10"])
ok("HubSpot Bcc on every draft", params[0]["params"]["bcc"] == [draft.D["hubspot_bcc"]])

# labels: missing tree is created, existing tree is left alone (idempotent)
json.dump({"labels": [{"name": n, "id": "I" + n} for n in draft.LABEL_TREE]}, open(os.path.join(d, "raw", "labels.json"), "w"))
ok("labels idempotent (nothing to create)", draft.label_ids(d)[1] == [])
json.dump({"labels": [{"name": "OM-1", "id": "x"}]}, open(os.path.join(d, "raw", "labels.json"), "w"))
ok("labels missing -> create list", len(draft.label_ids(d)[1]) == len(draft.LABEL_TREE) - 1)

# Gate 7 on synthetic raw MIME
def raw(att_bytes, name="HST_Flyer.pdf", href="https://www.youtube.com/watch?v=iNCItCda-8g", bcc="<HUBSPOT_BCC_ADDRESS>"):
    m = EmailMessage(); m["To"] = "person0188@x.org"; m["Cc"] = "person0334@x.org"; m["Subject"] = "S . . ."
    if bcc: m["Bcc"] = bcc
    m.set_content("x"); m.add_alternative('<p><a href="%s">v</a></p>' % href, subtype="html")
    if att_bytes: m.add_attachment(b"%" * att_bytes, maintype="application", subtype="pdf", filename=name)
    return base64.urlsafe_b64encode(m.as_bytes()).decode()
want = ("HST_Flyer.pdf", 1000)
g = lambda r, **kw: gate7.check(gate7.parse(r), want[0], want[1], 2, "<HUBSPOT_BCC_ADDRESS>", "https://www.youtube.com/watch?v=iNCItCda-8g", ["person0188@x.org"], ["person0334@x.org"], "S . . .")
ok("gate7 pass", g(raw(1000))["ok"])
ok("gate7 fail: no attachment", not g(raw(0))["ok"])
ok("gate7 fail: wrong size", not g(raw(500))["ok"])
ok("gate7 fail: wrapped link", not g(raw(1000, href="https://www.google.com/url?q=x"))["ok"])
ok("gate7 fail: no Bcc", not g(raw(1000, bcc=None))["ok"])
ok("gate7 finds raw in a saved result", gate7.find_raw({"message": {"raw": raw(1000)}}) is not None)

# shortfall reporting: summary names the machine and the reason (minimum vs what was possible)
dd = tempfile.mkdtemp()
summ_line = "%d of %d minimum" % (3, draft.M["minimum"]["OM-2"])
ok("minimums are OM-1 10 / OM-2 35 (machines block of the one settings file)", draft.M["minimum"] == {"OM-1": 10, "OM-2": 35})
src = open(os.path.join(HERE, "draft.py"), encoding="utf-8").read()
sf = draft.shortfall({"OM-1": 1, "OM-2": 40}, {"OM-1": 1, "OM-2": 52})
ok("shortfall reported for OM-1 only, with the reason", list(sf) == ["OM-1"] and "1 of 10 minimum" in sf["OM-1"] and "gates never lowered" in sf["OM-1"])
ok("never sends (no send action in the drafter)", "reply_to_message" not in src and "send_message" not in src)

n_ok = sum(1 for _, c in R if c); print("\n%d/%d pass" % (n_ok, len(R))); sys.exit(0 if n_ok == len(R) else 1)
