#!/usr/bin/env python3
"""run_integrity.py — did the run actually DELIVER what it claims?

Installed 2026-09-01 per CAPA-2026-09-01-missing-dossier.

Every other script in bin/ measures the QUALITY of the work. None of them measured whether the
thing Chris opens was produced. On 2026-08-31 that gap let three separate artifacts fail in three
different ways on the same night, and every metric came back green:

  1. EXISTENCE   the dossier was never written           -> nothing checked it existed
  2. EXECUTION   runs/<date>/sent_sweep.json was never   -> ledger_reconcile.py is listed LIVE in
                 written on any run                         method §0.10 and has NEVER ONCE RUN
  3. AGREEMENT   runs/2026-08-31/drafts.json was written -> the As-sent delta was computed from
                 correctly and never read back              memory and printed M=0 when M=2

This script answers all three with COUNTABLE OBJECTS rather than judgement, which is the same
discipline as P9's idempotency grep and dedup_check.py's set intersection.

  4. WRITER      (BQ-023, 2026-10-04) which path wrote each draft - Zapier or the native connector -
                 and whether every Zapier draft was READ BACK clean (§0.4 Z1-Z4), the Email 3 kit
                 verified attached, and every permission-classifier denial counted. Before this, the
                 `Draft writer:` and `Classifier:` lines (§0.6) were totalled by hand.

  Reads  : config.json (expected_outputs, draft_writer)  ·  runs/<date>/*  ·  runs/<prev>/drafts.json
           runs/<date>/classifier.json (the run writes it; [] when no denials)
  Writes : runs/<date>/integrity.json  +  the `Integrity:`, `Draft writer:` and `Classifier:` report lines
  Exit   : 0 clean · 1 a BINDING check failed · 2 a SHADOW check failed (report, do not block)

BINDING vs SHADOW follows the house precedent in method §0.10 — a new gate earns its teeth over
three runs. `binding: true` entries in config.expected_outputs fail the run today; everything
else reports and is scored toward its own 3-run clock.
"""
import json, sys, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
TODAY = datetime.date.today().isoformat()


def load(p, default=None):
    try:
        return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
    except Exception:
        return default


def prev_run_dir(runs, today):
    dirs = sorted(d.name for d in runs.iterdir() if d.is_dir() and d.name < today)
    return runs / dirs[-1] if dirs else None


def norm(addrs):
    return sorted(a.strip().lower() for a in (addrs or []))


def check_existence(cfg, run_dir):
    """1. Did every declared output get written, and is it dated today?"""
    out, missing_binding, missing_shadow = [], [], []
    for spec in cfg.get("expected_outputs", []):
        name = spec["path"].replace("<date>", TODAY)
        path = ROOT / name
        cond = spec.get("required", "always")
        if cond == "if_drafts" and not (run_dir / "drafts.json").exists():
            out.append({"path": name, "verdict": "n/a", "why": "no drafts this run"})
            continue
        if not path.exists():
            (missing_binding if spec.get("binding") else missing_shadow).append(name)
            out.append({"path": name, "verdict": "MISSING",
                        "binding": bool(spec.get("binding")), "why": spec.get("why", "")})
            continue
        # freshness: a file from a previous run sitting at the expected path is worse than absence,
        # because it reads as success. Date-stamped paths are self-proving; others get an mtime test.
        fresh = True
        if "<date>" not in spec["path"]:
            mt = datetime.date.fromtimestamp(path.stat().st_mtime).isoformat()
            fresh = (mt == TODAY)
        if not fresh:
            (missing_binding if spec.get("binding") else missing_shadow).append(name + " (STALE)")
            out.append({"path": name, "verdict": "STALE",
                        "binding": bool(spec.get("binding")), "why": "exists but not written today"})
        else:
            out.append({"path": name, "verdict": "ok", "bytes": path.stat().st_size})
    return out, missing_binding, missing_shadow


def check_agreement(run_dir):
    """2. Does drafts.json match what is ACTUALLY sitting in the Drafts folder?

    drafts.json is what the run BELIEVES it created. drafts_observed.json is a read-back of the
    mailbox. §0.11 already established the principle for one draft's hrefs — this applies it to the
    whole batch's recipients, which is where a wrong set is expensive.
    """
    declared = load(run_dir / "drafts.json")
    observed = load(run_dir / "drafts_observed.json")
    if declared is None:
        return {"status": "n/a", "why": "no drafts.json — no drafts created this run"}
    if observed is None:
        return {"status": "NO READ-BACK",
                "why": "drafts_observed.json absent — the run never read its own drafts back"}
    # 🔴 the To is the join key, so it MUST be normalised — Gmail lower-cases the domain on
    # write (person0955@org0687.example came back person0955@org0687.example) and a raw key reads
    # that as a divergence. Found by this script's own first run, 2026-09-01.
    dmap = {norm(d.get("to"))[0]: d for d in declared if d.get("to")}
    omap = {norm(o.get("to"))[0]: o for o in observed if o.get("to")}
    diffs = []
    for to in sorted(set(dmap) | set(omap)):
        d, o = dmap.get(to), omap.get(to)
        if d is None:
            diffs.append({"to": to, "kind": "IN MAILBOX, NOT DECLARED",
                          "observed_cc": norm(o.get("cc"))})
        elif o is None:
            diffs.append({"to": to, "kind": "DECLARED, NOT IN MAILBOX",
                          "org": d.get("org"), "declared_cc": norm(d.get("cc"))})
        elif norm(d.get("cc")) != norm(o.get("cc")):
            diffs.append({"to": to, "kind": "CC MISMATCH", "org": d.get("org"),
                          "declared_cc": norm(d.get("cc")), "observed_cc": norm(o.get("cc"))})
    return {"status": "clean" if not diffs else "DIVERGENT",
            "declared": len(declared), "observed": len(observed), "diffs": diffs}


def check_as_sent(runs, run_dir):
    """3. The As-sent delta, COMPUTED — never recalled.

    §0.6's `As-sent delta:` line has always had an M slot for Chris's recipient changes. Until now
    nothing computed it, and on 2026-09-01 the run printed M=0 when M=2 because it read the sent
    mail on its own instead of diffing it against the drafts artifact already on disk.
    """
    sweep = load(run_dir / "sent_sweep.json")
    if sweep is None:
        return {"status": "NO INPUT",
                "why": "runs/%s/sent_sweep.json absent — write the unfiltered 3-day sent sweep at "
                       "GATHER (method §0.3 step 5). ledger_reconcile.py needs the same file and has "
                       "never once run without it." % TODAY}
    prev = prev_run_dir(runs, TODAY)
    declared = load(prev / "drafts.json") if prev else None
    if declared is None:
        return {"status": "no prior batch", "sent_threads": len(sweep)}
    dmap = {}
    for d in declared:
        for a in (d.get("to") or []):
            dmap[a.strip().lower()] = d
    changes, matched = [], 0
    for s in sweep:
        sto = norm(s.get("to"))
        d = next((dmap[a] for a in sto if a in dmap), None)
        if d is None:
            # To was swapped by Chris — find the draft by any surviving Cc address
            scc = set(norm(s.get("cc")))
            d = next((x for x in declared
                      if scc & set(norm(x.get("cc")) + norm(x.get("to")))), None)
            if d is None:
                continue
        matched += 1
        dto, dcc = norm(d.get("to")), norm(d.get("cc"))
        scc = norm(s.get("cc"))
        ch = {}
        if dto != sto:
            ch["to"] = {"drafted": dto, "sent": sto}
        added = [a for a in scc if a not in dcc and a not in dto]
        removed = [a for a in dcc if a not in scc and a not in sto]
        if added:
            ch["cc_added_by_chris"] = added
        if removed:
            ch["cc_removed_by_chris"] = removed
        if ch:
            ch.update({"org": d.get("org"), "email_no": d.get("email_no"),
                       "recipient_count_as_sent": len(sto) + len(scc)})
            changes.append(ch)
    return {"status": "computed", "prior_batch": prev.name if prev else None,
            "sent_threads": len(sweep), "matched_to_a_draft": matched,
            "M": len(changes), "changes": changes}


def check_draft_writer(cfg, run_dir):
    """4. Which path wrote each draft, and was every Zapier draft proven? (BQ-023, 2026-10-04)

    config.draft_writer (installed 2026-10-03) says Email 2 and 3 are created through Zapier's Gmail
    actions and Email 1 natively. The run records, per row of drafts.json, `writer`, an optional
    `writer_fallback_reason`, `attachment_verified` (Email 3) and `zapier_readback` (= §0.4 Z1-Z4).
    This function only COUNTS those recorded objects into the two §0.6 lines. A row that lacks the
    fields is UNEXAMINED - printed as such, never scored as clean (the CI-040 / U2b rule).

    SHADOW: nothing here can fail the run (exit 2 at most) until it has earned its teeth over
    three clean runs, per the §0.10 graduated gate.
    """
    dw = cfg.get("draft_writer")
    if not dw:
        return {"status": "n/a", "why": "config.draft_writer absent (pre-cutover config)",
                "line_writer": None, "line_classifier": None, "findings": [], "shadow_fail": False}
    declared = load(run_dir / "drafts.json")
    observed = load(run_dir / "drafts_observed.json") or []
    # observed rows MAY carry wrapped_hrefs (method step 15, 2026-10-04); when they do, the mailbox
    # count beats the run's own claim - verify against Gmail, never against the run's memory.
    obs_wrapped = {o.get("thread"): o.get("wrapped_hrefs") for o in observed
                   if o.get("thread") and o.get("wrapped_hrefs") is not None}
    findings, unexamined = [], []
    zap = {1: 0, 2: 0, 3: 0}; fallback = []; native_cfg = 0
    att_total = att_ok = 0; wrapped = 0; compose_only = []
    if declared is None:
        line_writer = "Draft writer: no drafts this run"
    else:
        for d in declared:
            n = d.get("email_no"); org = d.get("org") or "?"
            exp = dw.get("email_%s" % n)
            w = d.get("writer")
            if w is None:
                unexamined.append("%s (E%s): no writer field" % (org, n)); continue
            if w == "zapier":
                zap[n] = zap.get(n, 0) + 1
                rb = d.get("zapier_readback")
                if rb is None:
                    unexamined.append("%s (E%s): Zapier draft never read back" % (org, n))
                else:
                    wr = obs_wrapped.get(d.get("thread"), rb.get("wrapped_hrefs"))
                    wr = 0 if wr is None else int(wr)
                    wrapped += wr
                    for k, label in (("thread_ok", "Z1 thread"), ("label_ok", "Z3 label"),
                                     ("one_draft_on_thread", "Z4 one draft")):
                        if not rb.get(k):
                            findings.append("%s (E%s): %s FALSE" % (org, n, label))
                    if wr:
                        findings.append("%s (E%s): Z2 - %d wrapped href(s) on a Zapier draft" % (org, n, wr))
                    # Z5 (2026-10-04): the draft's parent must be a VISIBLE message. Zapier replies to the
                    # newest message on the thread, trashed drafts included, and Gmail hides a draft whose
                    # parent is a trashed draft - it opens only from its compose link. Counted, never hidden.
                    if rb.get("parent_visible") is False:
                        compose_only.append("%s (E%s)" % (org, n))
                if n in (1, 3):   # Email 1 flyer (from 2026-10-04) and Email 3 kit are attached by Zapier
                    att_total += 1
                    av = d.get("attachment_verified")
                    if av is True:
                        att_ok += 1
                    elif av is None:
                        unexamined.append("%s (E%s): attachment never verified" % (org, n))
                    else:
                        findings.append("%s (E%s): Zapier draft WITHOUT verified attachment" % (org, n))
            if w != exp:
                why = d.get("writer_fallback_reason")
                fallback.append("%s (E%s) — %s" % (org, n, why or "NO REASON RECORDED"))
                if not why:
                    findings.append("%s (E%s): writer %s but config says %s, no fallback reason" % (org, n, w, exp))
            elif w == "native":
                native_cfg += 1
        line_writer = ("Draft writer: zapier %d (Email 1 %d · Email 2 %d · Email 3 %d) · native fallback %d%s · "
                       "attachments verified %d of %d · hrefs wrapped on Zapier drafts: %d · "
                       "compose-link-only %d%s · native as configured %d"
                       % (sum(zap.values()), zap.get(1, 0), zap.get(2, 0), zap.get(3, 0), len(fallback),
                          (" [" + "; ".join(fallback) + "]") if fallback else "",
                          att_ok, att_total, wrapped, len(compose_only),
                          (" [" + "; ".join(compose_only) + "]") if compose_only else "", native_cfg))
        if unexamined:
            line_writer += " · ⚪ UNEXAMINED %d (NOT a pass)" % len(unexamined)
    # --- classifier denials: a COUNT, never an anecdote (CAPA-2026-09-30 C5) ---
    cl = load(run_dir / "classifier.json")
    if cl is None:
        line_classifier = ("Classifier: NOT RECORDED — runs/%s/classifier.json absent; write it ([] when no "
                           "denials). Absence is a finding, not zero" % TODAY)
        cl_status = "NOT RECORDED"
    elif not isinstance(cl, list):
        line_classifier = "Classifier: MALFORMED — classifier.json must be a list"; cl_status = "MALFORMED"
    else:
        items = ["%s → %s" % (c.get("tool", "?"), c.get("target", "?")) for c in cl]
        line_classifier = "Classifier: %d writes denied%s" % (len(cl), (" [" + "; ".join(items) + "]") if cl else " [none]")
        cl_status = "recorded"
    shadow_fail = bool(findings or unexamined or fallback or compose_only) or cl_status != "recorded"
    return {"status": "computed", "zapier": zap, "fallback": fallback, "native_as_configured": native_cfg,
            "attachments": {"verified": att_ok, "of": att_total}, "wrapped_hrefs_on_zapier": wrapped,
            "compose_link_only": compose_only,
            "unexamined": unexamined, "findings": findings,
            "classifier": {"status": cl_status, "denials": cl if isinstance(cl, list) else None},
            "line_writer": line_writer, "line_classifier": line_classifier, "shadow_fail": shadow_fail}


def main():
    cfg = load(ROOT / "config.json", {})
    runs = ROOT / "runs"
    run_dir = runs / TODAY
    run_dir.mkdir(parents=True, exist_ok=True)

    existence, miss_bind, miss_shadow = check_existence(cfg, run_dir)
    agreement = check_agreement(run_dir)
    as_sent = check_as_sent(runs, run_dir)
    writer = check_draft_writer(cfg, run_dir)

    ok_ct = sum(1 for e in existence if e["verdict"] == "ok")
    tot = sum(1 for e in existence if e["verdict"] != "n/a")

    bits = ["outputs %d/%d present" % (ok_ct, tot)]
    bits.append("BINDING MISSING: " + ", ".join(miss_bind) if miss_bind else "binding outputs ok")
    if miss_shadow:
        bits.append("shadow missing: " + ", ".join(miss_shadow))
    bits.append("drafts read-back: " + agreement["status"] +
                ("" if not agreement.get("diffs") else " (%d)" % len(agreement["diffs"])))
    bits.append("as-sent delta: " + (("M = %d" % as_sent["M"]) if as_sent.get("status") == "computed"
                                     else as_sent["status"]))
    line = "Integrity: " + " · ".join(bits)

    result = {"date": TODAY, "line": line, "existence": existence,
              "agreement": agreement, "as_sent": as_sent, "draft_writer": writer,
              "binding_failures": miss_bind, "shadow_failures": miss_shadow}
    (run_dir / "integrity.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(line)
    if writer.get("line_writer"):
        print(writer["line_writer"])
        print(writer["line_classifier"])
        for f in writer.get("findings", []):
            print("  🔴 writer: %s" % f)
        for u in writer.get("unexamined", []):
            print("  ⚪ writer UNEXAMINED: %s" % u)
    for e in existence:
        if e["verdict"] in ("MISSING", "STALE"):
            print("  %s %s — %s%s" % ("🔴" if e.get("binding") else "⚠️ ",
                                      e["verdict"], e["path"],
                                      (" — " + e["why"]) if e.get("why") else ""))
    for d in agreement.get("diffs", []):
        print("  ⚠️  %s — %s" % (d["kind"], d.get("org") or d.get("to")))
    for c in as_sent.get("changes", []):
        parts = []
        if "to" in c:
            parts.append("To %s → %s" % (c["to"]["drafted"][0], c["to"]["sent"][0]))
        if "cc_added_by_chris" in c:
            parts.append("+%d Cc" % len(c["cc_added_by_chris"]))
        if "cc_removed_by_chris" in c:
            parts.append("-%d Cc" % len(c["cc_removed_by_chris"]))
        print("  ✏️  %s (E%s): %s → %d recipients as sent"
              % (c["org"], c["email_no"], ", ".join(parts), c["recipient_count_as_sent"]))

    if miss_bind:
        sys.exit(1)
    if miss_shadow or agreement.get("diffs") or agreement["status"] == "NO READ-BACK" \
            or as_sent.get("status") in ("NO INPUT",) or writer.get("shadow_fail"):
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
