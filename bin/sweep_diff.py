#!/usr/bin/env python3
"""sweep_diff.py — decide what the TLP refresh has to READ, so the session reads only that.

THE DASHBOARD GATHERS AND PRESENTS. Chris, 2026-09-28.  This script counts nothing. It never writes
a figure. It compares a fresh Gmail sweep against the thread ledger in TLP/dashboard-data.json and
says which threads are new or have grown since they were last read in full. Judgment stays with the
refresh session; the mechanical part (mailwarming gate, auto-reply patterns, bounce patterns, the
5-message preview cap, de-duplication against the counted record) lives here, where it is testable.

HOW A REFRESH USES IT
  1. The session runs the sweep queries (TLP-Rules.md, Gate 3) with view THREAD_VIEW_MINIMAL and
     saves each raw result page, exactly as the Gmail tool returned it, to
         Marketing/outreach-machine/runs/<today>/sweep/<anything>.json
  2.  python3 bin/sweep_diff.py                  -> prints TO READ / PROPOSED EXCLUSIONS / SKIPPED,
                                                   writes runs/<today>/sweep_diff.json
  3.  python3 bin/sweep_diff.py --apply-exclusions
                                                -> adds the proposed auto-reply / bounce / calendar
                                                   threads to the ledger as excluded (nothing else)
  4. The session reads the TO READ threads with get_thread, makes the judgment calls, writes the
     record rows, then registers each thread it read:
        python3 bin/sweep_diff.py set <thread_id> counted  --field Approaches --org "Org name"
        python3 bin/sweep_diff.py set <thread_id> excluded --reason same-org --org "Org name"
     `set` copies the thread's current message count and newest date from the sweep, so the next
     diff treats the thread as read-through-today.

Reads   TLP/dashboard-data.json (ledger only), runs/<date>/sweep/*.json
Writes  runs/<date>/sweep_diff.json; with --apply-exclusions or `set`, TLP/dashboard-data.json
Exit    0 normally; 2 when no sweep files are found (that is a run defect, not an empty week)
"""
import json, pathlib, re, sys, datetime, argparse, os, time
os.environ.setdefault("TZ", "America/Denver")
try:
    time.tzset()
except Exception:
    pass

HST  = pathlib.Path(__file__).resolve().parents[3]
DATA = HST / "TLP" / "dashboard-data.json"
RUNS = HST / "Marketing" / "outreach-machine" / "runs"

ME             = {"<SENDER_EMAIL>", "<PERSONAL_EMAIL>"}
MAILWARMING    = "Label_1"           # Apollo Mailwarming. Re-check if Gmail labels ever change.
PREVIEW_CAP    = 5                   # search_threads previews at most ~5 messages per thread
AUTO_RE        = re.compile(r"^(re:\s*)?(automatic reply|auto[- ]?reply|autoreply|out of (the )?office|ooo\b|automated response|auto response|"
                            r"thank you for (contacting|your email|your message)|we received your (email|message))", re.I)
CAL_RE         = re.compile(r"^(accepted|declined|tentative|tentatively accepted|updated invitation|invitation|canceled event|cancelled event):", re.I)
BOUNCE_SENDERS = re.compile(r"(mailer-daemon|postmaster|noreply@.*google|mail delivery)", re.I)
NOISE_SENDERS  = re.compile(r"(dmarc|no-?reply@(calendar|docs|drive)\.google\.com|@hubspot\.com|@apollo\.io|@fathom\.video)", re.I)


def load_sweep(day):
    files = sorted((RUNS / day / "sweep").glob("*.json"))
    threads = {}
    for f in files:
        raw = json.loads(f.read_text())
        for t in raw.get("threads", []):
            tid = t["id"]
            if tid not in threads or (t.get("messageCount") or 0) > (threads[tid].get("messageCount") or 0):
                threads[tid] = t
    return files, threads


def classify(t, ledger):
    """One thread -> (bucket, reason, detail). Buckets: read | exclude | skip."""
    msgs   = t.get("messages", [])
    count  = t.get("messageCount") or len(msgs)
    labels = {l for m in msgs for l in m.get("labelIds", [])}
    subj   = next((m.get("subject", "") for m in msgs if m.get("subject")), "")
    senders = [m.get("sender", "").lower() for m in msgs]
    inbound = [s for s in senders if s and s not in ME]
    newest  = max((m.get("date", "")[:10] for m in msgs), default="")

    if MAILWARMING in labels:
        return "skip", "mailwarming", ""
    e = ledger.get(t["id"])
    if e:
        if e.get("disposition") == "pending":
            return "read", "pending", e.get("note", "")
        if count > e.get("messages", 0):
            return "read", "grew", f"{e['messages']} -> {count} messages since last read; {e['disposition']} as {e.get('field') or e.get('reason')}"
        if count < e.get("messages", 0):
            return "read", "shrank", f"ledger has {e['messages']}, sweep shows {count} — a message was deleted or the sweep is partial"
        return "skip", "unchanged", ""
    if not inbound:
        return "skip", "send-only", ""
    if all(BOUNCE_SENDERS.search(s) for s in inbound):
        return "exclude", "bounce", subj
    if AUTO_RE.search(subj):
        return "exclude", "auto-reply", subj
    if CAL_RE.search(subj):
        return "exclude", "calendar", subj
    if all(NOISE_SENDERS.search(s) for s in inbound):
        return "exclude", "non-hst", subj
    cap = " ⚠ preview capped — read with get_thread" if len(msgs) >= PREVIEW_CAP else ""
    return "read", "new", f"{subj} · {count} msgs · newest {newest} · from {', '.join(sorted(set(inbound)))}{cap}"


def org_guess(t):
    """A label for the report only — the session names the organisation when it registers the thread."""
    for m in t.get("messages", []):
        s = m.get("sender", "")
        if s and s.lower() not in ME:
            return s.split("@")[-1]
    return "?"


def current_block(d, day):
    qs = [q for q in d["quarters"] if q["start"] <= day <= q["end"]]
    if not qs:
        sys.exit(f"PROBLEM no quarter block contains {day}")
    return qs[0]


def diff(day):
    d = json.loads(DATA.read_text())
    q = current_block(d, day)
    ledger = q.setdefault("threads", {})
    files, threads = load_sweep(day)
    if not files:
        print(f"PROBLEM no sweep files in {RUNS / day / 'sweep'} — save the raw search_threads pages there first")
        sys.exit(2)
    out = {"date": day, "quarter": q["id"], "files": [f.name for f in files], "threads_in_sweep": len(threads),
           "read": [], "exclude": [], "skipped": {}}
    for tid, t in sorted(threads.items(), key=lambda kv: max((m.get("date", "") for m in kv[1].get("messages", [])), default="")):
        bucket, reason, detail = classify(t, ledger)
        msgs = t.get("messages", [])
        row = {"thread": tid, "reason": reason, "messages": t.get("messageCount") or len(msgs),
               "newest": max((m.get("date", "")[:10] for m in msgs), default=""),
               "org": (ledger.get(tid) or {}).get("org") or org_guess(t), "detail": detail,
               "url": t.get("viewUrl", "")}
        if bucket == "read":
            out["read"].append(row)
        elif bucket == "exclude":
            out["exclude"].append(row)
        else:
            out["skipped"][reason] = out["skipped"].get(reason, 0) + 1
    # ledger threads the sweep never returned: nothing to do, but say so once so a broken query is visible
    missing = [tid for tid in ledger if tid not in threads]
    out["ledger_threads_not_in_sweep"] = len(missing)
    out["ledger_size"] = len(ledger)
    (RUNS / day).mkdir(parents=True, exist_ok=True)
    (RUNS / day / "sweep_diff.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    return out


def report(out):
    print(f"sweep_diff {out['date']} · {out['quarter']} · {out['threads_in_sweep']} threads in {len(out['files'])} sweep file(s) · ledger {out['ledger_size']}")
    print()
    print(f"TO READ — {len(out['read'])}")
    if out["read"]:
        print("| thread | why | msgs | newest | who | detail |")
        print("| --- | --- | --- | --- | --- | --- |")
        for r in out["read"]:
            print(f"| {r['thread']} | {r['reason']} | {r['messages']} | {r['newest']} | {r['org']} | {r['detail']} |")
    print()
    print(f"PROPOSED EXCLUSIONS — {len(out['exclude'])}  (apply with --apply-exclusions)")
    if out["exclude"]:
        print("| thread | reason | newest | from | subject |")
        print("| --- | --- | --- | --- | --- |")
        for r in out["exclude"]:
            print(f"| {r['thread']} | {r['reason']} | {r['newest']} | {r['org']} | {r['detail']} |")
    print()
    sk = out["skipped"]
    print("SKIPPED — " + ", ".join(f"{k} {v}" for k, v in sorted(sk.items())) if sk else "SKIPPED — none")
    if out["ledger_threads_not_in_sweep"]:
        print(f"note: {out['ledger_threads_not_in_sweep']} ledger thread(s) did not appear in this sweep — expected for threads "
              f"outside the sweep queries (different subject, inbound-only); a large number means a query changed")


def apply_exclusions(day):
    d = json.loads(DATA.read_text())
    q = current_block(d, day)
    ledger = q.setdefault("threads", {})
    out = json.loads((RUNS / day / "sweep_diff.json").read_text())
    n = 0
    for r in out["exclude"]:
        if r["thread"] in ledger:
            continue
        ledger[r["thread"]] = {"org": r["org"], "disposition": "excluded", "messages": r["messages"], "last": r["newest"],
                               "reason": r["reason"], "note": f"auto-excluded by sweep_diff {day}: {r['detail'][:80]}"}
        n += 1
    DATA.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
    print(f"added {n} excluded thread(s) to the {q['id']} ledger")


def set_entry(day, tid, disposition, org, field, reason, note):
    d = json.loads(DATA.read_text())
    q = current_block(d, day)
    ledger = q.setdefault("threads", {})
    _, threads = load_sweep(day)
    t = threads.get(tid)
    e = ledger.get(tid, {})
    msgs = (t or {}).get("messages", [])
    e.update({"org": org or e.get("org") or org_guess(t or {}), "disposition": disposition,
              "messages": (t or {}).get("messageCount") or len(msgs) or e.get("messages", 0),
              "last": max((m.get("date", "")[:10] for m in msgs), default=e.get("last", day))})
    if field:  e["field"] = field
    if reason: e["reason"] = reason
    if note:   e["note"] = note
    if disposition == "counted":
        e.pop("reason", None)
    ledger[tid] = e
    DATA.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
    print(f"{tid}: {disposition} · {e['org']} · {e['messages']} msgs through {e['last']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--date", default=datetime.date.today().isoformat(), help="run folder date, default today")
    ap.add_argument("--apply-exclusions", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    s = sub.add_parser("set", help="register a thread the session has read")
    s.add_argument("thread"); s.add_argument("disposition", choices=["counted", "excluded", "pending"])
    s.add_argument("--org"); s.add_argument("--field"); s.add_argument("--reason"); s.add_argument("--note")
    a = ap.parse_args()
    if a.cmd == "set":
        return set_entry(a.date, a.thread, a.disposition, a.org, a.field, a.reason, a.note)
    if a.apply_exclusions:
        return apply_exclusions(a.date)
    report(diff(a.date))


if __name__ == "__main__":
    main()
