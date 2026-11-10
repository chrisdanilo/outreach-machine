#!/usr/bin/env python3
"""send.py — the ONE follow-up sender for every machine (Rulebook C1, C8, C9, I, J, K, L). Stage 3: DRY RUN ONLY.

  python3 send.py plan    [--slot 2026-11-02] [--preview 2026-11-03] [--out master/dry-run-2026-11-02.md]
  python3 send.py labels  print the label migration plan (old trees -> OM-1 / OM-2). Never applies it.
  python3 send.py --live  FAILS CLOSED unless master/settings.json sender.live is true (it is false). Live sending reuses the
                          proven engine path (7_Send/programfiles/followup_send.py: fresh read <= 180 s -> arm in batches -> --intent GO ->
                          one Zapier reply_to_message per thread -> verify -> labels). Stage 3 never calls it.

Inputs: _shared/master/orgs.jsonl (the master list, rebuilt with Gmail state), 1_Read-the-Inbox/ledgers/gmail-state.json (inbox reader), _shared/master/settings.json.
Decisions come from seqrules.py — the same rules build_master.py uses for next_due.
Never sends Email 1. Never plans a thread twice. Never adds a covering colleague (J5). A successor named in an auto-reply
takes the departed recipient's spot (J6, Chris 2026-10-30) — successors.py.
"""
import argparse, collections, datetime, importlib.util, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_shared", "orchestrator")); import paths  # the one file that knows every folder (2026-11-03)
import seqrules, successors
from seqrules import ET

MASTER = paths.MASTER
S = paths.settings()
ROOT = paths.MASTER
MKT = paths.MARKETING
SEND_RUNS = paths.runs("send")                     # runs/<slot>/master-plan.json (was master/runs/<slot>/, 2026-11-03)
SND = S.get("sender", {})
ME = "chris@chrisdanilo.com"
SYM = {"open": None, "closed✗": "✗", "replied★": "★", "attention⚠": "⚠", "hold⏸": "⏸", "stopped": "✗"}
STAGE_NUM = {"E1-draft": "0", "E1": "1", "E2": "2", "E3": "3"}
SUCC_RECS, SUCC_VAL = successors.load()
PROV_BAD = [a for r in SUCC_RECS for a in successors.provenance_ok(r)]


def load():
    orgs = [json.loads(l) for l in open(paths.ORGS, encoding="utf-8")]
    gp = paths.GMAIL_STATE
    gs = json.load(open(gp, encoding="utf-8")) if os.path.exists(gp) else {"threads": {}, "separate_threads_by_domain": {}}
    return orgs, gs


def dom(a):
    return a.lower().rsplit("@", 1)[-1]


def recipients(t, g):
    """Email 1's actual To/Cc (Rulebook: recipients = what Chris sent), from the fullest source available."""
    for s in (g or {}).get("sends", []):
        if s.get("to"): return [x.lower() for x in s["to"]], [x.lower() for x in s.get("cc", [])], "Gmail (thread read)"
    for s in t["messages_sent"]:
        if s.get("to"): return [x.lower() for x in s["to"]], [x.lower() for x in s.get("cc", [])], "Gmail (label pull)"
    return [], [], None


def autos_for(t, g, gs, to, cc, last):
    out = []
    seen = set()
    cands = list((g or {}).get("auto", []))
    for a in to + cc:
        cands += [x for x in gs["separate_threads_by_domain"].get(dom(a), {}).get("auto", []) if x["sender"] == a]
    for x in cands:
        key = (x["sender"], x.get("thread"))
        if key in seen or x.get("redirect"): continue
        seen.add(key)
        out.append(dict(x, after_last_send=bool(last and x.get("date") and x["date"] >= last)))
    return out


SENT_FROM = "9999"


def plan(slot_date, orgs, gs, cal, sim=None):
    global SENT_FROM
    SENT_FROM = min([w.split()[0][:10] for w in gs.get("completeness", {}).get("sent_windows", [])] or ["9999"])
    slot = cal.slot(slot_date)
    if slot.date() != slot_date:
        return slot, [], {"bounces": 0, "sends": 0, "rate": 0.0, "not_business_day": True}
    rows, claimed_org = [], set()
    sim = sim or {}
    domidx = {}
    for o in orgs:
        for dd in o.get("domains") or []:
            domidx.setdefault(dd.lower(), {"org_id": o["org_id"], "name": o["name"], "has_thread": bool(o["threads"]),
                                           "excluded": any(v for v in (o.get("exclusions") or {}).values())})
    for o in sorted(orgs, key=lambda r: r["org_id"]):
        for t in o["threads"]:
            tid = t["thread_id"]
            g = gs["threads"].get(tid)
            st = t["status"]
            if t["stage"] == "E1-draft": continue                        # Email 1 is always Chris's (C1)
            mach = (t["machine"] or "?").split("/")[-1] if t["machine"] else "?"
            if "OM-1" in (t["machine"] or "") and "OM-2" in (t["machine"] or ""): mach = o["owner_machine"] if o["owner_machine"] != "none" else "OM-1"
            to, cc, rsrc = recipients(t, g)
            j6 = successors.apply(to, cc, SUCC_RECS, mach, o.get("domains") or [], domidx, SUCC_VAL, slot.date(), prov_bad=PROV_BAD) if SUCC_RECS else None
            sends = [{"date": s["date"], "to": s.get("to") or [], "cc": s.get("cc") or []} for s in t["messages_sent"]]
            if g and g.get("read") == "full": sends = g["sends"]
            sends = sends + sim.get(tid, {}).get("sends", [])
            if sim.get(tid, {}).get("closed"): continue
            last = sends[-1]["date"][:10] if sends else None
            gv = t.get("gmail") or {}
            bounced = gv.get("bounced", [])
            drafts = gv.get("drafts", 0)
            human = bool(gv.get("human")) and not st.startswith("closed")
            autos = autos_for(t, g, gs, to, cc, last)
            ex = o.get("exclusions") or {}
            stopped = None
            if st == "stopped": stopped = "stopped by Chris's R1 ruling (%s)" % (t.get("override") or "")[:90]
            elif o["owner_machine"] in ("OM-1", "OM-2") and mach != o["owner_machine"] and len({x["machine"] for x in o["threads"]}) > 1:
                stopped = "follow-ups belong to %s (both machines wrote to this org — Rulebook E6)" % o["owner_machine"]
            th = {"stage_floor": int(STAGE_NUM.get(t["stage"], "0")), "status": "open" if st in ("open",) else st, "sends": [dict(s, to=s.get("to") or to, cc=s.get("cc") or cc) for s in sends]}
            if human: th["status"] = "replied★"
            if j6 and j6["changed"] and th["sends"]:
                th["sends"][-1] = dict(th["sends"][-1], to=j6["to"], cc=j6["cc"])
            d = seqrules.decide(th, slot, cal, bounced=bounced, autos=autos, human=human, drafts=drafts,
                                review_hold=t.get("review_hold"), stopped=stopped,
                                exclusions={k: v for k, v in ex.items() if v},
                                partial=not (g and g.get("read") == "full"))
            if d["action"] in ("SEND", "REVIEW_DRAFT", "CLOSE") and d.get("partial") and d.get("due", "9")[:10] < SENT_FROM:
                d = dict(d, action="READ", reason="Email %s was due %s, before the complete sent-mail check (from %s) — the thread read confirms it was not already sent unlabelled, then it %s"
                         % (d.get("email") or 3, (d.get("due") or "")[:10], SENT_FROM, "goes" if d["action"] != "CLOSE" else "closes"))
            if d["action"] == "CLOSE" and d.get("partial"):
                d = dict(d, reason=d["reason"] + " (a thread read confirms no reply first)")
            if d["action"] == "NONE" and st.startswith("closed"): continue
            if d["action"] == "STOPPED" and st.startswith("replied") and not (human and t.get("gmail") and t["gmail"].get("human")): continue
            succ = [a for a in autos if "successor" in (a.get("note") or "").lower()]
            if j6 and (j6["changed"] or j6["needs"] or j6["flags"] or j6["notes"]):
                d = dict(d, notes=list(d.get("notes") or []) + j6["notes"] + j6["flags"])
                if d["action"] in ("SEND", "REVIEW_DRAFT"):
                    if j6["needs"]:
                        d = dict(d, action="HELD", reason="successor address(es) need the ZeroBounce check before this email goes (J6/H3): " + ", ".join(j6["needs"]))
                    elif any("left and no" in f for f in j6["flags"]):
                        d = dict(d, action="HELD", reason="the To recipient has left and no successor could be added — Chris decides (J6)")
            row = dict(d, org=o["name"], org_id=o["org_id"], thread=tid, machine=mach, stage=t["stage"], status=st,
                       recipients_src=rsrc, to=(j6["to"] if j6 and j6["changed"] else to), cc=(j6["cc"] if j6 and j6["changed"] else cc),
                       bounced=bounced, autos=[a["sender"] for a in autos if a["after_last_send"]],
                       successor_note=[a["sender"] + ": " + a["note"] for a in succ], human=gv.get("human") or [],
                       j6=({k: j6[k] for k in ("to", "cc", "add_names", "remove_names")} if j6 and j6["changed"] else None),
                       needs=(j6["needs"] if j6 else []))
            if d["action"] in ("SEND", "REVIEW_DRAFT"):                  # one org, one thread (C2 backstop)
                if o["org_id"] in claimed_org:
                    row.update(action="HELD", reason="another thread of this org is already going out this slot (one org, one thread)")
                claimed_org.add(o["org_id"])
            rows.append(row)
    # bounce breaker (C9): DSN bounces in the 7 days before the slot vs Chris's sends in the same window
    since = (slot.date() - datetime.timedelta(days=SND.get("bounce_breaker_window_days", 7))).isoformat()
    b = sum(1 for g in gs["threads"].values() for x in g.get("bounced", []) if x.get("date", "") >= since)
    n = sum(1 for g in gs["threads"].values() for w in g.get("sent_seen", []) if w["to"] >= since)
    rate = 100.0 * b / n if n else 0.0
    if rate > SND.get("bounce_breaker_pct", 3):
        for r in rows:
            if r["action"] in ("SEND", "REVIEW_DRAFT"): r.update(action="HELD", reason="BOUNCE BREAKER: %.1f%% bounces in 7 days — all sending stops until Chris rules" % rate)
    return slot, rows, {"bounces": b, "sends": n, "rate": rate}


GROUP = {"READ": "DECIDED AT 7 AM BY THE THREAD READ", "SEND": "WOULD SEND", "REVIEW_DRAFT": "REVIEW DRAFTS", "CLOSE": "WOULD CLOSE", "DELAYED": "DELAYED",
         "STOPPED": "STOPPED / HELD", "HELD": "STOPPED / HELD", "WAIT": "NOT DUE YET", "NONE": "NOTHING TO DO"}


def why(r):
    w = r["reason"]
    if r.get("dropped"): w += " · bounced Cc dropped: " + ", ".join(r["dropped"])
    if r.get("partial") and r["action"] in ("SEND", "CLOSE", "REVIEW_DRAFT"): w += " · count confirmed by a fresh thread read before sending"
    if r.get("duplicates"): w += " · an earlier email went out twice (copy not counted)"
    for nn in r.get("notes") or []: w += " · " + nn
    return w


def engine_copy_check():
    """Copy is the machine's template verbatim: prove both Email 2 and Email 3 bodies parse from each machine's file."""
    out = {}
    for m, folder in (("OM-1", "OM-1"), ("OM-2", "OM-2")):
        os.environ["FS_MACHINE"] = paths.machine_dir(folder)
        spec = importlib.util.spec_from_file_location("fs_" + m.replace("-", ""), os.path.join(HERE, "followup_send.py"))
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
            out[m] = {n: len(mod.copy_body(n)[0]) for n in (2, 3)}
            out[m]["file"] = os.path.basename(str(mod.COPY))
        except SystemExit as e:
            out[m] = {"error": str(e)}
    return out


def label_plan(orgs):
    c = collections.Counter(); ex = []
    for o in orgs:
        for t in o["threads"]:
            mach = (t["machine"] or "OM-1").split("/")[-1]
            sub = SYM.get(t["status"]) or STAGE_NUM.get(t["stage"], "0")
            tgt = "%s/%s" % (mach, sub)
            c[tgt] += 1
            if len(ex) < 5: ex.append((t["thread_id"], t["labels"], tgt))
    return c, ex


def report(slot_date, prev, out_path, orgs, gs, cal):
    slot, rows, br = plan(slot_date, orgs, gs, cal)
    sim = {}
    for r in rows:
        if r["action"] == "SEND": sim[r["thread"]] = {"sends": [{"date": slot.date().isoformat(), "to": r["to"], "cc": r["cc"]}]}
        if r["action"] == "CLOSE": sim[r["thread"]] = {"closed": True}
    pslot, prow, _ = plan(prev, orgs, gs, cal, sim=sim)
    L = []; A = L.append
    A("# Follow-up sender — DRY RUN for Monday %s, 07:00 ET\n" % slot.date())
    A("Built %s from the rebuilt master list + Gmail (read %s). **Nothing was sent, drafted or labelled.** "
      "Every send below still gets a fresh Gmail read (under 3 minutes old) right before it goes; anything that changed holds.\n"
      % (datetime.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), gs.get("as_of")))
    tot = collections.Counter(GROUP[r["action"]] for r in rows)
    bym = collections.Counter((r["machine"], r.get("email")) for r in rows if r["action"] == "SEND")
    A("## Totals\n")
    A("| Group | Threads |\n|---|---|")
    for gname in ("WOULD SEND", "REVIEW DRAFTS", "WOULD CLOSE", "DECIDED AT 7 AM BY THE THREAD READ", "DELAYED", "STOPPED / HELD", "NEEDS CHRIS"):
        n = tot.get(gname, 0) if gname != "NEEDS CHRIS" else None
        if gname != "NEEDS CHRIS": A("| %s | %d |" % (gname, n))
    A("| Not due yet (later this week or after) | %d |" % tot.get("NOT DUE YET", 0))
    A("\nWould send by machine: " + ", ".join("%s Email %s: %d" % (m, e, n) for (m, e), n in sorted(bym.items())) +
      "  ·  bounce check: %d bounces / %d sends in the last 7 days = %.1f%% (limit 3%%)\n" % (br["bounces"], br["sends"], br["rate"]))
    def table(action, cols=("Org", "Machine", "Email", "Recipients", "Why")):
        rs = sorted([r for r in rows if r["action"] in action], key=lambda r: (r["machine"], r.get("email") or 0, r["org"]))
        if not rs: A("_none_\n"); return
        A("| # | Org | Machine | Email | Recipients | Why |\n|---|---|---|---|---|---|")
        for i, r in enumerate(rs, 1):
            A("| %d | %s | %s | %s | %s | %s |" % (i, r["org"].replace("|", "/")[:60], r["machine"], r.get("email") or "–",
                                                r.get("recipients") if r.get("recipients") is not None else (len(r["to"]) + len(r["cc"]) or "?"), why(r).replace("|", "/")))
        A("")
    A("## WOULD SEND (Monday 7:00 AM ET)\n"); table(("SEND",))
    A("## REVIEW DRAFTS (drafted on the existing thread for Chris — never sent)\n"); table(("REVIEW_DRAFT",))
    rh = [r for r in rows if r["action"] == "NONE" and "review draft already" in r["reason"]]
    if rh: A("Already waiting in Gmail for Chris (nothing new planned): " + "; ".join(r["org"] for r in rh) + "\n")
    A("## WOULD CLOSE (✗ — Email 3 went out 7+ days ago, no reply)\n"); table(("CLOSE",))
    A("## DECIDED AT 7 AM BY THE THREAD READ (the record is missing a date; the fresh read settles it — send, close or wait)\n"); table(("READ",))
    A("## DELAYED\n"); table(("DELAYED",))
    A("## STOPPED / HELD\n"); table(("STOPPED", "HELD"))
    A("## NEEDS CHRIS\n")
    nc = []
    base = {}
    bp = os.path.join(ROOT, "orgs.jsonl.pre-2026-10-31-stage3")
    if os.path.exists(bp):
        for l in open(bp, encoding="utf-8"):
            o = json.loads(l)
            for t in o["threads"]: base[t["thread_id"]] = t["status"]
    newrep = [r for r in rows if r["action"] == "STOPPED" and r.get("human") and not base.get(r["thread"], "").startswith(("replied", "closed"))]
    if newrep:
        nc.append("**Replies the old records missed — Chris's move (mark ★ or ✗):** " + "; ".join(
            "%s (%s, %s)" % (r["org"], r["human"][0]["sender"], r["human"][0].get("date") or "?") for r in newrep))
    succ = [r for r in rows if r.get("successor_note")]
    if succ: nc.append("**Auto-replies naming new contacts (J6 applies once the inbox read records the successors):** " + "; ".join("%s: %s" % (r["org"], " / ".join(r["successor_note"])) for r in succ))
    j6rows = [r for r in rows if r.get("j6") or any("successor" in (n or "") or "J6" in (n or "") for n in (r.get("notes") or []))]
    if j6rows: nc.append("**Successors (J6):** " + "; ".join("%s → %s" % (r["org"], " · ".join(n for n in (r.get("notes") or []) if "successor" in n or "J6" in n or "⚠" in n)) for r in j6rows))
    exc = [r for r in rows if r["action"] == "STOPPED" and r["reason"].startswith("excluded")]
    if exc: nc.append("**Open threads to orgs now excluded (existing client / do-not-contact / prior relationship) — stopped; confirm:** " + "; ".join("%s (%s)" % (r["org"], r["reason"][10:]) for r in exc))
    redir = [x for v in gs["separate_threads_by_domain"].values() for x in v.get("redirect", [])]
    if redir: nc.append("**Auto-replies that name new contacts (J6 decides per thread — see Successors above):** " + "; ".join("%s (%s)" % (x["sender"], x["note"]) for x in redir))
    known = {t["thread_id"] for o in orgs for t in o["threads"]}
    newsent = sorted({tid for tid, g in gs["threads"].items() for w in g.get("sent_seen", []) if w["from"] >= "2026-10-28" and tid not in known and not g.get("human")})
    if newsent: nc.append("**Email 1s Chris sent 10/28–10/31 that are not on the master list yet (%d) — the next build attaches them once read; their Email 2 is not due before 11/4:** %s" % (len(newsent), ", ".join(newsent)))
    r1 = sum(1 for o in orgs for t in o["threads"] if t["status"] == "stopped")
    nc.append("R1-stopped threads (Chris's ruling): %d — nothing planned, ever." % r1)
    for x in EXTRA: nc.append(x)
    for x in nc: A("- " + x)
    A("")
    A("## Tuesday %s preview (assumes Monday's plan ran)\n" % pslot.date())
    pt = collections.Counter(GROUP[r["action"]] for r in prow)
    A(", ".join("%s: %d" % (k, v) for k, v in sorted(pt.items()) if k != "NOTHING TO DO") + "\n")
    rs = sorted([r for r in prow if r["action"] in ("SEND", "CLOSE", "REVIEW_DRAFT", "DELAYED")], key=lambda r: (r["action"], r["machine"], r["org"]))
    if rs:
        A("| Action | Org | Machine | Email | Why |\n|---|---|---|---|---|")
        for r in rs: A("| %s | %s | %s | %s | %s |" % (GROUP[r["action"]], r["org"].replace("|", "/")[:60], r["machine"], r.get("email") or "–", why(r).replace("|", "/")))
    A("\n## Label plan (not applied)\n")
    c, _ = label_plan(orgs)
    A("New trees OM-1 and OM-2 with /0 /1 /2 /3 /★ /✗ /⚠ /⏸. Each thread gets exactly one label, copied from its current state; the old "
      "trees stay untouched (read-only). A stage label moves only after a send is confirmed. Counts: " + ", ".join("%s %d" % kv for kv in sorted(c.items())) + "\n")
    cc = engine_copy_check()
    A("## Copy check\n")
    A("Bodies parsed verbatim from each machine's template (characters): " + "; ".join("%s %s: Email 2 = %s, Email 3 = %s" % (m, v.get("file"), v.get(2), v.get(3)) if "error" not in v else "%s ERROR %s" % (m, v["error"]) for m, v in cc.items()) +
      ". Email 3 attaches %s.\n" % SND.get("starter_kit", {}).get("filename"))
    open(out_path, "w", encoding="utf-8").write("\n".join(L) + "\n")
    json.dump({"slot": slot.isoformat(), "rows": rows, "preview": prow, "bounce": br}, open(out_path.replace(".md", ".json"), "w"), indent=1, ensure_ascii=False, default=str)
    return tot, rows, prow


EXTRA = []


def export(a, orgs, gs, cal):
    """The master plan for one slot, for the engine bridge (FS_MASTER_PLAN). Exit 3 + NEEDS when a successor address
    must be checked first (J6/H3): run each printed check, append the result to 1_Read-the-Inbox/ledgers/successor-validation.jsonl, rerun."""
    now = datetime.datetime.now(ET)
    sd = datetime.date.fromisoformat(a.slot) if a.slot else cal.next_slot(now - datetime.timedelta(hours=8)).date()
    slot, rows, br = plan(sd, orgs, gs, cal)
    needs = sorted({e for r in rows for e in (r.get("needs") or [])})
    d = os.path.join(SEND_RUNS, sd.isoformat()); os.makedirs(d, exist_ok=True)
    keep = [dict(thread=r["thread"], org=r["org"], org_id=r["org_id"], machine=r["machine"], action=r["action"], email=r.get("email"),
                 to=r["to"], cc=r["cc"], j6=r.get("j6"), reason=r["reason"]) for r in rows if r["action"] in ("SEND", "READ", "REVIEW_DRAFT")]
    other = [dict(thread=r["thread"], org=r["org"], machine=r["machine"], action=r["action"], email=r.get("email"), reason=r["reason"])
             for r in rows if r["action"] not in ("SEND", "READ", "REVIEW_DRAFT")]
    doc = {"slot": slot.isoformat(), "generated": now.isoformat(), "bounce": br, "rows": keep, "not_sent": other, "needs": needs}
    out = os.path.join(d, "master-plan.json")
    with open(out, "w", encoding="utf-8") as f: json.dump(doc, f, ensure_ascii=False, indent=1)
    by = collections.Counter((r["machine"], r["action"]) for r in keep)
    print("MASTER PLAN %s · slot %s · %s · not sent %d · bounce %.1f%%" % (out, slot.isoformat(), dict(by), len(other), br["rate"]))
    if br.get("not_business_day"):
        print("NOT A BUSINESS DAY: nothing is sent this slot (sends are delayed to the next business day). Read + report only.")
    if needs:
        print("NEEDS %d successor address check(s) (Rulebook J6/H3). For each: apollo_email_validation_validate(email) (ZeroBounce via Apollo), then append "
              "one line to 1_Read-the-Inbox/ledgers/successor-validation.jsonl: {\"email\": ..., \"result\": \"valid|catch-all|unknown|invalid\", \"source\": \"apollo/zerobounce\", \"date\": ...}; then rerun export." % len(needs))
        for e in needs: print("  CHECK " + e)
        sys.exit(3)


OM_SUBS = {"E1": "1", "E2": "2", "E3": "3", "E1-draft": "0"}
OM_STATUS = {"replied★": "★", "closed✗": "✗", "stopped": "✗", "attention⚠": "⚠", "hold⏸": "⏸"}


def _om_alias(name):
    """Old trees were migrated 1:1 onto OM-1/OM-2 and deleted on 2026-11-03; ledgers written before that still name them (2026-11-03)."""
    for old, new in (("CCR&R outreach", "OM-1"), ("Con Outreach", "OM-2")):
        if name == old or name.startswith(old + "/"): name = new + name[len(old):]
    return name.replace("/X", "/✗")

def label_orders(a, orgs):
    """Rulebook L: one tree per machine (OM-1, OM-2), sub-labels 0 1 2 3 ★ ✗ ⚠ ⏸, exactly one per thread.
    Needs --labels <list_labels JSON saved verbatim>. Prints create_label orders for missing labels (then save list_labels
    again and rerun), else the label_thread / unlabel_thread orders. Idempotent: a thread already carrying its target gets
    nothing; other OM sub-labels on it are removed. Old trees are left in place (the engine's gather still reads them)."""
    if not a.labels: sys.exit("label-orders needs --labels <saved list_labels JSON>")
    j = json.load(open(a.labels, encoding="utf-8"))
    labs = {x["name"]: (x.get("id") or x.get("labelId")) for x in (j.get("labels") or j)}  # Gmail list_labels returns labelId (Stage 8 fix)
    want = [m for m in ("OM-1", "OM-2")] + ["%s/%s" % (m, x) for m in ("OM-1", "OM-2") for x in ("0", "1", "2", "3", "★", "✗", "⚠", "⏸")]
    missing = [w for w in want if w not in labs]
    if missing:
        print("CREATE %d label(s) with create_label (parents first), save list_labels again, rerun:" % len(missing))
        for w in missing: print("  create_label name=" + w)
        sys.exit(3)
    gs = json.load(open(paths.GMAIL_STATE, encoding="utf-8"))["threads"]
    closes = set()
    if a.slot:
        mp = os.path.join(SEND_RUNS, a.slot, "master-plan.json")
        if os.path.exists(mp):
            closes = {r["thread"] for r in json.load(open(mp, encoding="utf-8"))["not_sent"] if r["action"] == "CLOSE"}
    adds, rems = collections.defaultdict(list), collections.defaultdict(list)
    for o in orgs:
        for t in o["threads"]:
            m = (t["machine"] or "").split("/")[-1]
            if m not in ("OM-1", "OM-2"): m = o["owner_machine"] if o["owner_machine"] in ("OM-1", "OM-2") else None
            if not m: continue
            sub = "✗" if t["thread_id"] in closes else (OM_STATUS.get(t["status"]) or OM_SUBS.get(t["stage"]))
            if not sub: continue
            target = "%s/%s" % (m, sub)
            have = {_om_alias(x) for x in ((gs.get(t["thread_id"]) or {}).get("labels") or t.get("labels") or [])}
            if target not in have:
                adds[labs[target]].append(t["thread_id"])
                if m not in have: adds[labs[m]].append(t["thread_id"])
            for other in [x for x in have if x.startswith(m + "/") and x != target and x in labs]:
                rems[labs[other]].append(t["thread_id"])
    n = 0
    for lid, ts in sorted(adds.items()):
        for tid in sorted(set(ts)): print("  label_thread threadId=%s labelIds=[%s]" % (tid, lid)); n += 1
    for lid, ts in sorted(rems.items()):
        for tid in sorted(set(ts)): print("  unlabel_thread threadId=%s labelIds=[%s]" % (tid, lid)); n += 1
    print("LABEL ORDERS: %d change(s). Apply in the order printed; each is idempotent." % n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="plan")
    ap.add_argument("--slot", default=None)
    ap.add_argument("--preview", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--note", action="append", default=[])
    ap.add_argument("--labels", default=None)
    a = ap.parse_args()
    if a.live:
        sys.exit("FAIL CLOSED: send.py never sends. Live sends go through the 7 AM send task (_shared/orchestrator/run.py send): send.py export -> "
                 "followup_send.py --machine <m> with FS_MASTER_PLAN, whose --intent checks the live gate.")
    cal = seqrules.Calendar(S)
    orgs, gs = load()
    if a.cmd == "labels":
        c, ex = label_plan(orgs)
        for k, v in sorted(c.items()): print(k, v)
        return
    if a.cmd == "export":
        return export(a, orgs, gs, cal)
    if a.cmd == "label-orders":
        return label_orders(a, orgs)
    now = datetime.datetime.now(ET)
    sd = datetime.date.fromisoformat(a.slot) if a.slot else cal.next_slot(now).date()
    pv = datetime.date.fromisoformat(a.preview) if a.preview else cal.roll(sd + datetime.timedelta(days=1))
    out = a.out or os.path.join(SEND_RUNS, "dry-run-%s.md" % sd.isoformat())
    EXTRA.extend(a.note)
    tot, rows, prow = report(sd, pv, out, orgs, gs, cal)
    print(out); print(dict(tot))


if __name__ == "__main__":
    main()
