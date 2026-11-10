#!/usr/bin/env python3
"""successors.py — Rulebook J6 (Chris 2026-10-30): a successor named in an auto-reply takes the departed recipient's spot.

Pure functions; no Gmail, no network. Inputs (master folder, one copy each):
  successors.jsonl            one record per auto-reply that names successors. The inbox read writes it from the
                              auto-reply text; every successor address must appear VERBATIM in the saved raw message
                              (provenance, Rulebook H6). Fields: sender (who left), departed_name, departed (true = left /
                              handed over; false = temporary cover -> never used, J5), message_id, raw (path), successors:
                              [{email, name, title, routing, applies, why, valid_until}].
  successor-validation.jsonl  ZeroBounce results (via Apollo) per address: {email, result: valid|catch-all|unknown|invalid, source, date}.

Choice (J6): routing that names our kind of request wins (score 2); else a title matching our request (score 1);
ties or no information -> Cc all tied. 4-person ceiling (G1): keep the most relevant / first named that fits, flag ⚠.
A successor at another org already in the master list with a thread or an exclusion is never added (C2) -> ⚠.
Invalid -> not added, ⚠. Not yet validated -> NEEDS (the thread waits for the check; never sent unchecked).
"""
import json, os, re, datetime

REQUEST = {  # what we ask each machine's recipients about
    "OM-1": r"train|professional development|\bpd\b|workforce|coach|quality|education",
    "OM-2": r"conference|speaker|keynote|event|professional development|\bpd\b|train|summit|institute",
}
TITLE = {
    "OM-1": r"director|professional development|training|coach|quality|education|program",
    "OM-2": r"event|conference|director|professional development|training|program|education",
}


import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_shared", "orchestrator")); import paths  # the one file that knows every folder (2026-11-03)


def load(master=None):
    master = master or paths.ledgers("read")   # 1_Read-the-Inbox/ledgers/ (2026-11-03)
    recs, val = [], {}
    p = os.path.join(master, "successors.jsonl")
    if os.path.exists(p):
        recs = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
    v = os.path.join(master, "successor-validation.jsonl")
    if os.path.exists(v):
        for l in open(v, encoding="utf-8"):
            if l.strip():
                x = json.loads(l); val[x["email"].lower()] = x
    return recs, val


def provenance_ok(rec, master=None):
    master = master or paths.ledgers("read")
    """Every successor address must appear verbatim in the saved auto-reply (H6). Returns list of bad addresses."""
    p = rec.get("raw")
    if not p: return [s["email"] for s in rec.get("successors", [])]
    p = p if os.path.isabs(p) else os.path.join(master, "successors-raw", os.path.basename(p))   # saved auto-replies live in ledgers/successors-raw/
    if not os.path.exists(p): return [s["email"] for s in rec.get("successors", [])]
    txt = open(p, encoding="utf-8").read().lower()
    return [s["email"] for s in rec.get("successors", []) if s["email"].lower() not in txt]


def dom(a):
    return a.lower().rsplit("@", 1)[-1]


def score(s, machine):
    r = (s.get("routing") or "").lower(); t = (s.get("title") or "").lower()
    if r and re.search(REQUEST.get(machine, REQUEST["OM-1"]), r): return 2
    if t and re.search(TITLE.get(machine, TITLE["OM-1"]), t): return 1
    return 0


def first(name):
    return (name or "").strip().split()[0] if (name or "").strip() else None


def apply(to, cc, recs, machine, this_domains, other_orgs, validation, slot_date, ceiling=4, prov_bad=None):
    """Returns dict(to, cc, add_names, remove_names, notes, flags, needs, changed).
    other_orgs: {domain: {"org_id","name","has_thread","excluded"}} for orgs OTHER than this one."""
    to, cc = list(to), list(cc)
    out = {"to": to, "cc": cc, "add_names": [], "remove_names": [], "notes": [], "flags": [], "needs": [], "changed": False}
    prov_bad = {a.lower() for a in (prov_bad or [])}
    this_domains = {d.lower() for d in this_domains}
    for rec in recs:
        who = rec["sender"].lower()
        if who not in to + cc: continue
        if not rec.get("departed"):
            out["notes"].append("%s is covering a temporary absence for %s — never added (J5)" % (", ".join(s["email"] for s in rec.get("successors", [])), who)); continue
        cands = []
        for s in rec.get("successors", []):
            e = s["email"].lower()
            if not s.get("applies", True):
                out["notes"].append("successor %s does not apply here (%s)" % (e, s.get("why") or "routing")); continue
            if s.get("valid_until") and s["valid_until"] < slot_date.isoformat():
                out["notes"].append("successor %s was only named through %s" % (e, s["valid_until"])); continue
            if e in prov_bad:
                out["flags"].append("⚠ successor %s not found verbatim in the saved auto-reply — not added" % e); continue
            if dom(e) not in this_domains and dom(e) in other_orgs:
                oo = other_orgs[dom(e)]
                if oo.get("has_thread") or oo.get("excluded"):
                    out["flags"].append("⚠ successor %s is at %s, which already has its own %s — not added (one org, one thread)"
                                        % (e, oo["name"], "thread" if oo.get("has_thread") else "exclusion")); continue
            if e in (a.lower() for a in to + cc): continue
            cands.append(dict(s, email=e, score=score(s, machine)))
        if not cands:
            if who in to: out["flags"].append("⚠ %s (To) has left and no usable successor was named — Chris decides" % who)
            continue
        best = max(c["score"] for c in cands)
        chosen = [c for c in cands if c["score"] == best] if best > 0 else cands
        if best > 0 and len(chosen) < len(cands):
            out["notes"].append("chose %s by %s" % (", ".join(c["email"] for c in chosen), "stated routing" if best == 2 else "title"))
        elif len(chosen) > 1:
            out["notes"].append("several successors and no information to choose — Cc all (%s)" % ", ".join(c["email"] for c in chosen))
        ok = []
        for c in chosen:
            v = validation.get(c["email"])
            if not v: out["needs"].append(c["email"]); continue
            if v["result"] == "invalid":
                out["flags"].append("⚠ successor %s failed the address check (invalid) — not added" % c["email"]); continue
            if v["result"] in ("catch-all", "unknown"):
                out["notes"].append("successor %s is %s — added, flagged (H4)" % (c["email"], v["result"]))
            ok.append(c)
        if out["needs"]: continue
        was_to = who in to
        if was_to: to.remove(who)
        else: cc.remove(who)
        out["remove_names"].append(rec.get("departed_name") or first(who.split("@")[0]))
        room = ceiling - len(to) - len(cc)
        if len(ok) > room:
            out["flags"].append("⚠ only %d of %d successors fit the 4-person ceiling — added %s" % (max(room, 0), len(ok), ", ".join(c["email"] for c in ok[:max(room, 0)])))
            ok = ok[:max(room, 0)]
        for i, c in enumerate(ok):
            (to if was_to and i == 0 else cc).append(c["email"])
            out["add_names"].append(first(c.get("name")) or c["email"].split("@")[0])
        if not ok and was_to:
            if cc: to.append(cc.pop(0)); out["flags"].append("⚠ %s (To) left; no successor added — first Cc promoted to To" % who)
            else: out["flags"].append("⚠ %s (To) left and no successor could be added — Chris decides" % who)
        out["changed"] = True
        out["notes"].append("J6: %s replaced by %s" % (who, ", ".join(c["email"] for c in ok) or "nobody"))
    out["to"], out["cc"] = to, cc
    return out
