#!/usr/bin/env python3
"""Website hints for Head Start grantees that have no website on file (Chris 2026-11-10, Issue 7).

The federal grantee list has no website column, so many grantee records reach the qualify step with nothing to read. This finds a
CANDIDATE website with Apollo's free organization lookup (fuzzy name + state). A candidate is kept only when Apollo's company name
matches the grantee's name closely; it is a HINT, never truth: it becomes the org's website only after a qualify or people helper
reads that site and a captured page on it names the org (the normal own-site check).

  python3 grantee_domains.py items [--cap N]     one JSON line per grantee to look up (never looked up before)
  python3 grantee_domains.py ingest FILE          lines {org_id, candidates: [{name, domain}]} exactly as Apollo returned them
"""
import argparse, datetime, json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_shared", "orchestrator")); import paths
ORGS = os.path.join(paths.MASTER, "orgs.jsonl")
LEDGER = os.path.join(paths.ROOT, "2_Discover", "ledgers", "grantee-domain-hints.jsonl")
TODAY = datetime.date.today().isoformat()
STOP = {"inc", "incorporated", "the", "of", "and", "co", "corp", "corporation", "llc", "a", "for", "dba", "county", "program", "programs"}
FREE = {"gmail.com", "yahoo.com", "facebook.com", "linkedin.com", "wixsite.com", "weebly.com"}
STATES = {"AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "DC": "District of Columbia",
          "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana",
          "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska",
          "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
          "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas",
          "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming", "PR": "Puerto Rico"}

def jl(p): return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()] if os.path.exists(p) else []
def toks(n): return {t for t in re.findall(r"[a-z0-9]+", (n or "").lower().replace("&", " and ")) if t not in STOP}
def score(a, b):
    A, B = toks(a), toks(b)
    if not A or not B: return 0.0
    def compact(n): return "".join(t for t in re.findall(r"[a-z0-9]+", (n or "").lower().replace("&", " and ")) if t not in {"inc", "incorporated", "the", "llc", "corp", "corporation", "co", "dba"})
    if compact(a) == compact(b): return 1.0          # "A.W.A.R.E., Inc." = "AWARE Inc."
    return 2 * len(A & B) / (len(A) + len(B))

def wanted(o):
    return ("ICP-003" in (o.get("icps") or []) and not o.get("domains") and not o.get("threads") and not o.get("referrer")
            and not any((o.get("exclusions") or {}).values()) and (o.get("fit") or {}).get("status") in ("fit", "unreviewed", "doubtful")
            and (o.get("state") or "").upper() != "CO")

def cmd_items(a):
    done = {r["org_id"] for r in jl(LEDGER)}; n = 0
    for o in sorted(jl(ORGS), key=lambda o: o["org_id"]):
        if not wanted(o) or o["org_id"] in done: continue
        st = (o.get("state") or "").upper()
        print(json.dumps({"org_id": o["org_id"], "name": o["name"], "state": st,
                          "location": ("%s, United States" % STATES[st]) if st in STATES else None}, ensure_ascii=False)); n += 1
        if a.cap and n >= a.cap: break
    print("# grantee website lookups: %d (free Apollo organization lookup; one per grantee, ever)" % n, file=sys.stderr)

def cmd_ingest(a):
    orgs = {o["org_id"]: o for o in jl(ORGS)}; out = []; kept = 0
    for x in jl(a.file):
        o = orgs.get(x.get("org_id"))
        if not o: continue
        best = None
        for c in x.get("candidates") or []:
            d = re.sub(r"^www\.", "", str(c.get("domain") or "").lower().strip())
            if not d or d in FREE: continue
            s = score(o["name"], c.get("name"))
            if s >= 0.8 and (best is None or s > best[0]): best = (s, d, c.get("name"))
        row = {"org_id": o["org_id"], "date": TODAY, "name": o["name"], "hint": best[1] if best else None,
               "apollo_name": best[2] if best else None, "score": round(best[0], 2) if best else None,
               "status": "candidate" if best else "no close match"}
        out.append(row); kept += bool(best)
        print("%-50s %s" % (o["name"][:50], ("%s (Apollo: %s, %.2f)" % (best[1], best[2], best[0])) if best else "no close match"))
    with open(LEDGER, "a", encoding="utf-8") as f:
        for r in out: f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    print("grantee website hints: %d looked up · %d candidates kept (name match ≥ 0.8) · %d no close match" % (len(out), kept, len(out) - kept))

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("items"); p.add_argument("--cap", type=int, default=60)
    p = sp.add_parser("ingest"); p.add_argument("file")
    a = ap.parse_args(); {"items": cmd_items, "ingest": cmd_ingest}[a.cmd](a)
