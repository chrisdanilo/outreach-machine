#!/usr/bin/env python3
"""invariants.py — the five things that must stay true through every change to the outreach machines.

Run it any time:  python3 Marketing/Automations/_shared/orchestrator/invariants.py
It reads files only (no Gmail, no Zapier, no network) and prints one line per invariant:
PASS / FAIL / WARN, plus THE OBJECT IT CHECKED, so a failure names the row, not just a verdict.
Exit code 1 if any invariant FAILS. Every cutover in the engine migration runs this before and after.

The five invariants (Phase 0 baseline, 2026-10-26):
  I1  One Email-1 thread per organisation, per machine, ever — and never the same org in BOTH machines.
      (A second thread at one org is allowed only as a declared supplemental thread: group == "supplemental_thread".)
  I2  Nothing is sent without a GO: the sender program has the --intent gate and every sender launcher
      record says Zapier is called ONLY on GO.
  I3  Do-not-contact is absolute: no confirmed DNC domain/address appears on any contacted row of any machine.
  I4  Email 1 is drafts-only: the night programs contain no send/reply call, and the draft launchers say NEVER SEND.
  I5  No simultaneous runs: the shared lock file parses, and if held, is younger than the stale limit.
"""
import json, os, re, sys, time
import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_shared", "orchestrator")); import paths  # the one file that knows every folder (2026-11-03)

ENGINE = paths.ROOT
MK = paths.MARKETING                              # Marketing/ (do-not-contact lives here)
M1 = paths.machine_dir("OM-1")
M2 = paths.machine_dir("OM-2")
MACHINES = {"M1": M1, "M2": M2}
LOCK = paths.LOCK
STALE_HOURS = 4.0


def jl(p):
    out = []
    if not os.path.exists(p):
        return out
    for l in open(p, encoding="utf-8"):
        l = l.strip()
        if l:
            try:
                out.append(json.loads(l))
            except Exception:
                pass
    return out


def read(p):
    try:
        return open(p, encoding="utf-8").read()
    except Exception:
        return ""


def first_existing(*paths):
    for p in paths:
        if os.path.exists(p):
            return p
    return None


R = []  # (invariant, verdict, object)


def rec(inv, verdict, obj):
    R.append((inv, verdict, obj))


# ---------------------------------------------------------------- I1
def i1():
    # shared tenants (gmail.com, a host university, a state agency) are mail hosts, not organisations — M1 config owns the list
    try:
        tenants = {d.lower() for m in paths.machines() for d in paths.machine(m).get("shared_tenant_domains", [])}   # one settings file (2026-11-03)
    except Exception:
        tenants = set()
    by_machine = {}
    for tag, root in MACHINES.items():
        rows = [r for r in jl(os.path.join(root, "contacted.jsonl")) if r.get("type") == "org"]
        seen = {}
        for r in rows:
            st = str(r.get("status", ""))
            if st.startswith("TRANSFERRED") or not r.get("thread"):
                continue                                  # moved to the other machine on purpose / a closure row, not a thread
            for d in r.get("domains") or []:
                d = d.lower()
                if d in tenants:
                    continue
                seen.setdefault(d, []).append(r)
        by_machine[tag] = seen
        dups = {d: rs for d, rs in seen.items() if len(rs) > 1}
        warn = 0
        for d, rs in dups.items():
            prim = [r for r in rs if r.get("group") != "supplemental_thread"]
            if len(prim) < 2:
                continue
            # two DIFFERENT organisations sharing a host domain (USU Bear River vs USU Eastern) is a shared-host shape, not a double send
            firsts = {(r.get("domains") or [""])[0].lower() for r in prim}
            if len(firsts) == len(prim):
                warn += 1
                rec("I1", "WARN", f"{tag}: {d} is a shared host for {len(prim)} different orgs (" + ", ".join(str(r.get('org')) for r in prim) + ") — not in config.shared_tenant_domains")
            else:
                rec("I1", "FAIL", f"{tag}: {d} has {len(prim)} primary threads for the same org: " + ", ".join(str(r.get("thread")) for r in prim))
        rec("I1", "PASS", f"{tag}: {len(seen)} org domains checked, one primary thread each ({sum(1 for rs in dups.values() if any(r.get('group')=='supplemental_thread' for r in rs))} declared supplemental, {warn} shared-host warnings)")
    both = set(by_machine["M1"]) & set(by_machine["M2"])
    if both:
        rec("I1", "FAIL", "org in BOTH machines' contacted.jsonl (not TRANSFERRED): " + ", ".join(sorted(both)[:15]))
    else:
        rec("I1", "PASS", "no org domain is live in both machines")


# ---------------------------------------------------------------- I2
def i2():
    senders = [os.path.join(paths.programs("send"), "followup_send.py")]
    for p in senders:
        if not p or not os.path.exists(p):
            continue
        t = read(p)
        ok = "--intent" in t and "GO" in t
        rec("I2", "PASS" if ok else "FAIL", f"{os.path.relpath(p, MK)}: --intent gate {'present' if ok else 'MISSING'}")
    # launcher record copies (the scheduled tasks are mirrored here)
    for p in [paths.LAUNCHERS["send"]]:  # the live sender orders (consolidation 2026-11-02)
        if os.path.exists(p):
            t = read(p)
            ok = re.search(r"ONLY (if|on)[^.\n]*GO", t) is not None
            rec("I2", "PASS" if ok else "WARN", f"{os.path.relpath(p, MK)}: 'call Zapier ONLY on GO' {'present' if ok else 'not found in record copy'}")


# ---------------------------------------------------------------- I3
def _mmdd(s, year="2026"):
    m = re.search(r"(\d{2})-(\d{2})", str(s or ""))
    return f"{year}-{m.group(1)}-{m.group(2)}" if m else None


def i3():
    """A DNC row is violated only by a contact AFTER the person asked (date_of_request). The rows that led to the
    request are history — they are exactly the people who asked — and are reported as covered, not failed."""
    reg = jl(paths.DNC_REGISTER)
    if not reg:
        rec("I3", "PASS", "do-not-contact/register.jsonl has 0 confirmed rows (nothing to violate); candidates pending: %d" % len(jl(paths.DNC_CANDIDATES)))
        return
    doms, mails = {}, {}
    for r in reg:
        d0 = r.get("date_of_request") or r.get("date") or "0000-00-00"
        if r.get("scope") == "domain" and r.get("domain"):
            doms[r["domain"].lower()] = (r.get("register_id"), d0)
        for e in r.get("emails") or ([r["email"]] if r.get("email") else []):
            mails[e.lower()] = (r.get("register_id"), d0)
    fails, covered = [], 0
    for tag, root in MACHINES.items():
        for r in jl(os.path.join(root, "contacted.jsonl")):
            if r.get("type") == "org":
                last = max((x for x in (_mmdd(r.get("e1")), _mmdd(r.get("e2")), _mmdd(r.get("e3"))) if x), default=None)
                for d in r.get("domains") or []:
                    if d.lower() in doms:
                        rid, d0 = doms[d.lower()]
                        if last and last > d0:
                            fails.append(f"{tag} org {d}: contact {last} AFTER {rid} request {d0} ({r.get('status','')[:40]})")
                        else:
                            covered += 1
            elif r.get("type") == "address":
                a = (r.get("address") or "").lower()
                hit = mails.get(a) or doms.get(a.split("@")[-1])
                if hit:
                    rid, d0 = hit
                    sent = _mmdd(r.get("sent") or r.get("stage"))
                    if sent and sent > d0:
                        fails.append(f"{tag} address {a}: sent {sent} AFTER {rid} request {d0}")
                    else:
                        covered += 1
    if fails:
        for h in fails[:15]:
            rec("I3", "FAIL", h)
    else:
        rec("I3", "PASS", f"{len(reg)} DNC rows; {covered} historical contacted rows are the requests themselves; no contact after any request date")


# ---------------------------------------------------------------- I4
def i4():
    for p in [os.path.join(paths.programs("draft"), "draft.py"), paths.NIGHTRUN_PY]:   # the night programs (2026-11-03)
        if os.path.exists(p):
            t = read(p)
            bad = re.findall(r"send_message|reply_to_message|gmail_reply_to_email", t)
            rec("I4", "FAIL" if bad else "PASS", f"{os.path.relpath(p, MK)}: {'contains ' + ','.join(set(bad)) if bad else 'no send/reply call'}")
    for p in [paths.LAUNCHERS["night"]]:  # the live night orders (consolidation 2026-11-02)
        if os.path.exists(p):
            t = read(p).upper()
            ok = "NEVER SEND" in t
            rec("I4", "PASS" if ok else "WARN", f"{os.path.relpath(p, MK)}: 'NEVER SEND' {'present' if ok else 'not found'}")


# ---------------------------------------------------------------- I5
def i5():
    if not os.path.exists(LOCK):
        rec("I5", "PASS", ".outreach-lock absent (never used yet)")
        return
    try:
        l = json.load(open(LOCK))
    except Exception as ex:
        rec("I5", "FAIL", f".outreach-lock unreadable: {ex}")
        return
    if not l.get("holder"):
        rec("I5", "PASS", f".outreach-lock FREE (last released by {l.get('released_by')} at {l.get('released_iso')})")
        return
    age_h = (time.time() - float(l.get("started", 0))) / 3600
    rec("I5", "PASS" if age_h < STALE_HOURS else "WARN", f".outreach-lock held by {l['holder']} for {age_h:.1f} h (stale limit {STALE_HOURS} h)")


def main():
    for f in (i1, i2, i3, i4, i5):
        try:
            f()
        except Exception as ex:
            rec(f.__name__.upper(), "FAIL", f"check crashed: {ex!r}")
    w = max(len(o) for _, _, o in R) if R else 10
    fails = 0
    for inv, v, obj in R:
        fails += v == "FAIL"
        print(f"{inv:3} {v:4} {obj}")
    print(f"\ninvariants: {sum(1 for r in R if r[1]=='PASS')} PASS · {sum(1 for r in R if r[1]=='WARN')} WARN · {fails} FAIL")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
