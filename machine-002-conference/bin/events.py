#!/usr/bin/env python3
"""
Machine 002 — event database tool (deterministic; no web access, no judgment).

The event database is events.jsonl in this machine's folder: one event per line.
Research (finding events, reading pages) is done by Claude; this script only
merges what research found, computes waves, checks the file, and writes reports.

Commands
  python3 bin/events.py merge <incoming.jsonl> [<incoming2.jsonl> ...] --run <YYYY-MM-DD>
      Fold research results into events.jsonl. New events are added; existing
      events are updated by the rules in merge_into(). Every changed field is
      appended to events-changes.jsonl (the history). A copy of events.jsonl
      as it was before the merge is saved to runs/<run>/events.pre-merge.jsonl.
  python3 bin/events.py waves [--today YYYY-MM-DD]
      Recompute the computed fields (wave, outreach_opens, machine_001_status,
      colorado, dnc) for every event and rewrite events.jsonl.
  python3 bin/events.py validate
      Check every row. Prints FAIL lines and exits 1 if any row is invalid.
  python3 bin/events.py report --run <YYYY-MM-DD>
      Write runs/<run>/refresh-report.md and events-calendar.generated.md
      (a read-only view of the database for review — never edit it by hand).
  python3 bin/events.py worklist [--segment <name>]
  python3 bin/events.py dupes
      List pairs of events that may be duplicates, for a person to judge.
  python3 bin/events.py retire <event_id> --why "<reason>" [--run YYYY-MM-DD]
      Take an event out of the database (e.g. a duplicate, or not a real event).
      Nothing is deleted: the row moves to events-retired.jsonl with the reason,
      and the move is logged in events-changes.jsonl.
      Print the events the next refresh must re-check (all of them, soonest
      event first) as JSONL, for the research step.
"""
import json, re, sys, os, shutil, datetime
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent.parent
DB = HERE / "events.jsonl"
CHANGES = HERE / "events-changes.jsonl"
CONFIG = json.load(open(HERE / "config.json"))

ORG_TYPES = set(CONFIG["org_types"])
DATE_STATUS = {"confirmed", "estimated", "unknown"}
CFP_STATUS = {"open", "upcoming", "closed", "not_found"}
CFP_TYPES = {"presenters", "keynote", "rfp", "sponsors_exhibitors", None}
YESNO = {"yes", "no", "unknown"}
PROCUREMENT = {"direct", "rfp", "unknown"}
COMPUTED = ("event_id", "wave", "event_month", "outreach_opens", "notice_months",
            "machine_001_status", "colorado", "dnc", "first_seen", "last_checked",
            "vertical", "evidence_grade", "excluded_machine_001")
VERTICAL_OF = CONFIG.get("vertical_of_org_type", {})


def evidence_grade(r):
    """A = named outside keynote or RFP on record · B = annual event dated (confirmed/estimated) · C = org/event only."""
    if r.get("keynote_slot") == "yes" or r.get("procurement") == "rfp":
        return "A"
    if (r.get("date_2027") or {}).get("status") in ("confirmed", "estimated"):
        return "B"
    return "C"


# ---------- helpers ----------
def load_jsonl(p):
    rows = []
    if not Path(p).exists():
        return rows
    for i, line in enumerate(open(p, encoding="utf-8"), 1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as e:
            sys.exit(f"FAIL {p} line {i}: not valid JSON ({e})")
    return rows


def write_jsonl(p, rows):
    tmp = Path(str(p) + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(tmp, p)


def norm_url(u):
    if not u:
        return ""
    u = u.strip()
    if "://" not in u:
        u = "https://" + u
    p = urlparse(u)
    host = p.netloc.lower().removeprefix("www.")
    path = p.path.rstrip("/").lower()
    return host + path


def host(u):
    return norm_url(u).split("/")[0]


def norm_text(s):
    s = (s or "").lower()
    s = re.sub(r"\b(20\d\d|annual|the|conference|conf|and|&)\b", " ", s)
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def slug(*parts):
    s = "-".join(p for p in parts if p)
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:80]


def make_id(r):
    return slug(r.get("organization") or "", re.sub(r"\b20\d\d\b", "", r.get("event_name") or ""))


def month_of(r):
    d = r.get("date_2027") or {}
    m = d.get("month")
    if not m and d.get("start"):
        m = d["start"][:7]
    return m if m and re.fullmatch(r"\d{4}-\d{2}", m) else None


def add_months(ym, n):
    y, m = map(int, ym.split("-"))
    m += n
    while m <= 0:
        m += 12; y -= 1
    while m > 12:
        m -= 12; y += 1
    return f"{y:04d}-{m:02d}"


def months_between(a, b):
    ya, ma = map(int, a.split("-")); yb, mb = map(int, b.split("-"))
    return (yb - ya) * 12 + (mb - ma)


# ---------- matching ----------
def find_match(row, db):
    """Same event = same event page, or same organization + same event name."""
    u = norm_url(row.get("event_url"))
    on, en = norm_text(row.get("organization")), norm_text(row.get("event_name"))
    for i, r in enumerate(db):
        if u and u == norm_url(r.get("event_url")) and norm_text(r.get("event_name")) == en:
            return i
    for i, r in enumerate(db):
        if on and en and norm_text(r.get("organization")) == on and norm_text(r.get("event_name")) == en:
            return i
    # No looser matching on purpose (2026-10-22): one organization's page often lists
    # several different events, and a "name contains name" rule merged the Head Start
    # California Annual Conference into its Managers & Directors Institute. The refresh
    # keeps event_name and organization exactly as stored, so exact matching is enough;
    # near-duplicates are found by `python3 bin/events.py dupes` and retired by a person.
    return None


DATE_RANK = {"confirmed": 3, "estimated": 2, "unknown": 1, None: 0}


def merge_into(old, new, run, log):
    """Rules: a confirmed date beats an estimate beats unknown; a newer confirmed
    date replaces an older one; call-for-proposals status always takes the
    newest reading; any empty field is filled; sources are combined."""
    eid = old["event_id"]

    def change(field, before, after, why):
        log.append({"run": run, "event_id": eid, "field": field,
                    "before": before, "after": after, "why": why})

    od, nd = old.get("date_2027") or {}, new.get("date_2027") or {}
    ors, nrs = od.get("status"), nd.get("status")
    if DATE_RANK.get(nrs, 0) > DATE_RANK.get(ors, 0):
        change("date_2027", od, nd, f"{ors or 'none'} -> {nrs}")
        old["date_2027"] = nd
    elif nrs == ors == "confirmed" and (nd.get("start"), nd.get("month")) != (od.get("start"), od.get("month")):
        change("date_2027", od, nd, "confirmed date changed on organizer page")
        old["date_2027"] = nd
    elif nrs == ors == "estimated" and nd.get("month") and nd.get("month") != od.get("month"):
        change("date_2027", od, nd, "estimate revised from a newer past edition")
        old["date_2027"] = nd

    oc, nc = old.get("call_for_proposals") or {}, new.get("call_for_proposals") or {}
    if nc and (nc.get("status"), nc.get("deadline"), nc.get("type")) != (oc.get("status"), oc.get("deadline"), oc.get("type")):
        if nc.get("status") and nc.get("status") != "not_found" or not oc:
            change("call_for_proposals", oc, nc, "newest reading")
            old["call_for_proposals"] = nc

    oo, no = old.get("owner") or {}, new.get("owner") or {}
    if no.get("name") and no.get("source_url") and no.get("name") != oo.get("name"):
        change("owner", oo, no, "new or different person found (with source)")
        old["owner"] = no
    elif no and oo and no.get("name") == oo.get("name"):
        for k in ("title", "email", "source_url"):
            if no.get(k) and not oo.get(k):
                change(f"owner.{k}", None, no[k], "gap filled")
                oo[k] = no[k]

    for k in ("event_url", "org_url", "city", "state", "country", "audience", "attendance",
              "last_held", "keynote_evidence_url", "last_keynote", "org_type"):
        if not old.get(k) and new.get(k):
            change(k, None, new[k], "gap filled")
            old[k] = new[k]
    for k, rank in (("keynote_slot", {"yes": 2, "no": 2, "unknown": 1}),
                    ("procurement", {"direct": 2, "rfp": 2, "unknown": 1})):
        if rank.get(new.get(k), 0) > rank.get(old.get(k), 0):
            change(k, old.get(k), new[k], "gap filled")
            old[k] = new[k]
    lh_o, lh_n = old.get("last_held") or {}, new.get("last_held") or {}
    if lh_n.get("start") and lh_o.get("start") and lh_n["start"] > lh_o["start"]:
        change("last_held", lh_o, lh_n, "newer past edition found")
        old["last_held"] = lh_n
    if new.get("notes") and new["notes"] not in (old.get("notes") or ""):
        old["notes"] = ((old.get("notes") or "") + f" | {run}: " + new["notes"]).strip(" |")
    old["sources"] = sorted(set((old.get("sources") or []) + (new.get("sources") or [])))
    old["last_checked"] = run


def cmd_merge(paths, run):
    db = load_jsonl(DB)
    rundir = HERE / "runs" / run
    rundir.mkdir(parents=True, exist_ok=True)
    if DB.exists() and not (rundir / "events.pre-merge.jsonl").exists():
        shutil.copy(DB, rundir / "events.pre-merge.jsonl")
    log, added, updated, bad = [], 0, 0, 0
    for p in paths:
        for new in load_jsonl(p):
            if not new.get("event_name") or not new.get("organization"):
                bad += 1
                print(f"SKIP (no name/org) in {Path(p).name}: {json.dumps(new)[:120]}")
                continue
            i = find_match(new, db)
            if i is None:
                new = {k: v for k, v in new.items() if k not in COMPUTED}
                new["event_id"] = make_id(new)
                ids = {r["event_id"] for r in db}
                base, n = new["event_id"], 2
                while new["event_id"] in ids:
                    new["event_id"] = f"{base}-{n}"; n += 1
                new["first_seen"] = run
                new["last_checked"] = run
                new.setdefault("found_by", Path(p).stem)
                db.append(new)
                log.append({"run": run, "event_id": new["event_id"], "field": "*", "before": None,
                            "after": "added", "why": f"new event from {Path(p).name}"})
                added += 1
            else:
                before = len(log)
                merge_into(db[i], new, run, log)
                updated += len(log) > before
    write_jsonl(DB, db)
    with open(CHANGES, "a", encoding="utf-8") as f:
        for c in log:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"Merge: {added} added · {updated} updated · {bad} skipped · {len(db)} events in database · {len(log)} changes logged")


# ---------- computed fields ----------
def load_001():
    """Organization domains Machine 001 has contacted, with its status text (read-only)."""
    p = HERE / CONFIG["machine_001_contacted"]
    out = {}
    for r in load_jsonl(p) if p.exists() else []:
        if r.get("type") == "org":
            for d in r.get("domains") or []:
                out[d.lower().removeprefix("www.")] = (r.get("org"), (r.get("status") or "")[:90])
    return out


def load_dnc():
    p = HERE / CONFIG["do_not_contact_register"]
    emails, domains = set(), set()
    for r in load_jsonl(p) if p.exists() else []:
        if r.get("scope") == "domain" and r.get("domain"):
            domains.add(r["domain"].lower())
        if r.get("email"):
            emails.add(r["email"].lower())
    return emails, domains


def cmd_waves(today):
    db = load_jsonl(DB)
    m001 = load_001()
    dnc_emails, dnc_domains = load_dnc()
    this_month = today[:7]
    w = CONFIG["waves"]
    for r in db:
        r["event_id"] = r.get("event_id") or make_id(r)
        m = month_of(r)
        r["event_month"] = m
        if not m:
            r["wave"], r["outreach_opens"], r["notice_months"] = "date_unknown", None, None
        elif m < w["earliest_event_month"]:
            r["wave"], r["outreach_opens"], r["notice_months"] = "skip_before_2027", None, None
        elif w["wave1_first"] <= m <= w["wave1_last"]:
            r["wave"], r["outreach_opens"] = "wave_1", this_month
            r["notice_months"] = months_between(this_month, m)
        else:
            opens = add_months(m, -w["lead_months"])
            r["wave"] = "rolling_open" if opens <= this_month else "rolling_later"
            r["outreach_opens"] = opens
            r["notice_months"] = months_between(this_month, m)
        hosts = {host(r.get("event_url")), host(r.get("org_url"))} - {""}
        hit = None
        for h in hosts:
            for d, v in m001.items():
                if h == d or h.endswith("." + d):
                    hit = v
        r["machine_001_status"] = f"{hit[0]}: {hit[1]}" if hit else "never contacted"
        # Chris 2026-10-23: every org Machine 001 has emailed is excluded from Machine 002 for now (kept in the file, never drafted)
        r["excluded_machine_001"] = bool(hit)
        r["vertical"] = VERTICAL_OF.get(r.get("org_type"), "ECE")
        r["evidence_grade"] = evidence_grade(r)
        r["colorado"] = (r.get("state") == "CO")
        c = r.get("call_for_proposals") or {}
        if c.get("status") == "open" and c.get("deadline") and c["deadline"] < today:
            c["status"] = "closed"
            c["note"] = f"deadline {c['deadline']} passed (set by waves on {today})"
        owner_email = ((r.get("owner") or {}).get("email") or "").lower()
        r["dnc"] = bool(owner_email and owner_email in dnc_emails) or any(
            h == d or h.endswith("." + d) for h in hosts for d in dnc_domains)
    db.sort(key=lambda r: (r.get("event_month") or "9999", r.get("organization") or ""))
    write_jsonl(DB, db)
    from collections import Counter
    c = Counter(r["wave"] for r in db)
    print("Waves: " + " · ".join(f"{k} {v}" for k, v in sorted(c.items())))


# ---------- validation ----------
def cmd_validate():
    db = load_jsonl(DB)
    fails, ids = [], set()
    for r in db:
        e = r.get("event_id") or "?"
        def f(msg): fails.append(f"FAIL {e}: {msg}")
        if e in ids: f("duplicate event_id")
        ids.add(e)
        for k in ("event_name", "organization", "event_url"):
            if not r.get(k): f(f"missing {k}")
        if r.get("org_type") not in ORG_TYPES: f(f"org_type '{r.get('org_type')}' not in config.org_types")
        d = r.get("date_2027") or {}
        if d.get("status") not in DATE_STATUS: f(f"date_2027.status '{d.get('status')}'")
        if d.get("status") in ("confirmed", "estimated"):
            if not month_of(r): f("dated status but no month")
            if not d.get("source_url"): f("dated status but no source_url")
        if d.get("status") == "unknown" and d.get("month"): f("unknown status but month set")
        c = r.get("call_for_proposals") or {}
        if c and c.get("status") not in CFP_STATUS: f(f"cfp status '{c.get('status')}'")
        if c.get("status") == "open" and not c.get("url"): f("open call with no url")
        if c and c.get("type") not in CFP_TYPES: f(f"cfp type '{c.get('type')}'")
        if r.get("keynote_slot") not in YESNO: f(f"keynote_slot '{r.get('keynote_slot')}'")
        if r.get("procurement") not in PROCUREMENT: f(f"procurement '{r.get('procurement')}'")
        o = r.get("owner") or {}
        if o.get("name") and not o.get("source_url"): f("owner named with no source_url")
        if o.get("email") and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-z]{2,}", o["email"], re.I):
            f(f"owner email malformed: {o['email']}")
    for x in fails: print(x)
    print(f"Validate: {len(db)} events · {len(fails)} problems")
    sys.exit(1 if fails else 0)


# ---------- reports ----------
def fmt_date(r):
    d = r.get("date_2027") or {}
    if d.get("status") == "confirmed":
        s = d.get("start") or d.get("month")
        return f"{s}{(' to ' + d['end']) if d.get('end') and d.get('end') != d.get('start') else ''} (confirmed)"
    if d.get("status") == "estimated":
        return f"{d.get('month')} (estimated)"
    return "unknown"


def link(text, url):
    return f"[{text}]({url})" if url else text


def owner_txt(r):
    o = r.get("owner") or {}
    if not o.get("name"):
        return "— not found"
    t = f"{o['name']}" + (f", {o['title']}" if o.get("title") else "")
    return link(t, o.get("source_url"))


def cfp_txt(r):
    c = r.get("call_for_proposals") or {}
    st = c.get("status") or "not_found"
    if st in ("open", "upcoming"):
        return link(f"{st.upper()} {c.get('type') or ''} {('due ' + c['deadline']) if c.get('deadline') else ''}".strip(), c.get("url"))
    return st.replace("_", " ")


def table(rows):
    out = ["| Event | Organization | St | 2027 date | Person in charge | Open call | Keynote slot | 001 status |",
           "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        name = link(r.get("event_name", "").replace("|", "/"), r.get("event_url"))
        flags = (" ⚑CO" if r.get("colorado") else "") + (" ⛔DNC" if r.get("dnc") else "")
        m001 = r.get("machine_001_status") or ""
        m001 = "never" if m001 == "never contacted" else m001.split(":")[1].strip()[:40] if ":" in m001 else m001[:40]
        out.append(f"| {name}{flags} | {(r.get('organization') or '').replace('|','/')} | {r.get('state') or ''} | {fmt_date(r)} | "
                   f"{owner_txt(r).replace('|','/')} | {cfp_txt(r)} | {r.get('keynote_slot')} | {m001.replace('|','/')} |")
    return "\n".join(out)


MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def cmd_report(run):
    from collections import Counter
    db = load_jsonl(DB)
    changes = [c for c in load_jsonl(CHANGES) if c.get("run") == run]
    rundir = HERE / "runs" / run
    rundir.mkdir(parents=True, exist_ok=True)
    by_month = Counter(r.get("event_month") for r in db if r.get("event_month"))
    status = Counter((r.get("date_2027") or {}).get("status") for r in db)
    waves = Counter(r.get("wave") for r in db)
    opens = sorted([r for r in db if (r.get("call_for_proposals") or {}).get("status") in ("open", "upcoming")],
                   key=lambda r: ((r.get("call_for_proposals") or {}).get("deadline") or "9999"))
    no_owner = [r for r in db if not (r.get("owner") or {}).get("name")]
    added = [c for c in changes if c["field"] == "*"]
    confirmed_now = [c for c in changes if c["field"] == "date_2027" and "-> confirmed" in c["why"]]
    moved = [c for c in changes if c["field"] == "date_2027" and ("changed" in c["why"] or "revised" in c["why"])]

    head = [f"# Event refresh — {run}", "",
            f"**Database:** {len(db)} events · dates: {status.get('confirmed',0)} confirmed · {status.get('estimated',0)} estimated · {status.get('unknown',0)} unknown",
            f"**Waves:** wave 1 (Jan–May 2027, outreach now) {waves.get('wave_1',0)} · rolling, open now {waves.get('rolling_open',0)} · rolling, opens later {waves.get('rolling_later',0)} · date unknown {waves.get('date_unknown',0)} · before 2027 (skip) {waves.get('skip_before_2027',0)}",
            f"**This run:** {len(added)} new events · {len(confirmed_now)} dates newly confirmed · {len(moved)} dates moved · {len(changes)} field changes in total",
            f"**Gaps left:** {len(no_owner)} events with no person in charge found", "",
            "## Events by month (2027)", "",
            "| " + " | ".join(MONTHS) + " |", "|" + "---|" * 12,
            "| " + " | ".join(str(by_month.get(f"2027-{i:02d}", 0)) for i in range(1, 13)) + " |", ""]
    sec = ["## Open and upcoming calls (soonest deadline first)", "", table(opens) if opens else "None found.", ""]
    if confirmed_now or moved:
        sec += ["## Dates confirmed or moved this run", ""]
        for c in confirmed_now + moved:
            a = c["after"] or {}
            sec.append(f"- {c['event_id']}: {c['why']} → {a.get('start') or a.get('month')} ({a.get('source_url')})")
        sec.append("")
    rep = head + sec
    (rundir / "refresh-report.md").write_text("\n".join(rep), encoding="utf-8")

    cal = ["---", "title: Machine 002 — event calendar (GENERATED VIEW — do not edit; source is events.jsonl)",
           f"generated: {run}", "---", "", f"# Event calendar — generated {run}", "",
           "Read-only view of `events.jsonl`. Edit the database, not this file. ⚑CO = Colorado (your call) · ⛔DNC = on the do-not-contact register.", ""] + head[2:]
    for wave, title in (("wave_1", "Wave 1 — events Jan–May 2027 · outreach opens now"),
                        ("rolling_open", "Rolling — outreach window already open"),
                        ("rolling_later", "Rolling — outreach opens later (month shown per event)"),
                        ("date_unknown", "Date unknown — no dated edition found"),
                        ("skip_before_2027", "Before 2027 — skipped")):
        rows = [r for r in db if r.get("wave") == wave]
        if not rows:
            continue
        cal += [f"## {title} ({len(rows)})", ""]
        if wave == "rolling_later":
            for opens in sorted({r["outreach_opens"] for r in rows}):
                grp = [r for r in rows if r["outreach_opens"] == opens]
                cal += [f"### Outreach opens {opens} ({len(grp)})", "", table(grp), ""]
        else:
            cal += [table(rows), ""]
    (HERE / "events-calendar.generated.md").write_text("\n".join(cal), encoding="utf-8")
    print(f"Report: runs/{run}/refresh-report.md · events-calendar.generated.md")


def cmd_worklist(segment=None):
    """Rows the refresh must re-check. With --segment, only the rows that segment's
    research agent owns (the segment that first found the event)."""
    db = load_jsonl(DB)
    db.sort(key=lambda r: (r.get("event_month") or "9999"))
    for r in db:
        if segment and r.get("found_by") != segment:
            continue
        print(json.dumps({k: r.get(k) for k in ("event_id", "event_name", "organization", "state", "event_url",
                                                 "org_url", "date_2027", "owner", "call_for_proposals", "keynote_slot")},
                         ensure_ascii=False))


def cmd_dupes():
    """Print pairs of events that MAY be the same event (same page, or same organization
    words and similar name), for a person to judge. Changes nothing."""
    db = load_jsonl(DB)
    stop = set("annual conference the of and early childhood education association state for in a on summit institute young children aeyc head start".split())
    def words(s): return set(w for w in re.findall(r"[a-z0-9]+", (s or "").lower()) if w not in stop and len(w) > 2 and not re.fullmatch(r"20\d\d", w))
    p = HERE / "not-duplicates.jsonl"   # pairs a person already judged as different events
    judged = {frozenset((x["a"], x["b"])) for x in load_jsonl(p)} if p.exists() else set()
    n = 0
    for i, a in enumerate(db):
        for b in db[i + 1:]:
            if frozenset((a["event_id"], b["event_id"])) in judged:
                continue
            same_page = norm_url(a.get("event_url")) and norm_url(a.get("event_url")) == norm_url(b.get("event_url"))
            ta, tb = words(a.get("event_name")), words(b.get("event_name"))
            oa, ob = words(a.get("organization")), words(b.get("organization"))
            jn = len(ta & tb) / max(1, len(ta | tb)); jo = len(oa & ob) / max(1, len(oa | ob))
            if (same_page and jn >= 0.3) or (jo >= 0.5 and jn >= 0.5):
                n += 1
                print(f"MAYBE SAME  {a['event_id']} ({a.get('event_month')})  <>  {b['event_id']} ({b.get('event_month')})")
    print(f"Dupes: {n} pairs to look at")


def cmd_retire(eid, why, run):
    db = load_jsonl(DB)
    keep = [r for r in db if r.get("event_id") != eid]
    gone = [r for r in db if r.get("event_id") == eid]
    if not gone:
        sys.exit(f"FAIL retire: no event with id {eid}")
    for r in gone:
        r["retired"] = {"run": run, "why": why}
    with open(HERE / "events-retired.jsonl", "a", encoding="utf-8") as f:
        for r in gone:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(CHANGES, "a", encoding="utf-8") as f:
        f.write(json.dumps({"run": run, "event_id": eid, "field": "*", "before": "in database",
                            "after": "retired", "why": why}, ensure_ascii=False) + "\n")
    write_jsonl(DB, keep)
    print(f"Retired {eid}: {why}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    def opt(name, default=None):
        return a[a.index(name) + 1] if name in a else default
    today = datetime.date.today().isoformat()
    if a[0] == "merge":
        files = [x for x in a[1:] if not x.startswith("--") and x != opt("--run")]
        cmd_merge(files, opt("--run", today))
    elif a[0] == "waves":
        cmd_waves(opt("--today", today))
    elif a[0] == "validate":
        cmd_validate()
    elif a[0] == "report":
        cmd_report(opt("--run", today))
    elif a[0] == "dupes":
        cmd_dupes()
    elif a[0] == "retire":
        cmd_retire(a[1], opt("--why", "no reason given"), opt("--run", today))
    elif a[0] == "worklist":
        cmd_worklist(opt("--segment"))
    else:
        sys.exit(__doc__)
