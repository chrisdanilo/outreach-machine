#!/usr/bin/env python3
"""timing.py -- when outreach about an event opens (Rulebook F; Stage 5, Chris 2026-10-30/31). Pure functions, no I/O.

  compute(event, as_of) -> {"edition_date", "edition_basis", "lead_months", "outreach_opens", "status", "why"}
  status is one of:
     open_now                 approach now
     queued_until YYYY-MM-DD  approach on that date (9 months before the event · the day a call for speakers opens ·
                              9 months before the NEXT edition when this one is under 1 month out or its keynote is chosen)
  The rules themselves live ONLY in the Rulebook, section F (Chris 2026-11-10). kind() and will_recur() apply Rulebook E3.
  An edition date given only as a month counts as the 1st of that month (earliest = go early)."""
import datetime, re

QUIET_MONTHS = 3

def add_months(d, n):
    y, m = divmod(d.month - 1 + n, 12)
    y += d.year; m += 1
    for day in (d.day, 28):
        try: return datetime.date(y, m, min(day, 31 if m in (1, 3, 5, 7, 8, 10, 12) else 30 if m != 2 else 29))
        except ValueError: continue
    return datetime.date(y, m, 28)

def parse_date(v):
    """'2027-01-30' | '2027-01' | '2027-01 (estimated)' | '2027-01-30 (confirmed)' -> (date, exact:bool) or (None, False)."""
    s = str(v or "").strip()
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        try: return datetime.date(int(m[1]), int(m[2]), int(m[3])), True
        except ValueError: return None, False
    m = re.match(r"^(\d{4})-(\d{2})\b", s)
    if m and 1 <= int(m[2]) <= 12: return datetime.date(int(m[1]), int(m[2]), 1), False
    return None, False

def parse_attendance(v):
    """'1,000+' -> 1000 · '500-700' -> 500 · 350 -> 350 · None/'unknown' -> None (unknown)."""
    if v is None: return None
    if isinstance(v, dict): v = v.get("value")          # Machine 2 records: {"value": "...", "source_url": "..."}
    if v is None: return None
    if isinstance(v, (int, float)): return int(v)
    v = re.sub(r"https?://\S+", " ", str(v))
    nums = [int(x.replace(",", "")) for x in re.findall(r"\d[\d,]*", str(v))]
    nums = [n for n in nums if n >= 10 and not (1990 <= n <= 2100)]
    return min(nums) if nums else None

def lead_months(attendance=None):
    """One lead for every event (Chris 2026-11-09): 9 months. Attendance is kept on the record but decides nothing."""
    return 9

def _yes(v): return str(v).strip().lower() in ("yes", "true", "likely", "y")

def edition(ev, as_of):
    """The next edition date on/after as_of: confirmed/estimated next date, else last edition rolled forward a year at a time."""
    d, exact = parse_date(ev.get("next_edition_date"))
    basis = "next edition date" + ("" if exact else " (month only — 1st of month)")
    if d is None:
        d, exact = parse_date(ev.get("last_edition_date"))
        basis = "last edition rolled forward a year (estimated)"
        if d is None: return None, None
    step = 24 if re.search(r"bienn", "%s %s" % (ev.get("cadence") or "", ev.get("name") or ""), re.I) else 12   # biennial events roll 2 years
    while d < as_of:
        d = add_months(d, step); basis = "rolled forward %s (estimated)" % ("two years — biennial" if step == 24 else "a year")
    return d, basis

def months_between(a, b):
    """Whole months from a to b (b >= a), e.g. 2026-11-09 -> 2027-05-14 = 6."""
    n = (b.year - a.year) * 12 + (b.month - a.month)
    if b.day < a.day: n -= 1
    return n

LEAD_MONTHS = 9        # F2: one lead for every event; size does not matter
NEAR_MONTHS = 3        # F4: 1-3 months out the keynote check decides
NEVER_MONTHS = 1       # F4 (Chris 2026-11-10): under 1 month out there is no outreach for this edition at all

def parse_year(v):
    m = re.match(r"^\s*((?:19|20)\d\d)", str(v or "")); return int(m[1]) if m else None

# What kind of event is it (Rulebook E3, Chris 2026-11-10). The helper's own answer (ev["kind"]) wins; else the name decides.
TRAINING = re.compile(r"pre-?\s?service|in-?\s?service|staff (training|development|day)|all-?staff|training (series|days?)|\btrainings\b|professional development (series|days?)|\bpd[ /](series|sessions?|days?)|coach(ing)?/pd|orientation|convocation|\bcourse\b|webinar", re.I)
CONFERENCE = re.compile(r"conference|convention|summit|symposium|institute|congress|forum|annual meeting|biennial meeting|campference|colloque|congr[eè]s", re.I)
UNCLEAR = re.compile(r"retreat|meeting|gathering|\bexpo\b|academy|series|sessions?\b|workshop|journ[eé]e", re.I)
def kind(ev):
    """'conference' (an event type that needs a keynote speaker -> OM-2) · 'training' (training day / staff training -> OM-1) ·
    'unclear' (retreat, meeting, gathering, expo ... -> not OM-2 until Chris decides; shown in the dossier's decisions)."""
    k = str(ev.get("kind") or "").strip().lower()
    if k in ("conference", "training", "unclear"): return k
    n = str(ev.get("name") or "")
    if TRAINING.search(n): return "training"
    if CONFERENCE.search(n): return "conference"
    if UNCLEAR.search(n): return "unclear"
    return "conference"

def will_recur(ev, as_of):
    """Is there a sign this event happens in the coming year (Rulebook E3, Chris 2026-11-10)? -> (bool, why).
    Yes: no date on record at all (a conference with no date is still approached) · two or more past editions on record ·
    the newest edition on record is within one cycle (last year or later; two years back when the event is biennial).
    No: the only edition on record is older than that."""
    ys = [y for y in (parse_year(ev.get("next_edition_date")), parse_year(ev.get("last_edition_date"))) if y]
    if not ys: return True, "no date on record"
    if len(ev.get("past_editions") or []) >= 2: return True, "%d past editions on record" % len(ev["past_editions"])
    bi = bool(re.search(r"bienn", "%s %s" % (ev.get("cadence") or "", ev.get("name") or ""), re.I))
    if max(ys) >= as_of.year - (2 if bi else 1): return True, "newest edition on record is %d%s" % (max(ys), " (biennial)" if bi else "")
    return False, "the only edition on record is %d — too old to assume it still runs" % max(ys)

def compute(ev, as_of):
    """Chris's decision tree (2026-11-09, amended 2026-11-10; Rulebook F). Returns edition_date, edition_basis, lead_months,
    outreach_opens, status, why. Planning date = the set next date, else the last edition rolled forward (interim estimate).
      a live call for speakers / open form / keynote request -> open_now (or queued to the day the call opens) — beats every rule below
      under 1 month out   -> no outreach for this edition: queued_until 9 months before the NEXT edition
      no date anywhere    -> open_now
      > 9 months out      -> queued_until (date - 9 months)
      3-9 months out      -> open_now
      1-3 months out      -> keynote listed, or this edition's call closed -> queued_until 9 months before the NEXT edition
                             no keynote listed, or cannot tell -> open_now
    The next edition is this one plus 12 months (24 if biennial), so "9 months before the next" is 3 months after this one."""
    out = {"edition_date": None, "edition_basis": None, "lead_months": LEAD_MONTHS, "outreach_opens": None, "status": "open_now", "why": ""}
    cfp = ev.get("cfp") or {}
    dl, _ = parse_date(cfp.get("deadline")); op, _ = parse_date(cfp.get("opens"))
    cfp_open = bool((dl and dl >= as_of) or (op and op >= as_of) or str(cfp.get("status") or "").lower() == "open" or ev.get("keynote_request"))
    d, basis = edition(ev, as_of)
    step = 24 if re.search(r"bienn", "%s %s" % (ev.get("cadence") or "", ev.get("name") or ""), re.I) else 12
    def next_cycle(reason):
        opens = add_months(add_months(d, step), -LEAD_MONTHS)
        out.update(outreach_opens=opens.isoformat(), status="queued_until %s" % opens.isoformat(),
                   why="event %s %s — no outreach for this edition; re-evaluate %s, 9 months before the next one (F4)" % (d.isoformat(), reason, opens.isoformat()))
        return out
    if d is not None:
        out.update(edition_date=d.isoformat(), edition_basis=basis)
    # a live call for speakers / open speaker form wins over EVERY timing rule, the under-1-month rule included (F3; Chris 2026-11-10)
    if cfp_open:
        if op and op > as_of:
            out.update(outreach_opens=op.isoformat(), status="queued_until %s" % op.isoformat(), why="published call for speakers opens %s (F3)" % op.isoformat())
        else:
            out.update(outreach_opens=as_of.isoformat(), status="open_now",
                       why="published %s — they are looking for speakers (F3/E5)" % ("keynote request" if ev.get("keynote_request") else "call for speakers" + (" — deadline %s" % dl.isoformat() if dl else "")))
        return out
    if d is not None and add_months(as_of, NEVER_MONTHS) > d: return next_cycle("is under 1 month out")
    if d is None:
        out.update(outreach_opens=as_of.isoformat(), status="open_now", why="no next or last edition date on record — no known time constraint, approach now (F1)"); return out
    m = months_between(as_of, d)
    if m >= LEAD_MONTHS:
        opens = add_months(d, -LEAD_MONTHS)
        if opens <= as_of:
            out.update(outreach_opens=as_of.isoformat(), status="open_now", why="event %s is %d months out — inside the 9-month window (F2)" % (d.isoformat(), m))
        else:
            out.update(outreach_opens=opens.isoformat(), status="queued_until %s" % opens.isoformat(), why="event %s is %d months out — opens 9 months before, %s (F2)" % (d.isoformat(), m, opens.isoformat()))
        return out
    if m >= NEAR_MONTHS:
        out.update(outreach_opens=as_of.isoformat(), status="open_now", why="event %s is %d months out — approach now (F2)" % (d.isoformat(), m)); return out
    # 1-3 months out: the keynote check decides (F4)
    listed = _yes(ev.get("keynote_announced"))
    closed = dl is not None and dl < as_of and add_months(d, -12) <= dl <= d      # THIS edition's call has closed
    if listed or closed: return next_cycle("is 1–3 months out and the keynote is %s" % ("already listed" if listed else "decided (call closed %s)" % dl.isoformat()))
    out.update(outreach_opens=as_of.isoformat(), status="open_now",
               why="event %s is 1–3 months out, %s — approach now (F4)" % (d.isoformat(), "no keynote listed" if str(ev.get("keynote_announced") or "").strip().lower() == "no" else "keynote not found on the pages read"))
    return out

RANK = {"open_now": 0, "queued_until": 1, "quiet_until": 2, "hold": 3, "date_unknown": 4}   # quiet_until / hold / date_unknown are no longer produced (2026-11-09); kept so old records still rank
def org_summary(results):
    """Best event for an OM-2 org: open now and 3-9 months out > open now 1-3 months out > open, no date > earliest queued."""
    if not results: return None
    def band(r):          # Chris 2026-11-10: look at the whole calendar; the best event is in the 3-9 month range, never simply the soonest
        if r["status"] != "open_now": return 9
        a, _ = parse_date(r.get("outreach_opens")); e, _ = parse_date(r.get("edition_date"))
        if not a or not e: return 2                      # open, no date on record
        return 0 if months_between(a, e) >= NEAR_MONTHS else 1   # 3-9 months first, then 1-3 months
    def key(r):
        st = r["status"].split(" ")[0]
        return (RANK.get(st, 9), band(r), r.get("outreach_opens") or "9999", r.get("edition_date") or "9999")
    ranked = sorted(results, key=key); best = ranked[0]
    out = {"status": best["status"], "outreach_opens": best.get("outreach_opens"), "event": best.get("event"), "edition_date": best.get("edition_date"), "why": best.get("why")}
    if len(ranked) > 1:   # Chris 2026-11-09: several conferences = high-value org; the dossier must show every event and why this one
        out["all_events"] = [{"event": r.get("event"), "url": r.get("url"), "status": r["status"], "edition_date": r.get("edition_date")} for r in ranked]
        out["best_fit_why"] = "%s is the best fit: %s; the other %d event(s) rank behind it (%s)." % (
            best.get("event") or "this event", best.get("why") or best["status"], len(ranked) - 1, "; ".join("%s → %s" % (r.get("event") or "?", r["status"]) for r in ranked[1:]))
    return out
