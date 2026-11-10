#!/usr/bin/env python3
"""run.py -- the one launcher for every Marketing scheduled task (Chris 2026-10-28: simplicity, durability, fidelity).

The scheduler stores only a pointer (identical for every task, one word differs):
    Mount the vault. Run:  python3 "$HOME/mnt/ClaudeVault/3.Human Skills Training/Marketing/Automations/_shared/orchestrator/run.py" <task>
    Do exactly what it prints, step by step, until it prints DONE. If the vault or that file is unreachable, stop
    and say so. Never do anything it did not print.

This script prints the task's standing orders, read at run time from the record copy in the vault
(the task launchers beside this file, each step's LAUNCHER-<step>.md in its phase's programfiles/), so a rule change is a vault edit (versioned next to the code) and
never a scheduler write again:

    night    THE NIGHT RUN (Sun–Thu ~8:41 PM MT) — every step in order, one lock; never sends.   Rulebook M
    send     THE 7 AM SEND TASK (Mon–Fri) — sends ONLY the night's approved list.                 Rulebook M (Chris 2026-10-31)
    supply   THE SUPPLY RUN (every day ~1 AM MT) — discover → qualify → events → people; stocks the shelf for the night; never drafts, never sends.  Rulebook M9 (Chris 2026-11-08)
    read     the inbox read + master rebuild (the night run's first step)
    discover / qualify / people / draft / report   the night run's steps (Rulebook D, C/E/F, C/G/H, C/G7/I1/L, M5)

Retired modes (day, refresh, inbox, night-m2-legacy, morning) were removed 2026-11-02 in the consolidation; their
launchers are kept for rollback under Automations/archive/retired-launchers/ (restore = copy back + re-add the mode here).

Before printing the orders it self-checks: every program in every programfiles/ folder compiles, settings.json parses, every launcher exists, the lock file is readable,
and it prints a PROGRAM VERSION fingerprint (sha256 of the code + config + orders) and logs it to
Automations/_shared/orchestrator/.program-versions.log, so every run's report can say exactly which program it ran.
Exit 0 = orders printed (the session proceeds). Exit 2 = self-check failed (FAIL CLOSED: the session reports and stops).
"""
import hashlib, json, os, py_compile, re, sys, datetime as dt
import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_shared", "orchestrator")); import paths  # the one file that knows every folder (2026-11-03)
MK = paths.ROOT   # Marketing/Automations/ (the one system folder, 2026-11-02; phase layout 2026-11-03)
PROGRAM_DIRS = [paths.ORCH, paths.MASTER] + [paths.programs(p) for p in paths.PHASES]   # every programfiles/ folder
TASKS = {"night": "LAUNCHER-night-run.md", "send": "LAUNCHER-send.md", "supply": "LAUNCHER-supply.md", "read": "LAUNCHER-read.md", "discover": "LAUNCHER-discover.md",
         "qualify": "LAUNCHER-qualify.md", "people": "LAUNCHER-people.md", "draft": "LAUNCHER-draft.md", "report": "LAUNCHER-report.md"}
ENG = MK
MARK = re.compile(r"^Your FIRST output message must begin with", re.M)

def orders(task):
    p = paths.LAUNCHERS[task]   # the two task launchers sit with the orchestrator; each step's launcher with its phase (2026-11-03)
    s = open(p, encoding="utf-8").read()
    m = MARK.search(s)
    if not m:
        raise SystemExit(f"FAIL CLOSED: {TASKS[task]} has no instruction block (no 'Your FIRST output message' line)")
    body = s[m.start():]
    # the record copies end the block at a line of '---' or at end of file
    body = re.split(r"\n---\s*\n", body, maxsplit=1)[0].rstrip() + "\n"
    return p, body

def selfcheck():
    bad = []
    for d in PROGRAM_DIRS:
        for f in sorted(os.listdir(d)):
            if f.endswith(".py"):
                try: py_compile.compile(os.path.join(d, f), doraise=True)
                except Exception as ex: bad.append(f"{os.path.relpath(os.path.join(d, f), MK)}: {ex}")
    for cfgp in (paths.SETTINGS,):   # the ONE settings file (2026-11-03)
        try: json.load(open(cfgp, encoding="utf-8"))
        except Exception as ex: bad.append(f"{os.path.relpath(cfgp, MK)}: {ex}")
    for p in paths.LAUNCHERS.values():
        if not os.path.exists(p): bad.append(f"missing launcher: {os.path.relpath(p, MK)}")
    lock = paths.LOCK
    if os.path.exists(lock):
        try: json.load(open(lock))
        except Exception as ex: bad.append(f".outreach-lock unreadable: {ex}")
    return bad

def fingerprint(task, orders_text):
    h = hashlib.sha256()
    for d in PROGRAM_DIRS:
        for f in sorted(os.listdir(d)):
            if f.endswith(".py"): h.update(open(os.path.join(d, f), "rb").read())
    h.update(open(paths.SETTINGS, "rb").read())
    h.update(orders_text.encode("utf-8"))
    return h.hexdigest()[:12]

def main(a):
    if not a or a[0] not in TASKS:
        print(__doc__); print("usage: run.py night|send|supply|read|discover|qualify|people|draft|report   (retired modes: see archive/retired-launchers/)"); return 2
    task = a[0]
    bad = selfcheck()
    if bad:
        print("FAIL CLOSED: the program does not pass its self-check. Report these lines and stop; run nothing else:")
        for b in bad: print("  - " + b)
        return 2
    p, body = orders(task)
    fp = fingerprint(task, body)
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    with open(paths.VERSIONS_LOG, "a", encoding="utf-8") as f:
        f.write(f"{now} {task} {fp}\n")
    print(f"PROGRAM VERSION {fp} · task {task} · orders from {os.path.relpath(p, MK)} · self-check OK · {now}")
    print("Include the line above in your report. These are your standing orders; the scripts they name print each step.")
    print("=" * 100)
    print(body)
    print("=" * 100)
    print("END OF ORDERS. Follow them exactly; when they are complete, the report they describe is the last thing you write.")
    return 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
