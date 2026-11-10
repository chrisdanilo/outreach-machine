#!/usr/bin/env python3
"""seqrules.py — the ONE place the sequence timing and stop rules live (Rulebook sections I, J, K, C).

Imported by send.py (the sender) and _shared/master/build_master.py (the master list's next_due column), so the
two can never disagree. Pure functions, no Gmail, no network.

Business day = Mon–Fri that is not a US bank holiday. Holidays = the Federal Reserve schedule
(https://www.federalreserve.gov/aboutthefed/k8.htm): Saturday holidays are not observed, Sunday holidays are
observed Monday. The list lives in _shared/master/settings.json (us_bank_holidays_federal_reserve) — one copy only.
Send slot = 07:00 America/New_York on a business day (Chris 2026-10-30: no per-recipient time zones).
A send that falls on a non-business day is DELAYED to the next business day's slot, never skipped; the next
email is timed from the day the previous one ACTUALLY went out.
"""
import datetime, json, os, re
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_shared", "orchestrator")); import paths  # the one file that knows every folder (2026-11-03)
MASTER = paths.MASTER


def settings(path=None):
    return json.load(open(path, encoding="utf-8")) if path else paths.settings()


class Calendar:
    def __init__(self, s=None):
        s = s or settings()
        self.holidays = set(s["us_bank_holidays_federal_reserve"])
        self.gap = int(s.get("sequence_gap_days", 7))
        hh, mm = (s.get("send_slot", "07:00 America/New_York").split()[0]).split(":")
        self.slot_time = datetime.time(int(hh), int(mm))
        self.last_covered = max(self.holidays) if self.holidays else None

    def covered(self, d):
        """FAIL CLOSED beyond the last year in the holiday list — an unknown holiday is never assumed open."""
        return self.last_covered is not None and d.year <= int(self.last_covered[:4])

    def is_business_day(self, d):
        return d.weekday() < 5 and d.isoformat() not in self.holidays

    def roll(self, d):
        while not self.is_business_day(d):
            d += datetime.timedelta(days=1)
        return d

    def slot(self, d):
        """07:00 ET on the first business day on or after date d."""
        return datetime.datetime.combine(self.roll(d), self.slot_time, ET)

    def next_slot(self, now):
        """First slot strictly after `now` (aware datetime)."""
        d = now.astimezone(ET).date()
        s = self.slot(d)
        while s <= now:
            d = d + datetime.timedelta(days=1)
            s = self.slot(d)
        return s

    def due(self, last_send_date):
        """Next email's due slot: last ACTUAL send + gap days, rolled forward to a business day."""
        return self.slot(last_send_date + datetime.timedelta(days=self.gap))


AUTO_SUBJ = re.compile(r"^(automatic reply|auto(matic)?[- ]?reply|autoreply|auto:|out of (the )?office|"
                       r"thank you for your (email|correspondence|message)|i am (currently )?out|[a-z]+ out:|"
                       r"out of office|.*\bout of the office\b)", re.I)


def msg_class(sender, subject=None, me="chris@chrisdanilo.com"):
    s = (sender or "").lower()
    if s == me:
        return "own"
    if "mailer-daemon" in s or "postmaster" in s:
        return "dsn"
    if subject is not None and (AUTO_SUBJ.match(subject.strip()) or subject.lower().startswith("undeliverable")):
        return "dsn" if subject.lower().startswith("undeliverable") else "auto"
    return "human" if subject is not None else "unknown"


def collapse_own(sends, minutes=24 * 60):
    """Rule 3a (old sender, Chris 2026-10-26): an own message less than 24 h after the previous own message is a copy, never a step."""
    out, dups = [], []
    for s in sorted(sends, key=lambda x: x["date"]):
        t = datetime.datetime.fromisoformat((s["date"] if "T" in s["date"] else s["date"][:10] + "T00:00:00") .replace("Z", "+00:00"))
        if t.tzinfo is None: t = t.replace(tzinfo=datetime.timezone.utc)   # a date-only record = that day; two on one day = one email
        if out and t and out[-1].get("_t") and (t - out[-1]["_t"]).total_seconds() <= minutes * 60:
            dups.append(s)
            continue
        s = dict(s, _t=t)
        out.append(s)
    for s in out:
        s.pop("_t", None)
    return out, dups


def decide(th, slot, cal, *, bounced=(), autos=(), human=False, drafts=0, review_hold=None,
           stopped=None, exclusions=None, partial=False, me="chris@chrisdanilo.com"):
    """One thread -> what happens at `slot` (aware datetime). Returns dict(action, email, reason, ...).
    th: {"status","sends":[{"date","to","cc"}], "labels":[...]}  (sends = Chris's own messages, oldest first)
    actions: SEND | REVIEW_DRAFT | CLOSE | WAIT | DELAYED | STOPPED | HELD | READ (decided by the fresh thread read) | NONE
    """
    sd = slot.astimezone(ET).date()
    if not cal.covered(sd):
        return {"action": "HELD", "reason": "FAIL CLOSED: holiday list does not cover %d" % sd.year}
    ex = {k: v for k, v in (exclusions or {}).items() if v}
    if ex:
        return {"action": "STOPPED", "reason": "excluded: " + ", ".join(sorted(ex))}
    if stopped:
        return {"action": "STOPPED", "reason": stopped}
    st = th.get("status") or "open"
    if st.startswith("closed"):
        return {"action": "NONE", "reason": "closed ✗"}
    if human or st.startswith("replied"):
        return {"action": "STOPPED", "reason": "a person replied — Chris's move (★)"}
    if st.startswith("attention"):
        return {"action": "HELD", "reason": "⚠ needs Chris (label)"}
    if st.startswith("hold"):
        return {"action": "HELD", "reason": "⏸ on hold (label)"}
    sends, dups = collapse_own(th.get("sends") or [])
    n = len(sends)
    if n == 0:
        return {"action": "NONE", "reason": "Email 1 not sent yet (Email 1 is always Chris's)"}
    last = datetime.date.fromisoformat(sends[-1]["date"][:10])
    rec_to = [a.lower() for a in (sends[0].get("to") or [])]
    rec_cc = [a.lower() for a in (sends[0].get("cc") or [])]
    if sends[-1].get("to"):  # follow the most recent email AS SENT (Chris's hand edits included)
        rec_to = [a.lower() for a in sends[-1]["to"]]
        rec_cc = [a.lower() for a in (sends[-1].get("cc") or [])]
    b = {x.lower() for x in bounced}
    base = {"sends": n, "last_sent": last.isoformat(), "duplicates": len(dups), "partial": partial}
    floor = int(th.get("stage_floor") or 0)          # a stage never moves backward (Gmail label / master stage)
    if floor > n:
        return dict(base, action="READ", email=min(floor + 1, 3) if floor < 3 else None,
                    reason="Email %d already went out (Gmail label) but its date is not read yet — the thread read decides %s"
                           % (floor, "close vs wait" if floor >= 3 else "when Email 3 is due"), needs_read=True)
    if n >= 3:
        cd = cal.due(last)
        if cd <= slot:
            return dict(base, action="CLOSE", reason="Email 3 sent %s, no reply in 7 days → ✗" % last)
        return dict(base, action="WAIT", reason="close ✗ on %s if no reply" % cd.date())
    nxt = n + 1
    due = cal.due(last)
    if drafts:
        if review_hold:
            return dict(base, action="NONE", email=nxt, reason="review draft already waiting in Gmail — Chris sends it")
        return dict(base, action="HELD", email=nxt, reason="a draft is open on the thread (Chris's)")
    unknown_rcpt = not rec_to
    if unknown_rcpt and b:
        return dict(base, action="HELD", email=nxt, reason="a bounce is on the thread and the recipients are not in the record yet — needs a thread read")
    if rec_to and all(a in b for a in rec_to):
        return dict(base, action="STOPPED", email=nxt, reason="To bounced: " + ", ".join(rec_to))
    live = [a for a in rec_to + rec_cc if a not in b]
    dropped = [a for a in rec_cc if a in b]
    if not live and not unknown_rcpt:
        return dict(base, action="STOPPED", email=nxt, reason="no deliverable recipient left")
    if due > slot:
        return dict(base, action="WAIT", email=nxt, reason="Email %d due %s" % (nxt, due.date()), due=due.isoformat(),
                    recipients=len(live), dropped=dropped)
    # out-of-office (Rulebook J): only auto-replies that arrived AFTER the last own send count
    act = [a for a in autos if a.get("after_last_send")]
    out_by = {a["sender"].lower(): a.get("return") for a in act}
    notes = ["recipients = Email 1's To/Cc, read from the thread at send time"] if unknown_rcpt else []
    if live and all(a in out_by for a in live):
        rets = [r for r in (out_by[a] for a in live) if r]
        if rets and len(rets) == len(live):
            earliest = min(datetime.date.fromisoformat(r) for r in rets)
            nd = cal.slot(earliest + datetime.timedelta(days=1))
            if nd > slot:
                return dict(base, action="DELAYED", email=nxt, reason="every recipient is out; earliest back %s" % earliest,
                            due=nd.isoformat(), recipients=len(live))
        else:
            notes.append("every recipient sent an auto-reply with no readable return date — check at send time")
    if nxt == 3 and act:
        unknown = [a["sender"] for a in act if not a.get("return")]
        still = [a["sender"] for a in act if a.get("return") and datetime.date.fromisoformat(a["return"]) >= slot.date()]
        if still:
            r = max(datetime.date.fromisoformat(a["return"]) for a in act if a.get("return"))
            return dict(base, action="DELAYED", email=nxt, reason="Email 3 waits while an auto-reply is active (back %s)" % r,
                        due=cal.slot(r + datetime.timedelta(days=1)).isoformat(), recipients=len(live))
        if unknown:
            notes.append("Email 3 waits while an auto-reply is active: return date not readable for %s — sender re-checks" % ", ".join(unknown))
    if review_hold:
        return dict(base, action="REVIEW_DRAFT", email=nxt, reason="review hold — draft on the existing thread for Chris",
                    recipients=(len(live) or None), dropped=dropped, notes=notes)
    if (slot.date() - last).days > 28:
        notes.append("long overdue: the last email went out %s" % last)
    return dict(base, action="SEND", email=nxt, overdue=due < slot, due=due.isoformat(),
                reason=("overdue since %s → next slot" % due.date()) if due < slot else "due",
                recipients=(len(live) or None), dropped=dropped, notes=notes)
