#!/usr/bin/env python3
"""people.py -- FIND + VERIFY PEOPLE (Rulebook C, G, H incl. H6; Stage 6, Chris 2026-10-31).

The AI finds people on the org's own pages and copies what it sees; THIS SCRIPT checks and decides. An address counts only
if it character-matches an address on a CAPTURE of the org's own live page (made in the Browser pane with the JavaScript
this script prints) or appears in the org's own auto-reply in Gmail (H6). Zero guessed or pattern addresses.
Decisions go to ONE place, 4_People/ledgers/decisions.jsonl, which build_master.py reads (contacts + the ready recipient set).

  python3 people.py next --run RUN [--cap N] [--only id,id] [--machine OM-1|OM-2]   tonight's orgs -> batches (resumable)
  python3 people.py js [--url U]                 the capture JavaScript (emails on the page + text lines) for the Browser pane
  python3 people.py capture --run RUN FILE       store capture(s), one JSON object per line
  python3 people.py ingest --run RUN --batch K FILE   Gate 1 (provenance) + master-list checks per person -> run/pending
  python3 people.py sweep-items --run RUN        H7 ROSTER SWEEP: named people WITHOUT a published address, ≤5 per org by role relevance (one JSON line each)
  python3 people.py sweep --run RUN FILE         record the sweep results; promote ONLY Apollo Verified + ZeroBounce valid/catch-all + org-domain addresses
  python3 people.py apollo-items --run RUN       the people that passed Gate 1 and still need Apollo (one JSON line each)
  python3 people.py apollo --run RUN FILE        record Apollo verdicts (identity + validity + credits) per person
  python3 people.py decide --run RUN             assemble each org's recipient set (Rulebook G) -> 4_People/ledgers/decisions.jsonl (the one ledger)
  python3 people.py stats

H7 (Chris 2026-11-02, CAPA apollo-roster-sweep): a person NAMED on the org's own page but with no published address is looked up in
Apollo (≤5 per org, by role relevance, never padded). The returned address is a CANDIDATE (4_People/runs/<RUN>/sweep.jsonl +
4_People/ledgers/sweep-ledger.jsonl, never truth) until all three hold: Apollo email_status Verified · ZeroBounce valid (catch-all allowed,
flagged ⚠) · address on the org's own domain. Only then is the person promoted into pending.jsonl (source apollo-verified) and goes
through the same gates. A general inbox is never the To while relevant named people are still unlooked-up (G3).
GATES (code): 1 provenance -- the exact address is on a captured live page of the org (or its own auto-reply, H6);
2 identity -- Apollo: confirmed / not_in_apollo (proceed, flagged: the live page is the evidence) / departed (dropped, ⚠);
3 validity -- valid / catch_all / unknown proceed (catch-all and unknown flagged); ONLY a definite invalid holds (H4).
MASTER CHECKS: bounced / departed / do-not-contact addresses anywhere in the master list; a recipient whose domain belongs
to an existing client or excluded org (C4); a recipient whose domain belongs to ANOTHER org that already has a thread
(one thread per org, C2); Colorado orgs never reach this step (C5).
ASSEMBLY (Rulebook G): up to 4 people (1 To + up to 3 Cc), ranked by ROLE for the owning machine; named people with
personal addresses first; a generic inbox is To only when no named person has an address AND the staff page was read
(G4, CAPA 2026-10-30); a generic event inbox printed on the event page may be a Cc when there is room; greeting names
every named recipient (first names), never a pronoun."""
import argparse, datetime, hashlib, json, os, re, sys
from zoneinfo import ZoneInfo

import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_shared", "orchestrator")); import paths  # the one file that knows every folder (2026-11-03)
ENG = paths.ROOT; MK = paths.MARKETING
MASTER = paths.MASTER; PDIR = paths.runs("people")
S = paths.settings()
ROOT = paths.MASTER
CFG = S.get("people", {})
INBOX = paths.PEOPLE_DECISIONS; ORGS = paths.ORGS; GSTATE = paths.GMAIL_STATE   # 4_People/ledgers/decisions.jsonl: the ONE people ledger (decision + retry_after), 2026-11-03
LEDGER = INBOX
TODAY = datetime.datetime.now(ZoneInfo("America/Denver")).date().isoformat()
MAXR = CFG.get("max_recipients", 4)
GENERIC = set(CFG.get("generic_local_parts", []))
RANK = paths.mset("role_rank")            # per machine, from the machines block of the one settings file
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+'-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

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
def em(e): return str(e or "").strip().strip("<>.,;:()[]'\"`").lower()
def dom(e): return em(e).split("@")[-1] if "@" in str(e) else ""
def base_dom(d):
    d = (d or "").lower()
    if d.startswith("www."): d = d[4:]
    return d
# Rulebook B4 (Chris 2026-11-10, ENG-R012): one org, many email domains. Never pair a free-mail, shared-tenant or own domain.
PAIRS = paths.DOMAIN_PAIRS
NEVER_PAIR = (set((S.get("draft") or {}).get("free_mail_domains") or []) | {base_dom(x) for v in paths.mset("shared_tenant_domains").values() for x in (v or [])}
              | {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com", "icloud.com", "comcast.net", "att.net", "msn.com", "live.com", "me.com",
                 "chrisdanilo.com", "googlemail.com", "google.com", "bcc.na2.hubspot.com"})
def pairs_known():
    """FINAL verdicts only (same / not-same). A candidate is not final: it waits for the Apollo check."""
    k = {}
    for r in jl(PAIRS):
        if r.get("verdict") in ("same", "not-same"): k[tuple(sorted((r["a"], r["b"])))] = r
    return k
def pairs_candidates():
    k = {}
    for r in jl(PAIRS):
        if r.get("verdict") == "candidate": k.setdefault(tuple(sorted((r["a"], r["b"]))), r)
    return k
def same_dom(d, doms): return any(d == base_dom(x) or d.endswith("." + base_dom(x)) or base_dom(x).endswith("." + d) for x in doms if x)
def is_generic(e, flag=None):
    if flag is True: return True
    lp = em(e).split("@")[0]
    return lp in GENERIC or bool(re.match(r"^(info|events?|conference|registration|training|admin|office)[._-]", lp))
_TITLES = r"(?:very\s+rev(?:erend)?|rt\.?\s+rev(?:erend)?|most\s+rev(?:erend)?|rev(?:erend)?|dr|mr|mrs|ms|mx|miss|prof(?:essor)?|fr|father|sr|sister|br|brother|rabbi|pastor|hon|honorable|msgr|deacon|dcn)"
def first_name(n):
    """Fallback only (Chris 2026-11-10, Issue 4): the helper records how the person goes by (greeting_name). When it did not,
    strip every leading title ('Very Rev.', 'Dr.', 'Sister') and take the first word."""
    n = str(n or "").strip()
    while True:
        m = re.match(r"^%s\.?\s+" % _TITLES, n, flags=re.I)
        if not m: break
        n = n[m.end():]
    f = n.split()[0].strip(",") if n.split() else ""
    return f.title() if f.isupper() and len(f) > 1 else f
def greet_name(p):
    """The name to greet a person by. Root rule (old Machine 1, U2/recipient_name_evidence; Chris 2026-11-10): the helper who reads
    the page records the name the person GOES BY, exactly as printed (a nickname in quotes or brackets wins). It is used only if it
    is really part of the printed name/quote; otherwise the title-stripping fallback is used and the draft is flagged."""
    g = str((p or {}).get("greeting_name") or "").strip().strip(",")
    hay = " ".join(str((p or {}).get(k) or "") for k in ("name", "quote"))
    if g and not re.match(r"^%s\.?$" % _TITLES, g, flags=re.I) and re.search(r"(?<![A-Za-z])%s(?![A-Za-z])" % re.escape(g), hay, flags=re.I):
        return g, True
    return first_name((p or {}).get("name")), False

# ---------------------------------------------------------------- master-list indexes (C2, C4, contact status)
def indexes(orgs):
    status, thread_dom, excl_dom = {}, {}, {}
    order = {"active": 0, "departed": 1, "bounced": 2, "do_not_contact": 3}
    for o in orgs:
        for c in o.get("contacts", []):
            s = c.get("status") or "active"
            if order.get(s, 0) > order.get(status.get(c["email"], "active"), 0): status[c["email"]] = s
        if o.get("threads"):
            for d in o.get("domains", []): thread_dom.setdefault(base_dom(d), o["org_id"])
        ex = sorted(k for k, v in (o.get("exclusions") or {}).items() if v)
        if ex:
            for d in o.get("domains", []): excl_dom.setdefault(base_dom(d), (o["org_id"], ex))
            for c in o.get("contacts", []):   # B4 patch 1 (Chris 2026-11-10): a client / excluded org's own contacts' domains are its domains too
                cd = base_dom(dom(c.get("email")))
                if cd and cd not in NEVER_PAIR: excl_dom.setdefault(cd, (o["org_id"], ex))
    return status, thread_dom, excl_dom

def eligible(o, redo=False):
    """Fit or doubtful, owned by a machine, no thread yet, no exclusion; OM-2 only when outreach is open now (Rulebook F).
    redo=True (Chris 2026-11-04, `next --only … --redo`): an org whose only threads are UNSENT Email 1 drafts may be re-worked, so the
    draft can be rebuilt with the new people rules. Any thread with a sent message still makes the org ineligible."""
    if o.get("referrer"): return False
    if o.get("threads") and not (redo and all(not (t.get("messages_sent") or []) for t in o["threads"])): return False
    if o["fit"]["status"] not in ("fit", "doubtful"): return False
    if o.get("owner_machine") not in ("OM-1", "OM-2"): return False
    if any(v for v in (o.get("exclusions") or {}).values()): return False
    if str(o.get("state") or "").upper() in ("CO", "COLORADO"): return False
    if o["owner_machine"] == "OM-2" and not str((o.get("outreach") or {}).get("status") or "").startswith("open"): return False
    return True

# ---------------------------------------------------------------- next
def cmd_next(a):
    rd = os.path.join(PDIR, a.run); os.makedirs(os.path.join(rd, "captures"), exist_ok=True)
    stp = os.path.join(rd, "state.json")
    if os.path.exists(stp):
        st = json.load(open(stp)); pend = [b for b in st["batches"] if b["status"] != "ingested"]
        print("RESUME run %s: %d of %d batches pending" % (a.run, len(pend), len(st["batches"])))
        for b in pend: print("BATCH %d  %s  ->  %s" % (b["k"], b["file"], b["result"]))
        return
    rows = jl(ORGS); led = {}
    for r in jl(LEDGER): led[r["org_id"]] = r
    only = [x.strip() for x in a.only.split(",")] if a.only else None
    pick = []
    for o in rows:
        if only is not None and o["org_id"] not in only: continue
        if not eligible(o, redo=bool(getattr(a, "redo", False) and only is not None)): continue
        if a.machine and o["owner_machine"] not in [x.strip() for x in a.machine.split(",")]: continue
        lr = led.get(o["org_id"])
        if only is None and lr and getattr(a, "night", None) and str(lr.get("run") or "").startswith(a.night + "-p"): continue   # already worked earlier tonight
        if only is None and lr and (lr.get("decision") == "ready" or (lr.get("retry_after") or "") > TODAY): continue
        pr = (0 if o["owner_machine"] == "OM-2" else 1, 0 if o["fit"]["status"] == "fit" else 1, o["org_id"])
        pick.append((pr, o))
    pick.sort(key=lambda x: x[0])
    if only is not None: pick.sort(key=lambda x: only.index(x[1]["org_id"]))
    cap = a.cap or CFG.get("per_night", 40); pick = pick[:cap]
    bs = a.batch_size or CFG.get("batch_size", 5); batches = []
    for i in range(0, len(pick), bs):
        k = i // bs + 1; bf = os.path.join(rd, "batch_%d.jsonl" % k); rf = os.path.join(rd, "result_%d.jsonl" % k)
        with open(bf, "w", encoding="utf-8") as f:
            for _, o in pick[i:i + bs]:
                evs = [{k2: e.get(k2) for k2 in ("name", "url", "edition_date", "cfp", "outreach_status")} for e in o.get("events", [])
                       if str(e.get("outreach_status") or "").startswith("open")] or [{k2: e.get(k2) for k2 in ("name", "url", "edition_date", "cfp")} for e in o.get("events", [])][:3]
                f.write(json.dumps({"org_id": o["org_id"], "name": o["name"], "state": o.get("state"), "domains": o.get("domains", []), "domain_hint": o.get("domain_hint"),
                    "machine": o["owner_machine"], "icps": o.get("icps", []), "fit": o["fit"]["status"], "events": evs[:4],
                    "known_contacts": [{k2: c.get(k2) for k2 in ("name", "role", "email", "evidence_url", "status")} for c in o.get("contacts", [])][:8],
                    "role_order": RANK.get(o["owner_machine"], [])}, ensure_ascii=False, sort_keys=True) + "\n")
        batches.append({"k": k, "file": bf, "result": rf, "orgs": [o["org_id"] for _, o in pick[i:i + bs]], "status": "pending"})
    wj(stp, {"run": a.run, "created": TODAY, "cap": cap, "batches": batches})
    print("RUN %s: %d orgs in %d batches (cap %d)" % (a.run, len(pick), len(batches), cap))
    for b in batches: print("BATCH %d  %s  ->  %s" % (b["k"], b["file"], b["result"]))
    print("CAPTURES: python3 people.py capture --run %s FILE" % a.run)

# ---------------------------------------------------------------- capture JavaScript (Browser pane)
JS = r"""(async () => { await new Promise(r => setTimeout(r, 1500));
 const dec = h => { try { const k = parseInt(h.substr(0,2),16); let s=''; for (let i=2;i<h.length;i+=2) s += String.fromCharCode(parseInt(h.substr(i,2),16)^k); return s; } catch(e) { return ''; } };
 const B = document.body; const all = B ? (B.innerText || B.textContent || '') : ''; const emails = new Set();
 document.querySelectorAll('a[href^="mailto:"]').forEach(a => { const v = decodeURIComponent(a.getAttribute('href').slice(7).split('?')[0]).trim(); if (v) emails.add(v); });
 document.querySelectorAll('[data-cfemail]').forEach(e => { const v = dec(e.getAttribute('data-cfemail')); if (v) emails.add(v); });
 (all.match(/[A-Za-z0-9._%%+'-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g) || []).forEach(v => emails.add(v));
 const parts = all.split(/\n+/).map(s => s.replace(/\s+/g,' ').trim()).filter(s => s.length > 1);
 const RK = /@|director|coordinator|manager|president|ceo|chair|executive|dean|specialist|administrator|lead|officer|conference|speaker|presenter|proposal|contact|staff|team|registrar|planner|event/i;
 const keep = new Set(); parts.forEach((p, i) => { if (RK.test(p)) { for (let j = Math.max(0, i-2); j <= Math.min(parts.length-1, i+2); j++) keep.add(j); } });
 const lines = []; let n = 0; for (const i of [...keep].sort((a,b)=>a-b)) { const s = parts[i].slice(0, 200); lines.push(s); n += s.length; if (n > %d) break; }
 return {url: location.href, requested: %s, title: document.title, chars: all.length, emails: [...emails].slice(0, 400), lines: lines,
         captured_at: new Date().toISOString()}; })()"""
VJS = r"""(async () => { await new Promise(r => setTimeout(r, 1500)); const Q = %s;
 const dec = h => { try { const k = parseInt(h.substr(0,2),16); let s=''; for (let i=2;i<h.length;i+=2) s += String.fromCharCode(parseInt(h.substr(i,2),16)^k); return s; } catch(e) { return ''; } };
 const F = s => (s||'').replace(/[\u2018\u2019]/g,"'").replace(/[\u201c\u201d]/g,'"').replace(/[\u2013\u2014]/g,'-').replace(/\u00a0/g,' ').replace(/\u2026/g,'...').replace(/\s+/g,' ').trim().toLowerCase();
 const B = document.body; const all = B ? (B.innerText || B.textContent || '') : ''; const hay = F(all); const emails = new Set();
 document.querySelectorAll('a[href^="mailto:"]').forEach(a => { const v = decodeURIComponent(a.getAttribute('href').slice(7).split('?')[0]).trim(); if (v) emails.add(v); });
 document.querySelectorAll('[data-cfemail]').forEach(e => { const v = dec(e.getAttribute('data-cfemail')); if (v) emails.add(v); });
 (all.match(/[A-Za-z0-9._%%+'-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g) || []).forEach(v => emails.add(v));
 return {url: location.href, requested: %s, title: document.title, chars: all.length, emails: [...emails].slice(0, 400),
         lines: Q.filter(q => hay.includes(F(q))), missing: Q.filter(q => !hay.includes(F(q))), mode: 'verify', captured_at: new Date().toISOString()}; })()"""
def cmd_js(a):
    """Scan mode (default): every address on the page + the text lines near names/titles (to read and choose people).
    Verify mode (--quotes JSON list or file): every address on the page + ONLY the chosen quotes the page itself confirms --
    the compact capture that gets stored (the page, not the helper, vouches for each line)."""
    if a.quotes:
        qs = json.load(open(a.quotes, encoding="utf-8")) if os.path.exists(a.quotes) else json.loads(a.quotes)
        print(VJS % (json.dumps(qs, ensure_ascii=False), json.dumps(a.url or ""))); return
    print(JS % (CFG.get("capture_chars", 5000), json.dumps(a.url or "")))

def cmd_capture(a):
    rd = os.path.join(PDIR, a.run, "captures"); os.makedirs(rd, exist_ok=True); n = 0
    for line in open(a.file, encoding="utf-8"):
        if not line.strip(): continue
        c = json.loads(line)
        for k in ("url", "chars", "lines", "emails"):
            if k not in c: sys.exit("FAIL CLOSED: capture missing %s" % k)
        for u in {c["url"], c.get("requested") or c["url"]}:
            json.dump(c, open(os.path.join(rd, uid(u) + ".json"), "w", encoding="utf-8"), ensure_ascii=False); n += 1
    print("stored %d capture keys" % n)

def load_caps(run):
    rd = os.path.join(PDIR, run, "captures"); caps = {}
    if os.path.isdir(rd):
        for f in os.listdir(rd):
            if f.endswith(".json"): caps[f[:-5]] = json.load(open(os.path.join(rd, f), encoding="utf-8"))
    return caps

def cap_of(url, caps): return caps.get(uid(url)) if url else None
def own_page(url, domains):
    h = base_dom(re.sub(r"^https?://", "", str(url or "")).split("/")[0])
    return any(h == base_dom(d) or h.endswith("." + base_dom(d)) for d in domains)

def provenance(p, org, caps, gstate):
    """Gate 1. Returns (ok, why). The exact address must be on a captured live page of the org's own site, or in the org's own
    auto-reply (H6). Emails on third-party pages (e.g. an event platform the org uses) count only if that page was captured and
    the address's domain is the org's own domain."""
    e = em(p.get("email"))
    if not e or "@" not in e: return False, "no address"
    if p.get("source") == "autoreply":
        t = (gstate.get("threads") or {}).get(str(p.get("thread_id")) or "") or {}
        blob = norm(json.dumps(t.get("auto") or []))
        if e in blob and any(dom(e) == base_dom(d) or dom(e).endswith("." + base_dom(d)) for d in org["domains"]):
            return True, "org's own auto-reply (H6)"
        return False, "address not in that thread's auto-reply"
    c = cap_of(p.get("evidence_url"), caps)
    if not c: return False, "evidence page not captured"
    if c.get("chars", 0) < 200 or re.search(r"page not found|404|access denied|forbidden|website expired", str(c.get("title", "")).lower()):
        return False, "evidence page unreadable"
    found = {em(x) for x in c.get("emails", [])}
    if e not in found: return False, "address not on the captured page (character match failed)"
    if not own_page(c.get("url") or p.get("evidence_url"), org["domains"]) and not any(dom(e) == base_dom(d) or dom(e).endswith("." + base_dom(d)) for d in org["domains"]):
        return False, "page and address are both off the org's own domain"
    return True, "on live page %s" % (c.get("url") or p.get("evidence_url"))

def quote_ok(p, caps):
    """The name/role quote must be on the same capture (keeps names and titles honest)."""
    q = norm(p.get("quote"))
    if not q: return False
    c = cap_of(p.get("evidence_url"), caps)
    return bool(c) and q in norm(" \n ".join(c.get("lines", [])))

# ---------------------------------------------------------------- ingest (Gate 1 + master checks)
def self_name_of(r, org, caps):
    """The org's own name as printed on its own site (Chris 2026-11-10, Issue 4 — same rule as the qualify step). Recorded here too, so every
    org gets it the night it is drafted: kept only if the quote is on the capture and contains the name; short name checked against the web address."""
    sn = r.get("self_name") or {}; out = {}
    for k in ("short", "formal"):
        v = str(sn.get(k) or "").strip()
        if v and norm(v) in norm(sn.get(k + "_quote")) and quote_ok({"quote": sn.get(k + "_quote"), "evidence_url": sn.get("url")}, caps): out[k] = v
    if not out: return None
    out["url"] = sn.get("url")
    if out.get("short"):
        stems = {base_dom(d).split(".")[0] for d in (org.get("domains") or []) if d}
        sh = re.sub(r"[^a-z0-9]", "", out["short"].lower())
        out["domain_match"] = any(sh and (sh in st or (len(sh) >= 4 and st.startswith(sh[:4]))) for st in stems)
    return out

def cmd_ingest(a):
    rd = os.path.join(PDIR, a.run); st = json.load(open(os.path.join(rd, "state.json")))
    b = next(x for x in st["batches"] if x["k"] == a.batch)
    rows = {r["org_id"]: r for r in jl(b["file"])}; res = {r["org_id"]: r for r in jl(a.file)}
    missing = sorted(set(rows) - set(res))
    if missing: sys.exit("FAIL CLOSED: result has no row for %s" % ", ".join(missing))
    caps = load_caps(a.run); orgs = jl(ORGS); byid = {o["org_id"]: o for o in orgs}
    gstate = json.load(open(GSTATE, encoding="utf-8")) if os.path.exists(GSTATE) else {}
    status, thread_dom, excl_dom = indexes(orgs)
    out = []
    for oid, row in rows.items():
        r = res[oid]; org = byid[oid]; people = []
        found_dom = None
        if not org.get("domains") and r.get("org_domain"):               # 2026-11-03: the helper found the org's own site
            cand = base_dom(norm(r["org_domain"]).replace("https://", "").replace("http://", "").split("/")[0])
            flat = lambda s: " ".join(re.sub(r"[^a-z0-9]+", " ", norm(s)).split())
            words = " ".join(flat(org.get("name") or row.get("name")).split()[:3])
            on_dom = [c_ for c_ in caps.values() if own_page(c_.get("url"), [cand])]
            for c_ in on_dom:
                if words and words in flat(c_.get("title", "") + " " + " ".join(c_.get("lines") or [])):
                    found_dom = cand; break
            if not found_dom and len(on_dom) >= 2: found_dom = cand   # 2026-11-04: the helper captured 2+ pages on its confirmed site
            if found_dom: org = dict(org, domains=[found_dom])
        for p in (r.get("people") or [])[:12]:
            e = em(p.get("email")); ok, why = provenance(p, org, caps, gstate); drop = None
            if ok:
                d = dom(e)
                if status.get(e) in ("bounced", "departed", "do_not_contact"): drop = "address is %s in the master list" % status[e]
                elif d in excl_dom and excl_dom[d][0] != oid: drop = "recipient domain belongs to an excluded org (%s: %s) — Rulebook C4" % (excl_dom[d][0], ",".join(excl_dom[d][1]))
                elif d in thread_dom and thread_dom[d] != oid: drop = "recipient domain belongs to %s, which already has a thread — one thread per org (C2)" % thread_dom[d]
            people.append({"name": (p.get("name") or "").strip() or None, "greeting_name": p.get("greeting_name"), "role": p.get("role"), "role_key": p.get("role_key") or "other_staff",
                           "email": e or None, "generic": is_generic(e, p.get("generic")) if e else False, "generic_event_inbox": bool(p.get("generic_event_inbox")),
                           "evidence_url": p.get("evidence_url"), "quote": p.get("quote"), "quote_verified": quote_ok(p, caps),
                           "source": p.get("source") or "page", "thread_id": p.get("thread_id"),
                           "gate1": "pass" if ok else "fail", "gate1_why": why, "dropped": drop})
        # E1.8 restored (Rulebook B4, Chris 2026-11-10): record BOTH the website domain and the mail domain(s) — even when identical.
        web = sorted({base_dom(d) for d in (org.get("domains") or []) if d})
        mail = sorted({base_dom(dom(p["email"])) for p in people if p["email"] and p["gate1"] == "pass" and p["source"] in ("page", "autoreply")} - NEVER_PAIR)
        e18 = {"website": web, "mail": mail, "pairs": [], "hold": None}
        for d in mail:
            if not web or same_dom(d, web): continue
            other = thread_dom.get(d) if thread_dom.get(d) not in (None, oid) else (excl_dom[d][0] if d in excl_dom and excl_dom[d][0] != oid else None)
            ev = next((p["evidence_url"] for p in people if p["email"] and dom(p["email"]) == d and p["gate1"] == "pass"), None)
            e18["pairs"].append({"a": web[0], "b": d, "proof": ev, "other_org": other})
            if other:   # the old de-dup check's HOLD: this org is only partly on record — held until the Apollo check (step 7b) answers
                e18["hold"] = "E1.8 partial match: an address on this org's own page uses %s, which belongs to %s on the master list" % (d, other)
        if e18["pairs"]:
            known = pairs_known()
            # 2026-11-10 replay: association pages print volunteers' DAY-JOB addresses (Nevada Registry -> washoeschools.net), so an
            # address on the page is a CANDIDATE, never proof by itself. Apollo (step 7b, same night) confirms before any join.
            cand = pairs_candidates()
            new = [dict(date=TODAY, run=a.run, org_id=oid, a=pr["a"], b=pr["b"], method="E1.8", verdict="candidate", proof="address printed on the org's own page: %s" % pr["proof"])
                   for pr in e18["pairs"] if tuple(sorted((pr["a"], pr["b"]))) not in known and tuple(sorted((pr["a"], pr["b"]))) not in cand]
            if new: ajl(PAIRS, new); print("  E1.8 candidate for the Apollo check: %s" % ", ".join("%s = %s" % (x["a"], x["b"]) for x in new))
        named_wo_email = [{"name": n["name"].strip(), "role": n.get("role"), "role_key": n.get("role_key") or guess_role_key(n.get("role")),
                           "greeting_name": n.get("greeting_name"), "evidence_url": n.get("evidence_url"), "quote": n.get("quote")}
                          for n in (r.get("named_without_email") or []) if n.get("name")][:8]
        out.append({"org_id": oid, "machine": row["machine"], "name": row["name"], "fit": row["fit"], "domain_discovered": found_dom, "e18": e18, "self_name": self_name_of(r, org, caps),
                    "pages_read": sorted(set(r.get("pages_read") or [])), "staff_page_read": bool(r.get("staff_page_read")),
                    "roster_searched": bool(r.get("roster_searched")), "named_without_email": named_wo_email, "people": people,
                    "note": (r.get("note") or "")[:300]})
        print("%-40s people %d · gate1 pass %d · dropped %d" % ((row.get("name") or row.get("org_id") or "?")[:40], len(people), sum(p["gate1"] == "pass" for p in people), sum(bool(p["dropped"]) for p in people)))
    ajl(os.path.join(rd, "pending.jsonl"), out)
    b["status"] = "ingested"; wj(os.path.join(rd, "state.json"), st)

def pending(run):
    last = {}
    for r in jl(os.path.join(PDIR, run, "pending.jsonl")): last[r["org_id"]] = r
    return last

def pkey(oid, e): return "%s|%s" % (oid, e)


# ---------------------------------------------------------------- H7 roster sweep (Chris 2026-11-02)
SWEEP_LEDGER = paths.SWEEP_LEDGER       # every lookup ever made: org|name -> result (never paid for twice)
SWEEP_MAX = CFG.get("sweep_max_per_org", 5)
ROLE_WORDS = [("cfp_contact", ("call for proposal", "proposal", "speaker", "cfp", "rfp")), ("event_contact", ("conference", "event", "summit", "symposium", "institute", "registration")),
              ("executive_director", ("executive director", "chief executive", "ceo", "president", "superintendent", "head of school", "founder", "owner")),
              ("pd_director", ("professional development", "professional learning", "training", "learning", "workforce", "education director", "director of education", "quality")),
              ("coaching_manager", ("coach", "mentor", "technical assistance", "ta ")), ("program_director", ("program", "programme", "early childhood", "child care", "childcare", "head start", "early learning", "services", "operations")),
              ("event_dept_director", ("membership", "communications", "outreach", "engagement", "community")), ("other_leader", ("director", "vice president", "vp", "chief", "manager", "coordinator", "lead", "specialist", "officer"))]
def guess_role_key(role):
    t = norm(role)
    if not t: return "other_staff"
    for k, words in ROLE_WORDS:
        if any(w in t for w in words): return k
    return "other_staff"

def skey(oid, name): return "%s|%s" % (oid, norm(name))
def sweep_ledger():
    led = {}
    for r in jl(SWEEP_LEDGER): led[r["key"]] = r
    return led
def relevant_unpublished(r, machine):
    """Named-without-email people of a pending org, ranked by role for the owning machine, capped at SWEEP_MAX (never padded)."""
    rank = {k: i for i, k in enumerate(RANK.get(machine, []))}
    have = {norm(p.get("name")) for p in r.get("people") or [] if p.get("name") and p.get("email")}
    cand = [n for n in (r.get("named_without_email") or []) if n.get("name") and norm(n["name"]) not in have]
    cand.sort(key=lambda n: (rank.get(n.get("role_key") or guess_role_key(n.get("role")), 99), norm(n["name"])))
    return cand[:SWEEP_MAX], cand[SWEEP_MAX:]

# ---------------------------------------------------------------- roster search (Chris 2026-11-10, Issue 1): an org whose own pages name NOBODY
ROSTER_LEDGER = os.path.join(os.path.dirname(SWEEP_LEDGER), "roster-search-ledger.jsonl")
ROSTER_TITLES = {"OM-2": ["conference", "events", "professional development", "executive director", "program director"],
                 "OM-1": ["professional development", "training", "executive director", "program director", "coaching"]}
def cmd_roster_items(a):
    """Orgs read tonight whose own pages named nobody at all (no person, with or without an address) and whose web address is known: Apollo
    people search (FREE, no emails) by that domain finds up to 5 people by role. They join the org's named-without-address list and go through
    the normal H7 sweep (Apollo Verified + ZeroBounce + the org's own domain). One search per org+domain, ever."""
    led = {r["key"] for r in jl(ROSTER_LEDGER)}; orgs = {o["org_id"]: o for o in jl(ORGS)}; n = 0
    for oid, r in sorted(pending(a.run).items()):
        if any(p.get("name") for p in r.get("people") or []) or r.get("named_without_email"): continue
        doms = [d for d in (orgs.get(oid, {}).get("domains") or ([r["domain_discovered"]] if r.get("domain_discovered") else [])) if d]
        if not doms: continue
        k = "%s|%s" % (oid, base_dom(doms[0]))
        if k in led: continue
        print(json.dumps({"key": k, "org_id": oid, "org_name": r["name"], "machine": r["machine"], "domain": base_dom(doms[0]),
                          "titles": ROSTER_TITLES.get(r["machine"], ROSTER_TITLES["OM-1"])}, ensure_ascii=False)); n += 1
    print("# roster items: %d (orgs whose pages named nobody; one free Apollo people search each)" % n, file=sys.stderr)

def cmd_roster(a):
    """Input lines {key, org_id, people: [{name, first_name, title, organization_domain}]}, exactly as Apollo returned them. Only people whose
    Apollo organization is on the searched domain are kept, up to SWEEP_MAX by role; they are added as named-without-address."""
    rd = os.path.join(PDIR, a.run); pend = pending(a.run); newrows, led = [], []
    for x in jl(a.file):
        oid = x.get("org_id"); r = pend.get(oid)
        if not r: continue
        dom_ = (x.get("key") or "|").split("|", 1)[1]
        keep = []
        for p in x.get("people") or []:
            od = base_dom(str(p.get("organization_domain") or ""))
            if not p.get("name") or (od and od != dom_): continue
            keep.append({"name": p["name"].strip(), "greeting_name": (p.get("first_name") or "").strip() or None, "role": p.get("title"),
                         "role_key": guess_role_key(p.get("title")), "evidence_url": None, "source": "apollo-roster"})
        rank = {k: i for i, k in enumerate(RANK.get(r["machine"], []))}
        keep.sort(key=lambda n: (rank.get(n["role_key"], 99), norm(n["name"])))
        keep = keep[:SWEEP_MAX]
        led.append({"key": x.get("key"), "org_id": oid, "date": TODAY, "run": a.run, "found": len(keep)})
        if keep:
            r2 = dict(r, named_without_email=keep); newrows.append(r2)
            print("ROSTER %s: %d people (%s)" % (r["name"], len(keep), ", ".join("%s — %s" % (k["name"], k["role"]) for k in keep)))
        else: print("ROSTER %s: nobody on %s in Apollo" % (r["name"], dom_))
    if newrows: ajl(os.path.join(rd, "pending.jsonl"), newrows)
    ajl(ROSTER_LEDGER, led)

def cmd_sweep_items(a):
    led = sweep_ledger(); orgs = {o["org_id"]: o for o in jl(ORGS)}; n = 0
    for oid, r in sorted(pending(a.run).items()):
        pick, deferred = relevant_unpublished(r, r["machine"])
        for p in pick:
            k = skey(oid, p["name"])
            if k in led: continue
            doms = orgs.get(oid, {}).get("domains") or []
            if not doms and r.get("domain_discovered"): doms = [r["domain_discovered"]]   # CAPA 2026-11-11: domain confirmed at ingest tonight
            print(json.dumps({"key": k, "org_id": oid, "org_name": r["name"], "machine": r["machine"], "domain": doms[0] if doms else None, "domains": doms,
                              "name": p["name"], "role": p.get("role"), "role_key": p.get("role_key")}, ensure_ascii=False)); n += 1
    print("# sweep items: %d (H7: ≤%d per org by role; people already in 4_People/ledgers/sweep-ledger.jsonl are not re-queried)" % (n, SWEEP_MAX), file=sys.stderr)

APOLLO_VERIFIED = {"verified"}
def sweep_verdict(v, org_domains):
    """Returns (promote: bool, result: resolved|held|queried-null, why, validity)."""
    e = em(v.get("email"))
    if not v.get("found") or not e: return False, "queried-null", "Apollo found no address for this person", None
    st = str(v.get("email_status") or "").strip().lower()
    if st not in APOLLO_VERIFIED: return False, "held", "Apollo email_status is '%s', not Verified — candidate only (H7)" % (st or "empty"), None
    zb = VALID.get(str(v.get("zerobounce") or v.get("validator_status") or "").strip().lower(), "unknown")
    if zb == "invalid": return False, "held", "ZeroBounce says invalid (H4)", "invalid"
    bd = {base_dom(d) for d in (org_domains or []) if d}
    if zb == "unknown":
        # Interim (Chris 2026-11-09, until his ZeroBounce account exists): the validator cannot run unattended, so an Apollo-Verified
        # address on the org's own domain is promoted FLAGGED instead of held. Flip people.apollo.zerobounce_interim_skip to false to restore H7.
        if (CFG.get("apollo") or {}).get("zerobounce_interim_skip") and base_dom(dom(e)) in bd:
            return True, "resolved", "Apollo Verified + org domain — ZeroBounce NOT run (interim rule, Chris 2026-11-09) ⚠", "unknown"
        return False, "held", "ZeroBounce result missing or unknown — H7 needs valid or catch-all", "unknown"
    if base_dom(dom(e)) not in bd: return False, "held", "address domain %s is not the org's own domain (%s)" % (dom(e), ", ".join(sorted(bd)) or "none on file"), zb
    return True, "resolved", "Apollo Verified + ZeroBounce %s + org domain" % zb, zb

def cmd_sweep(a):
    """Lines: {key, found, email, email_status (Apollo raw), apollo_title, apollo_org_domain, zerobounce (raw), credits_spent}."""
    rd = os.path.join(PDIR, a.run); pend = pending(a.run); orgs = {o["org_id"]: o for o in jl(ORGS)}
    rows = jl(a.file); out, promoted, led = [], {}, []
    for v in rows:
        if "key" not in v or "|" not in v["key"]: sys.exit("FAIL CLOSED: bad sweep line %s" % v)
        oid = v.get("org_id") or v["key"].split("|", 1)[0]; r = pend.get(oid)   # 2026-11-08: prefer the explicit org_id — an org_id that itself contains "|" (a bad id) breaks the key split
        if not r: sys.exit("FAIL CLOSED: sweep line for an org not in this run's pending: %s" % oid)
        odoms = orgs.get(oid, {}).get("domains") or []
        if not odoms:   # Head Start grantee rows often carry no domain; the org's own pages the people step read are its site (H1/H7)
            from urllib.parse import urlparse
            odoms = sorted({urlparse(u).netloc.lower().split(":")[0] for u in (r.get("pages_read") or []) if u})
        promote, result, why, validity = sweep_verdict(v, odoms)
        rec = dict(v); rec.update({"org_id": oid, "run": a.run, "date": TODAY, "result": result, "why": why, "validity": validity})
        out.append(rec); led.append({"key": v["key"], "org_id": oid, "run": a.run, "date": TODAY, "result": result, "email": em(v.get("email")) or None, "credits_spent": v.get("credits_spent"), "validity": validity})
        if promote:
            name = next((n for n in r.get("named_without_email") or [] if skey(oid, n["name"]) == v["key"]), {"name": v["key"].split("|", 1)[1]})
            promoted.setdefault(oid, []).append({"name": name.get("name"), "role": v.get("apollo_title") or name.get("role"), "role_key": name.get("role_key") or guess_role_key(name.get("role")),
                "email": em(v["email"]), "generic": False, "generic_event_inbox": False, "evidence_url": None, "quote": None, "quote_verified": False,
                "source": "apollo-verified", "thread_id": None, "gate1": "pass", "gate1_why": "H7: " + why, "dropped": None,
                "h7": {"apollo_status": v.get("email_status"), "zerobounce": validity, "flag": "⚠ catch-all domain (H7)" if validity == "catch_all" else None}})
    ajl(os.path.join(rd, "sweep.jsonl"), out); ajl(SWEEP_LEDGER, led)
    # promotion: a NEW pending row per org (pending() keeps the last row) + an Apollo verdict so decide sees it checked
    newrows, verdicts = [], []
    for oid, people in promoted.items():
        r = dict(pend[oid]); have = {p["email"] for p in r["people"] if p.get("email")}
        add = [p for p in people if p["email"] not in have]
        r["people"] = list(r["people"]) + add; r["h7_promoted"] = [p["email"] for p in add]; newrows.append(r)
        for p in add: verdicts.append({"key": pkey(oid, p["email"]), "identity": "confirmed", "apollo_title": p["role"], "email_status": p["h7"]["apollo_status"], "validity": p["h7"]["zerobounce"], "validator": "zerobounce", "credits_spent": 0, "via": "H7 sweep"})
    if newrows: ajl(os.path.join(rd, "pending.jsonl"), newrows)
    if verdicts: ajl(os.path.join(rd, "apollo.jsonl"), verdicts)
    cr = sum(v.get("credits_spent") for v in rows if isinstance(v.get("credits_spent"), (int, float)))
    ajl(os.path.join(rd, "credits.jsonl"), [{"date": TODAY, "lines": len(rows), "credits_spent": cr, "reported_lines": sum(isinstance(v.get("credits_spent"), (int, float)) for v in rows), "via": "H7 sweep"}])
    from collections import Counter
    c = Counter(o["result"] for o in out)
    print("sweep recorded: %d lookups · resolved %d · held %d · queried-null %d · promoted into pending %d · credits %s" % (len(out), c["resolved"], c["held"], c["queried-null"], sum(len(v) for v in promoted.values()), cr))

def cmd_carry(a):
    """Chris 2026-11-04: an H7 lookup is never repeated (sweep-items skips people already in the sweep ledger), so on a re-run a person
    Apollo RESOLVED earlier (Verified + validated + org domain) would silently drop off. This promotes them again from the ledger for every
    org in this run whose people step still names them (named_without_email). Same promotion shape as `sweep`; nothing is looked up."""
    rd = os.path.join(PDIR, a.run); pend = pending(a.run); led = {}
    for r in jl(SWEEP_LEDGER):
        if r.get("result") == "resolved" and r.get("email"): led.setdefault(r["org_id"], []).append(r)
    newrows, verdicts, n = [], [], 0
    for oid, r in sorted(pend.items()):
        have = {p.get("email") for p in r.get("people") or [] if p.get("email")}; add = []
        for nm in r.get("named_without_email") or []:
            nn = norm(nm.get("name"))
            for lr in led.get(oid, []):
                kn = lr["key"].split("|", 1)[1]
                kn2 = norm(re.sub(r",.*$", "", kn))   # drop credentials after a comma ("kandace thomas, mpp, phd")
                if lr["email"] in have or not nn or kn2 != nn: continue
                if (lr.get("date") or "") < (datetime.date.fromisoformat(TODAY) - datetime.timedelta(days=CFG.get("carry_max_age_days", 60))).isoformat(): continue
                add.append({"name": nm["name"], "role": nm.get("role"), "role_key": nm.get("role_key") or guess_role_key(nm.get("role")),
                    "email": em(lr["email"]), "generic": False, "generic_event_inbox": False, "evidence_url": None, "quote": None, "quote_verified": False,
                    "source": "apollo-verified", "thread_id": None, "gate1": "pass", "gate1_why": "H7 (resolved in run %s on %s): Apollo Verified + validated + org domain" % (lr.get("run"), lr.get("date")),
                    "dropped": None, "h7": {"apollo_status": "verified", "zerobounce": lr.get("validity") or "valid", "flag": "⚠ catch-all domain (H7)" if lr.get("validity") == "catch_all" else None, "carried_from": lr.get("run")}})
                have.add(lr["email"]); break
        if add:
            r2 = dict(r); r2["people"] = list(r.get("people") or []) + add; r2["h7_carried"] = [p["email"] for p in add]; newrows.append(r2); n += len(add)
            for p in add: verdicts.append({"key": pkey(oid, p["email"]), "identity": "confirmed", "apollo_title": p["role"], "email_status": "verified", "validity": "valid", "validator": "zerobounce", "credits_spent": 0, "via": "H7 carried"})
    if newrows: ajl(os.path.join(rd, "pending.jsonl"), newrows)
    if verdicts: ajl(os.path.join(rd, "apollo.jsonl"), verdicts)
    print("carried %d earlier H7-resolved people into %d orgs" % (n, len(newrows)))

def roster_line(r, led):
    pick, deferred = relevant_unpublished(r, r["machine"])
    keys = [skey(r["org_id"], n["name"]) for n in pick]
    # a person the sweep RESOLVED now carries an address, so relevant_unpublished no longer lists them — count them from the ledger
    extra = [k for k in led if k.startswith(r["org_id"] + "|") and k not in keys]
    res = [led[k]["result"] for k in keys if k in led] + [led[k]["result"] for k in extra]
    named = len({norm(p["name"]) for p in r.get("people") or [] if p.get("name")} | {norm(n["name"]) for n in r.get("named_without_email") or []})
    published = sum(1 for p in r.get("people") or [] if p.get("name") and p.get("email") and p.get("source") != "apollo-verified")
    return {"named": named, "published": published, "unpublished": len(pick) + len(deferred) + len(extra), "submitted": len(res), "resolved": res.count("resolved"),
            "held": res.count("held"), "queried_null": res.count("queried-null"), "deferred": len(deferred), "unswept": len([k for k in keys if k not in led])}
def roster_text(x): return "%d named · %d published · %d unpublished · %d submitted · %d resolved · %d held · %d queried-null · %d deferred" % (x["named"], x["published"], x["unpublished"], x["submitted"], x["resolved"], x["held"], x["queried_null"], x["deferred"])

def cmd_apollo_items(a):
    done = {r["key"] for r in jl(os.path.join(PDIR, a.run, "apollo.jsonl"))}
    orgs = {o["org_id"]: o for o in jl(ORGS)}
    for oid, r in sorted(pending(a.run).items()):
        for p in r["people"]:
            if p["gate1"] != "pass" or p["dropped"] or not p["email"]: continue
            k = pkey(oid, p["email"])
            if k in done: continue
            print(json.dumps({"key": k, "org_id": oid, "org_name": r["name"], "domain": (orgs[oid]["domains"] or [dom(p["email"])])[0],
                              "name": p["name"], "email": p["email"], "generic": p["generic"]}, ensure_ascii=False))

VALID = {"valid": "valid", "verified": "valid", "validated": "valid", "deliverable": "valid", "likely_to_engage": "valid",
         "catch_all": "catch_all", "catch-all": "catch_all", "accept_all": "catch_all", "accept-all": "catch_all",
         "invalid": "invalid", "undeliverable": "invalid", "bounced": "invalid", "do_not_mail": "invalid", "spamtrap": "invalid"}
def cmd_apollo(a):
    """Lines: {key, identity: confirmed|not_in_apollo|departed, apollo_title, apollo_org_domain, email_status (raw), validator,
    credits_spent (number or null)}. Unknown statuses become 'unknown' (proceed, flagged)."""
    rd = os.path.join(PDIR, a.run); rows = []
    for v in jl(a.file):
        if "key" not in v or v.get("identity") not in ("confirmed", "not_in_apollo", "departed"): sys.exit("FAIL CLOSED: bad apollo line %s" % v)
        raw = str(v.get("email_status") or "").strip().lower()
        v["validity"] = VALID.get(raw, "unknown") if not v.get("validity") else v["validity"]
        rows.append(v)
    ajl(os.path.join(rd, "apollo.jsonl"), rows)
    cr = [v.get("credits_spent") for v in rows if isinstance(v.get("credits_spent"), (int, float))]
    ajl(os.path.join(rd, "credits.jsonl"), [{"date": TODAY, "lines": len(rows), "credits_spent": sum(cr), "reported_lines": len(cr)}])
    print("apollo verdicts recorded: %d (credits reported: %s)" % (len(rows), sum(cr)))

# ---------------------------------------------------------------- assemble (Rulebook G) -- pure, tested
_FREE_MAIL = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com", "icloud.com", "comcast.net", "att.net", "msn.com", "live.com", "me.com", "frontier.com"}
def _own_inbox_domain(e, org_domains, p=None):
    """ENG-R008 keeps vendor / event-management inboxes out. Chris 2026-11-10 (Issue 1): an inbox is still the org's OWN when (a) it is on the
    org's domain, (b) it is on the parent of the org's own sub-site (aimh.gsu.edu -> gsu.edu), or (c) it is a free-mail inbox (gmail…) printed on
    the org's OWN page — volunteer-run associations (AEYC chapters) use one. A vendor company's domain is none of these."""
    d = e.split("@")[-1].lower(); bd = base_dom(d)
    doms = [str(x).lower() for x in (org_domains or []) if x]
    if bd in {base_dom(x) for x in doms} or any(x == d or x.endswith("." + d) or x.endswith("." + bd) for x in doms): return True
    return d in _FREE_MAIL and bool(p) and p.get("gate1") == "pass" and own_page(p.get("evidence_url"), doms)

def assemble(org_name, machine, people, apollo, staff_page_read, roster_searched, named_wo_email=(), fit="fit", org_domains=()):
    """people: ingested rows; apollo: {email: verdict}. Returns dict(decision, to, cc, greeting, flags, hold_reason, unblock, considered).
    org_domains (ENG-R008, Chris 2026-11-09): a generic / nameless inbox is accepted ONLY on the org's own domain — a vendor or
    event-management inbox printed on the org's page (events@emergentmethod.com on the LDOE page) is never a To or Cc."""
    rank = {k: i for i, k in enumerate(RANK.get(machine, []))}
    ok, flags, considered = [], [], []
    org_bd = {base_dom(d) for d in (org_domains or []) if d}
    for p in people:
        why = None
        if not p.get("email"): why = "no address"
        elif org_bd and (p.get("generic") or not p.get("name")) and not _own_inbox_domain(p["email"], org_domains, p):
            why = "generic inbox on a non-org domain %s — a vendor/event-management mailbox is never a recipient (ENG-R008)" % p["email"].split("@")[-1].lower()
            flags.append("⚠ %s dropped: generic inbox on a domain that is not the org's (ENG-R008)" % p["email"])
        elif p.get("gate1") != "pass": why = "provenance: " + str(p.get("gate1_why"))
        elif p.get("dropped"): why = p["dropped"]
        else:
            v = apollo.get(p["email"])
            if v is None: why = "not yet checked in Apollo"
            elif v.get("identity") == "departed": why = "Apollo: no longer at the org"; flags.append("⚠ %s appears to have left (Apollo) — not added" % (p.get("name") or p["email"]))
            elif v.get("validity") == "invalid" and p.get("source") == "apollo-verified": why = "address invalid (H4) — Apollo-found, not printed: skip, keep looking"
            elif v.get("validity") == "invalid": flags.append("⚠ %s: the validator says invalid, but it is printed on the org's own page/auto-reply — sent anyway, flagged (Chris 2026-11-09, H4)" % p["email"])
        considered.append({"email": p.get("email"), "name": p.get("name"), "role": p.get("role"), "excluded_because": why})
        if why: continue
        v = apollo[p["email"]]; q = dict(p)
        q["validity"] = v.get("validity", "unknown"); q["identity"] = v.get("identity")
        ok.append(q)
    if any((c["excluded_because"] or "").startswith("not yet checked") for c in considered):
        res = {"decision": "hold", "to": None, "cc": [], "greeting": None, "flags": flags, "considered": considered,
               "hold_reason": "addresses not yet checked in Apollo", "unblock": "run the Apollo check for this org (the whole recipient set is decided at once)"}
        return res
    seen = set(); uniq = []
    for p in ok:
        if p["email"] in seen: continue
        seen.add(p["email"]); uniq.append(p)
    named = [p for p in uniq if p.get("name") and not p.get("generic")]
    generic = [p for p in uniq if p.get("generic") or not p.get("name")]
    named.sort(key=lambda p: (rank.get(p.get("role_key"), 99), p["email"]))
    generic.sort(key=lambda p: (0 if p.get("generic_event_inbox") else 1, rank.get(p.get("role_key"), 99), p["email"]))   # role mailboxes (execdirector@) by role
    res = {"decision": "hold", "to": None, "cc": [], "greeting": None, "flags": flags, "hold_reason": None, "unblock": None, "considered": considered}
    if fit == "doubtful": flags.append("⚠ doubtful fit — in the dossier for Chris's decision, not drafted (Rulebook E2)")
    if named:
        sel = named[:MAXR]
        room = MAXR - len(sel)
        ev_inbox = [g for g in generic if g.get("generic_event_inbox")][:room]
        res.update(decision="ready", to=sel[0], cc=sel[1:] + ev_inbox)
        gn = [greet_name(p) for p in sel]
        names = [g for g, _ in gn if g]
        if any(not ok for g, ok in gn if g): flags.append("greeting name taken from the printed full name (no page-confirmed name) — check the greeting")
        res["greeting"] = "Hi %s," % (names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1])
        if len(named) > MAXR: flags.append("%d more named people found than the 4-person ceiling — kept the top %d by role" % (len(named) - MAXR, MAXR))
    elif generic:
        if not staff_page_read:
            res.update(hold_reason="only a generic inbox, and the staff page was not found and read (Rulebook G4)",
                       unblock="find and read the org's staff/leadership page (or 5+ URLs tried) — or a named person with an address")
            return res
        if not roster_searched:
            res.update(hold_reason="the full staff roster was not searched before dropping to a generic inbox (Rulebook G3)",
                       unblock="search the full roster (all staff/leadership pages) for named people first")
            return res
        g = generic[0]
        # named people without an address may be greeted (Rulebook G2 tier 3) ONLY if their page is on the org's own site (CAPA 2026-11-10 item 1)
        own_nw = [n for n in named_wo_email if n.get("source") != "apollo-roster" and (not org_domains or not n.get("evidence_url") or own_page(n["evidence_url"], org_domains))]
        if len(own_nw) < len(named_wo_email): flags.append("%d named people left out of the greeting: their page is not on the org's own site" % (len(named_wo_email) - len(own_nw)))
        nw = [g for g, _ in (greet_name(n) for n in own_nw) if g]
        res.update(decision="ready", to=g, cc=generic[1:MAXR])
        res["greeting"] = ("Hi %s and team," % ", ".join(nw[:3])) if nw else ("Hi %s team," % org_name)
        flags.append("generic inbox as To (Rulebook G2 tier %d)" % (3 if nw else 4))
    else:
        bad = [c for c in considered if c["excluded_because"]]
        if not people:
            res.update(hold_reason="no people with an address found on the org's own pages", unblock="a staff, leadership or event page that prints an address")
        elif any((c["excluded_because"] or "").startswith("not yet checked") for c in bad):
            res.update(hold_reason="addresses not yet checked in Apollo", unblock="run the Apollo check for this org")
        else:
            res.update(hold_reason="no address passed the checks: " + "; ".join(sorted({c["excluded_because"].split(":")[0] for c in bad})),
                       unblock="see each person's reason; a live-page address for a named person unblocks it")
        return res
    for p in [res["to"]] + res["cc"]:
        if p.get("validity") in ("catch_all", "unknown"): flags.append("address %s validity %s — proceeds, flagged (H4)" % (p["email"], p["validity"]))
        if p.get("identity") == "not_in_apollo": flags.append("%s not in Apollo — live page is the evidence" % p["email"])
    return res

def slim(p): return {k: p.get(k) for k in ("name", "role", "role_key", "email", "evidence_url", "validity", "identity", "generic", "source")}

def cmd_decide(a):
    rd = os.path.join(PDIR, a.run); caps = load_caps(a.run)
    ap = {}
    for v in jl(os.path.join(rd, "apollo.jsonl")): ap[v["key"]] = v
    out, led = [], []; sled = sweep_ledger()
    byid = {o["org_id"]: o for o in jl(ORGS)}   # ENG-R008: the org's own domains, so a generic inbox elsewhere is refused
    for oid, r in sorted(pending(a.run).items()):
        r.setdefault("org_id", oid)
        r.setdefault("org_domains", (byid.get(oid) or {}).get("domains") or [])
        apo = {p["email"]: ap[pkey(oid, p["email"])] for p in r["people"] if p.get("email") and pkey(oid, p["email"]) in ap}
        res = assemble(r["name"], r["machine"], r["people"], apo, r["staff_page_read"], r["roster_searched"], r.get("named_without_email") or [], r["fit"], org_domains=(r.get("org_domains") or []))
        roster = roster_line(r, sled)
        if res["decision"] == "ready" and res["to"] and (res["to"].get("generic") or not res["to"].get("name")) and roster["unswept"]:
            # G3/H7: a general inbox is never the To while relevant named people are still unlooked-up
            print("🔴 FINDING H7: %s — generic To refused: %d named people without a published address not yet looked up in Apollo" % (r["name"], roster["unswept"]))
            res.update(decision="hold", to=None, cc=[], greeting=None, hold_reason="H7: %d named people without a published address not yet looked up in Apollo — a general inbox cannot be the To until the sweep ran (G3)" % roster["unswept"],
                       unblock="run: people.py sweep-items --run %s → Apollo → people.py sweep, then decide again" % a.run)
        e18 = r.get("e18") or {}
        if e18.get("hold") and res["decision"] == "ready":   # E1.8 partial match: held until Apollo says NOT the same org (Rulebook B4)
            fin = pairs_known(); why = []
            for pr in e18.get("pairs") or []:
                if not pr.get("other_org"): continue
                v = (fin.get(tuple(sorted((pr["a"], pr["b"])))) or {}).get("verdict")
                if v == "same": why.append("Apollo says %s and %s are one org, and %s already has a thread (C2)" % (pr["a"], pr["b"], pr["other_org"]))
                elif v != "not-same": why.append("%s = %s not yet checked in Apollo" % (pr["a"], pr["b"]))
            if why:
                res.update(decision="hold", to=None, cc=[], greeting=None, hold_reason="E1.8 partial match: " + "; ".join(why) + " (Rulebook B4)",
                           unblock="the Apollo check (people step 7b) answers; if Apollo says same org, the org is already contacted")
        for p in r["people"]:
            if p.get("source") == "apollo-verified" and (p.get("h7") or {}).get("flag") and res["decision"] == "ready": res["flags"].append("%s: %s" % (p["email"], p["h7"]["flag"]))
        if res["decision"] == "hold" and not any(cap_of(u, caps) for u in r["pages_read"]) and not any(p["gate1"] == "pass" for p in r["people"]):
            res["hold_reason"] = ("no website on file for this org" if not r["pages_read"] else
                                  "none of the org's pages could be read (blocked, gone, or the site is not yet allowed in the Browser pane)")
            res["unblock"] = "add the org's website" if not r["pages_read"] else "allow the site in the Browser pane, or find a readable staff page"
        contacts = []
        for p in r["people"]:
            if not p.get("email") or p["gate1"] != "pass": continue
            v = apo.get(p["email"]) or {}
            contacts.append({"email": p["email"], "name": p["name"], "role": p["role"], "evidence_url": p["evidence_url"],
                             "verification": {"apollo": v.get("identity"), "zerobounce": v.get("validity"), "class": "vendor-resolved (Apollo Verified + ZeroBounce, H7)" if p.get("source") == "apollo-verified" else ("live-page" if p["source"] != "autoreply" else "auto-reply (H6)")},
                             "status": "departed" if v.get("identity") == "departed" else "active"})
        row = {"org_id": oid, "run": a.run, "decided": TODAY, "machine": r["machine"], "decision": res["decision"], "self_name": r.get("self_name"),
               "recipients": {"to": slim(res["to"]) if res["to"] else None, "cc": [slim(p) for p in res["cc"]], "greeting": res["greeting"]} if res["decision"] == "ready" else None,
               "hold_reason": res["hold_reason"], "unblock": res["unblock"], "flags": res["flags"], "contacts": contacts,
               "considered": res["considered"], "pages_read": r["pages_read"], "roster": roster, "roster_line": roster_text(roster),
               "by": "people %s (live-page + Apollo checks + H7 sweep)" % a.run}
        row["date"] = TODAY
        if r.get("domain_discovered"): row["domain_discovered"] = r["domain_discovered"]   # 2026-11-03 (p13)
        if r.get("e18"): row["e18"] = r["e18"]   # E1.8: both domains on the record, even when identical
        row["retry_after"] = None if (res["decision"] == "ready" or str(res["hold_reason"]).startswith("addresses not yet checked")) else plus_days(TODAY, CFG.get("recheck_hold_days", 14))
        out.append(row)
        n = (1 + len(res["cc"])) if res["decision"] == "ready" else 0
        print("%-6s %-40s %s · roster: %s" % (res["decision"].upper(), (r.get("name") or r.get("org_id") or "?")[:40], ("%d recipients · %s" % (n, res["greeting"])) if n else res["hold_reason"], roster_text(roster)))
    if a.test: ajl(os.path.join(rd, "test-decisions.jsonl"), out); print("TEST: decisions kept in the run folder only")
    else: ajl(INBOX, out)

def cmd_domain_items(a):
    """B4 patch 2 (Chris 2026-11-10): domains seen in REAL data for an org — Apollo-found addresses held as off-domain, and senders of the
    org's Gmail replies / auto-replies — that are not on file for it. Each is checked in Apollo (free people search); never guessed."""
    known = pairs_known(); orgs = jl(ORGS); byid = {o["org_id"]: o for o in orgs}; cap = CFG.get("domain_check_cap", 40); cands = {}
    def add(oid, d, src, ev):
        o = byid.get(oid) or {}; web = [base_dom(x) for x in o.get("domains") or [] if x]; d = base_dom(d or "")
        if not d or not web or d in NEVER_PAIR or same_dom(d, web) or (oid, d) in cands: return
        if tuple(sorted((web[0], d))) in known: return
        cands[(oid, d)] = {"key": "%s|%s" % (oid, d), "org_id": oid, "org_name": o.get("name"), "known_domain": web[0], "unknown_domain": d, "source": src, "evidence": ev}
    for (x, y), r in pairs_candidates().items():   # E1.8 candidates first (tonight's partial matches are held until these answer)
        o = byid.get(r.get("org_id")) or {}
        if tuple(sorted((x, y))) in known or (r.get("org_id"), r["b"]) in cands: continue
        cands[(r.get("org_id"), r["b"])] = {"key": "%s|%s" % (r.get("org_id"), r["b"]), "org_id": r.get("org_id"), "org_name": o.get("name"), "known_domain": r["a"],
                                         "unknown_domain": r["b"], "source": "E1.8 (address on the org's own page)", "evidence": r.get("proof")}
    for r in jl(SWEEP_LEDGER):
        if r.get("email") and r.get("result") == "held": add(r.get("org_id"), dom(r["email"]), "Apollo-found address", r["email"])
    for o in orgs:
        for t in o.get("threads") or []:
            g = t.get("gmail") or {}
            for kind in ("human", "auto"):
                for h in g.get(kind) or []:
                    s = h.get("sender") if isinstance(h, dict) else None
                    if s and "@" in s: add(o["org_id"], dom(s), "Gmail %s reply" % kind, "%s (thread %s)" % (s, h.get("thread") or t.get("thread_id")))
    rows = list(cands.values())[:cap]
    for x in rows: print(json.dumps(x, ensure_ascii=False))
    print("# domain items: %d of %d (cap %d). Apollo people search is free; a checked pair is never re-checked." % (len(rows), len(cands), cap), file=sys.stderr)

def cmd_domains(a):
    """Lines: {key, org_id, known_domain, unknown_domain, known_total, known_org, unknown_total, unknown_org}.
    SAME org = both domains return people AND Apollo names the same organization for both. Otherwise not joined (recorded, never retried)."""
    known = pairs_known(); new = []; n_same = 0
    for v in jl(a.file):
        for k in ("key", "org_id", "known_domain", "unknown_domain", "known_total", "unknown_total"):
            if k not in v: sys.exit("FAIL CLOSED: domain result missing %s" % k)
        kd, ud = base_dom(v["known_domain"]), base_dom(v["unknown_domain"])
        if tuple(sorted((kd, ud))) in known or ud in NEVER_PAIR: continue
        same = bool(v["known_total"]) and bool(v["unknown_total"]) and bool(norm(v.get("known_org"))) and norm(v.get("known_org")) == norm(v.get("unknown_org"))
        new.append({"date": TODAY, "run": a.run, "org_id": v["org_id"], "a": kd, "b": ud, "method": "apollo", "verdict": "same" if same else "not-same",
                    "proof": "Apollo people search: %s -> %s (%s people); %s -> %s (%s people)" % (kd, v.get("known_org"), v["known_total"], ud, v.get("unknown_org"), v["unknown_total"])})
        known[tuple(sorted((kd, ud)))] = new[-1]; n_same += same
        print("%-9s %s = %s  [%s]" % ("SAME" if same else "not same", kd, ud, v.get("known_org") or "-"))
    if new: ajl(PAIRS, new)
    print("recorded %d domain checks (%d same org) -> %s" % (len(new), n_same, PAIRS))

def cmd_stats(a):
    from collections import Counter
    rows = jl(ORGS); el = [o for o in rows if eligible(o)]
    print("eligible now:", dict(Counter(o["owner_machine"] for o in el)))
    print("ready recipient sets:", sum(1 for o in rows if o.get("recipients")), "· decisions rows:", len(jl(INBOX)))

def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("next"); p.add_argument("--run", required=True); p.add_argument("--cap", type=int); p.add_argument("--only"); p.add_argument("--machine", help="one machine or a comma list"); p.add_argument("--batch-size", type=int); p.add_argument("--night", help="night run id: skip orgs already worked in an earlier pass tonight"); p.add_argument("--redo", action="store_true", help="with --only: re-work orgs whose only threads are unsent drafts (Chris 2026-11-04)")
    p = sp.add_parser("js"); p.add_argument("--url"); p.add_argument("--quotes")
    p = sp.add_parser("capture"); p.add_argument("--run", required=True); p.add_argument("file")
    p = sp.add_parser("ingest"); p.add_argument("--run", required=True); p.add_argument("--batch", type=int, required=True); p.add_argument("file")
    p = sp.add_parser("roster-items"); p.add_argument("--run", required=True)
    p = sp.add_parser("roster"); p.add_argument("--run", required=True); p.add_argument("file")
    p = sp.add_parser("sweep-items"); p.add_argument("--run", required=True)
    p = sp.add_parser("sweep"); p.add_argument("--run", required=True); p.add_argument("file")
    p = sp.add_parser("carry"); p.add_argument("--run", required=True)
    p = sp.add_parser("apollo-items"); p.add_argument("--run", required=True)
    p = sp.add_parser("apollo"); p.add_argument("--run", required=True); p.add_argument("file")
    p = sp.add_parser("decide"); p.add_argument("--run", required=True); p.add_argument("--test", action="store_true")
    p = sp.add_parser("domain-items"); p.add_argument("--run", required=True)
    p = sp.add_parser("domains"); p.add_argument("--run", required=True); p.add_argument("file")
    sp.add_parser("stats")
    a = ap.parse_args()
    {"next": cmd_next, "js": cmd_js, "capture": cmd_capture, "ingest": cmd_ingest, "roster-items": cmd_roster_items, "roster": cmd_roster, "sweep-items": cmd_sweep_items, "sweep": cmd_sweep, "carry": cmd_carry, "apollo-items": cmd_apollo_items, "apollo": cmd_apollo,
     "decide": cmd_decide, "domain-items": cmd_domain_items, "domains": cmd_domains, "stats": cmd_stats}[a.cmd](a)
if __name__ == "__main__": main()
