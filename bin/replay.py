#!/usr/bin/env python3
"""replay.py — re-run the machine's scripts against a RECORDED run and diff the results.

The regression test the ADR of 2026-08-25 promised: "11 completed runs exist with full records —
replay them; the new code must reproduce them." Run this BEFORE changing a script and again AFTER.
A script that reproduces history is safe to ship; one that does not has either a bug or a
deliberate change, and the diff names which.

How it works (nothing in the vault is touched):
  1. A scratch copy of the machine is built OUTSIDE the vault (in $HOME/replay/<date>/), laid out
     like the real folder: <HST>/Marketing/outreach-machine/ and <HST>/TLP/.
  2. Its ledgers are the INPUTS AS THEY WERE THAT NIGHT — runs/<date>/*.pre-run.* where the run
     snapshotted them (from 2026-09-23 on). Older runs fall back to today's live ledgers and are
     marked fidelity=LIVE-FALLBACK: a count that has grown since is expected to differ.
  3. The clock is pinned to <date> (datetime.date.today() / datetime.now() inside each script).
  4. Each script runs in that copy; its output JSON is diffed against runs/<date>/<name>.json.
     Timestamps are ignored; every other key must match.

Usage
  python3 bin/replay.py 2026-09-24            # one recorded run
  python3 bin/replay.py --all                 # every run with recorded outputs
  python3 bin/replay.py 2026-09-24 --keep     # leave the scratch copy for inspection

Verdicts: MATCH · DIFF (keys listed) · NO SNAPSHOT (inputs not recorded that night) · NO RECORD · NO INPUT · ERROR
Exit 0 = every comparable script matched. Exit 1 = a DIFF or ERROR. Report: history/replay/<date>.json
"""
import sys, os, json, shutil, pathlib, subprocess, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent          # outreach-machine/
HST = ROOT.parents[1]                                          # 3.Human Skills Training/
RUNS = ROOT / "runs"
SCRATCH = pathlib.Path(os.environ.get("REPLAY_HOME", pathlib.Path.home())) / "replay"
VOLATILE = {"generated", "generated_at", "timestamp", "ts", "computed_at", "_updated"}

# ledger -> its pre-run snapshot name inside runs/<date>/
LEDGERS = {"config.json": "config.pre-run.json", "contacted.md": "contacted.pre-run.md",
           "contacted.jsonl": "contacted.pre-run.jsonl", "candidates.jsonl": "candidates.pre-run.jsonl",
           "calibration-log.jsonl": "calibration.pre-run.jsonl", "territory.json": "territory.pre-run.json",
           "warm.jsonl": "warm.pre-run.jsonl", "STATE.md": "STATE.pre-run.md",
           "funnel-conversion.json": "funnel-conversion.pre-run.json",
           "funnel-outcomes.json": "funnel-outcomes.pre-run.json"}
# counted record (TLP/dashboard-data.json, one block per quarter) is snapshotted too; handled in build()
COUNTED = ("dashboard-data.json", "counted-record.pre-run.json")
# scripts whose inputs are the ledgers above: without a snapshot their result is UNTESTABLE, not wrong
CORE = {"contacted.md", "contacted.jsonl", "candidates.jsonl", "calibration-log.jsonl", "territory.json", "config.json"}
STATIC = ["dossier-template.md", "funnel-outcomes.json", "hubspot-suppression.md"]
RUN_INPUTS = ["drafts.json", "drafts_observed.json", "sent_sweep.json"]

# script -> (argv builder, recorded output, needs)
def _qh_args(rec, d):
    q = rec.get("queue_health.json") or {}
    a = ["--waiting", str(q.get("waiting", -1))]
    if q.get("floor_met_tonight") is not None:
        a += ["--drafted-tonight", str(q["floor_met_tonight"])]
    return a

SCRIPTS = [
    ("bounce_rate.py",         lambda r, d: [],            "bounce_rate.json",         []),
    ("queue_health.py",        _qh_args,                   "queue_health.json",        ["queue_health.json"]),
    ("calibration.py",         lambda r, d: [],            "calibration.json",         []),
    ("preflight.py",           lambda r, d: [],            "preflight.json",           ["drafts.json"]),
    ("dossier_check.py",       lambda r, d: [d],           "dossier_check.json",       ["dossier"]),
    ("territory_check.py",     lambda r, d: [],            "territory.json",           []),
    ("territory_reconcile.py", lambda r, d: [],            "territory_reconcile.json", []),
    ("dashboard_seed.py",      lambda r, d: [],            "dashboard_seed.json",      ["tlp"]),
]

PATCH = r'''
import datetime as _dt, sys, runpy
_D = _dt.date.fromisoformat("%(date)s")
class _date(_dt.date):
    @classmethod
    def today(cls): return cls(_D.year, _D.month, _D.day)
class _datetime(_dt.datetime):
    @classmethod
    def now(cls, tz=None): return cls(_D.year, _D.month, _D.day, 9, 30, 0)
    @classmethod
    def utcnow(cls): return cls(_D.year, _D.month, _D.day, 15, 30, 0)
_dt.date, _dt.datetime = _date, _datetime
sys.argv = %(argv)r
runpy.run_path(%(script)r, run_name="__main__")
'''


def strip(o):
    if isinstance(o, dict):
        return {k: strip(v) for k, v in o.items() if k not in VOLATILE}
    if isinstance(o, list):
        return [strip(x) for x in o]
    return o


def diff_keys(a, b, path=""):
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a: out.append(path + k + " (only recorded)")
            elif k not in b: out.append(path + k + " (only replay)")
            else: out += diff_keys(a[k], b[k], path + k + ".")
    elif a != b:
        out.append(path.rstrip(".") + ": %s -> %s" % (json.dumps(a)[:60], json.dumps(b)[:60]))
    return out


def build(date, keep):
    box = SCRATCH / date
    if box.exists():
        shutil.rmtree(box)
    hst = box / "HST"
    om = hst / "Marketing" / "outreach-machine"
    (om / "runs" / date).mkdir(parents=True)
    (hst / "TLP").mkdir(parents=True)
    shutil.copytree(ROOT / "bin", om / "bin", ignore=shutil.ignore_patterns("__pycache__", "*.pre-*"))
    rec = RUNS / date
    # The recorded outputs were computed at §0.3 step 19, AFTER that night's ledger writes. So the
    # right inputs are the ledgers AS THEY STOOD AT THE END of that run, which is exactly what the
    # NEXT run snapshotted as its *.pre-run.* files. For the most recent run, the live ledgers ARE
    # that end-of-run state (nothing has run since). Only older runs without a following snapshot
    # fall back to live ledgers, and those are marked so a grown count is read as expected.
    later = sorted(d.name for d in RUNS.iterdir() if d.is_dir() and d.name > date and d.name[:2] == "20")
    nxt = RUNS / later[0] if later else None
    fidelity = {}
    for live, snap in LEDGERS.items():
        if nxt and (nxt / snap).exists():
            src, tag = nxt / snap, "END-OF-RUN (next run's snapshot)"
        elif not later and (ROOT / live).exists():
            src, tag = ROOT / live, "END-OF-RUN (live; latest run)"
        elif (ROOT / live).exists():
            src, tag = ROOT / live, "LIVE-FALLBACK"
        else:
            continue
        shutil.copy2(src, om / live)
        fidelity[live] = tag
    for f in STATIC:
        if (ROOT / f).exists(): shutil.copy2(ROOT / f, om / f)
    for f in RUN_INPUTS:
        if (rec / f).exists(): shutil.copy2(rec / f, om / "runs" / date / f)
    if (ROOT / f"dossier-{date}.md").exists():
        shutil.copy2(ROOT / f"dossier-{date}.md", om / f"dossier-{date}.md")
    if (rec / "dashboard_seed.json").exists():
        shutil.copy2(rec / "dashboard_seed.json", om / "runs" / date / "dashboard_seed.recorded.json")
    for f in ("dashboard-data.json", "tlp-practice-dashboard.html", "TLP-Rules.md"):
        if (HST / "TLP" / f).exists(): shutil.copy2(HST / "TLP" / f, hst / "TLP" / f)
    if nxt and (nxt / COUNTED[1]).exists():
        shutil.copy2(nxt / COUNTED[1], hst / "TLP" / COUNTED[0]); fidelity["counted-record"] = "END-OF-RUN (next run's snapshot)"
    elif later:
        fidelity["counted-record"] = "LIVE-FALLBACK"
    # previous run's drafts.json (as-sent delta input)
    prev = sorted(d.name for d in RUNS.iterdir() if d.is_dir() and d.name < date and d.name[:2] == "20")
    if prev and (RUNS / prev[-1] / "drafts.json").exists():
        (om / "runs" / prev[-1]).mkdir(parents=True, exist_ok=True)
        shutil.copy2(RUNS / prev[-1] / "drafts.json", om / "runs" / prev[-1] / "drafts.json")
    # funnel-conversion.json is an INPUT to dashboard_seed and an output of funnel_conversion.py;
    # give the sandbox whatever the vault has so dashboard_seed can run.
    return box, om, fidelity


def replay(date, keep=False):
    rec = RUNS / date
    if not rec.is_dir():
        print("no recorded run at runs/%s" % date); return 1
    recorded = {}
    for name in ("queue_health.json",):
        if (rec / name).exists(): recorded[name] = json.loads((rec / name).read_text(encoding="utf-8"))
    box, om, fidelity = build(date, keep)
    rows, bad = [], 0
    for script, argf, outname, needs in SCRIPTS:
        row = {"script": script, "output": outname}
        if "drafts.json" in needs and not (rec / "drafts.json").exists():
            row["verdict"] = "NO INPUT"; row["note"] = "no drafts.json that night"; rows.append(row); continue
        if "queue_health.json" in needs and "queue_health.json" not in recorded:
            row["verdict"] = "NO INPUT"; row["note"] = "no recorded --waiting"; rows.append(row); continue
        if "dossier" in needs and not (om / f"dossier-{date}.md").exists():
            row["verdict"] = "NO INPUT"; row["note"] = "dossier not on disk"; rows.append(row); continue
        if "tlp" in needs and not (box / "HST" / "TLP" / "tlp-practice-dashboard.html").exists():
            row["verdict"] = "NO INPUT"; row["note"] = "dashboard html absent"; rows.append(row); continue
        core_missing = [k for k, v in fidelity.items() if v == "LIVE-FALLBACK" and k in CORE]
        if core_missing and script != "dossier_check.py":
            row["verdict"] = "NO SNAPSHOT"; row["note"] = "inputs not recorded that night (pre-2026-09-23)"; rows.append(row); continue
        if script == "dashboard_seed.py" and any(fidelity.get(k) == "LIVE-FALLBACK" for k in ("funnel-conversion.json", "counted-record")):
            row["verdict"] = "NO SNAPSHOT"; row["note"] = "funnel/counted-record not recorded that night"; rows.append(row); continue
        argv = [script] + argf(recorded, date)
        code = PATCH % {"date": date, "argv": argv, "script": str(om / "bin" / script)}
        # preflight.py runs at §0.3 step 14, BEFORE the night's drafts are appended to contacted.jsonl
        # (it asks "is this org already contacted?"). Feed it the START-of-run ledger, then put the
        # end-of-run ledger back for the scripts that run at step 19.
        swap = script == "preflight.py" and (rec / "contacted.pre-run.jsonl").exists()
        if swap:
            shutil.copy2(om / "contacted.jsonl", om / "contacted.end.jsonl")
            shutil.copy2(rec / "contacted.pre-run.jsonl", om / "contacted.jsonl")
            row["input"] = "contacted.jsonl = start-of-run snapshot"
        r = subprocess.run([sys.executable, "-c", code], cwd=str(om), capture_output=True, text=True, timeout=120)
        if swap:
            shutil.copy2(om / "contacted.end.jsonl", om / "contacted.jsonl")
        row["exit"] = r.returncode
        row["stdout"] = r.stdout.strip()[-400:]
        if r.returncode not in (0, 1, 2, 3) or ("Traceback" in r.stderr):
            row["verdict"] = "ERROR"; row["note"] = r.stderr.strip()[-300:]; bad += 1; rows.append(row); continue
        got_p = om / "runs" / date / outname
        exp_p = rec / outname
        if not exp_p.exists():
            row["verdict"] = "NO RECORD"; rows.append(row); continue
        if not got_p.exists():
            row["verdict"] = "ERROR"; row["note"] = "script wrote no %s" % outname; bad += 1; rows.append(row); continue
        exp = strip(json.loads(exp_p.read_text(encoding="utf-8")))
        got = strip(json.loads(got_p.read_text(encoding="utf-8")))
        d = diff_keys(exp, got)
        if d:
            row["verdict"] = "DIFF"; row["diff"] = d[:12]; bad += 1
        else:
            row["verdict"] = "MATCH"
        rows.append(row)
    if not keep:
        shutil.rmtree(box, ignore_errors=True)
    report = {"date": date, "replayed_at": datetime.datetime.now().isoformat(timespec="minutes"),
              "fidelity": fidelity, "results": rows, "status": "OK" if bad == 0 else "DIFF"}
    out = ROOT / "history" / "replay"; out.mkdir(parents=True, exist_ok=True)
    (out / f"{date}.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    lf = [k for k, v in fidelity.items() if v == "LIVE-FALLBACK"]
    fb = "end-of-run ledgers" + ("" if not lf else " (LIVE-FALLBACK for %s — grown counts expected)" % ", ".join(lf))
    print("Replay %s — inputs: %s" % (date, fb))
    for r in rows:
        line = "  %-24s %-9s" % (r["script"], r["verdict"])
        if r.get("note"): line += " — " + r["note"].splitlines()[-1][:120]
        print(line)
        for d in r.get("diff", []): print("      · " + d)
    print("  => %s" % report["status"])
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__); sys.exit(0)
    keep = "--keep" in a
    if a[0] == "--all":
        dates = sorted(d.name for d in RUNS.iterdir() if d.is_dir() and d.name[:2] == "20")
        rc = 0
        for d in dates:
            rc |= replay(d, keep)
        sys.exit(rc)
    sys.exit(replay(a[0], keep))
