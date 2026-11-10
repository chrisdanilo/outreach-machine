#!/usr/bin/env python3
"""test_night.py -- the night run, UNTIMED loop (Chris 2026-10-31): sequencing, lock nesting, crash/resume, the pass loop
(minimum met, ceiling, supply exhausted, NO-PROGRESS guard, pass ceiling, Apollo floor), per-pass counters + timing file,
the pre-loop steps (inbox, labels, sendlist, review), the slot (next business day), and the SPLIT: the night never waits or sends. Runs in a throw-away copy of the program tree; the
measurements are injected (NIGHTRUN_METRICS), so the real lock, checkpoints and master list are never touched."""
import json, os, re, shutil, subprocess, sys, tempfile, time
import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_shared", "orchestrator")); import paths  # the one file that knows every folder (2026-11-03)
HERE = os.path.dirname(os.path.abspath(__file__)); ENG = paths.ROOT; MKT = ENG
# 2026-11-03: the REAL programs run against a scratch root (OUTREACH_ROOT) that holds only a settings copy; nothing live is touched
T = tempfile.mkdtemp(prefix="nighttest-")
TE = T
os.makedirs(os.path.join(TE, "_shared", "master")); os.makedirs(os.path.join(TE, "_shared", "orchestrator"))
shutil.copy(paths.SETTINGS, os.path.join(TE, "_shared", "master"))
os.environ["OUTREACH_ROOT"] = TE
LOCK = os.path.join(TE, "_shared", "orchestrator", ".outreach-lock"); MET = os.path.join(T, "metrics.json")
NIGHT = os.path.join(TE, "_shared", "orchestrator", "night"); DRUNS = os.path.join(TE, "5_Draft", "runs"); REPORTS = os.path.join(TE, "6_Report", "ledgers", "reports")
ok = fail = 0
def metrics(supply_m=None, due=5, pass_counts=None, orgs=1000):
    sup = {"due_sources": due, "machines": {m: dict({"draft_eligible": 5, "people_pool": 5, "qualify_pool": 5}, **((supply_m or {}).get(m, {}))) for m in ("OM-1", "OM-2")}}
    json.dump({"supply": sup, "pass_counts": pass_counts or {}, "orgs": orgs}, open(MET, "w"))
def run(args, now=None, mod="nightrun"):
    env = dict(os.environ); env.pop("NIGHTRUN_NOW", None); env["NIGHTRUN_METRICS"] = MET
    if now: env["NIGHTRUN_NOW"] = now
    exe = paths.NIGHTRUN_PY if mod == "nightrun" else paths.LOCK_PY
    r = subprocess.run([sys.executable, exe] + args, capture_output=True, text=True, env=env)
    return r.returncode, r.stdout + r.stderr
def check(name, cond, info=""):
    global ok, fail
    if cond: ok += 1; print("PASS", name)
    else: fail += 1; print("FAIL", name, "::", info[:500])
def state(run): return json.load(open(os.path.join(NIGHT, "runs", run, "state.json")))
def reset():
    if os.path.exists(NIGHT): shutil.rmtree(NIGHT)
    if os.path.exists(DRUNS): shutil.rmtree(DRUNS)
    json.dump({"holder": None}, open(LOCK, "w"))
def do_pass_steps(N1, steps=None, credits=5000, before_draft=None):
    """Drive one pass from the program's own output until it prints PASS n DONE (or LOOP DONE)."""
    outs = []
    for _ in range(12):
        rc, o = run(["next"], N1); outs.append(o)
        if "PASS" in o and "DONE:" in o or "LOOP DONE" in o: break
        if "CREDIT CHECK" in o:
            rc, o2 = run(["credits", "--remaining", str(credits)], N1); outs.append(o2); continue
        m = re.search(r"STEP (DISCOVER|QUALIFY|PEOPLE|DRAFT) ", o)
        if m:
            if m.group(1) == "DRAFT" and before_draft: before_draft()
            run(["done", "--step", m.group(1).lower(), "--status", "ok", "--note", "test"], N1)
    return "\n".join(outs)

def pre(N1):
    for x in ("inbox", "audit", "labels", "sendlist", "review"):
        run(["next"], N1) if x != "inbox" else None
        run(["done", "--step", x, "--status", "ok"], N1)

RUN = "2026-11-01"; N1 = "2026-11-01T21:20:00-07:00"
reset(); metrics()
rc, o = run(["start", "--run", RUN], N1); check("start acquires the night lock (untimed)", rc == 0 and "ACQUIRED by night-run" in o and "untimed" in o, o)
rc, o = run(["start", "--run", RUN], N1); check("a second start while the night is alive YIELDS", rc == 2 and "YIELD" in o, o)
rc, o = run(["next"], N1); check("first step is INBOX", "STEP 1/7 · INBOX" in o and "slot 2026-11-02" in o, o)
rc, o = run(["done", "--step", "discover", "--status", "ok"], N1); check("checkpointing a step that is not current fails closed", rc != 0 and "FAIL CLOSED" in o, o)
run(["done", "--step", "inbox", "--status", "ok"], N1)
rc, o = run(["next"], N1); check("step 2 is the drafts AUDIT", "STEP 2/7 · AUDIT" in o, o)
run(["done", "--step", "audit", "--status", "ok"], N1)
rc, o = run(["next"], N1); check("step 3 is LABELS (state labels only, never send)", "STEP 3/7 · LABELS" in o and "Never send" in o, o)
run(["done", "--step", "labels", "--status", "ok"], N1)
rc, o = run(["next"], N1); check("step 3 is SENDLIST for the slot", "STEP 4/7 · SENDLIST" in o and "sendlist.py build --night 2026-11-01 --slot 2026-11-02" in o, o)
run(["done", "--step", "sendlist", "--status", "ok"], N1)
rc, o = run(["next"], N1); check("step 4 is REVIEW in night-review mode (drafts only)", "STEP 5/7 · REVIEW" in o and "FS_MODE=night-review" in o and "NEVER a send" in o, o)
run(["done", "--step", "review", "--status", "ok"], N1)
# Chris 2026-11-08: loop order is people → draft → discover → qualify (the night starts on the shelf the Supply Run stocked)
rc, o = run(["next"], N1); check("pass 1 starts for both machines and asks for the Apollo credit check before PEOPLE (people is now the first loop step)", "PASS 1 starts — working OM-1, OM-2" in o and "CREDIT CHECK" in o, o)
run(["credits", "--remaining", "3000"], N1)
rc, o = run(["next"], N1); check("PEOPLE gets --machine list and --night, run <night>-p1", "PASS 1 · STEP PEOPLE · run 2026-11-01-p1" in o and "--machine OM-1,OM-2 --night 2026-11-01" in o, o)
rc, o = run(["acquire", "people"], mod="lock"); check("the current loop step nests inside the night lock", rc == 0 and "ACQUIRED-NESTED" in o, o)
rc, o = run(["acquire", "send"], mod="lock"); check("the 7 AM send lock is NOT blocked by the night lock", rc == 0 and "ACQUIRED" in o and json.load(open(LOCK)).get("holder") == "night-run", o)
rc, o = run(["acquire", "send", "--exclusive"], mod="lock"); check("a second send task yields to the first", rc == 2, o)
run(["release", "send"], mod="lock")
run(["release", "people"], mod="lock")
rc, o = run(["acquire", "supply-run"], mod="lock"); check("a supply run yields while the night run is alive", rc == 2 and "HELD BY night-run" in o, o)
rc, o = run(["time-left"], "2026-11-02T04:45:00-07:00"); check("no clock budgets any more (time-left says NO BUDGET)", "NO BUDGET" in o, o)
# CRASH mid-pass (after people printed): session dies; lock quiet 3 h; resume continues at PEOPLE of pass 1
l = json.load(open(LOCK)); l["started"] = l["heartbeat"] = time.time() - 3 * 3600; l.pop("quiet_until", None); json.dump(l, open(LOCK, "w"))
rc, o = run(["start", "--run", RUN], "2026-11-02T00:05:00-07:00"); check("after a crash a new start RESUMES", rc == 0 and "RESUMED" in o, o)
rc, o = run(["next"], "2026-11-02T00:06:00-07:00"); check("resume continues at PEOPLE of pass 1 (not redone, no second credit check)", "PASS 1 · STEP PEOPLE" in o, o)
run(["done", "--step", "people", "--status", "ok"], N1)
rc, o = run(["next"], N1); check("draft step writes this pass's allowance (ceilings 15/50 minus made)", "STEP DRAFT" in o, o)
# pass 1 drafts: OM-1 made 10 (meets minimum), OM-2 made 20
metrics(pass_counts={"2026-11-01-p1": {"sources_swept": 30, "orgs_found": 7, "qualified": {"OM-1": 40, "OM-2": 6}, "people_ready": {"OM-1": 12, "OM-2": 22}, "drafts": {"OM-1": 10, "OM-2": 20}}})
al = json.load(open(os.path.join(DRUNS, "2026-11-01-p1", "allowance.json")))
check("pass 1 allowance = full ceilings", al == {"OM-1": 15, "OM-2": 50}, json.dumps(al))
run(["done", "--step", "draft", "--status", "ok"], N1)
rc, o = run(["next"], N1); check("then DISCOVER with run <night>-p1 and --machines", "STEP DISCOVER · run 2026-11-01-p1" in o and "--machines OM-1,OM-2" in o, o)
run(["done", "--step", "discover", "--status", "ok"], N1)
rc, o = run(["next"], N1); check("qualify is limited to the machines still under minimum", "STEP QUALIFY" in o and "--machines OM-1,OM-2" in o, o)
run(["done", "--step", "qualify", "--status", "ok"], N1)
rc, o = run(["next"], N1); check("pass 1 closes with counters", "PASS 1 DONE" in o and '"sources_swept": 30' in o, o)
rc, o = run(["next"], N1); check("OM-1 met its minimum → pass 2 works OM-2 only", "PASS 2 starts — working OM-2" in o, o)
check("OM-1's stop reason recorded", "minimum met (10 of 10)" in state(RUN)["loop"]["stopped"].get("OM-1", ""), json.dumps(state(RUN)["loop"]["stopped"]))
o = do_pass_steps(N1)
al = json.load(open(os.path.join(DRUNS, "2026-11-01-p2", "allowance.json")))
check("pass 2 allowance: OM-1 0 (not worked), OM-2 50-20=30", al == {"OM-1": 0, "OM-2": 30}, json.dumps(al))
check("pass 2 qualify only for OM-2", "--machines OM-2" in o, o)
# pass 2 produced nothing for OM-2 → NO-PROGRESS guard stops OM-2 → loop done
rc, o = run(["next"], N1); check("NO-PROGRESS: a full pass with 0 drafts/0 people-ready/0 qualified stops the machine → LOOP DONE", "LOOP DONE after 2 pass(es)" in o and "no progress in pass 2" in o, o)
tf = os.path.join(REPORTS, "2026-11-02-timing.md"); tx = open(tf).read() if os.path.exists(tf) else ""
check("timing file written with per-pass counters", "| 1 | OM-1, OM-2 |" in tx and "| 2 | OM-2 |" in tx and "| 30 | 7 | 40 / 6 | 12 / 22 | 10 / 20 | 10 / 20 |" in tx, tx[:1500])
check("timing file has every step timed", "| discover | 1 |" in tx and "| inbox |" in tx, tx[-1500:])
rc, o = run(["next"], "2026-11-02T01:00:00-07:00"); check("loop done → straight to REPORT (no wait, no morning send)", "STEP 7/7 · REPORT" in o and "--date 2026-11-02" in o and "send_later" not in o and "WAKE" not in o, o)
run(["done", "--step", "report", "--status", "ok"], N1)
rc, o = run(["next"], N1); check("then ALL STEPS DONE", "ALL STEPS DONE" in o, o)
rc, o = run(["finish"], N1); check("finish releases the lock", "RELEASED by night-run" in o and not json.load(open(LOCK)).get("holder"), o)

# loop ends AFTER 07:00 ET → still just REPORT (the send task, not the night, sends)
reset(); metrics(pass_counts={"2026-11-02-p1": {"drafts": {"OM-1": 10, "OM-2": 35}, "qualified": {"OM-1": 1, "OM-2": 1}, "people_ready": {"OM-1": 1, "OM-2": 1}}})
run(["start", "--run", "2026-11-02"], "2026-11-02T21:10:00-07:00"); run(["next"], N1); pre(N1)
do_pass_steps(N1)
rc, o = run(["next"], "2026-11-03T05:30:00-07:00"); check("both minimums met in pass 1 → LOOP DONE", "LOOP DONE after 1 pass(es)" in o, o)
rc, o = run(["next"], "2026-11-03T05:30:00-07:00"); check("loop ending after 07:00 ET still goes to REPORT, never a send", "STEP 7/7 · REPORT" in o and "--date 2026-11-03" in o, o)
run(["finish"], N1)

# supply exhausted before any pass
reset(); metrics(supply_m={"OM-1": {"draft_eligible": 0, "people_pool": 0, "qualify_pool": 0}, "OM-2": {"draft_eligible": 0, "people_pool": 0, "qualify_pool": 0}}, due=0)
run(["start", "--run", "2026-11-03"], N1); run(["next"], N1); pre(N1)
rc, o = run(["next"], N1); check("supply exhausted for both → LOOP DONE with 0 passes and the reason", "LOOP DONE after 0 pass(es)" in o and "supply exhausted" in o, o)
run(["finish"], N1)

# Apollo credit floor: people skipped this pass and every later pass
reset(); metrics()
run(["start", "--run", "2026-11-04"], N1); run(["next"], N1); pre(N1)
o = do_pass_steps(N1, credits=100, before_draft=lambda: metrics(pass_counts={"2026-11-04-p1": {"drafts": {"OM-1": 1, "OM-2": 1}, "qualified": {"OM-1": 0, "OM-2": 0}, "people_ready": {"OM-1": 0, "OM-2": 0}}}))
check("credits below the floor (100 < 500) → people skipped, reported", "APOLLO FLOOR" in o, o)
o = do_pass_steps(N1)      # pass 2
check("floor hit earlier → pass 2 people skipped without asking again", "PEOPLE skipped in pass 2" in o and "CREDIT CHECK" not in o, o)
run(["finish"], N1)

# night before Thanksgiving (Wed 11-25) → slot rolls to Fri 11-27: sends delayed, never skipped
reset(); metrics(supply_m={m: {"draft_eligible": 0, "people_pool": 0, "qualify_pool": 0} for m in ("OM-1", "OM-2")}, due=0)
rc, o = run(["start", "--run", "2026-11-25"], "2026-11-25T21:20:00-07:00")
rc, o = run(["next"], N1); check("holiday: slot rolls to the next business day (Fri 11-27)", "slot 2026-11-27" in o, o)
run(["done", "--step", "inbox", "--status", "ok"], N1); run(["next"], N1); run(["done", "--step", "audit", "--status", "ok"], N1); run(["next"], N1); run(["done", "--step", "labels", "--status", "ok"], N1)
rc, o = run(["next"], N1); check("holiday: send list built for 11-27", "--slot 2026-11-27" in o, o)
run(["finish"], N1)
# Thursday night → Friday slot; Friday is not a night (Sun–Thu) but a Thursday run's slot is Friday
reset(); metrics(); run(["start", "--run", "2026-11-05"], "2026-11-05T21:20:00-07:00")
rc, o = run(["next"], N1); check("Thursday night → Friday slot", "slot 2026-11-06" in o, o); run(["finish"], N1)
reset(); metrics(); run(["start", "--run", "2026-11-08"], "2026-11-08T21:20:00-07:00")
rc, o = run(["next"], N1); check("Sunday night → Monday slot", "slot 2026-11-09" in o, o); run(["finish"], N1)

# pure decision function: ceiling + pass ceiling + no-progress
code = r'''
import sys, json; sys.path.insert(0, %r); import nightrun as NR
sup = {"due_sources": 3, "machines": {m: {"draft_eligible": 2, "people_pool": 2, "qualify_pool": 2} for m in ("OM-1","OM-2")}}
mins = {"OM-1": 10, "OM-2": 35}; ce = {"OM-1": 15, "OM-2": 50}
o, n = NR.decide({"OM-1": 15, "OM-2": 5}, mins, ce, sup, None, {}, 3, 25); print("A", o, n)
o, n = NR.decide({"OM-1": 2, "OM-2": 5}, mins, ce, sup, None, {}, 25, 25); print("B", o, n)
last = {"n": 4, "worked": ["OM-1","OM-2"], "drafts": {"OM-1": 0, "OM-2": 3}, "people_ready": {"OM-1": 0, "OM-2": 0}, "qualified": {"OM-1": 0, "OM-2": 0}}
o, n = NR.decide({"OM-1": 2, "OM-2": 5}, mins, ce, sup, last, {}, 4, 25); print("C", o, n)
last2 = dict(last, drafts={"OM-1": 0, "OM-2": 0}, qualified={"OM-1": 3, "OM-2": 0})
o, n = NR.decide({"OM-1": 2, "OM-2": 5}, mins, ce, sup, last2, {}, 4, 25); print("D", o, n)
''' % paths.ORCH
r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=dict(os.environ, NIGHTRUN_METRICS=MET)); o = r.stdout + r.stderr
check("ceiling reached stops a machine even above its minimum", "A ['OM-2']" in o and "ceiling reached (15 of 15)" in o, o)
check("pass ceiling (25) stops every open machine, reported", "B []" in o and "pass ceiling hit (25 passes)" in o, o)
check("no-progress guard stops only the machine with zero progress", "C ['OM-2']" in o and "no progress in pass 4" in o, o)
check("newly qualified orgs count as progress (no stop)", "D ['OM-1']" in o and "OM-2" in o.split("D ")[1], o)
shutil.rmtree(T)
# second start of a day after a FINISHED run opens a new run instead of resuming the finished one (2026-11-02)
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("nr", os.path.join(HERE, "nightrun.py")); nr = _ilu.module_from_spec(_spec); _spec.loader.exec_module(nr); nr.NDIR = tempfile.mkdtemp(prefix="nr2-")
os.makedirs(os.path.join(nr.NDIR, "runs", "2099-01-01"), exist_ok=True)
json.dump({"run": "2099-01-01", "status": "done", "steps": {}, "events": [], "timing": []}, open(os.path.join(nr.NDIR, "runs", "2099-01-01", "state.json"), "w"))
r2 = nr.next_free_run("2099-01-01")
check("second start after a finished run opens 2099-01-01-2", r2 == "2099-01-01-2")
json.dump({"run": "2099-01-01-2", "status": "done", "steps": {}, "events": [], "timing": []}, open(os.path.join(nr.NDIR, "runs", "2099-01-01-2", "state.json") if os.makedirs(os.path.join(nr.NDIR, "runs", "2099-01-01-2"), exist_ok=True) is None else "", "w"))
check("third start opens -3", nr.next_free_run("2099-01-01") == "2099-01-01-3")
json.dump({"run": "2099-01-02", "status": "running", "steps": {"inbox": {"status": "ok"}}, "events": [], "timing": []}, open(os.path.join(nr.NDIR, "runs", "2099-01-02", "state.json") if os.makedirs(os.path.join(nr.NDIR, "runs", "2099-01-02"), exist_ok=True) is None else "", "w"))
check("a crashed (not finished) run is still resumed under its own name", nr.next_free_run("2099-01-02") == "2099-01-02")

# slot never in the past (2026-11-09, CAPA 11/06 R2-4): a late or daytime start rolls the slot to the next business day after now
import datetime as _dt
def _slot(run, when):
    return nr.slot_for(run, _dt.datetime.fromisoformat(when))
check("on-time Sunday night run → Monday slot", _slot("2026-11-08", "2026-11-09T03:45:00+00:00") == "2026-11-09")
check("Sunday night run started Monday 10 AM ET → Tuesday slot (Monday 07:00 ET already past)", _slot("2026-11-08", "2026-11-09T15:10:00+00:00") == "2026-11-10")
check("Friday daytime second start (the R2-4 case) → Monday slot, not the past Friday slot", _slot("2026-11-05-2", "2026-11-06T16:25:00+00:00") == "2026-11-09")
check("Friday 05:00 ET (before the send) keeps the Friday slot", _slot("2026-11-05", "2026-11-06T10:00:00+00:00") == "2026-11-06")

print("\n%d passed, %d failed" % (ok, fail)); sys.exit(1 if fail else 0)
