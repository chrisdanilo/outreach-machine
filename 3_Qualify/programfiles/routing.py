#!/usr/bin/env python3
"""routing.py -- which machine owns an org (Rulebook E3/E4/E6; Stage 5). Pure functions, used by build_master.py.
  markets(icps, runs_event): MKT-001 for ICP-001/002/003/005 · MKT-002 for ICP-001–004/006 that run a conference that counts
  (Rulebook E3 — the rule lives there; timing.kind / timing.will_recur apply it). ICP-007/008 belong to no market.
  owner(r): a machine that already has a thread keeps the org (E6; Chris's owner overrides are applied after this);
  not a fit or no market -> none; MKT-002 -> OM-2; MKT-001 -> OM-1."""
MKT1 = {"ICP-001", "ICP-002", "ICP-003", "ICP-005"}
MKT2 = {"ICP-001", "ICP-002", "ICP-003", "ICP-004", "ICP-006"}
def markets(icps, runs_event):
    s = set(icps); mk = set()
    if s & MKT1: mk.add("MKT-001")
    if runs_event and s & MKT2: mk.add("MKT-002")
    return sorted(mk)
def owner(r):
    if r.get("threads"): return r["owner_machine"]
    if r["fit"]["status"] == "not_fit" or not r["markets"] or any((r.get("exclusions") or {}).values()): return "none"
    return "OM-2" if "MKT-002" in r["markets"] else "OM-1"
def keynote_events(events):
    """Every event on record (Rulebook E4: no keynote gate). Whether an event counts toward OM-2 is decided on the rebuild (E3)."""
    return [e for e in (events or []) if isinstance(e, dict)]
