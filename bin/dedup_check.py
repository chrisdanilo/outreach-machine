#!/usr/bin/env python3
"""dedup_check.py - R1 (one-org-one-thread) and R11 (two-ledger de-dup) as CODE, not a grep.

Installed 2026-08-25 per CAPA-2026-08-25-org-domain-identity, Chris approved.

WHY THIS EXISTS. R1/R11 were performed as `grep -c "<domain>" contacted.md`. A zero-hit grep cannot
distinguish "never contacted" from "contacted under this org's OTHER domain" - it returns 0 for both.
[Org 0462] publishes org0251.example and mails from org0253.example; Five County's
site is org0174.example and its mail is @org0389.example. Three such orgs are known.

WHAT IT DOES. Set intersection instead of substring search, over the UNION of:
  - contacted.jsonl org records          -> .domains[]   (already an ARRAY; the parser already
                                                          finds every domain in the Domain cell)
  - contacted.jsonl address records      -> .domain
  - config.json domain_aliases           -> both sides, treated as one identity
  - hubspot-suppression.md               -> any domain string
and expands every candidate domain through the alias map before comparing.

VERDICTS
  CLOSED  - a candidate domain intersects a recorded domain. R1 closes the org. Only Chris reopens.
  HOLD    - PARTIAL match: one domain of this org's alias-set is recorded and another is not, or the
            candidate resolves to an alias group that is only half-present. This is the case that was
            previously SILENT and is the whole point of the script.
  CLEAR   - no intersection anywhere. Genuinely new.

USAGE
  python3 bin/dedup_check.py org0253.example org0251.example
  python3 bin/dedup_check.py --json org0229.example
  python3 bin/dedup_check.py --audit          # scan the whole book for single-domain orgs + gaps
Exit codes: 0 CLEAR - 1 CLOSED - 2 HOLD - 3 input error
"""
import json, sys, pathlib, re, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent

def load():
    cfg = json.loads((ROOT/"config.json").read_text())
    aliases = {k.lower(): v.lower() for k, v in cfg.get("domain_aliases", {}).items()}
    # 2026-08-27, Chris D2 ("keep them separate. we will email each as a new org"):
    # a SHARED INSTITUTIONAL TENANT (org0572.example, org0227.example) is mailed from by many
    # unrelated orgs. An address there is a real R11 person-level hit, but it must NEVER
    # decide the ORG verdict - otherwise the first CCE association contacted closes every
    # other one. Tenants are dropped from the candidate set and reported separately.
    shared = {d.lower() for d in cfg.get("shared_tenant_domains", [])}
    # alias groups: undirected union-find over the alias pairs
    parent = {}
    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x: parent[x] = parent[parent[x]]; x = parent[x]
        return x
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb: parent[ra] = rb
    for a, b in aliases.items(): union(a, b)

    org_domains, addr_domains, org_of = collections.defaultdict(set), set(), {}
    for line in (ROOT/"contacted.jsonl").read_text().splitlines():
        if not line.strip(): continue
        r = json.loads(line)
        if r.get("type") == "org":
            label = r.get("org") or f"cohort:{(r.get('domains') or ['?'])[0]}"
            for d in r.get("domains", []):
                org_domains[label].add(d.lower()); org_of[d.lower()] = label
        elif r.get("type") == "address" and r.get("domain"):
            addr_domains.add(r["domain"].lower())
    supp = set(d.lower() for d in re.findall(r"[a-z0-9][a-z0-9.-]*\.(?:org|com|net|gov|edu|info|us|co|cc)",
                                             (ROOT/"hubspot-suppression.md").read_text().lower()))
    return find, org_domains, addr_domains, org_of, supp, aliases, shared

def group(find, d): return find(d.lower())

def check(cands, verbose=True):
    find, org_domains, addr_domains, org_of, supp, aliases, shared = load()
    recorded = set().union(*org_domains.values()) if org_domains else set()
    recorded |= addr_domains
    cands = [c.lower().strip() for c in cands if c.strip()]
    # Shared institutional tenants (Chris D2, 2026-08-27) never drive the ORG verdict.
    tenants = [c for c in cands if c in shared]
    if tenants:
        cands = [c for c in cands if c not in shared]
        if verbose:
            for t in tenants:
                print(f"   - {t} is a SHARED INSTITUTIONAL TENANT (config.shared_tenant_domains) - "
                      f"excluded from the org verdict; many unrelated orgs mail from it")
        if not cands:
            if verbose:
                print("R1/R11 de-dup: candidate set was ONLY shared tenants -> INPUT ERROR. "
                      "Pass the organisation's own website domain.")
            return "HOLD", ["candidate set contained only shared institutional tenants"]
    # expand candidates through alias groups
    cand_groups = {group(find, c) for c in cands}
    rec_by_group = collections.defaultdict(set)
    for d in recorded: rec_by_group[group(find, d)].add(d)

    hits = {c for c in cands if c in recorded}
    group_hits = {c for c in cands if rec_by_group.get(group(find, c))}
    supp_hits = {c for c in cands if c in supp}

    verdict, why = "CLEAR", []
    if hits:
        verdict = "CLOSED"
        for c in sorted(hits):
            why.append(f"{c} is in contacted (org: {org_of.get(c,'address-record only')})")
    elif group_hits:
        verdict = "CLOSED"
        for c in sorted(group_hits):
            sib = sorted(rec_by_group[group(find, c)])
            why.append(f"{c} shares an alias group with recorded {sib} -> SAME ORGANISATION")
    else:
        # PARTIAL: candidate set spans >1 alias group, or a known alias sibling is unrecorded
        known_alias_sibs = {a for c in cands for a in (aliases.get(c), ) if a} | \
                           {k for k, v in aliases.items() if v in cands}
        if len(cand_groups) > 1 and len(cands) > 1:
            verdict = "HOLD"
            why.append(f"candidate domains {cands} are NOT declared as one organisation in "
                       f"config.domain_aliases - cannot prove they are the same org or different orgs")
        elif known_alias_sibs and not (known_alias_sibs & recorded):
            why.append(f"alias siblings {sorted(known_alias_sibs)} known and also unrecorded - consistent")
    if supp_hits:
        why.append(f"ALSO in hubspot-suppression: {sorted(supp_hits)}")
        if verdict == "CLEAR": verdict = "HOLD"
    if verbose:
        print(f"R1/R11 de-dup: {' '.join(cands)} -> {verdict}")
        for w in why: print(f"   - {w}")
        if verdict == "CLEAR" and not why: print("   - no intersection in org records, address records, aliases or suppression")
    return verdict, why

def audit():
    find, org_domains, addr_domains, org_of, supp, aliases, shared = load()
    single = [o for o, d in org_domains.items() if len(d) == 1]
    multi  = {o: sorted(d) for o, d in org_domains.items() if len(d) > 1}
    orphan_addr = sorted(d for d in addr_domains
                         if d not in org_of and not any(group(find, d) == group(find, x) for x in org_of))
    print(f"Org identity: {len(org_domains)} orgs · {len(multi)} with both domains recorded · "
          f"{len(single)} single-domain · {len(orphan_addr)} ambiguous")
    if multi:
        print("  multi-domain orgs:")
        for o, d in sorted(multi.items()): print(f"    {o}: {d}")
    if orphan_addr:
        print("  🔴 AMBIGUOUS - address domains with no org record and no alias:")
        for d in orphan_addr: print(f"    {d}")
    print(f"  alias pairs configured: {len(aliases)}")
    return 0

if __name__ == "__main__":
    args = [a for a in sys.argv[1:]]
    if "--audit" in args: sys.exit(audit())
    as_json = "--json" in args
    cands = [a for a in args if not a.startswith("--")]
    if not cands: print(__doc__); sys.exit(3)
    v, why = check(cands, verbose=not as_json)
    if as_json: print(json.dumps({"candidates": cands, "verdict": v, "reasons": why}, indent=2))
    sys.exit({"CLEAR": 0, "CLOSED": 1, "HOLD": 2}[v])
