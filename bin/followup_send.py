#!/usr/bin/env python3
"""
followup_send.py -- the follow-up sender's program (method §0.16, config.followup_sender).

Emails 2 and 3 of the CCR&R sequence are SENT by a scheduled task ("CCR&R Follow-up Sender") at
08:30-10:00 in the recipient's time zone, on business days, never on a bank holiday. Chris approved
this on 2026-10-04 (rulings verbatim in config.followup_sender._why). Email 1 is never sent by a machine.

THE ONE DESIGN RULE: THE GMAIL THREAD IS THE LEDGER. No new ledger, no queue file.
  emails sent so far      = the number of Chris's own messages on the thread
  last send               = the newest of them
  next recipients/greeting= the previous email's To/Cc and its first line, AS SENT (R13)
  idempotency             = a send that happened but was not recorded is an extra own message -> never repeated

THIS SCRIPT CANNOT CALL GMAIL OR ZAPIER. Those are connector tools only the session can call. So the
session runs the exact reads this script prints, saves each tool result VERBATIM as a file under
runs/<date>/sender/<fire>/raw/, and this script computes everything from those files. The session
decides nothing (ARCHITECTURE-v2: GATHER by the session, COMPUTE by the script, ACT with printed params).

USAGE (one fire)
  python3 bin/followup_send.py --queries [--fire 0838ET]
      prints the Gmail reads to run and the folder to save them in (raw/search_N.json, raw/drafts_N.json)
  python3 bin/followup_send.py --plan [--fire 0838ET]
      pass 1: if it still needs thread reads or message bodies it prints NEEDS lines and exits 3 --
              save them as raw/thread_<id>.json / raw/message_<id>.json and run --plan again
      pass 2: writes plan.json -- one row per thread: armable | would-send | hold | skip, reason. NO PARAMS:
              nothing is sendable until --arm has re-read the thread (CAPA 2026-10-06)
  python3 bin/followup_send.py --arm [--fire 0838ET]
      pass 1: prints one get_thread METADATA_ONLY per armable row -> raw/arm_thread_<id>.json; exits 3
      pass 2: re-derives every armable row from that FRESH read (same message ids, same own count, no own
              message dated today, no stage/stop label, no hidden message, not claimed by another in-flight
              fire, read younger than arm_ttl_seconds) and writes armed.json -- the ONLY file that carries
              send params. Rows that fail are 'dropped' with the reason
  python3 bin/followup_send.py --verify [--fire 0838ET]
      pass 1: prints the Sent read-backs to run (raw/verify_thread_<id>.json, raw/verify_kit.json); exits 3
      pass 2: writes followup_sends.json and prints the exact label calls for stage_after_send. Each send is
              reconciled against the armed row (recipients), counted (own messages == plan + 1) and checked
              for a same-day duplicate; raw/zapier_<thread>.json for an un-armed thread is a 🔴 finding
OTHER
  python3 bin/followup_send.py --preview             the nightly's "Scheduled follow-ups:" line + table
  python3 bin/followup_send.py --report-yesterday    the nightly's "Sender:" line
  python3 bin/followup_send.py --as-of YYYY-MM-DD --fire <dir>   history replay: what WOULD have been sent
                                                     that day vs what Chris actually sent (the gather must
                                                     hold the full thread histories)
  python3 bin/followup_send.py --selftest            synthetic cases (weekend, holiday, window, idempotency)

CONCURRENCY (CAPA 2026-10-06 -- two fires overlapped and 8 orgs received Email 2 twice):
  * --queries FAILS CLOSED when another fire of the same day holds the sender: its queries.json is younger
    than config.followup_sender.fire_lock_minutes and it has no followup_sends.json. The run folder is the lock.
    --plan and --arm repeat the check. A fire that yields writes queries.json {aborted:true} and can never plan.
  * --plan carries no params; --arm re-reads every candidate thread seconds before the send and arms only what
    the fresh read confirms. Threads planned or armed by another in-flight fire are claimed -> dropped.
  * every raw file is validated structurally before it is trusted (16-hex ids, threadId == filename, counts,
    dates); one violation fails the whole fire closed -- a transcript with one error cannot be trusted anywhere.

DECISION RULES in --plan, in order; the first FALSE is the row's reason (method §0.16):
  0 today is a business day, not in never_send_dates, and the holiday list still covers today
    (an uncovered year FAILS the whole fire CLOSED -- an unknown holiday is never assumed open)
  1 no live draft on the thread (a draft = Chris's)            -> skip  live draft
  2 own messages on the thread == 1 or 2                        -> skip  stage complete / not ours
  3 no HUMAN message anywhere on the thread (a DSN or an auto-reply by subject prefix is not a human;
    a non-own message whose subject is unknown is fetched with get_message MINIMAL first)
                                                                   -> hold  human message on thread
    if the newest message is a DSN/auto-reply: allowed ONLY because the explicit `subject` param is
    proven to win (config zapier.subject_param_honored, tested 2026-10-05) -- the thread's own subject
    is always passed; a DSN on the thread whose bounced address the nightly has not yet written into
    config.hard_bounces/cleanup_departed                               -> hold  (R2 repair not recorded yet)
  4 no ★ X ⚠ ⏸ label; no hidden (trashed) message newest        -> skip / hold
  4b the newest own message is not dated today (org local)       -> skip  already sent today
  5 due = last own send + sequence_gap_days, rolled past weekends/holidays; today >= due -> skip not due
  6 org local time inside send_local_time..send_window_end       -> skip  not in window (next fire retries)
  7 recipients = previous email's To/Cc minus hard_bounces/cleanup_departed; bounced Cc -> dropped +
    R2 parenthetical; bounced To -> hold; >= 1 recipient left; EVERY recipient must be a Ledger B
    address in contacted.jsonl (a retyped or corrupted gather can never produce a new address)
  8 greeting names parsed from the previous email's first line; bounced names removed; >= 1 name
  9 body rendered from Cold-Outreach-Sequence-CCR&R.md (Email 2 v4 / Email 3 v3 + bold), bcc = hubspot_bcc

Exit codes: 0 ok · 2 reported problems (nothing to send, holds, findings) · 3 NEEDS more raw files · 1 structural / FAIL CLOSED
"""
import sys, os, re, json, glob, html, pathlib, datetime, argparse
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).resolve().parent.parent          # outreach-machine/
HST = ROOT.parents[1]                                          # 3.Human Skills Training/
COPY = HST / "Marketing" / "Cold-Outreach-Sequence-CCR&R.md"
CONFIG = ROOT / "config.json"
CONTACTED = ROOT / "contacted.jsonl"
RUNS = pathlib.Path(os.environ["FS_RUNS_OVERRIDE"]) if os.environ.get("FS_RUNS_OVERRIDE") else ROOT / "runs"
ET = ZoneInfo("America/New_York")
HEX = re.compile(r"\b[0-9a-f]{16}\b")
GREETING_WORDS = re.compile(r"^(hey|hi|hello|dear)\s+", re.I)
NAME_TOKEN = re.compile(r"^[A-Za-z][A-Za-z.'\-]*( [A-Za-z][A-Za-z.'\-]*){0,2}$")
# same discriminator bin/hubspot_cleanup.py uses (R17.1 cheap test: DSN sender, then the auto-reply subject prefix)
AUTO = re.compile(r"^(automatic reply|auto(matic)?[- ]?reply|autoreply|auto:|out of (the )?office|"
                  r"thank you for your (email|correspondence|message)|i am (currently )?out|delivery status notification|undeliverable)", re.I)


def other_kind(o):
    """dsn | auto | human | unknown (no subject fetched yet). Anything but dsn/auto stops the sequence."""
    snd = (o.get("sender") or "").lower()
    if "mailer-daemon" in snd or "postmaster" in snd:
        return "dsn"
    subj = o.get("subject")
    if subj is None:
        return "unknown"
    return "auto" if AUTO.match(subj.strip()) else "human"
UTC = datetime.timezone.utc


# ---------------------------------------------------------------- helpers
def jload(p):
    return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))


def jdump(p, o):
    pathlib.Path(p).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(p).write_text(json.dumps(o, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_dt(s):
    """Connector dates: '2026-10-01T12:00:00Z' (or with offset)."""
    s = s.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    d = datetime.datetime.fromisoformat(s)
    if d.tzinfo is None:
        d = d.replace(tzinfo=UTC)
    return d


def now_utc():
    # FS_NOW_OVERRIDE is honoured ONLY together with FS_RUNS_OVERRIDE (a sandbox runs folder): replay and dry
    # runs can pin the clock; a production fire (real runs/) can never be told what time it is.
    if os.environ.get("FS_NOW_OVERRIDE") and os.environ.get("FS_RUNS_OVERRIDE"):
        return parse_dt(os.environ["FS_NOW_OVERRIDE"])
    return datetime.datetime.now(UTC)


def cfg_block():
    cfg = jload(CONFIG)
    fs = cfg.get("followup_sender")
    if not fs:
        sys.exit("config.followup_sender missing -- nothing runs without it")
    return cfg, fs


def me(cfg):
    return cfg.get("draft_writer", {}).get("zapier", {}).get("connection", "<SENDER_EMAIL>").lower()


def discounted_sends():
    """config.followup_sender.discounted_sends: {message_id: why}. An own message listed here is NOT counted as a
    send (Chris 2026-10-12, CAPA 2026-10-06: the 8 duplicate Email 2s sent 7 min after the first must not make those
    threads read as 'stage complete'). It stays in the listed messages, so hidden-message counts are unaffected.
    Applied identically in ingest (plan), arm_gate and verify -- the three places own messages are counted."""
    try:
        return set((jload(CONFIG).get("followup_sender") or {}).get("discounted_sends", {}) or {})
    except Exception:
        return set()


def is_business_day(d, fs):
    return d.weekday() < 5 and d.isoformat() not in set(fs.get("never_send_dates", []))


def roll_forward(d, fs):
    while not is_business_day(d, fs):
        d += datetime.timedelta(days=1)
    return d


def holiday_coverage(fs, today):
    dates = sorted(fs.get("never_send_dates", []))
    last = datetime.date.fromisoformat(dates[-1]) if dates else None
    covered = bool(last) and today.year <= last.year
    days_left = (last - today).days if last else -1
    return last, covered, days_left


def contacted_index():
    """thread id -> org row; bounced address -> first name (Ledger B 'person')."""
    by_thread, bounce_name, known = {}, {}, set()
    if not CONTACTED.exists():
        return by_thread, bounce_name, known
    for line in CONTACTED.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("type") == "org":
            for t in HEX.findall(str(r.get("thread", ""))):
                by_thread[t] = r
        elif r.get("type") == "address":
            if r.get("address"):
                known.add(str(r["address"]).lower())
            if r.get("outcome") != "bounced":
                continue
            person = str(r.get("person") or "")
            m = re.search(r"[A-Z][a-z]+", person.replace("*", "").replace('"', ""))
            if m and "generic" not in person.lower() and "no name" not in person.lower():
                bounce_name[str(r.get("address", "")).lower()] = m.group(0)
    return by_thread, bounce_name, known


def org_zone(row, fs):
    """IANA zone for an org row: tz_overrides by mail domain first, then state_timezones."""
    if not row:
        return None, "no ledger row (state unknown)"
    for d in row.get("domains") or []:
        z = fs.get("tz_overrides", {}).get(str(d).lower())
        if z:
            return z, "override:" + d
    st = (row.get("state") or "").strip().upper()
    z = fs.get("state_timezones", {}).get(st)
    if not z:
        return None, f"no time zone for state {st or '?'}"
    return z, "state:" + st


# ---------------------------------------------------------------- copy file -> HTML
def copy_body(n):
    """The approved body of Email n (2 or 3) from the single source of truth, plus its link map."""
    text = COPY.read_text(encoding="utf-8")
    head = "## Email 2" if n == 2 else "## Email 3"
    start = text.index(head)
    lines = text[start:].split("\n")
    body, i = None, 0
    while i < len(lines):
        if lines[i].strip() == "Hey {Names}," and i > 0 and lines[i - 1].strip() == "":
            j = i
            while j < len(lines) and lines[j].strip() != "---":
                j += 1
            body = "\n".join(lines[i:j]).strip()
            break
        i += 1
    if body is None:
        raise SystemExit(f"copy file: Email {n} body not found (expected a 'Hey {{Names}},' block)")
    links = {}
    for m in re.finditer(r"`([^`]+)` → \*\*(https?://[^\s*]+)\*\*", text[start:start + 20000]):
        links[m.group(1).replace("\n", " ")] = m.group(2)
    return body, links


def inline(txt, links):
    """escape, then **x** -> <b>x</b> (or <b><a href>x</a></b> when x is the hyperlink phrase)."""
    out, pos = [], 0
    for m in re.finditer(r"\*\*(.+?)\*\*", txt, re.S):
        out.append(html.escape(txt[pos:m.start()], quote=False))
        phrase = " ".join(m.group(1).split())
        url = links.get(phrase)
        esc = html.escape(phrase, quote=False)
        out.append(f'<b><a href="{url}">{esc}</a></b>' if url else f"<b>{esc}</b>")
        pos = m.end()
    out.append(html.escape(txt[pos:], quote=False))
    return "".join(out)


def render_html(body_md, greeting, parenthetical, links):
    paras = [p for p in re.split(r"\n\s*\n", body_md.strip()) if p.strip()]
    assert paras and paras[0].strip() == "Hey {Names},", "template must open with the greeting line"
    blocks = [f"<p>{html.escape(greeting, quote=False)}</p>"]
    if parenthetical:
        blocks.append(f"<p>{html.escape(parenthetical, quote=False)}</p>")
    for p in paras[1:]:
        ls = [l.rstrip() for l in p.split("\n")]
        if all(l.lstrip().startswith("- ") for l in ls):
            items = "\n".join(f"<li>{inline(l.lstrip()[2:].strip(), links)}</li>" for l in ls)
            blocks.append(f"<ul>\n{items}\n</ul>")
        else:
            blocks.append(f"<p>{inline(' '.join(l.strip() for l in ls), links)}</p>")
    return '<div dir="ltr">\n' + "\n".join(blocks) + "\n</div>"


def greeting_names(first_line):
    """'Allison, Laura, and Kelli,' / 'Hey [Person 0495] and Sara,' -> ['Allison','Laura','Kelli'] / ['Molly','Sara'].
    Returns (names, problem)."""
    s = first_line.strip().rstrip(",:").strip()
    s = GREETING_WORDS.sub("", s)
    # 2026-10-09 (Chris, method §0.0 R2): generic inboxes are in the outreach. A team-form greeting
    # ('Stacie and team,' / 'Hi CDR team,') is carried forward as written instead of held for Chris.
    # 'team' survives as the last greeting token, so join_names() rebuilds 'Stacie and team'.
    parts = [p.strip() for p in re.split(r",|\band\b|&", s) if p.strip()]
    if not parts or not all(NAME_TOKEN.match(p) for p in parts):
        return [], f"unparsed greeting line: {first_line.strip()[:60]!r}"
    return parts, None


def join_names(names):
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return ", ".join(names[:-1]) + f", and {names[-1]}"


def parenthetical_for(dropped_names):
    """R2 approved copy. The never-assume-a-pronoun rule -> 'them'."""
    if not dropped_names:
        return None
    if len(dropped_names) == 1:
        return f"(I think I got {dropped_names[0]}'s email address wrong, so I'm not including them on this)"
    poss = " and ".join(n + "'s" for n in dropped_names)
    return f"(I think I got {poss} email addresses wrong, so I'm not including them on this)"


# ---------------------------------------------------------------- fire folders
def fire_dir(args, create=False):
    today = (args.today or now_utc().astimezone(ET).date().isoformat())
    if args.fire and os.path.sep in args.fire:
        d = pathlib.Path(args.fire)
    else:
        fid = args.fire or (now_utc().astimezone(ET).strftime("%H%M") + "ET")
        d = RUNS / today / "sender" / fid
    if create:
        (d / "raw").mkdir(parents=True, exist_ok=True)
    return d


def latest_fire_dir(days_back=1):
    """Most recent fire folder today or within days_back days (for --preview)."""
    today = now_utc().astimezone(ET).date()
    for k in range(0, days_back + 1):
        day = (today - datetime.timedelta(days=k)).isoformat()
        cands = sorted(glob.glob(str(RUNS / day / "sender" / "*" / "raw")))
        if cands:
            return pathlib.Path(cands[-1]).parent
    return None


# ---------------------------------------------------------------- concurrency guards (CAPA 2026-10-06)
LOCK_MINUTES_DEFAULT = 50          # < the 60-min slot spacing, > the longest fire seen (24 min on 2026-10-06)
ARM_TTL_DEFAULT = 180


def lock_minutes(fs):
    return int(fs.get("fire_lock_minutes", LOCK_MINUTES_DEFAULT))


def arm_ttl(fs):
    return int(fs.get("arm_ttl_seconds", ARM_TTL_DEFAULT))


def sibling_candidates(d, now=None, minutes=None):
    """Fire folders to inspect: the directory listing PLUS a by-name probe of every HHMMET folder a fire could
    have created in the last `minutes` (+5 ahead). The probe exists because the Cowork mount caches directory
    listings per session: on 2026-10-06 a sibling folder created at 14:35Z was invisible to a session's `ls`
    for over an hour until that session itself wrote into the parent. A stat() by exact name is a fresh lookup."""
    now = now or now_utc()
    seen = {pathlib.Path(q).parent for q in glob.glob(str(d.parent / "*" / "queries.json"))}
    if minutes:
        t = now.astimezone(ET) - datetime.timedelta(minutes=minutes)
        end = now.astimezone(ET) + datetime.timedelta(minutes=5)
        while t <= end:
            cand = d.parent / (t.strftime("%H%M") + "ET")
            if (cand / "queries.json").exists():
                seen.add(cand)
            t += datetime.timedelta(minutes=1)
    return sorted(seen)


def sibling_fires(d, now=None, minutes=None):
    """Every other fire folder of the same day that wrote queries.json:
    {fire, dir, started, aborted, done}. The run folder IS the lock -- no other file."""
    out = []
    for fd in sibling_candidates(d, now, minutes):
        q = fd / "queries.json"
        if fd.name == d.name:
            continue
        try:
            doc = jload(q)
            started = parse_dt(doc["generated"])
            aborted = bool(doc.get("aborted"))
        except Exception:
            started = datetime.datetime.fromtimestamp(os.path.getmtime(q), UTC)
            aborted = False
        out.append({"fire": fd.name, "dir": fd, "started": started, "aborted": aborted,
                    "done": (fd / "followup_sends.json").exists()})
    return out


def in_flight(d, fs, now):
    """(live, stale): siblings that are not done and not aborted. live = started within fire_lock_minutes
    (they HOLD the sender); stale = older than that and never verified (treated as crashed, reported)."""
    lim = datetime.timedelta(minutes=lock_minutes(fs))
    live, stale = [], []
    for s in sibling_fires(d, now, lock_minutes(fs)):
        if s["done"] or s["aborted"]:
            continue
        (live if now - s["started"] <= lim else stale).append(s)
    return live, stale


def claims(d, fs, now):
    """thread id -> fire id, for every thread a LIVE in-flight sibling has planned (plan.json armable) or
    armed (armed.json send). Those threads are off limits to this fire."""
    out = {}
    live, _ = in_flight(d, fs, now)
    for s in live:
        for name, key in (("plan.json", "armable"), ("armed.json", "send")):
            p = s["dir"] / name
            if p.exists():
                try:
                    for r in jload(p).get("rows", []):
                        if r.get("action") == key:
                            out[r["thread"]] = s["fire"]
                except Exception:
                    pass
    return out


def validate_raw(fdir):
    """Structural validation of EVERY raw file. Returns the list of violations. One violation = the
    transcript cannot be trusted anywhere -> the fire fails closed (CAPA 2026-10-06, chance point 2)."""
    raw = fdir / "raw"
    v = []

    def msg_ok(m, tid, where):
        mid = m.get("id")
        if not (isinstance(mid, str) and HEX.fullmatch(mid)):
            v.append(f"{where}: message id {mid!r} is not 16 hex"); return
        if tid and m.get("threadId") not in (None, tid):
            v.append(f"{where}: message {mid} threadId {m.get('threadId')} != {tid}")
        try:
            parse_dt(m["date"])
        except Exception:
            v.append(f"{where}: message {mid} date {m.get('date')!r} unparseable")
        snd = m.get("sender")
        if not isinstance(snd, str) or "@" not in snd:
            v.append(f"{where}: message {mid} sender {snd!r}")
        for k in ("toRecipients", "ccRecipients", "bccRecipients"):
            for a in m.get(k) or []:
                if not isinstance(a, str) or "@" not in a:
                    v.append(f"{where}: message {mid} {k} {a!r}")

    def thread_ok(t, where, expect=None):
        tid = t.get("id") or t.get("threadId")
        if not (isinstance(tid, str) and HEX.fullmatch(tid)):
            v.append(f"{where}: thread id {tid!r} is not 16 hex"); return
        if expect and tid != expect:
            v.append(f"{where}: thread id {tid} != filename {expect}")
        msgs = t.get("messages", [])
        if not isinstance(msgs, list):
            v.append(f"{where}: messages is not a list"); return
        mc = t.get("messageCount")
        if mc is not None and (not isinstance(mc, int) or mc < len(msgs)):
            v.append(f"{where}: messageCount {mc!r} < {len(msgs)} listed")
        ids = [m.get("id") for m in msgs]
        if len(set(ids)) != len(ids):
            v.append(f"{where}: duplicate message ids")
        for m in msgs:
            msg_ok(m, tid, where)

    for f in sorted(raw.glob("*.json")):
        name = f.name
        try:
            doc = jload(f)
        except Exception as e:
            v.append(f"{name}: not JSON ({e})"); continue
        if not isinstance(doc, dict):
            v.append(f"{name}: not a JSON object"); continue
        if name.startswith("search_") or name == "verify_kit.json":
            if not isinstance(doc.get("threads", []), list):
                v.append(f"{name}: threads is not a list"); continue
            for t in doc.get("threads", []):
                thread_ok(t, name)
        elif name.startswith(("thread_", "arm_thread_", "verify_thread_")):
            thread_ok(doc, name, expect=name.rsplit("_", 1)[-1][:-5])
        elif name.startswith("message_"):
            expect = name[len("message_"):-5]
            if doc.get("id") != expect:
                v.append(f"{name}: id {doc.get('id')!r} != filename {expect}")
            if not HEX.fullmatch(str(doc.get("threadId", ""))):
                v.append(f"{name}: threadId {doc.get('threadId')!r} is not 16 hex")
            try:
                parse_dt(doc["date"])
            except Exception:
                v.append(f"{name}: date {doc.get('date')!r} unparseable")
        elif name.startswith("drafts_"):
            if not isinstance(doc.get("drafts", []), list):
                v.append(f"{name}: drafts is not a list"); continue
            for dr in doc.get("drafts", []):
                tid = dr.get("threadId")
                if tid is not None and not HEX.fullmatch(str(tid)):
                    v.append(f"{name}: draft threadId {tid!r} is not 16 hex")
        elif name.startswith("zapier_"):
            tid = name[len("zapier_"):-5]
            for r in doc.get("results", []) or []:
                if r.get("threadId") not in (None, tid):
                    v.append(f"{name}: Zapier result threadId {r.get('threadId')} != {tid}")
    return v


def arm_gate(row, gthread, arm_doc, age_s, now, cfg, fs, claimed):
    """THE LAST CHECK BEFORE A SEND, from a FRESH get_thread read saved seconds ago. Pure: (ok, reason).
    Everything the plan assumed is re-derived here; any difference drops the row (fail closed)."""
    me_addr = me(cfg)
    ttl = arm_ttl(fs)
    if age_s > ttl:
        return False, f"arm read is {int(age_s)} s old (> {ttl} s) -- re-read"
    tid = row["thread"]
    if (arm_doc.get("id") or arm_doc.get("threadId")) != tid:
        return False, "arm read is for a different thread"
    msgs = sorted(arm_doc.get("messages", []), key=lambda m: parse_dt(m["date"]))
    disc = discounted_sends()
    ids = {m["id"] for m in msgs if m["id"] not in disc}
    gids = {x["id"] for x in gthread["sends"]} | {x["id"] for x in gthread["others"]}
    if ids != gids:
        new, gone = sorted(ids - gids), sorted(gids - ids)
        return False, "thread changed since the gather: " + (f"new message(s) {new}" if new else f"message(s) gone {gone}")
    own = [m for m in msgs if me_addr in (m.get("sender") or "").lower() and m["id"] not in disc]
    if len(own) != row["own_count"]:
        return False, f"own message count is {len(own)}, plan had {row['own_count']}"
    Z = ZoneInfo(row["tz"])
    today_local = now.astimezone(Z).date()
    if any(parse_dt(m["date"]).astimezone(Z).date() == today_local for m in own):
        return False, "an own message is already dated today -- already sent today"
    labels = set()
    for m in msgs:
        labels.update(m.get("labelIds", []) or [])
    stage = cfg["stage_labels"].get(str(row["email_no"]))
    if stage and stage in labels:
        return False, f"stage label {stage} (Email {row['email_no']} sent) already on the thread"
    stop_labels = {cfg["stage_labels"].get(k) for k in ("replied", "closed", "attention", "hold")} - {None}
    if stop_labels & labels:
        return False, "stop label present: " + ", ".join(sorted(stop_labels & labels))
    mc = arm_doc.get("messageCount")
    if mc is not None and mc - len(msgs) > 0:
        return False, f"{mc - len(msgs)} hidden message(s) on the thread"
    if tid in claimed:
        return False, f"claimed by in-flight fire {claimed[tid]}"
    return True, "fresh read agrees with the plan"


# ---------------------------------------------------------------- ingest raw tool outputs
def ingest(fdir, me_addr):
    """Builds the normalised gather from raw/*.json. Shapes are the connector's own:
       search_threads -> {threads:[{id,messageCount,messages:[{id,threadId,sender,toRecipients,ccRecipients,
                          bccRecipients,date,labelIds}]}]}  · list_drafts -> {drafts:[{threadId,...}]}
       get_thread -> {id,messageCount,messages:[...]} · get_message -> {id,threadId,plaintextBody,subject,...}"""
    raw = fdir / "raw"
    threads, drafts_threads, bodies = {}, set(), {}
    msg_count = {}

    def take(t):
        tid = t.get("id") or t.get("threadId")
        rec = threads.setdefault(tid, {"thread": tid, "messages": {}, "labels": set(), "complete": False, "subject": None})
        if t.get("messageCount") is not None:
            msg_count[tid] = int(t["messageCount"])
        for m in t.get("messages", []):
            rec["messages"][m["id"]] = m
            rec["labels"].update(m.get("labelIds", []))
            if m.get("subject") and not rec["subject"]:
                rec["subject"] = m["subject"]
        return rec

    for f in sorted(raw.glob("search_*.json")):
        for t in jload(f).get("threads", []):
            take(t)
    for f in sorted(raw.glob("thread_*.json")):
        rec = take(jload(f))
        rec["complete"] = True            # read in full (drafts/trashed still omitted by the connector)
    for f in sorted(raw.glob("drafts_*.json")):
        for d in jload(f).get("drafts", []):
            if d.get("threadId"):
                drafts_threads.add(d["threadId"])
    for f in sorted(raw.glob("message_*.json")):
        m = jload(f)
        bodies[m["id"]] = m
        rec = threads.get(m.get("threadId"))
        if rec is not None and m.get("subject") and not rec["subject"]:
            rec["subject"] = m["subject"]

    out = []
    for tid, rec in threads.items():
        msgs = sorted(rec["messages"].values(), key=lambda m: parse_dt(m["date"]))
        listed = len(msgs)
        count = msg_count.get(tid, listed)
        disc = discounted_sends()
        own = [m for m in msgs if me_addr in (m.get("sender") or "").lower() and m["id"] not in disc]
        others = [m for m in msgs if me_addr not in (m.get("sender") or "").lower()]
        out.append({
            "thread": tid, "subject": rec["subject"], "labels": sorted(rec["labels"]),
            "message_count": count, "listed": listed,
            "hidden": max(0, count - listed),              # drafts or trashed messages the connector omits
            "complete": rec["complete"] or count == listed,
            "live_draft": tid in drafts_threads,
            "sends": [{"id": m["id"], "date": m["date"], "to": [a.lower() for a in m.get("toRecipients", [])],
                       "cc": [a.lower() for a in m.get("ccRecipients", [])],
                       "bcc": [a.lower() for a in m.get("bccRecipients", [])],
                       "subject": m.get("subject") or (bodies.get(m["id"]) or {}).get("subject"),
                       "body": (bodies.get(m["id"]) or {}).get("plaintextBody")} for m in own],
            "others": [{"id": m["id"], "sender": m.get("sender"), "date": m["date"],
                        "subject": m.get("subject") or (bodies.get(m["id"]) or {}).get("subject")} for m in others],
            "newest": msgs[-1]["id"] if msgs else None,
            "newest_is_own": bool(msgs) and me_addr in (msgs[-1].get("sender") or "").lower(),
        })
    return {"generated": now_utc().isoformat(), "fire": fdir.name, "drafts_threads": sorted(drafts_threads),
            "threads": out}


# ---------------------------------------------------------------- the plan
def plan_rows(gather, cfg, fs, *, now=None, as_of=None, ignore_window=False, ignore_labels=False, ignore_drafts=False):
    me_addr = me(cfg)
    by_thread, bounce_name, known_addresses = contacted_index()
    stop_labels = {cfg["stage_labels"].get(k) for k in ("replied", "closed", "attention", "hold")} - {None}
    bounced = {a.lower() for a in cfg.get("hard_bounces", {})} | {a.lower() for a in cfg.get("cleanup_departed", {})}
    gap = int(cfg.get("sequence_gap_days", 7))
    need = int(cfg.get("sequence_length", 3))
    enabled = {str(x) for x in fs.get("enabled_emails", [])}
    start_h, start_m = map(int, fs["send_local_time"].split(":"))
    end_h, end_m = map(int, fs["send_window_end"].split(":"))
    hubspot = fs.get("hubspot_bcc")
    bodies = {2: copy_body(2), 3: copy_body(3)}
    now = now or now_utc()
    rows, needs = [], []

    for t in gather["threads"]:
        tid = t["thread"]
        row = by_thread.get(tid)
        r = {"thread": tid, "org": (row or {}).get("org"), "state": (row or {}).get("state"),
             "subject": t.get("subject"), "own_count": len(t["sends"]), "action": None, "reason": None}
        rows.append(r)

        def stop(action, reason):
            r["action"], r["reason"] = action, reason

        zone, zsrc = org_zone(row, fs)
        r["tz"] = zone
        # cut the thread at the as-of instant (history replay) so later messages do not exist yet
        sends, others = t["sends"], t["others"]
        if as_of:
            cutoff_local = datetime.datetime.combine(as_of, datetime.time(start_h, start_m), tzinfo=ZoneInfo(zone or "America/Denver"))
            sends = [s for s in sends if parse_dt(s["date"]) <= cutoff_local]
            others = [o for o in others if parse_dt(o["date"]) <= cutoff_local]
            later = [s for s in t["sends"] if parse_dt(s["date"]) > cutoff_local]
            r["chris_next_send"] = later[0]["date"] if later else None
            r["chris_next_to"] = [a for a in later[0]["to"] if a != me_addr] if later else None
            r["chris_next_cc"] = [a for a in later[0]["cc"] if a != me_addr] if later else None
            newest_is_own = bool(sends or others) and (not others or (sends and parse_dt(sends[-1]["date"]) > parse_dt(others[-1]["date"])))
        else:
            newest_is_own = t["newest_is_own"]

        if not ignore_drafts and t["live_draft"]:
            stop("skip", "live draft on thread (Chris's)"); continue
        n = len(sends)
        if n == 0:
            stop("skip", "not ours (no own message)"); continue
        if n >= need:
            stop("skip", "stage complete (3 of 3 sent)"); continue
        email_no = n + 1
        r["email_no"] = email_no
        auto_over = fs.get("auto_reply_overrides", {}) or {}   # {message_id: why} -- Chris's ruling that a message is an auto-reply
        kinds = {o["id"]: ("auto" if o["id"] in auto_over else other_kind(o)) for o in others}
        humans = [o for o in others if kinds[o["id"]] == "human"]
        unknown = [o for o in others if kinds[o["id"]] == "unknown"]
        if humans:
            stop("hold", "human message on thread (" + ", ".join(sorted({(o.get("sender") or "?") for o in humans})) + ") -- a reply stops the sequence; nightly classifies ★/X"); continue
        if unknown and as_of:
            stop("hold", "non-own message with no subject in the replay gather -- treated as a reply"); continue
        if unknown:
            for o in unknown:
                needs.append(("get_message_minimal", o["id"]))
            stop("needs", "non-own message needs its subject (auto-reply vs human)"); continue
        subject_ok = bool(fs.get("zapier", {}).get("subject_param_honored"))
        if not newest_is_own:
            # the newest message is a DSN or an auto-reply (humans were caught above). Zapier attaches the reply to it
            # and would inherit ITS subject -- allowed only when the explicit subject param is proven to win.
            if not subject_ok:
                stop("hold", "bounce / auto-reply is the newest message and the subject parameter is not proven -- nightly drafts it"); continue
            r["replying_over"] = kinds.get(t.get("newest"), "non-own")
        last_own_dt = parse_dt(sends[-1]["date"])
        fresh_dsn = [o for o in others if kinds[o["id"]] == "dsn" and parse_dt(o["date"]) > last_own_dt]
        if fresh_dsn:
            # a bounce AFTER the last send: the R2 repair (drop + parenthetical) needs the address in config first
            prev_rcpts = {a for a in sends[-1]["to"] + sends[-1]["cc"]}
            if not (prev_rcpts & bounced):
                stop("hold", "a bounce (DSN) arrived after the last send but none of its recipients is in config.hard_bounces / cleanup_departed yet -- the nightly records it first (R2)"); continue
        if not ignore_drafts and t["hidden"] > 0 and not t["complete"]:
            needs.append(("get_thread", tid)); stop("needs", "thread not read in full"); continue
        if not ignore_drafts and t["hidden"] > 0:
            stop("hold", f"{t['hidden']} hidden message(s) on thread (trashed draft?) -- a Zapier reply would attach to it; Chris: delete forever"); continue
        if not ignore_labels and stop_labels & set(t["labels"]):
            stop("skip", "stop label present: " + ", ".join(sorted(stop_labels & set(t["labels"])))); continue
        if not zone:
            stop("hold", zsrc); continue
        Z = ZoneInfo(zone)
        last = parse_dt(sends[-1]["date"]).astimezone(Z)
        today_local = (as_of or now.astimezone(Z).date())
        due = roll_forward(last.date() + datetime.timedelta(days=gap), fs)
        r["last_sent"], r["due"] = last.date().isoformat(), due.isoformat()
        if not as_of and last.date() == today_local:
            stop("skip", f"already sent today (own message at {last.strftime('%H:%M')} {zone})"); continue
        if today_local < due:
            stop("skip", f"not due until {due.isoformat()}"); continue
        if not is_business_day(today_local, fs):
            stop("skip", "not a business day"); continue
        local_now = now.astimezone(Z)
        r["local_now"] = local_now.strftime("%H:%M")
        if not ignore_window and not as_of:
            lo = local_now.replace(hour=start_h, minute=start_m, second=0, microsecond=0)
            hi = local_now.replace(hour=end_h, minute=end_m, second=0, microsecond=0)
            if not (lo <= local_now < hi):
                stop("skip", f"not in window ({fs['send_local_time']}-{fs['send_window_end']} {zone}; local now {r['local_now']})"); continue
        prev = sends[-1]
        to = [a for a in prev["to"] if a != me_addr]
        cc = [a for a in prev["cc"] if a != me_addr]
        dropped = [a for a in to + cc if a in bounced]
        if any(a in bounced for a in to):
            stop("hold", "To recipient bounced/departed -- who leads is Chris's call (R2)"); continue
        cc = [a for a in cc if a not in bounced]
        if not to:
            stop("hold", "no To recipient on previous email"); continue
        unknown = [a for a in to + cc if a not in known_addresses]
        if unknown:
            stop("hold", "recipient not in Ledger B (contacted.jsonl): " + ", ".join(unknown) + " -- gather corrupted or ledger behind; never send to an unverified address"); continue
        r["to"], r["cc"], r["dropped"] = to, cc, dropped
        if prev.get("body") is None:
            needs.append(("get_message", prev["id"])); stop("needs", "previous email body not fetched (greeting)"); continue
        first_line = next((l for l in prev["body"].splitlines() if l.strip()), "")
        names, problem = greeting_names(first_line)
        if problem:
            stop("hold", problem); continue
        dropped_first = [bounce_name.get(a) for a in dropped]
        if dropped and any(x is None for x in dropped_first):
            r["note"] = "a bounced generic inbox was dropped without a parenthetical (no name to carry)"
        dropped_first = [x for x in dropped_first if x]
        names = [nm for nm in names if nm.lower() not in {x.lower() for x in dropped_first}]
        if not names:
            stop("hold", "no greeting name left after dropping bounced recipients"); continue
        greeting = f"Hey {join_names(names)},"
        paren = parenthetical_for(dropped_first)
        body_md, links = bodies[email_no]
        body_html = render_html(body_md, greeting, paren, links)
        params = {"thread_id": tid, "to": to, "cc": cc, "bcc": [hubspot] if hubspot else [],
                  "body_type": "html", "body": body_html, "signature": "{{SIGNATURE}}",
                  "signature_delimiter": False, "label_ids": list(fs["zapier"].get("label_ids", ["Label_2"]))}
        if prev.get("subject"):
            params["subject"] = prev["subject"]          # the thread's own subject, never an inherited DSN/auto-reply one
        elif not newest_is_own:
            stop("hold", "previous email's subject unknown -- cannot reply over a bounce/auto-reply without it"); continue
        if email_no == 3:
            params["file"] = ["{{KIT_FILE}}"]
        r.update({"greeting": greeting, "parenthetical": paren, "previous_message_id": prev["id"],
                  "params": params})
        stop("armable" if str(email_no) in enabled else "would-send", "all rules pass -- awaiting the --arm fresh read")
    return rows, needs


def summarize(rows):
    c = {}
    for r in rows:
        c[r["action"]] = c.get(r["action"], 0) + 1
    return c


# ---------------------------------------------------------------- commands
def cmd_queries(args):
    cfg, fs = cfg_block()
    d = fire_dir(args)
    now = now_utc()
    live, stale = in_flight(d, fs, now)
    if live:
        s = live[0]
        print(f"FAIL CLOSED: fire {s['fire']} is in flight (queries.json at {s['started'].strftime('%H:%M:%S')}Z, no followup_sends.json yet) -- "
              f"another session holds the sender. NOTHING IS SENT BY THIS FIRE. Do not run --plan; report 'yielded to fire {s['fire']}' and stop.")
        sys.exit(1)
    for s in stale:
        print(f"NOTE: fire {s['fire']} started {s['started'].strftime('%H:%M')}Z and never verified -- older than {lock_minutes(fs)} min, treated as crashed")
    d = fire_dir(args, create=True)
    jdump(d / "queries.json", {"fire": d.name, "generated": now.isoformat(), "due_search": fs["due_search"], "lock": True})
    # second look, for a fire that started in the same instant (a race): the later-started fire yields
    live, _ = in_flight(d, fs, now_utc())
    losers = [s for s in live if (s["started"], s["fire"]) < (now, d.name)]
    if losers:
        s = losers[0]
        jdump(d / "queries.json", {"fire": d.name, "generated": now.isoformat(), "due_search": fs["due_search"], "lock": False,
                                   "aborted": True, "yielded_to": s["fire"]})
        print(f"FAIL CLOSED: fire {s['fire']} started at the same moment and holds the sender -- this fire yields. NOTHING IS SENT BY THIS FIRE. "
              f"Do not run --plan; report 'yielded to fire {s['fire']}' and stop.")
        sys.exit(1)
    print(f"FIRE {d.name} -- save every tool result VERBATIM under {d / 'raw'}/")
    print(f"Q1  search_threads  query: {fs['due_search']}")
    print("    view: THREAD_VIEW_METADATA_ONLY  pageSize: 50  -> raw/search_1.json, raw/search_2.json ... (follow nextPageToken until absent)")
    print("Q2  list_drafts  (no query -- D-SWEEP, unfiltered)  view: DRAFT_VIEW_METADATA_ONLY  pageSize: 50  -> raw/drafts_1.json, raw/drafts_2.json ...")
    print(f"THEN  python3 bin/followup_send.py --plan --fire {d.name}")


def fail_closed(d, name, reason, extra=None):
    doc = {"fire": d.name, "generated": now_utc().isoformat(), "failed_closed": reason, "rows": []}
    if extra:
        doc.update(extra)
    jdump(d / name, doc)
    print(f"FAIL CLOSED: {reason}. Nothing is sent by this fire.")
    sys.exit(1)


def guard_fire(d, fs, now, stage):
    """The lock and the transcript check, repeated at --plan and --arm. Exits 1 on failure."""
    q = d / "queries.json"
    if not q.exists():
        sys.exit(f"no queries.json under {d} -- --queries did not run (or failed closed); nothing to {stage}")
    qd = jload(q)
    if qd.get("aborted"):
        fail_closed(d, f"{stage}.json", f"this fire yielded to fire {qd.get('yielded_to')} at --queries")
    live, _ = in_flight(d, fs, now)
    if live:
        s = live[0]
        fail_closed(d, f"{stage}.json", f"fire {s['fire']} is in flight (started {s['started'].strftime('%H:%M:%S')}Z, not verified)")
    viol = validate_raw(d)
    if viol:
        print("\n".join("  " + x for x in viol[:12]) + ("" if len(viol) <= 12 else f"\n  ... {len(viol) - 12} more"))
        fail_closed(d, f"{stage}.json", f"raw transcript failed structural validation ({len(viol)} violation(s)) -- re-save the reads VERBATIM and run --plan again",
                    {"violations": viol})


def cmd_plan(args):
    cfg, fs = cfg_block()
    d = fire_dir(args)
    if not (d / "raw").exists():
        sys.exit(f"no raw/ under {d} -- run --queries first and save its reads")
    now = now_utc()
    guard_fire(d, fs, now, "plan")
    today_et = now.astimezone(ET).date()
    last, covered, days_left = holiday_coverage(fs, today_et)
    if not covered:
        jdump(d / "plan.json", {"fire": d.name, "failed_closed": f"never_send_dates ends {last}; today {today_et} is not covered", "rows": []})
        print(f"FAIL CLOSED: config.followup_sender.never_send_dates ends {last} -- refresh it. Nothing is sent."); sys.exit(1)
    gather = ingest(d, me(cfg))
    jdump(d / "gather.json", gather)
    rows, needs = plan_rows(gather, cfg, fs, now=now)
    if needs:
        print(f"NEEDS {len(needs)} more read(s) -- save each VERBATIM, then run --plan again:")
        for kind, ident in sorted(set(needs)):
            if kind == "get_thread":
                print(f"  get_thread  threadId={ident}  messageFormat=METADATA_ONLY  -> raw/thread_{ident}.json")
            elif kind == "get_message_minimal":
                print(f"  get_message messageId={ident}  messageFormat=MINIMAL      -> raw/message_{ident}.json")
            else:
                print(f"  get_message messageId={ident}  messageFormat=PLAIN_TEXT   -> raw/message_{ident}.json")
        jdump(d / "plan.json", {"fire": d.name, "incomplete": True, "needs": needs, "rows": rows})
        sys.exit(3)
    for r in rows:
        r.pop("params", None)                 # NO params in plan.json -- only --arm writes them (armed.json)
    plan = {"fire": d.name, "generated": now.isoformat(), "enabled_emails": fs.get("enabled_emails", []),
            "holiday_list_ends": last.isoformat() if last else None, "summary": summarize(rows), "rows": rows}
    jdump(d / "plan.json", plan)
    print(f"PLAN {d.name}: " + " · ".join(f"{k} {v}" for k, v in sorted(plan["summary"].items())) + f" · threads {len(rows)}")
    for r in rows:
        tag = r["action"].upper()
        who = r.get("org") or r["thread"]
        if r["action"] in ("armable", "would-send"):
            print(f"  {tag:10} Email {r['email_no']} · {who} · to {', '.join(r['to'])}" + (f" · cc {', '.join(r['cc'])}" if r["cc"] else "")
                  + f" · {r['greeting']}" + (" · " + r["parenthetical"] if r.get("parenthetical") else "") + f" · local {r['local_now']} {r['tz']}")
        else:
            print(f"  {tag:10} {who} -- {r['reason']}")
    armable = [r for r in rows if r["action"] == "armable"]
    if armable:
        print(f"\nNOTHING IS SENDABLE YET. {len(armable)} ARMABLE row(s) need the fresh read: python3 bin/followup_send.py --arm --fire {d.name}")
    else:
        print(f"\nNothing to send this fire. Then: python3 bin/followup_send.py --verify --fire {d.name}")
    sys.exit(0 if not any(r["action"] == "hold" for r in rows) else 2)


def cmd_arm(args):
    """The fresh read before the send. Pass 1 prints the reads; pass 2 arms or drops each row."""
    cfg, fs = cfg_block()
    d = fire_dir(args)
    now = now_utc()
    if not (d / "plan.json").exists():
        sys.exit("no plan.json -- run --plan first")
    plan = jload(d / "plan.json")
    if plan.get("incomplete") or plan.get("failed_closed"):
        sys.exit("plan.json is incomplete or failed closed -- run --plan until it completes")
    guard_fire(d, fs, now, "armed")
    gather = ingest(d, me(cfg))
    rows, needs = plan_rows(gather, cfg, fs, now=now)
    if needs:
        sys.exit("the gather no longer resolves (new NEEDS) -- run --plan again")
    gth = {t["thread"]: t for t in gather["threads"]}
    raw = d / "raw"
    armable = [r for r in rows if r["action"] == "armable"]
    ttl = arm_ttl(fs)
    missing = []
    for r in armable:
        p = raw / f"arm_thread_{r['thread']}.json"
        if not p.exists():
            missing.append((r["thread"], "missing"))
        elif now.timestamp() - os.path.getmtime(p) > ttl:
            missing.append((r["thread"], f"stale ({int(now.timestamp() - os.path.getmtime(p))} s)"))
    if missing:
        print(f"NEEDS {len(missing)} fresh read(s) -- save each VERBATIM, then run --arm again WITHIN {ttl} s:")
        for tid, why in missing:
            print(f"  get_thread  threadId={tid}  messageFormat=METADATA_ONLY  -> raw/arm_thread_{tid}.json   [{why}]")
        sys.exit(3)
    claimed = claims(d, fs, now)
    out, n_send = [], 0
    for r in rows:
        o = dict(r)
        if r["action"] == "armable":
            p = raw / f"arm_thread_{r['thread']}.json"
            ok, why = arm_gate(r, gth[r["thread"]], jload(p), now.timestamp() - os.path.getmtime(p), now, cfg, fs, claimed)
            o["arm_reason"] = why
            if ok:
                o["action"] = "send"; n_send += 1
            else:
                o["action"] = "dropped"; o["reason"] = why; o.pop("params", None)
        else:
            o.pop("params", None)
        out.append(o)
    armed = {"fire": d.name, "generated": now.isoformat(), "arm_ttl_seconds": ttl, "enabled_emails": fs.get("enabled_emails", []),
             "summary": summarize(out), "rows": out}
    jdump(d / "armed.json", armed)
    print(f"ARMED {d.name}: " + " · ".join(f"{k} {v}" for k, v in sorted(armed["summary"].items())))
    for o in out:
        who = o.get("org") or o["thread"]
        if o["action"] == "send":
            print(f"  SEND       Email {o['email_no']} · {who} · to {', '.join(o['to'])}" + (f" · cc {', '.join(o['cc'])}" if o["cc"] else "")
                  + f" · {o['greeting']} · {o['arm_reason']}")
        elif o["action"] == "dropped":
            print(f"  DROPPED    Email {o.get('email_no')} · {who} -- {o['reason']}")
    if n_send:
        z = fs["zapier"]
        print(f"\nACT NOW ({ttl} s budget): for each row in armed.json with action \"send\" call execute_zapier_write_action selected_api={z['selected_api']} "
              f"action={z['send_action']['action']} tool_name={z['send_action']['tool_name']} with that row's params VERBATIM, after resolving "
              f"{{{{SIGNATURE}}}} and {{{{KIT_FILE}}}} per config.followup_sender.zapier.resolve. Save each response as raw/zapier_<thread>.json. "
              f"Then: python3 bin/followup_send.py --verify --fire {d.name}")
    else:
        print(f"\nNothing armed. Then: python3 bin/followup_send.py --verify --fire {d.name}")
    sys.exit(0 if n_send else 2)


def cmd_verify(args):
    cfg, fs = cfg_block()
    d = fire_dir(args)
    now = now_utc()
    plan = jload(d / "plan.json")
    if plan.get("failed_closed"):
        jdump(d / "followup_sends.json", {"fire": d.name, "generated": now.isoformat(), "failed_closed": plan["failed_closed"],
                                          "summary": {"failed_closed": 1}, "rows": [], "label_calls": [], "findings": []})
        print(f"VERIFY {d.name}: the fire FAILED CLOSED ({plan['failed_closed']}); nothing was sent, nothing to label."); sys.exit(2)
    raw = d / "raw"
    if (d / "armed.json").exists():
        armed = jload(d / "armed.json")
        rows = armed["rows"]
    else:
        if any(r["action"] == "armable" for r in plan["rows"]):
            sys.exit("plan has ARMABLE rows but --arm never ran -- nothing may have been sent; run --arm (then ACT, then --verify)")
        rows = plan["rows"]
    sends = [r for r in rows if r["action"] == "send"]
    needs = []
    for r in sends:
        if not (raw / f"verify_thread_{r['thread']}.json").exists():
            needs.append(f"  get_thread  threadId={r['thread']}  messageFormat=METADATA_ONLY  -> raw/verify_thread_{r['thread']}.json")
    if any(r["email_no"] == 3 for r in sends) and not (raw / "verify_kit.json").exists():
        kit = cfg["draft_writer"]["zapier"]["email_3_attachment"]["filename"]
        needs.append(f"  search_threads  query: in:sent has:attachment filename:{kit} newer_than:1d  view: THREAD_VIEW_METADATA_ONLY  pageSize: 50  -> raw/verify_kit.json")
    if needs:
        print("NEEDS the Sent read-back -- save each VERBATIM, then run --verify again:")
        print("\n".join(needs)); sys.exit(3)
    viol = validate_raw(d)
    findings = [f"TRANSCRIPT: {x}" for x in viol]
    kit_threads = set()
    if (raw / "verify_kit.json").exists():
        kit_threads = {t["id"] for t in jload(raw / "verify_kit.json").get("threads", [])}
    me_addr = me(cfg)
    fire_start = parse_dt(plan["generated"]) - datetime.timedelta(minutes=30)
    armed_threads = {r["thread"] for r in sends}
    for z in sorted(raw.glob("zapier_*.json")):
        tid = z.name[len("zapier_"):-5]
        if tid not in armed_threads:
            findings.append(f"UNARMED SEND: raw/{z.name} exists but thread {tid} was never armed -- the session called Zapier outside the plan")
    out, label_calls = [], []
    for r in rows:
        o = {k: r.get(k) for k in ("thread", "org", "email_no", "action", "reason", "to", "cc", "greeting", "tz", "local_now", "due")}
        if r["action"] == "send":
            t = jload(raw / f"verify_thread_{r['thread']}.json")
            disc = discounted_sends()
            own = sorted([m for m in t.get("messages", []) if me_addr in (m.get("sender") or "").lower() and m["id"] not in disc], key=lambda m: parse_dt(m["date"]))
            new = [m for m in own if parse_dt(m["date"]) >= fire_start]
            Z = ZoneInfo(r["tz"]) if r.get("tz") else ET
            today_local = now.astimezone(Z).date()
            today_own = [m for m in own if parse_dt(m["date"]).astimezone(Z).date() == today_local]
            newest = new[-1] if new else None
            count_ok = len(own) == r["own_count"] + 1 and bool(new)
            if r["email_no"] == 3:
                count_ok = count_ok and r["thread"] in kit_threads
            prm = r.get("params") or {}
            recon = None
            if newest is not None:
                got_to = {a.lower() for a in newest.get("toRecipients", []) or []}
                got_cc = {a.lower() for a in newest.get("ccRecipients", []) or []}
                got_bcc = {a.lower() for a in newest.get("bccRecipients", []) or []}
                want_bcc = {a.lower() for a in prm.get("bcc", []) or []}
                recon = {"to": got_to == set(r["to"]), "cc": got_cc == set(r["cc"]), "bcc": want_bcc <= got_bcc}
                if not all(recon.values()):
                    findings.append(f"SENT-MISMATCH {r['thread']} ({r.get('org')}): sent to={sorted(got_to)} cc={sorted(got_cc)} bcc={sorted(got_bcc)} "
                                    f"vs armed to={r['to']} cc={r['cc']} bcc={sorted(want_bcc)} -- the params were not passed verbatim")
            if len(today_own) > 1:
                o["status"] = "DUPLICATE"
                findings.append(f"DUPLICATE SEND {r['thread']} ({r.get('org')}): {len(today_own)} own messages dated today: " + ", ".join(m["id"] for m in today_own))
            elif not count_ok:
                o["status"] = "UNVERIFIED"
            elif recon is not None and not all(recon.values()):
                o["status"] = "SENT-MISMATCH"
            else:
                o["status"] = "sent"
                step = fs["stage_after_send"][str(r["email_no"])]
                label_calls.append({"thread": r["thread"], "unlabel_thread": [step["remove"]], "label_thread": [step["add"]]})
            o["sent_message_id"] = newest["id"] if newest else None
            o["sent_at"] = newest["date"] if newest else None
            o["reconciled"] = recon
        else:
            o["status"] = r["action"]
        out.append(o)
    result = {"fire": d.name, "generated": now.isoformat(), "enabled_emails": plan.get("enabled_emails", []),
              "summary": {s_: sum(1 for x in out if x["status"] == s_) for s_ in sorted({x["status"] for x in out})},
              "rows": out, "label_calls": label_calls, "findings": findings}
    jdump(d / "followup_sends.json", result)
    print(f"VERIFY {d.name}: " + " · ".join(f"{k} {v}" for k, v in result["summary"].items()))
    for o in out:
        who = o.get("org") or o["thread"]
        if o["status"] in ("sent", "UNVERIFIED", "SENT-MISMATCH", "DUPLICATE"):
            print(f"  {o['status']:14} Email {o['email_no']} · {who} · {o.get('sent_at') or '-'}")
        elif o["status"] == "dropped":
            print(f"  {'dropped':14} Email {o.get('email_no')} · {who} -- {o['reason']}")
    if findings:
        print("\n🔴 FINDINGS (report each verbatim):")
        for f_ in findings:
            print("  " + f_)
    if label_calls:
        print("\nLABELS -- apply with the native Gmail tools, in this order per thread:")
        for c in label_calls:
            print(f"  unlabel_thread threadId={c['thread']} labelIds={c['unlabel_thread']}  then  label_thread threadId={c['thread']} labelIds={c['label_thread']}")
    print(f"\nREPORT: one line per row above, then the link computer://{d / 'followup_sends.json'}")
    bad = any(o["status"] in ("UNVERIFIED", "SENT-MISMATCH", "DUPLICATE") for o in out) or bool(findings)
    sys.exit(0 if not bad else 2)


def cmd_report_yesterday(args):
    cfg, fs = cfg_block()
    y = datetime.date.fromisoformat(args.today) if args.today else now_utc().astimezone(ET).date()
    y = y - datetime.timedelta(days=1)
    files = sorted(glob.glob(str(RUNS / y.isoformat() / "sender" / "*" / "followup_sends.json")))
    shadow = not fs.get("enabled_emails")
    if not is_business_day(y, fs):
        print(f"Sender: {y} was not a business day -- no fires expected · fires {len(files)}"); return
    sent = {2: 0, 3: 0}; would = {2: 0, 3: 0}; held, skipped, unv, dropped, bad = [], 0, 0, [], []
    findings = []
    started = len(glob.glob(str(RUNS / y.isoformat() / "sender" / "*" / "queries.json")))
    for f in files:
        doc = jload(f)
        findings += [f"{pathlib.Path(f).parent.name}: {x}" for x in doc.get("findings", [])]
        if doc.get("failed_closed"):
            findings.append(f"{pathlib.Path(f).parent.name}: FAILED CLOSED -- {doc['failed_closed']}")
        for o in doc["rows"]:
            if o["status"] == "sent":
                sent[o["email_no"]] += 1
            elif o["status"] == "would-send":
                would[o["email_no"]] += 1
            elif o["status"] == "hold":
                held.append(f"{o.get('org') or o['thread']}: {o['reason']}")
            elif o["status"] == "UNVERIFIED":
                unv += 1
            elif o["status"] == "dropped":
                dropped.append(f"{o.get('org') or o['thread']}: {o['reason']}")
            elif o["status"] in ("SENT-MISMATCH", "DUPLICATE"):
                bad.append(f"{o['status']} {o.get('org') or o['thread']}")
            else:
                skipped += 1
    # DUPLICATE-SEND AUDIT across every thread read back yesterday: two own messages on one UTC day = 🔴
    me_addr = me(cfg)
    seen = {}
    for p in glob.glob(str(RUNS / y.isoformat() / "sender" / "*" / "raw" / "*thread_*.json")):
        try:
            t = jload(p)
        except Exception:
            continue
        for m in t.get("messages", []):
            if me_addr in (m.get("sender") or "").lower():
                try:
                    day = parse_dt(m["date"]).date().isoformat()
                except Exception:
                    continue
                seen.setdefault((t.get("id"), day), set()).add(m["id"])
    dups = sorted(f"{tid} ({day}: {len(ids)} own)" for (tid, day), ids in seen.items() if len(ids) > 1 and day == y.isoformat())
    if dups:
        findings.append("DUPLICATE SEND AUDIT: " + "; ".join(dups))
    held_txt = "; ".join(sorted(set(held))) or "none"
    drop_txt = "; ".join(sorted(set(dropped))) or "none"
    fires_txt = f"fires {len(files)}/4" + (f" (started {started})" if started != len(files) else "") + ("" if len(files) >= 4 else " 🔴 fires missing")
    flag = (" 🔴 " + " · ".join(bad)) if bad else ""
    if shadow:
        print(f"Sender (shadow): yesterday would-send {would[2]} Email 2 · {would[3]} Email 3 · held {len(held)} [{held_txt}] · skipped {skipped} · {fires_txt}")
    else:
        print(f"Sender: yesterday {sent[2]} Email 2 · {sent[3]} Email 3 sent by the machine · {unv} UNVERIFIED · dropped at arm {len(dropped)} [{drop_txt}] · held {len(held)} [{held_txt}] · skipped {skipped} · {fires_txt}{flag}")
    for x in findings:
        print(f"  🔴 {x}")


def cmd_preview(args):
    cfg, fs = cfg_block()
    today = datetime.date.fromisoformat(args.today) if args.today else now_utc().astimezone(ET).date()
    last, covered, days_left = holiday_coverage(fs, today)
    warn = fs.get("holiday_coverage_warn_days", 60)
    hol = f"Holiday list ends {last}" + ("" if days_left >= warn else " 🔴 REFRESH config.followup_sender.never_send_dates")
    d = fire_dir(args) if args.fire else latest_fire_dir(days_back=3)
    if not d or not (d / "raw").exists():
        print(f"Scheduled follow-ups: no sender gather found (today or the last 3 days) · {hol}"); return
    gather = ingest(d, me(cfg))
    rows, needs = plan_rows(gather, cfg, fs, now=datetime.datetime.combine(today, datetime.time(12, 0), tzinfo=UTC), ignore_window=True)
    due = [r for r in rows if r["action"] in ("armable", "would-send") or (r["action"] == "needs")]
    by_zone = {}
    for r in due:
        z = {"America/New_York": "ET", "America/Chicago": "CT", "America/Denver": "MT", "America/Los_Angeles": "PT"}.get(r.get("tz"), r.get("tz") or "?")
        by_zone[z] = by_zone.get(z, 0) + 1
    hold_lbl = cfg["stage_labels"].get("hold")
    held = sum(1 for t in gather["threads"] if hold_lbl in t["labels"])
    print(f"Scheduled follow-ups: {len(due)} today (" + " · ".join(f"{k} {v}" for k, v in sorted(by_zone.items())) + f") · {held} held ⏸ · {hol}   ← from {d.name} gather of {gather['generated'][:10]}; the sender re-checks each thread at 8:30 local")
    for r in due:
        print(f"  Email {r.get('email_no')} · {r.get('org') or r['thread']} · {r.get('state')} · due {r.get('due')} · to {', '.join(r.get('to') or [])}")


def cmd_as_of(args):
    """History replay. The gather folder must hold full thread histories (search pages + thread reads)."""
    cfg, fs = cfg_block()
    d = fire_dir(args)
    as_of = datetime.date.fromisoformat(args.as_of)
    gather = ingest(d, me(cfg))
    rows, needs = plan_rows(gather, cfg, fs, now=datetime.datetime.combine(as_of, datetime.time(14, 45), tzinfo=UTC),
                            as_of=as_of, ignore_window=True, ignore_labels=True, ignore_drafts=True)
    # body-less rows: the greeting cannot be checked in replay; treat 'needs' as would-send for the decision test
    for r in rows:
        if r["action"] == "needs":
            r["action"] = "would-send"; r["reason"] = "decision only (body not fetched)"
        elif r["action"] == "armable":
            r["action"] = "send"
    out = {"as_of": as_of.isoformat(), "rows": [], "summary": {}}
    for r in rows:
        if r["action"] not in ("send", "would-send", "hold"):
            continue
        rec = {k: r.get(k) for k in ("thread", "org", "state", "email_no", "action", "reason", "due", "last_sent", "chris_next_send")}
        if r["action"] in ("send", "would-send"):
            if r.get("chris_next_send"):
                lat = (parse_dt(r["chris_next_send"]).date() - as_of).days
                rec["chris_latency_days"] = lat
                rec["recipients_match"] = (sorted(r.get("to") or []) == sorted(r.get("chris_next_to") or [])
                                           and sorted(r.get("cc") or []) == sorted(r.get("chris_next_cc") or []))
                if not rec["recipients_match"]:
                    rec["machine_to_cc"] = [r.get("to"), r.get("cc")]
                    rec["chris_to_cc"] = [r.get("chris_next_to"), r.get("chris_next_cc")]
            else:
                rec["chris_latency_days"] = None
        out["rows"].append(rec)
    ws_rows = [x for x in out["rows"] if x["action"] in ("send", "would-send")]
    out["summary"] = {"would_send": len(ws_rows), "hold": sum(1 for x in out["rows"] if x["action"] == "hold"),
                      "recipients_match": sum(1 for x in ws_rows if x.get("recipients_match") is True),
                      "recipients_differ": sum(1 for x in ws_rows if x.get("recipients_match") is False),
                      "chris_sent_later": sum(1 for x in ws_rows if x["chris_latency_days"] is not None),
                      "chris_never_sent_yet": sum(1 for x in ws_rows if x["chris_latency_days"] is None),
                      "median_latency_days": sorted(x["chris_latency_days"] for x in ws_rows if x["chris_latency_days"] is not None)[len([x for x in ws_rows if x["chris_latency_days"] is not None]) // 2] if any(x["chris_latency_days"] is not None for x in ws_rows) else None}
    jdump(d / f"replay_{as_of.isoformat()}.json", out)
    print(f"AS-OF {as_of}: would-send {out['summary']['would_send']} · hold {out['summary']['hold']} · Chris sent later {out['summary']['chris_sent_later']} (median {out['summary']['median_latency_days']} d) · never sent {out['summary']['chris_never_sent_yet']}")


# ---------------------------------------------------------------- self-test
def cmd_selftest(args):
    cfg, fs = cfg_block()
    fs = dict(fs); fs["enabled_emails"] = ["2", "3"]
    me_addr = me(cfg)
    bad = 0
    def mk(sends, others=(), labels=(), live_draft=False, hidden=0):
        msgs = sorted(list(sends) + list(others), key=lambda m: parse_dt(m["date"]))
        return {"thread": "1a0cda2aaddc2259", "subject": "Question about PD/Training at X . . .", "labels": list(labels),
                "message_count": len(msgs) + hidden, "listed": len(msgs), "hidden": hidden, "complete": True, "live_draft": live_draft,
                "sends": list(sends), "others": list(others), "newest": msgs[-1]["id"],
                "newest_is_own": me_addr in msgs[-1]["sender"]}
    def own(i, date, to=("person0962@org0123.example",), cc=("person0984@org0123.example", "person0797@org0123.example"), body="Nita, Patsy, and Lisette,\n\nMy name is Chris"):
        return {"id": f"m{i}", "date": date, "to": list(to), "cc": list(cc), "bcc": [], "body": body, "sender": me_addr,
                "subject": "Question about PD/Training at X . . ."}
    def other(i, date, sender="person1145@org0123.example"):
        return {"id": f"o{i}", "date": date, "sender": sender}
    def run(gather_threads, now, **kw):
        rows, needs = plan_rows({"threads": gather_threads}, cfg, fs, now=now, **kw)
        return rows[0]
    def check(name, row, action, reason_part=""):
        nonlocal bad
        ok = row["action"] == action and reason_part.lower() in (row["reason"] or "").lower()
        bad += 0 if ok else 1
        print(("PASS " if ok else "FAIL ") + f"{name}: {row['action']} -- {row['reason']}")
    # [Org 0156] is CA (PT). E1 sent Wed 2026-09-23 16:44Z. Due Wed 2026-09-30.
    base = own(1, "2026-09-23T16:44:00Z")
    pt = ZoneInfo("America/Los_Angeles")
    t = lambda d, h, m: datetime.datetime(*d, h, m, tzinfo=pt).astimezone(UTC)
    check("in window, due", run([mk([base])], t((2026, 9, 30), 8, 45)), "armable")
    r = run([mk([base])], t((2026, 9, 30), 8, 45)); print("      greeting:", r["greeting"], "| bcc:", r["params"]["bcc"], "| body starts:", r["params"]["body"][:60].replace("\n", " "))
    check("too early", run([mk([base])], t((2026, 9, 30), 8, 10)), "skip", "not in window")
    check("too late", run([mk([base])], t((2026, 9, 30), 10, 5)), "skip", "not in window")
    check("not due yet", run([mk([base])], t((2026, 9, 29), 8, 45)), "skip", "not due")
    check("weekend roll: sent Fri 09-25 -> due Fri 10-02 (Sat 10-03 no)", run([mk([own(1, "2026-09-25T16:00:00Z")])], t((2026, 10, 3), 8, 45)), "skip", "not a business day")
    check("holiday roll: sent Mon 10-05 -> due Mon 10-12 is Columbus Day -> Tue 10-13", run([mk([own(1, "2026-10-05T16:00:00Z")])], t((2026, 10, 12), 8, 45)), "skip", "not due until 2026-10-13")
    check("holiday roll resolves next day", run([mk([own(1, "2026-10-05T16:00:00Z")])], t((2026, 10, 13), 8, 45)), "armable")
    check("idempotency: 2 own -> Email 3", run([mk([base, own(2, "2026-09-30T15:40:00Z", body="Hey [Person 0510], Patsy, and Lisette,\n\nIs it worth")])], t((2026, 10, 7), 8, 45)), "armable")
    r = run([mk([base, own(2, "2026-09-30T15:40:00Z", body="Hey [Person 0510], Patsy, and Lisette,\n\nIs it worth")])], t((2026, 10, 7), 8, 45)); print("      email_no:", r["email_no"], "| file:", r["params"].get("file"), "| bolds:", r["params"]["body"].count("<b>"))
    check("idempotency: 3 own -> complete", run([mk([base, own(2, "2026-09-30T15:40:00Z"), own(3, "2026-10-07T15:40:00Z")])], t((2026, 10, 14), 8, 45)), "skip", "stage complete")
    check("unknown-kind message newest -> needs subject", run([mk([base], [other(1, "2026-09-28T12:00:00Z")])], t((2026, 9, 30), 8, 45)), "needs", "subject")
    hreply = {"id": "o1", "date": "2026-09-28T12:00:00Z", "sender": "person1145@org0123.example", "subject": "Re: Question about PD/Training at X . . ."}
    check("human reply newest -> hold", run([mk([base], [hreply])], t((2026, 9, 30), 8, 45)), "hold", "human message")
    anew = {"id": "o2", "date": "2026-09-23T16:45:00Z", "sender": "person0962@org0123.example", "subject": "Automatic reply: Question about PD/Training at X . . ."}
    r = run([mk([base], [anew])], t((2026, 9, 30), 8, 45))
    check("auto-reply newest, subject param proven -> send with explicit subject", r, "armable"); print("      subject param:", r["params"].get("subject"), "| replying_over:", r.get("replying_over"))
    fs_off = dict(fs); fs_off["zapier"] = dict(fs["zapier"]); fs_off["zapier"]["subject_param_honored"] = False
    rows_off, _ = plan_rows({"threads": [mk([base], [anew])]}, cfg, fs_off, now=t((2026, 9, 30), 8, 45))
    check("auto-reply newest, subject param NOT proven -> hold", rows_off[0], "hold", "subject parameter")
    dnew = {"id": "o3", "date": "2026-09-23T16:45:00Z", "sender": "mailer-daemon@googlemail.com", "subject": "Delivery Status Notification (Failure)"}
    check("DSN newest, bounce not yet in config -> hold", run([mk([base], [dnew])], t((2026, 9, 30), 8, 45)), "hold", "hard_bounces")
    # a human replied, Chris wrote back (own is newest) -> the sequence is over, never send a cold follow-up into a conversation
    hr = {"id": "o9", "date": "2026-09-25T12:00:00Z", "sender": "person1145@org0123.example", "subject": "Re: Question about PD/Training at X . . ."}
    check("human reply earlier, Chris replied after -> hold", run([mk([base, own(2, "2026-09-26T12:00:00Z", body="Hey [Person 0510],\n\nThanks")], [hr])], t((2026, 10, 7), 8, 45)), "hold", "human message")
    ar = {"id": "o8", "date": "2026-09-23T17:00:00Z", "sender": "person0984@org0123.example", "subject": "Automatic reply: Question about PD/Training at X . . ."}
    check("auto-reply earlier (not newest) -> proceeds", run([mk([own(1, "2026-09-23T16:44:00Z"), own(2, "2026-09-30T16:00:00Z", body="Hey [Person 0510], Patsy, and Lisette,\n\nIs it")], [ar])], t((2026, 10, 7), 8, 45)), "armable")
    dsn = {"id": "o7", "date": "2026-09-23T16:45:00Z", "sender": "mailer-daemon@googlemail.com", "subject": "Delivery Status Notification (Failure)"}
    check("DSN earlier (not newest) -> proceeds", run([mk([own(1, "2026-09-23T16:44:00Z"), own(2, "2026-09-30T16:00:00Z", body="Hey [Person 0510], Patsy, and Lisette,\n\nIs it")], [dsn])], t((2026, 10, 7), 8, 45)), "armable")
    unk = {"id": "o6", "date": "2026-09-23T17:00:00Z", "sender": "person0984@org0123.example"}
    check("non-own message without subject -> needs its subject", run([mk([own(1, "2026-09-23T16:44:00Z"), own(2, "2026-09-30T16:00:00Z")], [unk])], t((2026, 10, 7), 8, 45)), "needs", "subject")
    check("live draft -> skip", run([mk([base], live_draft=True)], t((2026, 9, 30), 8, 45)), "skip", "live draft")
    check("hidden trashed draft -> hold", run([mk([base], hidden=1)], t((2026, 9, 30), 8, 45)), "hold", "hidden")
    check("hold label -> skip", run([mk([base], labels=[cfg["stage_labels"]["hold"]])], t((2026, 9, 30), 8, 45)), "skip", "stop label")
    check("star label -> skip", run([mk([base], labels=["Label_12"])], t((2026, 9, 30), 8, 45)), "skip", "stop label")
    # bounced Cc -> dropped + parenthetical (use a real hard_bounces address with a Ledger B name)
    _, bn, _known = contacted_index()
    addr, nm = next(iter(bn.items()))
    r = run([mk([own(1, "2026-09-23T16:44:00Z", to=("person0962@org0123.example",), cc=(addr, "person0797@org0123.example"), body=f"Nita, {nm}, and Lisette,\n\nMy name")])], t((2026, 9, 30), 8, 45))
    check(f"bounced Cc {addr} ({nm}) dropped", r, "armable"); print("      greeting:", r["greeting"], "|", r["parenthetical"], "| cc:", r["cc"])
    dsn2 = {"id": "o4", "date": "2026-09-23T16:45:00Z", "sender": "mailer-daemon@googlemail.com", "subject": "Delivery Status Notification (Failure)"}
    r = run([mk([own(1, "2026-09-23T16:44:00Z", to=("person0962@org0123.example",), cc=(addr, "person0797@org0123.example"), body=f"Nita, {nm}, and Lisette,\n\nMy name")], [dsn2])], t((2026, 9, 30), 8, 45))
    check("DSN newest, bounce IS in config -> send over it with the drop", r, "armable"); print("      cc:", r["cc"], "| subject:", r["params"].get("subject"), "| over:", r.get("replying_over"))
    r = run([mk([own(1, "2026-09-23T16:44:00Z", to=(addr,), cc=("person0797@org0123.example",), body=f"{nm} and Lisette,\n\nMy name")])], t((2026, 9, 30), 8, 45))
    check("bounced To -> hold", r, "hold", "To recipient")
    r = run([mk([own(1, "2026-09-23T16:44:00Z", body="Stacie and team,\n\nMy name")])], t((2026, 9, 30), 8, 45))
    check("team greeting -> armable (2026-10-09 R2)", r, "armable"); print("      greeting:", r.get("greeting"))
    # ---- CAPA 2026-10-06: rule 4b, the lock, claims, the arm gate --------------------------------------
    check("4b already sent today -> skip", run([mk([base, own(2, "2026-09-30T15:40:00Z", body="Hey [Person 0510], Patsy, and Lisette,\n\nIs it")])], t((2026, 9, 30), 9, 0)), "skip", "already sent today")
    import tempfile, shutil
    global RUNS
    keep_runs = RUNS
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="fs-selftest-"))
    try:
        RUNS = tmp
        day = RUNS / "2026-10-06" / "sender"
        A, B = day / "0929ET", day / "0935ET"
        nowt = datetime.datetime(2026, 10, 6, 13, 35, 41, tzinfo=UTC)
        def jd(p, o): jdump(p, o)
        def pr(name, ok):
            nonlocal bad
            bad += 0 if ok else 1
            print(("PASS " if ok else "FAIL ") + name)
        jd(A / "queries.json", {"fire": "0929ET", "generated": "2026-10-06T13:29:31+00:00", "lock": True})
        live, stale = in_flight(B, fs, nowt)
        pr("lock: sibling in flight (6 min old, no verify) blocks", [x["fire"] for x in live] == ["0929ET"] and not stale)
        jd(A / "followup_sends.json", {"rows": []})
        live, stale = in_flight(B, fs, nowt)
        pr("lock: verified sibling releases", not live and not stale)
        jd(day / "0829ET" / "queries.json", {"fire": "0829ET", "generated": "2026-10-06T12:33:57+00:00", "lock": True})
        live, stale = in_flight(B, fs, nowt)
        pr("lock: 62-min-old unverified sibling is stale, not live", not live and [x["fire"] for x in stale] == ["0829ET"])
        jd(day / "0931ET" / "queries.json", {"fire": "0931ET", "generated": "2026-10-06T13:31:00+00:00", "aborted": True, "yielded_to": "0929ET"})
        live, stale = in_flight(B, fs, nowt)
        pr("lock: an aborted (yielded) sibling never blocks", not live)
        # claims: a live sibling's armable/send threads are off limits
        C = day / "0933ET"
        jd(C / "queries.json", {"fire": "0933ET", "generated": "2026-10-06T13:33:00+00:00", "lock": True})
        jd(C / "plan.json", {"rows": [{"thread": "1a0cda2aaddc2259", "action": "armable"}, {"thread": "1a0d2d112344fed5", "action": "skip"}]})
        jd(C / "armed.json", {"rows": [{"thread": "1a0e75626ba26f69", "action": "send"}]})
        cl = claims(B, fs, nowt)
        pr("claims: planned + armed threads of a live sibling are claimed, skipped ones are not",
           cl == {"1a0cda2aaddc2259": "0933ET", "1a0e75626ba26f69": "0933ET"})
        # --queries fails closed end to end when a sibling is live (subprocess, real CLI, temp RUNS via --fire path)
        import subprocess
        jd(day / "0940ET" / "queries.json", {"fire": "0940ET", "generated": now_utc().isoformat(), "lock": True})
        env = dict(os.environ); env["FS_RUNS_OVERRIDE"] = str(tmp)
        r_ = subprocess.run([sys.executable, __file__, "--queries", "--fire", str(day / "0945ET"), "--today", "2026-10-06"], capture_output=True, text=True, env=env)
        pr("--queries FAILS CLOSED (exit 1, no folder) while a sibling is in flight", r_.returncode == 1 and "FAIL CLOSED" in r_.stdout and not (day / "0945ET").exists())
        # validation: a malformed transcript is a violation
        bad_fire = day / "0950ET"
        jd(bad_fire / "raw" / "search_1.json", {"threads": [{"id": "1a0cda2aaddc2259", "messageCount": 1, "messages": [{"id": "nothex", "threadId": "1a0cda2aaddc2259", "date": "2026-09-23T16:44:00Z", "sender": me_addr}]}]})
        jd(bad_fire / "raw" / "message_1a0ee874036b56fe.json", {"id": "1a0ee874036b56ff", "threadId": "1a0e75626ba26f69", "date": "2026-09-29T18:57:16Z"})
        v = validate_raw(bad_fire)
        pr("validate_raw: bad message id + id/filename mismatch are both caught", len(v) == 2 and any("not 16 hex" in x for x in v) and any("!= filename" in x for x in v))
        good_fire = day / "0951ET"
        jd(good_fire / "raw" / "search_1.json", {"threads": [{"id": "1a0cda2aaddc2259", "messageCount": 1, "messages": [{"id": "1a05d8e45f21b532", "threadId": "1a0cda2aaddc2259", "date": "2026-09-23T16:44:00Z", "sender": me_addr, "toRecipients": ["person0962@org0123.example"]}]}]})
        pr("validate_raw: a clean transcript has no violations", validate_raw(good_fire) == [])
    finally:
        RUNS = keep_runs
        shutil.rmtree(tmp, ignore_errors=True)
    # the arm gate, pure
    row = run([mk([base])], t((2026, 9, 30), 8, 45)); assert row["action"] == "armable", row
    gth = mk([base]); tid = gth["thread"]
    def arm_doc(msgs, mc=None):
        return {"id": tid, "messageCount": mc if mc is not None else len(msgs), "messages": msgs}
    m1 = {"id": "m1", "threadId": tid, "sender": me_addr, "date": "2026-09-23T16:44:00Z", "labelIds": ["Label_2", "Label_9", "SENT"]}
    nowa = t((2026, 9, 30), 8, 46)
    def ag(doc, age=5, claimed=None):
        return arm_gate(row, gth, doc, age, nowa, cfg, fs, claimed or {})
    def pr2(name, res, ok, part=""):
        nonlocal bad
        good = res[0] == ok and part.lower() in res[1].lower()
        bad += 0 if good else 1
        print(("PASS " if good else "FAIL ") + f"{name}: {res}")
    pr2("arm: fresh read agrees -> armed", ag(arm_doc([m1])), True)
    m2 = {"id": "m2", "threadId": tid, "sender": me_addr, "date": "2026-09-30T15:41:00Z", "labelIds": ["Label_2", "SENT"]}
    pr2("arm: another fire's send appeared (today's failure) -> dropped", ag(arm_doc([m1, m2])), False, "thread changed")
    o1 = {"id": "o1", "threadId": tid, "sender": "person0962@org0123.example", "date": "2026-09-30T15:30:00Z", "labelIds": ["INBOX"]}
    pr2("arm: a reply appeared since the gather -> dropped", ag(arm_doc([m1, o1])), False, "thread changed")
    m1b = dict(m1); m1b["labelIds"] = ["Label_2", "Label_10", "SENT"]
    pr2("arm: stage label Label_10 (Email 2 sent) already present -> dropped", ag(arm_doc([m1b])), False, "stage label")
    m1c = dict(m1); m1c["labelIds"] = ["Label_2", "Label_9", cfg["stage_labels"]["attention"], "SENT"]
    pr2("arm: ⚠ appeared since the gather -> dropped", ag(arm_doc([m1c])), False, "stop label")
    pr2("arm: hidden message appeared (messageCount 2, 1 listed) -> dropped", ag(arm_doc([m1], mc=2)), False, "hidden")
    pr2("arm: read older than TTL -> re-read", ag(arm_doc([m1]), age=arm_ttl(fs) + 1), False, "re-read")
    pr2("arm: thread claimed by an in-flight fire -> dropped", ag(arm_doc([m1]), claimed={tid: "0929ET"}), False, "claimed")
    other_doc = arm_doc([m1]); other_doc["id"] = "1a0d2d112344fed5"
    pr2("arm: read is for a different thread -> dropped", ag(other_doc), False, "different thread")
    # holiday coverage
    last, covered, left = holiday_coverage(fs, datetime.date(2028, 1, 3)); print(("PASS " if not covered else "FAIL ") + f"fail-closed on uncovered year: covered={covered} last={last}")
    bad += 0 if not covered else 1
    print(f"\nSELFTEST {'OK' if bad == 0 else f'FAILED ({bad})'}")
    sys.exit(0 if bad == 0 else 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--queries", action="store_true"); ap.add_argument("--plan", action="store_true")
    ap.add_argument("--arm", action="store_true")
    ap.add_argument("--verify", action="store_true"); ap.add_argument("--preview", action="store_true")
    ap.add_argument("--report-yesterday", action="store_true"); ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--as-of", dest="as_of"); ap.add_argument("--fire"); ap.add_argument("--today")
    a = ap.parse_args()
    if a.queries: cmd_queries(a)
    elif a.plan: cmd_plan(a)
    elif a.arm: cmd_arm(a)
    elif a.verify: cmd_verify(a)
    elif a.preview: cmd_preview(a)
    elif a.report_yesterday: cmd_report_yesterday(a)
    elif a.selftest: cmd_selftest(a)
    elif a.as_of: cmd_as_of(a)
    else: ap.print_help()


if __name__ == "__main__":
    main()
