#!/usr/bin/env python3
"""Gapfix self-tests (2026-10-31): (1) overdue threads older than the old 45-day search are gathered and sent at the next
07:00 ET slot (Rulebook I4); (2) review-hold threads become ONE Zapier DRAFT reply, never a send, and nothing when a
review draft already exists (Rulebook I7). Pure fixtures + a dry --queries in a temp folder. Nothing sent."""
import datetime, importlib.util, json, os, pathlib, subprocess, sys, tempfile
HERE = pathlib.Path(__file__).resolve().parent
import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_shared", "orchestrator")); import paths  # the one file that knows every folder (2026-11-03)
MK = pathlib.Path(paths.ROOT)   # Automations/ (phase layout 2026-11-03)
R = []
def ok(name, cond, extra=""):
    R.append(bool(cond)); print(("PASS " if cond else "FAIL ") + name + (" -> " + extra if extra else ""))

sys.path.insert(0, str(HERE))
import seqrules
cal = seqrules.Calendar()
MON = cal.slot(datetime.date(2026, 11, 2))
th = lambda *ds, **k: {"status": "open", "stage_floor": 0, "sends": [{"date": d, "to": ["person0008@x.org"], "cc": []} for d in ds], **k}
d = seqrules.decide(th("2026-08-18", "2026-08-25"), MON, cal)
ok("seqrules: Email 3 last due 2026-09-01 (60+ days) -> SEND at next slot", d["action"] == "SEND" and d.get("email") == 3, d["action"] + " " + d.get("reason", ""))
d = seqrules.decide(th("2026-08-25"), MON, cal, review_hold=True)
ok("seqrules: review hold -> REVIEW_DRAFT, never SEND", d["action"] == "REVIEW_DRAFT", d["action"])
d = seqrules.decide(th("2026-08-25"), MON, cal, review_hold=True, drafts=1)
ok("seqrules: review hold + draft exists -> nothing", d["action"] == "NONE", d.get("reason", ""))

def engine(folder, plan_rows_spec, code):
    """Run `code` inside a subprocess that imported the engine for `folder` with a master plan."""
    tmp = tempfile.mkdtemp(prefix="gapfix_")
    mp = pathlib.Path(tmp) / "runs" / "2026-11-02"; mp.mkdir(parents=True)
    (mp / "master-plan.json").write_text(json.dumps({"slot": "2026-11-02T07:00:00-05:00", "rows": plan_rows_spec}))
    env = dict(os.environ, FS_MASTER_PLAN=str(mp / "master-plan.json"), FS_MODE="morning", FS_RUNS_OVERRIDE=str(pathlib.Path(tmp) / "eng-runs"))
    prog = ("import sys, importlib.util, json, datetime\nsys.argv=['x','--machine',%r]\n"
            "spec=importlib.util.spec_from_file_location('fs',%r); fs=importlib.util.module_from_spec(spec); spec.loader.exec_module(fs)\n" % (str(folder), str(HERE / "followup_send.py"))) + code
    return subprocess.run([sys.executable, "-c", prog], capture_output=True, text=True, env=env, cwd=str(HERE.parent)), tmp

OM1 = pathlib.Path(paths.machine_dir("OM-1"))
# (1a) master-mode gather reads every master-plan thread of THIS machine in full -- no 6-45-day search window
spec = [{"thread": "aaaaaaaaaaaaaaaa", "machine": "OM-1", "action": "SEND", "email": 3, "org": "Old ELC", "to": [], "cc": []},
        {"thread": "bbbbbbbbbbbbbbbb", "machine": "OM-2", "action": "SEND", "email": 2, "org": "Other machine", "to": [], "cc": []},
        {"thread": "cccccccccccccccc", "machine": "OM-1", "action": "REVIEW_DRAFT", "email": 2, "org": "Held org", "to": [], "cc": []}]
p, tmp = engine(OM1, spec, "a=fs.argparse.Namespace(fire=None, today='2026-11-02', thread=None)\n"
                "import pathlib\nfs.cmd_queries(type('A',(),{'fire':str(pathlib.Path(%r)/'f1'),'today':'2026-11-02'})())\n" % (tempfile.gettempdir()))
out = p.stdout + p.stderr
ok("engine: master gather prints get_thread for the overdue OM-1 thread", "threadId=aaaaaaaaaaaaaaaa" in out, out.strip().splitlines()[-1] if out.strip() else "no output")
ok("engine: master gather includes the review-hold thread", "threadId=cccccccccccccccc" in out)
ok("engine: master gather skips the other machine's thread", "bbbbbbbbbbbbbbbb" not in out)
ok("engine: no 6-45-day due search in master mode", "newer_than:45d" not in out)

# (1b) plan on a thread whose last own send is 60+ days old -> armable Email 3, bound to reply_to_message
code = r'''
FX=fs.FX; cfg,fsb=fs.cfg_block(); fsb=dict(fsb); fsb["enabled_emails"]=["2","3"]; me=fs.me(cfg)
def own(i,date,body):
    return {"id":"m%d"%i,"date":date,"to":[FX["to"]],"cc":[FX["cc1"]],"bcc":[],"body":body,"sender":me,"subject":FX["subject"]}
def mk(sends, live_draft=False):
    return {"thread":FX["thread"],"subject":FX["subject"],"labels":[],"message_count":len(sends),"listed":len(sends),"hidden":0,
            "complete":True,"live_draft":live_draft,"sends":sends,"others":[],"newest":sends[-1]["id"],"newest_is_own":True}
s=[own(1,"2026-08-18T15:00:00Z",FX["greet1"]+",\n\nMy name is Chris"),own(2,"2026-08-25T15:00:00Z","Hey "+FX["greet1"]+",\n\nIs it worth")]
now=datetime.datetime(2026,11,2,12,5,tzinfo=datetime.timezone.utc)
fs.MASTER_PLAN={FX["thread"]:{"thread":FX["thread"],"machine":"OM-1","action":"SEND","email":3,"org":"x","to":[FX["to"]],"cc":[FX["cc1"]]}}
r=fs.plan_rows({"threads":[mk(s)]},cfg,fsb,now=now)[0][0]
print("OVERDUE", r["action"], r.get("email_no"), (r.get("zapier") or {}).get("action"), r["reason"])
fs.MASTER_PLAN={FX["thread"]:{"thread":FX["thread"],"machine":"OM-1","action":"REVIEW_DRAFT","email":3,"org":"x","to":[FX["to"]],"cc":[FX["cc1"]]}}
r=fs.plan_rows({"threads":[mk(s)]},cfg,fsb,now=now)[0][0]
print("REVIEW", r["action"], r.get("kind"), (r.get("zapier") or {}).get("action"), r["reason"])
r=fs.plan_rows({"threads":[mk(s, live_draft=True)]},cfg,fsb,now=now)[0][0]
print("REVIEWDRAFTEXISTS", r["action"], r["reason"])
'''
p, _ = engine(OM1, [], code)
lines = {l.split()[0]: l for l in p.stdout.splitlines() if l.split()}
ov = lines.get("OVERDUE", p.stderr[-300:])
ok("engine: 60+-day overdue Email 3 is armable at the next slot (not filtered by age)", ov.startswith("OVERDUE armable 3 reply_to_message"), ov)
rv = lines.get("REVIEW", p.stderr[-300:])
ok("engine: review-hold row -> armable DRAFT bound to draft_v2_reply (never reply_to_message)", rv.startswith("REVIEW armable draft draft_v2_reply"), rv)
rx = lines.get("REVIEWDRAFTEXISTS", p.stderr[-300:])
ok("engine: review-hold with a draft already on the thread -> nothing", rx.startswith("REVIEWDRAFTEXISTS skip"), rx)

# (2) the real master plan for Monday carries the review-hold rows to the engine (no longer just 'owed')
mp = json.loads((pathlib.Path(paths.runs("send")) / "2026-11-02" / "master-plan.json").read_text())
ok("master plan: review drafts are engine rows", all(r["action"] != "REVIEW_DRAFT" for r in mp.get("not_sent", [])),
   "rows %d · review rows %d" % (len(mp["rows"]), sum(1 for r in mp["rows"] if r["action"] == "REVIEW_DRAFT")))
print("\n%d/%d gapfix tests pass" % (sum(R), len(R)))
sys.exit(0 if all(R) else 1)
