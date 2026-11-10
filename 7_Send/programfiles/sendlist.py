#!/usr/bin/env python3
"""sendlist.py -- the APPROVED SEND LIST (Chris 2026-10-31: two tasks for safety).

The NIGHT run never sends. Right after its inbox read it writes tomorrow morning's approved send list; the separate
7 AM SEND task sends ONLY the rows on that list. "Approved" = the night run's rulebook checks put it there. ANYTHING
FLAGGED IS NOT APPROVED (Chris 2026-10-31): ⚠ attention · ⏸ hold · review hold · doubtful fit · successor that needs
Chris · any open ruling that names the org or thread · two-machine owner question · uncertain stage ("decided by a
thread read") · held/stopped. Those rows are listed as NOT APPROVED with the reason and are never sent by the send task.

  python3 sendlist.py build --night RUN [--slot D]   write send-lists/<D>.json (+ .md) and send-lists/<D>-review.json,
                                                     atomically, marked final. D = the next business day after RUN
                                                     (Saturday/Sunday/holiday nights roll forward). If the list for D is
                                                     already FINAL, nothing changes (a resumed night can never alter it).
  python3 sendlist.py check [--date D]               for the send task: exit 0 + "LIST OK <path>" when today's FINAL list
                                                     exists; exit 2 + the reason otherwise (no list · not final · not a
                                                     business day). The send task then sends nothing.
  python3 sendlist.py wait                           sleeps <= 170 s toward 07:00 ET; prints WAKE at/after 07:00 ET
                                                     (the send task's in-session wait — it never schedules anything)
  python3 sendlist.py report [--date D]              the send task's result vs the list → section "7 AM send" in
                                                     6_Report/ledgers/reports/<D>.md (added or replaced) and printed.
"""
import argparse, datetime as dt, glob, json, os, re, sys, time, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_shared", "orchestrator")); import paths  # the one file that knows every folder (2026-11-03)
ENG = paths.ROOT
import seqrules
from seqrules import ET
S = paths.settings()
SL = paths.SEND_LISTS
MKT = paths.MARKETING
MACH_DIR = {m: paths.machine_dir(m) for m in paths.machines()}
GM = "https://mail.google.com/mail/u/0/#all/%s"


def now():
    v = os.environ.get("SENDLIST_NOW")
    return dt.datetime.fromisoformat(v).astimezone(dt.timezone.utc) if v else dt.datetime.now(dt.timezone.utc)
def rj(p, d=None): return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else d
def jl(p): return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()] if os.path.exists(p) else []
def wj_atomic(p, o):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f: json.dump(o, f, indent=1, ensure_ascii=False, sort_keys=True)
    os.replace(tmp, p)
def link(p):
    p = os.path.abspath(p); m = re.search(r"/mnt/ClaudeVault/(.*)$", p)
    return "computer://" + urllib.parse.quote("/Users/<you>/ClaudeVault/" + m.group(1) if m else p)
def list_path(d): return os.path.join(SL, "%s.json" % d)


def slot_for_night(run):
    """The morning after the night RUN (America/Denver date), rolled to the next business day (Rulebook I3)."""
    base = dt.date.fromisoformat(re.sub(r"^rehearsal-", "", run)[:10])
    return seqrules.Calendar(S).roll(base + dt.timedelta(days=1))


# ------------------------------------------------------------------ approval (pure; tested)
def open_rulings():
    out = []
    for f in [paths.RULINGS]:   # ONE rulings log for every machine (2026-11-03)
        out += [r for r in jl(f) if r.get("status") == "open"]
    return out

def flags_of(row, org, rulings):
    """Every reason this row is NOT approved (empty list = approved). Flagged = not approved (Chris 2026-10-31)."""
    why = []
    act = row.get("action")
    if act == "REVIEW_DRAFT": why.append("review hold — drafted for Chris, never auto-sent (Rulebook I7)")
    elif act == "READ": why.append("uncertain until a full thread read (%s)" % (row.get("reason") or "")[:140])
    elif act != "SEND": why.append("%s — %s" % (act, (row.get("reason") or "")[:160]))
    if act == "SEND" and str(row.get("email")) not in ("2", "3"): why.append("not Email 2 or 3 (Email 1 is always Chris's hand-sent draft)")
    for n in row.get("notes") or []:
        if "⚠" in n or "Chris" in n: why.append("flagged: " + n[:160])
    if (org.get("fit") or {}).get("status") == "doubtful": why.append("⚠ doubtful fit (Rulebook E2)")
    for f in org.get("flags") or []:
        if f.startswith("⚠") or f.startswith("REVIEW HOLD") or "Chris to confirm" in f: why.append("org flag: " + f[:140])
    for t in org.get("threads") or []:
        if t["status"] in ("attention⚠", "hold⏸") and t["thread_id"] != row.get("thread"):
            why.append("another thread of this org is %s" % t["status"])
        if t["thread_id"] == row.get("thread") and (t.get("review_hold") or t["status"] in ("attention⚠", "hold⏸")):
            why.append("thread is %s" % ("review hold" if t.get("review_hold") else t["status"]))
    keys = {k.lower() for k in [org.get("org_id") or "", row.get("thread") or "", org.get("name") or ""] + list(org.get("domains") or []) if k and len(k) > 4}
    for r in rulings:
        txt = (" ".join(str(r.get(k) or "") for k in ("question", "context", "key", "org_id", "thread", "domain"))).lower()
        hit = sorted(k for k in keys if k in txt)
        if hit: why.append("open ruling %s names this org/thread" % r.get("id"))
    return why


def build(a):
    import send as SN
    global SL
    run = a.night
    if run.startswith("rehearsal"):                    # a rehearsal never writes a real list the send task could pick up
        SL = os.path.join(SL, "rehearsal")
    d = dt.date.fromisoformat(a.slot) if a.slot else slot_for_night(run)
    p = list_path(d.isoformat())
    cur = rj(p)
    if cur and cur.get("final"):
        print("ALREADY FINAL: %s (built %s by night %s, %d approved) — unchanged; a later pass or a resumed night never alters it."
              % (p, cur.get("built_at"), cur.get("night_run"), len(cur.get("rows", []))))
        return 0
    cal = seqrules.Calendar(S)
    orgs, gs = SN.load()
    slot, rows, br = SN.plan(d, orgs, gs, cal)
    needs = sorted({e for r in rows for e in (r.get("needs") or [])})
    if needs:
        print("FAIL CLOSED: %d successor address(es) need the ZeroBounce check first (Rulebook J6/H3). Do the read orders' step 4 "
              "CHECK loop (send.py export --slot %s), then run this build again:" % (len(needs), d))
        for e in needs: print("  CHECK " + e)
        return 3
    byid = {o["org_id"]: o for o in orgs}
    rul = open_rulings()
    cp = paths.mset("template"); kit = S.get("sender", {}).get("starter_kit", {}); kit_src = paths.mset("starter_kit_source_message_id")
    approved, not_appr, review = [], [], []
    for r in sorted(rows, key=lambda r: (r["machine"], r.get("email") or 0, r["org"])):
        org = byid.get(r["org_id"], {})
        why = flags_of(r, org, rul)
        base = dict(thread=r["thread"], org=r["org"], org_id=r["org_id"], machine=r["machine"], email=r.get("email"))
        if r["action"] == "REVIEW_DRAFT":
            review.append(dict(base, action="REVIEW_DRAFT", to=r["to"], cc=r["cc"], j6=r.get("j6"), reason=r["reason"]))
        if why:
            if r["action"] in ("SEND", "READ", "REVIEW_DRAFT", "HELD") or any(x.startswith(("flagged", "org flag", "open ruling", "⚠")) for x in why):
                not_appr.append(dict(base, action=r["action"], not_approved_because=why))
            continue
        m = r["machine"]
        approved.append(dict(base, action="SEND", to=r["to"], cc=r["cc"], j6=r.get("j6"), reason=r["reason"],
                             template={"file": os.path.relpath(paths.expand(cp.get(m) or ""), ENG), "email": r.get("email")},
                             attachment=({"filename": kit.get("filename"), "source_message_id": kit_src.get(m)}
                                         if str(r.get("email")) == "3" else None),
                             approved_because="all rulebook checks passed at %s ET: %s; recipients = Email 1's actual To/Cc%s; nothing flagged"
                                              % (now().astimezone(ET).strftime("%Y-%m-%d %H:%M"), r["reason"],
                                                 " with a validated J6 successor" if r.get("j6") else "")))
    built = now().isoformat(timespec="seconds")
    doc = {"kind": "approved-send-list", "slot": d.isoformat(), "slot_time": "07:00 America/New_York", "night_run": run, "built_at": built,
           "final": True, "bounce": br, "rows": approved, "not_approved": not_appr,
           "rule": "Only rows in 'rows' may be sent, by the separate 7 AM send task. Flagged = not approved (Chris 2026-10-31)."}
    wj_atomic(os.path.join(SL, "%s-review.json" % d.isoformat()),
              {"kind": "review-list", "slot": d.isoformat(), "night_run": run, "built_at": built, "final": True, "rows": review})
    wj_atomic(p, doc)                                  # written whole, already final — there is no half-written list
    L = ["# Approved send list — %s 07:00 ET" % d.isoformat(), "",
         "Built by night run %s at %s. The 7 AM send task sends ONLY the rows below, after a fresh read of each thread; anything that changed "
         "overnight is skipped. Flagged = not approved (Chris 2026-10-31)." % (run, built), "",
         "**Approved: %d** (OM-1 %d · OM-2 %d) · **Not approved: %d** · **Review drafts tonight: %d** · bounce rate %.1f%%" % (
             len(approved), sum(1 for x in approved if x["machine"] == "OM-1"), sum(1 for x in approved if x["machine"] == "OM-2"),
             len(not_appr), len(review), br.get("rate") or 0), "",
         "## Approved", "", "| Org | Machine | Email | Recipients | Thread |", "|---|---|---|---|---|"]
    for x in approved:
        L.append("| %s | %s | %s | %d | [open](%s) |" % (x["org"].replace("|", "/"), x["machine"], x["email"], len(x["to"]) + len(x["cc"]), GM % x["thread"]))
    L += ["", "## Not approved (never sent by the send task)", "", "| Org | Machine | Email | Why not |", "|---|---|---|---|"]
    for x in not_appr:
        L.append("| %s | %s | %s | %s |" % (x["org"].replace("|", "/"), x["machine"], x.get("email") or "–", "; ".join(x["not_approved_because"]).replace("|", "/")[:300]))
    open(p.replace(".json", ".md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("SEND LIST FINAL %s · slot %s · approved %d (OM-1 %d / OM-2 %d) · not approved %d · review drafts %d%s" % (
        p, d, len(approved), sum(1 for x in approved if x["machine"] == "OM-1"), sum(1 for x in approved if x["machine"] == "OM-2"),
        len(not_appr), len(review), " · NOT A BUSINESS DAY (nothing approved)" if br.get("not_business_day") else ""))
    print("  plain English: " + p.replace(".json", ".md"))
    return 0


def today_et(a): return dt.date.fromisoformat(a.date) if getattr(a, "date", None) else now().astimezone(ET).date()

def check(a):
    d = today_et(a); p = list_path(d.isoformat())
    if not seqrules.Calendar(S).is_business_day(d):
        print("NO SEND: %s is not a business day — nothing is sent today (Rulebook I3)." % d); return 2
    doc = rj(p)
    if not doc:
        print("NO APPROVED LIST for %s (%s missing) — send nothing; report \"no approved list\"." % (d, os.path.relpath(p, ENG))); return 2
    if doc.get("kind") != "approved-send-list" or not doc.get("final") or doc.get("slot") != d.isoformat():
        print("NO SEND: %s is not a FINAL approved list for %s — send nothing." % (os.path.relpath(p, ENG), d)); return 2
    print("LIST OK %s · %d approved (OM-1 %d / OM-2 %d) · built %s by night %s" % (
        p, len(doc["rows"]), sum(1 for x in doc["rows"] if x["machine"] == "OM-1"), sum(1 for x in doc["rows"] if x["machine"] == "OM-2"),
        doc.get("built_at"), doc.get("night_run")))
    return 0


def wait(a):
    t = now().astimezone(ET); target = dt.datetime.combine(t.date(), dt.time(7, 0), ET)
    left = (target - t).total_seconds()
    if left <= 0: print("WAKE: it is 07:00 ET or later — continue."); return 0
    time.sleep(min(170, left)); left = (target - now().astimezone(ET)).total_seconds()
    if left <= 0: print("WAKE: it is 07:00 ET — continue."); return 0
    print("WAITING: %.1f min to 07:00 ET — run  python3 7_Send/programfiles/sendlist.py wait  again" % (left / 60)); return 0


def report(a):
    d = today_et(a).isoformat(); doc = rj(list_path(d)) or {"rows": []}
    res = {}
    for m, md in MACH_DIR.items():
        for f in sorted(glob.glob(os.path.join(paths.runs("send"), m, d + "*", "sender", "*", "followup_sends.json"))):
            for r in (rj(f, {}) or {}).get("rows", []):
                if r.get("thread") in {x["thread"] for x in doc["rows"]}:
                    prev = res.get(r["thread"])
                    if not prev or r.get("status") == "sent": res[r["thread"]] = dict(r, _file=f)
    sent = [x for x in doc["rows"] if (res.get(x["thread"]) or {}).get("status") == "sent"]
    other = [x for x in doc["rows"] if x not in sent]
    L = ["## 7 AM send (%s)" % d, "",
         "Approved list: %d · **sent: %d** · not sent: %d. The send task sends only the approved list; anything that changed overnight is skipped "
         "(tonight's run decides again)." % (len(doc["rows"]), len(sent), len(other)), ""]
    for x in sent: L.append("- ✓ %s · %s · Email %s · [thread](%s)" % (x["org"], x["machine"], x["email"], GM % x["thread"]))
    for x in other:
        r = res.get(x["thread"]) or {}
        L.append("- ✗ not sent: %s · %s · Email %s — %s" % (x["org"], x["machine"], x["email"], r.get("reason") or r.get("status") or "no send attempt recorded"))
    L += ["", "Files: [send list](%s)" % link(list_path(d).replace(".json", ".md"))] + ["- [%s](%s)" % (os.path.basename(os.path.dirname(v["_file"])), link(v["_file"])) for v in {r["_file"]: r for r in res.values()}.values()]
    txt = "\n".join(L) + "\n"
    rp = os.path.join(paths.REPORTS, "%s.md" % d)
    old = open(rp, encoding="utf-8").read() if os.path.exists(rp) else "# Outreach — morning report %s\n\n" % d
    old = re.sub(r"\n## 7 AM send \(.*?(?=\n## |\Z)", "\n", old, flags=re.S)
    os.makedirs(os.path.dirname(rp), exist_ok=True)
    open(rp, "w", encoding="utf-8").write(old.rstrip() + "\n\n" + txt)
    print(txt); print("written into " + rp); return 0


def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("build"); p.add_argument("--night", required=True); p.add_argument("--slot"); p.set_defaults(f=build)
    p = sp.add_parser("check"); p.add_argument("--date"); p.set_defaults(f=check)
    sp.add_parser("wait").set_defaults(f=wait)
    p = sp.add_parser("report"); p.add_argument("--date"); p.set_defaults(f=report)
    a = ap.parse_args(); sys.exit(a.f(a))


if __name__ == "__main__":
    main()
