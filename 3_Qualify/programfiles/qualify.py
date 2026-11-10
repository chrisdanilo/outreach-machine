#!/usr/bin/env python3
"""qualify.py -- QUALIFY + ROUTE + TIME, step 1 (fit) bookkeeping (Rulebook C, E, F; Stage 5, Chris 2026-10-30/31).

The AI reads pages and answers each ICP's must-have criteria with a quote; THIS SCRIPT decides. A quote counts only if it
is found verbatim (normalized) in a CAPTURE of that live page made in the Browser pane by the extractor JavaScript this
script prints (same idea as Machine 2's CAPA-2026-10-28 live-page check: the page's own words, never a summary).
Decisions go to ONE place, 3_Qualify/ledgers/decisions.jsonl, which build_master.py reads; routing (OM-1/OM-2/none) and
timing (outreach_opens / outreach_status per event, Rulebook F) are computed there, deterministically, every rebuild.

  python3 qualify.py next --run RUN            pick tonight's orgs within the cap -> batch files + checkpoint (resumable)
  python3 qualify.py js [--url U]              the capture JavaScript (keyword lines) to run in the Browser pane on a page
  python3 qualify.py js --url U --quotes JSON  the VERIFY JavaScript: the page confirms each exact quote; returns a compact
                                               capture holding only the confirmed quotes (lines) -> store it with capture
  python3 qualify.py capture --run RUN FILE    store capture(s) (one JSON object per line, as the JS returned them)
  python3 qualify.py ingest --run RUN --batch K FILE   verify a helper's answers against the captures, decide, write inbox
  python3 qualify.py support-items --run RUN   the verified "yes" quotes for the Haiku support check (one per line)
  python3 qualify.py support --run RUN FILE    record Haiku verdicts; a quote that does not support its criterion -> unknown
  python3 qualify.py set-date                  set master settings as_of = today (America/Denver); timing re-evaluates
  python3 qualify.py stats

DECISION (code): per ICP, every Must answered "yes" with a verified quote and no disqualifier hit -> that ICP fits;
a verified "no" on a Must, or a verified disqualifier hit -> that ICP fails; anything else -> unknown.
Org: any ICP fits -> fit (icps = the fitting ones) · else any unknown -> doubtful + ⚠ (Rulebook E2) ·
else not_fit (reason = the deciding criterion + quote). Rulebook C exclusions -> not_fit without a page read.
No readable page at all -> stays unreviewed, retried after 3 days (Machine 2's unreadable rule)."""
import argparse, datetime, hashlib, json, os, re, sys
from zoneinfo import ZoneInfo

import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_shared", "orchestrator")); import paths  # the one file that knows every folder (2026-11-03)
ENG = paths.ROOT; MK = paths.MARKETING; HST = paths.HST
MASTER = paths.MASTER; QDIR = paths.runs("qualify")
SETP = paths.SETTINGS
S = paths.settings()
ROOT = paths.MASTER
CFG = S.get("qualify", {})
INBOX = paths.QUALIFY_DECISIONS; ORGS = paths.ORGS                 # 3_Qualify/ledgers/decisions.jsonl (was 3_Qualify/ledgers/decisions.jsonl)
LEDGER = paths.QUALIFY_LEDGER; ICPDIR = paths.ICP_DIR             # 3_Qualify/ledgers/ledger.jsonl: what was checked and when to re-check
TODAY = datetime.datetime.now(ZoneInfo("America/Denver")).date().isoformat()
EVENT_ICPS = {"ICP-001", "ICP-002", "ICP-003", "ICP-004", "ICP-006"}

def jl(p): return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()] if os.path.exists(p) else []
def ajl(p, rows):
    with open(p, "a", encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
def wj(p, o):
    tmp = p + ".tmp"; json.dump(o, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True); os.replace(tmp, p)
FOLD = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-", " ": " ", "…": "..."})
def norm(s): return re.sub(r"\s+", " ", str(s or "").translate(FOLD)).strip().lower()
def uid(url): return hashlib.sha1(norm(url).rstrip("/").encode()).hexdigest()[:16]
def plus_days(d, n): return (datetime.date.fromisoformat(d) + datetime.timedelta(days=n)).isoformat()

# ---------------------------------------------------------------- ICP criteria, read from the ICP files (section 1, 2, 3)
def icps():
    out = {}
    for f in sorted(os.listdir(ICPDIR)):
        m = re.match(r"(ICP-\d{3})-.*\.md$", f)
        if not m: continue
        t = open(os.path.join(ICPDIR, f), encoding="utf-8").read()
        st = (re.search(r"^status:\s*(\S+)", t, re.M) or [None, "?"])[1]
        mk = [x.strip() for x in ((re.search(r"^markets:\s*\[([^\]]*)\]", t, re.M) or [None, ""])[1]).split(",") if x.strip()]
        if not mk or st.upper() in ("RETIRED", "SUPERSEDED"): continue
        ft = re.search(r"\*\*Function test:\*\*\s*(.+)", t)
        s2 = re.search(r"^## 2\..*?(?=^## 3\.)", t, re.M | re.S); s3 = re.search(r"^## 3\..*?(?=^## 4\.)", t, re.M | re.S)
        musts = []
        for row in re.findall(r"^\|(.+)\|\s*$", s2.group(0) if s2 else "", re.M):
            cells = [c.strip() for c in row.split("|")]
            if len(cells) >= 2 and cells[0].lower() != "criterion" and cells[1].lower().startswith("must"): musts.append(cells[0])
        dq = [re.sub(r"\[\[([^\]|]+)(\|[^\]]*)?\]\]", r"\1", b).strip() for b in re.findall(r"^- (.+)$", s3.group(0) if s3 else "", re.M)]
        out[m[1]] = {"file": f, "status": st, "markets": mk, "function_test": ft[1].strip() if ft else None, "musts": musts, "disqualifiers": dq}
    return out

def ledger():
    last = {}
    for r in jl(LEDGER): last[r["org_id"]] = r
    return last

def evidence_hash(o):
    ev = sorted((e.get("name") or "", str(e.get("next_edition_date") or ""), e.get("url") or "") for e in o.get("events", []))
    return hashlib.sha1(json.dumps([sorted(o.get("domains", [])), ev], sort_keys=True).encode()).hexdigest()[:12]

# ---------------------------------------------------------------- next: pick tonight's orgs
def hs_slots(o):
    """Funded slots when the org is a Head Start grantee from the official list (its ICP-003 basis), else None."""
    b = str((o.get("icp_basis") or {}).get("ICP-003") or "")
    if "Head Start grantee list" not in b: return None
    m = re.search(r"\((\d[\d,]*) slots", b)
    return int(m.group(1).replace(",", "")) if m else 0


def cmd_next(a):
    rd = os.path.join(QDIR, a.run); os.makedirs(os.path.join(rd, "captures"), exist_ok=True)
    stp = os.path.join(rd, "state.json")
    if os.path.exists(stp) and not a.only:
        st = json.load(open(stp)); pend = [b for b in st["batches"] if b["status"] != "ingested"]
        print("RESUME run %s: %d of %d batches pending" % (a.run, len(pend), len(st["batches"])))
        for b in pend: print("BATCH %d  %s  ->  %s" % (b["k"], b["file"], b["result"]))
        return
    IC = icps(); L = ledger(); rows = jl(ORGS)
    machines = set(x.strip() for x in a.machines.split(",") if x.strip()) if getattr(a, "machines", None) else None
    only = set(x.strip() for x in a.only.split(",")) if a.only else None
    code_dec, pick = [], []
    for o in rows:
        oid = o["org_id"]
        if only is not None:
            if oid not in only: continue
        else:
            if o.get("referrer"): continue
            if set(o["icps"]) and set(o["icps"]) <= {"ICP-007", "ICP-008"}: continue
            lr = L.get(oid)
            if lr and lr.get("retry_after") and lr["retry_after"] > TODAY: continue
            changed = bool(lr) and lr.get("evidence_hash") != evidence_hash(o) and lr.get("decision") != "unreadable"
            # calendar re-read (Chris 2026-11-10): an OM-2 org whose best event is parked for next year was read before helpers
            # were told to record the WHOLE calendar — read it once more so a later event in range is not missed
            recal = (o.get("owner_machine") == "OM-2" and not o.get("threads") and bool(lr) and str(lr.get("date") or "") < "2026-11-11"
                     and "(F4)" in str((o.get("outreach") or {}).get("why") or "") and str((o.get("outreach") or {}).get("status") or "").startswith("queued"))
            if o["fit"]["status"] != "unreviewed" and not changed and not recal: continue
        ex = {k: v for k, v in (o.get("exclusions") or {}).items() if v}
        if ex and only is None:
            code_dec.append({"org_id": oid, "run": a.run, "decided": TODAY, "decision": "not_fit", "icps": o["icps"],
                             "reason": "excluded (Rulebook C): " + "; ".join("%s — %s" % (k, (v.get("why") if isinstance(v, dict) else v)) for k, v in sorted(ex.items()))[:300],
                             "by": "code (exclusion)", "evidence_hash": evidence_hash(o)})
            continue
        cand = [i for i in o["icps"] if i in IC] or sorted(IC)
        basis = " ".join(str(v) for v in (o.get("icp_basis") or {}).values()).lower()
        if basis and all(re.search(r"\(draft\)|name rule|first pass", str(v).lower()) for v in o["icp_basis"].values()):
            cand = sorted(IC)          # first-pass tags are guesses: judge against every active ICP (e.g. Head Start grantees tagged ICP-002 by name)
        if a.icps: cand = [x.strip() for x in a.icps.split(",") if x.strip() in IC]   # test runs: judge against these ICPs only
        if (o.get("runs_event") or o.get("events")) and not a.icps:   # an event owner may fit through an event ICP too
            cand = sorted(set(cand) | ({"ICP-004", "ICP-006"} & set(IC)))
        likely = o["owner_machine"] if o["owner_machine"] in ("OM-1", "OM-2") else ("OM-2" if (o.get("events") or o.get("runs_event")) else None)
        if machines and likely and likely not in machines: continue   # the night loop works only machines still under their minimum
        hs = hs_slots(o)
        base = (0 if any("discovery" in s for s in o.get("sources", [])) else 1 if o["owner_machine"] == "OM-2" else 2 if o["owner_machine"] == "OM-1" else 3,
                0 if o.get("events") else 1)
        # order (Chris 2026-10-31; ICP-003 "300+ slots first"): non-Head Start candidates first, then Head Start grantees largest funded slots first
        if machines == {"OM-2"}: base = (0 if (o.get("events") or o.get("runs_event")) else 1,) + base   # a conference-only pass: event owners first
        else: base = (0,) + base
        pr = ((0,) + base + (0, oid)) if hs is None else ((1, 0, 0, 0, -hs, oid))
        pick.append((pr, o, cand))
    pick.sort(key=lambda x: x[0])
    cap = a.cap or CFG.get("per_night", 120)
    pick = pick[:cap]
    bs = a.batch_size or CFG.get("batch_size", 6); batches = []
    for i in range(0, len(pick), bs):
        k = i // bs + 1; bf = os.path.join(rd, "batch_%d.jsonl" % k); rf = os.path.join(rd, "result_%d.jsonl" % k)
        with open(bf, "w", encoding="utf-8") as f:
            for _, o, cand in pick[i:i + bs]:
                f.write(json.dumps({"org_id": o["org_id"], "name": o["name"], "state": o["state"], "country": o.get("country"), "domains": o["domains"],
                    "current_icps": o["icps"], "known_events": [{k2: e.get(k2) for k2 in ("name", "url", "next_edition_date", "last_edition_date", "attendance", "cfp", "keynote_path")} for e in o.get("events", [])][:6],
                    "check_events": bool(o.get("events") or o.get("runs_event") or set(cand) & {"ICP-004", "ICP-006"}),
                    "candidate_icps": [{"icp": c, "function_test": IC[c]["function_test"], "musts": IC[c]["musts"], "disqualifiers": IC[c]["disqualifiers"]} for c in cand]},
                    ensure_ascii=False, sort_keys=True) + "\n")
        batches.append({"k": k, "file": bf, "result": rf, "orgs": [o["org_id"] for _, o, _ in pick[i:i + bs]], "status": "pending"})
    if code_dec:
        ajl(INBOX, code_dec)
        ajl(LEDGER, [{"org_id": d["org_id"], "run": a.run, "date": TODAY, "decision": d["decision"], "evidence_hash": d["evidence_hash"]} for d in code_dec])
    wj(stp, {"run": a.run, "created": TODAY, "cap": cap, "batches": batches, "code_decisions": len(code_dec), "test_icps": a.icps or None})
    print("RUN %s: %d orgs to read in %d batches (cap %d) · %d decided by code (Rulebook C exclusions)" % (a.run, len(pick), len(batches), cap, len(code_dec)))
    for b in batches: print("BATCH %d  %s  ->  %s" % (b["k"], b["file"], b["result"]))
    print("CAPTURES go in %s (python3 qualify.py capture --run %s FILE)" % (os.path.join(rd, "captures"), a.run))

# ---------------------------------------------------------------- the capture JavaScript (Browser pane)
KW = ["train", "coach", "referral", "professional development", "technical assistance", "t/ta", "provider", "child care", "childcare",
      "early childhood", "early learning", "early care", "conference", "institute", "summit", "symposium", "keynote", "speaker", "presenter",
      "call for", "proposal", "rfp", "attendee", "participants", "registration", "head start", "member", "association", "network",
      "staff", "director", "closed", "merg", "funding", "funded", "counties", "county", "statewide", "who should attend", "audience",
      "breakout", "workshop", "2026", "2027", "mission", "we are", "about us", "serve", "educators", "infant", "toddler", "preschool"]
JS = r"""(async () => { await new Promise(r => setTimeout(r, 1500)); const KW = %s;
 const B = document.body; const all = B ? (B.innerText || B.textContent || '') : '';
 const parts = all.split(/\n+|(?<=[.!?])\s+(?=[A-Z0-9])/).map(s => s.replace(/\s+/g,' ').trim()).filter(s => s.length > 3);
 const lines = []; const seen = new Set(); let n = 0;
 for (const p of parts) { const l = p.toLowerCase(); if (!KW.some(k => l.includes(k))) continue; const s = p.slice(0, 320);
   if (seen.has(s)) continue; seen.add(s); lines.push(s); n += s.length; if (n > %d) break; }
 return {url: location.href, requested: %s, title: document.title, chars: all.length, head: all.replace(/\s+/g,' ').trim().slice(0, 500), lines: lines,
         captured_at: new Date().toISOString()}; })()"""
VJS = r"""(async () => { await new Promise(r => setTimeout(r, 1500)); const Q = %s; const F = s => (s||'').replace(/[\u2018\u2019]/g,"'").replace(/[\u201c\u201d]/g,'"').replace(/[\u2013\u2014]/g,'-').replace(/\u00a0/g,' ').replace(/\u2026/g,'...').replace(/\s+/g,' ').trim().toLowerCase();
 const B = document.body; const all = B ? (B.innerText || B.textContent || '') : ''; const hay = F(all);
 return {url: location.href, requested: %s, title: document.title, chars: all.length, head: '', lines: Q.filter(q => hay.includes(F(q))),
         missing: Q.filter(q => !hay.includes(F(q))), captured_at: new Date().toISOString(), mode: 'verify'}; })()"""
def cmd_js(a):
    if a.quotes:   # compact capture: the page itself confirms each quote; only confirmed quotes are stored (lines)
        qs = json.load(open(a.quotes, encoding="utf-8")) if os.path.exists(a.quotes) else json.loads(a.quotes)
        print(VJS % (json.dumps(qs, ensure_ascii=False), json.dumps(a.url or ""))); return
    print(JS % (json.dumps(KW), CFG.get("capture_chars", 3500), json.dumps(a.url or "")))

def cmd_capture(a):
    rd = os.path.join(QDIR, a.run, "captures"); os.makedirs(rd, exist_ok=True); n = 0
    for line in open(a.file, encoding="utf-8"):
        if not line.strip(): continue
        c = json.loads(line)
        for k in ("url", "chars", "lines"):
            if k not in c: sys.exit("FAIL CLOSED: capture missing %s" % k)
        for u in {c["url"], c.get("requested") or c["url"]}:
            json.dump(c, open(os.path.join(rd, uid(u) + ".json"), "w", encoding="utf-8"), ensure_ascii=False); n += 1
    print("stored %d capture keys" % n)

def load_caps(run):
    rd = os.path.join(QDIR, run, "captures"); caps = {}
    if os.path.isdir(rd):
        for f in os.listdir(rd):
            if f.endswith(".json"):
                c = json.load(open(os.path.join(rd, f), encoding="utf-8")); caps[f[:-5]] = c
    return caps

def verified(url, quote, caps):
    """True if quote is on the captured live page (or in a vault file for vault: urls)."""
    q = norm(quote)
    if not q or len(q) < 8: return False
    if str(url).startswith("vault:"):
        p = os.path.join(HST, url[6:].lstrip("/"))
        return os.path.exists(p) and q in norm(open(p, encoding="utf-8", errors="ignore").read())
    c = caps.get(uid(url))
    if not c: return False
    hay = norm(c.get("head", "") + " \n " + " \n ".join(c.get("lines", [])))
    return q in hay

def readable(url, caps):
    if str(url).startswith("vault:"): return os.path.exists(os.path.join(HST, url[6:].lstrip("/")))
    c = caps.get(uid(url))
    return bool(c) and c.get("chars", 0) >= CFG.get("unreadable_min_chars", 300) and not re.search(r"access denied|403|404|not found|forbidden|just a moment|attention required|cloudflare|security verification|website expired|err_|page is unavailable|page not found", str(c.get("title", "")).lower())

# ---------------------------------------------------------------- decide
def ans(x, caps, log, what):
    a_ = str(x.get("answer") or x.get("hit") or "unknown").lower()
    if a_ not in ("yes", "no"): return "unknown"
    if verified(x.get("url"), x.get("quote"), caps): return a_
    log.append("unverified %s quote → unknown: %s" % (what, str(x.get("quote"))[:80])); return "unknown"

def decide(row, res, caps, supp=None):
    supp = supp or {}; log = []; per = {}
    for cand in row["candidate_icps"]:
        icp = cand["icp"]; R = (res.get("icps") or {}).get(icp) or {}
        musts = R.get("musts") or []; dqs = R.get("disqualifiers") or []
        mv = []
        for mtxt in cand["musts"]:
            x = next((m for m in musts if norm(m.get("criterion"))[:40] == norm(mtxt)[:40]), None) or {}
            v = ans(x, caps, log, icp + " must")
            if v == "yes" and supp.get((icp, norm(mtxt)[:40])) == "no": v = "unknown"; log.append("support check: quote does not support '%s'" % mtxt[:50])
            mv.append((mtxt, v, x))
        dv = [(d.get("text"), ans(dict(d, answer=d.get("hit")), caps, log, icp + " disqualifier"), d) for d in dqs]
        hit = [d for d in dv if d[1] == "yes"]
        fails = [m for m in mv if m[1] == "no"]
        if hit: per[icp] = ("fails", "disqualifier: %s — \"%s\" (%s)" % (hit[0][0], hit[0][2].get("quote", "")[:160], hit[0][2].get("url")))
        elif fails: per[icp] = ("fails", "must not met: %s — \"%s\" (%s)" % (fails[0][0], fails[0][2].get("quote", "")[:160], fails[0][2].get("url")))
        elif mv and all(m[1] == "yes" for m in mv): per[icp] = ("fits", "; ".join("%s — \"%s\"" % (m[0][:60], m[2].get("quote", "")[:120]) for m in mv))
        else: per[icp] = ("unknown", "unconfirmed: " + "; ".join(m[0][:60] for m in mv if m[1] != "yes"))
    fits = sorted(i for i, v in per.items() if v[0] == "fits")
    yes_some = {c["icp"] for c in row["candidate_icps"] for m in ((res.get("icps") or {}).get(c["icp"]) or {}).get("musts") or []
                if str(m.get("answer")).lower() == "yes" and verified(m.get("url"), m.get("quote"), caps)}
    unk_all = sorted(i for i, v in per.items() if v[0] == "unknown")
    unk = [i for i in unk_all if i in yes_some] or [i for i in unk_all if i in row["current_icps"]] or unk_all   # doubtful ICPs = the ones with real evidence
    if fits: dec, icps_, reason = "fit", fits, " | ".join("%s: %s" % (i, per[i][1]) for i in fits)
    elif unk: dec, icps_, reason = "doubtful", unk, " | ".join("%s: %s" % (i, per[i][1]) for i in unk)
    else: dec, icps_, reason = "not_fit", row["current_icps"], " | ".join("%s: %s" % (i, v[1]) for i, v in sorted(per.items()))
    # event facts: only verified fields are kept
    evs = []
    for e in res.get("events") or []:
        f = {"name": e.get("name"), "url": e.get("url")}
        def vq(field_quote, url=None): return verified(url or e.get("evidence_url") or e.get("url"), e.get(field_quote), caps)
        if e.get("next_edition_date") and vq("date_quote"): f["next_edition_date"] = e["next_edition_date"]; f["dated_on_own_site"] = e.get("dated_on_own_site")
        if e.get("last_edition_date") and vq("last_date_quote"): f["last_edition_date"] = e["last_edition_date"]
        if e.get("attendance") and vq("attendance_quote"): f["attendance"] = e["attendance"]
        if e.get("keynote_path") in ("yes", "no") and vq("keynote_quote"): f["keynote_path"] = e["keynote_path"]
        if e.get("breakout_only") == "yes" and vq("breakout_quote"): f["breakout_only"] = "yes"
        if e.get("keynote_announced") == "yes" and vq("keynote_announced_quote"): f["keynote_announced"] = "yes"; f["keynote_announced_quote"] = e.get("keynote_announced_quote")
        cf = e.get("cfp") or {}
        if (cf.get("deadline") or cf.get("opens") or cf.get("status")) and verified(cf.get("url") or e.get("url"), cf.get("quote"), caps):
            f["cfp"] = {"url": cf.get("url"), "opens": cf.get("opens"), "deadline": cf.get("deadline"), "status": cf.get("status"), "quote": cf.get("quote")}
        kr = e.get("keynote_request") or {}
        if kr.get("quote") and verified(kr.get("url") or e.get("url"), kr.get("quote"), caps): f["keynote_request"] = {"url": kr.get("url"), "quote": kr["quote"]}
        f["evidence_url"] = e.get("evidence_url") or e.get("url")
        if len(f) > 3: evs.append(f)
    return dec, icps_, reason, per, evs, log

def cmd_ingest(a):
    rd = os.path.join(QDIR, a.run); st = json.load(open(os.path.join(rd, "state.json")))
    b = next(x for x in st["batches"] if x["k"] == a.batch)
    rows = {r["org_id"]: r for r in jl(b["file"])}
    res = {r["org_id"]: r for r in jl(a.file)}
    missing = sorted(set(rows) - set(res))
    if missing: sys.exit("FAIL CLOSED: result has no row for %s" % ", ".join(missing))
    caps = load_caps(a.run); orgs = {o["org_id"]: o for o in jl(ORGS)}
    out, led = [], []
    for oid, row in rows.items():
        r = res[oid]
        urls = set(r.get("pages_read") or [])
        if not any(readable(u, caps) for u in urls):
            led.append({"org_id": oid, "run": a.run, "date": TODAY, "decision": "unreadable", "retry_after": plus_days(TODAY, 3), "evidence_hash": evidence_hash(orgs.get(oid, {}))})
            print("UNREADABLE %s — retry after 3 days" % row["name"]); continue
        dec, icps_, reason, per, evs, log = decide(row, r, caps)
        out.append({"org_id": oid, "run": a.run, "decided": TODAY, "decision": dec, "icps": icps_, "reason": reason[:900],
                    "per_icp": {k: {"verdict": v[0], "why": v[1][:400]} for k, v in per.items()}, "events": evs,
                    "pages_read": sorted(urls), "notes": (r.get("note") or "")[:300], "log": log[:12], "by": "qualify %s (verified quotes)" % a.run,
                    "evidence_hash": evidence_hash(orgs.get(oid, {}))})
        led.append({"org_id": oid, "run": a.run, "date": TODAY, "decision": dec, "evidence_hash": evidence_hash(orgs.get(oid, {})),
                    "retry_after": plus_days(TODAY, CFG.get("doubtful_recheck_days", 30)) if dec == "doubtful" else None})
        print("%-9s %s  %s" % (dec.upper(), row["name"], ",".join(icps_)))
    if st.get("test_icps"):   # an ICP test (judged against some ICPs only) never becomes a master-list decision
        ajl(os.path.join(rd, "test-decisions.jsonl"), out); print("TEST RUN (ICPs %s): decisions kept in the run folder only" % st["test_icps"])
    else:
        ajl(INBOX, out); ajl(LEDGER, led)
    json.dump(res, open(os.path.join(rd, "answers_%d.json" % a.batch), "w", encoding="utf-8"), ensure_ascii=False)
    b["status"] = "ingested"; wj(os.path.join(rd, "state.json"), st)
    print("batch %d ingested: %d decisions, %d unreadable" % (a.batch, len(out), len(led) - len(out)))

def cmd_support_items(a):
    rd = os.path.join(QDIR, a.run)
    for d in jl(INBOX):
        if d.get("run") != a.run or d["decision"] != "fit": continue
        for icp, v in d.get("per_icp", {}).items():
            if v["verdict"] == "fits":
                print(json.dumps({"org_id": d["org_id"], "icp": icp, "evidence": v["why"]}, ensure_ascii=False))

def cmd_support(a):
    """Haiku verdict lines {org_id, icp, supports: yes|no, why}; a 'no' re-decides that org as doubtful (latest inbox row wins)."""
    inbox = [d for d in jl(INBOX) if d.get("run") == a.run]
    latest = {d["org_id"]: d for d in inbox}
    add = []
    for v in jl(a.file):
        if str(v.get("supports")).lower() != "no": continue
        d = dict(latest[v["org_id"]]); pi = dict(d["per_icp"]); pi[v["icp"]] = {"verdict": "unknown", "why": "support check: " + str(v.get("why"))[:200]}
        fits = sorted(i for i, x in pi.items() if x["verdict"] == "fits")
        d.update(per_icp=pi, decision="fit" if fits else "doubtful", icps=fits or sorted(i for i, x in pi.items() if x["verdict"] == "unknown"),
                 reason=(d["reason"] + " | support check downgraded " + v["icp"])[:900], by=d["by"] + " + support check")
        latest[v["org_id"]] = d; add.append(d)
    ajl(INBOX, add); print("support check: %d org decisions revised" % len(add))

def cmd_set_date(a):
    s = json.load(open(SETP, encoding="utf-8")); s["as_of"] = a.date or TODAY; wj(SETP, s); print("as_of =", s["as_of"])

def cmd_stats(a):
    rows = jl(ORGS); from collections import Counter
    print("fit:", dict(Counter(o["fit"]["status"] for o in rows)))
    print("owner:", dict(Counter(o["owner_machine"] for o in rows)))
    print("OM-2 outreach:", dict(Counter((o.get("outreach") or {}).get("status", "-").split(" ")[0] for o in rows if o["owner_machine"] == "OM-2")))
    print("inbox decisions:", len(jl(INBOX)), "· ledger rows:", len(jl(LEDGER)))

def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("next"); p.add_argument("--run", required=True); p.add_argument("--cap", type=int); p.add_argument("--only", help="comma-separated org_ids (tests / manual)"); p.add_argument("--icps", help="judge only against these ICPs (10-org tests)"); p.add_argument("--batch-size", type=int)
    p.add_argument("--machines", help="night loop: only candidates that could route to these machines (comma list)")
    p = sp.add_parser("js"); p.add_argument("--url"); p.add_argument("--quotes", help="JSON list (or file) of exact quotes: print the VERIFY script (compact capture)")
    p = sp.add_parser("capture"); p.add_argument("--run", required=True); p.add_argument("file")
    p = sp.add_parser("ingest"); p.add_argument("--run", required=True); p.add_argument("--batch", type=int, required=True); p.add_argument("file")
    p = sp.add_parser("support-items"); p.add_argument("--run", required=True)
    p = sp.add_parser("support"); p.add_argument("--run", required=True); p.add_argument("file")
    p = sp.add_parser("set-date"); p.add_argument("--date")
    sp.add_parser("stats")
    a = ap.parse_args()
    {"next": cmd_next, "js": cmd_js, "capture": cmd_capture, "ingest": cmd_ingest, "support-items": cmd_support_items, "support": cmd_support,
     "set-date": cmd_set_date, "stats": cmd_stats}[a.cmd](a)
if __name__ == "__main__": main()
