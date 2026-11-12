#!/usr/bin/env python3
"""test_dossier.py — the 2026-11-04 dossier outline, with the 2026-11-10 change (cards first, then the top 10 decisions). Offline: builds a scratch root (OUTREACH_ROOT) and runs dossier.py on it."""
import json, os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
R = []
def ok(name, cond): R.append((name, bool(cond))); print(("PASS " if cond else "FAIL ") + name)
def w(root, rel, rows=None, text=None):
    p = os.path.join(root, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        if text is not None: f.write(text)
        else:
            for r in rows: f.write(json.dumps(r) + "\n")
def org(oid, name, dom, to, cc=(), **kw):
    o = {"org_id": oid, "name": name, "domains": [dom] if dom else [], "state": "OR", "icps": ["ICP-001"], "events": [], "flags": [],
         "exclusions": {}, "fit": {"status": "fit", "reason": "Machine 1 candidate status HELD: internal"}, "recipients": {"to": to, "cc": list(cc)}}
    o.update(kw); return o
P = lambda n, e, role, src="live-page", ev="https://a.org/team": {"name": n, "email": e, "role": role, "source": src, "evidence_url": ev, "identity": "confirmed", "validity": "unknown"}

root = tempfile.mkdtemp()
orgs = [org("org:a.org", "Alpha CCR&R", "a.org", P("Ann Lee", "person0212@a.org", "Executive Director"), [P("Bo Tam", "person0373@a.org", "Training Coordinator")]),
        org("org:b.org", "Beta Action", "b.org", {"name": None, "email": "info@b.org", "role": "general inbox", "source": "page", "generic": True, "evidence_url": "https://b.org/contact"}),
        org("org:c.org", "Gamma Center", "c.org", P("Cy Doe", "person0703@c.org", "Video Lending Library", ev="https://c.org/contact")),
        org("org:d.org", "Delta Kids", "d.org", P("Di Fox", "person0801@d.org", "Project Manager", ev="https://d.org/program")),
        org("org:d2", "Delta Kids (2nd record)", None, P("Di Fox", "person0801@d.org", "Project Manager")),
        org("org:e.org", "Epsilon Conf", "e.org", P("Ed Ray", "person0899@e.org", "Conference Director", ev="https://e.org/conf"), events=[{"name": "E Summit", "url": "https://e.org/summit", "next_edition_date": "2027-03-01", "keynote_path": "yes"}])]
w(root, "_shared/master/orgs.jsonl", orgs)
D = lambda oid, name, m, k, did, to, cc=(), **kw: dict({"org_id": oid, "org_name": name, "machine": m, "run": "N1-p1", "create_order": k, "status": "DRAFTED", "draft_id": did,
         "thread_id": "t" + did, "subject": "Question about PD/Training at %s . . ." % name, "greeting": "Hi", "to": to, "cc": list(cc), "created_at": "2026-11-04T05:00:00+00:00", "flags": [], "state": "OR"}, **kw)
w(root, "5_Draft/ledgers/drafts.jsonl", [D("org:a.org", "Alpha CCR&R", "OM-1", 1, "d1", "person0212@a.org", ["person0373@a.org"]),
                                         D("org:b.org", "Beta Action", "OM-1", 2, "d2", "info@b.org"),
                                         D("org:c.org", "Gamma Center", "OM-1", 3, "d3", "person0703@c.org"),
                                         D("org:d.org", "Delta Kids", "OM-1", 4, "d4", "person0801@d.org"),
                                         D("org:e.org", "Epsilon Conf", "OM-2", 1, "d5", "person0899@e.org", event="E Summit")])
w(root, "4_People/runs/N1-p1/result_1.jsonl", [{"org_id": "org:b.org", "pages_read": ["https://b.org/leadership", "https://b.org/contact"], "named_without_email": [{"name": "Kim Park", "role": "Executive Director"}]},
                                               {"org_id": "org:d.org", "pages_read": ["https://d.org/our-team", "https://d.org/program"], "named_without_email": [{"name": "[Person 0100]", "role": "Executive Director"}, {"name": "[Person 1532]", "role": "Training Coordinator"}]}])
w(root, "4_People/ledgers/sweep-ledger.jsonl", [{"key": "org:d.org|ana goode", "result": "queried-null"}])
w(root, "5_Draft/runs/N1-p1/verify.json", text=json.dumps({"1": {"draft_id": "d1", "gate7": {"ok": True}}, "2": {"draft_id": "d2", "gate7": {"ok": True}}, "3": {"draft_id": "d3", "gate7": {"ok": False, "why": "Cc differs"}}}))
w(root, "_shared/master/seeds/OM-1/hubspot-suppression.md", text="# x\n## §A — HARD BLOCK\n| `zzz.org` | Z |\n## §C — INTERNAL\n`a.org`\n## §D — NEEDS CHRIS\n`client.example` · `b.org` · `client.example`\n## §E — other\n`d.org`\n")
out = os.path.join(root, "out.md")
env = dict(os.environ, OUTREACH_ROOT=root)
p = subprocess.run([sys.executable, os.path.join(HERE, "dossier.py"), "--night", "N1", "--slot", "2026-11-04", "--out", out], env=env, capture_output=True, text=True)
ok("dossier.py runs on a scratch root", p.returncode == 0 and os.path.exists(out))
t = open(out, encoding="utf-8").read() if os.path.exists(out) else ""
top = t.split("## ⚠️ Top 10 decisions")[-1].split("\n---")[0]
ok("title + decisions heading", "# 📤 Dossier — 2026-11-04" in t and "## ⚠️ Top 10 decisions" in t)
ok("OM2 cards come before OM1 cards", 0 < t.find("📧 2️⃣ OM2 — Position 1") < t.find("📧 1️⃣ OM1 — Position 1"))
ok("positions newest first per machine (Delta = OM1 #1, Alpha = OM1 #4)", "1️⃣ OM1 — Position 1 · Delta Kids" in t and "1️⃣ OM1 — Position 4 · Alpha CCR&R" in t)
ok("§D paragraph domain is a block (Beta)", "Beta Action** — on the HubSpot block list (b.org)" in top)
ok("§C internal and §E are NOT blocks", "(a.org)" not in top and "(d.org)" not in top)
ok("general inbox is a decision", "goes to a general inbox (info@b.org)" in top)
ok("named leader without address is a decision (Delta)", "Delta Kids** — no leader on the draft" in top and "[Person 0100]" in top)
ok("non-leader recipients are a decision (Gamma)", "Gamma Center** — recipients hold no leader or PD role" in top)
ok("Gate 7 failure is a decision", "Gate 7 read-back FAILED: Cc differs" in top)
ok("duplicate recipient across org records", "person0801@d.org is also a recipient under org:d2" in top)
ok("clean org has no decision line (Alpha)", "Alpha CCR&R**" not in top)
ok("one line per org (Beta reasons joined)", top.count("Beta Action**") == 1)
ok("flagged cards carry ⚠️ see decisions; clean ones do not", "Delta Kids · OR  ⚠️ see decisions" in t and "Alpha CCR&R · OR  ⚠️" not in t)
ok("table header + one row per recipient", "| Name | Title | Email | Source |" in t and t.count("person0212@a.org |") == 1 and t.count("person0373@a.org |") == 1)
ok("sources: 📄 printed, 📄 same page, 📮 inbox", "📄 printed on [a.org/team]" in t and "📄 same page" in t and "📮 general inbox" in t)
ok("not-on-draft people with sweep result", "[Person 0100] (Executive Director) — Apollo: no email" in t and "[Person 1532] (Training Coordinator) — never looked up" in t)
ok("OM2 reasoning names the event and its window (2026-11-09: no keynote-path field)", "OM2: event E Summit, next edition 2027-03-01 (" in t)
ok("internal hold text never shown as fit", "Machine 1 candidate status" not in t)
ok("event page listed", "[e.org/summit](https://e.org/summit)" in t)
ok("no GIF / sending reminders", "GIF" not in t)
# empty top section
w(root, "5_Draft/ledgers/drafts.jsonl", [D("org:a.org", "Alpha CCR&R", "OM-1", 1, "d1", "person0212@a.org", ["person0373@a.org"])])
subprocess.run([sys.executable, os.path.join(HERE, "dossier.py"), "--night", "N1", "--slot", "2026-11-04", "--out", out], env=env, capture_output=True, text=True)
t2 = open(out, encoding="utf-8").read()
ok("empty decisions → 'Nothing needs you tonight.'", "Nothing needs you tonight." in t2)
ok("decisions sit beneath the draft cards (Chris 2026-11-10)", t.find("📧 1️⃣ OM1 — Position 1") < t.find("## ⚠️ Top 10 decisions"))
# never more than 10 decisions, however many orgs are waiting; doubtful orgs are asked about, not drafted
many = orgs + [org("org:w%d.org" % i, "Waiting %02d" % i, "w%d.org" % i, P("Jo Doe", "jo@w%d.org" % i, "Executive Director"), owner_machine="OM-1", threads=[], fit={"status": "doubtful", "reason": "unconfirmed: staff named"}) for i in range(30)]
w(root, "_shared/master/orgs.jsonl", many)
subprocess.run([sys.executable, os.path.join(HERE, "dossier.py"), "--night", "N1", "--slot", "2026-11-04", "--out", out], env=env, capture_output=True, text=True)
t3 = open(out, encoding="utf-8").read(); sec = t3.split("## ⚠️ Top 10 decisions")[-1].split("\n---")[0]
ok("top 10 only: 10 numbered lines, the rest only counted", sec.count("\n10. ") == 1 and "\n11. " not in sec and "20 more are waiting" in sec)
ok("doubtful org is a yes/no question", "Doubtful fit — draft it tomorrow?** Waiting 00" in sec)
ok("waiting orgs get no card", "Position 2 · Waiting" not in t3 and t3.count("# 📧") == 1)
ok("no OM2 drafts → one line", "No OM2 drafts tonight." in t2)
n = sum(1 for _, c in R if c); print("\n%d/%d pass" % (n, len(R))); sys.exit(0 if n == len(R) else 1)
