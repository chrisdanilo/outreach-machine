#!/usr/bin/env python3
"""queue_health.py - slack, pace and floor lines. LIVE (report-only, never blocks).
Usage: queue_health.py --waiting N [--drafted-tonight N]
    --waiting: Email 1 drafts in Gmail at run end (the run counts them at GATHER).
Reads: config.json, contacted.jsonl. Writes: runs/<date>/queue_health.json."""
import json, sys, datetime, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
cfg = json.loads((ROOT/"config.json").read_text())
args = dict(zip(sys.argv[1::2], sys.argv[2::2]))
waiting = int(args.get("--waiting", -1))
if waiting < 0: print("FATAL: --waiting N required (count Email 1 drafts in Gmail first)"); sys.exit(2)
target, ceiling = int(cfg["target_drafts"]), int(cfg["queue_ceiling"])
today = datetime.date.today()
# pace: E1 dates over the last 5 WEEKDAYS from contacted.jsonl org records
e1_dates, unsent = [], 0
for line in (ROOT/"contacted.jsonl").read_text().splitlines():
    r = json.loads(line)
    if r.get("type")=="org" and r.get("e1") and r.get("cohort")!="pre-machine":
        # 2026-09-17: a DRAFT WAITING row carries an e1 DATE but no send. Counting it as
        # "outreached" made the Pace line read 36% on a night when nothing had been sent for
        # nine days - the exact fact Pace exists to surface. Ledger A gained draft-waiting rows
        # on 2026-09-16; before that this filter was a no-op, which is why it was never needed.
        if str(r.get("status","")).upper().startswith("DRAFT WAITING"): unsent += 1; continue
        try: e1_dates.append(datetime.date(today.year, int(r["e1"][:2]), int(r["e1"][3:5])))
        except ValueError: pass
wdays, d = [], today
while len(wdays) < 5:
    if d.weekday() < 5: wdays.append(d)
    d -= datetime.timedelta(days=1)
recent = sum(1 for x in e1_dates if x in set(wdays))
pace_target = 5 * target
slack = waiting / target if target else 0
art = {"script":"queue_health.py","run_date":today.isoformat(),"waiting":waiting,"target":target,
       "ceiling":ceiling,"runs_of_slack":round(slack,2),"floor_met_tonight":args.get("--drafted-tonight"),
       "pace_5_weekday":recent,"pace_target":pace_target,"pace_pct":round(recent/pace_target*100) if pace_target else 0,
       "draft_waiting_rows_excluded":unsent}
out = ROOT/"runs"/today.isoformat(); out.mkdir(parents=True, exist_ok=True)
(out/"queue_health.json").write_text(json.dumps(art, indent=2))
print(f"Queue: {waiting} Email 1 drafts waiting · runs of slack: {slack:.1f}" + ("   🔴 BELOW 1 RUN OF SLACK — say so at the top of the report" if slack < 1 else ""))
print(f"Pace: {recent} orgs outreached over the last 5 weekdays · target {pace_target} · {art['pace_pct']}% of pace"
      + (f"   (DRAFT WAITING rows excluded: {unsent} - drafted is not outreached)" if unsent else ""))
