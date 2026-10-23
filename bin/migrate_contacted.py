#!/usr/bin/env python3
"""
migrate_contacted.py - contacted.md -> contacted.jsonl, with two independent verifiers.

CONTRACT (Stage 2 of IMPLEMENTATION-PLAN-2026-08-25-v2):
    migrate : parse contacted.md ledgers -> contacted.jsonl (org/address/correction records)
    render  : contacted.jsonl -> contacted.generated.md (Ledger A + B tables only)
    verify  : (1) DATA ROUND-TRIP - re-parse the rendered markdown, compare record sets
              (2) INDEPENDENT CROSS-CHECK - recompute bounce numbers from the jsonl and
                  compare against runs/<today>/bounce_rate.json (written by bounce_rate.py)
    Exit 0 = verified. Non-zero = the diff names what dropped. Markdown stays AUTHORITATIVE
    until 5 consecutive clean dual-write runs (the run prints this script's verify line).
"""
import json, re, sys, datetime, pathlib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
CFG  = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))

def parse_md(text):
    recs = []
    # ---- LEDGER A machine era ----
    a_block = text.split("# LEDGER A")[1].split("# LEDGER B")[0]
    for line in a_block.splitlines():
        if not line.startswith("|") or re.match(r"^\|[-\s|]+\|$", line) or "| Org |" in line.replace("**",""):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) >= 8 and re.match(r"^\d\d-\d\d$", cells[3]) and not cells[0].startswith("\u21b3"):
            doms = re.findall(r"[a-z0-9.-]+\.(?:org|com|net|gov|edu|us|info|co|cc)", cells[1].lower())  # +cc 2026-10-04 BQ-027
            recs.append({"type":"org","org":cells[0],"domains":doms,"state":cells[2],
                         "e1":cells[3],"e2":cells[4],"e3":cells[5],"status":cells[6],
                         "thread":cells[7],"catch_all":"catch-all" in cells[0]})
        elif any(c for c in cells):
            recs.append({"type":"correction","ledger":"A","raw":line.strip()})
    # ---- pre-machine cohort domains ----
    pre = a_block.split("pre-machine cohort")[1] if "pre-machine cohort" in a_block else ""
    for dom in re.findall(r"`([a-z0-9.-]+\.(?:org|com|net|gov|edu|info|cc))`", pre):
        recs.append({"type":"org","cohort":"pre-machine","domains":[dom],"status":"CLOSED-R1"})
    if "+20 more" in pre:
        recs.append({"type":"note","note":"pre-machine cohort INCOMPLETE here: +20 domains / 61 addresses remain authoritative in CCRR-Suppression-Already-Contacted.md - check it too (transcription owed)"})
    # ---- LEDGER B bounced ----
    b_block = text.split("# LEDGER B")[1]
    bounced = b_block.split("BOUNCED")[1].split("## ✅ DELIVERED")[0]
    for line in bounced.splitlines():
        if not line.startswith("|") or re.match(r"^\|[-\s|]+\|$", line) or "| Address |" in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) >= 5 and "@" in cells[0]:
            addr = re.sub(r"[`*🆕\s]", "", cells[0]).lower()
            recs.append({"type":"address","outcome":"bounced","address":addr,
                         "domain":addr.split("@",1)[1],"person":cells[1],"org":cells[2],
                         "sent":cells[3],"dsn":"Auto-reply" not in cells[4] and "auto-reply" not in cells[4],
                         "note":cells[4]})
    # ---- LEDGER B delivered (port of bounce_rate.py expansion) ----
    deliv = b_block.split("## ✅ DELIVERED")[1].split("\n---\n")[0]
    for line in deliv.splitlines():
        if not line.startswith("|") or re.match(r"^\|[-\s|]+\|$", line) or "Addresses" in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3:
            continue
        toks = [re.sub(r"[*`()\[\],]", "", t) for t in re.split(r"[ ·|]+", cells[1]) if "@" in t]
        if not toks:
            continue
        dom = None
        for t in reversed(toks):
            p = t.split("@",1)[1]
            if "." in p: dom = p.lower(); break
        for t in toks:
            p = t.split("@",1)[1]
            d = p.lower() if "." in p else dom
            addr = t.lower() if "." in p else ((t + dom).lower() if dom else t.lower())
            recs.append({"type":"address","outcome":"delivered","address":addr,"domain":d,
                         "org_label":cells[0],"stage":cells[2],
                         "replied":"🟢" in cells[1] and ("🟢 **"+t) in cells[1].replace("`","")})
    return recs

def key(r):
    if r["type"]=="org":     return ("org", tuple(r.get("domains",[])), r.get("e1",""), r.get("status",""))
    if r["type"]=="address": return ("addr", r["outcome"], r["address"])
    return (r["type"], r.get("raw", r.get("note","")))

def render(recs):
    out = ["# LEDGER A — ORGANISATIONS (GENERATED — do not hand-edit)\n",
           "| Org | Domain | ST | E1 sent | E2 | E3 | Status | Thread |","|---|---|---|---|---|---|---|---|"]
    pre = []
    for r in recs:
        if r["type"]=="org" and r.get("cohort")!="pre-machine":
            out.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
                r["org"], " ".join(r["domains"]), r["state"], r["e1"], r["e2"], r["e3"], r["status"], r["thread"]))
        elif r["type"]=="org":
            pre.append(r["domains"][0])
        elif r["type"]=="correction":
            out.append(r["raw"])
    out.append("\n## Ledger A — pre-machine cohort\n")
    out.append(" · ".join("`%s`" % d for d in pre) + " · **+20 more — the full address list remains in `CCRR-Suppression-Already-Contacted.md` §A and is authoritative for the addresses.**")
    out.append("\n# LEDGER B — PEOPLE\n\n## 🔴 BOUNCED\n")
    out += ["| Address | Person | Org | Sent | Bounce |","|---|---|---|---|---|"]
    for r in recs:
        if r["type"]=="address" and r["outcome"]=="bounced":
            out.append("| `%s` | %s | %s | %s | %s |" % (r["address"], r["person"], r["org"], r["sent"], r["note"]))
    out.append("\n## ✅ DELIVERED — every other address, by organisation\n")
    out += ["| Org | Addresses | Stage |","|---|---|---|"]
    from collections import OrderedDict
    groups = OrderedDict()
    for r in recs:
        if r["type"]=="address" and r["outcome"]=="delivered":
            groups.setdefault((r["org_label"], r["stage"]), []).append(("🟢 " if r.get("replied") else "") + r["address"])
    for (org, stage), addrs in groups.items():
        out.append("| %s | %s | %s |" % (org, " · ".join(addrs), stage))
    out.append("\n---\n")
    return "\n".join(out) + "\n"

def cross_check(recs):
    """Recompute bounce_rate.py's scored numbers FROM THE JSONL and diff against its artifact."""
    today = datetime.date.today().isoformat()
    art_p = ROOT / "runs" / today / "bounce_rate.json"
    src_m = max((ROOT / "contacted.md").stat().st_mtime, (ROOT / "config.json").stat().st_mtime)
    if not art_p.exists() or art_p.stat().st_mtime < src_m:
        # RP-029 (2026-10-10): derived artifact older than its inputs -> regenerate before reading
        import subprocess
        subprocess.run([sys.executable, str(HERE / "bounce_rate.py")], capture_output=True)
        if not art_p.exists():
            return ["bounce_rate.json missing for today - bin/bounce_rate.py did not write it"]
    art = json.loads(art_p.read_text())
    dates = {}
    for r in recs:
        if r["type"]=="org" and r.get("e1") and re.match(r"^\d\d-\d\d$", r.get("e1","")):
            for d in r["domains"]: dates[d] = r["e1"]
    for alias, canon in CFG.get("domain_aliases",{}).items():
        if canon in dates: dates.setdefault(alias, dates[canon])
    never = {a.lower() for a in CFG["never_recipients"]}
    catch_all = set(CFG["catch_all_domains"])
    cut = CFG["bounce_rate_baseline"][5:]
    den = ca = 0
    for r in recs:
        if r["type"]=="address" and r["outcome"]=="delivered" and r["address"] not in never:
            dt = dates.get(r["domain"])
            if dt and dt >= cut:
                den += 1
                if r["domain"] in catch_all: ca += 1
    b = sum(1 for meta in CFG["hard_bounces"].values() if meta["sent"][5:] >= cut)
    mine = {"hard_bounces": b, "attempted_raw": den + b, "denominator_non_catch_all": den + b - ca}
    theirs = {k: art["scored_window"][k] for k in mine}
    return [] if mine == theirs else ["jsonl recompute %s != bounce_rate.py %s" % (mine, theirs)]

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "verify"
    text = (ROOT / "contacted.md").read_text(encoding="utf-8")
    recs = parse_md(text)
    if cmd in ("migrate", "verify"):
        with open(ROOT / "contacted.jsonl", "w", encoding="utf-8") as f:
            for r in recs: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    if cmd in ("render", "verify"):
        (ROOT / "contacted.generated.md").write_text(render(recs), encoding="utf-8")
    if cmd == "verify":
        back = parse_md((ROOT / "contacted.generated.md").read_text(encoding="utf-8"))
        orig_k = {key(r) for r in recs if r["type"] in ("org","address")}
        back_k = {key(r) for r in back if r["type"] in ("org","address")}
        problems = []
        if orig_k - back_k: problems.append("DROPPED in round-trip: %s" % sorted(orig_k - back_k)[:10])
        if back_k - orig_k: problems.append("INVENTED in round-trip: %s" % sorted(back_k - orig_k)[:10])
        problems += cross_check(recs)
        n_org = sum(1 for r in recs if r["type"]=="org"); n_addr = sum(1 for r in recs if r["type"]=="address")
        if problems:
            print("Ledger dual-write: 🔴 FAILED — " + " · ".join(problems)); return 1
        print(f"Ledger dual-write: clean — {n_org} org records · {n_addr} address records · round-trip exact · bounce cross-check exact")
        return 0
    return 0

if __name__ == "__main__":
    sys.exit(main())
