#!/usr/bin/env python3
"""
counted_record.py — the ONE reader of the counted record.

TLP/dashboard-data.json is the source of truth for every OUTCOME figure: Approaches,
Meetings, Proposals, Sales, Delivery, Pink Sheets. Those numbers are a judgment call made by
a refresh session with TLP-Rules.md in hand. No script derives them, and no script may
re-derive them from a different source -- that is how a page ends up showing one quantity
twice (25 and 14 on 2026-09-07, when the funnel counted replies out of contacted.jsonl).

Until 2026-09-28 this module parsed a markdown table in TLP-Practice-Dashboard.md. The record
is now JSON with one block per quarter; the markdown file is archived.

Division of ownership, so it stays fixed:
  OUTCOMES  -> TLP/dashboard-data.json                 (this module)
  SENDS     -> contacted.jsonl                          (the outreach machine)
  CAMPAIGN  -> funnel-outcomes.json                     (which outcomes are cold outreach, and
               ATTRIBUTION                               which email produced each reply)

read() returns (counted_through, {field: (value, target)}) summed over every quarter block that
overlaps the campaign era (CAMPAIGN_FLOOR onward). The funnel is campaign-scoped and does not
reset at a quarter rollover, so its comparator must not either. Null fields (a quarter not yet
counted) are skipped, never treated as zero.
"""
import json, pathlib

HST  = pathlib.Path(__file__).resolve().parents[3]
DATA = HST / "TLP" / "dashboard-data.json"

FIELDS = ("Approaches", "Meetings", "Proposals", "Sales", "Delivery", "Pink Sheets")
CAMPAIGN_FLOOR = "2026-08-11"


def load(path=None):
    return json.loads((path or DATA).read_text())


def current_quarter(d, today):
    """The block whose dates contain today; else the most recent block that has started."""
    qs = sorted(d["quarters"], key=lambda q: q["start"])
    for q in qs:
        if q["start"] <= today <= q["end"]:
            return q
    started = [q for q in qs if q["start"] <= today]
    return started[-1] if started else qs[0]


def read(path=None):
    """Return (counted_through, {field: (value, target)}). Raises if no quarter carries a counted
    Approaches figure -- a missing counted record must stop the run, never default to zero."""
    d = load(path)
    blocks = [q for q in d["quarters"] if q["end"] >= CAMPAIGN_FLOOR]
    through = max((q.get("counted_through") or "" for q in blocks), default="")
    if not through:
        raise SystemExit("counted_record: no counted_through date in any quarter block")
    rows = {}
    for f in FIELDS:
        vals = [q["fields"].get(f) for q in blocks if q["fields"].get(f) is not None]
        target = None
        for q in blocks:
            if q["fields"].get(f) is not None:
                target = q["targets"].get(f)       # the latest counted quarter's target
        rows[f] = (sum(vals) if vals else None, target)
    if rows["Approaches"][0] is None:
        raise SystemExit("counted_record: Approaches has no value in any quarter block")
    return through, rows


def value(rows, field):
    return rows.get(field, (None, None))[0]
