#!/usr/bin/env python3
"""dossier.py — the verification packet Chris reads BEFORE sending a night's Email 1 drafts.

Layout (Chris 2026-11-04, templates/dossier-template.md — the outline is binding; old 2026-09-03 template retired to templates/retired/; repeating parts repeat as often as the data needs):
  📤 Dossier — <date>            (Chris 2026-11-10: ONLY the drafts going out that day, then the top 10 decisions beneath — never a full list)
  📧 2️⃣ OM2 — Position N · Org · ST   one card per OM-2 draft, Position 1 = top of the OM-2/0 Drafts view (newest first)
  📧 1️⃣ OM1 — Position N · Org · ST   same card, OM-1
  ⚠️ Top 10 decisions                 beneath the cards, numbered, never more than 10: flags on today's drafts first, then doubtful-fit orgs
                                      waiting for a yes/no (Rulebook E2), "is this a conference?" orgs and orgs that fit neither machine (E3)
  card: 🏢 Org — website · 👥 Staff page(s) · 📅 Event / training page(s) · Name|Title|Email|Source table · 🧠 Reasoning · 🔗 Supporting pages
Built ONLY from records the night run already wrote (drafts ledger, master list, people results, H7 sweep ledger, Gate 7 verify.json,
the HubSpot suppression seed); nothing is looked up.

  python3 5_Draft/programfiles/dossier.py --night 2026-11-03 --slot 2026-11-04 [--out PATH]
Writes 5_Draft/ledgers/dossiers/dossier-<slot>.md and prints the path.
"""
import os, sys, re, json, argparse, datetime, glob, collections, urllib.parse
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_shared", "orchestrator")); import paths

LEADER = re.compile(r"\b(director|executive|chief|ceo|coo|cfo|president|superintendent|head of|vice president|vp|founder|principal)\b", re.I)
PD_ROLE = re.compile(r"\b(director|executive|chief|ceo|president|superintendent|manager|coordinator|training|professional development|coach|lead|specialist|officer)\b", re.I)
STAFF_PAGE = re.compile(r"(staff|team|leadership|about|board|directory|contact|people|who-we-are|our-team|executive)", re.I)
EVENT_PAGE = re.compile(r"(event|conference|training|professional-development|/pd|workshop|calendar|summit|institute|program|fccn|course|class)", re.I)
INTERNAL_FIT = re.compile(r"^(Machine \d candidate status|.*HELD_)", re.I)

def link(p):
    p = os.path.abspath(p); m = re.search(r"/mnt/ClaudeVault/(.*)$", p)
    return "computer://" + urllib.parse.quote("/Users/<you>/ClaudeVault/" + m.group(1) if m else p)
def jl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()] if os.path.exists(p) else []
def dom(e): return (e or "").split("@")[-1].lower()
def md(url, label=None):
    if not url: return ""
    lab = label or re.sub(r"^https?://(www\.)?", "", url).rstrip("/")
    return "[%s](%s)" % (lab[:70], url)
def same_site(d, doms):
    return any(d == x or d.endswith("." + x) or x.endswith("." + d) for x in doms)
def norm(s): return re.sub(r"[^a-z]", "", (s or "").lower())

def suppression_tokens():
    """Domains/addresses that are BLOCKED in the HubSpot suppression seed: §A, §B, §D and any 'ADDED TO §A/§B/§D' section.
    Read straight from the file (not from the master's exclusions) so a parser miss upstream cannot hide a block here."""
    p = os.path.join(paths.SEEDS, "OM-1", "hubspot-suppression.md")
    if not os.path.exists(p): return set()
    toks, on = set(), False
    for line in open(p, encoding="utf-8"):
        if line.startswith("## "):
            h = line[3:]
            on = bool(re.match(r"§[ABD]\b", h) or re.search(r"ADDED TO §[ABD]", h))
        if on:
            for t in re.findall(r"`([^`\s]+)`", line):
                t = t.lower()
                if "@" in t or re.match(r"^[a-z0-9-]+(\.[a-z0-9-]+)+$", t): toks.add(t)
    return toks

def people_result(oid):
    """The latest people-helper result line for this org (any run), or {}."""
    best = (None, {})
    for f in glob.glob(os.path.join(paths.runs("people"), "*", "result_*.jsonl")):
        run = os.path.basename(os.path.dirname(f))
        for r in jl(f):
            if r.get("org_id") == oid and (best[0] is None or run > best[0]): best = (run, r)
    return best[1]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--night", required=True); ap.add_argument("--slot"); ap.add_argument("--out")
    ap.add_argument("--threads", help="a file with one Gmail thread id per line: build the dossier for exactly these unsent drafts, whatever night made them (Chris 2026-11-10: the dossier covers the drafts going out that day)")
    a = ap.parse_args()
    night = a.night
    if a.threads:
        want = [x.strip() for x in open(a.threads, encoding="utf-8") if x.strip()]; last = {}
        for r in jl(paths.DRAFTS):
            if r.get("status") == "DRAFTED" and r.get("thread_id") in want: last[r["thread_id"]] = r
        drafts = [last[t] for t in want if t in last]
    else:
        drafts = [r for r in jl(paths.DRAFTS) if str(r.get("run", "")) == night or str(r.get("run", "")).startswith(night + "-p")]
    made = [r for r in drafts if r.get("status") == "DRAFTED"]
    held = [r for r in drafts if r.get("status") != "DRAFTED"]
    if not drafts: sys.exit("no draft records for night run %s in %s" % (night, paths.DRAFTS))
    orgs = {o["org_id"]: o for o in jl(paths.ORGS)}
    g7 = {}
    for vf in glob.glob(os.path.join(paths.runs("draft"), ("*" if a.threads else night + "*"), "verify.json")):
        for k, v in json.load(open(vf, encoding="utf-8")).items():
            if v.get("draft_id"): g7[v["draft_id"]] = v.get("gate7") or {}
    sweep = {}
    for s in jl(paths.SWEEP_LEDGER): sweep[s.get("key")] = s.get("result")
    blocked = suppression_tokens()
    # every recipient address on any OTHER drafted org (duplicate-person check)
    addr_orgs = collections.defaultdict(set)
    for r in jl(paths.DRAFTS):
        if r.get("status") == "DRAFTED":
            for e in [r.get("to")] + list(r.get("cc") or []):
                if e: addr_orgs[str(e).lower()].add(r["org_id"])
    for oid, o in orgs.items():   # ready recipient sets on other org records (e.g. two records for one org)
        rec = o.get("recipients") or {}
        for p in ([rec.get("to")] if rec.get("to") else []) + list(rec.get("cc") or []):
            if p and p.get("email"): addr_orgs[str(p["email"]).lower()].add(oid)
    slot = a.slot or (max(r["created_at"] for r in made)[:10] if made else datetime.date.today().isoformat())
    out = a.out or os.path.join(paths.DOSSIERS, "dossier-%s.md" % slot)

    # Drafts-outbox order: newest first = later pass first, then later create_order first
    made.sort(key=lambda r: (str(r.get("run")), r.get("create_order") or 0), reverse=True)
    cards, decisions, domain_mismatch = [], [], []
    pos = collections.Counter()
    for r in made:
        m = r["machine"]; pos[m] += 1; P = pos[m]
        o = orgs.get(r["org_id"], {}); rec = o.get("recipients") or {}
        # 2026-11-04 (review P2): show what is IN THE DRAFT (the draft row), enriched from the master list's records for those addresses
        info = {str(p.get("email") or "").lower(): p for p in ([rec.get("to")] if rec.get("to") else []) + list(rec.get("cc") or []) if p}
        for c_ in o.get("contacts") or []: info.setdefault(str(c_.get("email") or "").lower(), {"email": c_.get("email"), "name": c_.get("name"), "role": c_.get("role"), "source": (c_.get("verification") or {}).get("class") or "page", "evidence_url": c_.get("evidence_url")})
        addrs = ([r["to"]] if r.get("to") else []) + list(r.get("cc") or [])
        people = [("To" if i == 0 else "Cc", info.get(str(e).lower()) or {"email": e, "name": None, "role": None, "source": "?"}) for i, e in enumerate(addrs)] if addrs else \
                 ([("To", rec["to"])] if rec.get("to") else []) + [("Cc", p) for p in (rec.get("cc") or [])]
        pr = people_result(r["org_id"])
        doms = o.get("domains") or ([r["org_domain"]] if r.get("org_domain") else [])
        pages = list(dict.fromkeys(pr.get("pages_read") or []))
        if not doms and pages: doms = [re.sub(r"^www\.", "", urllib.parse.urlparse(pages[0]).netloc.lower())]   # no domain on file: the site the people step read
        site = ("https://" + doms[0]) if doms else None
        ev_urls = [e.get("url") for e in (o.get("events") or []) if e.get("url")]
        staff = [u for u in pages if STAFF_PAGE.search(u)]
        events = list(dict.fromkeys(ev_urls + [u for u in pages if EVENT_PAGE.search(u) and u not in staff]))
        tag = "%s #%d %s" % (m.replace("OM-", "OM"), P, r["org_name"])
        anchor = staff[0] if staff else (people[0][1].get("evidence_url") if people else None) or site
        mine = []
        def D(text, url=None):
            if any(norm(text) == norm(x) for x in mine): return
            mine.append(text)
        # --- decision triggers (only things that change whether / how Chris sends)
        def isblk(t): return bool(t) and (t in blocked or ("@" not in t and any(t.endswith("." + b) for b in blocked if "@" not in b)))
        hits = sorted({t for p in people for t in (str(p[1].get("email") or "").lower(), dom(p[1].get("email"))) if isblk(t)} | {d for d in doms if isblk(d)})
        if hits: D("on the HubSpot block list (%s) — do NOT send cold; check the relationship first" % ", ".join(hits))
        ex = sorted(k for k, v in (o.get("exclusions") or {}).items() if v)
        if ex: D("master list exclusion: %s" % ", ".join(ex))
        for f in (r.get("flags") or []) + [x for x in (o.get("flags") or []) if str(x).startswith("⚠")]:
            if "doubtful fit" in str(f) and (o.get("fit") or {}).get("status") == "fit": continue   # a flag from the night it was drafted; the org is a fit now
            if f not in mine: D(str(f).lstrip("⚠ "))
        to = rec.get("to") or {}
        if to and (to.get("generic") or not to.get("name")):
            D("goes to a general inbox (%s) — no named person with an address" % to.get("email"))
        roles = [str(p[1].get("role") or "") for p in people]
        named_wo = [n for n in (pr.get("named_without_email") or []) if n.get("name") and norm(n["name"]) not in {norm(p[1].get("name")) for p in people}]
        leaders_off = [n for n in named_wo if LEADER.search(str(n.get("role") or ""))]
        if people and not any(LEADER.search(x) for x in roles) and leaders_off:
            D("no leader on the draft; named but not reachable: %s" % "; ".join("%s (%s)" % (n["name"], n.get("role")) for n in leaders_off[:3]))
        elif people and not any(PD_ROLE.search(x) for x in roles):
            D("recipients hold no leader or PD role (%s) — check they are the right people" % "; ".join(x or "no title" for x in roles))
        for lab, p in people:
            e = str(p.get("email") or "").lower()
            others = addr_orgs.get(e, set()) - {r["org_id"]}
            if others: D("%s is also a recipient under %s — duplicate org record?" % (e, ", ".join(sorted(others))))
            if str(p.get("validity")).replace("-", "_") == "catch_all": D("%s is on a catch-all domain — a bounce is more likely" % e)
            if p.get("identity") == "departed": D("%s — Apollo says this person has LEFT the org" % e)
        gate = g7.get(r.get("draft_id")) or {}
        if gate and not gate.get("ok"): D("Gate 7 read-back FAILED: %s" % gate.get("why"))
        if mine: decisions.append((tag, mine, anchor))
        mails = sorted({dom(p[1].get("email")) for p in people if p[1].get("email")})
        if doms and any(not same_site(x, doms) for x in mails): domain_mismatch.append((tag, site, mails))
        cards.append(dict(r=r, o=o, P=P, people=people, staff=staff, events=events, site=site, named_wo=named_wo, flagged=bool(mine), pr=pr))

    L = ["---", "business: Human Skills Training", "type: dossier", "title: Outreach — Dossier %s (night run %s)" % (slot, night),
         "status: verify before sending", "owner: Chris Danilo", "run: %s (slot %s)" % (night, slot), "drafts: %d" % len(made),
         "template: 5_Draft/programfiles/templates/dossier-template.md",
         "generated: %s by 5_Draft/programfiles/dossier.py" % datetime.datetime.now().astimezone().isoformat(timespec="minutes"), "---", ""]
    by_m = collections.Counter(c["r"]["machine"] for c in cards)
    L += ["# 📤 Dossier — %s" % slot, "",
          "%d new Email 1 drafts · 2️⃣ OM2 %d · 1️⃣ OM1 %d. Positions = order in each machine's /0 Drafts view (Position 1 = top)." % (len(made), by_m.get("OM-2", 0), by_m.get("OM-1", 0)), "",
          "The top 10 decisions are beneath the draft cards.", ""]
    for m, num in (("OM-2", "2️⃣"), ("OM-1", "1️⃣")):
        rows = [c for c in cards if c["r"]["machine"] == m]
        L += ["---", ""]
        if not rows:
            L += ["# %s %s" % (num, m.replace("OM-", "OM")), "", "No %s drafts tonight." % m.replace("OM-", "OM"), ""]; continue
        for c in rows:
            r, o = c["r"], c["o"]
            L.append("# 📧 %s %s — Position %d · %s · %s%s" % (num, m.replace("OM-", "OM"), c["P"], r["org_name"], r.get("state") or o.get("state") or "—", "  ⚠️ see decisions below" if c["flagged"] else ""))
            L.append("")
            L.append("- 🏢 **Org:** %s — %s" % (r["org_name"], md(c["site"]) if c["site"] else "no website on file"))
            L.append("- 👥 **Staff page(s):** %s" % (" · ".join(md(u) for u in c["staff"]) if c["staff"] else "none recorded"))
            L.append("- 📅 **Event / training page(s):** %s" % (" · ".join(md(u) for u in c["events"]) if c["events"] else "none read"))
            L.append("- ✉️ **Subject** `%s` · **Greeting** `%s,` · [open draft in Gmail](https://mail.google.com/mail/u/0/#all/%s)" % (r.get("subject"), r.get("greeting"), r["thread_id"]))
            L += ["", "| Name | Title | Email | Source |", "|---|---|---|---|"]
            seen = set()
            for lab, p in c["people"]:
                src, ev = p.get("source") or "?", p.get("evidence_url")
                if p.get("generic") or not p.get("name"): s = "📮 general inbox" + ((" · printed on " + md(ev)) if ev else "")
                elif src in ("live-page", "page"): s = ("📄 same page" if ev in seen else "📄 printed on " + md(ev)) if ev else "📄 printed on the org's page"
                elif src == "apollo-verified": s = "🔍 Apollo-verified" + ((" (named on " + md(c["staff"][0]) + ")") if c["staff"] else "")
                elif src == "autoreply": s = "📄 the org's own auto-reply"
                else: s = src
                if ev: seen.add(ev)
                L.append("| %s%s | %s | %s | %s |" % ("**To** " if lab == "To" else "Cc ", p.get("name") or "(general inbox)", p.get("role") or "—", p.get("email"), s))
            L.append("")
            # reasoning: why these staff, who was left off, why this machine
            why = []
            roles = ", ".join(str(p[1].get("role") or "?") for p in c["people"])
            why.append("On the draft: %s." % roles)
            off = []
            for n in c["named_wo"]:
                k = "%s|%s" % (r["org_id"], str(n["name"]).lower())
                res = sweep.get(k)
                off.append("%s (%s) — %s" % (n["name"], n.get("role") or "?", {"resolved": "Apollo found an address, not used", "queried-null": "Apollo: no email", "held": "Apollo address held (not verified)"}.get(res, "never looked up")))
            if off: why.append("Not on the draft: " + "; ".join(off) + ".")
            ev = (o.get("events") or [])
            if m == "OM-2" and not r.get("event"):
                why.append("OM2: ⚠ no named event on this draft — check before sending.")
            elif m == "OM-2":
                e = next((x for x in ev if x.get("name") == r["event"]), {})
                why.append("OM2: event %s, next edition %s (%s)." % (r["event"], r.get("edition_date") or e.get("next_edition_date") or "?", r.get("why") or "window open"))
                if r.get("all_events"):   # Chris 2026-11-09: several conferences — show every event's URL and why this one was chosen
                    why.append("Other events at this org: " + "; ".join("%s%s [%s]" % (x.get("event") or "?", " <%s>" % x["url"] if x.get("url") else "", x["status"]) for x in r["all_events"] if x.get("event") != r["event"]) + ". " + (r.get("best_fit_why") or ""))
            if m == "OM-1":
                why.append("OM1: %s; %s." % (", ".join(o.get("icps") or []) or "ICP ?", "no open event on file" if not ev else "event on file but not in OM2's window"))
            fr = (o.get("fit") or {}).get("reason") or ""
            if "Holds an active HS or EHS grant" in fr: why.append("Fit: Head Start / EHS grantee on the federal grantee list.")
            elif fr and not INTERNAL_FIT.search(fr): why.append("Fit: " + fr[:220] + ("…" if len(fr) > 220 else ""))
            L.append("- 🧠 **Reasoning:** " + " ".join(why))
            sup = list(dict.fromkeys([p[1].get("evidence_url") for p in c["people"] if p[1].get("evidence_url")] + c["staff"][:2] + c["events"][:2]))
            L.append("- 🔗 **Supporting pages:** %s" % (" · ".join(md(u) for u in sup) if sup else "none recorded"))
            L.append("")
    # ---- ⚠️ Top 10 decisions (Chris 2026-11-10): beneath the cards, never more than 10, never the full list
    items = ["**%s** — %s%s" % (tag, " · ".join(texts), (" · " + md(url)) if url else "") for tag, texts, url in decisions]
    if domain_mismatch:
        items.append("**mail domain ≠ website** — %s. OK to treat each as one org?" % " · ".join("%s (%s → %s)" % (t, (s or "").replace("https://", ""), ", ".join(ms)) for t, s, ms in domain_mismatch))
    def waiting(o): return not o.get("threads") and not any((o.get("exclusions") or {}).values()) and not o.get("referrer") and (o.get("fit") or {}).get("status") in ("fit", "doubtful")
    def site_of(o): return (" · " + md("https://" + o["domains"][0])) if o.get("domains") else ""
    def nm(o): return "%s%s" % (o.get("name"), " (%s)" % o["state"] if o.get("state") else "")
    q_doubt, q_conf, q_none = [], [], []
    for o in sorted(orgs.values(), key=lambda o: (0 if o.get("owner_machine") == "OM-2" else 1, str(o.get("name")))):
        if not waiting(o): continue
        oo = o.get("outreach") or {}
        if o.get("routing_unclear"):
            evs = [e for e in o.get("events") or [] if e.get("kind_used") == "unclear"]
            q_conf.append("**Is this a conference?** %s — %s. Yes → OM2 (keynote pitch) · no → %s%s" % (nm(o), "; ".join("%s%s" % (e.get("name") or "unnamed event", " " + md(e["url"]) if e.get("url") else "") for e in evs[:2]), "OM1 (training pitch)" if o.get("owner_machine") == "OM-1" else "no outreach", site_of(o)))
        elif o["fit"]["status"] == "doubtful" and o.get("owner_machine") in ("OM-1", "OM-2") and (o.get("recipients") or {}).get("to") and (o["owner_machine"] == "OM-1" or oo.get("status") == "open_now"):
            q_doubt.append("**Doubtful fit — draft it tomorrow?** %s — would go to %s%s · why doubtful: %s%s" % (nm(o), o["owner_machine"].replace("OM-", "OM"),
                (" for %s (%s)" % (oo.get("event") or "its conference", oo.get("edition_date") or "no date on record")) if o["owner_machine"] == "OM-2" else "", (o["fit"].get("reason") or "not recorded")[:170], site_of(o)))
        elif o.get("owner_machine") == "none" and set(o.get("icps") or []) & {"ICP-001", "ICP-002", "ICP-003", "ICP-004", "ICP-005", "ICP-006"}:
            q_none.append("**Fits neither machine — what should happen?** %s — %s · %s%s" % (nm(o), ", ".join(o.get("icps") or []), o.get("routing_note") or "no conference on record, and this customer type is conference-only", site_of(o)))
    queues, more = [q for q in (q_doubt, q_conf, q_none) if q], []
    while queues:            # one of each kind in turn, so every kind of decision gets seen
        for q in list(queues):
            more.append(q.pop(0))
            if not q: queues.remove(q)
    allitems = items + more
    L += ["---", "", "## ⚠️ Top 10 decisions", ""]
    if allitems:
        L += ["%d. %s" % (i + 1, t) for i, t in enumerate(allitems[:10])]
        L += ["", "Reply in chat with the number and yes / no. A yes on a doubtful org puts it on the next day's draft list; a no closes it."]
        if len(allitems) > 10: L.append("%d more are waiting; they come up as these are answered." % (len(allitems) - 10))
    else:
        L.append("Nothing needs you tonight.")
    L.append("")
    ok7 = sum(1 for c in cards if (g7.get(c["r"].get("draft_id")) or {}).get("ok"))
    L += ["---", "✅ Gate 7 read-back passed on %d of %d drafts (flyer, HubSpot bcc, video link, recipients)." % (ok7, len(cards))]
    if held: L.append("Held at draft time: %d (see the night report)." % len({r["org_id"] for r in held}))
    L += ["", "Records: [drafts ledger](%s) · [master list](%s) · [this dossier](%s)" % (link(paths.DRAFTS), link(paths.ORGS), link(out)), ""]
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write("\n".join(L))
    print("DOSSIER %s · %d drafts (OM-1 %d · OM-2 %d) · %d held · %d decision line(s)" % (out, len(made), by_m.get("OM-1", 0), by_m.get("OM-2", 0), len(held), len(decisions) + (1 if domain_mismatch else 0)))

if __name__ == "__main__": main()
