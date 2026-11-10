#!/usr/bin/env python3
"""lock.py — one lock for every outreach task (Chris, 2026-10-26: 'make this serial so there is no
chance of them running simultaneously').

The lock is a file: Automations/.outreach-lock (JSON: holder, fire, started, heartbeat, quiet_until). Rules:
  acquire <holder> [--fire ID] [--exclusive]  -> exit 0 and prints ACQUIRED, or exit 2 and prints HELD BY <holder> ...
                                   --exclusive: the SAME holder that is still alive also yields (the night run uses it,
                                   so a second night start can never run beside a live one).
  release <holder>              -> releases only if <holder> owns it (exit 0), else exit 2
  beat <holder> [--until EPOCH] -> the holder proves it is alive (heartbeat = now). --until marks a planned
                                   quiet wait (e.g. the night run waiting for 07:00 ET): the lock is never
                                   stale before that time.
  status [send]                 -> prints the lock (or the send lock) or FREE
  SEND LOCK (2026-10-31): holder "send" (the 7 AM send task) uses its own file .outreach-send-lock — independent of
                                   the night run's lock in both directions.
  --stale-hours H (default 4)   -> a lock whose last sign of life (start, heartbeat, or the end of a planned
                                   quiet wait) is older than H hours is treated as abandoned and taken over,
                                   and that takeover is printed (it is a finding for the report).

NIGHT RUN NESTING (Stage 8, 2026-10-31). The night run holds the lock as "night-run" for the whole night and
runs the existing steps (discover, qualify, people, draft, morning-sender) inside it. While the night run's
checkpoint file says it is AT that step (night/current.json), the step's own
`acquire <step-holder>` prints ACQUIRED-NESTED (exit 0, the night lock is kept) and its `release` prints
RELEASED-NESTED (exit 0, the night lock is kept). Any other holder — including the same step started by a
separate scheduled task while the night run is elsewhere — still yields. Every launcher calls `acquire`
FIRST and `release` LAST; a launcher that cannot acquire does nothing else and reports "yielded to <holder>".
"""
import json, sys, os, time, datetime as dt
import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_shared", "orchestrator")); import paths  # the one file that knows every folder (2026-11-03)
ROOT = paths.ROOT
LOCK = paths.LOCK
# SEND LOCK (Chris 2026-10-31: two tasks for safety). The 7 AM send task holds its OWN lock file, so the night run
# (holder night-run, still looping at 7 AM on a long night) can never block or overlap the sends, and the send task
# can never block the night. Holder "send" always uses this file; every other holder uses the shared lock above.
SEND_HOLDER = "send"
LOCK_SEND = paths.LOCK_SEND
NIGHT_CUR = paths.NIGHT_CUR
NIGHT = "night-run"
# UMBRELLA HOLDERS (2026-11-08, the Supply Run): the night run and the supply run each hold the lock for a whole run and run the
# step launchers inside it; a step nests under whichever umbrella is alive AND at that step (its current.json).
UMBRELLAS = {NIGHT: paths.NIGHT_CUR, "supply-run": paths.SUPPLY_CUR}

def read():
    # The vault forbids deletes, so a released lock is a file whose holder is null, not a missing file.
    try:
        l = json.load(open(LOCK)); return l if l.get("holder") else None
    except Exception: return None

def alive_at(l):
    """Last sign of life: start, heartbeat, or the end of a planned quiet wait."""
    return max(l.get("started") or 0, l.get("heartbeat") or 0, l.get("quiet_until") or 0)

def night_step_holder(umbrella=NIGHT):
    try:
        c = json.load(open(UMBRELLAS[umbrella]))
        return c.get("step_holder") if c.get("status") == "running" else None
    except Exception: return None

def write(o): json.dump(o, open(LOCK, "w"))

def main(a):
    stale = 4.0
    if "--stale-hours" in a:
        i = a.index("--stale-hours"); stale = float(a[i+1]); del a[i:i+2]
    if not a: print(__doc__); return 3
    global LOCK
    if len(a) > 1 and a[1] == SEND_HOLDER: LOCK = LOCK_SEND        # the send lock: acquire/release/beat/status send
    cmd = a[0]; now = time.time()
    if cmd == "status":
        l = read()
        if not l: print("FREE"); return 0
        print(f"HELD BY {l['holder']} fire={l.get('fire')} since={l['started_iso']} quiet_for_min={(now-alive_at(l))/60:.0f}"
              + (f" quiet_until={dt.datetime.utcfromtimestamp(l['quiet_until']).isoformat()}Z" if l.get("quiet_until") and l["quiet_until"] > now else ""))
        return 0
    if cmd == "acquire":
        holder = a[1]; fire = a[a.index("--fire")+1] if "--fire" in a else None; excl = "--exclusive" in a
        l = read()
        if l and l["holder"] in UMBRELLAS and holder != l["holder"] and LOCK != LOCK_SEND and (now - alive_at(l)) < stale*3600:
            if night_step_holder(l["holder"]) == holder:
                print(f"ACQUIRED-NESTED by {holder} inside {l['holder']} fire={l.get('fire')} (the {l['holder']} lock is kept)"); return 0
        if l and (now - alive_at(l)) < stale*3600 and l["holder"] != holder:
            print(f"HELD BY {l['holder']} fire={l.get('fire')} quiet_for_min={(now-alive_at(l))/60:.0f} -> yield"); return 2
        if l and (now - alive_at(l)) >= stale*3600:
            print(f"FINDING: stale lock from {l['holder']} (no sign of life for {(now-alive_at(l))/3600:.1f}h) taken over")
        if l and l["holder"] == holder and excl and (now - alive_at(l)) < stale*3600:
            print(f"HELD BY {holder} (another live session) fire={l.get('fire')} quiet_for_min={(now-alive_at(l))/60:.0f} -> yield"); return 2
        if l and l["holder"] == holder and (now - alive_at(l)) < stale*3600:
            print(f"FINDING: {holder} already held the lock (fire={l.get('fire')}) and is acquiring again — treated as a resume")
        write({"holder": holder, "fire": fire, "started": now, "heartbeat": now, "started_iso": dt.datetime.utcnow().isoformat()+"Z"})
        print(f"ACQUIRED by {holder} fire={fire}"); return 0
    if cmd == "beat":
        holder = a[1]; l = read()
        if not l or l["holder"] != holder: print(f"NOT YOURS: held by {(l or {}).get('holder')}"); return 2
        l["heartbeat"] = now
        if "--until" in a: l["quiet_until"] = float(a[a.index("--until")+1])
        write(l); print(f"BEAT {holder}" + (f" quiet_until={l.get('quiet_until')}" if "--until" in a else "")); return 0
    if cmd == "release":
        holder = a[1]; l = read()
        if not l: print("FREE already"); return 0
        if l["holder"] in UMBRELLAS and holder != l["holder"] and night_step_holder(l["holder"]) == holder:
            print(f"RELEASED-NESTED by {holder} (the {l['holder']} lock is kept)"); return 0
        if l["holder"] != holder: print(f"NOT YOURS: held by {l['holder']}"); return 2
        write({"holder": None, "released_by": holder, "released_iso": dt.datetime.utcnow().isoformat()+"Z", "previous": l})
        print(f"RELEASED by {holder}"); return 0
    print(__doc__); return 3

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
