#!/usr/bin/env python3
"""calibration.py — WERE WE RIGHT ABOUT THIS ADDRESS?

Installed 2026-08-28 on Chris's instruction: "I want to keep a record of how many emails we
thought were invalid but ended up being okay to send (didn't bounce) and how many we thought
were safe to send but ended up bouncing... so that we can learn about our process and how much
we can trust tools like zerobounce and apollo and these websites themselves."

Reads calibration-log.jsonl. Writes runs/<date>/calibration.json.
Prints the one-line stat that goes at the TOP OF EVERY DOSSIER.

THE CONFUSION MATRIX. Positive = "this address is safe to send."

                          | actually deliverable | actually bad
  we said SAFE   (sent)   |         TP           |     FN   <- "thought safe, it bounced"
  we said UNSAFE (held)   |         FP           |     TN   <- "thought invalid, was fine"

🔴 THE CENSORING PROBLEM, STATED UP FRONT.
A held address is never sent, so its true outcome is normally UNOBSERVABLE. FP and TN can only
be scored when a side-channel proves the answer: Chris overrides the hold and sends; the person
replies or auto-replies from that mailbox; or the same mailbox turns up delivering elsewhere.
Every other hold is CENSORED and is counted separately.

🔴 THEREFORE: `FP = 0` NEVER MEANS "we do not over-block." It usually means "we never found out."
The censored count is printed beside it precisely so the zero cannot be misread — this is
method.md §0.9's "over-blocking is invisible and permanent" made countable.

Row schema (append-only, one row per address per decision):
 {"date","address","org","predicted":"VALID|INVALID","predictor","class":"V1|V2|V3|inference",
  "hold_type":"deliverability|identity|selection","action":"SENT|HELD",
  "outcome":"delivered|bounced|no-signal|untested","evidence","note"}

`predictor` is WHO made the call — the thing whose trustworthiness we are measuring:
  website-live-page · website-cached · apollo · zerobounce · machine-inference
  · machine-rule:<rule> · human-transcription · unknown-historical

`hold_type` — only `deliverability` and `identity` are predictions about the ADDRESS and score.
`selection` (e.g. R4 excluded the CEO) is a preference, not a claim about validity: NEVER scored.
"""
import json, sys, datetime, pathlib, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOG = ROOT / "calibration-log.jsonl"
if not LOG.exists():
    print("Address calibration: no log yet — calibration-log.jsonl not found"); sys.exit(3)

rows = [json.loads(l) for l in LOG.read_text().splitlines() if l.strip()]
scored = [r for r in rows if r.get("hold_type") in ("deliverability", "identity")]

TP = [r for r in scored if r["predicted"] == "VALID"   and r["outcome"] == "delivered"]
FN = [r for r in scored if r["predicted"] == "VALID"   and r["outcome"] == "bounced"]
FP = [r for r in scored if r["predicted"] == "INVALID" and r["outcome"] == "delivered"]
TN = [r for r in scored if r["predicted"] == "INVALID" and r["outcome"] == "bounced"]
CENSORED = [r for r in scored if r["predicted"] == "INVALID" and r["outcome"] == "untested"]
NOSIG = [r for r in scored if r["outcome"] == "no-signal"]

sent = len(TP) + len(FN)
precision = (len(TP) / sent * 100) if sent else None

# Per-predictor trust: only rows whose outcome was actually observed
by_pred = collections.defaultdict(lambda: {"right": 0, "wrong": 0, "censored": 0})
for r in scored:
    p = r.get("predictor", "unknown")
    if r["outcome"] == "untested":
        by_pred[p]["censored"] += 1
    elif r in TP or r in TN:
        by_pred[p]["right"] += 1
    elif r in FN or r in FP:
        by_pred[p]["wrong"] += 1

out = {
    "generated": datetime.date.today().isoformat(),
    "sent_and_observed": sent,
    "TP_said_safe_and_delivered": len(TP),
    "FN_said_safe_but_bounced": len(FN),
    "FP_said_invalid_but_was_fine": len(FP),
    "TN_said_invalid_and_was_bad": len(TN),
    "CENSORED_held_never_tested": len(CENSORED),
    "no_signal": len(NOSIG),
    "send_precision_pct": round(precision, 2) if precision is not None else None,
    "by_predictor": {k: dict(v) for k, v in sorted(by_pred.items())},
    "FN_detail": [{"address": r["address"], "org": r.get("org"), "date": r.get("date"),
                   "predictor": r.get("predictor"), "note": r.get("note")} for r in FN],
    "FP_detail": [{"address": r["address"], "org": r.get("org"), "date": r.get("date"),
                   "predictor": r.get("predictor"), "note": r.get("note")} for r in FP],
}
d = ROOT / "runs" / datetime.date.today().isoformat()
d.mkdir(parents=True, exist_ok=True)
(d / "calibration.json").write_text(json.dumps(out, indent=2))

prec = f"{out['send_precision_pct']}%" if precision is not None else "n/a"
line = (f"Address calibration: {sent} sent & observed · "
        f"{len(FN)} said-safe-but-BOUNCED · {len(FP)} said-invalid-but-FINE · "
        f"{len(CENSORED)} held & never tested (unknowable) · send precision {prec}")
print(line)

if "--detail" in sys.argv:
    print("\n  Predictor                 right  wrong  censored")
    for k, v in sorted(by_pred.items()):
        print(f"  {k:<26}{v['right']:>5}{v['wrong']:>7}{v['censored']:>10}")
    if FN:
        print("\n  🔴 SAID SAFE, BOUNCED:")
        for r in FN:
            print(f"    {r['date']}  {r['address']:<45} [{r.get('predictor')}] {r.get('note','')}")
    if FP:
        print("\n  🟢 SAID INVALID, WAS FINE:")
        for r in FP:
            print(f"    {r['date']}  {r['address']:<45} [{r.get('predictor')}] {r.get('note','')}")
    if CENSORED:
        print(f"\n  ⬜ HELD, NEVER TESTED — {len(CENSORED)} addresses. We do not know if these were")
        print("     over-blocks. This number is the honest size of our blind spot.")
