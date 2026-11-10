#!/usr/bin/env python3
"""report.py -- the ONE morning report for every machine (Rulebook M5; Stage 7, Chris 2026-10-30).

Plain English, one screen first, details below. Built only from files the runs wrote (nothing is decided here):
an executive summary (drafts vs minimums, approved sends, waiting drafts, health), then the night run's ONE prioritized
issues list with a CAPA for each (reports/<date>-capa.md, written by the orchestrator from --issues seeds), then links.
Details (drafts table, holds, sends/closes, H7 sweep, open questions) go to reports/<date>-details.md, never the chat.
Chris 2026-11-03: no reply list and no step-status block in the report.

  python3 report.py [--date YYYY-MM-DD] [--sample]   (default date = today, America/New_York)
Writes outreach-engine/reports/<date>.md (or <date>-sample.md) and prints the same text.
"""
import argparse, collections, datetime, glob, json, os, re, urllib.parse
from zoneinfo import ZoneInfo

import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_shared", "orchestrator")); import paths  # the one file that knows every folder (2026-11-03)
def _mt(t): return datetime.datetime.fromisoformat(t).astimezone(ZoneInfo("America/Denver")).strftime("%H:%M") if t else "—"   # 2026-11-08
ENG = paths.ROOT
MASTER = paths.MASTER
S = paths.settings()
ROOT = paths.MASTER
MKT = paths.MARKETING
MACH_DIR = {m: paths.machine_dir(m) for m in paths.machines()}
MIN = paths.mset("minimum")
GM = "https://mail.google.com/mail/u/0/#all/%s"


def jl(p): return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()] if os.path.exists(p) else []
def rj(p, d=None): return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else d


def link(p):
    p = os.path.abspath(p)
    m = re.search(r"/mnt/ClaudeVault/(.*)$", p)
    mac = "/Users/<you>/ClaudeVault/" + m.group(1) if m else p
    return "computer://" + urllib.parse.quote(mac)


def build(date, sample=False):
    used = []
    def use(p):
        if os.path.exists(p) and p not in used: used.append(p)
        return p
    orgs = [json.loads(l) for l in open(use(paths.ORGS), encoding="utf-8")]
    byid = {o["org_id"]: o for o in orgs}
    # sends + closes (morning sender)
    mp = rj(use(os.path.join(paths.runs("send"), date, "master-plan.json")), {})
    sent, unver, dup, fails = [], [], [], []
    for m, md in MACH_DIR.items():
        for f in sorted(glob.glob(os.path.join(paths.runs("send"), m, date + "*", "sender", "*", "followup_sends.json"))):
            use(f); j = rj(f, {})
            for r in j.get("rows", []):
                if r.get("action") == "send" and r.get("status") == "sent": sent.append((m, r))
                elif r.get("status") == "UNVERIFIED": unver.append((m, r))
                elif r.get("status") == "DUPLICATE": dup.append((m, r))
            for x in j.get("findings") or []:
                if "FAIL" in str(x) or "DUPLICATE" in str(x): fails.append("%s: %s" % (m, x))
    closes = [r for r in mp.get("not_sent", []) if r.get("action") == "CLOSE"]
    # drafts made last night (latest draft run on or before the date) + every Email 1 draft still waiting
    di = [r for r in jl(use(paths.DRAFTS)) if (r.get("run") or "") <= date]
    # the untimed night loop (2026-10-31) drafts in passes: runs <night>-p1, -p2 … all belong to the same night.
    # A second fire of the same evening is <date>-2-pN; pick the latest FIRE, not the lexically largest run
    # (CAPA-2026-11-03-report: "2026-11-02-p2" sorted above "2026-11-02-2-p4" and the report showed fire 1's drafts).
    night_of = lambda r: re.sub(r"-p\d+$", "", r or "")
    def _fire_key(r):
        m = re.match(r"^(\d{4}-\d\d-\d\d)(?:-(\d+))?", night_of(r) or "")
        return (m.group(1), int(m.group(2) or 1)) if m else ("", 0)
    last_run = max((r["run"] for r in di), key=_fire_key, default=None)
    tonight_runs = sorted({r["run"] for r in di if last_run and night_of(r["run"]) == night_of(last_run)})
    tonight = sorted([r for r in di if r["run"] in tonight_runs and r["status"] == "DRAFTED"], key=lambda r: (r["run"], -r.get("create_order", 0)), reverse=False)
    held_tonight = [r for r in di if r["run"] in tonight_runs and r["status"] in ("HELD", "SPARE")]
    summ = {"made": {}, "shortfall": {}}
    for rr in tonight_runs:
        sm = rj(use(os.path.join(paths.runs("draft"), rr, "summary.json")), {}) or {}
        for m, v in (sm.get("made") or {}).items(): summ["made"][m] = summ["made"].get(m, 0) + v
    for m_, mn in MIN.items():                         # shortfall vs the NIGHT's total (all passes)
        if tonight_runs and summ["made"].get(m_, 0) < mn:
            summ["shortfall"][m_] = "%d of %d minimum tonight — see the night timing above for why the loop stopped" % (summ["made"].get(m_, 0), mn)
    waiting = [(o, t) for o in orgs for t in o["threads"] if t["stage"] == "E1-draft" and t["status"] == "open"]
    # replies needing Chris
    rep = []
    for o in orgs:
        for t in o["threads"]:
            if t["status"] in ("replied★", "attention⚠"):
                h = ((t.get("gmail") or {}).get("human") or [{}])[-1]
                rep.append((h.get("date") or t.get("last_sent_at") or "", o, t, h))
    rep.sort(key=lambda x: x[0], reverse=True)
    # holds
    ph = collections.Counter(); ph_ex = collections.defaultdict(list)
    for o in orgs:
        if o.get("people_hold") and o.get("owner_machine") in MACH_DIR:
            r = (o["people_hold"].get("reason") or "?").split(":")[0]
            ph[r] += 1
            if len(ph_ex[r]) < 3: ph_ex[r].append((o.get("name") or o.get("org_id") or "?", o["people_hold"].get("unblock")))
    # rulings
    rul = []
    for f in [paths.RULINGS]:   # ONE rulings log (2026-11-03)
        for r in jl(use(f)):
            if r.get("status") == "open": rul.append(r)
    # defaults in use that wait for Chris's confirmation (settings pending_rulings; Stage 8)
    # listed FIRST so they always show (Stage 8)
    rul = [{"id": r["id"], "question": r["question"]} for r in S.get("pending_rulings", [])] + rul
    # apollo credits
    cred = 0; cred_runs = []
    for f in sorted(glob.glob(os.path.join(paths.runs("people"), "*", "credits.jsonl"))):
        for r in jl(f):
            if r.get("date") and r["date"] >= (datetime.date.fromisoformat(date) - datetime.timedelta(days=1)).isoformat():
                cred += r.get("credits_spent", 0); cred_runs.append(f)
    for f in cred_runs: use(f)
    night_st = None
    for f in sorted(glob.glob(os.path.join(paths.NIGHT_RUNS, "*", "state.json"))):
        st_ = rj(f, {}) or {}
        if st_.get("slot") == date and (night_st is None or (st_.get("started") or "") > (night_st[1].get("started") or "")): night_st = (f, st_)
    cr = [p.get("credits_remaining") for p in (((night_st or (None, {}))[1].get("loop") or {}).get("passes") or []) if p.get("credits_remaining") is not None]
    cred_line = ("%d remaining · %d used between tonight's first and last checks" % (cr[-1], cr[0] - cr[-1])) if cr else ("%d recorded by helpers" % cred)
    # issue seeds for the CAPA section: every step the night run checkpointed partial/failed, with its note
    seeds = []
    if night_st:
        st_ = night_st[1]
        for k_, v_ in (st_.get("steps") or {}).items():
            if (v_ or {}).get("status") in ("partial", "failed"): seeds.append("%s %s — %s" % (k_, v_["status"], v_.get("note")))
        for p in ((st_.get("loop") or {}).get("passes") or []):
            for k_, v_ in (p.get("steps") or {}).items():
                if (v_ or {}).get("status") in ("partial", "failed", "skipped"): seeds.append("pass %s %s %s — %s" % (p["n"], k_, v_["status"], v_.get("note")))
    # FAIL CLOSED anywhere in tonight's / this morning's run folders
    for f in glob.glob(os.path.join(paths.runs("send"), date, "**", "*"), recursive=True) + glob.glob(os.path.join(paths.runs("read"), date, "**", "*"), recursive=True) + [f for rr in (tonight_runs or ["-"]) for f in glob.glob(os.path.join(paths.runs("draft"), rr, "**", "*"), recursive=True)]:
        if "fail" in os.path.basename(f).lower(): fails.append("file %s" % os.path.basename(f))
    br = (mp.get("bounce") or {})

    L = []; A = L.append            # the executive summary (Chris 2026-11-03: one screen, issues + CAPA, no reply list, no step status)
    Dt = []; B = Dt.append          # details — written to <date>-details.md, linked, never pasted into the report
    A("# Outreach — %s%s" % (date, " (SAMPLE)" if sample else ""))
    A("")
    sld = os.path.join(paths.SEND_LISTS, "rehearsal") if sample else paths.SEND_LISTS
    sl = rj(use(os.path.join(sld, "%s.json" % date)), None)
    made = {m: sum(1 for r in tonight if r["machine"] == m) for m in ("OM-1", "OM-2")}
    A("## Executive summary")
    A("| | OM-1 (PD/training) | OM-2 (conferences) |"); A("|---|---|---|")
    A("| Email 1 drafts made tonight | %d of %d minimum | %d of %d minimum |" % (made["OM-1"], MIN["OM-1"], made["OM-2"], MIN["OM-2"]))
    if sl:
        A("| Approved for the 7 AM send | %d | %d |" % (sum(1 for x in sl["rows"] if x["machine"] == "OM-1"), sum(1 for x in sl["rows"] if x["machine"] == "OM-2")))
    A("")
    A("- **Waiting for you in Gmail:** %d Email 1 drafts (add the GIF, then send) · **not approved for sending:** %s · **open questions:** %d" % (
        len(waiting), len(sl.get("not_approved", [])) if sl else "no list", len(rul)))
    A("- **Health:** bounce rate (7 days) %s · Apollo credits %s · FAIL CLOSED %s" % (
        ("%.1f%%" % br["rate"]) if br.get("rate") is not None else "n/a", cred_line, ("; ".join(fails[:3]) if fails else "none")))
    for m, line in (summ.get("shortfall") or {}).items(): A("- ⚠ %s short: %s" % (m, line.split(" — ")[0]))
    # Chris 2026-11-06 (option 8): OM-2 supply next to its minimum, and searches used per pass — so a target that cannot be met shows the same night
    sup = collections.Counter()
    for o_ in (json.loads(l_) for l_ in open(paths.ORGS, encoding="utf-8") if l_.strip()):
        if o_.get("owner_machine") != "OM-2": continue
        st2 = ((o_.get("outreach") or {}).get("status") or "")
        if not st2:   # 2026-11-08: say WHY the org has no outreach window instead of calling everything "undated" (138 of 153 were really "keynote path unknown")
            evs_ = o_.get("events") or []
            dated_ = any(e.get("edition_date") or e.get("next_edition_date") or e.get("last_edition_date") for e in evs_)
            st2 = "no event on record" if not evs_ else ("no event date" if not dated_ else "window not computed")   # 2026-11-09: the outside-speaker gate is gone
        if st2 == "open_now":
            st2 = "ready, already emailed" if o_.get("threads") else ("ready, contacts held" if not (o_.get("recipients") or {}).get("to") else "ready to draft")
        sup[st2.split(" 20")[0].replace("_until", " until later")] += 1
    A("- **OM-2 supply (minimum %d/night):** %s" % (MIN["OM-2"], " · ".join("%s %d" % kv for kv in sorted(sup.items(), key=lambda x: -x[1]))))
    # Chris 2026-11-08: the shelf the Supply Run (~1 AM) left and what the night found at its start — so a shortfall reads as a supply problem or a drafting problem
    sh_ = (night_st[1].get("shelf_at_start") if night_st else None) or {}
    if sh_.get("machines"):
        A("- **Shelf at the start of the night** (left by the supply run %s): %s · places still due for discovery %d" % (sh_.get("supply_run") or "none yet",
          " · ".join("%s ready to draft %d, people to find %d, to qualify %d" % (m, sh_["machines"][m]["draft_eligible"], sh_["machines"][m]["people_pool"], sh_["machines"][m]["qualify_pool"]) for m in ("OM-1", "OM-2")), sh_.get("due_sources", 0)))
    sl_ = rj(os.path.join(paths.SUPPLY, "shelf-latest.json"), None)
    if sl_ and sl_.get("run"):
        srun_ = rj(os.path.join(paths.SUPPLY_RUNS, sl_["run"], "state.json"), {}) or {}
        sk_ = [k_ for k_, v_ in (srun_.get("steps") or {}).items() if (v_ or {}).get("status") in ("skipped", "failed")]
        A("- **Supply run %s:** %s%s" % (sl_["run"], "finished %s MT" % _mt(srun_["finished"]) if srun_.get("finished") else (srun_.get("status") or "unknown"), (" · skipped/failed: " + ", ".join(sk_)) if sk_ else " · every step ran"))
    if night_st:
        srch = []
        for p_ in sorted(((night_st[1].get("loop") or {}).get("passes") or []), key=lambda x: x["n"]):
            dst = rj(os.path.join(paths.runs("discover"), "%s-p%d" % (night_st[1]["run"], p_["n"]), "state.json"), None)
            if dst: srch.append("pass %d %d of %d (%s)" % (p_["n"], dst.get("searches_used", 0), dst.get("searches_cap", 0), "+".join(dst.get("machines") or p_.get("machines") or [])))
        if srch: A("- **Discovery searches logged:** %s · platform limit 200 per session, shared by every helper" % " · ".join(srch))
    A("")
    cp = os.path.join(paths.REPORTS, "%s-capa.md" % date)
    A("## Issues and CAPA (most severe first)")
    if os.path.exists(cp):
        use(cp); A(open(cp, encoding="utf-8").read().strip())
    elif seeds or fails or summ.get("shortfall"):
        A("🔴 The night run has not written its issues/CAPA file (%s). Unresolved seeds:" % os.path.basename(cp))
        for x in seeds + fails: A("- " + x)
    else:
        A("No issues.")
    A("")
    if a_seeds_only[0]:
        return None, "\n".join("- " + x for x in seeds + fails + ["shortfall %s: %s" % kv for kv in (summ.get("shortfall") or {}).items()]) + "\n"
    # ---- details file
    B("# Outreach details — %s" % date); B("")
    B("## Email 1 drafts made tonight (Gmail order, newest on top)")
    if tonight:
        B("| Org | Machine | To + Cc | Greeting | Subject | Thread |"); B("|---|---|---|---|---|---|")
        for r in tonight:
            B("| %s | %s | %d | %s | %s | %s |" % (r["org_name"], r["machine"], 1 + len(r.get("cc") or []), r.get("greeting"), r.get("subject"),
                                              ("[open](%s)" % (GM % r["thread_id"])) if r.get("thread_id") else "—"))
            for f in r.get("flags") or []: B("|  | ↳ %s |  |  |  |  |" % f)
            if r.get("short_how", "").endswith("check before sending"): B("|  | ↳ subject short name trimmed by rule — check it |  |  |  |  |")
    else:
        B("No new Email 1 drafts from the last run.")
    older = [(o, t) for o, t in waiting if t["thread_id"] not in {r.get("thread_id") for r in tonight}]
    if older: B("\nOlder Email 1 drafts still unsent: %d — e.g. %s" % (len(older), ", ".join("[%s](%s)" % (o.get("name") or o["org_id"], GM % t["thread_id"]) for o, t in older[:5])))
    if held_tonight:
        B("\nHeld at draft time: " + "; ".join(sorted({"%s — %s" % (r["org_name"], r["reason"]) for r in held_tonight})[:10]))
    B("")
    B("## Sent (7 AM send task) and closed")
    if sent:
        for m, r in sent: B("- %s · %s · Email %s · sent" % (r.get("org"), m, r.get("email_no")))
    else: B("- No sends recorded for %s." % date)
    for r in closes[:20]: B("- ✗ closed: %s (%s)" % (r.get("org"), r.get("machine")))
    if len(closes) > 20: B("- … and %d more closed" % (len(closes) - 20))
    for m, r in unver + dup: B("- 🔴 %s · %s · %s" % (r.get("org"), m, r.get("status")))
    B("")
    B("## Held — and what would unblock them")
    for r, n in ph.most_common(6):
        B("- **%d** — %s. Unblock: %s. e.g. %s" % (n, r, ph_ex[r][0][1], ", ".join(x[0] for x in ph_ex[r])))
    B("")
    ros = [o for o in orgs if o.get("roster_line") and o.get("owner_machine") in MACH_DIR and ((o.get("recipients") or {}).get("decided") or (o.get("people_hold") or {}).get("decided")) in (date, (datetime.date.fromisoformat(date) - datetime.timedelta(days=1)).isoformat())]
    if ros:
        B("## People found but not published — the Apollo roster sweep (H7)")
        tot = {"unpublished": 0, "submitted": 0, "resolved": 0, "held": 0, "queried-null": 0, "deferred": 0}
        for o in ros:
            parts = dict((k.strip(), int(v)) for v, k in re.findall(r"(\d+) ([a-z-]+)", o["roster_line"]))
            for k in tot: tot[k] += parts.get(k, 0)
        B("- **%d** named people without a published address · **%d** looked up in Apollo · **%d** resolved · **%d** held · **%d** not found · **%d** deferred" % (tot["unpublished"], tot["submitted"], tot["resolved"], tot["held"], tot["queried-null"], tot["deferred"]))
        B("")
    B("## Open questions for you")
    for r in rul[:25]: B("- %s — %s" % (r.get("id"), r.get("question")))
    if not rul: B("- none")
    tp = os.path.join(paths.REPORTS, "%s-timing%s.md" % (date, "-rehearsal" if sample else ""))
    if os.path.exists(tp): use(tp)
    out = os.path.join(paths.REPORTS, "%s%s.md" % (date, "-sample" if sample else ""))
    dout = os.path.join(paths.REPORTS, "%s%s-details.md" % (date, "-sample" if sample else ""))
    B(""); B("## Files")
    for p in used: B("- [%s](%s)" % (os.path.relpath(p, MKT), link(p)))
    A("## Links")
    dos = os.path.join(paths.DOSSIERS, "dossier-%s.md" % date)  # Chris 2026-11-06: always link the day's sending dossier
    A("- [Dossier (read before sending)](%s) · [Details: drafts, holds, sends, open questions](%s) · [Send list](%s) · [Night timing](%s)" % (
        link(dos), link(dout), link(os.path.join(sld, "%s.md" % date)), link(tp)))
    os.makedirs(os.path.dirname(dout), exist_ok=True)
    open(dout, "w", encoding="utf-8").write("\n".join(Dt) + "\n")
    return out, "\n".join(L) + "\n"


a_seeds_only = [False]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--date"); ap.add_argument("--sample", action="store_true"); ap.add_argument("--night", help="(informational) the night run id")
    ap.add_argument("--issues", action="store_true", help="print the issue seeds (partial/failed steps, FAIL CLOSED, shortfalls) for the CAPA file; writes nothing")
    a = ap.parse_args()
    date = a.date or datetime.datetime.now(ZoneInfo("America/New_York")).date().isoformat()
    if a.issues:
        a_seeds_only[0] = True; print(build(date, a.sample)[1]); return
    out, txt = build(date, a.sample)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
