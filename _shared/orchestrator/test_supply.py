#!/usr/bin/env python3
"""test_supply.py -- the SUPPLY RUN (Chris 2026-11-08): sequencing (discover → qualify → events → people → shelf), its own caps in every
order line, the events step skipped until enabled, the Apollo credit check, the HARD STOP (steps skipped and reported, shelf still measured),
the daytime hard stop (19:30), the refusal too close to the night run, yielding to a live night run, lock nesting under supply-run,
crash/resume, and that no order line ever mentions a draft, a label, Zapier or a send. Scratch root (OUTREACH_ROOT); nothing live is touched."""
import json, os, re, shutil, subprocess, sys, tempfile, time
import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_shared", "orchestrator")); import paths
T = tempfile.mkdtemp(prefix="supplytest-"); TE = T
os.makedirs(os.path.join(TE, "_shared", "master")); os.makedirs(os.path.join(TE, "_shared", "orchestrator"))
shutil.copy(paths.SETTINGS, os.path.join(TE, "_shared", "master"))
os.environ["OUTREACH_ROOT"] = TE
LOCK = os.path.join(TE, "_shared", "orchestrator", ".outreach-lock"); MET = os.path.join(T, "metrics.json")
SUP = os.path.join(TE, "_shared", "orchestrator", "supply")
json.dump({"supply": {"due_sources": 599, "machines": {m: {"draft_eligible": 3, "people_pool": 40, "qualify_pool": 500} for m in ("OM-1", "OM-2")}}, "pass_counts": {}, "orgs": 3000}, open(MET, "w"))
ok = fail = 0
def run(args, now=None, mod="supply"):
    env = dict(os.environ); env.pop("SUPPLYRUN_NOW", None); env["NIGHTRUN_METRICS"] = MET
    if now: env["SUPPLYRUN_NOW"] = now
    exe = os.path.join(os.path.dirname(os.path.abspath(__file__)), "supplyrun.py") if mod == "supply" else paths.LOCK_PY
    r = subprocess.run([sys.executable, exe] + args, capture_output=True, text=True, env=env)
    return r.returncode, r.stdout + r.stderr
def check(name, cond, info=""):
    global ok, fail
    if cond: ok += 1; print("PASS", name)
    else: fail += 1; print("FAIL", name, "::", info[:600])
def reset():
    if os.path.exists(SUP): shutil.rmtree(SUP)
    json.dump({"holder": None}, open(LOCK, "w"))
FORBIDDEN = re.compile(r"draft|label|zapier|send_|reply_to|sendlist", re.I)

N1 = "2026-11-09T01:00:00-07:00"
reset()
rc, o = run(["start"], N1); check("start at 1 AM acquires the lock as supply-run with a 04:30 hard stop", rc == 0 and "ACQUIRED by supply-run" in o and "hard stop 04:30" in o and "supply-2026-11-09" in o, o)
rc, o = run(["start"], N1); check("a second start while alive YIELDS", rc == 2 and "YIELD" in o, o)
rc, o = run(["next"], N1); check("step 1 DISCOVER carries this run's caps and all machines", "STEP 1/5 · DISCOVER" in o and "--run supply-2026-11-09 --machines OM-1,OM-2 --sources 90 --branches 25 --searches 90" in o, o)
check("no discover order mentions drafting, labels, Zapier or sending", not FORBIDDEN.search(o.replace("Do not run its REPORT step", "")), o)
rc, o = run(["acquire", "discover"], mod="lock"); check("the current step nests inside the supply lock", rc == 0 and "ACQUIRED-NESTED" in o and "supply-run" in o, o)
rc, o = run(["acquire", "qualify"], mod="lock"); check("a different step does NOT nest (yields)", rc == 2, o)
rc, o = run(["acquire", "night-run", "--exclusive"], mod="lock"); check("a night run yields while the supply run is alive", rc == 2 and "HELD BY supply-run" in o, o)
rc, o = run(["acquire", "send"], mod="lock"); check("the 7 AM send lock is independent of the supply lock", rc == 0 and json.load(open(LOCK)).get("holder") == "supply-run", o); run(["release", "send"], mod="lock")
rc, o = run(["release", "discover"], mod="lock"); check("step release is nested (supply lock kept)", "RELEASED-NESTED" in o, o)
rc, o = run(["done", "--step", "qualify", "--status", "ok"], N1); check("checkpointing a step that is not current fails closed", rc != 0 and "FAIL CLOSED" in o, o)
run(["done", "--step", "discover", "--status", "ok", "--note", "11 batches"], N1)
rc, o = run(["next"], N1); check("step 2 QUALIFY with cap 200, every machine", "STEP 2/5 · QUALIFY" in o and "--run supply-2026-11-09 --cap 200" in o and "--machines" not in o, o)
# crash mid-qualify: lock quiet 3 h; a new start resumes at QUALIFY
l = json.load(open(LOCK)); l["started"] = l["heartbeat"] = time.time() - 3 * 3600; json.dump(l, open(LOCK, "w"))
rc, o = run(["start"], "2026-11-09T01:40:00-07:00"); check("after a crash a new start RESUMES the same run", rc == 0 and "RESUMED" in o and "supply-2026-11-09 " in o, o)
rc, o = run(["next"], "2026-11-09T01:41:00-07:00"); check("resume continues at QUALIFY (discover not redone)", "STEP 2/5 · QUALIFY" in o, o)
run(["done", "--step", "qualify", "--status", "ok"], N1)
rc, o = run(["next"], N1); check("step 3 EVENTS is skipped (retired 2026-11-09), with the reason", "EVENTS skipped" in o and "retired 2026-11-09" in o, o)
rc, o = run(["next"], N1); check("before PEOPLE it asks for the Apollo credit check", "CREDIT CHECK" in o, o)
rc, o = run(["credits", "--remaining", "3000"], N1); check("credits above the floor → OK", "CREDITS OK" in o, o)
rc, o = run(["next"], N1); check("step 4 PEOPLE with cap 40, both machines, no --night", "STEP 4/5 · PEOPLE" in o and "--run supply-2026-11-09 --machine OM-1,OM-2 --cap 40" in o and "--night" not in o, o)
run(["done", "--step", "people", "--status", "partial", "--note", "26 ready / 14 held"], N1)
rc, o = run(["next"], N1); check("step 5 SHELF: rebuild then measure", "STEP 5/5 · SHELF" in o and "build_master.py" in o and "supplyrun.py shelf" in o, o)
rc, o = run(["shelf"], N1); check("shelf prints the table and writes shelf-latest.json", "Ready to draft" in o and os.path.exists(os.path.join(SUP, "shelf-latest.json")) and json.load(open(os.path.join(SUP, "shelf-latest.json")))["run"] == "supply-2026-11-09", o)
run(["done", "--step", "shelf", "--status", "ok"], N1)
rc, o = run(["next"], N1); check("then ALL STEPS DONE", "ALL STEPS DONE" in o, o)
rc, o = run(["finish"], N1); check("finish releases the lock and reports the skipped step", "RELEASED by supply-run" in o and not json.load(open(LOCK)).get("holder") and "events (" in o, o)
tx = open(os.path.join(SUP, "runs", "supply-2026-11-09", "timing.md")).read()
check("timing file has every step and the shelf", "| discover |" in tx and "| people |" in tx and "Shelf at the end" in tx, tx[:800])
rc, o = run(["start"], "2026-11-09T02:30:00-07:00"); check("a second start on a finished day opens supply-<date>-2", rc == 0 and "supply-2026-11-09-2" in o, o); run(["finish"])

# HARD STOP: started 01:00, clock passes 04:30 during qualify → people/events skipped, shelf still measured
reset(); run(["start"], N1); run(["next"], N1); run(["done", "--step", "discover", "--status", "ok"], N1); run(["next"], N1)
rc, o = run(["done", "--step", "qualify", "--status", "partial", "--note", "ran out of time"], "2026-11-09T04:35:00-07:00")
rc, o = run(["next"], "2026-11-09T04:35:00-07:00"); check("past the hard stop: EVENTS skipped with the hard-stop reason", "HARD STOP" in o and "EVENTS skipped" in o, o)
rc, o = run(["next"], "2026-11-09T04:36:00-07:00"); check("past the hard stop: PEOPLE skipped too (no credit check asked)", "HARD STOP" in o and "PEOPLE skipped" in o and "CREDIT CHECK" not in o, o)
rc, o = run(["next"], "2026-11-09T04:37:00-07:00"); check("the SHELF step still runs after the hard stop", "STEP 5/5 · SHELF" in o, o)
run(["shelf"], N1); run(["done", "--step", "shelf", "--status", "ok"], N1); rc, o = run(["finish"], N1); check("finish lists both skipped steps", "events (" in o and "people (" in o, o)

# Apollo floor
reset(); run(["start"], N1)
for s_ in ("discover", "qualify"): run(["next"], N1); run(["done", "--step", s_, "--status", "ok"], N1)
run(["next"], N1); run(["next"], N1); rc, o = run(["credits", "--remaining", "100"], N1); check("credits below the floor → people skipped, reported", "APOLLO FLOOR" in o, o)
rc, o = run(["next"], N1); check("people skipped after the floor", "PEOPLE skipped" in o, o); run(["finish"], N1)

# daytime start by hand → 19:30 hard stop; evening start → refused
reset(); rc, o = run(["start"], "2026-11-09T14:00:00-07:00"); check("a daytime start gets the 19:30 hard stop", rc == 0 and "hard stop 19:30" in o, o); run(["finish"], N1)
reset(); rc, o = run(["start"], "2026-11-09T20:00:00-07:00"); check("a start at 20:00 is REFUSED (too close to the 20:41 night run) and takes no lock", rc == 2 and "REFUSED" in o and not json.load(open(LOCK)).get("holder"), o)
# a live night run → the supply run yields
reset(); json.dump({"holder": "night-run", "fire": "2026-11-08", "started": time.time(), "heartbeat": time.time(), "started_iso": "x"}, open(LOCK, "w"))
rc, o = run(["start"], N1); check("yields to a live night run", rc == 2 and "YIELD" in o and "HELD BY night-run" in o, o)
print("\n%d passed, %d failed" % (ok, fail)); shutil.rmtree(T, ignore_errors=True); sys.exit(1 if fail else 0)
