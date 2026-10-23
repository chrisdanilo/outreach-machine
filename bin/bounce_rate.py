#!/usr/bin/env python3
"""
bounce_rate.py - derive the machine-era bounce rate from contacted.md. Nothing is carried forward.

WHY THIS EXISTS
    On 2026-08-25 the bounce rate was published TWICE from an estimated denominator -
    once from a "~140" carried forward in contacted.md, once from a name-join that
    silently dropped two-thirds of Ledger B. That number GATES new-org drafting.
    See CAPA-2026-08-25-empty-new-org-queue section 4c.

CONTRACT
    Reads   : contacted.md (Ledger B), config.json
    Writes  : runs/<date>/bounce_rate.json
    Exits   : 0 on success, 1 on a failed internal identity, 2 on unreadable input
    Carries : NOTHING. Every number is re-derived from the ledger on every run.

THE RULE THIS ENFORCES
    A number that gates a control is counted in the run that uses it, from a named
    file, and the artifact records which file and which filter produced it.
"""

import json, re, sys, datetime, pathlib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent


def load_config():
    return json.loads((ROOT / "config.json").read_text(encoding="utf-8"))


def org_domain_send_dates(text):
    """Ledger A -> {domain: 'MM-DD'}. Keyed on DOMAIN, never on org name.

    Org names differ between the two ledgers ('[Org 1003] (United Way
    Cville)' vs 'Blue Ridge'), so a name join drops rows silently. Domains appear in
    both and are exact.
    """
    block = text.split("# LEDGER A")[1].split("# LEDGER B")[0]
    out = {}
    for line in block.splitlines():
        if not line.startswith("|") or "---" in line or "CORRECTION" in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 4 or not re.match(r"^\d\d-\d\d$", cells[3]):
            continue
        for dom in re.findall(r"[a-z0-9.-]+\.(?:org|com|net|gov|edu|us|info|co|cc)", cells[1].lower()):  # +edu 2026-08-27: org0227.example · +cc 2026-10-04 BQ-027: org0672.example, org0072.example
            out[dom] = cells[3]
    return out


def delivered_addresses(text, never):
    """Ledger B DELIVERED -> [(address, domain)]. Truncated entries ('mlocascio@')
    inherit the domain from the last fully-qualified address in the same cell."""
    block = text.split("# LEDGER B")[1].split("## ✅ DELIVERED")[1].split("\n---\n")[0]
    rows = []
    for line in block.splitlines():
        if not line.startswith("|") or "---" in line or "Addresses" in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        toks = [re.sub(r"[*`()\[\],]", "", t) for t in re.split(r"[ ·|]+", cells[1]) if "@" in t]
        if not toks:
            continue
        dom = None
        for t in reversed(toks):
            part = t.split("@", 1)[1]
            if "." in part:
                dom = part.lower()
                break
        for t in toks:
            part = t.split("@", 1)[1]
            d = part.lower() if "." in part else dom
            addr = t.lower() if "." in part else (t + dom).lower() if dom else t.lower()
            if addr in never:
                continue
            rows.append((addr, d))
    return rows


def main():
    cfg = load_config()
    today = datetime.date.today().isoformat()
    try:
        text = (ROOT / "contacted.md").read_text(encoding="utf-8")
    except OSError as e:
        print(f"FATAL: cannot read contacted.md - {e}", file=sys.stderr)
        return 2

    baseline = cfg["bounce_rate_baseline"][5:]          # 'YYYY-MM-DD' -> 'MM-DD'
    catch_all = set(cfg["catch_all_domains"])
    never = {a.lower() for a in cfg["never_recipients"]}
    bounces = cfg["hard_bounces"]

    dates = org_domain_send_dates(text)
    for alias, canonical in cfg.get("domain_aliases", {}).items():
        if canonical in dates:
            dates.setdefault(alias, dates[canonical])
    delivered = delivered_addresses(text, never)

    bounced_domains = {a.split("@", 1)[1].lower() for a in bounces}
    unmapped = sorted({d for _, d in delivered if d and d not in dates})

    def score(cut):
        den = ca = 0
        for _, dom in delivered:
            dt = dates.get(dom)
            if dt and dt >= cut:
                den += 1
                if dom in catch_all:
                    ca += 1
        b = sum(1 for meta in bounces.values() if meta["sent"][5:] >= cut)
        return b, den + b, ca

    b_all, att_all, ca_all = score("00-00")
    b_base, att_base, ca_base = score(baseline)

    nca_base = att_base - ca_base
    rate = (b_base / nca_base * 100) if nca_base else 0.0
    rate_raw = (b_base / att_base * 100) if att_base else 0.0
    ceiling = float(cfg["max_bounce_rate_pct"])
    c = ceiling / 100.0
    headroom = max(0, int((c * nca_base - b_base) / (1 - c))) if nca_base else 0

    # ---- internal identities. A silent join failure is what this catches. ----
    problems = []
    if unmapped:
        problems.append(f"{len(unmapped)} delivered domain(s) absent from Ledger A: {unmapped}")
    if att_base > att_all:
        problems.append("baseline window larger than all-time - impossible")
    if b_base > len(bounces):
        problems.append("more baseline bounces than configured bounces")
    if nca_base <= 0:
        problems.append("non-catch-all denominator is zero - refusing to divide")

    artifact = {
        "script": "bounce_rate.py",
        "version": "1.0.0",
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "run_date": today,
        "status": "FAILED" if problems else "OK",
        "problems": problems,
        "source_file": "contacted.md",
        "filter": {
            "baseline": cfg["bounce_rate_baseline"],
            "catch_all_domains_excluded": sorted(catch_all),
            "never_recipients_excluded": sorted(never),
            "bounce_definition": "DSN-confirmed only; auto-replies never count",
        },
        "all_time": {
            "hard_bounces": b_all,
            "attempted": att_all,
            "catch_all": ca_all,
            "rate_non_catch_all_pct": round(b_all / (att_all - ca_all) * 100, 2) if att_all - ca_all else None,
        },
        "scored_window": {
            "since": cfg["bounce_rate_baseline"],
            "hard_bounces": b_base,
            "attempted_raw": att_base,
            "catch_all_excluded": ca_base,
            "denominator_non_catch_all": nca_base,
            "rate_non_catch_all_pct": round(rate, 2),
            "rate_raw_pct": round(rate_raw, 2),
        },
        "ceiling_pct": ceiling,
        "over_ceiling": rate > ceiling,
        "new_org_drafting": "HOLD" if rate > ceiling else "CLEAR",
        "headroom_bounces": headroom,
        "headroom_definition": "further consecutive bounced sends before the rate exceeds the ceiling; each one adds to BOTH numerator and denominator",
    }

    outdir = ROOT / "runs" / today
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "bounce_rate.json").write_text(json.dumps(artifact, indent=2), encoding="utf-8")

    print(f"Bounces: {b_base} of {nca_base} non-catch-all since {cfg['bounce_rate_baseline']} "
          f"= {rate:.2f}% (raw {rate_raw:.2f}% of {att_base}) · ceiling {ceiling}% · "
          f"{artifact['new_org_drafting']} · headroom {artifact['headroom_bounces']} bounce(s)")
    print(f"All-time for reference: {b_all} of {att_all - ca_all} non-catch-all = "
          f"{artifact['all_time']['rate_non_catch_all_pct']}%")
    if problems:
        for p in problems:
            print(f"FAILED: {p}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
