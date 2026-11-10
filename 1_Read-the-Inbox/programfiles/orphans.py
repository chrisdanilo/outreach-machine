#!/usr/bin/env python3
"""orphans.py — the nightly DRAFTS AUDIT (Chris 2026-11-06, CAPA 2026-11-06 #10). Audits, then resolves; Chris does no work.

An ORPHAN is an unsent Email 1 draft (threadId == messageId, subject "Question about …") that carries no machine label —
e.g. the 26 OM-2 drafts of 10/30 that the 11/03 migration dropped from the records. Labels can only be set when Zapier
creates a draft (the Gmail connector refuses to label an existing draft), so the fix is always: delete and rewrite.

For each orphan, matched to its org (drafts-ledger thread first, else a unique recipient-domain match; no match = reported only,
never touched — personal drafts are safe):
  1. the org passes its owning machine's gates now            → REWRITE on that machine (draft.py --redo: new labelled draft,
                                                                Gate 7, then the old draft goes to Trash)
  2. OM-2 org with no dated keynote event and an OM-1 market   → HAND OFF to OM-1 (Rulebook E7, overrides.json handoff, email1 true),
                                                                then as 1/3 under OM-1 (Chris 2026-11-06: "not fit for OM-2 → redraft for OM-1")
  3. anything else (not open yet, not fit, no ready recipients) → DELETE the old draft; the org stays in its machine's queue and
                                                                gets a fresh draft the normal way when it passes the gates
A rewrite that draft.py holds (e.g. prior contact found) also ends in DELETE. Every delete is recorded in the drafts ledger
(status DELETED, supersedes = the old draft id) so the master list drops the dead thread.

  python3 orphans.py next --slot D --night N [--threads t1,t2]   the state machine: prints the ONE next step; rerun after each
  (--threads: also audit these labelled-but-unrecorded Email 1 threads from the drafts ledger — one-time backfill use)
Working folder: 1_Read-the-Inbox/runs/<D>/orphans/ ; raw reads in 1_Read-the-Inbox/runs/gmail/<D>/orphan_drafts_p<n>.json
"""
import argparse, collections, datetime, json, os, re, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_shared", "orchestrator")); import paths
sys.path.insert(0, paths.programs("draft")); import draft as DR

BY = "orphan audit — Chris standing rule 2026-11-06"
QUERY = 'has:nouserlabels subject:"Question about"'


def rj(p, d=None): return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else d
def jl(p): return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()] if os.path.exists(p) else []
def wj(p, o):
    os.makedirs(os.path.dirname(p), exist_ok=True); json.dump(o, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
def dom(e): return (e or "").split("@")[-1].lower().strip()


def wdir(slot): return os.path.join(paths.runs("read"), slot, "orphans")
def gdir(slot): return os.path.join(paths.GMAIL_RAW, slot)


def pages(slot):
    out, n = [], 1
    while True:
        p = os.path.join(gdir(slot), "orphan_drafts_p%d.json" % n)
        if not os.path.exists(p): return out, n
        j = rj(p) or {}
        out.append(j); n += 1
        if not j.get("nextPageToken"): return out, None


def gather(slot, extra):
    """[(draft_id, message_id, thread_id, to[], cc[], source)] — orphans from the reads + the --threads backfill set."""
    pg, more = pages(slot)
    if more: return None, more, (pg[-1].get("nextPageToken") if pg else None)
    rows, seen = [], set()
    for j in pg:
        for x in j.get("drafts") or []:
            labs = set(x.get("labelIds") or [])
            if any(l.startswith("Label_") for l in labs): continue          # has a user label: not an orphan
            if x.get("threadId") != x.get("messageId"): continue             # a reply on an existing thread: never touched here
            rows.append({"draft_id": x["id"], "message_id": x["messageId"], "thread_id": x["threadId"], "to": x.get("toRecipients") or [],
                         "cc": x.get("ccRecipients") or [], "source": "unlabelled draft"}); seen.add(x["threadId"])
    if extra:
        led = {r.get("thread_id"): r for r in jl(paths.DRAFTS) if r.get("status") == "DRAFTED"}
        for t in extra:
            r = led.get(t)
            if not r or t in seen: continue
            rows.append({"draft_id": r["draft_id"], "message_id": t, "thread_id": t, "to": [r["to"]] if isinstance(r.get("to"), str) else (r.get("to") or []),
                         "cc": r.get("cc") or [], "source": "backfilled ledger row (--threads)"})
    return rows, None, None


def match(rows, orgs):
    led = {r.get("thread_id"): r for r in jl(paths.DRAFTS) if r.get("status") == "DRAFTED"}
    by_id = {o["org_id"]: o for o in orgs}
    by_dom = collections.defaultdict(set)
    for o in orgs:
        for d in o.get("domains") or []: by_dom[d.lower()].add(o["org_id"])
    for r in rows:
        oid = (led.get(r["thread_id"]) or {}).get("org_id")
        if oid not in by_id:
            for t in [o for o in orgs if any((x if isinstance(x, str) else x.get("thread_id")) == r["thread_id"] for x in o.get("threads") or [])]: oid = t["org_id"]
        if oid not in by_id:
            c = set().union(*[by_dom.get(dom(e), set()) for e in r["to"] + r["cc"]]) if (r["to"] or r["cc"]) else set()
            oid = next(iter(c)) if len(c) == 1 else None
        r["org_id"] = oid if oid in by_id else None
    return rows


def classify(rows, orgs):
    idx = DR.indexes(orgs); by_id = {o["org_id"]: o for o in orgs}
    for r in rows:
        o = by_id.get(r["org_id"])
        if not o: r.update(action="REPORT", reason="no org matched — never touched (personal or unknown draft)"); continue
        m = o.get("owner_machine"); w = DR.why_not(o, idx, redo=True)
        r.update(org_name=o.get("name"), machine=m)
        if w is None: r.update(action="REWRITE", reason="passes %s gates now" % m); continue
        if m == "OM-2" and w.startswith("outreach not open (no dated keynote event") and "MKT-001" in (o.get("markets") or []):
            r.update(action="HANDOFF", reason="OM-2: %s; org is also an OM-1 market → OM-1 (Rulebook E7)" % w); continue
        r.update(action="DELETE", reason="%s: %s — stays queued; fresh draft when it passes the gates" % (m, w))
    return rows


def write_handoffs(rows):
    ov = rj(paths.OVERRIDES); have = {e["org_id"] for e in ov.get("handoff", [])}; n = 0
    for r in rows:
        if r["action"] != "HANDOFF" or r["org_id"] in have: continue
        ov.setdefault("handoff", []).append({"by": BY, "org_id": r["org_id"], "from_machine": "OM-2", "to_machine": "OM-1",
                                             "prior_threads": [r["thread_id"]], "reason": r["reason"], "email1": True}); n += 1
    if n:
        bak = os.path.join(paths.ARCHIVE, "overrides.json.bak-%s" % now()[:10])
        if not os.path.exists(bak): json.dump(rj(paths.OVERRIDES), open(bak, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        json.dump(ov, open(paths.OVERRIDES, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    return n


def cmd_next(a):
    W = wdir(a.slot); S = rj(os.path.join(W, "state.json"), {}); save = lambda: wj(os.path.join(W, "state.json"), S)
    extra = [t for t in (a.threads or "").split(",") if t]
    if "rows" not in S:
        rows, more, tok = gather(a.slot, extra)
        if rows is None:
            print("AUDIT READ: list_drafts(query=%s, pageSize 50, view DRAFT_VIEW_METADATA_ONLY%s) -> save VERBATIM as %s ; then rerun next."
                  % (json.dumps(QUERY), (", pageToken=%s" % tok) if tok else "", os.path.join(gdir(a.slot), "orphan_drafts_p%d.json" % more))); return 0
        orgs = DR.load_orgs(); rows = classify(match(rows, orgs), orgs)
        S["rows"] = rows; save()
        if write_handoffs(rows):
            S["handoffs"] = True; save()
            print("AUDIT HANDOFFS written to overrides.json (%d org(s) OM-2 → OM-1). Rebuild: python3 \"%s\" ; then rerun next." % (sum(r["action"] == "HANDOFF" for r in rows), paths.BUILD_MASTER)); return 0
    rows = S["rows"]
    if not rows:
        print("AUDIT DONE: no orphan drafts."); return 0
    if S.get("handoffs") and not S.get("reclassified"):
        orgs = DR.load_orgs(); idx = DR.indexes(orgs); by_id = {o["org_id"]: o for o in orgs}
        for r in rows:
            if r["action"] != "HANDOFF": continue
            o = by_id[r["org_id"]]; w = DR.why_not(o, idx, redo=True)
            if o.get("owner_machine") != "OM-1": r.update(action="DELETE", reason="handoff did not apply (owner %s) — %s" % (o.get("owner_machine"), r["reason"]))
            elif w is None: r.update(action="REWRITE", machine="OM-1", reason="handed off OM-2 → OM-1; passes OM-1 gates now")
            else: r.update(action="DELETE", machine="OM-1", reason="handed off OM-2 → OM-1; OM-1: %s — queued for OM-1, fresh draft when ready" % w)
        S["reclassified"] = True; save()
    run = "%s-audit" % a.night
    redo = [{"org_id": r["org_id"], "old_draft_id": r["draft_id"], "old_message_id": r["message_id"]} for r in rows if r["action"] == "REWRITE"]
    if redo and not S.get("redo_done"):
        rp = os.path.join(W, "redo.json"); wj(rp, redo)
        summ = rj(os.path.join(DR.rdir(run), "summary.json"))
        if not summ:
            print("AUDIT REWRITE %d draft(s): follow python3 5_Draft/programfiles/draft.py next --run %s --redo \"%s\" exactly, step by step, until DRAFT DONE "
                  "(lock: lock.py acquire draft … release draft); do the trash_message lines it prints; then rerun this next." % (len(redo), run, rp)); return 0
        done = {r.get("supersedes") for r in jl(paths.DRAFTS) if r.get("run") == run and r.get("status") == "DRAFTED"}
        for r in rows:
            if r["action"] == "REWRITE":
                if r["draft_id"] in done: r["action"] = "REWRITTEN"
                else: r.update(action="DELETE", reason="rewrite held by the drafter (see %s/held.json) — old draft removed" % DR.rdir(run))
        S["redo_done"] = True; save()
    dels = [r for r in rows if r["action"] == "DELETE"]
    if dels and not S.get("deleted"):
        print("AUDIT DELETE %d old draft(s): call delete_draft for each, then run: python3 1_Read-the-Inbox/programfiles/orphans.py deleted --slot %s --night %s" % (len(dels), a.slot, a.night))
        for r in dels: print("  delete_draft(draftId=%s)   # %s · %s" % (r["draft_id"], r.get("org_name"), r["reason"]))
        return 0
    c = collections.Counter(r["action"] for r in rows)
    wj(os.path.join(W, "summary.json"), {"slot": a.slot, "counts": dict(c), "rows": rows})
    print("AUDIT DONE: %s · details %s" % (json.dumps(dict(c)), os.path.join(W, "summary.json")))
    for r in rows: print("  %-10s %-45s %s" % (r["action"], (r.get("org_name") or r["thread_id"])[:45], r["reason"]))
    return 0


def cmd_deleted(a):
    W = wdir(a.slot); S = rj(os.path.join(W, "state.json"), {})
    rows = [r for r in S.get("rows", []) if r["action"] == "DELETE"]
    with open(paths.DRAFTS, "a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps({"created_at": now(), "draft_id": None, "machine": r.get("machine"), "org_id": r["org_id"], "org_name": r.get("org_name"),
                                "reason": "orphan audit: old draft deleted — " + r["reason"], "run": "%s-audit" % a.night, "status": "DELETED",
                                "supersedes": r["draft_id"], "thread_id": None}, ensure_ascii=False, sort_keys=True) + "\n")
    S["deleted"] = True; wj(os.path.join(W, "state.json"), S)
    print("RECORDED %d deletion(s) in the drafts ledger. Rebuild: python3 \"%s\" ; then rerun next." % (len(rows), paths.BUILD_MASTER)); return 0


def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    x = sp.add_parser("next"); x.add_argument("--slot", required=True); x.add_argument("--night", required=True); x.add_argument("--threads"); x.set_defaults(f=cmd_next)
    x = sp.add_parser("deleted"); x.add_argument("--slot", required=True); x.add_argument("--night", required=True); x.set_defaults(f=cmd_deleted)
    a = ap.parse_args(); sys.exit(a.f(a))


if __name__ == "__main__":
    main()
