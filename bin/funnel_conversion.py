#!/usr/bin/env python3
"""
funnel_conversion.py — the ONLY place the outreach conversion arithmetic lives.

Reads   : TLP/dashboard-data.json  (THE counted record -- every outcome figure, via counted_record.py)
          contacted.jsonl          (machine-written org + address ledger -- SENDS ONLY)
          funnel-outcomes.json     (which counted outcomes are cold outreach, and which email produced each reply)
Writes  : funnel-conversion.json   (machine-readable result, timestamped)
          funnel-conversion.md     (the same result as markdown; the dashboard reads the .json)

Rules this script exists to enforce (see TLP/TLP-Rules.md):
  - A send is never an Approach. Both are counted in ORGANISATIONS (Chris, 2026-09-02).
  - 🔴 ONE SOURCE PER QUANTITY. Outcomes come from the counted record and are never re-derived here.
    Until 2026-09-07 this script counted replies out of contacted.jsonl's status markers, which made
    the page show Approaches twice — 25 at the top from the counted record, 14 in the funnel from the
    ledger — and the ledger lagged, so the published reply RATE fell while outreach was improving.
    The ledger owns sends. It does not own outcomes.
  - Only cold-outreach outcomes enter the funnel. ASU and Morgan County are counted but not campaign,
    and the scope line names every counted outcome the funnel leaves out.
  - Apollo Mailwarming is excluded upstream (it never reaches contacted.jsonl) — asserted, not assumed.
  - Rates print an em dash, never 0, when a denominator is under MIN_DENOMINATOR.
  - Nothing here is ever posted to the TLBS site.

Usage: python3 bin/funnel_conversion.py [--check]
       --check exits non-zero if attribution is incomplete (for the nightly run manifest).
"""
import json, re, sys, datetime, pathlib
import counted_record as CR

ROOT   = pathlib.Path(__file__).resolve().parent.parent
LEDGER = ROOT / "contacted.jsonl"
OUTCOM = ROOT / "funnel-outcomes.json"
OUTJSON= ROOT / "funnel-conversion.json"
OUTMD  = ROOT / "funnel-conversion.md"

MIN_DENOMINATOR = 20          # below this a rate is not reported
LEDGER_FLOOR    = "2026-08-11"
DATE            = re.compile(r"\b(\d{2}-\d{2})\b")

# outcome buckets, in report order
BUCKETS = [("meeting",   "advanced to a meeting"),
           ("declined",  "declined outright"),
           ("deferred",  "keep-on-file or deferred"),
           ("forwarded", "forwarded on, no commitment"),
           ("live",      "still live, no meeting yet")]


def sent_date(v):
    """A stage date, or None when the cell records a draft / due / cancelled send."""
    if not v:
        return None
    v = str(v)
    if any(k in v.lower() for k in ("due", "drafted", "cancel")):
        return None
    m = DATE.search(v)
    return m.group(1) if m else None


def pct(n, d):
    """Rate against the SEND base. Floored — a rate off a handful of sends misleads."""
    return None if (not d or d < MIN_DENOMINATOR) else round(100.0 * n / d, 1)


def step(n, d):
    """Step conversion. Never floored, but never bare either — the denominator rides along,
    because 100% of 2 and 100% of 200 are not the same claim."""
    return None if not d else round(100.0 * n / d, 1)


def fmt(p):
    if p is None:
        return "—"
    return f"{int(p)}%" if float(p).is_integer() else f"{p}%"


def load():
    orgs, addrs = [], []
    dedup_closed = [0]
    for line in LEDGER.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        if r.get("type") == "org" and r.get("org"):
            orgs.append(r)
        elif r.get("type") == "org":
            dedup_closed[0] += 1          # org: None — closed at de-duplication, never emailed
        elif r.get("type") == "address":
            addrs.append(r)
    outcomes = json.loads(OUTCOM.read_text()) if OUTCOM.exists() else {}
    return orgs, addrs, outcomes, dedup_closed[0]


def compute():
    orgs, addrs, oc, dedup_closed = load()
    attrib = {k.lower(): v for k, v in oc.get("replies", {}).items()}
    through, counted_rows = CR.read()          # THE outcome figures. Never re-derived below.

    contacted, draft_waiting = [], 0
    for r in orgs:
        # A row that replied is not a draft, whatever its status says. [Org 0698] read
        # "DRAFT WAITING -- not yet sent" on 2026-09-07 having been sent on 1 Sep and
        # replied the same day; counting it as an excluded draft while also counting it
        # as an Approach would contradict itself inside one paragraph. It still belongs
        # in `contacted` when it carries a send date -- only the draft tally is corrected.
        replier = r.get("org", "").replace("*", "").strip().lower() in attrib
        if "not yet sent" in str(r.get("status", "")).lower() and not replier:
            draft_waiting += 1
        elif sent_date(r.get("e1")):
            contacted.append(r)

    e1 = len(contacted)          # ledger-known first sends
    e2 = sum(1 for r in contacted if sent_date(r.get("e2")))
    e3 = sum(1 for r in contacted if sent_date(r.get("e3")))

    # ---- Approaches: the counted record's number, split campaign / not ----
    # The attribution file names the campaign organisations. The counted record says how many
    # Approaches exist in total. The funnel shows the campaign ones and NAMES the remainder,
    # so the two figures on the page reconcile in the open instead of disagreeing silently.
    counted_approaches = CR.value(counted_rows, "Approaches")
    campaign_orgs = sorted(attrib.keys())
    replied = [r for r in contacted if r["org"].replace("*", "").strip().lower() in attrib]

    # An attributed reply whose organisation never got a ledger row: it replied, so it is an
    # Approach, but the send record cannot place it in the sequence. Surface it, never drop it.
    in_ledger = {r["org"].replace("*", "").strip().lower() for r in contacted}
    replied_not_in_ledger = [k for k in campaign_orgs if k not in in_ledger]
    n_campaign = len(campaign_orgs)

    # An organisation that replied was certainly contacted, whatever the ledger says. Counting it
    # in the numerator but not the denominator mixes two populations and inflates every rate.
    # So the send base is: ledger sends UNION campaign repliers. It is a FLOOR -- there may be
    # other sends the ledger never recorded -- and the coverage note says so.
    n_contacted = len(contacted) + len(replied_not_in_ledger)
    unscoped = (counted_approaches - n_campaign) if counted_approaches is not None else None

    # ---- sequence position: every contacted org appears exactly once ----
    pos = {"e1": 0, "e2": 0, "e3_no_response": 0, "replied": n_campaign}
    for r in contacted:
        if r in replied:
            continue
        if sent_date(r.get("e3")):
            pos["e3_no_response"] += 1
        elif sent_date(r.get("e2")):
            pos["e2"] += 1
        else:
            pos["e1"] += 1

    # ---- outcome buckets, straight off the attribution file ----
    missing, stage_drop, bucket = [], {"E1": [], "E2": [], "E3": []}, {k: [] for k, _ in BUCKETS}
    for key in campaign_orgs:
        a = attrib[key]
        label = key.split(" ⚠")[0].title() if key.islower() else key
        bucket[a["outcome"]].append(label)
        if a["outcome"] in ("declined", "deferred"):
            stage_drop[a["reply_stage"]].append(label)

    # ---- scope reconciliation: counted = campaign + non-campaign, or the run fails ----
    nc = oc.get("non_campaign", {})
    scope, scope_bad = {}, []
    def recon(field, campaign_n, named):
        c = CR.value(counted_rows, field)
        scope[field] = {"counted": c, "campaign": campaign_n,
                        "non_campaign": [f"{x['org']} ({x['date']})" for x in named]}
        if c is not None and campaign_n + len(named) != c:
            scope_bad.append(f"{field}: counted {c} != campaign {campaign_n} + non-campaign {len(named)}")

    meetings  = oc.get("meetings", [])
    proposals = oc.get("proposals", [])
    sales     = oc.get("sales", [])
    sales_val = sum(s.get("value", 0) for s in sales)
    held = [m for m in meetings if m.get("state") == "held"]
    held_orgs = {m["org"].strip().lower() for m in held}
    prop_after_meeting = [x for x in proposals if x["org"].strip().lower() in held_orgs]
    prop_no_meeting    = [x for x in proposals if x["org"].strip().lower() not in held_orgs]
    met_no_proposal    = [m["org"] for m in held
                          if m["org"].strip().lower() not in {x["org"].strip().lower() for x in proposals}]
    recon("Approaches", n_campaign, nc.get("approaches", []))
    recon("Meetings",   len(held),  nc.get("meetings", []))
    recon("Proposals",  len(proposals), nc.get("proposals", []))

    sent_per_email = {"E1": n_contacted, "E2": e2, "E3": e3}   # same base as the funnel above
    return {
        "generated":  datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        "floor":      LEDGER_FLOOR,
        "orgs_contacted": n_contacted,
        "orgs_contacted_in_ledger": e1,
        "emails_sent":    {"e1": e1, "e2": e2, "e3": e3, "total": e1 + e2 + e3},
        "addresses":  {"delivered": sum(1 for a in addrs if a.get("outcome") == "delivered"),
                       "bounced":   sum(1 for a in addrs if a.get("outcome") == "bounced")},
        "excluded":   {"draft_waiting": draft_waiting, "closed_at_dedup": dedup_closed},
        "approaches": {"orgs": n_campaign, "people": oc.get("approach_people"),
                       "counted": counted_approaches, "unscoped": unscoped,
                       "not_in_send_ledger": replied_not_in_ledger},
        "meetings":   {"total": len(meetings),
                       "held":   sum(1 for m in meetings if m.get("state") == "held"),
                       "booked": sum(1 for m in meetings if m.get("state") == "booked"),
                       "items":  meetings},
        "proposals":  {"total": len(proposals), "items": proposals,
                       "after_meeting": len(prop_after_meeting),
                       "without_meeting": [x["org"] for x in prop_no_meeting],
                       "met_but_no_proposal": met_no_proposal},
        "sales":      {"total": len(sales), "value": sales_val, "items": sales},
        "scope": scope,
        "scope_errors": scope_bad,
        "sequence_position": pos,
        "buckets":    {k: bucket[k] for k, _ in BUCKETS},
        "drop_by_email": {k: {"orgs": v, "n": len(v), "sent": sent_per_email[k],
                              "pct": pct(len(v), sent_per_email[k])} for k, v in stage_drop.items()},
        "unattributed": missing,
        "counted_through": through,
    }


def render(d):
    a, m, p, s = d["approaches"], d["meetings"], d["proposals"], d["sales"]
    n   = d["orgs_contacted"]
    pos = d["sequence_position"]
    per = lambda x: fmt(pct(x, n))
    ratio = lambda x: f"1 in {round(n / x)}" if x else "—"
    bk = f", {m['booked']} booked" if m.get("booked") else ""

    L = []
    A = L.append
    A("<!-- BEGIN FUNNEL CONVERSION — GENERATED BY bin/funnel_conversion.py — DO NOT HAND-EDIT -->")
    A("")
    A("### Funnel conversion — NOT A TLBS FIELD, NEVER POSTED")
    A("")
    A(f"*CCR&R Outreach Machine · from {d['floor']} · generated {d['generated']}*")
    if d["unattributed"]:
        A("")
        A(f"> ⚠️ **{len(d['unattributed'])} replying organisation(s) not yet attributed** — "
          f"{', '.join(d['unattributed'])}. Drop-off figures below are incomplete until "
          "`funnel-outcomes.json` carries a reply stage and outcome for each.")
    A("")
    A("#### Chart 1 — the funnel")
    A("")
    A("| Stage | Count | % of contacted | Step conversion |")
    A("| --- | --- | --- | --- |")
    A(f"| **Organisations contacted** — first email sent | **{n}** | 100% | "
      f"{d['emails_sent']['total']} emails to {d['addresses']['delivered']} delivered addresses |")
    A(f"| **Approaches** — an organisation replied; engagement is the trigger, not a send | **{a['orgs']}** | "
      f"**{per(a['orgs'])}** | {per(a['orgs'])} reply |")
    A(f"| **Meetings** — commercial conversations **held**; a booked call is not one yet | **{m['held']}** | "
      f"**{per(m['held'])}** | {fmt(step(m['held'], a['orgs']))} — {m['held']} of {a['orgs']} approaches{bk} |")
    A(f"| **Proposals** — scope and price, sent | **{p['total']}** | **{per(p['total'])}** | "
      f"{p['after_meeting']} of {p['total']} followed a meeting |")
    A(f"| **Sales** — committed work | **{s['total']}** | **{per(s['total'])}** | "
      f"USD {s['value']:,} |")
    A("")
    A("*Band widths in the visual taper for shape; the percentage on every band carries the value.*")
    A("")
    A(f"**Rules of thumb:** {ratio(a['orgs'])} organisations contacted produces an Approach · "
      f"{ratio(m['held'])} a Meeting held · {ratio(p['total'])} a Proposal.")
    if p.get("without_meeting") or p.get("met_but_no_proposal"):
        bits = []
        if p.get("without_meeting"):
            bits.append(f"**{', '.join(p['without_meeting'])}** asked for a proposal without meeting first")
        if p.get("met_but_no_proposal"):
            bits.append(f"**{', '.join(p['met_but_no_proposal'])}** met but produced no proposal")
        A("")
        A("Proposals do not map one-to-one onto meetings: " + "; ".join(bits) + ".")
    A("")
    A("#### Chart 2 — where the contacted organisations sit, and where they dropped")
    A("")
    A("Every organisation appears once, at its current position. Widths are literal.")
    A("")
    A("| Current position | Orgs | % |")
    A("| --- | --- | --- |")
    A(f"| Email 1 sent, follow-up not yet due | {pos['e1']} | {per(pos['e1'])} |")
    A(f"| Email 2 sent, awaiting Email 3 | {pos['e2']} | {per(pos['e2'])} |")
    A(f"| Email 3 sent — **no response**, closed | {pos['e3_no_response']} | {per(pos['e3_no_response'])} |")
    A(f"| Replied — sequence stopped | {pos['replied']} | {per(pos['replied'])} |")
    A(f"| **Total** | **{n}** | **100%** |")
    A("")
    A("**Where they said no or not now**, keyed to the email that produced the reply:")
    A("")
    A("| Dropped after | Orgs | % of orgs sent that email | Who |")
    A("| --- | --- | --- | --- |")
    for k in ("E1", "E2", "E3"):
        r = d["drop_by_email"][k]
        who = " · ".join(r["orgs"]) if r["orgs"] else "—"
        A(f"| Email {k[-1]} | {r['n']} | {fmt(r['pct'])} of {r['sent']} | {who} |")
    A(f"| **No response, whole sequence** | **{pos['e3_no_response']}** | "
      f"**{per(pos['e3_no_response'])} of {n}** | all three emails sent, never answered |")
    A("")
    tot_no = sum(d["drop_by_email"][k]["n"] for k in ("E1", "E2", "E3"))
    A(f"**{tot_no} organisations said no or not now — {fmt(pct(tot_no, n))} of everyone contacted.** "
      f"Not counted there: {len(d['buckets']['forwarded'])} forwarded the email on without commitment, "
      f"and {len(d['buckets']['live'])} are still live with no meeting yet.")
    A("")
    A("**Proposals is not a number to maximise.** Reported as a count with its ratio, never against a pace "
      "target — see the integrity note in the Proposals section. A low figure here is not underperformance.")
    A("")
    A(f"**Coverage.** Ledger floor `{d['floor']}`; the pre-machine cohort (~20 domains / 61 addresses) has no "
      f"reliable send dates and is excluded by rule. Excluded from the denominator: "
      f"{d['excluded']['draft_waiting']} drafts not yet sent and {d['excluded']['closed_at_dedup']} rows closed at "
      f"de-duplication. Deliverability: {d['addresses']['delivered']} delivered, {d['addresses']['bounced']} hard "
      f"bounces ({fmt(pct(d['addresses']['bounced'], d['addresses']['delivered'] + d['addresses']['bounced']))}). "
      "Approaches count **organisations** (Chris, 2026-09-02) — the same unit as the send denominator. "
      f"**The send base is a floor.** {d['orgs_contacted_in_ledger']} organisations have a first-send date in the "
      f"ledger; {len(d['approaches']['not_in_send_ledger'])} more replied without one and are added, because an "
      "organisation that replied was certainly contacted. Any send the ledger never recorded is still missing, so "
      "every rate here is an upper bound on the true rate. Rates print `—`, never `0`, when a denominator "
      f"is under {MIN_DENOMINATOR}. `Apollo Mailwarming` never enters this ledger.")
    if d["approaches"]["not_in_send_ledger"]:
        A("")
        A(f"> ⚠️ **{len(d['approaches']['not_in_send_ledger'])} organisations replied but have no usable send row** — "
          f"{', '.join(d['approaches']['not_in_send_ledger'])}. They are counted as contacted and as Approaches; "
          "they cannot be placed in the sequence chart above. The outreach run needs to reconcile them.")
    A("")
    A("<!-- END FUNNEL CONVERSION -->")
    return "\n".join(L) + "\n"


def main():
    d = compute()
    OUTJSON.write_text(json.dumps(d, indent=2) + "\n")
    OUTMD.write_text(render(d))
    print(f"Conversion: {d['orgs_contacted']} contacted → {d['approaches']['orgs']} approaches "
          f"({fmt(pct(d['approaches']['orgs'], d['orgs_contacted']))}) → {d['meetings']['total']} meetings "
          f"→ {d['proposals']['total']} proposals · queue: {d['sequence_position']['e1']} at E1, "
          f"{d['sequence_position']['e2']} at E2, {d['sequence_position']['e3_no_response']} closed")
    if d["unattributed"]:
        print(f"⚠️  UNATTRIBUTED: {', '.join(d['unattributed'])}", file=sys.stderr)
        if "--check" in sys.argv:
            sys.exit(1)


if __name__ == "__main__":
    main()
