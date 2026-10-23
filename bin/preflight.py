#!/usr/bin/env python3
"""preflight.py - the §0.4 assertions as code. 🔴 SHADOW MODE: prints verdicts beside the LLM's
own pre-flight for >=3 runs; its holds DO NOT BIND until 3 runs of agreement are recorded.
Input: runs/<date>/drafts.json - written by the run before Phase ACT:
 [{"org":..., "domain":..., "email_no":1|2|3, "to":[a], "cc":[a], "bcc":[a],
   "greeting_names":[...], "recipient_names":[...],
   "recipient_name_evidence":[...],   # CI-040 2026-08-29: each name AS IT APPEARS ON THE SOURCE
                                      # PAGE, transcribed in the same act that transcribes the
                                      # address for R6a. Absent => U2b is UNEXAMINED, never a pass.
   "recipients":[{"addr":a, "class":"V1|V2|V3", "evidence":"url-or-verdict", "date":"YYYY-MM-DD"}],
   "attested": {"U5_suppression_today":b, "U6_ledger_reconciled":b, "U8_template_verbatim":b,
                "U9_binding_read":b, "U10_sent_checked":b, "E16_employment_checked":b},
   # --- BQ-023, 2026-10-04: WHICH PATH WROTE THE DRAFT (config.draft_writer, Zapier cutover 2026-10-03) ---
   "writer": "zapier"|"native",          # the path that actually created this draft
   "writer_fallback_reason": "...",      # ONLY when writer differs from config.draft_writer.email_<n>
   "attachment_verified": true|false,    # Email 3 by Zapier: true ONLY after `list_drafts ... has:attachment
                                         # filename:pdf` returned THIS draft id (method step 12 ③). Absent on E1/E2
   "zapier_readback": {"thread_ok":b, "wrapped_hrefs":n, "label_ok":b, "one_draft_on_thread":b,
                       "parent_visible":b}   # = §0.4 Z1..Z5 as recorded objects, from the native read-back.
                                         # parent_visible (Z5, 2026-10-04): false when the thread's newest
                                         # message at creation was a live/trashed draft -> the draft opens only
                                         # from its compose link (config.draft_writer.zapier.reply_parent_rule).
                                         # Rows WITHOUT "writer" (nights before 2026-10-04) get no W verdicts,
                                         # so replay.py still reproduces them.
   }]
 Companion file: runs/<date>/classifier.json - every permission-classifier denial of a write,
 [] when none (read by run_integrity.py, not by this script).
Reads contacted.jsonl for U4/E1.1. Writes runs/<date>/preflight.json."""
import json, sys, datetime, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
today = datetime.date.today().isoformat()
p = ROOT/"runs"/today/"drafts.json"
if not p.exists(): print(f"NO INPUT: write runs/{today}/drafts.json before ACT, then rerun (shadow)"); sys.exit(3)
drafts = json.loads(p.read_text())
CFG = json.loads((ROOT/"config.json").read_text(encoding="utf-8"))
DW = CFG.get("draft_writer")   # None before the 2026-10-03 cutover -> no W verdicts at all
bounced, org_dom = set(), set()
for line in (ROOT/"contacted.jsonl").read_text().splitlines():
    r = json.loads(line)
    if r.get("type")=="address" and r["outcome"]=="bounced": bounced.add(r["address"])
    if r.get("type")=="org": org_dom.update(r.get("domains",[]))
results, holds = [], 0
for d in drafts:
    v = {}
    v["U1"] = len(d.get("to",[]))==1 and len(d.get("cc",[]))<=3  # cc ceiling RAISED 2->3 on 2026-08-28 (Chris). To is still exactly 1.
    # U2 - with the 2026-08-25 (D2) GENERIC-INBOX CARVE-OUT.
    # A V3 recipient (published address, NO name attached) carries no name, so it is greeted as
    # "and team". Named humans still require exact first-name parity. See method.md §0.4 U2.
    _cls = {r.get("addr","").lower(): r.get("class","") for r in d.get("recipients", [])}
    _all = [a.lower() for a in d.get("to", []) + d.get("cc", [])]
    _v3 = [a for a in _all if _cls.get(a) == "V3"]
    _greet = [g.lower() for g in d.get("greeting_names", [])]
    _team_tok = [g for g in _greet if g in ("team", "and team")]
    _named_greet = sorted(g for g in _greet if g not in ("team", "and team"))
    _named_recip = sorted(n.split()[0].lower() for n in d.get("recipient_names", []))
    v["U2"] = (_named_greet == _named_recip) and (len(_team_tok) == (1 if _v3 else 0))
    # U2b - NAME EVIDENCE ANCHOR (CI-040, 2026-08-29). U2 proves the greeting matches what the run
    # BELIEVES the names are. It cannot prove the run read the page correctly, because both sides of
    # U2 come from the run. R6a solved exactly this for addresses by anchoring to a quoted source
    # string; this is the same anchor one field over.
    _ev = d.get("recipient_name_evidence")
    if _ev is None:
        v["U2b"] = None          # UNEXAMINED, not clean - printed as a third state, never scored pass
    else:
        _names = d.get("recipient_names", [])
        v["U2b"] = (len(_ev) == len(_names)) and all(x == y for x, y in zip(_names, _ev))
    v["U4"] = not any(a.lower() in bounced for a in d.get("to",[])+d.get("cc",[]))
    v["U7"] = not d.get("bcc")
    for k, val in d.get("attested",{}).items(): v[k.split("_")[0]] = bool(val)
    if d.get("email_no")==1:
        v["E1.1"] = d.get("domain") not in org_dom
        v["E1.7"] = all(r.get("class") in ("V1","V2","V3") and r.get("evidence") for r in d.get("recipients",[]))
        # E1.7 V3 - AMENDED 2026-08-25 (Chris, D2). A V3 (published address, NO name attached) may take
        # the To ONLY when the org publishes NO named human anywhere, i.e. the draft has zero
        # recipient_names and the greeting uses the "Hi <Org> team," form. Where ANY named human
        # exists, that human takes the To and the V3 rides as a Cc under the "and team" greeting.
        _v3_in_to = any(r.get("class") == "V3" and r["addr"] in d.get("to", []) for r in d.get("recipients", []))
        _has_named_human = bool(d.get("recipient_names"))
        _team_greeting = "team" in [g.lower() for g in d.get("greeting_names", [])]
        v["V3-to-only-when-no-human"] = (not _v3_in_to) or ((not _has_named_human) and _team_greeting)
    # W - DRAFT WRITER (BQ-023, 2026-10-04). Evaluated ONLY when the row carries "writer" (schema from
    # 2026-10-04) AND config.draft_writer exists. Older recorded nights have neither, get no new keys,
    # and replay.py keeps MATCHing them. The question each W answers:
    #   W1  did the draft take the path config.draft_writer prescribes for its email number? A row on
    #       the other path is legitimate ONLY with a recorded writer_fallback_reason (method step 12).
    #   W2  (Email 3 by Zapier) does config name the kit file AND the sent message it is pulled from?
    #   W3  (any Zapier draft) was it read back, and did Z1..Z4 all hold? No read-back = UNEXAMINED.
    #   W4  (Email 3 by Zapier) did the has:attachment read-back return this draft? None = UNEXAMINED.
    if "writer" in d and DW:
        _n = d.get("email_no"); _exp = DW.get(f"email_{_n}")
        v["W1"] = (d.get("writer") == _exp) or bool(d.get("writer_fallback_reason"))
        if d.get("writer") == "zapier":
            _rb = d.get("zapier_readback")
            if _rb is None:
                v["W3"] = None
            else:
                v["W3"] = (_rb.get("wrapped_hrefs") == 0 and bool(_rb.get("thread_ok"))
                           and bool(_rb.get("label_ok")) and bool(_rb.get("one_draft_on_thread"))
                           and _rb.get("parent_visible") is not False)   # Z5 (2026-10-04): absent = not checked, False = hidden draft
            if _n in (1, 3):   # Email 1 = flyer (2026-10-04), Email 3 = starter kit; Email 2 carries nothing
                _att = (DW.get("zapier") or {}).get("email_%s_attachment" % _n) or {}
                v["W2"] = bool(_att.get("filename")) and bool(_att.get("source_message_id"))
                _av = d.get("attachment_verified")
                v["W4"] = None if _av is None else bool(_av)
    bad = [k for k, ok in v.items() if ok is False]
    unex = [k for k, ok in v.items() if ok is None]
    holds += bool(bad)
    results.append({"org":d.get("org"),"verdicts":v,"holds":bad,"unexamined":unex})
    # 🔴 A card carrying an UNEXAMINED verdict must never also read "all pass" — that is the exact
    # false-clean this assertion exists to prevent (CI-040, barrier 2026-09-02).
    _card = "🔴 SHADOW-HOLD " + ",".join(bad) if bad else ("all pass ✅" if not unex else "no holds")
    if unex: _card += "  ⚪ UNEXAMINED " + ",".join(unex) + " (NOT a pass)"
    print(f"  {d.get('org')}: " + _card)
out = ROOT/"runs"/today; out.mkdir(parents=True, exist_ok=True)
(out/"preflight.json").write_text(json.dumps({"mode":"SHADOW","drafts":len(drafts),"holds":holds,"results":results}, indent=2))
print(f"Pre-flight (script, SHADOW): {len(drafts)} drafts · {holds} shadow-holds — compare with your own §0.4 pass; disagreements are findings")
