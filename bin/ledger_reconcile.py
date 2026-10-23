#!/usr/bin/env python3
"""ledger_reconcile.py - R14 set-difference: Gmail sent sweep vs contacted.jsonl. LIVE (read-only).
Input: runs/<date>/sent_sweep.json - written by the run at GATHER:
    [{"thread": id, "date": "MM-DD", "to": [addr], "cc": [addr], "org_domain": "x.org"}]
Output: the appends owed to BOTH ledger forms. Exit 3 = input artifact missing (run must write it first)."""
import json, sys, datetime, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
today = datetime.date.today().isoformat()
p = ROOT/"runs"/today/"sent_sweep.json"
if not p.exists(): print(f"NO INPUT: write runs/{today}/sent_sweep.json at GATHER (unfiltered 3d sent sweep per D-SWEEP), then rerun"); sys.exit(3)
sweep = json.loads(p.read_text())
known_addr, known_dom = set(), set()
for line in (ROOT/"contacted.jsonl").read_text().splitlines():
    r = json.loads(line)
    if r.get("type")=="address": known_addr.add(r["address"])
    if r.get("type")=="org": known_dom.update(r.get("domains",[]))
missing_a, missing_b = [], []
for s in sweep:
    if s.get("org_domain") and s["org_domain"] not in known_dom: missing_a.append(s)
    for a in (s.get("to",[]) + s.get("cc",[])):
        if a.lower() not in known_addr: missing_b.append({"address":a.lower(),"thread":s.get("thread"),"date":s.get("date")})
print(f"Contacted ledger: {len(sweep)} sends swept · {len(missing_a)} org(s) + {len(missing_b)} address(es) MISSING — append to contacted.md AND contacted.jsonl:")
for x in missing_a: print("  ORG:", json.dumps(x, ensure_ascii=False))
for x in missing_b: print("  ADDR:", json.dumps(x, ensure_ascii=False))
sys.exit(0 if not (missing_a or missing_b) else 1)
