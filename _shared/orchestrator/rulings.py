#!/usr/bin/env python3
"""rulings.py — the ONE place a question for Chris is written, and the one place it is closed.

Why (2026-10-26, improvement #3): open decisions were scattered across BUILD-QUEUE tickets, config
`open_rulings`, STATE "decisions for Chris", dossier ⚑ flags and `machine_001_hold_carried` fields, so
nothing could tell whether a question had already been answered — which is how a ruled issue gets
re-raised. Now: a machine may only ask Chris something by appending an OPEN row here; the dossier's
decisions table is GENERATED from the open rows; a RULED row is never re-asked.

File: 0_Design-and-Purpose/decisions/rulings.jsonl — ONE log for every machine (2026-11-03); one JSON row per ruling:
  {"id": "M2-R003", "machine": "OM-2" | "OM-1" | "shared", "status": "open"|"ruled", "opened": "YYYY-MM-DD", "question": "...", "context": "...",
   "ruling": "...", "ruled_on": "YYYY-MM-DD", "by": "chris"|"claude-default", "applied_in": "config.json daily.skip_states"}

Usage (--machine OM-1 | OM-2 | shared; default shared):
  rulings.py open  --machine M --q "question" [--context "why it came up"] [--by claude]
  rulings.py rule  --machine M <id> --ruling "the ruling" [--by chris|claude-default] [--applied "where it now lives"]
  rulings.py list  --machine M [--all]            # open rows (or all)
  rulings.py table --machine M                     # markdown table of OPEN rows, for the dossier
  rulings.py seed  --machine M --from seed.json    # one-time import: a list of rows (open or ruled)
  rulings.py check --machine M --q "question"      # exit 0 + prints the id if this question already exists (open or ruled)

Guard against re-raising: `open` refuses a question that already exists (same normalised text, or the same
`key` if you pass --key), and prints the existing id and its ruling. Ruled rows are never re-opened; if the
world changed, open a NEW row that cites the old id in its context.
"""
import argparse, datetime, json, os, re, sys
import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_shared", "orchestrator")); import paths  # the one file that knows every folder (2026-11-03)

# 2026-11-03: ONE rulings log for every machine (0_Design-and-Purpose/decisions/rulings.jsonl); each row carries machine = OM-1 | OM-2 | shared.
# --machine is now that label (a folder path still works: its last name is mapped; "Automations" / "." = shared).
PREFIX = {"OM-1": "M1", "OM-2": "M2", "shared": "ENG", "Automations": "ENG", "outreach-machine": "M1", "outreach-machine-002-conference": "M2", "outreach-engine": "ENG"}
LABEL = {"OM-1": "OM-1", "OM-2": "OM-2", "M1": "OM-1", "M2": "OM-2", "outreach-machine": "OM-1", "outreach-machine-002-conference": "OM-2"}


def label(machine):
    base = os.path.basename(os.path.abspath(machine)) if ("/" in str(machine) or machine == ".") else str(machine)
    return LABEL.get(base, "shared")


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def path(machine=None):
    return paths.RULINGS


def load_all():
    rows = []
    if os.path.exists(paths.RULINGS):
        for l in open(paths.RULINGS, encoding="utf-8"):
            l = l.strip()
            if l:
                rows.append(json.loads(l))
    return rows


def load(machine):
    """This machine's rows (shared rows belong to every machine)."""
    m = label(machine)
    return [r for r in load_all() if r.get("machine") == m or r.get("machine") == "shared" or m == "shared"]


def save(machine, rows):
    """Write back: the given rows replace this machine's rows; other machines' rows are kept, in file order."""
    m = label(machine); mine = {r["id"]: r for r in rows}
    out = []
    for r in load_all():
        if r["id"] in mine: out.append(mine.pop(r["id"]))
        elif r.get("machine") == m and m != "shared": continue
        else: out.append(r)
    out.extend(mine.values())
    os.makedirs(os.path.dirname(paths.RULINGS), exist_ok=True)
    with open(paths.RULINGS, "w", encoding="utf-8") as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def prefix(machine):
    return PREFIX.get(label(machine), "MX")


def next_id(machine, rows):
    pre = prefix(machine)
    n = 0
    for r in rows:
        m = re.match(rf"^{pre}-R(\d+)$", r.get("id", ""))
        if m:
            n = max(n, int(m.group(1)))
    return f"{pre}-R{n+1:03d}"


def today():
    return datetime.date.today().isoformat()


def find(rows, q, key=None):
    nq = norm(q)
    for r in rows:
        if key and r.get("key") == key:
            return r
        if norm(r.get("question")) == nq:
            return r
    return None


def cmd_open(a):
    rows = load(a.machine)
    ex = find(rows, a.q, a.key)
    if ex:
        print(f"EXISTS {ex['id']} [{ex['status']}]: {ex['question']}")
        if ex.get("ruling"):
            print(f"  ruling ({ex.get('ruled_on')}, {ex.get('by')}): {ex['ruling']}")
        return 2
    r = {"id": next_id(a.machine, rows), "machine": label(a.machine), "status": "open", "opened": today(), "question": a.q.strip(),
         "context": (a.context or "").strip(), "ruling": "", "ruled_on": "", "by": "", "applied_in": ""}
    if a.key:
        r["key"] = a.key
    if a.by:
        r["opened_by"] = a.by
    rows.append(r)
    save(a.machine, rows)
    print(f"OPEN {r['id']}: {r['question']}")
    return 0


def cmd_rule(a):
    rows = load(a.machine)
    for r in rows:
        if r["id"] == a.id:
            if r["status"] == "ruled" and not a.force:
                print(f"ALREADY RULED {r['id']} on {r['ruled_on']} by {r['by']}: {r['ruling']}  (use --force to amend; prefer a new row)")
                return 2
            r.update({"status": "ruled", "ruling": a.ruling.strip(), "ruled_on": today(), "by": a.by or "chris",
                      "applied_in": (a.applied or r.get("applied_in") or "").strip()})
            save(a.machine, rows)
            print(f"RULED {r['id']} by {r['by']}: {r['ruling']}")
            return 0
    print(f"NO SUCH ID {a.id}")
    return 1


def cmd_list(a):
    rows = load(a.machine)
    for r in rows:
        if a.all or r["status"] == "open":
            tag = "OPEN " if r["status"] == "open" else "ruled"
            print(f"{r['id']}  {tag}  {r['opened']}  {r['question']}")
            if r["status"] == "ruled":
                print(f"      → {r['ruling']}  ({r['ruled_on']}, {r['by']}{'; in ' + r['applied_in'] if r.get('applied_in') else ''})")
    print(f"\n{sum(1 for r in rows if r['status']=='open')} open · {sum(1 for r in rows if r['status']=='ruled')} ruled")
    return 0


def table(machine):
    rows = [r for r in load(machine) if r["status"] == "open"]
    if not rows:
        return "No open decisions."
    L = ["| # | Question | Context | Until you rule, the machine does |", "|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['id']} | {r['question']} | {r.get('context','')} | {r.get('default','') or '—'} |")
    L.append("")
    L.append(f"Rule in chat: \"rule {rows[0]['id']}: …\" — Claude records it here and it is never asked again.")
    return "\n".join(L)


def cmd_table(a):
    print(table(a.machine))
    return 0


def cmd_seed(a):
    rows = load(a.machine)
    new = json.load(open(a.src, encoding="utf-8"))
    n = 0
    for s in new:
        if find(rows, s["question"], s.get("key")):
            continue
        r = {"id": next_id(a.machine, rows), "machine": label(a.machine), "status": s.get("status", "open"), "opened": s.get("opened") or today(),
             "question": s["question"].strip(), "context": s.get("context", ""), "ruling": s.get("ruling", ""),
             "ruled_on": s.get("ruled_on", "") or (today() if s.get("status") == "ruled" else ""),
             "by": s.get("by", "") , "applied_in": s.get("applied_in", "")}
        for k in ("key", "default", "source"):
            if s.get(k):
                r[k] = s[k]
        rows.append(r)
        n += 1
    save(a.machine, rows)
    print(f"seeded {n} rows → {path(a.machine)} ({len(rows)} total)")
    return 0


def cmd_check(a):
    ex = find(load(a.machine), a.q, a.key)
    if ex:
        print(f"{ex['id']} [{ex['status']}] {ex.get('ruling') or ''}")
        return 0
    print("NOT FOUND")
    return 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["open", "rule", "list", "table", "seed", "check"])
    ap.add_argument("id", nargs="?")
    ap.add_argument("--machine", default="shared")
    ap.add_argument("--q"); ap.add_argument("--context"); ap.add_argument("--key"); ap.add_argument("--by")
    ap.add_argument("--ruling"); ap.add_argument("--applied"); ap.add_argument("--force", action="store_true")
    ap.add_argument("--all", action="store_true"); ap.add_argument("--from", dest="src")
    a = ap.parse_args()
    if a.cmd in ("open", "check") and not a.q:
        ap.error("--q is required")
    if a.cmd == "rule" and not (a.id and a.ruling):
        ap.error("rule needs <id> and --ruling")
    if a.cmd == "seed" and not a.src:
        ap.error("seed needs --from")
    return {"open": cmd_open, "rule": cmd_rule, "list": cmd_list, "table": cmd_table, "seed": cmd_seed, "check": cmd_check}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
