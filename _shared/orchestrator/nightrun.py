#!/usr/bin/env python3
"""nightrun.py -- THE NIGHT RUN, untimed (Rulebook M; Stage 8; Chris 2026-10-30/31).

One start, Sunday–Thursday ~8:41 PM MT. It only SEQUENCES the existing steps — each step's standing orders stay the
single source (_shared/orchestrator/run.py <mode>). Order: inbox → labels → sendlist → review → LOOP → report.
🔴 THE NIGHT RUN NEVER SENDS EMAIL (Chris 2026-10-31, two tasks for safety). It writes tomorrow morning's APPROVED SEND
LIST (7_Send/programfiles/sendlist.py build; flagged = not approved) and the separate 7 AM send task (_shared/orchestrator/run.py send) sends only that
list. Review-hold replies are made here as DRAFTS (FS_MODE=night-review — the engine refuses any send in that mode).
THE LOOP (Chris 2026-10-31: "run until the minimum thresholds are hit — not a timed thing"):
  pass 1, 2, 3 …  each pass = discover → qualify → people → draft Email 1, working ONLY the machines still under their
  nightly minimum (draft.minimum, e.g. OM-1 10 / OM-2 35). Counters: drafts made tonight per machine (the goal) and
  the pass number. A machine leaves the loop when:
     minimum met · ceiling reached (draft.max_per_night) · supply exhausted (nothing left to discover, qualify, find
     people for or draft) · NO PROGRESS (a full pass added 0 drafts, 0 new people-ready orgs and 0 newly qualified
     orgs for it) · the pass ceiling (night.loop.max_passes, default 25) — a last-resort guard, reported if ever hit.
  Gates are never lowered to hit a minimum; a shortfall is reported with its reason.
  Apollo guard: if the cycle's remaining Apollo credits are below night.loop.apollo_credit_floor, people-step lookups
  stop for the night (reported).
No step deadlines and no waiting: the night run ends when the loop and the report are done. The 07:00 ET send is a
different task with its own lock (lock.py send lock), so a long night can never block or overlap it.
Every step and every pass is timed and counted → 6_Report/ledgers/reports/<slot>-timing.md (and a short table in the morning report).

  python3 nightrun.py start [--run R] [--slot D] [--rehearsal]   acquire the night lock (or RESUME a crashed run)
  python3 nightrun.py next                                         print the ONE next step (or WAIT / DONE)
  python3 nightrun.py done --step S --status ok|partial|failed|skipped [--note TEXT]   checkpoint the current step
  python3 nightrun.py credits --remaining N                        record Apollo credits left (asked before each people step)
  python3 nightrun.py finish                                       PRUNE (captures > 3 days, dossiers/reports > 30 days, __pycache__ — the last step of the night, 2026-11-03), release the night lock, mark the run done
  python3 nightrun.py prune [--dry]                                the same prune, on its own
  python3 nightrun.py status
  python3 nightrun.py time-left                                    (kept for old orders) prints NO BUDGET — the run is untimed

Checkpoints: _shared/orchestrator/night/runs/<RUN>/state.json after every step; night/current.json says which step is running (the lock lets
only THAT step's holder nest). A resumed run continues at the first unfinished step (or the unfinished step of the
current pass); the steps are idempotent (a draft or a send already made is never made again).
Second start: if the night lock showed a sign of life within night.stale_hours_for_second_start, the new start YIELDS.
"""
import argparse, datetime as dt, glob, json, os, shutil, subprocess, sys, time
from zoneinfo import ZoneInfo
import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_shared", "orchestrator")); import paths  # the one file that knows every folder (2026-11-03)

ENG = paths.ROOT
MKT = paths.MARKETING
S = paths.settings()
N = S["night"]; LOOP = N.get("loop", {})
MT = ZoneInfo(N["timezone"]); ET = ZoneInfo("America/New_York")
NDIR = paths.NIGHT; CUR = paths.NIGHT_CUR
LOCKPY = paths.LOCK_PY
STEPS = N["steps"]                      # inbox, labels, sendlist, review, loop, report  (never a send step)
LSTEPS = N["loop_steps"]                # discover, qualify, people, draft
MACHINES = paths.machines()
from seqrules import Calendar  # one holiday/business-day source


def now():
    v = os.environ.get("NIGHTRUN_NOW")
    return dt.datetime.fromisoformat(v).astimezone(dt.timezone.utc) if v else dt.datetime.now(dt.timezone.utc)
def iso(t=None): return (t or now()).isoformat(timespec="seconds")
def rj(p, d=None): return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else d
def jl(p): return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()] if os.path.exists(p) else []
def wj(p, o):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"; json.dump(o, open(tmp, "w", encoding="utf-8"), indent=1, ensure_ascii=False, sort_keys=True); os.replace(tmp, p)
def lock(*a):
    r = subprocess.run([sys.executable, LOCKPY] + list(a), capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()
def default_run(t=None):
    t = (t or now()).astimezone(MT)
    return (t.date() if t.hour >= 12 else t.date() - dt.timedelta(days=1)).isoformat()
def run_paths(run): d = os.path.join(NDIR, "runs", run); return d, os.path.join(d, "state.json")   # (was paths(); renamed 2026-11-03 — paths is the folder module)
def load(run): return rj(run_paths(run)[1]) or {"run": run, "steps": {}, "events": [], "timing": []}
def save(st): wj(run_paths(st["run"])[1], st); write_timing(st)
def ev(st, msg): st["events"].append({"at": iso(), "what": msg})
def holder(step): return N["holders"].get(step)
def setcur(st, step, status="running"):
    wj(CUR, {"run": st["run"], "slot": st["slot"], "status": status, "step": step, "step_holder": holder(step),
             "pass": (st.get("loop") or {}).get("pass"), "rehearsal": st.get("rehearsal", False), "updated": iso()})
def cur():
    c = rj(CUR)
    if not c: raise SystemExit("FAIL CLOSED: no night run is in progress (run: nightrun.py start)")
    return c
def first_open(st):
    for s in STEPS:
        if st["steps"].get(s, {}).get("status") not in ("ok", "partial", "failed", "carried", "skipped"): return s
    return None
def minimums(st): return N["rehearsal_minimums"] if st.get("rehearsal") else paths.mset("minimum")
def ceilings(st): return paths.mset("max_per_night")
def prun(st, n): return "%s-p%d" % (st["run"], n)


# ------------------------------------------------------------------ measuring (read-only; tests inject NIGHTRUN_METRICS)
def _inject():
    p = os.environ.get("NIGHTRUN_METRICS"); return rj(p) if p else None

def made_tonight(st):
    inj = _inject()
    if inj is not None:
        return {m: sum((inj.get("pass_counts", {}).get(prun(st, p["n"]), {}).get("drafts", {}) or {}).get(m, 0)
                       for p in st.get("loop", {}).get("passes", [])) for m in MACHINES}
    out = {m: 0 for m in MACHINES}
    for p in st.get("loop", {}).get("passes", []):
        sm = rj(os.path.join(paths.runs("draft"), prun(st, p["n"]), "summary.json"), {}) or {}
        for m in MACHINES: out[m] += int((sm.get("made") or {}).get(m, 0))
    return out

def supply(st):
    """What is still left tonight, per machine: draft-eligible, people pool, qualify pool; and due discovery sources."""
    inj = _inject()
    if inj is not None: return inj["supply"]
    import draft as DR, people as PE, discover as DI
    orgs = DR.load_orgs(); idx = DR.indexes(orgs)
    today = dt.datetime.now(MT).date().isoformat()
    pled = {}
    for r in jl(paths.PEOPLE_DECISIONS): pled[r["org_id"]] = r
    qled = {}
    for r in jl(paths.QUALIFY_LEDGER): qled[r["org_id"]] = r
    out = {"due_sources": sum(1 for r in DI.jl(DI.SRC) if DI.due(r) and r.get("type") != "branch") + sum(1 for r in DI.jl(DI.SRC) if DI.due(r) and r.get("type") == "branch"),
           "machines": {m: {"draft_eligible": 0, "people_pool": 0, "qualify_pool": 0} for m in MACHINES}}
    for o in orgs:
        m = o.get("owner_machine")
        if m in MACHINES and DR.why_not(o, idx) is None: out["machines"][m]["draft_eligible"] += 1
        if m in MACHINES and PE.eligible(o) and not (o.get("recipients") or {}).get("to"):
            lr = pled.get(o["org_id"])
            if not (lr and (lr.get("decision") == "ready" or (lr.get("retry_after") or "") > today or str(lr.get("run") or "").startswith(st["run"] + "-p"))):
                out["machines"][m]["people_pool"] += 1
        if (o.get("fit") or {}).get("status") == "unreviewed" and not o.get("referrer") and not any(v for v in (o.get("exclusions") or {}).values()) \
                and not (set(o.get("icps") or []) and set(o["icps"]) <= {"ICP-007", "ICP-008"}):
            lr = qled.get(o["org_id"])
            if lr and (lr.get("retry_after") or "") > today: continue
            likely = m if m in MACHINES else ("OM-2" if (o.get("events") or o.get("runs_event")) else None)
            for mm in MACHINES:
                if likely in (None, mm): out["machines"][mm]["qualify_pool"] += 1
    return out

def pass_counts(st, n, before_orgs):
    """Counters for one pass: sources swept, orgs found, newly qualified / people-ready / drafts per machine."""
    inj = _inject(); R = prun(st, n)
    if inj is not None:
        c = dict(inj.get("pass_counts", {}).get(R, {}))
        for k in ("qualified", "people_ready", "drafts"): c.setdefault(k, {m: 0 for m in MACHINES})
        c.setdefault("sources_swept", 0); c.setdefault("orgs_found", 0); return c
    orgs = jl(paths.ORGS); owner = {o["org_id"]: o.get("owner_machine") for o in orgs}
    stp = rj(os.path.join(paths.runs("discover"), R, "state.json"), {}) or {}
    swept = sum(len(b.get("ids", [])) for b in stp.get("batches", []) if b.get("status") == "ingested" and not b.get("search"))
    q = {m: 0 for m in MACHINES}; pr = {m: 0 for m in MACHINES}
    for r in jl(paths.QUALIFY_LEDGER):
        if r.get("run") == R and r.get("decision") in ("fit", "doubtful") and owner.get(r["org_id"]) in q: q[owner[r["org_id"]]] += 1
    for r in jl(paths.PEOPLE_DECISIONS):
        if r.get("run") == R and r.get("decision") == "ready" and owner.get(r["org_id"]) in pr: pr[owner[r["org_id"]]] += 1
    sm = rj(os.path.join(paths.runs("draft"), R, "summary.json"), {}) or {}
    return {"sources_swept": swept, "orgs_found": max(0, len(orgs) - (before_orgs or len(orgs))), "qualified": q, "people_ready": pr,
            "drafts": {m: int((sm.get("made") or {}).get(m, 0)) for m in MACHINES}}

def org_count():
    inj = _inject()
    if inj is not None: return inj.get("orgs", 0)
    return len(jl(paths.ORGS))


# ------------------------------------------------------------------ the loop decision (pure; tested)
def decide(made, mins, ceils, sup, last_counts, stopped, pass_no, max_passes):
    """Return (open_machines, new_stops{m: reason}). last_counts = the counters of the pass just finished (or None)."""
    new = {}
    for m in MACHINES:
        if m in stopped: continue
        if made.get(m, 0) >= ceils[m]: new[m] = "ceiling reached (%d of %d)" % (made.get(m, 0), ceils[m]); continue
        if made.get(m, 0) >= mins[m]: new[m] = "minimum met (%d of %d)" % (made.get(m, 0), mins[m]); continue
        s = sup["machines"][m]
        if s["draft_eligible"] == 0 and s["people_pool"] == 0 and s["qualify_pool"] == 0 and sup["due_sources"] == 0:
            new[m] = "supply exhausted (%d of %d): nothing left tonight to discover, qualify, find people for or draft" % (made.get(m, 0), mins[m]); continue
        if last_counts is not None and m in last_counts.get("worked", []):
            if last_counts["drafts"].get(m, 0) == 0 and last_counts["people_ready"].get(m, 0) == 0 and last_counts["qualified"].get(m, 0) == 0:
                new[m] = ("no progress in pass %d (0 drafts, 0 new people-ready, 0 newly qualified) — supply-exhausted for the night (%d of %d)"
                          % (last_counts["n"], made.get(m, 0), mins[m])); continue
    open_ = [m for m in MACHINES if m not in stopped and m not in new]
    if open_ and pass_no >= max_passes:
        for m in open_: new[m] = "pass ceiling hit (%d passes) — last-resort guard (%d of %d)" % (max_passes, made.get(m, 0), mins[m])
        open_ = []
    return open_, new


# ------------------------------------------------------------------ timing file
def mt(t): return dt.datetime.fromisoformat(t).astimezone(MT).strftime("%H:%M") if t else "—"
def write_timing(st):
    if not st.get("slot"): return
    rows = []
    for t in st.get("timing", []):
        rows.append("| %s | %s | %s | %s | %s | %s | %s |" % (t["what"], t.get("pass") or "", mt(t.get("start")), mt(t.get("end")),
                    ("%.1f" % (t["seconds"] / 60)) if t.get("seconds") is not None else "…", t.get("status") or "running", (t.get("note") or "")[:120]))
    lp = st.get("loop") or {}
    prow = []; run_tot = {m: 0 for m in MACHINES}
    for p in lp.get("passes", []):
        c = p.get("counts")
        if not c: prow.append("| %d | %s | (running) | | | | | | |" % (p["n"], ", ".join(p["machines"]))); continue
        for m in MACHINES: run_tot[m] += c["drafts"].get(m, 0)
        f = lambda k: " / ".join(str(c[k].get(m, 0)) for m in MACHINES)
        prow.append("| %d | %s | %s | %d | %d | %s | %s | %s | %s |" % (p["n"], ", ".join(p["machines"]), ("%.1f" % (p["seconds"] / 60)) if p.get("seconds") else "",
                    c["sources_swept"], c["orgs_found"], f("qualified"), f("people_ready"), f("drafts"), " / ".join(str(run_tot[m]) for m in MACHINES)))
    tot = sum(t.get("seconds") or 0 for t in st.get("timing", []) if not t.get("pass"))
    mins = minimums(st)
    L = ["# Night run timing — %s (slot %s)%s" % (st["run"], st["slot"], " · REHEARSAL" if st.get("rehearsal") else ""), "",
         "<!-- short -->",
         "Started %s MT · %s · total %.0f min · passes %d · drafts tonight %s (minimums %s)" % (
             mt(st.get("started")), ("finished %s MT" % mt(st.get("finished"))) if st.get("finished") else "still running",
             tot / 60, len(lp.get("passes", [])), " / ".join("%s %d" % (m, run_tot[m]) for m in MACHINES), " / ".join("%s %d" % (m, mins[m]) for m in MACHINES)), "",
         "| Pass | Machines worked | Min | Sources swept | Orgs found | Qualified (OM-1/OM-2) | People-ready (OM-1/OM-2) | Drafts (OM-1/OM-2) | Drafts so far |",
         "|---|---|---|---|---|---|---|---|---|"] + prow + [""]
    for m, r in sorted((lp.get("stopped") or {}).items()): L.append("- %s left the loop: %s" % (m, r))
    L += ["<!-- /short -->", "", "## Every step", "", "| Step | Pass | Start MT | End MT | Minutes | Status | Note |", "|---|---|---|---|---|---|---|"] + rows
    name = ("%s-timing%s.md" % (st["slot"], "-rehearsal" if st.get("rehearsal") else ""))
    p = os.path.join(paths.REPORTS, name); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write("\n".join(L) + "\n")

def tstart(st, what, pas=None):
    for t in st["timing"]:
        if t["what"] == what and t.get("pass") == pas and t.get("end") is None: return
    st["timing"].append({"what": what, "pass": pas, "start": iso(), "end": None, "seconds": None})
def tend(st, what, pas, status, note):
    for t in reversed(st["timing"]):
        if t["what"] == what and t.get("pass") == pas and t.get("end") is None:
            t["end"] = iso(); t["status"] = status; t["note"] = note
            t["seconds"] = (dt.datetime.fromisoformat(t["end"]) - dt.datetime.fromisoformat(t["start"])).total_seconds(); return
    st["timing"].append({"what": what, "pass": pas, "start": iso(), "end": iso(), "seconds": 0, "status": status, "note": note})


# ------------------------------------------------------------------ commands
def next_free_run(run):
    """A start on a day whose run already FINISHED opens a new run (2026-11-02-2, -3 …) instead of resuming the finished one.
    Root cause of the 'loop exits instantly' finding (10/31 and 11/02): the second start of a day loaded the finished state,
    found every step done and printed ALL STEPS DONE. A crashed (not finished) run is still resumed as before."""
    base, n = run, 1
    while (load(run).get("status") == "done"):
        n += 1; run = "%s-%d" % (base, n)
    return run

def slot_for(run, t=None):
    """The send slot a night run writes for: the business day after the run's night — but never a slot whose 07:00 ET
    send is already past (CAPA 2026-11-06 R2-4: a late/daytime fire reused a past slot, so its drafts were on no list).
    If the derived slot's 07:00 ET is already behind us, the slot rolls to the next business day after now."""
    t = (t or now()).astimezone(ET)
    cal = Calendar(S)
    slot = cal.roll(dt.date.fromisoformat(run.replace("rehearsal-", "")[:10]) + dt.timedelta(days=1))
    cutoff = t.date() if t.hour < 7 else t.date() + dt.timedelta(days=1)   # earliest slot whose 07:00 ET is still ahead
    if slot < cutoff: slot = cal.roll(cutoff)
    return slot.isoformat()

def cmd_start(a):
    run = a.run or next_free_run(default_run())
    if a.rehearsal and not run.startswith("rehearsal"):   # 2026-11-03: a rehearsal is ALWAYS named rehearsal-… — sendlist.py/draft.py key their sandboxes on the name
        run = next_free_run("rehearsal-" + dt.datetime.now(MT).date().isoformat())
    slot = a.slot or slot_for(run)   # 2026-11-09 (CAPA 11/06 R2-4): never a slot whose 07:00 ET send has already happened
    rc, out = lock("acquire", "night-run", "--fire", run, "--exclusive", "--stale-hours", str(N["stale_hours_for_second_start"]))
    print(out)
    if rc != 0:
        print("YIELD: another night run is alive (it showed a sign of life within %.0f h). Do nothing else; report \"yielded\"."
              % N["stale_hours_for_second_start"]); return 2
    st = load(run); st.setdefault("timing", [])
    resumed = bool(st["steps"]) or bool((st.get("loop") or {}).get("passes"))
    st.update({"run": run, "slot": slot, "rehearsal": bool(a.rehearsal or run.startswith("rehearsal")), "status": "running"})
    st.setdefault("started", iso())
    ev(st, ("RESUMED at step %s" % first_open(st)) if resumed else "STARTED")
    if not resumed:   # Chris 2026-11-08: record the shelf the Supply Run left, so a shortfall reads as "shelf empty" or "shelf full, drafting failed"
        try: st["shelf_at_start"] = dict(supply(st), measured=iso(), supply_run=(rj(os.path.join(paths.SUPPLY, "shelf-latest.json"), {}) or {}).get("run"))
        except Exception as ex: st["shelf_at_start"] = {"error": str(ex)[:200]}
    save(st); setcur(st, first_open(st) or "report")
    mins = minimums(st)
    print("NIGHT RUN %s · approved send list for %s 07:00 ET (sent by the separate send task — this run NEVER sends) · %s · untimed: the loop runs until minimums %s are met or supply is exhausted%s" % (
        run, slot,
        "RESUMED" if resumed else "fresh start", ", ".join("%s %d" % (m, mins[m]) for m in MACHINES),
        " · REHEARSAL (test drafts go only to chris@chrisdanilo.com, labeled OM-TEST, then deleted)" if st["rehearsal"] else ""))
    sh = st.get("shelf_at_start") or {}
    if sh.get("machines"): print("SHELF AT START (left by the supply run %s): %s · due sources %d" % (sh.get("supply_run") or "— none yet",
        ", ".join("%s ready-to-draft %d / people-to-find %d / to-qualify %d" % (m, sh["machines"][m]["draft_eligible"], sh["machines"][m]["people_pool"], sh["machines"][m]["qualify_pool"]) for m in MACHINES), sh.get("due_sources", 0)))
    print("Now run: python3 _shared/orchestrator/nightrun.py next")
    return 0


COMMON = ("Skip that order set's MOUNT step (already mounted). Its LOCK line prints ACQUIRED-NESTED and its RELEASE line prints "
          "RELEASED-NESTED — that is correct (the night lock covers the whole night). Do not run its REPORT step; the night run reports once at the end.")

def cmd_next(a):
    c = cur(); st = load(c["run"]); st.setdefault("timing", [])
    lock("beat", "night-run")
    s = first_open(st)
    if s is None:
        setcur(st, "finish"); save(st); print("ALL STEPS DONE → python3 _shared/orchestrator/nightrun.py finish"); return 0
    if s == "loop": return loop_next(st)
    setcur(st, s); tstart(st, s); save(st)
    run, slot = st["run"], st["slot"]; reh = st.get("rehearsal")
    i = STEPS.index(s) + 1; total = len(STEPS)
    print("STEP %d/%d · %s · run %s · slot %s" % (i, total, s.upper(), run, slot))
    if s == "inbox":
        print("  Follow the orders printed by: python3 \"$MK/_shared/orchestrator/run.py\" read — with D=%s (the slot the send list is for). %s" % (slot, COMMON))
    elif s == "audit":
        print("  DRAFTS AUDIT (Chris 2026-11-06, CAPA 2026-11-06 #10 — audit, then resolve; Chris does no work). From \"$ENG\": "
              "python3 1_Read-the-Inbox/programfiles/orphans.py next --slot %s --night %s — do EXACTLY the one step it prints (the list_drafts read saved "
              "verbatim · rebuild · the draft.py --redo loop for rewrites, with its Gate 7 and trash_message lines · delete_draft ONLY for the drafts it names, then "
              "orphans.py deleted · rebuild), rerun next after each, until it prints AUDIT DONE. Never touch a draft it does not name. "
              "Checkpoint with its AUDIT DONE counts.%s" % (slot, run, " REHEARSAL: run the read and the plan only — no rewrite, no delete." if reh else ""))
    elif s == "labels":
        print("  Rulebook L, from \"$ENG\": list_labels → save verbatim as $ENG/1_Read-the-Inbox/runs/%s/labels.json ; python3 7_Send/programfiles/send.py label-orders --labels "
              "$ENG/1_Read-the-Inbox/runs/%s/labels.json --slot %s . If it prints CREATE lines: create_label each (parents first), save list_labels again, rerun. "
              "Then apply ONLY the label_thread / unlabel_thread orders it prints, in order (state labels only — closes ✗ included). "
              "Never send, never draft in this step." % (slot, slot, slot))
    elif s == "sendlist":
        print("  python3 7_Send/programfiles/sendlist.py build --night %s --slot %s   — writes tomorrow's APPROVED send list (flagged = not approved) and the "
              "review list. It is final once written; a resumed night never changes it. FAIL CLOSED with CHECK lines → do the read orders' step 4 "
              "check loop, then run it again. Nothing is sent by this step or by anything in this night run." % (run, slot))
    elif s == "review":
        print("  REVIEW-HOLD DRAFTS (Rulebook I7 — drafts on the existing thread, NEVER a send). For each machine, OM-2 then OM-1 "
              "(OM-2 = \"$MK/_shared/machines/OM-2\", OM-1 = \"$MK/_shared/machines/OM-1\"), from \"$ENG\" with "
              "export FS_MASTER_PLAN=\"$ENG/7_Send/ledgers/send-lists/%s%s-review.json\" FS_MODE=night-review : python3 7_Send/programfiles/followup_send.py --machine <folder> --queries (run the printed reads, save verbatim) → "
              "--plan (until no NEEDS) → --arm in batches → for each armed row: --intent; ONLY on GO call execute_zapier_write_action with the action "
              "it names (draft_v2_reply / gmail_create_draft_reply) and the row's params VERBATIM → --verify (list_drafts read-back). The engine "
              "REFUSES any send in this mode. A review list with 0 rows → checkpoint ok \"no review drafts\".%s" % (
                  "rehearsal/" if reh else "", slot, " REHEARSAL: do --queries/--plan only, no drafts." if reh else ""))
    elif s == "report":
        print("  (0) python3 5_Draft/programfiles/dossier.py --night %s --slot %s  → the sending dossier Chris reads next to Gmail Drafts (built from the records; nothing looked up)." % (run, slot))
        print("  (a) python3 6_Report/programfiles/report.py --date %s --issues  → the issue seeds. (b) Write 6_Report/ledgers/reports/%s-capa.md: ONE prioritized issues list "
              "(P1 wrong/unwanted contact or rule broken · P2 lost output · P3 process), seeds + your own mistakes, shared root causes grouped; each entry: "
              "what happened · impact · root cause · containment · corrective · preventive · interactions · decision needed. "
              "(c) python3 6_Report/programfiles/report.py --date %s%s — its text (executive summary → issues/CAPA → links) is the night run's ONE report; "
              "no reply list, no step status (Chris 2026-11-03)." % (slot, slot, slot, " --sample --night %s" % run if reh else ""))
    print("  When the step is complete: python3 _shared/orchestrator/nightrun.py done --step %s --status ok|partial|failed --note \"<one line>\" ; then python3 _shared/orchestrator/nightrun.py next" % s)
    return 0


def loop_next(st):
    lp = st.setdefault("loop", {"pass": 0, "passes": [], "stopped": {}, "credit_floor_hit": False})
    tstart(st, "loop")
    cur_p = lp["passes"][-1] if lp["passes"] else None
    if cur_p is None or cur_p.get("counts") is not None:
        # between passes: decide who is still worked
        made = made_tonight(st); sup = supply(st)
        last = None
        if cur_p is not None:
            last = dict(cur_p["counts"], n=cur_p["n"], worked=cur_p["machines"])
        open_, new = decide(made, minimums(st), ceilings(st), sup, last, lp["stopped"], len(lp["passes"]), int(LOOP.get("max_passes", 25)))
        for m, r in new.items(): lp["stopped"][m] = r; ev(st, "LOOP STOP %s: %s" % (m, r))
        if not open_:
            st["steps"]["loop"] = {"status": "ok", "at": iso(), "note": "%d pass(es); drafts tonight %s; %s" % (
                len(lp["passes"]), ", ".join("%s %d" % (m, made[m]) for m in MACHINES), "; ".join("%s: %s" % kv for kv in sorted(lp["stopped"].items())))}
            tend(st, "loop", None, "ok", st["steps"]["loop"]["note"]); save(st)
            print("LOOP DONE after %d pass(es). Drafts made tonight: %s." % (len(lp["passes"]), ", ".join("%s %d of %d" % (m, made[m], minimums(st)[m]) for m in MACHINES)))
            for m, r in sorted(lp["stopped"].items()): print("  %s: %s" % (m, r))
            print("Run: python3 _shared/orchestrator/nightrun.py next"); return 0
        n = len(lp["passes"]) + 1
        cur_p = {"n": n, "machines": open_, "start": iso(), "steps": {}, "before_orgs": org_count(), "made_before": made}
        lp["passes"].append(cur_p); lp["pass"] = n
        ev(st, "PASS %d START for %s" % (n, ", ".join(open_)))
        print("PASS %d starts — working %s (drafts so far: %s)" % (n, ", ".join(open_), ", ".join("%s %d/%d" % (m, made[m], minimums(st)[m]) for m in MACHINES)))
    n = cur_p["n"]; R = prun(st, n); ms = ",".join(cur_p["machines"])
    sub = next((x for x in LSTEPS if cur_p["steps"].get(x, {}).get("status") is None), None)
    if sub is None:          # pass complete → counters
        cur_p["end"] = iso(); cur_p["seconds"] = (dt.datetime.fromisoformat(cur_p["end"]) - dt.datetime.fromisoformat(cur_p["start"])).total_seconds()
        cur_p["counts"] = pass_counts(st, n, cur_p.get("before_orgs"))
        tend(st, "pass", n, "ok", "worked %s · %s" % (ms, json.dumps({k: cur_p["counts"][k] for k in ("sources_swept", "orgs_found", "qualified", "people_ready", "drafts")})))
        save(st); print("PASS %d DONE: %s. Run: python3 _shared/orchestrator/nightrun.py next" % (n, json.dumps(cur_p["counts"])))
        return 0
    tstart(st, "pass", n)
    if sub == "people" and lp.get("credit_floor_hit"):
        cur_p["steps"]["people"] = {"status": "skipped", "at": iso(), "note": "Apollo credit floor hit earlier tonight"}
        tstart(st, "people", n); tend(st, "people", n, "skipped", "Apollo credit floor hit earlier tonight"); save(st)
        print("PEOPLE skipped in pass %d: Apollo credits below the floor. Run: python3 _shared/orchestrator/nightrun.py next" % n); return 0
    if sub == "people" and cur_p.get("credits_remaining") is None:
        setcur(st, "loop"); save(st)
        print("PASS %d · CREDIT CHECK before PEOPLE: call apollo_usage_stats_credit_usage_stats once, read the credits REMAINING this cycle, then run:" % n)
        print("  python3 _shared/orchestrator/nightrun.py credits --remaining <N>   ; then python3 _shared/orchestrator/nightrun.py next")
        return 0
    setcur(st, sub); tstart(st, sub, n)
    if sub == "draft":       # how many drafts each machine may still make tonight (0 = not worked this pass)
        made = made_tonight(st); ce = ceilings(st)
        wj(os.path.join(paths.runs("draft"), R, "allowance.json"),
           {m: (max(0, ce[m] - made[m]) if m in cur_p["machines"] else 0) for m in MACHINES})
    save(st)
    reh = st.get("rehearsal"); caps = N["rehearsal_caps"]
    print("PASS %d · STEP %s · run %s · machines %s · slot %s" % (n, sub.upper(), R, ms, st["slot"]))
    if sub == "discover":
        extra = (" REHEARSAL CAPS: python3 2_Discover/programfiles/discover.py next --run %s --sources %d --branches %d --searches %d"
                 % (R, caps["discover_sources"], caps["discover_branches"], caps["discover_searches"])) if reh else ""
        print("  Follow the orders printed by: python3 \"$MK/_shared/orchestrator/run.py\" discover — with RUN=%s, steps 2–6 (default caps from settings). "
              "Add to its  discover.py next  call: --machines %s  (OM-2 sources first and their searches protected — Chris 2026-11-06). "
              "If it picks nothing (no sources due and no searches), checkpoint ok with note \"nothing due\". %s%s" % (R, ms, COMMON, extra))
    elif sub == "qualify":
        print("  Follow the orders printed by: python3 \"$MK/_shared/orchestrator/run.py\" qualify — with RUN=%s, steps 2–8. Add to its  qualify.py next  call: "
              "--machines %s%s  (only candidates that could route to machines still under their minimum; non-Head Start first, then Head Start "
              "grantees largest first). If it picks nothing, checkpoint ok with note \"nothing to qualify\". %s" % (R, ms, (" --cap %d" % caps["qualify"]) if reh else "", COMMON))
    elif sub == "people":
        print("  Follow the orders printed by: python3 \"$MK/_shared/orchestrator/run.py\" people — with RUN=%s, steps 2–9 (9 = rebuild + release). Add to its  people.py next  call: "
              "--machine %s --night %s%s. If it picks nothing, checkpoint ok with note \"nothing to find\". %s" % (R, ms, st["run"], (" --cap %d" % caps["people"]) if reh else "", COMMON))
    elif sub == "draft":
        extra = (" REHEARSAL: the drafter addresses every draft ONLY to chris@chrisdanilo.com (no Cc), labels it OM-TEST, records nothing, "
                 "and at DRAFT DONE prints the delete_draft orders: do them.") if reh else ""
        print("  Follow the orders printed by: python3 \"$MK/_shared/orchestrator/run.py\" draft — with R=%s, step 2 only (the loop until DRAFT DONE). The drafter reads "
              "this pass's allowance (drafts still allowed tonight per machine; 0 = not worked). %s%s" % (R, COMMON, extra))
    print("  When the step is complete: python3 _shared/orchestrator/nightrun.py done --step %s --status ok|partial|failed --note \"<one line with counts>\" ; then python3 _shared/orchestrator/nightrun.py next" % sub)
    return 0




def cmd_time_left(a):
    lock("beat", "night-run"); print("NO BUDGET: the night run is untimed (Chris 2026-10-31) — keep going"); return 0


def cmd_credits(a):
    c = cur(); st = load(c["run"]); lp = st.get("loop") or {}
    if not lp.get("passes"): raise SystemExit("FAIL CLOSED: no pass is running")
    p = lp["passes"][-1]; p["credits_remaining"] = a.remaining
    floor = int(LOOP.get("apollo_credit_floor", 500))
    if a.remaining < floor:
        lp["credit_floor_hit"] = True
        p["steps"]["people"] = {"status": "skipped", "at": iso(), "note": "Apollo credits %d below the floor %d" % (a.remaining, floor)}
        tstart(st, "people", p["n"]); tend(st, "people", p["n"], "skipped", p["steps"]["people"]["note"])
        ev(st, "APOLLO FLOOR %d < %d — people lookups stop tonight" % (a.remaining, floor))
        save(st); print("APOLLO FLOOR: %d remaining < %d — people lookups stop for tonight (reported). Run: python3 _shared/orchestrator/nightrun.py next" % (a.remaining, floor)); return 0
    save(st); print("CREDITS OK: %d remaining (floor %d). Run: python3 _shared/orchestrator/nightrun.py next" % (a.remaining, floor)); return 0


def cmd_done(a):
    c = cur(); st = load(c["run"])
    lp = st.get("loop") or {}
    if a.step in LSTEPS:
        if first_open(st) != "loop" or not lp.get("passes"): raise SystemExit("FAIL CLOSED: %s is a loop step but no pass is running" % a.step)
        p = lp["passes"][-1]
        if c["step"] != a.step: raise SystemExit("FAIL CLOSED: the current step is %s, not %s" % (c["step"], a.step))
        p["steps"][a.step] = {"status": a.status, "note": a.note or "", "at": iso()}
        tend(st, a.step, p["n"], a.status, a.note or "")
        ev(st, "PASS %d DONE %s %s" % (p["n"], a.step, a.status)); setcur(st, "loop"); save(st)
        lock("beat", "night-run")
        print("CHECKPOINT pass %d %s = %s. Next: python3 _shared/orchestrator/nightrun.py next" % (p["n"], a.step, a.status)); return 0
    if a.step not in STEPS: raise SystemExit("FAIL CLOSED: unknown step %s" % a.step)
    if a.step != c["step"]: raise SystemExit("FAIL CLOSED: the current step is %s, not %s" % (c["step"], a.step))
    st["steps"][a.step] = {"status": a.status, "note": a.note or "", "at": iso()}
    tend(st, a.step, None, a.status, a.note or "")
    ev(st, "DONE %s %s" % (a.step, a.status)); save(st)
    setcur(st, first_open(st) or "finish"); lock("beat", "night-run")
    print("CHECKPOINT %s = %s. Next: python3 _shared/orchestrator/nightrun.py next" % (a.step, a.status)); return 0


PRUNE = S["night"].get("prune", {"captures_days": 3, "records_days": 30})

def prune(today=None, dry=False):
    """THE LAST STEP OF THE NIGHT (Chris 2026-11-03): page captures and other run working files older than captures_days (3), dossiers and reports
    older than records_days (30), and every __pycache__ leave the live tree. The evidence stays: each phase ledger holds the quote + URL + date.
    Records (dossiers, reports) move to archive/records/ and are kept. The vault shell forbids deletes, so working files that cannot be removed are MOVED
    to archive/pruned/<today>/ (same relative path) — Chris can empty that folder."""
    today = today or dt.datetime.now(MT).date()
    def age_days(p):
        try: return (today - dt.datetime.fromtimestamp(os.path.getmtime(p), MT).date()).days
        except Exception: return 0
    cands = []   # (path, is_dir)
    # 7_Send/runs is NEVER pruned: the sender re-reads every past fire's followup_sends.json for uncleared DUPLICATE findings (full stop on a duplicate, Chris 2026-10-26)
    for ph in ("read", "discover", "qualify", "people", "draft"):
        rd = paths.runs(ph)
        tops = [d for d in sorted(glob.glob(os.path.join(rd, "*"))) if os.path.isdir(d)]
        if ph == "read":   # raw Gmail pulls sit one level down: runs/gmail/<date>/
            tops = [d for d in tops if os.path.basename(d) != "gmail"] + [d for d in sorted(glob.glob(os.path.join(rd, "gmail", "*"))) if os.path.isdir(d)]
        for d in tops:
            # a run folder is pruned only when EVERY file in it is older than the limit (a resumed run keeps its files)
            files = [f for f in glob.glob(os.path.join(d, "**", "*"), recursive=True) if os.path.isfile(f)]
            if files and all(age_days(f) > PRUNE["captures_days"] for f in files): cands.append((d, True))
    records = []   # dossiers/reports older than records_days are RECORDS: they go to archive/records/ (kept), never to pruned/
    for d in (paths.DOSSIERS, paths.REPORTS):
        for f in sorted(glob.glob(os.path.join(d, "**", "*.md"), recursive=True)):
            if os.path.basename(f).upper() != "README.MD" and age_days(f) > PRUNE["records_days"]: records.append(f)
    for d in [paths.ORCH, paths.MASTER] + [paths.programs(p) for p in paths.PHASES]:
        pc = os.path.join(d, "__pycache__")
        if os.path.isdir(pc): cands.append((pc, True))
    out = {"removed": 0, "moved": 0, "records": 0, "paths": []}
    for f in records:
        rel = os.path.relpath(f, ENG)
        if dry: out["paths"].append("RECORD " + rel); continue
        dest = os.path.join(paths.ARCHIVE, "records", rel); os.makedirs(os.path.dirname(dest), exist_ok=True)
        try: os.rename(f, dest); out["records"] += 1; out["paths"].append("RECORD " + rel)
        except OSError as ex: out["paths"].append("%s: could not archive (%s)" % (rel, ex))
    for p, is_dir in cands:
        rel = os.path.relpath(p, ENG)
        if dry: out["paths"].append(rel); continue
        try:
            shutil.rmtree(p) if is_dir else os.remove(p); out["removed"] += 1
        except (PermissionError, OSError):
            dest = os.path.join(paths.ARCHIVE, "pruned", today.isoformat(), rel); os.makedirs(os.path.dirname(dest), exist_ok=True)
            try: os.rename(p, dest); out["moved"] += 1
            except OSError as ex: out["paths"].append("%s: could not prune (%s)" % (rel, ex)); continue
        out["paths"].append(rel)
    return out

def cmd_prune(a):
    r = prune(dry=a.dry)
    print("PRUNE%s: %d removed · %d moved to archive/pruned/ · %d records to archive/records/ · %d paths" % (" (dry run)" if a.dry else "", r["removed"], r["moved"], r["records"], len(r["paths"])))
    for p in r["paths"][:60]: print("  " + p)
    return 0

def cmd_finish(a):
    c = cur(); st = load(c["run"])
    try:
        pr = prune(); st["prune"] = {"removed": pr["removed"], "moved": pr["moved"], "records": pr["records"], "n": len(pr["paths"])}; ev(st, "PRUNED %d removed, %d moved to archive/pruned, %d records to archive/records" % (pr["removed"], pr["moved"], pr["records"]))
    except Exception as ex:
        st["prune"] = {"error": repr(ex)}; ev(st, "PRUNE FAILED %r" % (ex,))
    st["status"] = "done"; st["finished"] = iso(); ev(st, "FINISHED"); save(st)
    wj(CUR, {"run": st["run"], "slot": st["slot"], "status": "done", "step": None, "step_holder": None, "updated": iso()})
    rc, out = lock("release", "night-run"); print(out); print("NIGHT RUN %s DONE · prune: %s · timing: 6_Report/ledgers/reports/%s-timing%s.md" % (st["run"], json.dumps(st["prune"]), st["slot"], "-rehearsal" if st.get("rehearsal") else "")); return 0


def cmd_status(a):
    c = rj(CUR) or {}
    run = getattr(a, "run", None) or c.get("run")
    if not run: print("no night run recorded"); return 0
    st = load(run); lp = st.get("loop") or {}
    print("NIGHT RUN %s · slot %s · status %s · current step %s · pass %s" % (run, st.get("slot"), st.get("status"),
          c.get("step") if c.get("run") == run else "-", lp.get("pass")))
    for s in STEPS:
        x = st["steps"].get(s)
        print("  %-8s %s" % (s, ("%s · %s · %s" % (x["status"], x.get("at", ""), x.get("note", ""))) if x else "not yet"))
    for p in lp.get("passes", []):
        print("    pass %d (%s): %s" % (p["n"], ", ".join(p["machines"]), ", ".join("%s=%s" % (k, v["status"]) for k, v in p["steps"].items()) or "starting"))
    return 0


def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("start"); p.add_argument("--run"); p.add_argument("--slot"); p.add_argument("--rehearsal", action="store_true"); p.set_defaults(f=cmd_start)
    sp.add_parser("next").set_defaults(f=cmd_next)
    p = sp.add_parser("done"); p.add_argument("--step", required=True); p.add_argument("--status", required=True, choices=["ok", "partial", "failed", "skipped"]); p.add_argument("--note"); p.set_defaults(f=cmd_done)
    p = sp.add_parser("credits"); p.add_argument("--remaining", type=int, required=True); p.set_defaults(f=cmd_credits)
    sp.add_parser("time-left").set_defaults(f=cmd_time_left)
    sp.add_parser("finish").set_defaults(f=cmd_finish)
    p = sp.add_parser("prune"); p.add_argument("--dry", action="store_true"); p.set_defaults(f=cmd_prune)
    p = sp.add_parser("status"); p.add_argument("--run"); p.set_defaults(f=cmd_status)
    a = ap.parse_args(); sys.exit(a.f(a))


if __name__ == "__main__":
    main()
