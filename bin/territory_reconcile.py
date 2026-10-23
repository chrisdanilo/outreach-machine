#!/usr/bin/env python3
"""territory_reconcile.py — does the territory ledger agree with the ledgers of record?

Installed 2026-09-03 alongside territory_check.py.

territory_check.py asks "is the walk in order?". This asks the prior question: "does the walk
describe reality?". A territory whose counts drift from contacted.jsonl is worse than no territory
ledger at all, because it makes a false claim countable and therefore trusted.

Same shape as ledger_reconcile.py (Gmail vs contacted) and migrate_contacted.py (md vs jsonl) —
set-difference between two stores that should agree, reported as the appends owed.

  Reads  : territory.json · contacted.jsonl · candidates.jsonl
  Writes : the `Territory reconcile:` line + runs/<date>/territory_reconcile.json
  Exit   : 0 clean · 1 a drift was found (report-only by design; does not fail the run)
"""
import json, sys, datetime, pathlib, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
TODAY = datetime.date.today().isoformat()


def rows(p):
    return [json.loads(l) for l in (ROOT / p).read_text(encoding="utf-8").splitlines() if l.strip()]


def main():
    tp = ROOT / "territory.json"
    if not tp.exists():
        print("Territory reconcile: SKIPPED — territory.json not found"); return 0
    led = json.loads(tp.read_text(encoding="utf-8"))
    T, excl = led["territories"], led.get("excluded", {})

    orgs = [r for r in rows("contacted.jsonl") if r.get("type") == "org"]
    cand = rows("candidates.jsonl")

    ledger_contacted = collections.Counter(o["state"] for o in orgs if o.get("state"))
    ledger_held = collections.Counter(
        c["state"] for c in cand
        if c.get("state") and (str(c.get("status", "")).startswith("HELD")
                               or c.get("status") == "RESEARCH_OWED_GATE1"))

    drift, unknown_state, states_missing = [], [], []

    # 1 · a state that appears in Ledger A but has no territory row at all
    for st in ledger_contacted:
        if st not in T and st not in excl:
            states_missing.append(st)

    # 2 · counts that disagree. territory.json may legitimately lead Ledger A by one run (drafted
    #     tonight, logged by R14 tomorrow), so a POSITIVE delta is expected and a NEGATIVE one is not.
    for st, t in T.items():
        lc, lh = ledger_contacted.get(st, 0), ledger_held.get(st, 0)
        if t["contacted"] < lc:
            drift.append({"state": st, "field": "contacted", "territory": t["contacted"],
                          "ledger": lc, "kind": "TERRITORY BEHIND LEDGER — an org was contacted and never entered"})
        elif t["contacted"] > lc:
            drift.append({"state": st, "field": "contacted", "territory": t["contacted"],
                          "ledger": lc, "kind": "expected — drafted, not yet R14-logged"})
        if t["held"] != lh:
            drift.append({"state": st, "field": "held", "territory": t["held"], "ledger": lh,
                          "kind": "held count disagrees with candidates.jsonl"})

    # 3 · the honest gap: rows that cannot be assigned to any territory
    unknown_state = [{"store": "contacted.jsonl", "n": sum(1 for o in orgs if not o.get("state"))},
                     {"store": "candidates.jsonl", "n": sum(1 for c in cand if not c.get("state"))}]

    hard = [d for d in drift if "BEHIND LEDGER" in d["kind"] or "disagrees" in d["kind"]]
    tot_unknown = sum(u["n"] for u in unknown_state)

    print(f"Territory reconcile: {len(T)} territories · {len(hard)} hard drift · "
          f"{len(states_missing)} states in Ledger A with no territory row · "
          f"{tot_unknown} rows unassignable (state:null)")
    for d in hard:
        print(f"  🔴 {d['state']} {d['field']}: territory={d['territory']} ledger={d['ledger']} — {d['kind']}")
    for st in states_missing:
        print(f"  🔴 {st} has {ledger_contacted[st]} contacted organisations and NO territory row")
    for u in unknown_state:
        if u["n"]:
            print(f"  ⚠️ {u['n']} rows in {u['store']} carry state:null — those organisations cannot be "
                  f"assigned to a territory, so every affected `remaining` is overstated")

    outdir = ROOT / "runs" / TODAY
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "territory_reconcile.json").write_text(json.dumps({
        "script": "territory_reconcile.py", "version": "1.0.0",
        "generated_at": datetime.datetime.now().astimezone().isoformat(), "run_date": TODAY,
        "drift": drift, "hard_drift": hard, "states_missing_row": states_missing,
        "unassignable": unknown_state,
        "status": "OK" if not hard and not states_missing else "PROBLEM",
    }, indent=2), encoding="utf-8")
    return 1 if (hard or states_missing) else 0


if __name__ == "__main__":
    sys.exit(main())
