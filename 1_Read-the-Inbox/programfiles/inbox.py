#!/usr/bin/env python3
"""inbox.py — the INBOX READER (Rulebook B, G8, H5, J, K). Gmail is the record of what happened.

Writes 1_Read-the-Inbox/ledgers/gmail-state.json, which _shared/master/build_master.py reads (Gmail wins; a stage never moves backward).

  python3 inbox.py bootstrap         turn the 2026-10-31 Gmail extraction (_shared/master/seeds/gmail-2026-10-31/threads/) into gmail-state.json
  python3 inbox.py queries           print the Gmail searches a fresh read must run (each window must return < 50 threads)
  python3 inbox.py ingest F.json...  merge verbatim get_thread results (METADATA view) into gmail-state.json — Gmail wins

What it derives per thread: Chris's sends (date / to / cc), human replies, auto-replies (return date when readable),
bounces (which address), open drafts, labels, machine. Separate-thread replies (most auto-replies and some human
replies arrive as their own thread) are kept by sender address/domain so the sender can match them to an org.
Reads only. Never sends, drafts or labels anything.
"""
import datetime, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_shared", "orchestrator")); import paths  # the one file that knows every folder (2026-11-03)
import seqrules

MASTER = paths.MASTER
S = paths.settings()
ROOT = paths.MASTER
STATE = paths.GMAIL_STATE                                   # 1_Read-the-Inbox/ledgers/gmail-state.json
XDIR = paths.inp("gmail_threads_2026_10_31")                # the 2026-10-31 extraction (a seed, never pruned)
ME = "chris@chrisdanilo.com"
FREEMAIL = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com", "icloud.com", "comcast.net", "att.net", "msn.com", "live.com", "me.com"}

# Gmail label ids (list_labels 2026-10-31). Old trees are READ-ONLY; OM-1/OM-2 are the new trees (Rulebook H5).
LABELS = {"Label_2": "CCR&R outreach", "Label_8": "CCR&R outreach/0", "Label_9": "CCR&R outreach/1", "Label_10": "CCR&R outreach/2",
          "Label_11": "CCR&R outreach/3", "Label_12": "CCR&R outreach/★", "Label_13": "CCR&R outreach/X", "Label_14": "CCR&R outreach/⚠",
          "Label_15": "CCR&R outreach/⏸", "Label_17": "Con Outreach", "Label_18": "Con Outreach/0", "Label_19": "Con Outreach/1",
          "Label_20": "Con Outreach/2", "Label_21": "Con Outreach/3", "Label_22": "Con Outreach/★", "Label_23": "Con Outreach/X",
          "Label_24": "Con Outreach/⚠", "Label_25": "Con Outreach/⏸",
          # OM trees (Rulebook L). 2026-11-03: old trees migrated onto these and retired (Chris); without these names the
          # builder saw OM labels as raw ids and read no stage from them (CAPA-2026-11-03-label-trees).
          "Label_27": "OM-1", "Label_28": "OM-1/0", "Label_29": "OM-1/1", "Label_30": "OM-1/2", "Label_31": "OM-1/3",
          "Label_32": "OM-1/★", "Label_33": "OM-1/✗", "Label_34": "OM-1/⚠", "Label_35": "OM-1/⏸",
          "Label_36": "OM-2", "Label_37": "OM-2/0", "Label_38": "OM-2/1", "Label_39": "OM-2/2", "Label_40": "OM-2/3",
          "Label_41": "OM-2/★", "Label_42": "OM-2/✗", "Label_43": "OM-2/⚠", "Label_44": "OM-2/⏸"}


def id_time(hexid):
    """Gmail ids encode the time: ms = int(id,16) >> 20 (verified 2026-10-31 against internalDate)."""
    return datetime.datetime.fromtimestamp((int(hexid, 16) >> 20) / 1000, datetime.timezone.utc)


def dom(addr):
    d = addr.lower().rsplit("@", 1)[-1].strip()
    for p in ("mail.", "email."):
        if d.startswith(p): d = d[len(p):]
    return d


def machine_of(labels):
    if any(l.startswith("Con Outreach") or l.startswith("OM-2") for l in labels): return "OM-2"
    if any(l.startswith("CCR&R outreach") or l.startswith("OM-1") for l in labels): return "OM-1"
    return None


def rows(fn):
    for line in open(os.path.join(XDIR, fn), encoding="utf-8"):
        if line.startswith("#") or not line.strip(): continue
        yield line.rstrip("\n").split("\t")


def blank():
    return {"read": None, "sends": [], "labels": [], "human": [], "auto": [], "bounced": [], "dsn": False, "drafts": [],
            "sent_seen": [], "non_chris_seen": False, "notes": []}


def bootstrap():
    T = {}
    th = lambda t: T.setdefault(t, blank())
    # 1. threads read in full (get_thread METADATA_ONLY)
    for r in rows("threads-compact.tsv"):
        r += [""] * (8 - len(r))
        tid, cnt, sends, to, cc, others, labs, note = r[:8]
        t = th(tid); t["read"] = "full"; t["message_count_incl_drafts"] = int(cnt or 0)
        to_l = [x for x in to.split(",") if x]; cc_l = [x for x in cc.split(",") if x]
        t["sends"] = [{"date": d, "to": to_l, "cc": cc_l} for d in sends.split(";") if d]
        t["labels"] = sorted({LABELS.get(l, l) for l in labs.split(",") if l})
        for o in [x for x in others.split(";") if x]:
            mid, dt, snd = o.split("@", 2)
            t["non_chris_seen"] = True
            t.setdefault("_others", []).append({"id": mid, "date": dt, "sender": snd})
        if note: t["notes"].append(note)
        m = re.search(r"(\d+) draft", note)
        if m: t["drafts_count_hint"] = int(m.group(1))
    # 2. sent windows (complete, each < 50 threads): a Chris send happened inside [from, to]
    for line in open(os.path.join(XDIR, "sent-windows.txt"), encoding="utf-8"):
        if line.startswith("#") or "|" not in line: continue
        dr, q, ids = line.rstrip("\n").split("|", 2)
        a = dr.split("..")[0]; b = a[:8] + dr.split("..")[1] if ".." in dr else a
        for tid in ids.split():
            th(tid)["sent_seen"].append({"from": a, "to": b, "query": q})
    # 3. every thread with a non-Chris message, Aug 1–Oct 31 (complete windows)
    windows = []
    for line in open(os.path.join(XDIR, "nonchris-threads.txt"), encoding="utf-8"):
        if line.startswith("# W"): windows.append(line[2:].strip()); continue
        if line.startswith("#"): continue
        for tid in line.split(): th(tid)["non_chris_seen"] = True
    # 4. classified non-Chris messages
    sep = {"human": [], "auto": [], "redirect": []}
    for tid, snd, cls, *note in rows("inbound-classified.tsv"):
        note = note[0] if note else ""
        rec = {"sender": snd.lower(), "thread": tid, "date": id_time(tid).date().isoformat(), "note": note}
        t = th(tid)
        if cls == "HUMAN": t["human"].append(rec); sep["human"].append(rec)
        elif cls == "BOUNCE": t["dsn"] = True
        elif cls == "REDIRECT": t["auto"].append(dict(rec, redirect=True)); sep["redirect"].append(rec)
        elif cls == "AUTO": t["auto"].append(rec); sep["auto"].append(rec)
    # 5. auto-replies (mostly separate threads → matched later by sender address)
    for snd, tid, ret, *note in rows("autoreplies.tsv"):
        rec = {"sender": snd.lower(), "thread": tid, "date": id_time(tid).date().isoformat(), "return": ret or None, "note": note[0] if note else ""}
        th(tid)["auto"].append(rec); sep["auto"].append(rec)
    # 6. bounces (DSN read; which address)
    for tid, addr, mid, *note in rows("bounces.tsv"):
        t = th(tid); t["dsn"] = True; t["bounced"].append({"address": addr.lower(), "dsn_id": mid, "date": id_time(mid).date().isoformat(), "note": note[0] if note else ""})
    # 7. open drafts
    for tid, mid, kind in rows("drafts.tsv"):
        if kind.startswith("personal"): continue
        th(tid)["drafts"].append({"draft_message_id": mid, "kind": kind, "date": id_time(mid).date().isoformat()})
    for t in T.values():
        others = t.pop("_others", [])
        for o in others:
            s = o["sender"].lower()
            if "mailer-daemon" in s or "postmaster" in s: t["dsn"] = True
            elif not any(h["sender"] == s for h in t["human"]) and not any(a["sender"] == s for a in t["auto"]):
                t["human"].append({"sender": s, "thread": None, "date": o["date"][:10], "note": "in-thread non-Chris message (unclassified → treated as a person)"})
        t["machine"] = machine_of(t["labels"])
        t["read"] = t["read"] or ("windows" if (t["sent_seen"] or t["non_chris_seen"]) else "drafts")
    by_dom = {}
    for k, lst in sep.items():
        for rec in lst:
            d = dom(rec["sender"])
            if d in FREEMAIL: d = rec["sender"]
            by_dom.setdefault(d, {"human": [], "auto": [], "redirect": []})[k].append(rec)
    state = {
        "_README": "Written by 1_Read-the-Inbox/programfiles/inbox.py from Gmail (read-only). build_master.py merges it; Gmail wins; a stage never moves backward. "
                   "read=full: get_thread read every message. read=windows: only search windows saw it — the sender re-reads the thread (<=180 s) before any action.",
        "as_of": S["as_of"], "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "completeness": {
            "rule": "Gmail search returns at most 50 threads and has no paging; a window is complete only if it returned fewer than 50.",
            "inbound_windows": windows,
            "sent_windows": [l.split("|")[0] + " " + l.split("|")[1] + " (%d)" % len(l.split("|")[2].split())
                             for l in open(os.path.join(XDIR, "sent-windows.txt"), encoding="utf-8") if "|" in l and not l.startswith("#")],
            "label_windows": "_shared/master/seeds/gmail-2026-10-31/pull/README.txt (label trees by date window; partial windows marked)",
        },
        "threads": dict(sorted(T.items())),
        "separate_threads_by_domain": dict(sorted(by_dom.items())),
    }
    write(state)
    full = sum(1 for t in T.values() if t["read"] == "full")
    print("gmail-state: %d threads (%d read in full), %d sender domains with separate-thread replies; human=%d auto=%d dsn=%d drafts=%d"
          % (len(T), full, len(by_dom), sum(1 for t in T.values() if t["human"]), sum(1 for t in T.values() if t["auto"]),
             sum(1 for t in T.values() if t["dsn"]), sum(len(t["drafts"]) for t in T.values())))


def write(state):
    tmp = STATE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f: json.dump(state, f, ensure_ascii=False, indent=1, sort_keys=False)
    os.replace(tmp, STATE)


def queries():
    print("""Fresh Gmail read (run each; split any window that returns 50 until all are < 50):
 1. labels: (label:"CCR&R outreach" OR label:"Con Outreach" OR label:"OM-1" OR label:"OM-2") after:A before:B   METADATA view
 2. sent:   in:sent subject:("PD/Training" OR "your conference") after:A before:B
 3. inbound: subject:("PD/Training" OR "your conference") -from:%s after:A before:B
 4. auto-replies (separate threads): subject:("automatic reply" OR "out of office" OR "out of the office") after:A
 5. bounces: from:(mailer-daemon OR postmaster) after:A   (ignore DMARC reports)
 6. drafts: list_drafts (one page holds 50)
 Then get_thread (METADATA) for every thread the sender would act on, within 180 s of acting, and `inbox.py ingest` the JSON.""" % ME)


def ingest(paths):
    state = json.load(open(STATE, encoding="utf-8"))
    for p in paths:
        j = json.load(open(p, encoding="utf-8"))
        j = j.get("thread", j)
        tid = j.get("id") or j.get("threadId")
        t = state["threads"].setdefault(tid, blank())
        sends, human = [], []
        labs = set()
        for m in j.get("messages", []):
            snd = (m.get("sender") or m.get("from") or "").lower()
            snd = re.sub(r".*<([^>]+)>.*", r"\1", snd)
            subj = m.get("subject") or ""
            date = m.get("date") or id_time(m["id"]).isoformat()
            to = m.get("to") or m.get("toRecipients") or []; cc = m.get("cc") or m.get("ccRecipients") or []
            to = to if isinstance(to, list) else [x.strip() for x in to.split(",") if x.strip()]
            cc = cc if isinstance(cc, list) else [x.strip() for x in cc.split(",") if x.strip()]
            labs |= {LABELS.get(l, l) for l in m.get("labelIds", m.get("labels", []))}
            c = seqrules.msg_class(snd, subj, ME)
            if c == "own": sends.append({"date": date, "to": to, "cc": cc, "message_id": m.get("id")})
            elif c == "dsn": t["dsn"] = True
            elif c == "auto": t["auto"].append({"sender": snd, "thread": tid, "date": date[:10], "return": None, "note": subj[:120]})
            else: human.append({"sender": snd, "thread": tid, "date": date[:10], "note": subj[:120]})
        if sends and all(set(x["to"]) <= {"claude@chrisdanilo.com"} for x in sends):
            t.update(read="full", sends=[], sent_seen=[], labels=sorted(labs), machine=None, not_outreach="template test to claude@chrisdanilo.com")
            print("ingested", tid, "template test thread — not outreach"); continue
        t.update(read="full", sends=sends, labels=sorted(labs), machine=machine_of(labs))
        t["message_count_incl_drafts"] = j.get("messageCount", len(j.get("messages", [])))
        if j.get("messageCount", 0) > len(j.get("messages", [])):
            t["drafts"] = t["drafts"] or [{"draft_message_id": None, "kind": "draft on thread (count)", "date": None}]
        for h in human:
            if h not in t["human"]: t["human"].append(h)
        if not sends:                                  # a SEPARATE reply thread (no send by Chris in it): index it by sender so
            by_dom = state.setdefault("separate_threads_by_domain", {})   # build_master.py can match it to the org (2026-11-03)
            for kind, lst in (("human", human), ("auto", [a for a in t["auto"] if a.get("thread") == tid])):
                for rec in lst:
                    d = dom(rec["sender"])
                    if d in FREEMAIL: d = rec["sender"]
                    slot_ = by_dom.setdefault(d, {"human": [], "auto": [], "redirect": []}).setdefault(kind, [])
                    if not any(x.get("thread") == rec["thread"] and x["sender"] == rec["sender"] for x in slot_): slot_.append(rec)
        print("ingested", tid, "sends=%d human=%d" % (len(sends), len(t["human"])))
    write(state)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "bootstrap"
    {"bootstrap": bootstrap, "queries": queries}.get(cmd, lambda: ingest(sys.argv[2:]))()
