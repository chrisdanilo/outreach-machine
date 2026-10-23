#!/usr/bin/env python3
"""learn_diff.py - FULL-BODY sent-vs-template diff (Phase 5 learn pass). LIVE (read-only).
Usage: learn_diff.py sent_body.txt template_body.txt [--skip-greeting]
Log copy changes, change nothing - Chris directs template changes."""
import sys, difflib
a, b = open(sys.argv[1]).read().splitlines(), open(sys.argv[2]).read().splitlines()
if "--skip-greeting" in sys.argv: a, b = a[1:], b[1:]
d = list(difflib.unified_diff(b, a, "template", "as-sent", lineterm=""))
print("Copy: byte-identical to template ✅" if not d else "Copy: 🔴 DIVERGENCE — log, never apply:\n" + "\n".join(d[:40]))
sys.exit(0 if not d else 1)
