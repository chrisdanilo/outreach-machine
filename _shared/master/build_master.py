#!/usr/bin/env python3
"""Build the outreach master list (one row per organization) from the old machines' files + Gmail.

Deterministic: same inputs -> byte-identical outputs. Old sources are read-only.
Run:  python3 build_master.py            (from this folder; paths come from settings.json)
"""
import csv, json, os, re, sys, io, datetime, collections

HERE = os.path.dirname(os.path.abspath(__file__))
import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_shared", "orchestrator")); import paths  # the one file that knows every folder (2026-11-03)
S = paths.settings()
ROOT = paths.MASTER
MKT = paths.MARKETING

def P(key, group="inputs"):
    return paths.expand(S[group][key])

# 2026-11-03: ONE settings file. Per-machine data lists (aliases, shared tenants, bounces, departed, never, existing clients) come from the
# machines block, every machine in order (OM-1 then OM-2), so a new machine's lists join the identity rules the same way.
def mall(key):
    out = {} if isinstance(paths.machine(paths.machines()[0])[key], dict) else []
    for m in paths.machines():
        v = paths.machine(m)[key]
        if isinstance(out, dict): out.update(v)
        else: out.extend(x for x in v if x not in out)
    return out

def jl(path):
    if not os.path.exists(path): return []
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]

FREEMAIL = {"gmail.com","yahoo.com","hotmail.com","outlook.com","aol.com","icloud.com","comcast.net","att.net","msn.com","live.com","me.com"}
EVENT_HOSTS = {"sched.com","eventbrite.com","cvent.com","whova.com","regfox.com","eventsair.com","pheedloop.com","swoogo.com","itce.catholic.edu","google.com","sites.google.com","wixsite.com","weebly.com","wix.com","squarespace.com","new-frame.com","godaddysites.com"}

def norm_dom(d):
    if not d: return ""
    d = str(d).strip().strip("`").lower().split()[0] if str(d).strip() else ""
    d = re.sub(r"^https?://", "", d).split("/")[0].split("?")[0]
    if "@" in d: d = d.split("@")[-1]
    if d.startswith("www."): d = d[4:]
    return d

def host_of(url):
    d = norm_dom(url)
    for h in EVENT_HOSTS:
        if d == h or d.endswith("." + h): return ""
    return d

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")[:80]

def mid_date(mid):
    try: return datetime.datetime.utcfromtimestamp((int(mid, 16) >> 20) / 1000).strftime("%Y-%m-%d")
    except Exception: return None

def clean_thread(t):
    if not t: return ""
    m = re.search(r"[0-9a-f]{16}", str(t))
    return m.group(0) if m else ""

# ---------------------------------------------------------------- identity
SHARED = {norm_dom(x) for x in mall("shared_tenant_domains")} | FREEMAIL
parent = {}
def find(x):
    parent.setdefault(x, x)
    while parent[x] != x:
        parent[x] = parent[parent[x]]; x = parent[x]
    return x
def union(a, b):
    a, b = norm_dom(a), norm_dom(b)
    if not a or not b or a in SHARED or b in SHARED: return
    ra, rb = find(a), find(b)
    if ra != rb:
        lo, hi = sorted([ra, rb]); parent[hi] = lo
for a, b in sorted(mall("domain_aliases").items()): union(a, b)
# Rulebook B4 (Chris 2026-11-10, ENG-R012): pairs the machine proved itself (E1.8: address printed on the org's own page; Apollo: both domains = one Apollo org)
for _r in (jl(paths.DOMAIN_PAIRS) if os.path.exists(paths.DOMAIN_PAIRS) else []):
    if _r.get("verdict") == "same": union(_r.get("a"), _r.get("b"))

M1C = jl(P("m1_contacted_jsonl")); M2C = jl(P("m2_contacted")); CARDS = jl(P("m2_cards_bank"))
for r in M1C + M2C:
    if r.get("type") == "org":
        ds = [norm_dom(x) for x in (r.get("domains") or [])]
        for d in ds[1:]: union(ds[0], d)
for c in CARDS:
    ds = [norm_dom(c.get("org_domain"))] + [norm_dom(x) for x in (c.get("org_domains") or [])]
    ds = [d for d in ds if d and host_of(d)]
    for d in ds[1:]: union(ds[0], d)

NAMEIDX = collections.defaultdict(set)   # (name slug, state) -> keys of domain-keyed orgs
STATE_CODES = set("AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY PR GU VI AS MP AB BC MB NB NL NS NT NU ON PE QC SK YT".split())
def split_state(name, state=None):
    """Head Start grantee names carry a trailing state code ('Kenaitze Indian Tribe Ak'). Strip it so the
    same org keys the same way from every source (fix 2026-10-30: Kenaitze duplicate, AWARE name)."""
    toks = (name or "").strip().split()
    st = (state or "").upper()[:2]
    if len(toks) > 1 and toks[-1].upper() in STATE_CODES and (not st or toks[-1].upper() == st):
        return " ".join(toks[:-1]), toks[-1].upper()
    return name, state
def key_for(domain=None, name=None, state=None):
    d = norm_dom(domain)
    if d and d not in SHARED and host_of(d): return "d:" + find(d)
    if name:
        if not (state or "").strip() or (name or "").strip().split()[-1].upper() == (state or "").upper()[:2]:
            name, state = split_state(name, state)
        st = (state or "").upper()[:2]
        hits = NAMEIDX.get((slug(name), st)) or (NAMEIDX.get((slug(name), "")) if not st else None) or set()
        if len(hits) == 1: return next(iter(hits))
        if not st:
            anyst = set().union(*[v for (n_, s_), v in NAMEIDX.items() if n_ == slug(name)]) if any(n_ == slug(name) for (n_, s_) in NAMEIDX) else set()
            if len(anyst) == 1: return next(iter(anyst))
        return "n:" + slug(name) + "|" + st
    return None

# ---------------------------------------------------------------- store
ORGS = {}
def org(key, name=None, domain=None, state=None, country=None, source=None):
    if key is None: return None
    o = ORGS.get(key)
    if o is None:
        o = ORGS[key] = {"_key": key, "name": None, "aliases": set(), "domains": set(), "state": None, "country": None,
                         "icps": {}, "fit": None, "exclusions": {}, "events": {}, "contacts": {}, "threads": {},
                         "notes": [], "referrer": False, "history": [], "sources": set(), "_m2_status": None, "_cand": None}
    if name and key.startswith("d:"):
        NAMEIDX[(slug(name), (state or o["state"] or "").upper()[:2])].add(key); NAMEIDX[(slug(name), "")].add(key)
    if name:
        if not o["name"]: o["name"] = name.strip()
        elif name.strip() != o["name"]: o["aliases"].add(name.strip())
    d = norm_dom(domain)
    if d and d not in SHARED: o["domains"].add(d)
    if state and not o["state"]: o["state"] = str(state).upper()[:2] if len(str(state)) <= 3 else str(state)
    if country and not o["country"]: o["country"] = country
    if source: o["sources"].add(source)
    return o

def add_icp(o, icp, why):
    if o and icp and icp not in o["icps"]: o["icps"][icp] = why
def set_fit(o, status, reason, source, strong=False):
    rank = {"not_fit": 3, "fit": 2, "doubtful": 1, "unreviewed": 0}
    if o["fit"] is None or strong or rank[status] > rank[o["fit"]["status"]]:
        o["fit"] = {"status": status, "reason": reason, "source": source}
def excl(o, kind, why, source):
    if o is not None: o["exclusions"].setdefault(kind, {"why": why, "source": source})
def contact(o, email, source, name=None, role=None, status=None, evidence_url=None, verification=None):
    if o is None or not email or "@" not in email: return
    e = email.strip().strip("`").lower()
    if "bcc.na2.hubspot.com" in e or e.endswith("@chrisdanilo.com"): return
    c = o["contacts"].setdefault(e, {"email": e, "name": None, "role": None, "evidence_url": None,
                                     "verification": {"apollo": None, "zerobounce": None, "class": None},
                                     "status": "active", "source": set()})
    c["source"].add(source)
    if name and not c["name"]: c["name"] = name
    if role and not c["role"]: c["role"] = role
    if evidence_url and not c["evidence_url"]: c["evidence_url"] = evidence_url
    if verification:
        for k, v in verification.items():
            if v is not None and c["verification"].get(k) is None: c["verification"][k] = v
    order = {"active": 0, "departed": 1, "bounced": 2, "do_not_contact": 3}
    if status and order[status] > order[c["status"]]: c["status"] = status
def hist(o, date, what, source):
    if o is not None: o["history"].append({"date": date or "", "what": what, "source": source})

THREADS = {}   # thread_id -> dict
def thread(tid, machine, o, source):
    tid = clean_thread(tid)
    if not tid or o is None: return None
    t = THREADS.setdefault(tid, {"thread_id": tid, "machines": set(), "orgs": set(), "ledger_dates": {}, "ledger_status": [],
                                 "gmail_msgs": {}, "labels": set(), "sources": set(), "m2_sent": False})
    if machine: t["machines"].add(machine)
    t["orgs"].add(o["_key"]); t["sources"].add(source)
    o["threads"].setdefault(tid, True)
    return t

FINDINGS = collections.defaultdict(list)
RECON = collections.OrderedDict()
def recon(src, read, matched=0, created=0, skipped=0, note=""):
    RECON[src] = {"read": read, "matched": matched, "created": created, "skipped": skipped, "note": note}

def touch(key, **kw):
    if key is None: return None, False
    existed = key in ORGS
    o = org(key, **kw)
    return o, existed

NAME_KEY = {}  # org label -> key (for shared-tenant address rows)

# ---------------------------------------------------------------- M1 contacted (Ledger A orgs + Ledger B addresses)
m = c = s = 0
for r in M1C:
    if r.get("type") != "org": continue
    ds = [norm_dom(x) for x in (r.get("domains") or [])]
    k = None
    for d in ds:
        k = key_for(d)
        if k: break
    k = k or key_for(None, r.get("org"), r.get("state"))
    o, ex = touch(k, name=r.get("org"), state=r.get("state"), country="US", source="M1 contacted (Ledger A)")
    if o is None: continue
    m += ex; c += (not ex)
    for d in ds:
        if d not in SHARED: o["domains"].add(d)
    NAME_KEY[(r.get("org") or "").strip().lower()] = k
    set_fit(o, "fit", "emailed by Machine 1 (CCR&R)", "M1 contacted")
    t = thread(r.get("thread"), "OM-1", o, "M1 contacted")
    if t is not None:
        for i, kk in enumerate(["e1", "e2", "e3"], 1):
            v = (r.get(kk) or "").strip().strip("*")
            mm = None if "due" in v.lower() else re.match(r"(\d\d)-(\d\d)", v)
            if mm: t["ledger_dates"][i] = "2026-%s-%s" % mm.groups()
        t["ledger_status"].append(("M1", r.get("status") or ""))
    if r.get("transferred_to"):
        hist(o, r.get("transferred_on"), "Machine 1 ledger: transferred to %s" % r.get("transferred_to"), "M1 contacted")
    hist(o, "", "Machine 1 ledger status: " + (r.get("status") or ""), "M1 contacted")
recon_orgs = (sum(1 for r in M1C if r.get("type") == "org"), m, c)
addr_rows = [r for r in M1C if r.get("type") == "address"]
am = 0
for r in addr_rows:
    d = norm_dom(r.get("domain") or r.get("address"))
    k = key_for(d) or NAME_KEY.get((r.get("org_label") or "").strip().lower())
    if not k: k = key_for(None, r.get("org_label"), None)
    o, ex = touch(k, name=r.get("org_label"), source="M1 contacted (Ledger B)")
    if o is None: continue
    am += ex
    st = "bounced" if r.get("outcome") == "bounced" else None
    contact(o, r.get("address"), "M1 contacted (Ledger B)", status=st)
recon("M1 contacted — org rows (Ledger A)", recon_orgs[0], recon_orgs[1], recon_orgs[2])
recon("M1 contacted — address rows (Ledger B)", len(addr_rows), am, len(addr_rows) - am, note="addresses become contacts")
recon("M1 contacted — correction/note rows", sum(1 for r in M1C if r.get("type") not in ("org", "address")), 0, 0,
      sum(1 for r in M1C if r.get("type") not in ("org", "address")), "historical corrections; superseded by Gmail")

# ---------------------------------------------------------------- M1 candidates
CAND = jl(P("m1_candidates")); m = c = 0
FIT_OF = {"OUT_OF_MARKET": ("not_fit", True), "HELD_D_DOUBT": ("doubtful", False), "RELEASED_REMAINING": ("unreviewed", False),
          "RESEARCH_OWED_FROM_M2": ("unreviewed", False), "RESEARCH_OWED_GATE1": ("unreviewed", False)}
for r in CAND:
    d = norm_dom(r.get("domain"))
    k = key_for(d, r.get("org"), r.get("state"))
    o, ex = touch(k, name=r.get("org"), domain=d, state=r.get("state"), country="US", source="M1 candidates")
    if o is None: continue
    m += ex; c += (not ex)
    for x in (r.get("domains") or []): union(d, x)
    st = r.get("status", "")
    o["_cand"] = st
    fs, strong = FIT_OF.get(st, ("fit", False))
    set_fit(o, fs, "Machine 1 candidate status %s%s" % (st, (": " + (r.get("reason") or r.get("why") or ""))[:300] if (r.get("reason") or r.get("why")) else ""), "M1 candidates", strong)
    if st.startswith("CLOSED_R1"): excl(o, "existing_client", "Machine 1 CLOSED_R1: " + (r.get("reason") or r.get("why") or "")[:200], "M1 candidates")
    if st == "CLOSED_X": hist(o, r.get("date"), "Machine 1 closed (X): " + (r.get("reason") or "")[:200], "M1 candidates")
    if r.get("thread"): thread(r.get("thread"), "OM-1", o, "M1 candidates")
    for ct in (r.get("contacts") or []):
        if isinstance(ct, dict):
            contact(o, ct.get("email") or ct.get("address"), "M1 candidates", name=ct.get("name"), role=ct.get("title") or ct.get("role"),
                    evidence_url=ct.get("evidence") or ct.get("source_url"))
        elif isinstance(ct, str) and "@" in ct: contact(o, ct, "M1 candidates")
    hist(o, r.get("date") or r.get("seeded"), "Machine 1 candidate: %s" % st, "M1 candidates")
recon("M1 candidates", len(CAND), m, c)

# ---------------------------------------------------------------- M1 warm leads (verbatim notes)
W = jl(P("m1_warm")); m = c = 0
for r in W:
    k = key_for(r.get("domain"), r.get("org"), r.get("state"))
    o, ex = touch(k, name=r.get("org"), domain=r.get("domain"), state=r.get("state"), source="M1 warm")
    if o is None: continue
    m += ex; c += (not ex)
    keep = {kk: r[kk] for kk in ("status","event","evidence","condition","re_entry_condition","next_action","next_action_date","quote","note","classification") if r.get(kk)}
    o["notes"].append({"text": json.dumps(keep, ensure_ascii=False, sort_keys=True), "source": "M1 warm.jsonl (verbatim fields)"})
    if r.get("thread"): thread(r.get("thread"), "OM-1", o, "M1 warm")
recon("M1 warm leads", len(W), m, c)

# ---------------------------------------------------------------- M1 config: bounces, departed, never
for e, v in sorted((mall("hard_bounces") or {}).items()):
    k = key_for(e) or NAME_KEY.get((v.get("org") or "").lower())
    o = org(k, name=v.get("org"), source="M1 config hard_bounces"); contact(o, e, "M1 config hard_bounces", status="bounced")
for e, v in sorted((mall("cleanup_departed") or {}).items()):
    k = key_for(e) or NAME_KEY.get((v.get("org") or "").lower())
    o = org(k, name=v.get("org"), source="M1 config cleanup_departed"); contact(o, e, "M1 config cleanup_departed", status="departed")
    o["notes"].append({"text": v.get("evidence") or "", "source": "M1 config cleanup_departed"})
for e in sorted(mall("never_recipients") or []):
    k = key_for(e); o = org(k, source="M1 config never_recipients"); contact(o, e, "M1 config never_recipients", status="do_not_contact")
recon("M1 config — hard bounces / departed / never", len(mall("hard_bounces") or {}) + len(mall("cleanup_departed") or {}) + len(mall("never_recipients") or []), note="contact status only")

# ---------------------------------------------------------------- HubSpot suppression (mirror; used only for exclusions)
sec = None; sub = None; hs_n = 0
for line in open(P("m1_hubspot_suppression"), encoding="utf-8"):
    if line.startswith("## "): sec = line[3:12]; sub = None
    if line.startswith("### "): sub = line[4:].strip()
    if not line.startswith("|") or not sec: continue
    if sec.startswith("§A"):
        mm = re.search(r"`([a-z0-9.-]+\.[a-z]{2,})`", line)
        if not mm: continue
        cells = [x.strip() for x in line.strip().strip("|").split("|")]
        o = org(key_for(mm.group(1), cells[1] if len(cells) > 1 else None), name=cells[1] if len(cells) > 1 else None, domain=mm.group(1), source="HubSpot suppression §A")
        if sub and (sub.startswith("Customers") or sub.startswith("Open deals")):
            excl(o, "existing_client", "%s — %s" % (sub, cells[-1] if cells else ""), "hubspot-suppression.md §A")
        else:
            excl(o, "prior_relationship", "%s — %s" % (sub, cells[-1] if cells else ""), "hubspot-suppression.md §A")
        hs_n += 1
    elif sec.startswith("§B") or sec.startswith("§D"):
        for e in re.findall(r"[\w.+-]+@[\w.-]+\.[a-z]{2,}", line):
            o = org(key_for(e), source="HubSpot suppression " + sec[:2])
            if o is None: continue
            if sec.startswith("§B"): contact(o, e, "hubspot-suppression.md §B", status="do_not_contact")
            else: excl(o, "prior_relationship", "HubSpot §D — real correspondence, needs Chris", "hubspot-suppression.md §D")
            hs_n += 1
recon("HubSpot suppression (§A domains, §B/§D addresses)", hs_n, note="exclusions only — HubSpot never decides fit or sends")
# 2026-11-04 (CAPA addendum A): the loop above reads TABLE rows only. Blocks written as paragraphs — all of §D, §A "Closed-lost" and
# "Peers / partners", and "ADDED TO §A/§B/§D" sections — were silently skipped (client.example was drafted). Read every backticked
# domain/address in those sections too. HS_BLOCKED also feeds the subdomain pass below (client.example under client.example).
HS_BLOCKED = set(); sec2 = None; added = False; hs_par = collections.Counter()
for line in open(P("m1_hubspot_suppression"), encoding="utf-8"):
    if line.startswith("## "):
        h = line[3:]; mm = re.match(r"§([ABCDE])\b", h); ma = re.search(r"ADDED TO §([ABD])", h)
        sec2 = mm.group(1) if mm else (ma.group(1) if ma else None); added = bool(ma and not mm)
    if sec2 not in ("A", "B", "D") or (line.startswith("|") and sec2 in ("A", "B") and not added): continue   # table rows of §A/§B proper: handled above
    for tok in re.findall(r"`([^`\s]+)`", line):
        tok = tok.lower().strip()
        if "@" in tok and re.match(r"^[\w.+-]+@[\w.-]+\.[a-z]{2,}$", tok):
            o = org(key_for(tok), source="HubSpot suppression §" + sec2)
            if o is None: continue
            if sec2 == "B": contact(o, tok, "hubspot-suppression.md §B", status="do_not_contact")
            else: excl(o, "prior_relationship", "HubSpot §%s — real correspondence, needs Chris" % sec2, "hubspot-suppression.md §" + sec2)
            HS_BLOCKED.add(tok); hs_par[sec2] += 1
        elif sec2 in ("A", "D") and re.match(r"^[a-z0-9-]+(\.[a-z0-9-]+)+$", tok) and not re.search(r"\.(jsonl?|md|py|csv|txt|pdf|html?)$", tok):
            o = org(key_for(tok), domain=tok, source="HubSpot suppression §" + sec2)
            excl(o, "prior_relationship", "HubSpot §%s (paragraph block) — relationship, needs Chris" % sec2, "hubspot-suppression.md §" + sec2)
            HS_BLOCKED.add(tok); hs_par[sec2] += 1
recon("HubSpot suppression paragraphs (§A lists, §D, ADDED-TO sections)", sum(hs_par.values()), note="per section: " + ", ".join("§%s %d" % kv for kv in sorted(hs_par.items())))

# ---------------------------------------------------------------- M2 config existing clients
for cl in (mall("existing_clients") or []):
    _ds = [norm_dom(x) for x in cl.get("domains") or []]
    for _d in _ds[1:]: union(_ds[0], _d)
    for d in cl.get("domains") or []:
        o = org(key_for(d, cl.get("name")), name=cl.get("name"), domain=d, source="M2 config existing_clients")
        excl(o, "existing_client", "%s (%s)" % (cl.get("why") or "", cl.get("folder") or ""), "M2 config existing_clients")

# ---------------------------------------------------------------- DNC register
for r in jl(P("dnc_register")):
    o = org(key_for(r.get("domain"), r.get("org")), name=r.get("org"), domain=r.get("domain"), source="do-not-contact register")
    if r.get("scope") == "person":      # Chris 2026-11-03 (Trying Together): a person-scope row blocks only the named addresses
        for e in r.get("emails") or []: contact(o, e, "do-not-contact register (person)", name=r.get("name"), status="do_not_contact")
        continue
    excl(o, "do_not_contact", "%s — \"%s\" (%s; %s)" % (r.get("register_id"), r.get("quote"), r.get("date_of_request"), r.get("confirmed_by")), "do-not-contact/register.jsonl")
    for e in r.get("emails") or []: contact(o, e, "do-not-contact register", name=r.get("name"), status="do_not_contact")

# ---------------------------------------------------------------- M2 organizations + events
M2O = jl(P("m2_organizations")); m = c = 0
EV2ORG = {}
for r in M2O:
    k = key_for(r.get("domain"), r.get("organization"))
    o, ex = touch(k, name=r.get("organization"), domain=r.get("domain"), source="M2 organizations")
    if o is None: continue
    m += ex; c += (not ex)
    o["_m2_status"] = r.get("status")
    st = r.get("status")
    if st == "in_events": set_fit(o, "fit", "Machine 2: runs a qualifying conference (in events list)", "M2 organizations")
    elif st == "retired": set_fit(o, "not_fit", "Machine 2: retired — " + (r.get("note") or "")[:200], "M2 organizations")
    elif st == "no_conference": set_fit(o, "unreviewed", "Machine 2: no own conference found (not MKT-002) — " + (r.get("verify_note") or r.get("note") or "")[:200], "M2 organizations")
    else: set_fit(o, "unreviewed", "Machine 2 status %s — %s" % (st, (r.get("note") or "")[:200]), "M2 organizations")
    for eid in r.get("events") or []: EV2ORG.setdefault(eid, k)
    hist(o, r.get("first_seen"), "Machine 2 found via %s" % r.get("found_by"), "M2 organizations")
recon("M2 organizations", len(M2O), m, c)

ICP_OF_TYPE = {"ccrr_or_cca": "ICP-001", "workforce_board": "ICP-002", "state_system_intermediary": "ICP-002", "state_agency": "ICP-002",
               "education_service_agency": "ICP-002", "head_start_grantee": "ICP-003", "aeyc_affiliate": "ICP-004",
               "head_start_state_assoc": "ICP-004", "head_start_regional_assoc": "ICP-004", "family_child_care_assoc": "ICP-004"}
def ev_rec(r, status, source):
    d27 = r.get("date_2027") or {}
    cfp = r.get("call_for_proposals") or {}
    lh = r.get("last_held") or {}
    nxt = d27.get("start") or (d27.get("month") and "%s (%s)" % (d27.get("month"), d27.get("status")))
    return {"name": r.get("event_name"), "url": r.get("event_url"), "last_edition_date": lh.get("start"),
            "next_edition_date": nxt, "attendance": r.get("attendance"),
            "cfp": {"url": cfp.get("url"), "opens": cfp.get("opens"), "deadline": cfp.get("deadline")},
            "keynote_path": r.get("keynote_slot"), "outreach_opens": r.get("outreach_opens"), "status": status,
            "large": r.get("large"), "event_id": r.get("event_id"), "source": source}
EV = jl(P("m2_events")); m = c = 0; ev_unlinked = 0
CARD_EV = {cd.get("event_id"): cd for cd in CARDS}
for r in EV:
    eid = r.get("event_id")
    k = EV2ORG.get(eid)
    if not k and eid in CARD_EV: k = key_for(CARD_EV[eid].get("org_domain"), r.get("organization"), r.get("state"))
    if not k: k = key_for(host_of(r.get("org_url")) or host_of(r.get("event_url")), r.get("organization"), r.get("state"))
    if not k: ev_unlinked += 1; continue
    o, ex = touch(k, name=r.get("organization"), state=r.get("state"), country=r.get("country"), source="M2 events")
    if o is None: continue
    m += ex; c += (not ex)
    o["events"][eid] = ev_rec(r, "active (%s)" % (r.get("wave") or "unscheduled"), "M2 events.jsonl")
    if r.get("org_type") in ICP_OF_TYPE: add_icp(o, ICP_OF_TYPE[r["org_type"]], "Machine 2 org_type %s" % r["org_type"])
    if r.get("colorado"): excl(o, "colorado", "event row flagged Colorado", "M2 events")
    if r.get("dnc"): excl(o, "do_not_contact", "event row flagged DNC", "M2 events")
recon("M2 events", len(EV), m, c, ev_unlinked, "unlinked = no org domain or name to attach to")
RET = jl(P("m2_events_retired")); rc = 0
for r in RET:
    eid = r.get("event_id"); k = EV2ORG.get(eid) or key_for(host_of(r.get("org_url")) or host_of(r.get("event_url")), r.get("organization"), r.get("state"))
    if not k: continue
    o = org(k, name=r.get("organization"), state=r.get("state"), source="M2 events-retired"); rc += 1
    o["events"].setdefault(eid, ev_rec(r, "retired: " + str(r.get("retired_reason") or r.get("reason") or "")[:120], "M2 events-retired.jsonl"))
recon("M2 events (retired)", len(RET), rc, note="kept as history on the org")

# ---------------------------------------------------------------- M2 cards bank (contacts, prior relationships)
m = c = 0
for cd in CARDS:
    k = key_for(cd.get("org_domain"), cd.get("organization"), cd.get("state"))
    o, ex = touch(k, name=cd.get("organization"), domain=cd.get("org_domain"), state=cd.get("state"), source="M2 cards bank")
    if o is None: continue
    m += ex; c += (not ex)
    if cd.get("org_type") in ICP_OF_TYPE: add_icp(o, ICP_OF_TYPE[cd["org_type"]], "Machine 2 org_type %s" % cd["org_type"])
    if cd.get("prior_relationship"): excl(o, "prior_relationship", str(cd.get("prior_relationship"))[:200], "M2 cards bank")
    for grp in ("candidates",):
        for p in cd.get(grp) or []:
            if isinstance(p, dict):
                contact(o, p.get("email"), "M2 cards bank", name=p.get("name"), role=p.get("title") or p.get("role"),
                        evidence_url=p.get("evidence_url") or p.get("source_url") or cd.get("staff_page_url"))
    for inbox in (cd.get("generic_inbox"), cd.get("org_inbox")):
        if isinstance(inbox, str): contact(o, inbox, "M2 cards bank (inbox)")
        elif isinstance(inbox, dict): contact(o, inbox.get("email") or inbox.get("address"), "M2 cards bank (inbox)")
recon("M2 cards bank (banked research)", len(CARDS), m, c)

# ---------------------------------------------------------------- M2 verify queue + hand-offs + referrers + keynoters
VQ = jl(P("m2_verify_queue")); m = c = 0
for r in VQ:
    k = key_for(r.get("domain"), r.get("organization"))
    o, ex = touch(k, name=r.get("organization"), domain=r.get("domain"), source="M2 verify queue")
    if o is None: continue
    m += ex; c += (not ex)
    if r.get("decision"): hist(o, r.get("added"), "Machine 2 verify decision: %s (%s)" % (r.get("decision"), r.get("stage")), "M2 verify queue")
    if o["fit"] is None: set_fit(o, "unreviewed", "Machine 2 verify queue: %s" % (r.get("decision") or r.get("state")), "M2 verify queue")
recon("M2 verify queue", len(VQ), m, c)
HO = jl(P("m2_handoff_to_m1")); m = c = 0
for r in HO:
    k = key_for(r.get("domain"), r.get("organization"))
    o, ex = touch(k, name=r.get("organization"), domain=r.get("domain"), source="M2 hand-off to M1")
    if o is None: continue
    m += ex; c += (not ex)
    o["notes"].append({"text": "Hand-off from Machine 2 (no dated conference): " + (r.get("why") or "")[:400], "source": "M2 handoff-to-m1.jsonl"})
recon("M2 hand-offs to Machine 1", len(HO), m, c)
RF = jl(P("m2_referrers")); m = c = 0
for r in RF:
    k = key_for(r.get("domain"), (r.get("name") or "") + " (referrer)")
    o, ex = touch(k, name=r.get("org") or (r.get("name") or "") + " (warm referrer)", domain=r.get("domain"), source="M2 referrers")
    if o is None: continue
    m += ex; c += (not ex)
    o["referrer"] = True
    o["notes"].append({"text": "Warm referrer — never emailed by a machine. %s · %s" % (r.get("name"), r.get("relationship")), "source": "M2 referrers.jsonl"})
recon("M2 warm referrers", len(RF), m, c, note="referrer=true; never emailed")
KN = jl(P("m2_keynoters"))
recon("M2 keynoters", len(KN), 0, 0, len(KN), "people, not organizations: discovery sources only (Rulebook D5)")

# ---------------------------------------------------------------- M2 contacted
m = c = 0
for r in M2C:
    if r.get("type") == "org":
        ds = [norm_dom(x) for x in (r.get("domains") or [])]
        k = None
        for d in ds:
            k = key_for(d)
            if k: break
        k = k or key_for(None, r.get("org"), r.get("state"))
        o, ex = touch(k, name=r.get("org"), state=r.get("state"), source="M2 contacted")
        if o is None: continue
        m += ex; c += (not ex)
        for d in ds:
            if d not in SHARED: o["domains"].add(d)
        set_fit(o, "fit", "emailed by Machine 2 (conference)", "M2 contacted")
        t = thread(r.get("thread"), "OM-2", o, "M2 contacted")
        if t is not None:
            mm = re.search(r"(\d{4}-\d\d-\d\d)", r.get("status") or "")
            if mm and "SENT" in (r.get("status") or ""): t["ledger_dates"][1] = mm.group(1)
            t["ledger_status"].append(("M2", r.get("status") or ""))
        for e in (r.get("to") or []) + (r.get("cc") or []): contact(o, e, "M2 contacted")
        if r.get("followup_add_cc"):
            o["notes"].append({"text": "Add as Cc on Email 2: " + ", ".join(r["followup_add_cc"]), "source": "M2 contacted followup_add_cc"})
        if r.get("followup_not_before"):
            o["notes"].append({"text": "Quiet window: no follow-up before %s" % r["followup_not_before"], "source": "M2 contacted"})
    elif r.get("type") == "address":
        o = org(key_for(r.get("domain") or r.get("address"), r.get("org_label")), name=r.get("org_label"), source="M2 contacted")
        contact(o, r.get("address"), "M2 contacted", status="bounced" if r.get("outcome") == "bounced" else None)
recon("M2 contacted (org + address rows)", len(M2C), m, c)

# (2026-11-03: the shadow contact register was retired — superseded by this list; see archive/MOVES log)

# ---------------------------------------------------------------- national CCR&R list + Head Start grantees
rows = list(csv.DictReader(open(P("m1_national_ccrr_csv"), encoding="utf-8"))); m = c = 0
for r in rows:
    d = norm_dom(r.get("Website domain"))
    k = key_for(d, r.get("Org"), r.get("State"))
    o, ex = touch(k, name=r.get("Org"), domain=d, state=r.get("State"), country="US", source="M1 national CCR&R list")
    if o is None: continue
    m += ex; c += (not ex)
    add_icp(o, "ICP-001", "national CCR&R list")
    if o["fit"] is None: set_fit(o, "unreviewed", "national CCR&R list disposition: %s" % r.get("Disposition"), "M1 national CCR&R list")
    if r.get("Contact email (if generic/known)"): contact(o, r["Contact email (if generic/known)"], "M1 national CCR&R list")
recon("National CCR&R list", len(rows), m, c)
rows = list(csv.DictReader(open(P("hs_grantees_csv"), encoding="utf-8"))); m = c = 0
for r in rows:
    rname, _st = split_state(r.get("recipient_name"), r.get("admin_state"))
    disp = (r.get("program_admin_name") or "").strip() or rname
    k = key_for(None, rname, r.get("admin_state"))
    if k and k.startswith("n:"):   # no domain-keyed match on the legal name: try the program's own name (fix 2026-10-30)
        st_ = (r.get("admin_state") or "").upper()[:2]
        hits = NAMEIDX.get((slug(disp), st_)) or set()
        if len(hits) == 1: k = next(iter(hits))
    o, ex = touch(k, name=disp, state=r.get("admin_state"), country="US", source="Head Start grantee universe")
    if o is None: continue
    m += ex; c += (not ex)
    if o["name"] and split_state(o["name"], o["state"])[0] != o["name"]:   # an earlier source used the raw 'Name St' form
        o["aliases"].add(o["name"]); o["name"] = disp
    if rname and rname != o["name"]: o["aliases"].add(rname)
    o["_hs_grant"] = r.get("grants")
    add_icp(o, "ICP-003", "Head Start grantee list (%s slots, %s)" % (r.get("funded_slots_total"), r.get("size_band")))
    set_fit(o, "unreviewed", "Head Start grantee, not yet reviewed (%s funded slots)" % r.get("funded_slots_total"), "HS grantee universe")
recon("Head Start grantee universe", len(rows), m, c, note="no domains in source; keyed by name+state")

# ---------------------------------------------------------------- sequence tracker rows (verbatim per-org notes)
DOM_INDEX = collections.defaultdict(set)
for k, o in ORGS.items():
    for d in o["domains"]: DOM_INDEX[d].add(k)
st_rows = 0
for line in open(P("m1_sequence_tracker"), encoding="utf-8"):
    if not line.startswith("|") or line.startswith("|---"): continue
    hits = set()
    for d in re.findall(r"[a-z0-9-]+(?:\.[a-z0-9-]+)*\.(?:org|com|net|gov|edu|us|cc|info)\b", line.lower()):
        for k in DOM_INDEX.get(norm_dom(d), ()): hits.add(k)
    for k in sorted(hits):
        o = ORGS[k]
        if sum(1 for n in o["notes"] if n["source"] == "M1 sequence-tracker.md") < 3:
            o["notes"].append({"text": line.strip()[:600], "source": "M1 sequence-tracker.md"}); st_rows += 1
recon("M1 sequence tracker (table rows naming an org domain)", st_rows, note="first 3 rows per org kept verbatim")

# ---------------------------------------------------------------- EMAIL 1 DRAFTS (Stage 7, 5_Draft/programfiles/draft.py) — threads the drafter created
# Each row of drafts-inbox.jsonl with status DRAFTED registers its Gmail thread on the org (stage E1-draft until Gmail shows
# Chris sent it; the inbox reader and Gmail state then move it on). Registered BEFORE the Gmail sections so Gmail state applies.
DI = jl(paths.DRAFTS)                    # 5_Draft/ledgers/drafts.jsonl
def _oid_of(key): return "org:" + (key[2:] if key.startswith("d:") else slug(key[2:].replace("|", "-")))
OID2KEY = {_oid_of(k_): k_ for k_ in list(ORGS)}
SUPERSEDED = {d.get("supersedes") for d in DI if d.get("supersedes")}   # 2026-11-04: a re-drafted org — the replaced draft is no longer a thread
D_REG = collections.Counter(); D_LATER = []   # rows whose org is only created by a later section (discovery inbox) — second pass below
for d in DI:
    if d.get("status") != "DRAFTED" or not d.get("thread_id") or d.get("draft_id") in SUPERSEDED: D_REG["skipped"] += 1; continue
    # 2026-11-02 (CAPA drafts-unattached): the drafter's own org_id wins; the domain / name+state matches below are
    # fallbacks for rows written before org_id was carried. An org with no domain on file otherwise lost its thread
    # and came back as a draft candidate the next pass (caught only by the Gmail C2 check).
    k = OID2KEY.get(d.get("org_id"))
    for dm in ([] if k else [d.get("org_domain")] + list(d.get("domains") or [])):
        kk = key_for(domain=dm) if dm else None
        if kk and kk in ORGS: k = kk; break
    if not k:
        kk = key_for(name=d.get("org_name"), state=d.get("state"))
        if kk and kk in ORGS: k = kk
    if not k: FINDINGS["draft_unattached"].append((d.get("org_id"), d.get("thread_id"))); D_REG["unattached"] += 1; D_LATER.append(d); continue
    o = ORGS[k]
    t = thread(d["thread_id"], d.get("machine"), o, "Email 1 draft %s" % d.get("run"))
    if t is None: FINDINGS["draft_unattached"].append((d.get("org_id"), d.get("thread_id"))); D_REG["unattached"] += 1; continue
    t["labels"].add("%s/0" % d.get("machine"))
    hist(o, (d.get("created_at") or "")[:10], "Email 1 drafted by %s (draft %s, %d recipient(s))" % (d.get("machine"), d.get("draft_id"), 1 + len(d.get("cc") or [])), "draft %s" % d.get("run"))
    D_REG["registered"] += 1
recon("Email 1 drafts (Stage 7 drafter)", len(DI), D_REG["registered"], 0, D_REG["skipped"] + D_REG["unattached"], "DRAFTED rows registered as E1-draft threads")

# ---------------------------------------------------------------- GMAIL (truth)
gdir = P("gmail_dir")
G_MSGS = {}
for fn in sorted(os.listdir(gdir)) if os.path.isdir(gdir) else []:
    if not fn.endswith(".txt") or fn == "README.txt": continue
    for line in open(os.path.join(gdir, fn), encoding="utf-8"):
        if line.startswith("#") or "|" not in line: continue
        p = (line.rstrip("\n").split("|") + ["", "", "", "", ""])[:5]
        tid, mid, snd, to, cc = p
        G_MSGS.setdefault(tid, {})[mid] = {"sender": snd, "to": [x for x in to.split(";") if x], "cc": [x for x in cc.split(";") if x], "date": mid_date(mid), "file": fn}
G_LABELS = {}
lp = os.path.join(gdir, "labels_ids.json")
if os.path.exists(lp):
    for lab, ids in sorted(json.load(open(lp)).items()):
        base = lab.split(" [")[0]
        for t in ids: G_LABELS.setdefault(t, set()).add(base)
gm = gc = gorph = 0
for tid in sorted(set(G_MSGS) | set(G_LABELS)):
    labs = G_LABELS.get(tid, set())
    machine = "OM-2" if any(l.startswith("Con Outreach") for l in labs) or any("Con" in v["file"] or "con_" in v["file"] for v in G_MSGS.get(tid, {}).values()) else "OM-1"
    if tid in THREADS:
        t = THREADS[tid]; gm += 1
    else:
        # attach Gmail-only thread by recipient domain
        k = None
        for v in G_MSGS.get(tid, {}).values():
            for e in v["to"] + v["cc"]:
                k = key_for(e)
                if k and k in ORGS: break
                k = None
            if k: break
        if not k:
            gorph += 1; FINDINGS["gmail_orphans"].append((tid, sorted(labs))); continue
        o = ORGS[k]; t = thread(tid, machine, o, "Gmail"); gc += 1
        FINDINGS["gmail_only_threads"].append((tid, o["name"], sorted(labs)))
    t["labels"] |= labs; t["machines"].add(machine); t["sources"].add("Gmail")
    for mid, v in G_MSGS.get(tid, {}).items():
        t["gmail_msgs"][mid] = v
        if v["sender"] == "chris@chrisdanilo.com" and machine == "OM-2": t["m2_sent"] = True
        o = ORGS[sorted(t["orgs"])[0]]
        for e in v["to"] + v["cc"]: contact(o, e, "Gmail")
recon("Gmail (labels + message windows pulled 2026-10-31)", len(set(G_MSGS) | set(G_LABELS)), gm, gc, gorph,
      "matched = thread already known from a ledger; created = Gmail-only thread attached by recipient domain; skipped = could not attach")

# ---------------------------------------------------------------- GMAIL STATE (Stage 3 inbox reader, 1_Read-the-Inbox/programfiles/inbox.py) — Gmail wins
GS_PATH = paths.GMAIL_STATE               # 1_Read-the-Inbox/ledgers/gmail-state.json
GS = json.load(open(GS_PATH, encoding="utf-8")) if GS_PATH and os.path.exists(GS_PATH) else {"threads": {}, "separate_threads_by_domain": {}}
def _ts(s_):
    try: return datetime.datetime.fromisoformat(s_.replace("Z", "+00:00"))
    except Exception: return None
def _gs_merge(t, tid, g):
    """Gmail state onto one thread (also used by the second drafts pass — CAPA 2026-11-06: threads registered late missed Gmail and stayed E1-draft after sending)."""
    t["gs"] = g
    t["labels"] |= set(g.get("labels") or [])
    if g.get("machine"): t["machines"].add(g["machine"])
    if g["read"] == "full":                           # every message read: Gmail's own sends replace the windowed pull
        for mid in [m for m, v in t["gmail_msgs"].items() if v["sender"] == "chris@chrisdanilo.com"]: del t["gmail_msgs"][mid]
        for i, s_ in enumerate(g["sends"]):
            t["gmail_msgs"]["full:%s:%d" % (tid, i)] = {"sender": "chris@chrisdanilo.com", "to": s_["to"], "cc": s_["cc"], "date": s_["date"][:10], "ts": s_["date"], "file": "gmail-state"}
    else:                                             # windows only: add a send the record does not have yet (latest date in the window — never early)
        for w_ in g["sent_seen"]:
            known = [v["date"] for v in t["gmail_msgs"].values() if v["sender"] == "chris@chrisdanilo.com"] + list(t["ledger_dates"].values())
            if not any(x and w_["from"] <= x <= w_["to"] or (x and abs((datetime.date.fromisoformat(x) - datetime.date.fromisoformat(w_["from"])).days) <= 1) for x in known):
                t["gmail_msgs"]["win:%s:%s" % (tid, w_["from"])] = {"sender": "chris@chrisdanilo.com", "to": [], "cc": [], "date": w_["to"], "file": "gmail-state sent window " + w_["from"] + ".." + w_["to"], "window": True}
                FINDINGS["gs_window_send"].append((tid, w_["from"], w_["to"]))
    if g["human"]: t["gs_human"] = g["human"]
gs_m = gs_new = 0
for tid, g in sorted(GS["threads"].items()):
    outreach = bool(g["sends"] or g["sent_seen"] or g["drafts"] or g["bounced"] or (g.get("labels") and g.get("machine")))
    if tid not in THREADS:
        if not outreach or g["human"]: continue        # a separate reply thread or a conversation: matched to an org by sender below
        k = None
        for s_ in g["sends"]:
            for e in s_["to"] + s_["cc"]:
                k = key_for(e)
                if k and k in ORGS: break
                k = None
            if k: break
        if not k:
            FINDINGS["gs_unattached"].append((tid, g.get("machine"), g["read"], ",".join(x["from"] for x in g["sent_seen"]) or "-"))
            continue
        t = thread(tid, g.get("machine") or "OM-1", ORGS[k], "Gmail"); gs_new += 1
        FINDINGS["gmail_only_threads"].append((tid, ORGS[k]["name"], sorted(g.get("labels") or [])))
    t = THREADS[tid]; gs_m += 1
    _gs_merge(t, tid, g)
# separate-thread human replies: matched to the org by the sender's address/domain (conservative: any person at the org stops it)
_ADDR = {e: k for k, o_ in ORGS.items() for e in o_["contacts"]}     # exact address → org (fallback when the sender's domain is not the org's, 2026-11-03)
for d, v in sorted(GS.get("separate_threads_by_domain", {}).items()):
    for h in v.get("human", []):
        k = key_for(h["sender"])
        if not k or k not in ORGS: k = _ADDR.get(h["sender"].lower())
        if not k or k not in ORGS: FINDINGS["gs_human_unmatched"].append((h["sender"], h["thread"], h["note"])); continue
        for tid in ORGS[k]["threads"]:
            t = THREADS[tid]
            if tid != h["thread"] and not any(x.get("thread") == h["thread"] for x in t.get("gs_human", [])):
                t.setdefault("gs_human", []).append(dict(h, matched="sender domain"))
recon("Gmail state (inbox reader, %s)" % GS.get("as_of", "?"), len(GS["threads"]), gs_m, gs_new, len(FINDINGS["gs_unattached"]),
      "read in full = %d threads; others from complete search windows (re-read by the sender before acting)" % sum(1 for g in GS["threads"].values() if g["read"] == "full"))

def _evkey(n):
    """event identity for de-duplication: drop years, ordinals, 'annual', parentheses and punctuation."""
    n = re.sub(r"\([^)]*\)", " ", (n or "").lower())
    n = re.sub(r"\b(19|20)\d\d\b|\b\d+(st|nd|rd|th)\b|\bannual\b", " ", n)
    return slug(n)
# ---------------------------------------------------------------- DISCOVERY INBOX (Stage 4, 2_Discover/programfiles/discover.py) — new finds and updates
# Append-only, processed in file order (deterministic). First-pass ICP tags; fit stays "unreviewed" until Stage 5 qualifies.
# People with an email on a live page become contacts (verification is Stage 6); people without one are kept as notes.
DI = jl(paths.FINDS)                     # 2_Discover/ledgers/finds.jsonl
m = c = 0; di_people = 0
for r in DI:
    og = r.get("org") or {}
    nm, st = og.get("name"), og.get("state")
    if nm and (not st or nm.strip().split()[-1].upper() == str(st).upper()[:2]): nm, st = split_state(nm, st)
    k = key_for(og.get("domain"), nm, st)
    o, ex = touch(k, name=nm, domain=og.get("domain"), state=st, country=og.get("country"), source="discovery")
    if o is None: continue
    m += ex; c += (not ex)
    for i in r.get("icps") or []: add_icp(o, i, "discovery first pass (%s): %s" % (r.get("run"), (r.get("icp_why") or "")[:120]))
    if o["fit"] is None: set_fit(o, "unreviewed", "found by discovery %s — Stage 5 qualifies" % r.get("run"), "discovery")
    for e in r.get("events") or []:
        eid = "disc:" + ((e.get("url") or "") + "#" + slug(e.get("name") or ""))[:180]
        _nd, _ns, _u = str(e.get("next_edition_date") or "")[:10], _evkey(e.get("name")), (e.get("url") or "").rstrip("/")
        _hit = next((x for x in o["events"].values() if (_nd and len(_nd) == 10 and str(x.get("next_edition_date") or "")[:10] == _nd)
                     or (_ns and _evkey(x.get("name")) == _ns) or (_u and (x.get("url") or "").rstrip("/") == _u)), None)
        if _hit is not None:   # the org already has this event: never duplicate it; fill in what discovery newly learned
            src_ = "discovery %s · %s" % (r.get("run"), e.get("evidence_url") or r.get("evidence_url"))
            if e.get("next_edition_date") and (not _hit.get("next_edition_date") or "estimated" in str(_hit.get("next_edition_date"))):
                _hit["next_edition_date"] = e["next_edition_date"]; _hit["source"] = "%s; date from %s" % (_hit.get("source"), src_)
            cf = e.get("cfp") or {}
            hc = _hit.setdefault("cfp", {"url": None, "opens": None, "deadline": None}) or {}
            for kk in ("url", "opens", "deadline"):
                if cf.get(kk) and not hc.get(kk): hc[kk] = cf[kk]; _hit["source"] = "%s; call-for-speakers %s from %s" % (_hit.get("source"), kk, src_)
            _hit["cfp"] = hc
            if e.get("attendance") and not _hit.get("attendance"): _hit["attendance"] = e["attendance"]
            continue
        o["events"].setdefault(eid, {"name": e.get("name"), "url": e.get("url"), "last_edition_date": e.get("last_edition_date"),
            "next_edition_date": e.get("next_edition_date"), "attendance": e.get("attendance"),
            "cfp": e.get("cfp") or {"url": None, "opens": None, "deadline": None}, "keynote_path": e.get("keynote_path"),
            "outreach_opens": None, "status": "active (found by discovery, unverified)", "large": None, "event_id": eid,
            "source": "discovery %s · %s" % (r.get("run"), e.get("evidence_url") or r.get("evidence_url"))})
    for pp in r.get("people") or []:
        if pp.get("email"):
            contact(o, pp["email"], "discovery %s" % r.get("run"), name=pp.get("name"), role=pp.get("role"), evidence_url=pp.get("evidence_url"))
        else:
            o["notes"].append({"text": "Person found (no email yet — Stage 6 finds and verifies): %s · %s · %s" % (pp.get("name"), pp.get("role"), pp.get("evidence_url")),
                               "source": "discovery %s" % r.get("run")})
        di_people += 1
    hist(o, r.get("found"), "found by discovery source %s (%s)" % (r.get("source_id"), r.get("evidence_url")), "discovery")
recon("Discovery inbox (Stage 4)", len(DI), m, c, note="%d people captured" % di_people)

# ---------------------------------------------------------------- EMAIL 1 DRAFTS, second pass (orgs created by the discovery inbox above)
for d in D_LATER:
    k = {_oid_of(k_): k_ for k_ in list(ORGS)}.get(d.get("org_id"))
    if not k: continue
    o = ORGS[k]
    t = thread(d["thread_id"], d.get("machine"), o, "Email 1 draft %s" % d.get("run"))
    if t is None: continue
    t["labels"].add("%s/0" % d.get("machine"))
    if clean_thread(d["thread_id"]) in GS["threads"] and "gs" not in t: _gs_merge(t, clean_thread(d["thread_id"]), GS["threads"][clean_thread(d["thread_id"])])
    hist(o, (d.get("created_at") or "")[:10], "Email 1 drafted by %s (draft %s, %d recipient(s))" % (d.get("machine"), d.get("draft_id"), 1 + len(d.get("cc") or [])), "draft %s" % d.get("run"))
    FINDINGS["draft_unattached"] = [x for x in FINDINGS["draft_unattached"] if x[1] != d["thread_id"]]
    D_REG["registered"] += 1; D_REG["unattached"] -= 1
RECON["Email 1 drafts (Stage 7 drafter)"].update({"matched": D_REG["registered"], "skipped": D_REG["skipped"] + D_REG["unattached"]})
if FINDINGS["draft_unattached"]: print("DRAFT ROWS NOT ATTACHED:", FINDINGS["draft_unattached"], file=sys.stderr)

# 2026-11-04: a blocked HubSpot domain also blocks its subdomains (client.example under client.example).
HS_SUB = 0
for _k, _o in ORGS.items():
    if _o["exclusions"].get("prior_relationship") or _o["exclusions"].get("existing_client"): continue
    for _d in list(_o["domains"]):
        _hit = next((b_ for b_ in HS_BLOCKED if "@" not in b_ and _d.endswith("." + b_)), None)
        if _hit: excl(_o, "prior_relationship", "HubSpot block on parent domain %s" % _hit, "hubspot-suppression.md (subdomain)"); HS_SUB += 1; break
if HS_SUB: print("HubSpot block applied to %d subdomain org(s)" % HS_SUB)
# ---------------------------------------------------------------- derive threads, owners, next_due
AS_OF = datetime.date.fromisoformat(S["as_of"])
HOL = set(S["us_bank_holidays_federal_reserve"])
GAP = S["sequence_gap_days"]
def bizday(d):
    while d.weekday() >= 5 or d.isoformat() in HOL: d += datetime.timedelta(days=1)
    return d
NEXT_SLOT = bizday(AS_OF if AS_OF.weekday() < 5 else AS_OF + datetime.timedelta(days=1))
if NEXT_SLOT == AS_OF: NEXT_SLOT = AS_OF  # a weekday as_of: the 7 AM slot that day (build runs overnight)
LABEL_STAGE = [("/3", "E3"), ("/2", "E2"), ("/1", "E1"), ("/0", "E1-draft")]
def stage_status(t):
    labs = t["labels"]
    sfx = {l.split("/")[-1] if "/" in l else "" for l in labs}
    status = "open"
    if "X" in sfx or "✗" in sfx: status = "closed✗"   # old trees used X, OM trees use ✗ (CAPA-2026-11-03-label-trees)
    elif "★" in sfx: status = "replied★"
    elif "⏸" in sfx: status = "hold⏸"
    elif "⚠" in sfx: status = "attention⚠"
    g_stage = None
    for suf, stg in LABEL_STAGE:
        if suf[1:] in sfx: g_stage = stg; break
    sent = []
    prev_ts = None
    for mid, v in sorted(t["gmail_msgs"].items(), key=lambda kv: (kv[1].get("ts") or kv[1]["date"] or "")):
        if v["sender"] != "chris@chrisdanilo.com": prev_ts = None; continue   # Rule 3a needs nothing between the two own messages
        ts = _ts(v["ts"]) if v.get("ts") else (_ts(datetime.datetime.utcfromtimestamp((int(mid, 16) >> 20) / 1000).isoformat() + "+00:00") if re.fullmatch(r"[0-9a-f]{16}", mid) else None)
        if ts and prev_ts and (ts - prev_ts).total_seconds() < 24 * 3600:   # Rule 3a: a copy < 24 h after the previous own message is never a step
            FINDINGS["duplicate_sends"].append((t["thread_id"], v["date"])); continue
        prev_ts = ts or prev_ts
        sent.append({"date": v["date"], "to": v["to"], "cc": v["cc"], "message_id": None if ":" in mid else mid,
                     "source": "Gmail sent window (date = latest day of window)" if v.get("window") else "Gmail"})
    gd = {s_["date"] for s_ in sent}
    full = (t.get("gs") or {}).get("read") == "full"   # every message read in Gmail: the ledger adds nothing (Gmail wins)
    for n, d in sorted(t["ledger_dates"].items()):
        if full: continue
        if not any(abs((datetime.date.fromisoformat(d) - datetime.date.fromisoformat(x)).days) <= 1 for x in gd if x):
            sent.append({"date": d, "to": [], "cc": [], "message_id": None, "source": "ledger (not yet seen in Gmail pull)"})
    sent.sort(key=lambda x: x["date"])
    # Sequence emails are >= 7 days apart. Two "sends" < 5 days apart where one is only a ledger line or a sent-window
    # sighting are the SAME email with two dates (the ledger often records the draft day); keep the later (Gmail) date.
    merged = []
    for s_ in sent:
        if merged and (datetime.date.fromisoformat(s_["date"]) - datetime.date.fromisoformat(merged[-1]["date"])).days < 5 \
                and (s_["message_id"] is None or merged[-1]["message_id"] is None) and not (s_["source"] == merged[-1]["source"] == "Gmail"):
            keep = s_ if s_["source"].startswith("Gmail") else merged[-1]
            if keep is s_ or merged[-1]["source"].startswith("ledger"):
                FINDINGS["date_merged"].append((t["thread_id"], merged[-1]["date"], s_["date"]))
            merged[-1] = dict(keep, date=max(s_["date"], merged[-1]["date"]) if not (merged[-1]["source"] == "Gmail" and merged[-1]["message_id"]) else merged[-1]["date"])
            continue
        merged.append(s_)
    sent = merged
    for i, s_ in enumerate(sent, 1): s_["n"] = i
    l_stage = {0: "E1-draft", 1: "E1", 2: "E2"}.get(len(t["ledger_dates"]), "E3")
    RANK = {"E1-draft": 0, "E1": 1, "E2": 2, "E3": 3}
    ltxt = " ".join(x[1] for x in t["ledger_status"])
    if status == "open" and not labs:
        if re.search(r"(^|\W)(X|CLOSED)\b", ltxt): status = "closed✗"
        elif "★" in ltxt: status = "replied★"
    if t.get("gs_human") and not status.startswith("closed"): status = "replied★"   # Gmail shows a person replied (Rulebook K1)
    dated = {0: "E1-draft", 1: "E1", 2: "E2"}.get(len(sent), "E3")
    stage = max([x for x in (g_stage, dated) if x], key=lambda x: RANK[x])   # never step backwards: a missed label or a missed ledger line must not cause a repeat send
    if "OM-2" in t["machines"] and not g_stage and (t["m2_sent"] or "SENT" in ltxt) and stage == "E1-draft": stage = "E1"
    if g_stage and t["ledger_dates"] and g_stage != l_stage and g_stage != "E1-draft":
        FINDINGS["stage_disagree"].append((t["thread_id"], l_stage, g_stage, "Gmail label ahead of ledger" if RANK[g_stage] > RANK[l_stage] else "Gmail label behind ledger"))
    for n, d in sorted(t["ledger_dates"].items()):
        gs = [x["date"] for x in sent if x["source"] == "Gmail"]
        if gs and len(gs) >= n and abs((datetime.date.fromisoformat(gs[n - 1]) - datetime.date.fromisoformat(d)).days) > 1:
            FINDINGS["date_disagree"].append((t["thread_id"], n, d, gs[n - 1]))
    last = max([x["date"] for x in sent], default=None)
    nd = None; overdue = False
    undated = RANK.get(stage, 0) > len(sent)
    if status == "open" and stage in ("E1", "E2", "E3") and undated:
        nd = "UNKNOWN — Gmail shows %s but its send date is not in this pull; the sender must read the thread before acting" % stage
        FINDINGS["undated"].append(t["thread_id"])
    elif status == "open" and stage in ("E1", "E2") and last:
        due = bizday(datetime.date.fromisoformat(last) + datetime.timedelta(days=GAP))
        if due < NEXT_SLOT: overdue = True; due = NEXT_SLOT
        nd = due.isoformat() + " 07:00 ET" + (" (overdue → next slot)" if overdue else "")
    elif status == "open" and stage == "E3" and last:
        cd = bizday(datetime.date.fromisoformat(last) + datetime.timedelta(days=GAP))
        nd = ("close ✗ now — no reply since Email 3 (%s); was due %s" % (last, cd.isoformat())) if cd < NEXT_SLOT else ("close ✗ on %s if no reply" % cd.isoformat())
    return stage, status, sent, last, nd, overdue

def _gview(t):
    g = t.get("gs")
    h = t.get("gs_human") or []
    if not g and not h: return None
    g = g or {}
    return {"read": g.get("read"), "human": [{"sender": x["sender"], "date": x.get("date"), "thread": x.get("thread"), "note": x.get("note", "")} for x in h],
            "bounced": [x["address"] for x in g.get("bounced", [])], "dsn": g.get("dsn", False), "drafts": len(g.get("drafts", [])),
            "auto": [{"sender": x["sender"], "date": x.get("date"), "return": x.get("return")} for x in g.get("auto", [])]}
OUT = []
# 2026-11-06 (CAPA phantom drafts): threads Gmail says do not exist ("Requested entity was not found") — legacy unsent drafts that were
# deleted. An open, never-sent one is dropped (it is not a draft waiting for Chris); a stopped/replied one is kept for its stop status.
GONE = {json.loads(l)["thread_id"] for l in open(os.path.join(paths.ledgers("read"), "gone-threads.jsonl"), encoding="utf-8") if l.strip()} \
    if os.path.exists(os.path.join(paths.ledgers("read"), "gone-threads.jsonl")) else set()
GONE_KEEP = {e["thread_id"] for e in json.load(open(paths.OVERRIDES, encoding="utf-8")).get("thread_status", [])}   # Chris ruled on these: keep
OVERDUE = collections.Counter(); STAGE_COUNT = collections.Counter(); TWO = []
for k in sorted(ORGS):
    o = ORGS[k]
    ths = []
    machines = set()
    for tid in sorted(o["threads"]):
        t = THREADS[tid]
        stage, status, sent, last, nd, ov = stage_status(t)
        if tid in GONE and stage == "E1-draft" and not sent and status == "open" and tid not in GONE_KEEP: FINDINGS["gone_thread_dropped"].append((o["name"], tid)); continue
        mach = sorted(t["machines"])
        machines |= set(mach)
        lab = sorted(t["labels"])
        ths.append({"thread_id": tid, "machine": "/".join(mach) or None, "label": lab[0] if lab else None, "labels": lab,
                    "stage": stage, "messages_sent": sent, "last_sent_at": last, "status": status, "next_due": nd,
                    "sources": sorted(t["sources"]), "gmail": _gview(t)})
        STAGE_COUNT[("/".join(mach) or "?", stage, status)] += 1
        if ov: OVERDUE["/".join(mach) or "?"] += 1
    icps = dict(o["icps"])
    if not icps:
        nm = (o["name"] or "").lower()
        if "OM-1" in machines or o["_cand"]:
            if re.search(r"\baeyc\b|association|head start assoc|network for|alliance\b|coalition of|federation", nm) and not re.search(r"early learning coalition", nm):
                icps["ICP-004"] = "name rule: association/network (draft)"
            elif re.search(r"resource (and|&) referral|cc ?r ?& ?r|ccr&r|child care aware|early learning coalition|\belc\b|child care council|4-?c'?s?\b|child care resources?|childcare resource", nm):
                icps["ICP-001"] = "name rule (draft)"
            else:
                icps["ICP-002"] = "Machine 1 market (MKT-001) — not a CCR&R by name (draft)"
    icp_list = sorted(icps) or ["unclassified"]
    has_event = any(e["status"].startswith("active") for e in o["events"].values()) or o["_m2_status"] == "in_events"   # Chris 2026-11-09: any conference counts; no outside-keynote gate
    markets = set()
    if set(icp_list) & {"ICP-001", "ICP-002", "ICP-003", "ICP-005"}: markets.add("MKT-001")
    if has_event and set(icp_list) & {"ICP-001", "ICP-002", "ICP-003", "ICP-004", "ICP-006"}: markets.add("MKT-002")
    if has_event and icp_list == ["unclassified"]: FINDINGS["event_org_outside_icps"].append((o["name"], k))
    if o["state"] == "CO": excl(o, "colorado", "state CO — Chris works Colorado personally (Rulebook C5)", "state field")
    flags = []
    if machines == {"OM-1", "OM-2"} or (len(machines) > 1):
        owner = "OM-2" if has_event else "OM-1"; flags.append("two machines have threads — Chris to confirm owner")
        TWO.append((o["name"], k, owner))
    elif machines: owner = sorted(machines)[0]
    elif o["referrer"]: owner = "none"
    elif has_event and set(icp_list) & {"ICP-001", "ICP-002", "ICP-003", "ICP-004", "ICP-006"}: owner = "OM-2"
    elif "MKT-001" in markets: owner = "OM-1"
    else: owner = "none"
    dom = sorted(o["domains"])
    primary = k[2:] if k.startswith("d:") else None
    oid = "org:" + (primary or slug(k[2:].replace("|", "-")))
    rec = {"org_id": oid, "name": o["name"], "aliases": sorted(o["aliases"]), "domains": ([primary] if primary else []) + [d for d in dom if d != primary],
           "state": o["state"], "country": o["country"], "icps": icp_list, "icp_basis": {k2: v for k2, v in sorted(icps.items())},
           "markets": sorted(markets), "owner_machine": owner, "flags": flags, "runs_event": bool(has_event),
           "fit": o["fit"] or {"status": "unreviewed", "reason": None, "source": None},
           "exclusions": {kk: o["exclusions"].get(kk) for kk in ("existing_client", "do_not_contact", "colorado", "prior_relationship", "other")},
           "events": [o["events"][e] for e in sorted(o["events"])],
           "contacts": [dict(v, source=sorted(v["source"])) for _, v in sorted(o["contacts"].items())],
           "threads": ths, "notes": o["notes"], "referrer": o["referrer"],
           "history": sorted(o["history"], key=lambda h: (h["date"] or "", h["what"])), "sources": sorted(o["sources"])}
    OUT.append(rec)

# duplicate org_id guard
ids = collections.Counter(r["org_id"] for r in OUT)
for r in OUT:
    if ids[r["org_id"]] > 1: r["org_id"] += "|" + (r["state"] or "")

# ambiguous merges: same name slug under different keys, same state
byname = collections.defaultdict(list)
for r in OUT: byname[(slug(r["name"]), r["state"])].append(r["org_id"])
AMBIG = sorted((n, s_, sorted(v)) for (n, s_), v in byname.items() if len(v) > 1 and n)

# ---------------------------------------------------------------- Chris's overrides (applied LAST; survive rebuilds)
OVR_PATH = paths.OVERRIDES
OVR = json.load(open(OVR_PATH, encoding="utf-8")) if os.path.exists(OVR_PATH) else {}
BYID = {r["org_id"]: r for r in OUT}
OVR_MISSING = []
def _derive(r):
    s_ = set(r["icps"])
    mk = set()
    if s_ & {"ICP-001", "ICP-002", "ICP-003", "ICP-005"}: mk.add("MKT-001")
    if r.get("runs_event") and s_ & {"ICP-001", "ICP-002", "ICP-003", "ICP-004", "ICP-006"}: mk.add("MKT-002")
    return sorted(mk)
MERGED = []
GONE = {}
# Automatic merge (Stage 4, 2026-10-31): two rows attached to the SAME Gmail thread are the same org (one thread per org, Rulebook C2).
# Survivor = row with a web domain, then more contacts, then a reviewed fit, then org_id order. Deterministic; logged in the report.
_tm = collections.defaultdict(list)
for r in OUT:
    for t in r["threads"]: _tm[t["thread_id"]].append(r["org_id"])
_auto, _seen = [], set()
def _rank(oid):
    r = BYID[oid]
    return (0 if r["domains"] else 1, -len(r["contacts"]), 1 if r["fit"]["status"] == "unreviewed" else 0, oid)
for tid in sorted(_tm):
    ids_ = sorted(set(_tm[tid]) - _seen)
    if len(ids_) < 2: continue
    ids_.sort(key=_rank)
    _auto.append({"into": ids_[0], "from": ids_[1:], "reason": "same Gmail thread %s" % tid, "by": "automatic: one thread = one org (Rulebook C2)"})
    _seen.update(ids_[1:])
def _fold(e, fid):
    """Fold duplicate row fid into e['into'] (contacts, events, threads, domains, sources unioned)."""
    r = BYID[e["into"]]
    f = BYID.pop(fid, None)
    if not f: OVR_MISSING.append(("merge", fid)); return
    for k_ in ("domains", "sources", "aliases", "markets"):
        r[k_] = sorted(set(r[k_]) | set(f[k_]))
    r["aliases"] = sorted(set(r["aliases"]) | ({f["name"]} - {r["name"]}))
    have = {c_["email"] for c_ in r["contacts"]}
    r["contacts"] += [c_ for c_ in f["contacts"] if c_["email"] not in have]
    r["events"] += [ev for ev in f["events"] if ev not in r["events"]]
    r["threads"] += [t for t in f["threads"] if t["thread_id"] not in {x["thread_id"] for x in r["threads"]}]
    r["history"] += f["history"]; r["notes"] += f["notes"]
    r["icps"] = sorted((set(r["icps"]) | set(f["icps"])) - ({"unclassified"} if set(r["icps"]) | set(f["icps"]) != {"unclassified"} else set()))
    r["icp_basis"] = dict(f["icp_basis"], **r["icp_basis"])
    for k_, v_ in f["exclusions"].items():
        if v_ and not r["exclusions"].get(k_): r["exclusions"][k_] = v_
    r["state"] = r["state"] or f["state"]; r["country"] = r["country"] or f["country"]
    r["runs_event"] = r["runs_event"] or f["runs_event"]; r["referrer"] = r["referrer"] or f["referrer"]
    if r["owner_machine"] == "none": r["owner_machine"] = f["owner_machine"]
    r["flags"] = r["flags"] + ["merged duplicate row %s — %s (%s)" % (fid, e["reason"], e["by"])]
    MERGED.append((e["into"], fid)); GONE[fid] = e["into"]
for e in _auto + OVR.get("merge", []):                     # unambiguous duplicate rows folded into one (applied first; later overrides see the survivor)
    if not BYID.get(e["into"]): OVR_MISSING.append(("merge", e["into"])); continue
    for fid in e["from"]: _fold(e, fid)
# Shared-recipient check (Chris 2026-11-10, Issue 3 prevention; CAPA 2026-11-10 item 5). Two rows that list the SAME person's
# address: same name or the org's own acronym, and not both already emailed -> one org, folded automatically (logged in the report).
# Anything else (different names: a board member or partner who sits on two orgs; or both rows already have a live thread)
# -> both rows carry `shared_recipient` and are held for Chris until he rules: overrides merge (same org) or shared_ok (keep both).
_SR_STOP = {"the", "of", "and", "for", "inc", "a", "an", "at", "in", "on", "llc", "co"}
_SR_GENERIC = {"association", "early", "childhood", "child", "care", "education", "children", "center", "county", "young",
               "head", "start", "family", "services", "inc", "council", "network", "program", "programs", "school", "district"}
_SR_COMMON_ACR = {"hsa", "ece", "ccr", "ccrr", "aeyc", "aimh", "cec", "dec", "ehs", "hs", "pd", "usa", "us"}
def _sr_tokens(n):
    n = re.sub(r"\(.*?\)", "", (n or "").lower())
    return {t for t in re.findall(r"[a-z0-9]+", n) if t not in _SR_STOP and t not in _SR_GENERIC}
def _sr_acrs(n):
    words = [w for w in re.findall(r"[A-Za-z]+", re.sub(r"\(.*?\)", "", n or "")) if w.lower() not in _SR_STOP]
    a = {x.lower().replace("-", "").replace("&", "") for x in re.findall(r"\b[A-Z][A-Z&-]{2,11}\b", n or "")}
    a |= {x.lower().replace("-", "") for x in re.findall(r"\(([A-Z][A-Za-z&-]{2,12})\)", n or "")}
    if len(words) >= 3: a.add("".join(w[0] for w in words).lower())
    return {x for x in a if len(x) >= 3 and x not in _SR_COMMON_ACR}
def _sr_same_name(a, b):
    A, B = _sr_tokens(a), _sr_tokens(b)
    dice = (2 * len(A & B) / (len(A) + len(B))) if A and B else 0
    return dice >= 0.75 or bool(_sr_acrs(a) & _sr_acrs(b))
_SR_OK = {tuple(sorted((GONE.get(x["a"], x["a"]), GONE.get(x["b"], x["b"])))) for x in OVR.get("shared_ok", [])}
SR_AUTO, SR_HELD = [], []
def _sr_index():
    ix = collections.defaultdict(set)
    for oid, r in BYID.items():
        if r.get("referrer"): continue
        for c_ in r["contacts"]:
            e_ = (c_.get("email") or "").lower().strip()
            if e_ and (c_.get("status") or "active") not in ("bounced",): ix[e_].add(oid)
        for t in r["threads"]:
            for m_ in t.get("messages_sent") or []:
                for e_ in (m_.get("to") or []) + (m_.get("cc") or []): ix[e_.lower()].add(oid)
    return ix
for _pass in range(3):                        # a fold can create a new shared pair; settle in at most three passes
    _changed = False
    for e_, ids in sorted(_sr_index().items()):
        ids = sorted(i for i in ids if i in BYID)
        for i_ in range(len(ids)):
            for j_ in range(i_ + 1, len(ids)):
                a, b = ids[i_], ids[j_]
                if a not in BYID or b not in BYID or (a, b) in _SR_OK: continue
                ra, rb = BYID[a], BYID[b]
                if _sr_same_name(ra["name"], rb["name"]) and not (ra["threads"] and rb["threads"]):
                    into, fid = sorted((a, b), key=lambda o: (0 if BYID[o]["threads"] else 1,) + _rank(o))
                    e = {"into": into, "from": [fid], "reason": "same recipient %s and the same name" % e_, "by": "automatic: one person + one name = one org (Chris 2026-11-10)"}
                    _fold(e, fid); SR_AUTO.append((into, fid, e_)); _changed = True
    if not _changed: break
for e_, ids in sorted(_sr_index().items()):
    ids = sorted(i for i in ids if i in BYID)
    for i_ in range(len(ids)):
        for j_ in range(i_ + 1, len(ids)):
            a, b = ids[i_], ids[j_]
            if (a, b) in _SR_OK: continue
            why = "both already have a live email thread" if (BYID[a]["threads"] and BYID[b]["threads"]) else "different names"
            for x, y in ((a, b), (b, a)):
                BYID[x].setdefault("shared_recipient", [])
                if not any(s_["email"] == e_ and s_["other_org"] == y for s_ in BYID[x]["shared_recipient"]):
                    BYID[x]["shared_recipient"].append({"email": e_, "other_org": y, "other_name": BYID[y]["name"], "why": why})
            SR_HELD.append((a, b, e_, why))
OUT = [r for r in OUT if r["org_id"] in BYID]
for fid, into in GONE.items():          # later overrides that name a merged-away row land on its survivor
    while into in GONE: into = GONE[into]
    BYID[fid] = BYID[into]

# Website hints for Head Start grantees with no website on file (Chris 2026-11-10, Issue 7): a CANDIDATE from Apollo's free lookup, never truth —
# the qualify / people helper opens it first and it becomes the org's website only when a captured page on it names the org.
for h in jl(os.path.join(paths.ROOT, "2_Discover", "ledgers", "grantee-domain-hints.jsonl")):
    r = BYID.get(GONE.get(h["org_id"], h["org_id"]))
    if r and h.get("hint") and not r["domains"]: r["domain_hint"] = h["hint"]

# ---------------------------------------------------------------- QUALIFY (Stage 5, 3_Qualify/programfiles/qualify.py) — fit decisions from verified live-page quotes
# Latest decision per org wins (append-only inbox, processed in file order). Applied after duplicate merges and BEFORE
# Chris's overrides, so his rulings always win. A machine that already has a thread with the org keeps it (Rulebook E6).
import timing as TIMING, routing as ROUTING          # 3_Qualify/programfiles (on sys.path via paths)
QI = jl(paths.QUALIFY_DECISIONS)         # 3_Qualify/ledgers/decisions.jsonl
Q_LATEST = {}
for d in QI: Q_LATEST[GONE.get(d["org_id"], d["org_id"])] = d
Q_APPLIED = collections.Counter()
def _evmatch(evs, f):
    u = (f.get("url") or "").rstrip("/"); nk = _evkey(f.get("name"))
    return next((x for x in evs if (u and (x.get("url") or "").rstrip("/") == u) or (nk and _evkey(x.get("name")) == nk)), None)
# The org's own name as printed on its site (Chris 2026-11-10, Issue 4): the newest decision that recorded one wins.
for d in QI:
    if d.get("self_name") and BYID.get(GONE.get(d["org_id"], d["org_id"])): BYID[GONE.get(d["org_id"], d["org_id"])]["self_name"] = d["self_name"]
for oid in sorted(Q_LATEST):
    d = Q_LATEST[oid]; r = BYID.get(oid)
    if not r: OVR_MISSING.append(("qualify", oid)); continue
    if d.get("evidence_hash") is None: pass
    # Retired must-have (Chris 2026-11-09, cleaned out of the ICP files 2026-11-10): "outside-keynote path; dated edition". A decision
    # that is doubtful ONLY because that retired line could not be confirmed is a fit (the helpers were told not to answer it).
    if d["decision"] == "doubtful":
        def _retired_only(why):
            parts = [x.strip().lower() for x in str(why or "").replace("unconfirmed:", "").split(";") if x.strip()]
            return bool(parts) and str(why or "").startswith("unconfirmed:") and all(x.startswith("outside-keynote path") or x == "dated edition" or x.startswith("runs its own conference with a dated edition and an outside-") for x in parts)
        _fx = sorted(i for i, v in (d.get("per_icp") or {}).items() if v.get("verdict") == "unknown" and _retired_only(v.get("why")))
        if _fx and (r["events"] or d.get("events")):     # only where a conference is actually on record
            d = dict(d, decision="fit", icps=_fx, reason="fit: the only unconfirmed line was the retired outside-keynote must-have (Rulebook E4, 2026-11-09)"); Q_APPLIED["doubtful→fit (retired must)"] += 1
    if d["decision"] in ("fit", "doubtful") and d.get("icps"): r["icps"] = sorted(d["icps"]); r["icp_basis"] = {i: "qualify %s (verified quotes)" % d.get("run") for i in r["icps"]}
    r["fit"] = {"status": d["decision"], "reason": d.get("reason"), "source": d.get("by"), "decided": d.get("decided"), "per_icp": d.get("per_icp")}
    if d["decision"] == "doubtful": r["flags"] = r["flags"] + ["⚠ doubtful fit — in the dossier for Chris's decision, not drafted (Rulebook E2)"]
    for f in d.get("events") or []:
        ev = _evmatch(r["events"], f)
        if ev is None:
            ev = {"name": f.get("name"), "url": f.get("url"), "last_edition_date": None, "next_edition_date": None, "attendance": None,
                  "cfp": {"url": None, "opens": None, "deadline": None}, "keynote_path": None, "outreach_opens": None,
                  "status": "active (found by qualify)", "large": None, "event_id": "q:" + ((f.get("url") or f.get("evidence_url") or "") + "#" + slug(f.get("name") or ""))[:180], "source": "qualify"}
            if not ev["url"]: ev["url"] = f.get("evidence_url")   # CAPA 2026-11-10 (CASE): the page qualify read is the event's page
            r["events"].append(ev)
        for k_ in ("next_edition_date", "last_edition_date", "attendance", "keynote_path", "breakout_only", "keynote_announced", "keynote_request", "dated_on_own_site", "kind", "cadence", "past_editions"):
            if f.get(k_) is not None: ev[k_] = f[k_]
        if f.get("cfp"): ev["cfp"] = dict(ev.get("cfp") or {}, **{k_: v_ for k_, v_ in f["cfp"].items() if v_})
        ev["source"] = "%s; verified by qualify %s (%s)" % (ev.get("source"), d.get("run"), f.get("evidence_url"))
    kp = ROUTING.keynote_events(r["events"])
    if d.get("events") or d["decision"] != "doubtful": r["runs_event"] = bool(kp) or r["runs_event"]   # Chris 2026-11-09: an event on record = runs an event; keynote_path/breakout_only decide nothing
    r["markets"] = ROUTING.markets(r["icps"], r["runs_event"])
    r["owner_machine"] = ROUTING.owner(r)
    Q_APPLIED[d["decision"]] += 1
# Rulebook C: an excluded org is not a fit (existing client, do-not-contact, Colorado, prior relationship). Chris's own fit rulings stand.
for r in OUT:
    ex = sorted(k_ for k_, v_ in (r.get("exclusions") or {}).items() if v_)
    if ex and r["fit"]["status"] != "not_fit" and r["fit"].get("source") != "Chris ruling":
        r["fit"] = {"status": "not_fit", "reason": "excluded (Rulebook C): " + ", ".join(ex), "source": "code (exclusion)"}
        r["owner_machine"] = ROUTING.owner(r)
# one event per edition inside an org: same name key + same edition month, or same URL -> merged (fills missing fields)
EV_MERGED = 0
for r in OUT:
    keep = []
    for ev in r["events"]:
        nk = _evkey(ev.get("name")); m7 = str(ev.get("next_edition_date") or "")[:7]; u = (ev.get("url") or "").rstrip("/")
        hit = next((x for x in keep if (nk and _evkey(x.get("name")) == nk and str(x.get("next_edition_date") or "")[:7] == m7) or (u and (x.get("url") or "").rstrip("/") == u and _evkey(x.get("name")) == nk)), None)
        if hit is None: keep.append(ev); continue
        for k_, v_ in ev.items():
            if v_ not in (None, "", {}) and hit.get(k_) in (None, "", {}): hit[k_] = v_
        hit["source"] = "%s; merged duplicate event (%s)" % (hit.get("source"), ev.get("event_id")); EV_MERGED += 1
    r["events"] = keep

for e in OVR.get("classify", []):
    r = BYID.get(e["org_id"])
    if not r: OVR_MISSING.append(("classify", e["org_id"])); continue
    if "icps" in e:
        r["icps"] = sorted(e["icps"]); r["icp_basis"] = {i: "%s (%s)" % (e["reason"], e["by"]) for i in r["icps"]}
        r["markets"] = _derive(r)
    if "fit" in e: r["fit"] = {"status": e["fit"], "reason": "%s (%s)" % (e["reason"], e["by"]), "source": "Chris ruling"}
    if not r["threads"]:   # never override a machine that already has a thread
        if r["fit"]["status"] == "not_fit" or not r["markets"]: r["owner_machine"] = "none"
        elif "MKT-002" in r["markets"]: r["owner_machine"] = "OM-2"
        else: r["owner_machine"] = "OM-1"
    if e.get("flag"): r["flags"] = r["flags"] + [e["flag"]]
    if e.get("exclude"):     # Chris: not an organization / never contact (Rulebook C) — recorded as an 'other' exclusion
        r["exclusions"]["other"] = {"why": "%s (%s)" % (e["reason"], e["by"]), "source": "overrides.json"}
        r["fit"] = {"status": "not_fit", "reason": "excluded: %s (%s)" % (e["reason"], e["by"]), "source": "Chris ruling"}
        r["owner_machine"] = "none"
for e in OVR.get("owner", []):
    r = BYID.get(e["org_id"])
    if not r: OVR_MISSING.append(("owner", e["org_id"])); continue
    r["owner_machine"] = e["owner_machine"]
    r["flags"] = [f for f in r["flags"] if not f.startswith("two machines have threads")] + ["owner %s — %s (%s)" % (e["owner_machine"], e["reason"], e["by"])]
for e in OVR.get("handoff", []):    # Chris 2026-11-03: an org with no conference moves OM-2 -> OM-1 (Rulebook E7)
    r = BYID.get(e["org_id"])
    if not r: OVR_MISSING.append(("handoff", e["org_id"])); continue
    r["handoff"] = dict({k_: e[k_] for k_ in ("from_machine", "to_machine", "prior_threads", "reason", "by")}, email1=e.get("email1") is True)
    r["owner_machine"] = e["to_machine"]
    r["flags"] = [f for f in r["flags"] if not f.startswith("owner ")] + ["⚠ handoff %s→%s — %s (%s); prior thread(s) %s — %s" % (e["from_machine"], e["to_machine"], e["reason"], e["by"], ", ".join(e["prior_threads"]),
        "new Email 1 allowed, flagged for Chris" if e.get("email1") is True else "no new sequence: they already heard from us; any next touch is Chris's personal reply on the existing thread")]
for e in OVR.get("thread_status", []):
    r = BYID.get(e["org_id"])
    t = next((t for t in (r or {}).get("threads", []) if t["thread_id"] == e["thread_id"]), None)
    if not t: OVR_MISSING.append(("thread_status", e["org_id"], e["thread_id"])); continue
    t["status"] = e["status"]; t["next_due"] = None; t["override"] = "%s (%s)" % (e["reason"], e["by"])
for e in OVR.get("review_hold", []):
    r = BYID.get(e["org_id"])
    if not r: OVR_MISSING.append(("review_hold", e["org_id"])); continue
    r["review_hold"] = {"reason": e["reason"], "by": e["by"]}
    r["flags"] = r["flags"] + ["REVIEW HOLD — draft for Chris, never auto-send (%s)" % e["by"]]
    for t in r["threads"]:
        if (e.get("thread_id") in (None, t["thread_id"])) and t["status"] == "open":
            t["review_hold"] = True
            if t["next_due"]: t["next_due"] = "REVIEW HOLD (draft for Chris, do not send) — " + t["next_due"]
if OVR_MISSING: print("OVERRIDES NOT APPLIED (org/thread not found):", OVR_MISSING)


# Event overrides (Chris / Stage 7): set fields on one event of one org, matched by name substring (case-insensitive) or URL.
for e in OVR.get("event", []):
    r = BYID.get(e["org_id"])
    if not r: OVR_MISSING.append(("event", e["org_id"])); continue
    hit = [ev for ev in r["events"] if (e.get("match") or "").lower() in (ev.get("name") or "").lower() or (e.get("url") and (ev.get("url") or "").rstrip("/") == e["url"].rstrip("/"))]
    if not hit: OVR_MISSING.append(("event", e["org_id"], e.get("match"))); continue
    for ev in hit:
        ev.update(e.get("set") or {})
        ev["source"] = "%s; override: %s (%s)" % (ev.get("source"), e["reason"], e["by"])
    r["flags"] = r["flags"] + ["event override — %s (%s)" % (e["reason"], e["by"])]

# ---------------------------------------------------------------- TIMING (Stage 5, Rulebook F) — every event, every rebuild, as of settings.as_of
# outreach_opens + outreach_status on each event; the org's best event in r["outreach"] (OM-2 orgs). The night run advances
# as_of each night (qualify set-date), so newly due events open on their own.
TIMING_COUNT = collections.Counter(); REROUTED = collections.Counter()
for r in OUT:
    res = []
    for ev in r["events"]:
        t_ = TIMING.compute(ev, AS_OF)
        ev["outreach_opens"] = t_["outreach_opens"]; ev["outreach_status"] = t_["status"]; ev["outreach_why"] = t_["why"]
        ev["edition_date"] = t_["edition_date"]
        # Rulebook E3 (Chris 2026-11-10): an event counts toward OM-2 only when it is a conference (an event type that needs a
        # keynote) AND there is a sign it happens in the coming year. Training days / staff trainings and stale one-off editions do not.
        k_ = TIMING.kind(ev); rec_ok, rec_why = TIMING.will_recur(ev, AS_OF)
        ev["kind_used"] = k_; ev["counts_for_om2"] = bool(k_ == "conference" and rec_ok)
        ev["counts_why"] = ("conference; " + rec_why) if ev["counts_for_om2"] else ("event type is %s" % k_ if k_ != "conference" else rec_why)
        if str(ev.get("status") or "active").startswith("active") and ev["counts_for_om2"]:
            res.append(dict(t_, event=ev.get("name"), url=ev.get("url") or ev.get("evidence_url")))
    # no counting conference -> not an OM-2 org (E3). Never moves an org that already has a thread, a handoff, or Chris's own owner ruling.
    if r["owner_machine"] == "OM-2" and not r["threads"] and not r.get("handoff") and not any(str(f).startswith("owner ") for f in r["flags"]) and not res:
        act = [ev for ev in r["events"] if str(ev.get("status") or "active").startswith("active")]
        r["runs_event"] = False; r["markets"] = ROUTING.markets(r["icps"], False); r["owner_machine"] = ROUTING.owner(r)
        r["routing_note"] = "not OM-2 (Rulebook E3): " + ("; ".join("%s — %s" % (ev.get("name") or "unnamed event", ev["counts_why"]) for ev in act[:4]) or "no event on record")
        r["routing_unclear"] = any(ev["kind_used"] == "unclear" for ev in act)
        REROUTED[r["owner_machine"]] += 1
    r["outreach"] = TIMING.org_summary(res) if (r["owner_machine"] == "OM-2" or "MKT-002" in r["markets"]) else None
    if r["outreach"]: TIMING_COUNT[r["outreach"]["status"].split(" ")[0]] += 1

# ---------------------------------------------------------------- PEOPLE (Stage 6, 4_People/programfiles/people.py) — checked contacts + the ready recipient set
# Latest decision per org wins (append-only inbox, file order). Contacts carry their checks (live page / auto-reply, Apollo,
# validity). r["recipients"] = the ready set (1 To + up to 3 Cc, greeting) for Stage 7, or None with r["people_hold"] = why.
PI = jl(paths.PEOPLE_DECISIONS)          # 4_People/ledgers/decisions.jsonl
P_LATEST = {}
for d in PI: P_LATEST[GONE.get(d["org_id"], d["org_id"])] = d
P_APPLIED = collections.Counter()
for oid in sorted(P_LATEST):
    d = P_LATEST[oid]; r = BYID.get(oid)
    if not r: OVR_MISSING.append(("people", oid)); continue
    if d.get("domain_discovered") and d["domain_discovered"] not in (r.get("domains") or []):   # people step found the org's own site (2026-11-03)
        r["domains"] = sorted(set(r.get("domains") or []) | {d["domain_discovered"]})
    have = {c_["email"]: c_ for c_ in r["contacts"]}
    for c_ in d.get("contacts") or []:
        x = have.get(c_["email"])
        if x is None:
            x = {"email": c_["email"], "name": c_.get("name"), "role": c_.get("role"), "evidence_url": c_.get("evidence_url"),
                 "verification": {"apollo": None, "zerobounce": None, "class": None}, "status": "active", "source": []}
            r["contacts"].append(x); have[c_["email"]] = x
        for k_ in ("name", "role", "evidence_url"):
            if c_.get(k_) and not x.get(k_): x[k_] = c_[k_]
        x["verification"] = dict(x.get("verification") or {}, **{k_: v_ for k_, v_ in (c_.get("verification") or {}).items() if v_})
        if c_.get("status") == "departed" and x.get("status") == "active": x["status"] = "departed"
        x["source"] = sorted(set(x.get("source") or []) | {"people %s" % d.get("run")})
    r["contacts"].sort(key=lambda c_: c_["email"])
    if d.get("self_name"): r["self_name"] = d["self_name"]          # the org's own printed name (Chris 2026-11-10, Issue 4)
    if d["decision"] == "ready":
        r["recipients"] = dict(d["recipients"], decided=d.get("decided"), by=d.get("by")); r["people_hold"] = None; r["roster_line"] = d.get("roster_line")
    else:
        r["recipients"] = None; r["people_hold"] = {"reason": d.get("hold_reason"), "unblock": d.get("unblock"), "decided": d.get("decided")}; r["roster_line"] = d.get("roster_line")
    for f_ in d.get("flags") or []:
        if f_.startswith("⚠") and f_ not in r["flags"]: r["flags"] = r["flags"] + [f_]
    P_APPLIED[d["decision"]] += 1

# Guard (Chris 2026-10-31): a record whose id, name or domain looks like a run folder ("__run_") is not an
# organization (it was built from a run folder) — it never reaches the master list.
def _is_run_folder(r):
    return any("__run_" in str(v) for v in [r.get("org_id"), r.get("name")] + list(r.get("domains") or []))
JUNK_DROPPED = sorted(r["org_id"] for r in OUT if _is_run_folder(r))
OUT = [r for r in OUT if not _is_run_folder(r)]
if JUNK_DROPPED: print("dropped %d run-folder record(s): %s" % (len(JUNK_DROPPED), ", ".join(JUNK_DROPPED)))
OUT.sort(key=lambda r: r["org_id"])
with open(P("orgs", "outputs"), "w", encoding="utf-8") as f:
    for r in OUT: f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")

# ---------------------------------------------------------------- CSV view
buf = io.StringIO(); w = csv.writer(buf, lineterminator="\n")
w.writerow(["READ-ONLY VIEW generated from orgs.jsonl (the master list) by build_master.py on as_of " + S["as_of"] + " — edits here are lost on rebuild"])
w.writerow(["org_id", "name", "state", "icps", "markets", "owner_machine", "fit", "fit_reason", "exclusions", "thread_stage_status", "next_due", "events", "contacts", "referrer", "flags"])
for r in OUT:
    ex = "; ".join("%s: %s" % (k, v["why"]) for k, v in r["exclusions"].items() if v)
    th = "; ".join("%s %s %s" % (t["machine"], t["stage"], t["status"]) for t in r["threads"])
    nd = "; ".join(t["next_due"] for t in r["threads"] if t["next_due"])
    ev = " | ".join("%s (%s) %s" % (e["name"], e["next_edition_date"] or "date ?", e["url"] or "") for e in r["events"])
    ct = " | ".join("%s%s%s" % (c_["name"] + " " if c_["name"] else "", c_["email"], "" if c_["status"] == "active" else " [" + c_["status"] + "]") for c_ in r["contacts"])
    w.writerow([r["org_id"], r["name"], r["state"], ",".join(r["icps"]), ",".join(r["markets"]), r["owner_machine"], r["fit"]["status"],
                (r["fit"]["reason"] or "")[:200], ex[:300], th, nd, ev[:1000], ct[:1000], "yes" if r["referrer"] else "", "; ".join(r["flags"])])
open(P("csv", "outputs"), "w", encoding="utf-8").write(buf.getvalue())

# ---------------------------------------------------------------- report (counts; deterministic)
L = []
A = L.append
A("# Master list — build report (as_of %s)\n" % S["as_of"])
A("Generated by build_master.py. Counts only; the plain-English summary for Chris lives in the session report.\n")
A("## Totals\n")
A("| | count |\n|---|---|")
A("| organizations | %d |" % len(OUT))
A("| contacts | %d |" % sum(len(r["contacts"]) for r in OUT))
A("| events | %d |" % sum(len(r["events"]) for r in OUT))
A("| threads | %d |" % sum(len(r["threads"]) for r in OUT))
A("| owner OM-1 / OM-2 / none | %d / %d / %d |" % tuple(sum(1 for r in OUT if r["owner_machine"] == x) for x in ("OM-1", "OM-2", "none")))
for x in ("fit", "doubtful", "not_fit", "unreviewed"): A("| fit = %s | %d |" % (x, sum(1 for r in OUT if r["fit"]["status"] == x)))
for x in ("existing_client", "do_not_contact", "colorado", "prior_relationship"): A("| excluded: %s | %d |" % (x, sum(1 for r in OUT if r["exclusions"].get(x))))
A("| referrers (never emailed) | %d |" % sum(1 for r in OUT if r["referrer"]))
A("\n## Reconciliation by source\n")
A("| source | rows read | matched existing org | created org | skipped | note |\n|---|---|---|---|---|---|")
for k, v in RECON.items(): A("| %s | %s | %s | %s | %s | %s |" % (k, v["read"], v["matched"], v["created"], v["skipped"], v["note"]))
A("\n## Threads by machine · stage · status\n")
A("| machine | stage | status | threads |\n|---|---|---|---|")
for (mch, stg, sts), n in sorted(STAGE_COUNT.items()): A("| %s | %s | %s | %d |" % (mch, stg, sts, n))
A("\n## Overdue follow-ups (next slot %s 07:00 ET)\n" % NEXT_SLOT.isoformat())
for mch, n in sorted(OVERDUE.items()): A("- %s: %d" % (mch, n))
A("\n## Gmail vs ledger\n")
A("- stage disagreements (Gmail label vs ledger dates): %d" % len(FINDINGS["stage_disagree"]))
_c = collections.Counter(x[3] for x in FINDINGS["stage_disagree"])
for kk, vv in sorted(_c.items()): A("  - %s: %d" % (kk, vv))
for x in sorted(FINDINGS["stage_disagree"])[:12]: A("  - thread %s: ledger %s · Gmail %s (%s)" % x)
A("- open threads whose current stage has no known send date (needs the sender's fresh read): %d" % len(FINDINGS["undated"]))
A("- date disagreements (>1 day): %d" % len(FINDINGS["date_disagree"]))
for x in sorted(FINDINGS["date_disagree"])[:15]: A("  - thread %s email %s: ledger %s · Gmail %s" % x)
A("- Gmail threads not in any ledger, attached by recipient domain: %d" % len(FINDINGS["gmail_only_threads"]))
for x in sorted(FINDINGS["gmail_only_threads"])[:15]: A("  - %s · %s · %s" % (x[0], x[1], ",".join(x[2])))
A("- Gmail-state: Chris's sends found only by complete sent windows (added; date = latest day of window): %d" % len(FINDINGS["gs_window_send"]))
A("- Gmail-state: ledger/window dates merged into one email (< 5 days apart; later Gmail date kept): %d" % len(FINDINGS["date_merged"]))
A("- Gmail-state: duplicate own sends collapsed (Rule 3a, < 24 h apart): %d" % len(FINDINGS["duplicate_sends"]))
for x in sorted(set(FINDINGS["duplicate_sends"])): A("  - thread %s · %s" % x)
A("- Gmail-state: outreach threads in Gmail not attachable to an org (need a full read): %d" % len(FINDINGS["gs_unattached"]))
for x in sorted(FINDINGS["gs_unattached"]): A("  - %s · %s · read=%s · sent window %s" % x)
A("- Gmail-state: separate-thread human replies whose sender matched no org: %d" % len(FINDINGS["gs_human_unmatched"]))
for x in sorted(FINDINGS["gs_human_unmatched"]): A("  - %s · thread %s · %s" % x)
A("- Gmail threads that could not be attached to any org: %d" % len(FINDINGS["gmail_orphans"]))
for x in sorted(FINDINGS["gmail_orphans"])[:30]: A("  - %s · %s" % (x[0], ",".join(x[1])))
A("\n## Two machines have threads (%d)\n" % len(TWO))
for n, k, own in sorted(TWO, key=lambda x: str(x[0])): A("- %s → owner by rule %s" % (n, own))
A("\n## Qualify (Stage 5)\n")
A("- decisions applied: %s · duplicate events merged: %d" % (dict(sorted(Q_APPLIED.items())) or "none yet", EV_MERGED))
A("- OM-2 outreach timing (as of %s): %s" % (S["as_of"], dict(sorted(TIMING_COUNT.items()))))
A("- Moved out of OM-2 because no conference on record counts (Rulebook E3, 2026-11-10): %s" % (dict(sorted(REROUTED.items())) or "none"))
A("\n## Same person on two rows (Chris 2026-11-10): %d folded automatically · %d pairs held for Chris\n" % (len(SR_AUTO), len(SR_HELD)))
for a_, b_, e_, w_ in SR_HELD: A("- HELD %s + %s — share %s (%s)" % (a_, b_, e_, w_))
for a_, b_, e_ in SR_AUTO: A("- folded %s into %s — share %s" % (b_, a_, e_))
A("\n## Duplicate rows merged (overrides.json merge) (%d)\n" % len(MERGED))
for a_, b_ in MERGED: A("- %s ← %s" % (a_, b_))
A("\n## Possible duplicates kept separate (same name + state, different identity) (%d)\n" % len(AMBIG))
for n, s_, v in AMBIG[:60]: A("- %s (%s): %s" % (n, s_, ", ".join(v)))
A("\n## Event-running orgs outside ICP-001–004 (%d)\n" % len(FINDINGS["event_org_outside_icps"]))
for n, k in sorted(FINDINGS["event_org_outside_icps"], key=lambda x: str(x[0]))[:40]: A("- %s" % n)
open(P("report", "outputs"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("orgs=%d contacts=%d events=%d threads=%d" % (len(OUT), sum(len(r["contacts"]) for r in OUT), sum(len(r["events"]) for r in OUT), sum(len(r["threads"]) for r in OUT)))
