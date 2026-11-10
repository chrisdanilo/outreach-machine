#!/usr/bin/env python3
"""test_split.py -- the two-task split (Chris 2026-10-31): the night run never sends; the separate 7 AM send task sends ONLY
the rows on the night's FINAL approved send list. Flagged = not approved. Everything runs in throw-away folders; the real
lock, send lists, runs folders and Gmail are never touched (no Zapier call is ever made by a test)."""
import json, os, re, shutil, subprocess, sys, tempfile
import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_shared", "orchestrator")); import paths  # the one file that knows every folder (2026-11-03)
HERE = os.path.dirname(os.path.abspath(__file__)); ENG = paths.ROOT; MKT = ENG   # phase layout (2026-11-03): paths.py names every folder
OM1 = paths.machine_dir("OM-1")
OM2 = paths.machine_dir("OM-2")
T = tempfile.mkdtemp(prefix="splittest-")
ok = fail = 0
def check(name, cond, info=""):
    global ok, fail
    if cond: ok += 1; print("PASS", name)
    else: fail += 1; print("FAIL", name, "::", str(info)[:600])
def sh(args, env=None):
    e = dict(os.environ); e.update(env or {})
    r = subprocess.run(args, capture_output=True, text=True, env=e); return r.returncode, r.stdout + r.stderr

# ---------------------------------------------------------------- 1. the night orders contain no send path
rc, night = sh([sys.executable, paths.RUN_PY, "night"])
rc2, read = sh([sys.executable, paths.RUN_PY, "read"])
src = open(paths.NIGHTRUN_PY, encoding="utf-8").read()
def send_mentions(txt):
    return [l for l in txt.splitlines() if re.search(r"reply_to_message|gmail_reply_to_email|send_later|FS_MODE=send\b", l)
            and not re.search(r"never|NEVER|no reply_to_message|REFUSES|refuses", l)]
check("night orders print OK and say NEVER SEND EMAIL", rc == 0 and "NEVER SEND EMAIL" in night, night[:300])
check("night orders: every mention of a send action is a prohibition", not send_mentions(night), send_mentions(night))
check("read orders (the night's inbox step) have no send path", rc2 == 0 and not send_mentions(read), send_mentions(read))
check("nightrun.py has no send / wake / morning code", not send_mentions(src) and "wait_step" not in src and "def cmd_sleep" not in src, send_mentions(src))
st = json.load(open(paths.SETTINGS))
check("night steps = inbox, labels, sendlist, review, loop, report (no send step)", st["night"]["steps"] == ["inbox", "labels", "sendlist", "review", "loop", "report"], st["night"]["steps"])
check("live sends only in FS_MODE=send", st["sender"].get("live_mode") == "send", st["sender"].get("live_mode"))
rc, o = sh([sys.executable, paths.RUN_PY, "morning"]); check("the retired morning sender is not a mode", rc != 0 and "usage" in o, o)
rc, o = sh([sys.executable, paths.RUN_PY, "send"]); check("send orders print, approved-list only", rc == 0 and "approved" in o.lower() and "Email 1" in o, o[:300])

# ---------------------------------------------------------------- 2. flagged = not approved (pure)
import sendlist as SLM
base_row = {"thread": "1a00000000000001", "action": "SEND", "email": 2, "notes": [], "reason": "Email 2 due"}
base_org = {"org_id": "org:example-ccrr.org", "name": "Example CCR&R", "domains": ["example-ccrr.org"], "flags": [], "fit": {"status": "ok"},
            "threads": [{"thread_id": "1a00000000000001", "status": "active"}]}
def F(row=None, org=None, rul=None):
    r = dict(base_row, **(row or {})); g = json.loads(json.dumps(base_org)); g.update(org or {}); return SLM.flags_of(r, g, rul or [])
check("clean SEND row is approved", F() == [], F())
check("Email 1 is never approved", F({"email": 1}) != [], F({"email": 1}))
check("REVIEW_DRAFT not approved", F({"action": "REVIEW_DRAFT"}) != [])
check("READ (uncertain) not approved", F({"action": "READ"}) != [])
check("HELD not approved", F({"action": "HELD"}) != [])
check("⚠ note not approved", F({"notes": ["⚠ two machines own this org"]}) != [])
check("successor needing Chris not approved", F({"notes": ["J6 successor — Chris to pick"]}) != [])
check("doubtful fit not approved", F(org={"fit": {"status": "doubtful"}}) != [])
check("org REVIEW HOLD flag not approved", F(org={"flags": ["REVIEW HOLD: reply mentions budget"]}) != [])
check("this thread ⏸ not approved", F(org={"threads": [{"thread_id": "1a00000000000001", "status": "hold⏸"}]}) != [])
check("another thread of the org ⚠ not approved", F(org={"threads": [{"thread_id": "1a00000000000001", "status": "active"}, {"thread_id": "1a00000000000002", "status": "attention⚠"}]}) != [])
check("thread under review hold not approved", F(org={"threads": [{"thread_id": "1a00000000000001", "status": "active", "review_hold": True}]}) != [])
check("open ruling naming the domain not approved", F(rul=[{"id": "R9", "status": "open", "question": "Is example-ccrr.org in OM-1 or OM-2?"}]) != [])
check("open ruling about another org does not block", F(rul=[{"id": "R9", "status": "open", "question": "Is other-org.org a vendor?"}]) == [])

# ---------------------------------------------------------------- 3. list final + check refusals
SLM.SL = os.path.join(T, "send-lists"); os.makedirs(SLM.SL)
def write_list(d, **kw):
    doc = {"kind": "approved-send-list", "slot": d, "final": True, "built_at": d + "T03:00:00+00:00", "night_run": "x", "rows": [], "not_approved": []}
    doc.update(kw); json.dump(doc, open(os.path.join(SLM.SL, d + ".json"), "w")); return doc
class A: pass
a = A(); a.night = "2026-11-01"; a.slot = "2026-11-02"
write_list("2026-11-02", rows=[{"thread": "t", "machine": "OM-1"}])
import io, contextlib
buf = io.StringIO()
with contextlib.redirect_stdout(buf): rc = SLM.build(a)
check("a FINAL list is never changed (resumed night / later pass)", rc == 0 and "ALREADY FINAL" in buf.getvalue() and json.load(open(os.path.join(SLM.SL, "2026-11-02.json")))["rows"] == [{"thread": "t", "machine": "OM-1"}], buf.getvalue())
check("night of Sun 11-01 → Monday 11-02 slot", str(SLM.slot_for_night("2026-11-01")) == "2026-11-02")
check("night of Wed 11-25 → Fri 11-27 (Thanksgiving: delayed, never skipped)", str(SLM.slot_for_night("2026-11-25")) == "2026-11-27")
def chk(date, env_now=None):
    b = A(); b.date = date; out = io.StringIO()
    with contextlib.redirect_stdout(out): rc = SLM.check(b)
    return rc, out.getvalue()
rc, o = chk("2026-11-02"); check("check: today's final list → LIST OK", rc == 0 and "LIST OK" in o, o)
rc, o = chk("2026-11-03"); check("check: no list → NO APPROVED LIST, send nothing", rc == 2 and "NO APPROVED LIST" in o, o)
write_list("2026-11-04", final=False); rc, o = chk("2026-11-04"); check("check: non-final list → NO SEND", rc == 2 and "NO SEND" in o, o)
write_list("2026-11-05", kind="review-list"); rc, o = chk("2026-11-05"); check("check: a review list is not a send list", rc == 2, o)
rc, o = chk("2026-11-07"); check("check: Saturday → NO SEND", rc == 2 and "not a business day" in o, o)
rc, o = chk("2026-11-26"); check("check: Thanksgiving → NO SEND", rc == 2 and "not a business day" in o, o)

# ---------------------------------------------------------------- 4. the engine's --intent gate (no Zapier call ever made)
TID, OTHER = "1a0000000000aaaa", "1a0000000000bbbb"
TR = os.path.join(T, "root"); os.makedirs(os.path.join(TR, "_shared", "master")); os.makedirs(os.path.join(T, "lists"))
shutil.copytree(paths.TEMPLATES, os.path.join(TR, "5_Draft", "programfiles", "templates"))
def settings(**kw):
    s = json.loads(json.dumps(st)); s["sender"].update({"live": True, "live_mode": "send", "live_from": "2026-01-01"}); s["sender"].update(kw)
    json.dump(s, open(os.path.join(TR, "_shared", "master", "settings.json"), "w"))
def lst(d, rows, **kw):
    doc = {"kind": "approved-send-list", "slot": d, "final": True, "built_at": d + "T04:00:00+00:00", "rows": rows}; doc.update(kw)
    p = os.path.join(T, "lists", d + ".json"); json.dump(doc, open(p, "w")); return p
def fire(name, kind=None):
    d = os.path.join(T, "fires", name); shutil.rmtree(d, ignore_errors=True); os.makedirs(os.path.join(d, "raw"))
    row = {"thread": TID, "action": "send", "zapier": {"action": "reply_to_message", "tool_name": "gmail_reply_to_email"}}
    if kind: row.update(kind=kind, zapier={"action": "draft_v2_reply", "tool_name": "gmail_create_draft_reply"})
    json.dump({"rows": [row]}, open(os.path.join(d, "armed.json"), "w")); return d
def intent(fd, plan, mode, now, thread=TID):
    env = {"FS_MASTER_PLAN": plan, "FS_RUNS_OVERRIDE": os.path.join(T, "runs"), "FS_NOW_OVERRIDE": now, "OUTREACH_ROOT": TR}
    if mode: env["FS_MODE"] = mode
    else: env["FS_MODE"] = ""
    return sh([sys.executable, os.path.join(HERE, "followup_send.py"), "--machine", OM1, "--intent", "--thread", thread, "--fire", fd], env)
settings()
GOOD = lst("2026-11-02", [{"thread": TID, "action": "SEND", "email": 2, "machine": "OM-1"}])
rc, o = intent(fire("n1"), GOOD, "night-review", "2026-11-02T12:05:00Z"); check("the NIGHT (night-review) can never send, even an approved row", rc == 1 and "REFUSED" in o and "7 AM send task" in o, o)
rc, o = intent(fire("n2"), GOOD, None, "2026-11-02T12:05:00Z"); check("no mode → refused", rc == 1 and "REFUSED" in o, o)
rc, o = intent(fire("n3"), lst("2026-11-02b", [{"thread": OTHER, "action": "SEND"}], slot="2026-11-02"), "send", "2026-11-02T12:05:00Z"); check("send task: thread not on the list → refused", rc == 1 and "not an approved SEND" in o, o)
rc, o = intent(fire("n4"), lst("2026-11-02c", [{"thread": TID, "action": "SEND"}], slot="2026-11-02", final=False), "send", "2026-11-02T12:05:00Z"); check("send task: list not final → refused", rc == 1 and "FINAL" in o, o)
rc, o = intent(fire("n5"), GOOD, "send", "2026-11-02T11:55:00Z"); check("send task: before 07:00 ET → refused", rc == 1 and "before 07:00 ET" in o, o)
SAT = lst("2026-11-07", [{"thread": TID, "action": "SEND"}])
rc, o = intent(fire("n6"), SAT, "send", "2026-11-07T12:05:00Z"); check("send task: Saturday → refused", rc == 1 and "not a business day" in o, o)
rc, o = intent(fire("n7"), GOOD, "send", "2026-11-03T12:05:00Z"); check("send task: yesterday's list → refused", rc == 1 and "today's FINAL" in o, o)
settings(live=False); rc, o = intent(fire("n8"), GOOD, "send", "2026-11-02T12:05:00Z"); check("sender.live false → refused", rc == 1 and "sender.live is false" in o, o); settings()
fd = fire("go"); rc, o = intent(fd, GOOD, "send", "2026-11-02T12:05:00Z"); check("send task, approved row, 07:05 ET Monday → GO (reply_to_message)", rc == 0 and o.startswith("GO") and "reply_to_message" in o, o)
rc, o = intent(fd, GOOD, "send", "2026-11-02T12:06:00Z"); check("never twice: a second intent for the same thread is refused", rc == 1 and "already attempted" in o, o)
REV = lst("2026-11-02r", [{"thread": TID, "action": "REVIEW_DRAFT"}], kind="review-list", slot="2026-11-02")
rc, o = intent(fire("d1", kind="draft"), REV, "night-review", "2026-11-02T03:00:00Z"); check("night review step: a review-hold DRAFT is allowed (draft action, not a send)", rc == 0 and "draft_v2_reply" in o and "NOT a send" in o, o)
rc, o = intent(fire("d2", kind="draft"), REV, "send", "2026-11-02T12:05:00Z"); check("send task cannot make review drafts", rc == 1 and "REFUSED" in o, o)

# ---------------------------------------------------------------- 5. overnight reply → skipped by the send task
code = r'''
import os, sys, json
sys.argv = ["x", "--machine", %r]; sys.path.insert(0, %r)
import followup_send as FS
cfg, fs = FS.cfg_block()
g = {"threads": [{"thread": %r, "subject": "s", "sends": [], "others": [{"date": "2026-11-02T10:30:00+00:00", "sender": "dir@example.org"}]},
                 {"thread": %r, "subject": "s", "sends": [], "others": [{"date": "2026-11-01T10:30:00+00:00", "sender": "old@example.org"}]}]}
FS.MASTER_PLAN = {%r: {"thread": %r, "action": "SEND"}, %r: {"thread": %r, "action": "REVIEW_DRAFT"}}
rows = FS.plan_rows(g, cfg, fs, now=FS.parse_dt("2026-11-02T12:05:00+00:00"))
rows = rows[0] if isinstance(rows, tuple) else rows
print(json.dumps([[r["thread"], r["action"], r["reason"]] for r in rows]))
''' % (OM1, HERE, TID, OTHER, TID, TID, OTHER, OTHER)
rc, o = sh([sys.executable, "-c", code], {"FS_MODE": "send", "FS_MASTER_PLAN": GOOD, "FS_RUNS_OVERRIDE": os.path.join(T, "runs"), "OUTREACH_ROOT": TR})
check("a reply that arrived after the list was built → held, not sent", "changed since the approved list was made" in o and "dir@example.org" in o, o)
check("a REVIEW_DRAFT row is skipped by the send task", "not an approved send on the list" in o, o)
code2 = "import sys; sys.argv=['x','--machine',%r]; sys.path.insert(0, " + repr(HERE) + "); import followup_send as FS; print(FS.this_machine())"
rc, o1 = sh([sys.executable, "-c", code2 % OM1], {"OUTREACH_ROOT": TR}); rc, o2 = sh([sys.executable, "-c", code2 % OM2], {"OUTREACH_ROOT": TR})
check("the sender knows which machine it runs for from the folder name (OM-1 / OM-2)", o1.strip() == "OM-1" and o2.strip() == "OM-2", o1 + o2)

# ---------------------------------------------------------------- 6. the two locks never block each other
TL = os.path.join(T, "lk"); os.makedirs(os.path.join(TL, "_shared", "orchestrator", "night")); os.environ["OUTREACH_ROOT"] = TL   # the real lock.py, pointed at a scratch root
LK = paths.LOCK_PY
rc, o = sh([sys.executable, LK, "acquire", "night-run"]); check("night lock acquired", rc == 0, o)
rc, o = sh([sys.executable, LK, "acquire", "send", "--exclusive"]); check("send lock acquired while the night holds its lock", rc == 0 and "ACQUIRED by send" in o, o)
rc, o = sh([sys.executable, LK, "acquire", "send", "--exclusive"]); check("a second send task yields", rc == 2, o)
rc, o = sh([sys.executable, LK, "acquire", "discover"]); check("the send lock does not let a stray step past the night lock", rc == 2, o)
sh([sys.executable, LK, "release", "send"]); sh([sys.executable, LK, "release", "night-run"])

shutil.rmtree(T)
print("\n%d passed, %d failed" % (ok, fail)); sys.exit(1 if fail else 0)
