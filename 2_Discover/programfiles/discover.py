#!/usr/bin/env python3
"""discover.py -- the ONE discovery engine for every outreach machine (Rulebook D; Stage 4, Chris 2026-10-30/31).

Deterministic bookkeeping only. The AI does the reading/research (one batch per helper) and returns JSON results;
this script decides WHAT to sweep next, checks results, and writes finds to ONE place: 2_Discover/ledgers/finds.jsonl,
which build_master.py reads. Nothing here edits orgs.jsonl, sends, drafts or contacts anyone.

  python3 discover.py build-sources          seed/refresh the source list (idempotent; keeps sweep history)
  python3 discover.py next --run RUN         pick tonight's due sources within the caps -> batch files + checkpoint
                                             (re-running for the same RUN RESUMES: prints the batches still pending)
  python3 discover.py checkq --q "QUERY"     REPEAT or OK (no-repeat search log; Rulebook D4)
  python3 discover.py ingest --run RUN --batch K FILE   validate one batch's results -> inbox, sources, search log
  python3 discover.py stats                  source list by type / due / swept; inbox size

FILES (outreach-engine/discovery/ unless noted)
  sources.jsonl     one row per source {id, type, label, region, org_type, url, icps[], priority, status, sweeps,
                    last_swept, next_resweep, yield{finds,new_events,people,keynoters,new_sources}, origin, note}
  keynoters.jsonl   people whose speaking pages are sources (never contacts, never emailed — Rulebook D5)
  search-log.jsonl  every web search ever run {q, norm, run, date, domains_seen}; a repeat is refused
  PROMPT.md         the helper instructions + output schema
  runs/<RUN>/       batch_<k>.jsonl, result_<k>.jsonl, state.json (checkpoint), known-domains.txt
  2_Discover/ledgers/finds.jsonl   append-only finds; build_master.py turns them into master-list rows
"""
import argparse, datetime, hashlib, json, os, re, sys
from zoneinfo import ZoneInfo

import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_shared", "orchestrator")); import paths  # the one file that knows every folder (2026-11-03)
ENG = paths.ROOT
MK = paths.MARKETING
HST = paths.HST
DISC = paths.ledgers("discover"); DRUNS = paths.runs("discover")
MASTER = paths.MASTER
S = paths.settings()
ROOT = paths.MASTER
CFG = S["discovery"]
INBOX = paths.FINDS                                            # 2_Discover/ledgers/finds.jsonl (was 2_Discover/ledgers/finds.jsonl)
SRC = paths.SOURCES; KEY = paths.KEYNOTERS; SLOG = paths.SEARCH_LOG   # THE one discovery ledger (2026-11-03)
ICPDIR = paths.ICP_DIR
TODAY = datetime.datetime.now(ZoneInfo("America/Denver")).date().isoformat()

def jl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()] if os.path.exists(p) else []
def wjl(p, rows):
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    os.replace(tmp, p)
def ajl(p, rows):
    with open(p, "a", encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
def norm_dom(d):
    d = re.sub(r"^https?://", "", str(d or "").strip().lower()).split("/")[0].split("?")[0]
    return d[4:] if d.startswith("www.") else d
def slug(s): return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")[:80]
def normq(q): return " ".join(sorted(re.sub(r"[^a-z0-9 ]+", " ", (q or "").lower()).split()))
def plus_days(d, n): return (datetime.date.fromisoformat(d) + datetime.timedelta(days=n)).isoformat()

# ---------------------------------------------------------------- active ICPs (only ICPs that belong to a market are ever searched)
def active_icps():
    out = {}
    for f in sorted(os.listdir(ICPDIR)):
        m = re.match(r"(ICP-\d{3})-.*\.md$", f)
        if not m: continue
        txt = open(os.path.join(ICPDIR, f), encoding="utf-8").read()
        st = re.search(r"^status:\s*(\S+)", txt, re.M); mk = re.search(r"^markets:\s*\[([^\]]*)\]", txt, re.M)
        markets = [x.strip() for x in (mk.group(1) if mk else "").split(",") if x.strip()]
        status = st.group(1) if st else "?"
        sec4 = re.search(r"^## 4\..*?(?=^## 5\.)", txt, re.M | re.S)
        sec1 = re.search(r"\*\*Function test:\*\*\s*(.+)", txt)
        if markets and status.upper() not in ("RETIRED", "SUPERSEDED"):
            out[m.group(1)] = {"file": f, "status": status, "markets": markets,
                               "function_test": sec1.group(1).strip() if sec1 else None,
                               "where": sec4.group(0).strip() if sec4 else None}
    return out

EVENT_ICPS = ["ICP-001", "ICP-002", "ICP-003", "ICP-004", "ICP-006"]          # event owners (MKT-002)
TYPE_ICPS = {   # directory org_type -> ICPs it serves; [] = no active ICP (parked, never swept)
    "aeyc_affiliate": ["ICP-004"], "head_start_assoc": ["ICP-004", "ICP-003"], "ccrr_child_care_aware": ["ICP-001"],
    "family_child_care_assoc": ["ICP-004"], "afterschool_network": [], "infant_mental_health_assoc": ["ICP-006"],
    "state_early_learning_agency_pd_calendar": ["ICP-002"], "education_service_agencies": ["ICP-002"],
    "community_college_ece": ["ICP-006"], "pd_registry": ["ICP-002"],
    "provincial_ece_association": ["ICP-004"], "child_care_federation_or_coalition": ["ICP-004"],
    "provincial_ministry_ece_pd_calendar": ["ICP-002"], "college_ece_programs": ["ICP-006"], "school_age_care_assoc": []}
ASSOC_TYPES = {"aeyc_affiliate", "head_start_assoc", "family_child_care_assoc", "infant_mental_health_assoc",
               "provincial_ece_association", "child_care_federation_or_coalition"}

# ---------------------------------------------------------------- build-sources
def build_sources():
    pri, rs = CFG["priority"], CFG["resweep_days"]
    act = active_icps()
    old = {r["id"]: r for r in jl(SRC)}
    rows = {}
    def put(r):
        prev = old.get(r["id"]) or rows.get(r["id"])
        if prev:   # keep sweep history; refresh descriptive fields
            for k in ("status", "sweeps", "last_swept", "next_resweep", "yield", "note"):
                if prev.get(k) is not None: r[k] = prev[k]
        r["icps"] = sorted(i for i in r["icps"] if i in act)
        if not r["icps"] and r.get("status") not in ("swept", "not_found"): r["status"] = "parked"   # serves no active ICP
        rows[r["id"]] = r
    def base(id_, type_, label, region=None, org_type=None, url=None, icps=(), origin="", note=None, last=None, nxt=None, sweeps=0, status="queued"):
        return {"id": id_, "type": type_, "label": label, "region": region, "org_type": org_type, "url": url,
                "icps": list(icps), "priority": pri[type_] if type_ != "directory" else (pri["assoc_directory"] if org_type in ASSOC_TYPES else pri["directory"]),
                "status": status, "sweeps": sweeps, "last_swept": last, "next_resweep": nxt,
                "yield": {"finds": 0, "new_events": 0, "people": 0, "keynoters": 0, "new_sources": 0}, "origin": origin, "note": note}
    # 2026-11-03: ONE discovery ledger. The old Machine 2 source map was folded into sources.jsonl (every row present); rows not re-derived
    # below are kept as they are (see the end of this function), so the ledger is the source of its own history.
    # keynoter bank -> people file (sources, never contacts)
    kb = {}
    for k in jl(KEY):
        kid = "kn:" + slug(k.get("name"))
        kb.setdefault(kid, dict(k, id=kid))
        put(base(kid, "keynoter", "keynoter: " + (k.get("name") or ""), url=k.get("speaking_url") or k.get("site"),
                 icps=EVENT_ICPS, origin=(old.get(kid) or {}).get("origin") or "keynoter bank", note=(k.get("focus") or None)))   # keep "found on <page>"
    wjl(KEY, [kb[k] for k in sorted(kb)])
    # Machine 1 territory: each state's CCR&R lead-agency directory
    terr = json.load(open(os.path.join(paths.machine_dir("OM-1"), "territory.json"), encoding="utf-8"))
    for stc, t in sorted(terr.get("territories", {}).items()):
        if not isinstance(t, dict): continue
        excluded = t.get("status") == "EXCLUDED" or stc == "CO"
        put(base("state:%s:ccrr_directory" % stc, "state_directory", "%s CCR&R lead-agency directory" % stc, stc, "ccrr_directory",
                 t.get("directory_url"), ["ICP-001", "ICP-002"], "Machine 1 territory",
                 "Machine 1 status %s · enumerated %s · remaining %s" % (t.get("status"), t.get("enumerated"), t.get("remaining")),
                 t.get("directory_read"), plus_days(t["directory_read"], rs["state_directory"]) if t.get("directory_read") else None,
                 1 if t.get("directory_read") else 0, "parked" if excluded else ("swept" if t.get("directory_read") else "queued")))
    # Branch sources: every known event page in the master list (sponsors, exhibitors, partners, committee, keynote pages)
    for o in jl(os.path.join(ROOT, "orgs.jsonl")):
        if o.get("referrer") or o["fit"]["status"] == "not_fit" or o["exclusions"].get("colorado"): continue
        for e in o.get("events") or []:
            u = e.get("url")
            if not u or not str(u).startswith("http"): continue
            bid = "branch:" + hashlib.sha1(u.encode()).hexdigest()[:12]
            bicps = [i for i in o["icps"] if i in EVENT_ICPS]
            if not bicps and o["icps"] != ["unclassified"]: continue      # e.g. ICP-007/008 orgs: no active market, never searched
            put(base(bid, "branch", "branch: %s — %s" % (o["name"], e.get("name") or u), o.get("state"), None, u,
                     bicps or EVENT_ICPS, "master list event", "org " + o["org_id"]))
    # Partner pages (Chris 2026-11-04): pages listing an org's partners, written by the qualify/people helpers -> 'partners' sources
    for pp in jl(os.path.join(paths.ledgers("discover"), "partner-pages.jsonl")):
        u = pp.get("url")
        if not u or not str(u).startswith("http"): continue
        pid = "partners:" + hashlib.sha1(u.encode()).hexdigest()[:10]
        put(base(pid, "partners", "partners: " + (pp.get("label") or u), pp.get("state"), None, u,
                 ["ICP-001", "ICP-002", "ICP-003", "ICP-004", "ICP-006"], "partner page found on " + str(pp.get("found_on") or "?")))
    # List pages (Chris 2026-11-06, option 5): national/umbrella pages that list many orgs of one kind — mined without searching
    for ls in jl(os.path.join(paths.ledgers("discover"), "list-sources.jsonl")):
        if not str(ls.get("url") or "").startswith("http"): continue
        put(base(ls["id"], "list", ls.get("label") or ls["url"], None, ls.get("org_type"), ls["url"], ls.get("icps") or EVENT_ICPS,
                 "list-sources.jsonl", " · ".join(x for x in (ls.get("verified"), ls.get("note")) if x) or None))
    # every ledger row not re-derived above is kept (the old source map, sources found by earlier sweeps, swept history) — re-checked against the active ICPs
    for oid, r in old.items():
        if oid not in rows: put(dict(r))
    # parked reason note
    for r in rows.values():
        if r["status"] == "parked" and not (r.get("note") or "").startswith("PARKED"):
            r["note"] = ("PARKED: serves no ICP in an active market" if not r["icps"] else "PARKED: Colorado / excluded territory") + ((" · " + r["note"]) if r.get("note") else "")
    wjl(SRC, [rows[k] for k in sorted(rows)])
    print("SOURCES %d · %s" % (len(rows), counts(rows.values())))
    print("ACTIVE ICPS (searched): " + ", ".join("%s(%s)" % (k, v["status"]) for k, v in sorted(act.items())))

def counts(rows):
    c = {}
    for r in rows:
        k = "%s/%s" % (r["type"], r["status"])
        c[k] = c.get(k, 0) + 1
    return ", ".join("%s %d" % kv for kv in sorted(c.items()))

def due(r):
    return r["status"] not in ("parked",) and r["icps"] and (r["next_resweep"] is None and r["status"] == "queued" or (r["next_resweep"] or "9999") <= TODAY)

# Chris 2026-11-06 (option 2): OM-2 first, and its searches protected. A source "serves OM-2" when it is event-shaped or an association/IMH kind.
OM2_TYPES = {"keynoter", "calendar", "venue", "branch", "partners", "list"}
OM2_ORG_TYPES = {"aeyc_affiliate", "head_start_assoc", "family_child_care_assoc", "infant_mental_health_assoc", "community_college_ece",
                 "provincial_ece_association", "child_care_federation_or_coalition", "college_ece_programs"}
def serves_om2(r):
    return r["type"] in OM2_TYPES or r.get("org_type") in OM2_ORG_TYPES or any(i in ("ICP-004", "ICP-006") for i in r.get("icps") or [])
NEEDS_SEARCH = {"directory", "state_directory", "search"}
def needs_search(r): return r["type"] in NEEDS_SEARCH and not r.get("url")

REGION_ORDER = None
def region_rank(r):
    global REGION_ORDER
    if REGION_ORDER is None:
        REGION_ORDER = {s: i for i, s in enumerate(CFG["region_order"])}
    return REGION_ORDER.get((r.get("region") or "").upper(), 999)

# ---------------------------------------------------------------- next (with checkpoint/resume)
def next_run(run, n_src=None, n_br=None, n_q=None, machines=None):
    d = os.path.join(DRUNS, run); st_p = os.path.join(d, "state.json")
    if os.path.exists(st_p):
        st = json.load(open(st_p))
        pend = [b for b in st["batches"] if b["status"] != "ingested"]
        print("RESUME run %s: %d of %d batches still pending" % (run, len(pend), len(st["batches"])))
        for b in pend: print("BATCH %s %s -> write results to %s · SEARCHES ALLOWED %d" % (b["k"], b["file"], b["result"], b.get("searches_allowed", 0)))
        print("SEARCHES LEFT TONIGHT %d" % (st["searches_cap"] - st["searches_used"]))
        return
    os.makedirs(d, exist_ok=True)
    rows = jl(SRC)
    ms = set((machines or "OM-1,OM-2").split(","))
    cand = [r for r in rows if due(r)]
    if ms == {"OM-2"}: cand = [r for r in cand if serves_om2(r)]          # a pass for OM-2 only sweeps OM-2 sources
    cand = sorted(cand, key=lambda r: (0 if "OM-2" in ms and serves_om2(r) else 1, r["priority"], region_rank(r), r["id"]))
    src = [r for r in cand if r["type"] != "branch"][:CFG["sources_per_night"] if n_src is None else n_src]
    br = [r for r in cand if r["type"] == "branch"][:CFG["branch_events_per_night"] if n_br is None else n_br]
    per = CFG["rows_per_helper"]
    batches = []
    picked = src + br
    for i in range(0, len(picked), per):
        k = "%02d" % (len(batches) + 1)
        bf = os.path.join(d, "batch_%s.jsonl" % k); rf = os.path.join(d, "result_%s.jsonl" % k)
        wjl(bf, picked[i:i + per])
        batches.append({"k": k, "file": bf, "result": rf, "ids": [r["id"] for r in picked[i:i + per]], "status": "pending"})
    qcap = CFG["searches_per_night"] if n_q is None else n_q
    if qcap > 0:
        k = "%02d" % (len(batches) + 1)
        bf = os.path.join(d, "batch_%s.jsonl" % k); rf = os.path.join(d, "result_%s.jsonl" % k)
        act = active_icps()
        icp_order = sorted(act, key=lambda i: (0 if i in ("ICP-004", "ICP-006") and "OM-2" in ms else 1, i))
        if ms == {"OM-2"}: icp_order = [i for i in icp_order if i in ("ICP-004", "ICP-006")]
        wjl(bf, [{"id": "search:%s:%s" % (run, i), "type": "search", "label": "web search fallback for %s" % i, "icps": [i],
                  "function_test": act[i]["function_test"], "where": act[i]["where"]} for i in icp_order])
        batches.append({"k": k, "file": bf, "result": rf, "ids": ["search:%s:%s" % (run, i) for i in icp_order], "status": "pending", "search": True})
    # per-batch search allowance (2026-11-06): a batch may never spend another batch's searches; OM-2 batches get the protected share
    rowsof = {x["k"]: jl(x["file"]) for x in batches}
    srch = [x for x in batches if any(needs_search(r) for r in rowsof[x["k"]])]
    om2b = [x for x in srch if "OM-2" in ms and all(serves_om2(r) for r in rowsof[x["k"]])]
    oth = [x for x in srch if x not in om2b]
    share = float(CFG.get("om2_search_share", 0.7)) if om2b and oth else (1.0 if om2b else 0.0)
    pool2, pool1 = int(qcap * share), qcap - int(qcap * share)
    for grp, pool in ((om2b, pool2), (oth, pool1)):
        for i, x in enumerate(grp): x["searches_allowed"] = pool // len(grp) + (1 if i < pool % len(grp) else 0)
    for x in batches: x.setdefault("searches_allowed", 0)
    # known domains for helpers (skip what we already have; the builder dedups anyway)
    known = sorted({dd for o in jl(os.path.join(ROOT, "orgs.jsonl")) for dd in o.get("domains", [])})
    open(os.path.join(d, "known-domains.txt"), "w").write("\n".join(known) + "\n")
    st = {"run": run, "created": TODAY, "batches": batches, "searches_cap": qcap, "searches_used": 0, "machines": sorted(ms)}
    json.dump(st, open(st_p, "w"), indent=1)
    print("RUN %s: %d sources + %d branch events + search fallback (%d searches max) in %d batches" % (run, len(src), len(br), qcap, len(batches)))
    for b in batches: print("BATCH %s %s -> write results to %s · SEARCHES ALLOWED %d" % (b["k"], b["file"], b["result"], b["searches_allowed"]))
    print("KNOWN DOMAINS %s (%d)" % (os.path.join(d, "known-domains.txt"), len(known)))

def checkq(q):
    n = normq(q)
    hit = next((r for r in jl(SLOG) if r["norm"] == n), None)
    print(("REPEAT (run %s, %s) — do not search this again" % (hit["run"], hit["date"])) if hit else "OK")
    return 1 if hit else 0

# ---------------------------------------------------------------- ingest
def _content(rec):
    return hashlib.sha1(json.dumps([rec["find_id"].split("-")[0], rec["org"], rec["icps"], rec["events"], rec["people"]], sort_keys=True).encode()).hexdigest()

SCHEMA_TOP = {"id", "status", "finds", "keynoters", "new_sources", "searches", "note"}
def ingest(run, k, path):
    d = os.path.join(DRUNS, run); st_p = os.path.join(d, "state.json"); st = json.load(open(st_p))
    b = next(x for x in st["batches"] if x["k"] == k)
    res = jl(path)
    errs = []
    ids = {r.get("id") for r in res}
    for i in b["ids"]:
        if i not in ids: errs.append("missing result line for %s" % i)
    act = active_icps()
    slog = jl(SLOG); seen_q = {r["norm"] for r in slog}
    _inb = jl(INBOX)
    inbox_ids = {r["find_id"] for r in _inb}
    inbox_content = {_content(r) for r in _inb}
    new_inbox, new_q, repeats = [], [], []
    srcs = {r["id"]: r for r in jl(SRC)}
    used = st["searches_used"]
    for r in res:
        extra = set(r) - SCHEMA_TOP
        if extra: errs.append("%s: unknown fields %s" % (r.get("id"), sorted(extra)))
        for f in r.get("finds") or []:
            nm, dom = (f.get("organization") or "").strip(), norm_dom(f.get("domain"))
            if not nm and not dom: errs.append("%s: a find has no organization or domain" % r.get("id")); continue
            if not f.get("evidence_url"): errs.append("%s: %s has no evidence_url" % (r.get("id"), nm or dom)); continue
            icps = sorted({i for i in (f.get("icps") or []) if re.match(r"ICP-\d{3}$", i)})
            fid = hashlib.sha1(("%s|%s|%s" % (dom, slug(nm), (f.get("state") or "").upper())).encode()).hexdigest()[:16]
            rec = {"find_id": fid, "run": run, "source_id": r.get("id"), "found": TODAY,
                   "org": {"name": nm or None, "domain": dom or None, "state": (f.get("state") or None), "country": f.get("country") or None,
                           "url": f.get("org_url") or None},
                   "icps": icps, "icp_why": f.get("icp_why"), "evidence_url": f["evidence_url"],
                   "events": [{"name": e.get("name"), "url": e.get("url"), "last_edition_date": e.get("last_edition_date"),
                               "next_edition_date": e.get("next_edition_date"), "attendance": e.get("attendance"),
                               "cfp": e.get("cfp") or {"url": None, "opens": None, "deadline": None},
                               "keynote_path": e.get("keynote_path"), "evidence_url": e.get("evidence_url") or e.get("url")}
                              for e in (f.get("events") or [])],
                   "people": [{"name": p.get("name"), "role": p.get("role"), "email": (p.get("email") or None),
                               "evidence_url": p.get("evidence_url")} for p in (f.get("people") or []) if p.get("evidence_url")],
                   "note": f.get("note")}
            ch = _content(rec)
            if ch in inbox_content: continue          # exact same find already in the inbox: nothing new
            if fid in inbox_ids: rec["find_id"] = fid + "-" + ch[:6]   # same org, new events/people: keep both
            inbox_ids.add(rec["find_id"]); inbox_content.add(ch); new_inbox.append(rec)
        for q in r.get("searches") or []:
            n = normq(q.get("q"))
            if not n: continue
            if n in seen_q: repeats.append(q.get("q")); continue
            seen_q.add(n); used += 1
            new_q.append({"q": q.get("q"), "norm": n, "run": run, "date": TODAY, "domains_seen": q.get("domains_seen") or [], "source_id": r.get("id")})
        s = srcs.get(r.get("id"))
        if s:
            s["status"] = "swept" if r.get("status") != "not_found" else "not_found"
            s["sweeps"] = (s.get("sweeps") or 0) + 1; s["last_swept"] = TODAY
            s["next_resweep"] = plus_days(TODAY, CFG["resweep_days"].get(s["type"], 120))
            y = s["yield"]; y["finds"] += len(r.get("finds") or []); y["keynoters"] += len(r.get("keynoters") or []); y["new_sources"] += len(r.get("new_sources") or [])
            y["new_events"] += sum(len(f.get("events") or []) for f in r.get("finds") or []); y["people"] += sum(len(f.get("people") or []) for f in r.get("finds") or [])
            if r.get("note"): s["note"] = (r["note"] or "")[:300]
        for kp in r.get("keynoters") or []:
            if not kp.get("name"): continue
            kid = "kn:" + slug(kp["name"])
            if kid not in srcs:
                srcs[kid] = {"id": kid, "type": "keynoter", "label": "keynoter: " + kp["name"], "region": None, "org_type": None,
                             "url": kp.get("speaking_url") or kp.get("site"), "icps": [i for i in EVENT_ICPS if i in act],
                             "priority": CFG["priority"]["keynoter"], "status": "queued", "sweeps": 0, "last_swept": None, "next_resweep": None,
                             "yield": {"finds": 0, "new_events": 0, "people": 0, "keynoters": 0, "new_sources": 0},
                             "origin": "found on %s" % (kp.get("found_on") or r.get("id")), "note": kp.get("focus")}
                ajl(KEY, [dict(kp, id=kid, added=TODAY)])
        for ns in r.get("new_sources") or []:
            if ns.get("type") not in ("calendar", "venue", "directory", "partners") or not ns.get("url"): continue
            nid = "%s:%s" % (ns["type"], hashlib.sha1(ns["url"].encode()).hexdigest()[:10])
            if nid not in srcs:
                srcs[nid] = {"id": nid, "type": ns["type"], "label": ns.get("label") or ns["url"], "region": ns.get("region"), "org_type": None,
                             "url": ns["url"], "icps": [i for i in EVENT_ICPS if i in act], "priority": CFG["priority"].get(ns["type"], 50),
                             "status": "queued", "sweeps": 0, "last_swept": None, "next_resweep": None,
                             "yield": {"finds": 0, "new_events": 0, "people": 0, "keynoters": 0, "new_sources": 0},
                             "origin": "found on %s" % r.get("id"), "note": None}
    if used > st["searches_cap"]: errs.append("search cap exceeded: %d > %d" % (used, st["searches_cap"]))
    if "searches_allowed" in b and len(new_q) > b["searches_allowed"]:
        errs.append("this batch's search allowance exceeded: %d logged > %d allowed (list only the searches you are allowed; the rest are not done)" % (len(new_q), b["searches_allowed"]))
    if b["status"] == "ingested":   # a re-run of an ingested batch writes nothing; it only shows what would be new
        print("ALREADY INGESTED batch %s — re-check only, nothing written: %d new finds · %d new searches · %d repeated searches refused" % (k, len(new_inbox), len(new_q), len(repeats)))
        return 0
    if errs:
        print("FAIL CLOSED: batch %s results rejected; fix the result file and ingest again:" % k)
        for e in errs: print("  - " + e)
        return 2
    ajl(INBOX, new_inbox); ajl(SLOG, new_q)
    wjl(SRC, [srcs[x] for x in sorted(srcs)])
    st["searches_used"] = used; b["status"] = "ingested"; b["counts"] = {"finds": len(new_inbox), "searches": len(new_q), "repeats_refused": len(repeats)}
    json.dump(st, open(st_p, "w"), indent=1)
    print("INGESTED batch %s: %d finds to the inbox · %d new searches logged · %d repeated searches refused%s" %
          (k, len(new_inbox), len(new_q), len(repeats), (" (" + "; ".join(repeats[:5]) + ")") if repeats else ""))
    left = [x["k"] for x in st["batches"] if x["status"] != "ingested"]
    print("PENDING BATCHES: " + (", ".join(left) if left else "none — rebuild the master list"))
    return 0

def stats():
    rows = jl(SRC)
    print("SOURCES %d · %s" % (len(rows), counts(rows)))
    print("DUE NOW %d" % sum(1 for r in rows if due(r)))
    print("INBOX %d finds · SEARCH LOG %d · KEYNOTERS %d" % (len(jl(INBOX)), len(jl(SLOG)), len(jl(KEY))))

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("--run"); ap.add_argument("--batch"); ap.add_argument("--q"); ap.add_argument("file", nargs="?"); ap.add_argument("--sources", type=int); ap.add_argument("--branches", type=int); ap.add_argument("--searches", type=int); ap.add_argument("--machines")
    a = ap.parse_intermixed_args()
    if a.cmd == "build-sources": build_sources()
    elif a.cmd == "next": next_run(a.run, a.sources, a.branches, a.searches, a.machines)
    elif a.cmd == "checkq": sys.exit(checkq(a.q))
    elif a.cmd == "ingest": sys.exit(ingest(a.run, a.batch, a.file))
    elif a.cmd == "stats": stats()
    else: print(__doc__); sys.exit(2)
