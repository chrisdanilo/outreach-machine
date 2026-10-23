#!/usr/bin/env python3
"""dossier_check.py — does the produced dossier match the pinned template?

Installed 2026-09-03 on Chris's instruction: "Why does the structure of the dossier keep changing?
Build an outline template for the dossier that each scheduled task run will just fill in."

🔴 THE DEFECT THIS EXISTS TO END.
method §0.6a pins the dossier's section order IN PROSE. Prose has to be read and re-derived by
whatever is running, every night. It drifted on 2026-09-02, Chris complained, §0.6a was written to
stop it — and it drifted again on 2026-09-03, because a paragraph describing a heading list is not
a heading list. dossier-template.md is now the shape; this script is the check.

Same discipline as P9's idempotency grep and dedup_check.py's set intersection: A COUNTABLE OBJECT
BEATS A JUDGEMENT. The run cannot "mostly" satisfy a heading list.

  Reads  : dossier-template.md (the REQUIRED HEADINGS fenced block) · dossier-<date>.md
  Writes : the `Dossier shape:` report line · runs/<date>/dossier_check.json
  Exit   : 0 clean · 1 a required heading is MISSING or OUT OF ORDER · 2 shadow-only warnings

BINDING vs SHADOW follows the house precedent in method §0.10 — a new gate earns its teeth over
three runs. Until Chris ratifies, this runs SHADOW: it reports and does not fail the run.
"""
import json, re, sys, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
TODAY = datetime.date.today().isoformat()
SHADOW = True  # flip to False once ratified — see method §0.10's graduated-gate precedent

# Tokens the template uses for the parts that legitimately vary run to run.
TOKEN = re.compile(r"\{\{.*?\}\}")


def normalise(h):
    """A heading matches if its FIXED text matches. {{tokens}} are wildcards, case-insensitive,
    whitespace-collapsed. '# 1 · NEW ORGANISATIONS — Email 1 × 15' matches the template's
    '# 1 · NEW ORGANISATIONS — Email 1 × {{N_E1}}'."""
    h = TOKEN.sub("\x00", h.strip())
    h = re.sub(r"\s+", " ", h)
    return h.lower()


def to_regex(tmpl_heading):
    parts = [re.escape(p) for p in normalise(tmpl_heading).split("\x00")]
    return re.compile("^" + ".*?".join(parts) + "$")


def required_headings(template_path):
    """Parse the REQUIRED HEADINGS fenced block. The template is the single source of the shape —
    this script hard-codes nothing."""
    txt = template_path.read_text(encoding="utf-8")
    m = re.search(r"## REQUIRED HEADINGS.*?\n```\n(.*?)\n```", txt, re.S)
    if not m:
        return None
    out = []
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line:
            continue
        lm = re.match(r"^(H[1-6])\s+(#{1,6}\s+.*)$", line)
        if lm:
            out.append({"level": int(lm.group(1)[1]), "text": lm.group(2)})
    return out


def actual_headings(doc_path):
    out = []
    fence = False
    for i, line in enumerate(doc_path.read_text(encoding="utf-8").splitlines(), 1):
        if line.lstrip().startswith("```"):
            fence = not fence            # never read a heading out of a fenced block
            continue
        if fence:
            continue
        if re.match(r"^#{1,6}\s+\S", line):
            out.append({"line": i, "text": line.rstrip()})
    return out


def main():
    date = sys.argv[1] if len(sys.argv) > 1 else TODAY
    tmpl = ROOT / "dossier-template.md"
    doc = ROOT / f"dossier-{date}.md"

    if not tmpl.exists():
        print(f"Dossier shape: SKIPPED — dossier-template.md not found. The template IS the spec; "
              f"without it there is nothing to check against."); return 2
    if not doc.exists():
        print(f"Dossier shape: 🔴 NO DOSSIER — dossier-{date}.md does not exist. "
              f"run_integrity.py owns that failure; this check has nothing to inspect."); return 2

    req = required_headings(tmpl)
    if req is None:
        print("Dossier shape: SKIPPED — no 'REQUIRED HEADINGS' fenced block in dossier-template.md")
        return 2

    act = actual_headings(doc)
    act_norm = [normalise(a["text"]) for a in act]

    missing, out_of_order, found = [], [], []
    cursor = -1
    for r in req:
        rx = to_regex(r["text"])
        hit = next((i for i, a in enumerate(act_norm) if rx.match(a)), None)
        if hit is None:
            missing.append(r["text"])
            continue
        found.append({"required": r["text"], "found_at_line": act[hit]["line"],
                      "as_written": act[hit]["text"]})
        if hit < cursor:
            out_of_order.append({"heading": r["text"], "expected_after_line": cursor,
                                 "found_at_line": act[hit]["line"]})
        cursor = max(cursor, hit)

    ok = not missing and not out_of_order
    verdict = "matches template ✅" if ok else (
        ("🔴 MISSING: " + " · ".join(missing) if missing else "") +
        ("  " if missing and out_of_order else "") +
        ("🔴 OUT OF ORDER: " + " · ".join(x["heading"] for x in out_of_order) if out_of_order else ""))

    mode = "SHADOW" if SHADOW else "BINDING"
    print(f"Dossier shape: {len(found)}/{len(req)} required headings present · {verdict} "
          f"[{mode}, per dossier-template.md]")
    for m_ in missing:
        print(f"  🔴 MISSING — {m_}")
    for o in out_of_order:
        print(f"  🔴 OUT OF ORDER — {o['heading']} (found line {o['found_at_line']}, "
              f"expected after line {o['expected_after_line']})")

    outdir = ROOT / "runs" / date
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "dossier_check.json").write_text(json.dumps({
        "script": "dossier_check.py", "version": "1.0.0", "mode": mode,
        "generated_at": datetime.datetime.now().astimezone().isoformat(),
        "run_date": date, "template": str(tmpl.name), "document": str(doc.name),
        "required": len(req), "present": len(found),
        "missing": missing, "out_of_order": out_of_order, "found": found,
        "status": "OK" if ok else "PROBLEM",
    }, indent=2), encoding="utf-8")

    if ok:
        return 0
    return 2 if SHADOW else 1


if __name__ == "__main__":
    sys.exit(main())
