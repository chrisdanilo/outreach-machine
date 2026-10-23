#!/usr/bin/env python3
"""build_queue.py — count BUILD-QUEUE.md, never recall it.

Prints the §0.6 `Build queue:` line and writes runs/<date>/build_queue.json.
Counts are rows in the OPEN and CLOSED tables of BUILD-QUEUE.md (one ticket per row, id BQ-NNN).
"""
import re, json, pathlib, datetime, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TODAY = datetime.date.today().isoformat()


def rows(section):
    txt = (ROOT / "BUILD-QUEUE.md").read_text(encoding="utf-8")
    m = re.search(r"^## %s\s*$(.*?)(?=^## |\Z)" % section, txt, re.S | re.M)
    body = m.group(1) if m else ""
    out = []
    for line in body.splitlines():
        mm = re.match(r"^\|\s*(BQ-\d{3})\s*\|(.*)$", line)
        if mm:
            cells = [c.strip() for c in mm.group(2).split("|")]
            out.append({"id": mm.group(1), "cells": cells})
    return out


def main():
    op, cl = rows("OPEN"), rows("CLOSED")
    chris = [r["id"] for r in op if len(r["cells"]) > 2 and "Chris" in r["cells"][2]]
    closed_recent = [r["id"] for r in cl if len(r["cells"]) > 1 and r["cells"][1] >= (datetime.date.today() - datetime.timedelta(days=7)).isoformat()]
    oldest = op[0]["id"] if op else "—"
    line = "Build queue: %d open (%d wait on Chris: %s) · %d closed in the last 7 days · oldest open: %s" % (
        len(op), len(chris), ", ".join(chris) if chris else "none", len(closed_recent), oldest)
    d = ROOT / "runs" / TODAY; d.mkdir(parents=True, exist_ok=True)
    (d / "build_queue.json").write_text(json.dumps({"script": "build_queue.py", "run_date": TODAY, "line": line,
        "open": [r["id"] for r in op], "waiting_on_chris": chris, "closed": [r["id"] for r in cl]}, indent=2))
    print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
