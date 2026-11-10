#!/usr/bin/env python3
"""draft.py -- Stage 7: Email 1 drafts for every machine (Rulebook C, G7, I1, L, M; Chris 2026-10-30/31).

Code decides and fills; the AI never writes copy. Only the greeting and the org's short name vary (Rulebook C6).
Each draft is created by Zapier (clean links, real PDF attached, Rulebook C7), labeled <machine>/0 at creation,
then proven by Gate 7 on the RAW message (attachment bytes, unwrapped links, HubSpot Bcc, recipients, subject).
Email 1 is never sent by a machine (C1): Chris adds the GIF and sends it.

  python3 draft.py next --run <date>       the state machine: prints the ONE next step (labels -> select + Gmail
                                            checks -> gate -> create -> verify -> record -> done)
  python3 draft.py show --run <date> --n N print row N's exact Zapier params (placeholders {{SIGNATURE}} {{E1_FILE}})
  python3 draft.py candidates [--machine OM-1|OM-2]    read-only: who is eligible tonight and why others are not
  python3 draft.py render --machine OM-1|OM-2 --greeting "Carrie and Stephanie"   print the body HTML
Run folder: 5_Draft/runs/<run>/ (raw/ holds every Gmail/Zapier result saved VERBATIM).
"""
import argparse, collections, datetime, html, json, os, re, sys

import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_shared", "orchestrator")); import paths  # the one file that knows every folder (2026-11-03)
ENG = paths.ROOT
MASTER = paths.MASTER
S = paths.settings()
ROOT = paths.MASTER
MKT = paths.MARKETING
D = S["draft"]
M = {k: paths.mset(k) for k in ("minimum", "max_per_night", "subject", "template", "attachment")}   # per-machine settings, from the machines block (2026-11-03)
ME = "chris@chrisdanilo.com"
MACHINES = paths.machines()
LABEL_TREE = list(MACHINES) + ["%s/%s" % (m, x) for m in MACHINES for x in ("0", "1", "2", "3", "★", "✗", "⚠", "⏸")]
# REHEARSAL (Stage 8, 2026-10-31): a run named "rehearsal-…" addresses every draft ONLY to Chris (no Cc), prefixes the subject,
# labels it OM-TEST (not <machine>/0), records nothing in the master list, and ends by printing the delete orders.
TEST_LABEL = "OM-TEST"
REH_CAP = int(S.get("night", {}).get("rehearsal_caps", {}).get("draft_per_machine", 1))
def is_reh(d): return os.path.basename(d).startswith("rehearsal")   # run folder = 5_Draft/runs/<run> (2026-11-03)
def allowance(d):
    """The night run (untimed loop, Chris 2026-10-31) writes <run folder>/allowance.json before each pass's draft step:
    {machine: drafts still allowed tonight}. 0 = that machine already met its minimum (or its ceiling) — not drafted this pass.
    No file = a standalone run: the nightly ceiling applies."""
    a = None
    p = os.path.join(d, "allowance.json")
    if os.path.exists(p): a = json.load(open(p, encoding="utf-8"))
    out = {}
    for m in MACHINES:
        base = REH_CAP if is_reh(d) else M["max_per_night"][m]
        out[m] = max(0, min(base, int(a.get(m, base)))) if a is not None else base
    return out


def P(s):
    return paths.expand(s)


def jl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()] if os.path.exists(p) else []


def ajl(p, rows):
    with open(p, "a", encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")


def wj(p, o):
    with open(p, "w", encoding="utf-8") as f: json.dump(o, f, ensure_ascii=False, indent=1, sort_keys=True)


def rj(p, default=None):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else default


def dom(a):
    return str(a or "").strip().lower().rsplit("@", 1)[-1]


# ------------------------------------------------------------------ copy (verbatim from the approved template files)
def _esc(s):
    return html.escape(s, quote=False).replace("'", "&#39;").replace('"', "&quot;")


def _inline(t):
    out, pos = [], 0
    for m in re.finditer(r"\*\*(.+?)\*\*|(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", t):
        out.append(_esc(t[pos:m.start()]))
        if m.group(1) is not None:
            inner = m.group(1)
            if re.fullmatch(r"https?://\S+", inner):
                out.append('<b><a href="%s" target="_blank">%s</a></b>' % (inner, _esc(inner)))
            else:
                out.append("<b>%s</b>" % _inline(inner))
        else:
            out.append("<i>%s</i>" % _esc(m.group(2)))
        pos = m.end()
    out.append(_esc(t[pos:]))
    return "".join(out)


def e1_markdown(machine):
    """The Email 1 body block of the machine's template: from the bare '{Names},' line to the next '---'.
    The GIF placeholder line ('[▶ ...') is dropped: Chris inserts the GIF by hand; nothing in its place ships."""
    txt = open(P(M["template"][machine]), encoding="utf-8").read()
    start = txt.index("## Email 1")
    lines = txt[start:].split("\n")
    i = next(i for i, l in enumerate(lines) if l.strip() == "{Names},")
    j = next(j for j in range(i + 1, len(lines)) if lines[j].strip() == "---" or lines[j].startswith("### ") or lines[j].startswith("## "))
    body = [l for l in lines[i:j] if not l.strip().startswith("[▶")]
    return "\n".join(body).strip()


def render_md(body_md):
    paras = [p for p in re.split(r"\n\s*\n", body_md.strip()) if p.strip()]
    assert paras[0].strip() == "{Names},", "Email 1 template must open with the bare '{Names},' line"
    blocks = []
    first = "{Names},<br><br>" + _inline(" ".join(l.strip() for l in paras[1].split("\n")))
    blocks.append("<p>%s</p>" % first)
    for p in paras[2:]:
        ls = [l.rstrip() for l in p.split("\n") if l.strip()]
        if all(l.lstrip().startswith("- ") for l in ls):
            blocks.append("<ul>\n" + "\n".join("<li>%s</li>" % _inline(l.lstrip()[2:].strip()) for l in ls) + "\n</ul>")
        else:
            blocks.append("<p>%s</p>" % _inline(" ".join(l.strip() for l in ls)))
    return '<div dir="ltr">\n<div>\n' + "\n".join(blocks) + "\n</div>\n</div>"


def e1_html_block(machine):
    txt = open(P(M["template"][machine]), encoding="utf-8").read()
    m = re.search(r"### Email 1 — body HTML.*?```html\n(.*?)```", txt, re.S)
    return m.group(1).strip() if m else None


def e1_template(machine):
    """OM-2 ships its approved HTML block as written; OM-1 (no HTML block) is rendered from its markdown by fixed rules
    (config draft_writer.html_rules: <p> per paragraph, results as <ul><li>, **bold** -> <b>, *can* -> <i>, video as a link)."""
    blk = e1_html_block(machine)
    return blk if blk else render_md(e1_markdown(machine))


def text_of_html(h):
    h = re.sub(r"<br\s*/?>", "\n", h)
    h = re.sub(r"</(p|li|ul|div)>", "\n", h)
    t = html.unescape(re.sub(r"<[^>]+>", "", h))
    return re.sub(r"\s+", " ", t).strip()


def text_of_md(md):
    md = "\n".join(l for l in md.split("\n") if not l.strip().startswith("[▶"))
    md = re.sub(r"^\s*-\s+", "", md, flags=re.M)
    md = md.replace("**", "")
    md = re.sub(r"(?<![\w*])\*(\w[^*]*?)\*(?![\w*])", r"\1", md)
    return re.sub(r"\s+", " ", md).strip()


def body_for(machine, greeting):
    t = e1_template(machine)
    if "{Names}" not in t: raise SystemExit("FAIL CLOSED: %s Email 1 template has no {Names}" % machine)
    return t.replace("{Names}", _esc(greeting))


# ------------------------------------------------------------------ subject short name + greeting
BOILER = [(r"^the\s+", ""), (r",?\s+(inc\.?|llc|incorporated)$", ""), (r"^early learning coalition of\s+", "ELC "),
          (r"^child care council of\s+", "Child Care "), (r"\s+county$", " County")]


def cards_shorts():
    out = {}
    for c in jl(P(S["inputs"].get("m2_cards_bank", ""))) if S["inputs"].get("m2_cards_bank") else []:
        d = (c.get("org_domain") or "").lower()
        if d and c.get("short"): out[d] = c["short"]
    return out


STATE_CODES = set("AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA PR RI SC SD TN TX UT VT VA WA WV WI WY ON BC AB MB SK QC NS NB NL PE".split())
LEGAL = {"INC", "LLC", "LTD", "CORP", "CO", "PLLC", "PC", "NFP", "NPO"}
SMALL = {"of", "the", "and", "for", "&", "in", "at", "on", "a", "an", "inc", "inc.", "llc", "de", "la", "del", "y"}


def _initials(name):
    w = [x for x in re.split(r"[\s,\-–/&().]+", name or "") if x and x.lower() not in SMALL]
    return "".join(x[0] for x in w if x[0].isalpha()).upper()


def short_name(o, shorts=None):
    """The subject's org name — the OM-1 rule Chris ratified 2026-08-12/14 (method.md Phase 3, restored 2026-11-06):
    ALWAYS a short form. (1) the org's own short brand (research card, an acronym it prints after its name, or its domain
    when the domain IS its initials: ecin.org → ECIN, cciu.org → CCIU, bcesc.org → BCESC); (2) else a plain shortening of its
    own formal name — keep the distinguishing words, drop boilerplate (', Inc.', 'Early Learning Coalition of' → 'ELC'),
    cut at a dash or colon. Never invent an acronym; never use a legal suffix as a name; no all-caps shouting."""
    shorts = shorts if shorts is not None else cards_shorts()
    for d in o.get("domains") or []:
        if shorts.get(d): return shorts[d], "the org's short name from Machine 2's research card"
    for n in [o["name"]] + list(o.get("aliases") or []):
        for m in re.finditer(r"\(([A-Z][A-Za-z&]{1,11})\)", n or ""):
            if m.group(1).upper() not in LEGAL: return m.group(1), "the org's own acronym (%s)" % n
    for n in o.get("aliases") or []:
        if re.fullmatch(r"[A-Z][A-Z&]{1,9}", (n or "").strip()) and n.strip() not in LEGAL: return n.strip(), "the org's own acronym"
    ini = _initials(re.sub(r"\s*\([^)]*\)", "", o["name"] or ""))
    rec = o.get("recipients") or {}
    mail_doms = [p_["email"].split("@")[-1].lower() for p_ in ([rec.get("to")] if rec.get("to") else []) + list(rec.get("cc") or []) if p_ and p_.get("email")]
    for d in list(o.get("domains") or []) + [x for x in mail_doms if x not in (o.get("domains") or [])]:   # the org's site AND its staff's email domain (cfsri.org)
        stem = re.sub(r"^www\.", "", d.lower()).split(".")[0]
        if stem.isalpha() and 3 <= len(stem) <= 8 and ini.startswith(stem.upper()) and len(stem) >= min(3, len(ini)):
            return stem.upper(), "the org's acronym, as used in its own domain (%s)" % d
        # initials + a state/province code in the domain: cfsri.org (Children's Friend and Service, RI) → CFS (Chris 2026-11-06)
        if stem.isalpha() and len(ini) >= 3 and stem.upper().startswith(ini) and stem.upper()[len(ini):] in STATE_CODES \
                and stem.upper()[len(ini):] == (o.get("state") or "").upper():   # the code must be the org's own state (soesd ≠ SOE + SD)
            return ini, "the org's acronym, as used in its own domain (%s, + state code)" % d
    s = re.sub(r"\s*\([^)]*\)", "", o["name"] or "").strip()
    s = re.split(r"\s+[-–—:|]\s+", s)[0].strip()
    for pat, rep in BOILER: s = re.sub(pat, rep, s, flags=re.I).strip()
    s = re.sub(r"[,\s]+$", "", s)
    if s.isupper() and " " in s:      # 'CAGUAS MUNICIPALITY …' → 'Caguas Municipality …' (one-word codes like MHSA-MS stay)
        s = " ".join(w if w in ("ECE", "PD", "ESC", "ESD", "ISD", "USD", "CAA") else (w.lower() if i and w.lower() in SMALL else w.capitalize())
                     for i, w in enumerate(s.split()))
    if len(s.replace(" ", "")) <= 5 and s.upper() not in ("ECIN",):   # 'Child' from 'Child, Inc.' — too thin: keep the formal name
        s = re.sub(r"\s*\([^)]*\)", "", o["name"] or "").strip()
    return s, "formal name shortened by rule — check before sending"


def e1_greeting(machine, rec_greeting, short):
    """Email 1 greeting = bare names, no salutation word (both templates). Stage 6 stores 'Hi A, B and C,'."""
    g = re.sub(r"^\s*(hi|hey|hello|dear)\s+", "", rec_greeting or "", flags=re.I).strip().rstrip(",").strip()
    if not g or re.fullmatch(r".*\bteam", g) and " and team" not in g:
        return ("%s conference team" % short) if machine == "OM-2" else ("Hi %s team" % short)
    return g


# ------------------------------------------------------------------ eligibility (Rulebook C, E, F, G) — code only
def load_orgs():
    return [json.loads(l) for l in open(paths.ORGS, encoding="utf-8")]


def indexes(orgs):
    client_doms, bad_addr, thread_dom = set(), {}, {}
    for o in orgs:
        if (o.get("exclusions") or {}).get("existing_client"):
            client_doms |= set(o.get("domains") or [])
            # Rulebook B4 patch 1 (Chris 2026-11-10): every domain a client's own contacts use is a client domain (never free-mail / shared tenants)
            _never = set(D["free_mail_domains"]) | {x for v in S["machines"].values() for x in (v.get("shared_tenant_domains") or [])} | {"chrisdanilo.com"}
            client_doms |= {c["email"].lower().split("@")[-1] for c in o.get("contacts") or [] if "@" in (c.get("email") or "")} - _never
        for c in o.get("contacts") or []:
            if c.get("status") in ("bounced", "departed", "do_not_contact"): bad_addr[c["email"].lower()] = c["status"]
        if o.get("threads"):
            for d in o.get("domains") or []: thread_dom[d] = o["org_id"]
    dnc = jl(P(S["inputs"]["dnc_register"])) if S["inputs"].get("dnc_register") else []
    for r in dnc:
        for k in ("email", "address"):
            if r.get(k): bad_addr[r[k].lower()] = "do_not_contact"
        for k in ("domain",):
            if r.get(k) and r.get("scope") != "person": client_doms.add(("dnc", r[k].lower()))   # person scope blocks the address only
    return client_doms, bad_addr, thread_dom


def why_not(o, idx, redo=False):
    """None = eligible; else the reason (plain English).
    redo=True (Chris 2026-11-04): the org is being RE-drafted — its only threads are unsent Email 1 drafts, which the new draft replaces."""
    client_doms, bad_addr, thread_dom = idx
    m = o.get("owner_machine")
    if m not in MACHINES: return "no owning machine"
    if o.get("referrer"): return "warm referrer — never emailed (D5)"
    ho = o.get("handoff") or {}
    if o.get("threads") and not (redo and all(not (t.get("messages_sent") or []) for t in o["threads"])):
        prior = set(ho.get("prior_threads") or [])
        live = [t for t in o["threads"] if t["thread_id"] not in prior or t.get("status") not in ("stopped", "closed✗")]
        # a handoff opens a NEW Email 1 only when Chris says so (email1: true) — never for an org that already heard
        # from us and answered (Chris 2026-11-03: no top-of-sequence email after a reply)
        if not (ho.get("to_machine") == m and ho.get("email1") is True and not live):
            return "already has a thread (one thread per org, C2)"
    if o["fit"]["status"] == "doubtful": return "doubtful fit — in the dossier for Chris's decision, not drafted (Rulebook E2)"
    if o["fit"]["status"] != "fit": return "fit is %s" % o["fit"]["status"]
    ex = [k for k, v in (o.get("exclusions") or {}).items() if v]
    if ex: return "excluded: " + ", ".join(ex)
    if (o.get("state") or "").upper() == "CO": return "Colorado (C5)"
    if m == "OM-2" and ((o.get("outreach") or {}).get("status") or "") != "open_now":
        return "outreach not open (%s)" % ((o.get("outreach") or {}).get("status") or "no event on record")
    rec = o.get("recipients")
    if not rec or not rec.get("to"): return "no ready recipient set (Stage 6: %s)" % ((o.get("people_hold") or {}).get("reason") or "not yet run")
    free = set(D["free_mail_domains"])
    for i, p in enumerate([rec["to"]] + list(rec.get("cc") or [])):
        e = p["email"].lower(); d = dom(e)
        if e in bad_addr and i == 0: return "To address %s is %s" % (e, bad_addr[e])
        if d in client_doms or ("dnc", d) in client_doms: return "recipient domain %s belongs to an existing client / do-not-contact (C3/C4)" % d
        if d not in free and d in thread_dom and thread_dom[d] != o["org_id"] and d not in (o.get("domains") or []):
            return "recipient domain %s belongs to another org that already has a thread (C2)" % d
    return None


def priority(o):
    m = o["owner_machine"]
    if m == "OM-2":
        oo = o.get("outreach") or {}
        # Chris 2026-11-10: events 3-9 months out are drafted first, then 1-3 months, then no date — never simply the soonest event
        try: days = (datetime.date.fromisoformat(oo["edition_date"]) - datetime.date.fromisoformat(oo["outreach_opens"])).days
        except Exception: days = None
        band = 2 if days is None else 0 if days >= 89 else 1
        return (0, band, oo.get("edition_date") or "9999", o["org_id"])
    icp_rank = min([{"ICP-001": 0, "ICP-002": 1, "ICP-003": 2, "ICP-005": 3}.get(i, 9) for i in o["icps"]] or [9])
    return (1, 0 if o["fit"]["status"] == "fit" else 1, icp_rank, o["org_id"])


def recipients_of(o, idx):
    """To + Cc from Stage 6, dropping a bounced/departed/DNC Cc (flagged)."""
    _, bad_addr, _ = idx
    rec = o["recipients"]; flags = []
    cc = []
    for p in rec.get("cc") or []:
        if p["email"].lower() in bad_addr: flags.append("Cc %s dropped (%s)" % (p["email"], bad_addr[p["email"].lower()])); continue
        cc.append(p)
    return rec["to"], cc, flags


def sent_queries(o, to, cc):
    free = set(D["free_mail_domains"])
    terms = []
    for d in sorted(set(o.get("domains") or []) | {dom(p["email"]) for p in [to] + cc}):
        if d and d not in free: terms.append(d)
    addrs = sorted({p["email"].lower() for p in [to] + cc if dom(p["email"]) in free})
    keys = terms + addrs
    q = "in:anywhere {%s}" % " ".join("from:%s to:%s cc:%s" % (k, k, k) for k in keys)
    dq = "{%s}" % " ".join("to:%s cc:%s" % (k, k) for k in keys)
    return q, dq


# ------------------------------------------------------------------ run folder + state
def rdir(run):
    d = os.path.join(paths.runs("draft"), run); os.makedirs(os.path.join(d, "raw"), exist_ok=True); return d


def st_load(d): return rj(os.path.join(d, "state.json"), {})
def st_save(d, s): wj(os.path.join(d, "state.json"), s)


def label_ids(d):
    j = rj(os.path.join(d, "raw", "labels.json"))
    if j is None: return None, None
    labs = {x["name"]: (x.get("id") or x.get("labelId")) for x in (j.get("labels") if isinstance(j, dict) else j) or []}  # Gmail returns labelId
    want = LABEL_TREE + ([TEST_LABEL] if is_reh(d) else [])
    return labs, [w for w in want if w not in labs]


def find_key(obj, names):
    if isinstance(obj, dict):
        for k in names:
            if isinstance(obj.get(k), str) and obj[k]: return obj[k]
        for v in obj.values():
            r = find_key(v, names)
            if r: return r
    if isinstance(obj, list):
        for v in obj:
            r = find_key(v, names)
            if r: return r
    return None


def search_count(p):
    j = rj(p)
    if j is None: return None
    for k in ("threads", "drafts"):
        if isinstance(j, dict) and isinstance(j.get(k), list): return len(j[k])
    if isinstance(j, dict) and not j: return 0          # {} = zero matching items
    if isinstance(j, list): return len(j)
    return len(find_list(j))


def find_list(j):
    if isinstance(j, dict):
        for v in j.values():
            if isinstance(v, list): return v
    return []


# ------------------------------------------------------------------ steps
def step_select(d, s):
    orgs = load_orgs(); idx = indexes(orgs); shorts = cards_shorts()
    redo = s.get("redo") or {}
    if redo: orgs = [o for o in orgs if o["org_id"] in redo]
    elig, why = [], collections.Counter()
    for o in orgs:
        w = why_not(o, idx, redo=bool(redo))
        if w: why[(o.get("owner_machine"), w.split(" (")[0].split(":")[0])] += 1; continue
        elig.append(o)
    elig.sort(key=priority)
    cands = []
    for m in MACHINES:
        allow = len(redo) if redo else allowance(d)[m]
        if allow <= 0: continue          # the night loop is not working this machine this pass
        pool = [o for o in elig if o["owner_machine"] == m][: (allow + 2) if is_reh(d) else int(allow * 1.5) + 2]
        for o in pool:
            to, cc, fl = recipients_of(o, idx)
            short, how = short_name(o, shorts)
            g = e1_greeting(m, o["recipients"].get("greeting"), short)
            q, dq = sent_queries(o, to, cc)
            cands.append({"n": len(cands) + 1, "org_id": o["org_id"], "org_name": o["name"], "org_domain": (o.get("domains") or [None])[0],
                          "domains": o.get("domains") or [], "state": o.get("state"), "machine": m, "priority": list(priority(o)),
                          "to": to, "cc": cc, "greeting": g, "short": short, "short_how": how,
                          "subject": M["subject"][m].replace("{Short}", short), "flags": fl + [f for f in o.get("flags") or [] if f.startswith("⚠")],
                          "event": (o.get("outreach") or {}).get("event"), "edition_date": (o.get("outreach") or {}).get("edition_date"),
                          "why": (o.get("outreach") or {}).get("why"), "all_events": (o.get("outreach") or {}).get("all_events"), "best_fit_why": (o.get("outreach") or {}).get("best_fit_why"),
                          "query_sent": q, "query_drafts": dq, "prior_threads": (o.get("handoff") or {}).get("prior_threads") or [],
                          "supersedes": (redo.get(o["org_id"]) or {}).get("old_draft_id"), "supersedes_message": (redo.get(o["org_id"]) or {}).get("old_message_id")})
    wj(os.path.join(d, "candidates.json"), {"eligible": {m: sum(1 for o in elig if o["owner_machine"] == m) for m in MACHINES},
                                            "not_eligible": {"%s · %s" % k: v for k, v in sorted(why.items(), key=lambda x: (str(x[0][0]), x[0][1]))},
                                            "rows": cands})
    s["selected"] = True; st_save(d, s)
    return cands


def owed_reads(d, cands):
    out = []
    for c in cands:
        if not os.path.exists(os.path.join(d, "raw", "sent_%d.json" % c["n"])):
            out.append("  search_threads(query=%s, pageSize 50, view THREAD_VIEW_METADATA_ONLY) -> raw/sent_%d.json" % (json.dumps(c["query_sent"]), c["n"]))
        if not os.path.exists(os.path.join(d, "raw", "drafts_%d.json" % c["n"])):
            out.append("  list_drafts(query=%s, pageSize 50) -> raw/drafts_%d.json" % (json.dumps(c["query_drafts"]), c["n"]))
    return out


def step_gate(d, s, cands, labs):
    rows, held = [], []
    taken = collections.Counter(); seen_addr = {}
    for c in cands:
        # 2026-11-04 (review P1): two org records sharing a recipient must never both get an Email 1 in the same pass
        addrs = [str(c["to"]["email"]).lower()] + [str(p["email"]).lower() for p in c["cc"]]
        dup = next((a for a in addrs if a in seen_addr), None)
        if dup: held.append(dict(c, status="HELD", reason="%s is already a recipient of %s in this pass — duplicate org record? (C2)" % (dup, seen_addr[dup]))); continue
        ns, nd = search_count(os.path.join(d, "raw", "sent_%d.json" % c["n"])), search_count(os.path.join(d, "raw", "drafts_%d.json" % c["n"]))
        if ns and c.get("prior_threads"):     # handoff (Rulebook E7): only the prior threads Chris named are allowed
            sj = rj(os.path.join(d, "raw", "sent_%d.json" % c["n"])) or {}
            ns = sum(1 for t in (sj.get("threads") or []) if t.get("id") not in set(c["prior_threads"]))
        if ns: held.append(dict(c, status="HELD", reason="Gmail already has %d thread(s) with this org or its recipients — prior contact (C2/C4)" % ns)); continue
        if nd and c.get("supersedes"):   # redo: the draft being replaced does not count
            dj = rj(os.path.join(d, "raw", "drafts_%d.json" % c["n"])) or {}
            nd = sum(1 for x in (dj.get("drafts") or []) if x.get("id") != c["supersedes"])
        if nd: held.append(dict(c, status="HELD", reason="a draft to this org already exists in Gmail (C2)")); continue
        if not s.get("redo") and taken[c["machine"]] >= allowance(d)[c["machine"]]: held.append(dict(c, status="SPARE", reason="tonight's ceiling reached — first in line next night")); continue
        taken[c["machine"]] += 1
        for a in addrs: seen_addr[a] = c["org_name"]
        rows.append(c)
    # create in reverse priority: the last created lands on top of Gmail (OM-2 above OM-1, then by priority)
    order = [r for r in rows if r["machine"] == "OM-1"][::-1] + [r for r in rows if r["machine"] == "OM-2"][::-1]
    params = []
    reh = is_reh(d)
    for i, c in enumerate(order, 1):
        m = c["machine"]; att = M["attachment"][m]
        params.append({"create_order": i, "n": c["n"], "org_id": c["org_id"], "org_name": c["org_name"], "machine": m,
                       "zapier": {"selected_api": D["zapier"]["selected_api"], "action": D["zapier"]["action"], "tool_name": D["zapier"]["tool_name"]},
                       "params": {"to": [ME] if reh else [c["to"]["email"]], "cc": [] if reh else [p["email"] for p in c["cc"]], "bcc": [D["hubspot_bcc"]],
                                  "subject": ("[REHEARSAL — do not send] " + c["subject"]) if reh else c["subject"], "body_type": "html", "body": body_for(m, c["greeting"]),
                                  "label_ids": [labs[TEST_LABEL]] if reh else [labs[m], labs[m + "/0"]], "signature": "{{SIGNATURE}}", "signature_delimiter": False,
                                  "file": ["{{E1_FILE}}"]},
                       "attachment": att})
    wj(os.path.join(d, "draft-params.json"), params)
    wj(os.path.join(d, "held.json"), held)
    s["gated"] = True; st_save(d, s)
    return params, held


def cmd_next(a):
    d = rdir(a.run); s = st_load(d)
    if getattr(a, "redo", None) and not s.get("redo"):
        s["redo"] = {r["org_id"]: r for r in json.load(open(a.redo, encoding="utf-8"))}; st_save(d, s)
    R = lambda f: os.path.join(d, "raw", f)
    print("RUN FOLDER %s" % d)
    # 1 labels
    labs, missing = label_ids(d)
    if labs is None:
        print("STEP 1 LABELS: list_labels -> save VERBATIM as %s ; then rerun next." % R("labels.json")); return 0
    if missing:
        print("STEP 1 LABELS: create the missing labels (parents first), then list_labels again over %s and rerun next:" % R("labels.json"))
        for w in missing: print("  create_label displayName=%s" % w)
        return 0
    # 2 select + Gmail checks
    cj = rj(os.path.join(d, "candidates.json"))
    cands = cj["rows"] if cj else step_select(d, s)
    owed = owed_reads(d, cands)
    if owed:
        print("STEP 2 GMAIL CHECKS (C2/C4) for %d candidate(s): run each read and save VERBATIM as named, then rerun next:" % len(cands))
        for l in owed: print(l)
        return 0
    # 3 gate
    params = rj(os.path.join(d, "draft-params.json"))
    if params is None:
        params, held = step_gate(d, s, cands, labs)
        print("STEP 3 GATE: %d to create, %d held/spare (held.json). Rerun next." % (len(params), len(held))); return 0
    # 4 create
    todo = [p for p in params if not os.path.exists(R("zapier_%d.json" % p["n"]))]
    if todo:
        p = todo[0]
        print("STEP 4 CREATE: %d/%d created. Next = create_order %d (%s · %s):" % (len(params) - len(todo), len(params), p["create_order"], p["machine"], p["org_name"]))
        print("  1) {{E1_FILE}} FRESH for this draft: execute_zapier_read_action(selected_api %s, action %s, params {message_id: %s, attachment_filename: %s}) -> the hydrate reference"
              % (D["zapier"]["selected_api"], D["zapier"]["attachment_action"], p["attachment"]["source_message_id"], p["attachment"]["filename"]))
        print("  2) {{SIGNATURE}} once per session: inspect_zapier_actions(tool_name='%s', enum_property='signature') -> its one value" % D["zapier"]["tool_name"])
        print("  3) python3 5_Draft/programfiles/draft.py show --run %s --n %d  -> the exact params; fill ONLY the two placeholders; change nothing else" % (a.run, p["n"]))
        print("  4) execute_zapier_write_action(selected_api %s, action %s, tool_name %s, params) ONCE -> save the response VERBATIM as %s"
              % (D["zapier"]["selected_api"], D["zapier"]["action"], D["zapier"]["tool_name"], R("zapier_%d.json" % p["n"])))
        print("     A failed call is saved as returned (never retried for this org tonight). Then rerun next.")
        return 0
    # 5 verify (Gate 7). Zapier's draft_v2 returns the new MESSAGE id + threadId (not the draft id) — verified 2026-10-31.
    res = rj(os.path.join(d, "verify.json"), {})
    for p in params:
        n = p["n"]; k = str(n)
        if k in res and res[k].get("final"): continue
        zr = rj(R("zapier_%d.json" % n))
        mid = find_key(zr, ["id", "messageId", "message_id"]); thread_id = find_key(zr, ["threadId", "thread_id"])
        if not mid:
            res[k] = {"final": True, "status": "HELD", "reason": "Zapier did not return the new draft (create failed; not retried tonight)"}
            wj(os.path.join(d, "verify.json"), res); continue
        dl = R("draftlist_%d.json" % n)
        if not os.path.exists(dl):
            print("STEP 5 VERIFY (%s): list_drafts(query=%s, pageSize 10) -> save VERBATIM as %s ; then rerun next."
                  % (p["org_name"], json.dumps('subject:"%s"' % p["params"]["subject"]), dl)); return 0
        did = next((x.get("id") for x in (rj(dl) or {}).get("drafts", []) if x.get("messageId") == mid), None)
        if not did:
            res[k] = {"final": True, "status": "HELD", "reason": "the created draft (message %s) was not found in Drafts — check Gmail" % mid}
            wj(os.path.join(d, "verify.json"), res); continue
        g7 = R("gate7_%d.json" % n)
        if not os.path.exists(g7):
            pr = p["params"]
            print("STEP 5 VERIFY — GATE 7 (%s, draft %s):" % (p["org_name"], did))
            print("  1) get_draft(draftId=%s, messageFormat RAW). The result is ~6 MB, so it lands in a file in the cloud workspace." % did)
            print("  2) Once per session, stage 5_Draft/programfiles/gate7.py to the cloud (device_stage_files). In the CLOUD shell run (python3 -I):")
            print("     python3 -I <staged gate7.py> --file <that saved result file> --want %s:%d --tol %s --bcc %s --video %s --to %s %s --subject %s --out <cloud>/gate7_%d.json"
                  % (p["attachment"]["filename"], p["attachment"]["size_bytes"], D["attachment_tolerance_pct"], D["hubspot_bcc"], D["video_url"],
                     " ".join(pr["to"]), ("--cc " + " ".join(pr["cc"])) if pr["cc"] else "--cc", json.dumps(pr["subject"]), n))
            print("  3) Copy that small verdict file to the Mac as %s (device_commit_files, or a quoted heredoc of its one line). Then rerun next." % g7)
            return 0
        v = rj(g7)
        if v.get("ok"):
            res[k] = {"final": True, "status": "DRAFTED", "draft_id": did, "message_id": mid, "thread_id": thread_id, "gate7": v}
        else:
            tries = res.get(k, {}).get("tries", 0) + 1
            print("STEP 5 GATE 7 FAILED for %s (%s): delete_draft(draftId=%s) now." % (p["org_name"], v.get("why"), did))
            if tries < 2:
                for f in ("zapier_%d.json", "draftlist_%d.json", "gate7_%d.json"):
                    if os.path.exists(R(f % n)): os.replace(R(f % n), R((f % n).replace(".json", ".try%d.json" % tries)))
                res[k] = {"final": False, "tries": tries, "last_failure": v.get("why")}
                wj(os.path.join(d, "verify.json"), res)
                print("  The draft will be recreated once (fresh attachment reference). After the delete, rerun next."); return 0
            res[k] = {"final": True, "status": "HELD", "reason": "Gate 7 failed twice: %s" % v.get("why"), "deleted_draft": did, "tries": tries}
            wj(os.path.join(d, "verify.json"), res)
            print("  Held after two failures. After the delete, rerun next."); return 0
        wj(os.path.join(d, "verify.json"), res)
    # 6 record (a rehearsal records nothing)
    if is_reh(d) and not s.get("recorded"):
        s["recorded"] = True; st_save(d, s)
        print("STEP 6 REHEARSAL: nothing recorded in the master list. Rerun next."); return 0
    if not s.get("recorded"):
        cand = {c["n"]: c for c in cands}
        rows = []
        now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
        for p in params:
            c = cand[p["n"]]; v = res[str(p["n"])]
            rows.append({"run": a.run, "created_at": now, "status": v["status"], "reason": v.get("reason"), "org_id": c["org_id"], "org_name": c["org_name"],
                         "org_domain": c["org_domain"], "domains": c["domains"], "state": c["state"], "machine": c["machine"], "draft_id": v.get("draft_id"),
                         "thread_id": v.get("thread_id"), "subject": c["subject"], "greeting": c["greeting"], "short_how": c["short_how"],
                         "to": c["to"]["email"], "cc": [x["email"] for x in c["cc"]], "flags": c["flags"], "event": c.get("event"),
                         "edition_date": c.get("edition_date"), "why": c.get("why"), "all_events": c.get("all_events"), "best_fit_why": c.get("best_fit_why"), "create_order": p["create_order"], "supersedes": c.get("supersedes") if v["status"] == "DRAFTED" else None})
        for h in rj(os.path.join(d, "held.json"), []):
            rows.append({"run": a.run, "created_at": now, "status": h["status"], "reason": h["reason"], "org_id": h["org_id"], "org_name": h["org_name"],
                         "machine": h["machine"], "thread_id": None, "draft_id": None})
        ajl(paths.DRAFTS, rows)
        s["recorded"] = True; st_save(d, s)
        print("STEP 6 RECORDED %d row(s) in the drafts inbox. Now rebuild: python3 _shared/master/build_master.py ; then rerun next." % len(rows)); return 0
    # 7 done
    made = collections.Counter(p["machine"] for p in params if res[str(p["n"])]["status"] == "DRAFTED")
    summ = {"run": a.run, "made": dict(made), "minimum": M["minimum"], "eligible": cj["eligible"] if cj else None,
            "shortfall": shortfall(made, (cj or {}).get("eligible", {}))}
    wj(os.path.join(d, "summary.json"), summ)
    print("DRAFT DONE: %s" % json.dumps(summ, ensure_ascii=False))
    if s.get("redo"):
        cand = {c["n"]: c for c in cands}
        old = [cand[p["n"]] for p in params if res[str(p["n"])]["status"] == "DRAFTED" and cand[p["n"]].get("supersedes_message")]
        print("REDO: %d replacement draft(s) passed Gate 7. Move each REPLACED draft to Trash (recoverable), then rebuild the master list:" % len(old))
        for c in old: print("  trash_message(messageId=%s)   # old draft %s · %s" % (c["supersedes_message"], c["supersedes"], c["org_name"]))
    if is_reh(d):
        ids = [v.get("draft_id") for v in res.values() if v.get("draft_id")]
        print("REHEARSAL CLEAN-UP — delete each test draft, then the test label:")
        for x in ids: print("  delete_draft(draftId=%s)" % x)
        print("  delete_label(%s)  (its id is in %s)" % (TEST_LABEL, R("labels.json")))
    return 0


def shortfall(made, eligible):
    """Rulebook M4 / machine settings: a missed minimum is REPORTED with its reason, never met by lowering a gate."""
    out = {}
    for m in MACHINES:
        if made.get(m, 0) < M["minimum"][m]:
            out[m] = "%d of %d minimum: only %d %s org(s) were open, fit and had a ready recipient set; the rest are held (gates never lowered)" % (
                made.get(m, 0), M["minimum"][m], eligible.get(m, 0), m)
    return out


def cmd_show(a):
    d = rdir(a.run)
    for p in rj(os.path.join(d, "draft-params.json"), []):
        if p["n"] == a.n:
            print(json.dumps(p["params"], ensure_ascii=False, indent=1)); return 0
    print("no row n=%d" % a.n); return 2


def cmd_candidates(a):
    orgs = load_orgs(); idx = indexes(orgs)
    c = collections.Counter(); ok = collections.Counter()
    for o in orgs:
        w = why_not(o, idx)
        if a.machine and o.get("owner_machine") != a.machine: continue
        if w: c[(o.get("owner_machine"), w.split(" (")[0].split(":")[0])] += 1
        else: ok[o["owner_machine"]] += 1
    print("ELIGIBLE NOW:", dict(ok))
    for (m, w), n in sorted(c.items(), key=lambda x: -x[1]):
        if m in MACHINES: print("  %-5s %4d  %s" % (m, n, w))
    return 0


def cmd_render(a):
    print(body_for(a.machine, a.greeting)); return 0


def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    x = sp.add_parser("next"); x.add_argument("--run", required=True); x.add_argument("--redo", help="JSON list [{org_id, old_draft_id, old_message_id}]: re-draft these orgs, replacing their unsent drafts (Chris 2026-11-04)"); x.set_defaults(f=cmd_next)
    x = sp.add_parser("show"); x.add_argument("--run", required=True); x.add_argument("--n", type=int, required=True); x.set_defaults(f=cmd_show)
    x = sp.add_parser("candidates"); x.add_argument("--machine"); x.set_defaults(f=cmd_candidates)
    x = sp.add_parser("render"); x.add_argument("--machine", required=True); x.add_argument("--greeting", required=True); x.set_defaults(f=cmd_render)
    a = ap.parse_args(); sys.exit(a.f(a))


if __name__ == "__main__":
    main()
