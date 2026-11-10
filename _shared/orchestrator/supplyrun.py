#!/usr/bin/env python3
"""supplyrun.py — THE SUPPLY RUN sequencer (Chris 2026-11-08). One run a day, ~1 AM MT, every day of the week.

Job in one sentence: before the night run, sweep the due sources, qualify what was found, check event certainty (once Chris
rules on the triggers), and find people — so the night run starts on a stocked shelf and spends its time on drafts.

It is the night run's little sibling and reuses everything: the same step launchers (run.py discover|qualify|people), the same
lock file (holder "supply-run", nesting exactly like "night-run"), the same settings file (block "supply"), the same ledgers.
Differences, on purpose:
  - It NEVER drafts, never reads or writes Gmail, never sends, never writes a send list. Steps: discover → qualify → events → people → shelf.
  - It is TIMED: a hard stop (settings supply.hard_stop_local, 04:30 MT) so it has released everything before the 06:52 ET send task.
    Started by hand in the daytime, the hard stop is 19:30 MT so it is gone before the 20:41 night run. Unfinished steps are skipped and reported.
  - One pass, fixed caps (settings supply.caps) — its own session has its own 200-web-search platform budget.
  - It yields if a night run is alive (the shared lock), and the night run's steps yield to it the same way.
Usage (the launcher prints these): start | next | done --step S --status ok|partial|failed|skipped --note "…" | credits --remaining N | finish | status
"""
import argparse, datetime as dt, json, os, subprocess, sys
from zoneinfo import ZoneInfo
import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_shared", "orchestrator")); import paths
import nightrun as NR            # supply() — the shelf measure — and the small helpers; nothing here changes the night run's state

S = paths.settings(); SP = S["supply"]
MT = ZoneInfo(SP["timezone"])
STEPS = SP["steps"]; CAPS = SP["caps"]; HOLDER = "supply-run"
SDIR = paths.SUPPLY; CUR = paths.SUPPLY_CUR
MACHINES = paths.machines()

def now():
    v = os.environ.get("SUPPLYRUN_NOW")
    return dt.datetime.fromisoformat(v).astimezone(dt.timezone.utc) if v else dt.datetime.now(dt.timezone.utc)
def iso(t=None): return (t or now()).isoformat(timespec="seconds")
def rj(p, d=None): return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else d
def wj(p, o):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"; json.dump(o, open(tmp, "w", encoding="utf-8"), indent=1, ensure_ascii=False, sort_keys=True); os.replace(tmp, p)
def lock(*a):
    r = subprocess.run([sys.executable, paths.LOCK_PY] + list(a), capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()
def run_paths(run): d = os.path.join(SDIR, "runs", run); return d, os.path.join(d, "state.json")
def load(run): return rj(run_paths(run)[1]) or {"run": run, "steps": {}, "events": [], "timing": []}
def save(st): wj(run_paths(st["run"])[1], st); write_timing(st)
def ev(st, msg): st["events"].append({"at": iso(), "what": msg})
def holder(step): return SP["holders"].get(step)
def setcur(st, step, status="running"):
    wj(CUR, {"run": st["run"], "status": status, "step": step, "step_holder": holder(step), "deadline": st.get("deadline"), "updated": iso()})
def cur():
    c = rj(CUR)
    if not c: raise SystemExit("FAIL CLOSED: no supply run is in progress (run: supplyrun.py start)")
    return c
def first_open(st):
    for s in STEPS:
        if st["steps"].get(s, {}).get("status") not in ("ok", "partial", "failed", "skipped"): return s
    return None
def default_run(t=None): return "supply-" + (t or now()).astimezone(MT).date().isoformat()
def next_free_run(run):
    base, n = run, 1
    while load(run).get("status") == "done": n += 1; run = "%s-%d" % (base, n)
    return run

def deadline_for(t):
    """Hard stop for a run started at t (MT). Night-time start (before the stop) → today's hard_stop_local. Daytime start → 19:30,
    so the run is gone before the 20:41 night run. A start between 19:30 and midnight is refused — too close to the night run."""
    loc = t.astimezone(MT); hh, mm = map(int, SP["hard_stop_local"].split(":"))
    stop = loc.replace(hour=hh, minute=mm, second=0, microsecond=0)
    if loc < stop: return stop
    evening = loc.replace(hour=19, minute=30, second=0, microsecond=0)
    if loc < evening: return evening
    return None
def past_deadline(st): return st.get("deadline") and now() >= dt.datetime.fromisoformat(st["deadline"])
def mtfmt(t): return dt.datetime.fromisoformat(t).astimezone(MT).strftime("%H:%M") if t else "—"

# ------------------------------------------------------------------ timing file (same shape as the night's)
def tstart(st, what):
    if not any(x["what"] == what and x.get("end") is None for x in st["timing"]): st["timing"].append({"what": what, "start": iso(), "end": None, "status": None, "note": ""})
def tend(st, what, status, note):
    for x in reversed(st["timing"]):
        if x["what"] == what and x.get("end") is None:
            x.update(end=iso(), status=status, note=(note or "")[:160]); return
def write_timing(st):
    d, _ = run_paths(st["run"]); L = ["# Supply run timing — %s" % st["run"], "",
         "Started %s MT · hard stop %s MT · %s" % (mtfmt(st.get("started")), mtfmt(st.get("deadline")), ("finished %s MT" % mtfmt(st.get("finished"))) if st.get("finished") else "running"), "",
         "| Step | Start MT | End MT | Minutes | Status | Note |", "|---|---|---|---|---|---|"]
    for x in st["timing"]:
        mins = ("%.1f" % ((dt.datetime.fromisoformat(x["end"]) - dt.datetime.fromisoformat(x["start"])).total_seconds() / 60)) if x.get("end") else "…"
        L.append("| %s | %s | %s | %s | %s | %s |" % (x["what"], mtfmt(x["start"]), mtfmt(x.get("end")), mins, x.get("status") or "running", (x.get("note") or "").replace("|", "/")))
    if st.get("shelf"): L += ["", "## Shelf at the end of this run", shelf_text(st["shelf"])]
    os.makedirs(d, exist_ok=True); open(os.path.join(d, "timing.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")

def shelf_text(sh):
    rows = ["| Machine | Ready to draft (open, fit, people found, never emailed) | Fit and open, people still to find | Found, not yet qualified |", "|---|---|---|---|"]
    for m in MACHINES:
        s = sh["machines"][m]; rows.append("| %s | %d | %d | %d |" % (m, s["draft_eligible"], s["people_pool"], s["qualify_pool"]))
    rows.append(""); rows.append("Places still due for a discovery sweep: %d" % sh["due_sources"])
    return "\n".join(rows)

# ------------------------------------------------------------------ commands
COMMON = ("Skip that order set's MOUNT step (already mounted). Its LOCK line prints ACQUIRED-NESTED and its RELEASE line prints RELEASED-NESTED — "
          "correct (the supply lock covers the whole run). Do not run its REPORT step; the supply run reports once at the end. "
          "Run at most %d browser helpers at a time; each closes its own tab. HARD STOP RULE (2026-11-08): never start a helper batch that cannot finish "
          "before the hard stop (allow ~6 min per batch); leave such batches PENDING (not ingested, never marked unreadable) and checkpoint the step partial "
          "with the count left pending — a squeezed helper's empty answers must not push an org back 3 days." % SP.get("max_browser_helpers", 5))

OVERRIDE = os.path.join(SDIR, "deadline-override.json")   # one-time manual deadline (Chris 2026-11-08: "run again and load up for tonight") — consumed by the next start
def take_override(t):
    o = rj(OVERRIDE)
    if not o or not o.get("deadline"): return None
    try: dl = dt.datetime.fromisoformat(o["deadline"])
    except Exception: return None
    if dl.tzinfo is None: dl = dl.replace(tzinfo=MT)
    os.replace(OVERRIDE, OVERRIDE + ".used-" + t.astimezone(MT).strftime("%Y%m%d-%H%M"))
    return dl if dl > t else None

def cmd_start(a):
    t = now(); ov = take_override(t); dl = ov or deadline_for(t)
    if ov: print("ONE-TIME DEADLINE OVERRIDE in force: hard stop %s MT (%s). A night run that fires meanwhile yields to this run; it is fired by hand afterwards." % (ov.astimezone(MT).strftime("%H:%M"), (rj(OVERRIDE + ".used-" + t.astimezone(MT).strftime("%Y%m%d-%H%M"), {}) or {}).get("reason", "manual")))
    if dl is None:
        print("REFUSED: it is %s MT — too close to the night run (20:41). The supply run starts at ~1 AM, or by hand before 19:30 MT. Do nothing else." % t.astimezone(MT).strftime("%H:%M")); return 2
    run = a.run or next_free_run(default_run(t))
    rc, out = lock("acquire", HOLDER, "--fire", run, "--exclusive", "--stale-hours", str(SP["stale_hours_for_second_start"]))
    print(out)
    if rc != 0:
        print("YIELD: another run holds the outreach lock (a night run or another supply run, alive within %.0f h). Do nothing else; report \"yielded\"." % SP["stale_hours_for_second_start"]); return 2
    st = load(run); st.setdefault("timing", [])
    resumed = bool(st["steps"])
    st.update({"run": run, "status": "running", "deadline": iso(dl)}); st.setdefault("started", iso(t))
    ev(st, ("RESUMED at step %s" % first_open(st)) if resumed else "STARTED")
    save(st); setcur(st, first_open(st) or "shelf")
    print("SUPPLY RUN %s · %s · hard stop %s MT · steps %s · caps %s · NEVER drafts, NEVER touches Gmail, NEVER sends." % (
        run, "RESUMED" if resumed else "fresh start", dl.strftime("%H:%M"), " → ".join(STEPS), json.dumps(CAPS)))
    print("Now run: python3 _shared/orchestrator/supplyrun.py next"); return 0

def cmd_next(a):
    c = cur(); st = load(c["run"]); st.setdefault("timing", [])
    lock("beat", HOLDER)
    s = first_open(st)
    if s is None:
        setcur(st, "finish"); save(st); print("ALL STEPS DONE → python3 _shared/orchestrator/supplyrun.py finish"); return 0
    if past_deadline(st) and s != "shelf":
        st["steps"][s] = {"status": "skipped", "note": "hard stop %s MT reached before this step" % mtfmt(st["deadline"]), "at": iso()}
        tstart(st, s); tend(st, s, "skipped", st["steps"][s]["note"]); ev(st, "HARD STOP: %s skipped" % s); save(st)
        print("HARD STOP %s MT reached — %s skipped (reported). Run: python3 _shared/orchestrator/supplyrun.py next" % (mtfmt(st["deadline"]), s.upper())); return 0
    if s == "events" and not SP.get("events_step_enabled"):
        st["steps"]["events"] = {"status": "skipped", "note": "event-certainty step retired 2026-11-09 (Chris: no date = approach now; nothing left for it to decide)", "at": iso()}
        tstart(st, s); tend(st, s, "skipped", st["steps"]["events"]["note"]); save(st)
        print("EVENTS skipped: step retired 2026-11-09 (Chris's decision tree needs no event-certainty check). Run: python3 _shared/orchestrator/supplyrun.py next"); return 0
    if s == "people" and st.get("credits_remaining") is None and not st.get("credit_floor_hit"):
        setcur(st, "people"); save(st)
        print("CREDIT CHECK before PEOPLE: call apollo_usage_stats_credit_usage_stats once, read the credits REMAINING this cycle, then run:")
        print("  python3 _shared/orchestrator/supplyrun.py credits --remaining <N>   ; then python3 _shared/orchestrator/supplyrun.py next"); return 0
    if s == "people" and st.get("credit_floor_hit"):
        st["steps"]["people"] = {"status": "skipped", "note": "Apollo credits below the floor", "at": iso()}
        tstart(st, s); tend(st, s, "skipped", st["steps"]["people"]["note"]); save(st)
        print("PEOPLE skipped: Apollo credits below the floor. Run: python3 _shared/orchestrator/supplyrun.py next"); return 0
    setcur(st, s); tstart(st, s); save(st)
    R = st["run"]; ms = ",".join(MACHINES)
    print("STEP %d/%d · %s · run %s · hard stop %s MT (now %s)" % (STEPS.index(s) + 1, len(STEPS), s.upper(), R, mtfmt(st["deadline"]), now().astimezone(MT).strftime("%H:%M")))
    if s == "discover":
        print("  Follow the orders printed by: python3 \"$MK/_shared/orchestrator/run.py\" discover — with RUN=%s, steps 2–6. Its  discover.py next  call becomes: "
              "python3 2_Discover/programfiles/discover.py next --run %s --machines %s --sources %d --branches %d --searches %d  "
              "(OM-2 sources first with their searches protected; every helper is told its SEARCHES ALLOWED). If it picks nothing, checkpoint ok \"nothing due\". %s"
              % (R, R, ms, CAPS["discover_sources"], CAPS["discover_branches"], CAPS["discover_searches"], COMMON))
    elif s == "qualify":
        print("  Follow the orders printed by: python3 \"$MK/_shared/orchestrator/run.py\" qualify — with RUN=%s, steps 2–8. Its  qualify.py next  call becomes: "
              "python3 3_Qualify/programfiles/qualify.py next --run %s --cap %d  (every machine; non-Head Start first, then Head Start grantees largest first). "
              "If it picks nothing, checkpoint ok \"nothing to qualify\". %s" % (R, R, CAPS["qualify"], COMMON))
    elif s == "events":
        print("  EVENT CERTAINTY (Rulebook F7, Chris 2026-11-08): python3 3_Qualify/programfiles/events.py next --run %s --cap %d — do exactly the one step it prints until EVENTS DONE. %s"
              % (R, CAPS["events"], COMMON))
    elif s == "people":
        print("  Follow the orders printed by: python3 \"$MK/_shared/orchestrator/run.py\" people — with RUN=%s, steps 2–9 (9 = rebuild + release). Its  people.py next  call becomes: "
              "python3 4_People/programfiles/people.py next --run %s --machine %s --cap %d . If it picks nothing, checkpoint ok \"nothing to find\". %s"
              % (R, R, ms, CAPS["people"], COMMON))
    elif s == "shelf":
        print("  (a) cd \"$ENG\" && python3 _shared/master/build_master.py   (b) python3 _shared/orchestrator/supplyrun.py shelf   — measures and records the shelf the night run will start on. Then checkpoint ok.")
    print("  When the step is complete: python3 _shared/orchestrator/supplyrun.py done --step %s --status ok|partial|failed --note \"<one line with counts>\" ; then python3 _shared/orchestrator/supplyrun.py next" % s)
    return 0

def cmd_credits(a):
    c = cur(); st = load(c["run"]); st["credits_remaining"] = a.remaining
    floor = int((S["night"].get("loop") or {}).get("apollo_credit_floor", 500))   # the ONE floor, shared with the night run
    if a.remaining < floor:
        st["credit_floor_hit"] = True; ev(st, "APOLLO FLOOR %d < %d" % (a.remaining, floor)); save(st)
        print("APOLLO FLOOR: %d remaining < %d — people lookups skipped this run (reported). Run: python3 _shared/orchestrator/supplyrun.py next" % (a.remaining, floor)); return 0
    save(st); print("CREDITS OK: %d remaining (floor %d). Run: python3 _shared/orchestrator/supplyrun.py next" % (a.remaining, floor)); return 0

def cmd_done(a):
    c = cur(); st = load(c["run"])
    if a.step not in STEPS: raise SystemExit("FAIL CLOSED: unknown step %s" % a.step)
    if a.step != c["step"]: raise SystemExit("FAIL CLOSED: the current step is %s, not %s" % (c["step"], a.step))
    st["steps"][a.step] = {"status": a.status, "note": a.note or "", "at": iso()}
    tend(st, a.step, a.status, a.note or ""); ev(st, "DONE %s %s" % (a.step, a.status)); save(st)
    setcur(st, first_open(st) or "finish"); lock("beat", HOLDER)
    print("CHECKPOINT %s = %s. Next: python3 _shared/orchestrator/supplyrun.py next" % (a.step, a.status)); return 0

def cmd_shelf(a):
    c = cur(); st = load(c["run"])
    sh = NR.supply(st); sh["measured"] = iso(); sh["run"] = st["run"]
    st["shelf"] = sh; save(st); wj(os.path.join(SDIR, "shelf-latest.json"), sh)   # the night run and the morning report read this
    print("SHELF (what the night run will find):"); print(shelf_text(sh)); return 0

def cmd_finish(a):
    c = rj(CUR)
    if not c: print("nothing to finish"); return 0
    st = load(c["run"]); st["status"] = "done"; st["finished"] = iso(); ev(st, "FINISHED"); save(st); setcur(st, "finish", "done")
    rc, out = lock("release", HOLDER); print(out)
    sk = [s for s in STEPS if st["steps"].get(s, {}).get("status") in ("skipped", "failed")]
    print("SUPPLY RUN %s FINISHED at %s MT.%s" % (st["run"], mtfmt(st["finished"]), (" Skipped/failed: " + ", ".join("%s (%s)" % (s, st["steps"][s].get("note", "")[:80]) for s in sk)) if sk else ""))
    if st.get("shelf"): print(shelf_text(st["shelf"]))
    print("Your last message: the shelf table above, then one line per skipped or failed step with its reason, then: python3 _shared/orchestrator/supplyrun.py status  (its link lines). Nothing else.")
    return 0

def cmd_status(a):
    c = rj(CUR); run = a.run or (c or {}).get("run")
    if not run: print("no supply run yet"); return 0
    st = load(run); d, _ = run_paths(run)
    print("run %s · status %s · started %s MT · deadline %s MT" % (run, st.get("status"), mtfmt(st.get("started")), mtfmt(st.get("deadline"))))
    for s in STEPS: print("  %-9s %s %s" % (s, (st["steps"].get(s) or {}).get("status", "—"), (st["steps"].get(s) or {}).get("note", "")[:100]))
    def mac(p):   # the device shell sees the vault under $HOME/mnt/ClaudeVault; Chris's links must be the Mac path
        home_mnt = os.path.join(os.path.expanduser("~"), "mnt", "ClaudeVault")
        return p.replace(home_mnt, "/Users/<you>/ClaudeVault") if p.startswith(home_mnt) else p
    print("Links: computer://%s · computer://%s" % (mac(os.path.join(d, "timing.md")), mac(paths.MASTER_CSV))); return 0

def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("start"); p.add_argument("--run"); p.set_defaults(f=cmd_start)
    p = sp.add_parser("next"); p.set_defaults(f=cmd_next)
    p = sp.add_parser("done"); p.add_argument("--step", required=True); p.add_argument("--status", required=True, choices=["ok", "partial", "failed", "skipped"]); p.add_argument("--note"); p.set_defaults(f=cmd_done)
    p = sp.add_parser("credits"); p.add_argument("--remaining", type=int, required=True); p.set_defaults(f=cmd_credits)
    p = sp.add_parser("shelf"); p.set_defaults(f=cmd_shelf)
    p = sp.add_parser("finish"); p.set_defaults(f=cmd_finish)
    p = sp.add_parser("status"); p.add_argument("--run"); p.set_defaults(f=cmd_status)
    a = ap.parse_args(); sys.exit(a.f(a) or 0)

if __name__ == "__main__": main()
