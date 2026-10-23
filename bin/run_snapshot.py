#!/usr/bin/env python3
"""run_snapshot.py — copy the ledgers AS THEY STAND at the start of a run into runs/<date>/*.pre-run.*

Why: bin/replay.py can only re-test a night's scripts if it has the inputs those scripts saw. The
2026-09-23 and 09-24 runs made these copies on their own initiative and both replay EXACTLY; the
runs before them made none and cannot be re-tested. A habit that two runs kept and twenty did not
is the failure class this machine keeps meeting — so from 2026-09-26 it is a step (§0.3 step 2b)
and a declared output, not a habit.

Idempotent: a snapshot that already exists for today is never overwritten (a second fire of the
task must not replace the start-of-run state with a mid-run one).

Usage: python3 bin/run_snapshot.py          (writes runs/<today>/…, prints one line)
"""
import shutil, pathlib, datetime, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
HST = ROOT.parents[1]
TODAY = datetime.date.today().isoformat()

# live file -> snapshot name. Keep in step with bin/replay.py LEDGERS.
FILES = {
    ROOT / "config.json":            "config.pre-run.json",
    ROOT / "contacted.md":           "contacted.pre-run.md",
    ROOT / "contacted.jsonl":        "contacted.pre-run.jsonl",
    ROOT / "candidates.jsonl":       "candidates.pre-run.jsonl",
    ROOT / "calibration-log.jsonl":  "calibration.pre-run.jsonl",
    ROOT / "territory.json":         "territory.pre-run.json",
    ROOT / "warm.jsonl":             "warm.pre-run.jsonl",
    ROOT / "STATE.md":               "STATE.pre-run.md",
    ROOT / "funnel-conversion.json": "funnel-conversion.pre-run.json",
    ROOT / "funnel-outcomes.json":   "funnel-outcomes.pre-run.json",
    HST / "TLP" / "dashboard-data.json":       "counted-record.pre-run.json",
}


def main():
    out = ROOT / "runs" / TODAY
    out.mkdir(parents=True, exist_ok=True)
    made, kept, absent = [], [], []
    for src, name in FILES.items():
        dst = out / name
        if dst.exists():
            kept.append(name); continue
        if not src.exists():
            absent.append(src.name); continue
        shutil.copy2(src, dst); made.append(name)
    print("Pre-run snapshot: %d written · %d already present · %d absent%s"
          % (len(made), len(kept), len(absent), (" (" + ", ".join(absent) + ")") if absent else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
