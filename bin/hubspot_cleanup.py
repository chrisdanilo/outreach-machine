#!/usr/bin/env python3
"""
hubspot_cleanup.py -- decides which HubSpot contacts get tagged for Chris to delete.

Installed 2026-09-22 on Chris's instruction. Goal: stay under the HubSpot plan's 1,000-contact limit.
NOT a do-not-contact list -- re-contact is allowed; the extension re-creates a contact on the next send.

THE MACHINE NEVER DELETES. It sets ONE contact property, `outreach_cleanup`, and Chris bulk-deletes
from a saved HubSpot view. The vault keeps the permanent record in hubspot-cleanup.jsonl.

WHO GETS TAGGED (deterministic -- no reply text is read here):
  delete_no_reply      every recipient who PERSONALLY received all 3 emails (to or cc on each), whose own
                       Email 3 went out >= hubspot_cleanup.grace_days ago (14, Chris 2026-09-30; was
                       sequence_gap_days=7), on a thread where no human ever replied. Per-person count
                       added 2026-10-07 (Chris): someone on email 1 only, or added mid-sequence, is NOT
                       cleanable yet
  delete_declined      every recipient on the thread of an org classified declined / deferred
                       in funnel-outcomes.json (Chris's confirmed classifications).
                       FORWARDED orgs are KEPT (Chris 2026-09-30: the forwarder may still be useful)
  delete_bounced_left  one person: config.hard_bounces, or config.cleanup_departed (left the org)

NEVER TAGGED:
  - anyone on a thread labelled replied (star) or on a thread named in an ACTIVE warm.jsonl row
  - any email address written inside an ACTIVE warm.jsonl row (e.g. a named successor)
  - anyone who also sits on ANY thread that is not cleanable (an address is tagged only if every
    thread it appears on is finished)
  - orgs classified live or meeting
  - HubSpot: any deal, lead status set, or lifecycle stage other than lead/subscriber/blank
HELD (reported, not tagged -- D-DOUBT):
  - thread carries the attention label, or has a non-Chris message that is not a bounce and not an
    auto-reply, and the org has no confirmed outcome
  - thread preview may be truncated (>= preview_limit messages) and was not read in full
  - warm.jsonl row with no status (its thread and named addresses are protected meanwhile)
SCOPE: only threads carrying the parent label `CCR&R outreach` (Label_2) or owned by a contacted.jsonl
  org row. Every other thread in Chris's sent mail is ignored -- never tagged.

USAGE
  python3 bin/hubspot_cleanup.py candidates <run_dir> [--today YYYY-MM-DD]
      reads  <run_dir>/threads.json      (Gmail snapshot written by the run -- format in method §0.15)
      writes <run_dir>/candidates.json   (emails to look up in HubSpot, with reason + evidence; holds)
  python3 bin/hubspot_cleanup.py decide <run_dir>
      reads  <run_dir>/candidates.json + <run_dir>/hubspot.json  (HubSpot facts per email)
      writes <run_dir>/tags.json         (the exact HubSpot writes: id -> value)
      appends hubspot-cleanup.jsonl       (one line per NEW tag -- idempotent, never duplicates)
      prints the report line
"""
import json, re, sys, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOG = ROOT / "hubspot-cleanup.jsonl"
ME = "<SENDER_EMAIL>"
LABEL = {"replied": "Label_12", "attention": "Label_14"}
AUTO = re.compile(r"^(automatic reply|auto(matic)?[- ]?reply|autoreply|auto:|out of (the )?office|"
                  r"thank you for your (email|correspondence|message)|i am (currently )?out)", re.I)
HUBSPOT_VALUE = "remove"  # the single value written to HubSpot (Chris 2026-10-07); reasons stay in the log
OUTCOME_TAG = {"declined": "delete_declined", "deferred": "delete_declined"}
OUTCOME_KEEP = {"live", "meeting", "forwarded"}  # forwarded kept -- Chris 2026-09-30
WARM_INACTIVE = {"closed", "deferred", "deferred-named-re-entry"}
OK_STAGES = {"", "lead", "subscriber", None}
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
HEX = re.compile(r"\b[0-9a-f]{16}\b")


def jl(p):
    return [json.loads(l) for l in pathlib.Path(p).read_text().splitlines() if l.strip()]


def norm(s):
    return (s or "").replace("*", "").strip().lower()


def load_context():
    cfg = json.loads((ROOT / "config.json").read_text())
    ledger = jl(ROOT / "contacted.jsonl")
    outcomes = json.loads((ROOT / "funnel-outcomes.json").read_text()).get("replies", {})
    warm = jl(ROOT / "warm.jsonl")
    # org name -> thread ids, from the ledger's org rows
    org_threads = {}
    for r in ledger:
        if r.get("type") == "org" and r.get("org"):
            org_threads.setdefault(norm(r["org"]), set()).update(HEX.findall(str(r.get("thread"))))
    thread_outcome = {}
    for org, a in outcomes.items():
        for t in org_threads.get(org.lower(), ()):
            thread_outcome[t] = (a["outcome"], org)
    active_threads, protected, warm_holds = set(), set(), []
    for w in warm:
        st = (w.get("status") or "").strip()
        blob = json.dumps(w)
        if not st or (st.lower() not in WARM_INACTIVE and not HEX.findall(str(w.get("thread")))):
            warm_holds.append(f'{w.get("org")} [{st or "no status"}{"" if HEX.findall(str(w.get("thread"))) else ", no thread id"}]')
        if not st:
            active_threads.update(HEX.findall(str(w.get("thread"))))
            protected.update(e.lower() for e in EMAIL.findall(blob))
        elif st.lower() not in WARM_INACTIVE:
            active_threads.update(HEX.findall(str(w.get("thread"))))
            protected.update(e.lower() for e in EMAIL.findall(blob))
    ledger_threads = set()
    for r in ledger:
        if r.get("type") == "org":
            ledger_threads.update(HEX.findall(str(r.get("thread"))))
    return cfg, thread_outcome, active_threads, protected, warm_holds, ledger_threads


def cmd_candidates(run_dir, today):
    cfg, thread_outcome, active_threads, protected, warm_holds, ledger_threads = load_context()
    snap = json.loads((run_dir / "threads.json").read_text())
    limit = snap.get("preview_limit", 5)
    gap = cfg.get("hubspot_cleanup", {}).get("grace_days", 14)  # Chris 2026-09-30: 14-day grace after Email 3
    need = cfg.get("sequence_length", 3)
    thread_verdict, holds, out_of_scope = {}, [], 0
    addr_threads, addr_sends = {}, {}
    for t in snap["threads"]:
        tid = t["thread"]
        # SCOPE: only CCR&R outreach threads -- parent label OR a thread id the ledger owns.
        # Anything else in Chris's sent mail (clients, vendors, forms) is never touched.
        if "Label_2" not in t["labels"] and tid not in ledger_threads:
            out_of_scope += 1
            continue
        rcpts = sorted({a for s in t["sends"] for a in s["to"] + s["cc"]} - {ME})
        for a in rcpts:
            addr_threads.setdefault(a, set()).add(tid)
        # PER-PERSON send dates: which of the emails THIS address was actually on (to or cc).
        # Chris 2026-10-07: a person is only cleanable once *they* have received all three emails
        # and the grace period has passed -- being on a thread whose Email 3 went out is not enough.
        addr_sends[tid] = {a: sorted({s["date"][:10] for s in t["sends"] if a in s["to"] + s["cc"]}) for a in rcpts}
        dates = sorted({s["date"][:10] for s in t["sends"]})
        outcome, org = thread_outcome.get(tid, (None, None))
        humans = [o for o in t["others"]
                  if "mailer-daemon" not in o["sender"] and "postmaster" not in o["sender"]
                  and not AUTO.match(o.get("subject") or "")]
        v = None
        if LABEL["replied"] in t["labels"] or tid in active_threads or outcome in OUTCOME_KEEP:
            v = ("keep", "replied, live or warm")
        elif LABEL["attention"] in t["labels"]:
            v = ("hold", "attention label set")
        elif outcome in OUTCOME_TAG:
            v = ("tag", OUTCOME_TAG[outcome], f"funnel-outcomes: {outcome} ({org})")
        elif t.get("preview_count", 0) >= limit and not t.get("complete"):
            v = ("hold", "preview may be truncated -- read the thread in full")
        elif humans:
            v = ("hold", "unclassified reply from " + ", ".join(sorted({h['sender'] for h in humans})))
        elif len(dates) >= need:
            e3 = datetime.date.fromisoformat(dates[need - 1])
            exit_day = e3 + datetime.timedelta(days=gap)
            if today >= exit_day:
                v = ("tag", "delete_no_reply", f"Email 3 sent {e3}, no reply by {exit_day}")
            else:
                v = ("wait", f"reply window open until {exit_day}")
        else:
            v = ("wait", f"sequence in progress ({len(dates)} of {need} sent)")
        thread_verdict[tid] = (v, rcpts, t.get("subject", ""))
        if v[0] == "hold":
            holds.append({"thread": tid, "subject": t.get("subject", ""), "why": v[1]})
    cands = {}
    for tid, (v, rcpts, subj) in thread_verdict.items():
        if v[0] != "tag":
            continue
        for a in rcpts:
            if a in protected:
                continue
            others = [thread_verdict[x][0][0] for x in addr_threads[a] if x != tid and x in thread_verdict]
            if any(o != "tag" for o in others):
                continue
            evidence = v[2]
            if v[1] == "delete_no_reply":
                # Chris 2026-10-07: count the emails THIS person received, not the thread's.
                mine = addr_sends[tid].get(a, [])
                if len(mine) < need:
                    continue  # they personally got fewer than 3 emails -- not cleanable yet
                my_e3 = datetime.date.fromisoformat(mine[need - 1])
                my_exit = my_e3 + datetime.timedelta(days=gap)
                if today < my_exit:
                    continue  # their own grace window is still open
                evidence = f"Email 3 to this address sent {my_e3}, no reply by {my_exit}"
            cands.setdefault(a, {"email": a, "value": v[1], "evidence": evidence, "thread": tid})
    # person-level: bounced or departed, regardless of the thread's state
    person = {k.lower(): "hard bounce" for k in cfg.get("hard_bounces", {})}
    person.update({k.lower(): "left the organisation" for k in cfg.get("cleanup_departed", {})})
    for a, why in person.items():
        if a in protected or a in cands:
            continue
        cands[a] = {"email": a, "value": "delete_bounced_left", "evidence": why,
                    "thread": sorted(addr_threads.get(a, [""]))[0]}
    counts = {}
    for c in cands.values():
        counts[c["value"]] = counts.get(c["value"], 0) + 1
    out = {"generated": today.isoformat(), "candidates": sorted(cands.values(), key=lambda c: c["email"]),
           "holds": holds, "warm_rows_without_status": warm_holds, "counts": counts,
           "threads_seen": len(thread_verdict), "threads_out_of_scope": out_of_scope}
    (run_dir / "candidates.json").write_text(json.dumps(out, indent=1))
    print(f"candidates: {len(cands)} {counts} · holds: {len(holds)} · outreach threads: {len(thread_verdict)}"
          f" · ignored (not outreach): {out_of_scope} · warm rows needing a thread id/status: {len(warm_holds)}")


def cmd_decide(run_dir):
    c = json.loads((run_dir / "candidates.json").read_text())
    hs = {k.lower(): v for k, v in json.loads((run_dir / "hubspot.json").read_text()).items()}
    logged = {(r["email"], r["value"]) for r in jl(LOG)} if LOG.exists() else set()
    tags, skipped, new_lines = [], {"not in HubSpot": 0, "already tagged": 0, "relationship": []}, []
    for cand in c["candidates"]:
        h = hs.get(cand["email"])
        if not h:
            skipped["not in HubSpot"] += 1
            continue
        if h.get("outreach_cleanup"):
            skipped["already tagged"] += 1
            continue
        if (h.get("num_associated_deals") or 0) not in (0, "0") or h.get("hs_lead_status") \
                or (h.get("lifecyclestage") or "") not in OK_STAGES:
            skipped["relationship"].append(cand["email"])
            continue
        # Chris 2026-10-07: HubSpot only needs to know the contact is marked for removal. The reason
        # (no_reply / declined / bounced_left) lives in hubspot-cleanup.jsonl, not in HubSpot.
        tags.append({"id": int(h["id"]), "email": cand["email"], "value": HUBSPOT_VALUE, "reason": cand["value"]})
        if (cand["email"], cand["value"]) not in logged:
            new_lines.append({"date": c["generated"], "email": cand["email"], "hubspot_id": int(h["id"]),
                              "value": cand["value"], "evidence": cand["evidence"], "thread": cand["thread"],
                              "hs_created": h.get("createdate"), "hs_source": h.get("hs_object_source_label")})
    (run_dir / "tags.json").write_text(json.dumps({"tags": tags, "skipped": skipped}, indent=1))
    with LOG.open("a") as f:
        for l in new_lines:
            f.write(json.dumps(l) + "\n")
    by = {}
    for t in tags:
        by[t["reason"]] = by.get(t["reason"], 0) + 1
    print(f"HubSpot cleanup: {len(tags)} to tag {by} · {len(c['holds'])} held · "
          f"{skipped['not in HubSpot']} not in HubSpot · {skipped['already tagged']} already tagged · "
          f"{len(skipped['relationship'])} kept (relationship) · {len(new_lines)} new log lines")


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("candidates", "decide"):
        print(__doc__); sys.exit(3)
    rd = pathlib.Path(sys.argv[2])
    if not rd.is_absolute():
        rd = ROOT / rd
    if sys.argv[1] == "candidates":
        today = datetime.date.today()
        if "--today" in sys.argv:
            today = datetime.date.fromisoformat(sys.argv[sys.argv.index("--today") + 1])
        cmd_candidates(rd, today)
    else:
        cmd_decide(rd)
