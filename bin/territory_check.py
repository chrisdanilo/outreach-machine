#!/usr/bin/env python3
"""territory_check.py — is the machine working ONE territory at a time, in order?

Installed 2026-09-03 on Chris's instruction: "Why are there 7 new states in this one run? I want
this machine to be systematic and methodical by going county by county across the United States."

🔴 THE DEFECT THIS EXISTS TO END.
On 2026-09-03 the run touched 23 states and drafted into 9 of them in one night. It broke no rule,
because there was none: method.md contains ZERO instances of "saturat*", "territor*", "density" or
"enumerat*". §0.8.3 forbids meeting the floor by descending the TIER ladder. §0.7.2 forbids meeting
it by descending the MARKET. Nothing forbade meeting it by CHANGING THE TERRITORY — the cheapest
door, and the only one marked "Free".

THE RULE THIS ENFORCES (method §0.8.6):
  The territory gate constrains ORDER, never VOLUME. It does not fail the floor and does not stall
  the run. A run short of target_drafts in the active territory SATURATES it, closes it, opens the
  next in `order`, and keeps drafting. Crossing boundaries mid-run is LEGAL and reported.
  🔴 Only two things FAIL: (1) a territory opened OUT OF ORDER, (2) two territories IN PROGRESS
  at once — because both mean the walk stopped being a walk.

  Reads  : territory.json
  Writes : the two §0.6 report lines + runs/<date>/territory.json
  Exit   : 0 clean · 1 out-of-order open or concurrent IN PROGRESS · 2 shadow warnings only
"""
import json, sys, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
TODAY = datetime.date.today().isoformat()
SHADOW = True   # flip to False once Chris ratifies — graduated-gate precedent, method §0.10

DONE = {"CONTACTED", "HELD", "OUT_OF_MARKET", "CLOSED_R1"}
THIN = 0.30     # held/total above this is reported as SATURATED THIN, never hidden


def saturated(t):
    """§0.8.6. Countable, so it cannot be argued with. Returns (bool, [reasons it is not])."""
    why = []
    if not t.get("enumerated"):
        why.append("not enumerated — no denominator exists")
    if t.get("lead_agencies_total") is None:
        why.append("lead_agencies_total is null")
    if t.get("remaining") is None:
        why.append("remaining is null")
    elif t["remaining"] > 0:
        why.append(f"{t['remaining']} agencies REMAINING")
    ags = t.get("agencies") or []
    # 🔴 A COUNT WITHOUT THE ROSTER BEHIND IT IS A RECALLED NUMBER. The whole point of the ledger is
    # that coverage is VISIBLE; `contacted: 9` with an empty agencies[] is exactly the measured-vs-
    # recalled defect this machine keeps finding in itself. Itemise or it does not close.
    if t.get("lead_agencies_total") is not None and not ags:
        why.append(f"agencies[] is empty — {t['lead_agencies_total']} agencies claimed, 0 itemised")
    if t.get("lead_agencies_total") is not None and ags and len(ags) != t["lead_agencies_total"]:
        why.append(f"agencies[] holds {len(ags)} rows, lead_agencies_total says {t['lead_agencies_total']}")
    for a in ags:
        d = a.get("disposition")
        if d not in DONE:
            why.append(f"{a.get('org')}: disposition {d!r}")
        if d == "HELD":
            # 🔴 a HELD row with no reason is not a saturated agency, it is an unfinished one
            if not (a.get("reason") or "").strip():
                why.append(f"{a.get('org')}: HELD with no reason")
            r = a.get("retry")
            if not (isinstance(r, str) and (r.startswith("event: ") or len(r) == 10)):
                why.append(f"{a.get('org')}: HELD with retry={r!r} — needs a date or 'event: ...'")
        if d == "OUT_OF_MARKET" and not (a.get("reason") or "").strip():
            why.append(f"{a.get('org')}: OUT_OF_MARKET with no reason")
    return (not why), why


def main():
    p = ROOT / "territory.json"
    if not p.exists():
        print("Territory: SKIPPED — territory.json not found. The ledger IS the walk; "
              "without it there is no order to check.")
        return 2
    led = json.loads(p.read_text(encoding="utf-8"))
    T, order, excl = led["territories"], led["order"], led.get("excluded", {})
    active = led.get("active_territory")

    problems, warnings = [], []

    # ---- FAIL 1: more than one territory IN PROGRESS -------------------------------------------
    in_prog = [s for s, t in T.items() if t.get("status") == "IN PROGRESS"]
    if len(in_prog) > 1:
        problems.append(f"🔴 {len(in_prog)} territories are IN PROGRESS at once: {', '.join(sorted(in_prog))}. "
                        f"The walk is only a walk if one is open. (This is the 2026-09-03 state and is "
                        f"the debt being paid down, not a new breach — see the migration block.)")

    # ---- FAIL 2: an open territory that sits AFTER an unsaturated earlier one -------------------
    rank = {s: i for i, s in enumerate(order)}
    # 🔴 MIGRATION BASELINE. 20 territories were already open when this gate was installed on
    # 2026-09-03 — that is the debt the ledger exists to pay down, not a breach to punish nightly.
    # A gate that can never pass gets switched off, and a switched-off gate protects nothing.
    # Only territories OPENED AFTER the baseline are scored for order.
    baseline = led.get("migration_baseline") or {}
    grandfathered = set(baseline.get("territories_open_at_install", []))
    out_of_order = []
    for s in in_prog:
        if s in grandfathered:
            continue
        if s not in rank:
            warnings.append(f"{s} is IN PROGRESS but absent from `order`")
            continue
        earlier = [e for e in order[:rank[s]] if e in T and e not in excl]
        for e in earlier:
            ok, _ = saturated(T[e])
            if not ok and T[e].get("status") != "SATURATED":
                out_of_order.append((s, e)); break
    if out_of_order:
        for s, e in out_of_order:
            problems.append(f"🔴 OUT-OF-ORDER OPEN — {s} is open while {e} (earlier in `order`) is not saturated")

    # ---- the active territory ------------------------------------------------------------------
    if active not in T:
        problems.append(f"🔴 active_territory {active!r} is not in territories")
        at = None
    else:
        at = T[active]

    # ---- report lines --------------------------------------------------------------------------
    sat_now = [s for s, t in T.items() if saturated(t)[0]]
    if at:
        ok, why = saturated(at)
        tot = at.get("lead_agencies_total")
        pct = f"{round(100*at['contacted']/tot)}%" if tot else "—%"
        cc, ct = at.get("counties_covered"), at.get("counties_total")
        counties = f"counties {cc if cc is not None else '?'} of {ct if ct is not None else '?'}"
        status = "SATURATED" if ok else at.get("status", "IN PROGRESS")
        print(f"Territory: {active} {status} — {at['contacted']+at['held']+at['out_of_market']} of "
              f"{tot if tot is not None else '?'} lead agencies · {at['contacted']} contacted · "
              f"{at['held']} held · {at['out_of_market']} out-of-market · "
              f"{at['remaining'] if at['remaining'] is not None else '?'} remaining · {pct} · "
              f"{counties} · opened {at.get('opened') or '—'} · last worked {at.get('last_worked') or '—'}")
        if not ok:
            print("  not saturated because: " + " · ".join(why[:6]) + (" · …" if len(why) > 6 else ""))
        if tot and at["held"] / tot > THIN:
            warnings.append(f"⚠️ {active} SATURATED THIN — {at['held']} of {tot} held, not contacted. "
                            f"A state finished mostly by holding is a finding about the state.")

    nxt = next((s for s in order if s in T and s not in excl and T[s].get("status") != "SATURATED"
                and s != active), None)
    nxt_n = T[nxt]["lead_agencies_total"] if nxt and nxt in T else None
    nxt_e = "yes" if nxt and T[nxt].get("enumerated") else "no"
    print(f"Territory order: next {nxt or '—'} ({nxt_n if nxt_n is not None else '?'} agencies, "
          f"enumerated {nxt_e}) · boundaries crossed this run: {len(in_prog)-1 if len(in_prog)>1 else 0}"
          f"{' ['+', '.join(sorted(in_prog))+']' if len(in_prog)>1 else ''} · "
          f"out-of-order opens: {len(out_of_order)} · SATURATED to date: {len(sat_now)} of 51")

    if grandfathered:
        still = sorted(g for g in grandfathered if g in T and T[g].get("status") != "SATURATED")
        print(f"  ⏪ migration debt: {len(still)} of {len(grandfathered)} territories open at install "
              f"still unsaturated — {', '.join(still) if still else 'none'} "
              f"(grandfathered from the order check until closed)")

    un_enum = [s for s, t in T.items() if not t.get("enumerated")]
    if un_enum:
        print(f"  ⚠️ never enumerated (no denominator): {', '.join(sorted(un_enum))} — "
              f"§0.3 step 12b enumerates before drafting")

    for w in warnings:
        print("  " + w)
    for pr in problems:
        print("  " + pr)

    mode = "SHADOW" if SHADOW else "BINDING"
    outdir = ROOT / "runs" / TODAY
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "territory.json").write_text(json.dumps({
        "script": "territory_check.py", "version": "1.0.0", "mode": mode,
        "generated_at": datetime.datetime.now().astimezone().isoformat(), "run_date": TODAY,
        "active_territory": active, "next": nxt,
        "in_progress": sorted(in_prog), "out_of_order": out_of_order,
        "saturated": sorted(sat_now), "never_enumerated": sorted(un_enum),
        "problems": problems, "warnings": warnings,
        "status": "OK" if not problems else "PROBLEM",
    }, indent=2), encoding="utf-8")

    if not problems:
        return 0
    return 2 if SHADOW else 1


if __name__ == "__main__":
    sys.exit(main())
