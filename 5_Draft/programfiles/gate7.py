#!/usr/bin/env python3
"""gate7.py -- Gate 7 for Email 1 drafts (Stage 7): decode the RAW MIME of a draft and check it.

Gmail's get_draft never lists attachments for API-created drafts, so the only proof is the raw message
(reused from Machine 2's verify_attachment.py, CAPA 2026-10-26). Standalone: no vault imports, so it can run
in the cloud session on a large tool-result file too.

  python3 gate7.py --file <saved get_draft RAW result> --want HST_Flyer.pdf:3501128 [--tol 2]
        [--bcc <HUBSPOT_BCC_ADDRESS>] [--video https://www.youtube.com/watch?v=iNCItCda-8g]
        [--to person0008@x.org] [--cc person0269@x.org ...] [--subject "..."] [--out result.json]
Prints one JSON verdict {"ok", "attachment", "checks", "why"}; exit 0 = PASS, 2 = FAIL.
"""
import argparse, base64, email, json, re, sys
from email import policy


def find_raw(obj):
    if isinstance(obj, str) and len(obj) > 200 and re.fullmatch(r"[A-Za-z0-9_\-=\s]+", obj[:500] or ""):
        return obj
    if isinstance(obj, dict):
        for k in ("raw", "rawMessage", "raw_message"):
            if isinstance(obj.get(k), str): return obj[k]
        for v in obj.values():
            r = find_raw(v)
            if r: return r
    if isinstance(obj, list):
        for v in obj:
            r = find_raw(v)
            if r: return r
    return None


def parse(raw_b64url):
    s = re.sub(r"\s+", "", raw_b64url)
    data = base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))
    return email.message_from_bytes(data, policy=policy.default)


def attachments(msg):
    out = []
    for part in msg.walk():
        fn = part.get_filename()
        cd = str(part.get("Content-Disposition", ""))
        if fn and ("attachment" in cd or part.get_content_maintype() == "application"):
            out.append((fn, len(part.get_payload(decode=True) or b"")))
    return out


def html_of(msg):
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            return part.get_content()
    return ""


def addrs(v):
    return sorted({a.lower() for a in re.findall(r"[\w.+'-]+@[\w.-]+\.\w+", str(v or ""))})


def check(msg, want_name, want_size, tol, bcc=None, video=None, to=None, cc=None, subject=None):
    checks, why = {}, []
    found = attachments(msg)
    hit = [f for f in found if f[0] == want_name]
    ok_att = bool(hit) and abs(hit[0][1] - want_size) <= want_size * tol / 100.0
    checks["attachment"] = ok_att
    if not ok_att: why.append("attachment %s %s not found within %s%% (found %s)" % (want_name, want_size, tol, found))
    h = html_of(msg)
    checks["links_unwrapped"] = "google.com/url" not in h
    if not checks["links_unwrapped"]: why.append("a link is Google-wrapped (google.com/url)")
    if video:
        checks["video_href"] = ('href="%s"' % video) in h
        if not checks["video_href"]: why.append("video link missing or altered")
    if bcc:
        checks["bcc"] = bcc.lower() in addrs(msg.get("Bcc"))
        if not checks["bcc"]: why.append("HubSpot Bcc missing")
    if to is not None:
        checks["to"] = addrs(msg.get("To")) == sorted(a.lower() for a in to)
        if not checks["to"]: why.append("To differs: %s" % addrs(msg.get("To")))
    if cc is not None:
        checks["cc"] = addrs(msg.get("Cc")) == sorted(a.lower() for a in cc)
        if not checks["cc"]: why.append("Cc differs: %s" % addrs(msg.get("Cc")))
    if subject is not None:
        checks["subject"] = str(msg.get("Subject", "")).strip() == subject.strip()
        if not checks["subject"]: why.append("subject differs: %r" % str(msg.get("Subject", "")))
    return {"ok": all(checks.values()), "attachment": [list(f) for f in found], "checks": checks, "why": "; ".join(why) or None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True); ap.add_argument("--want", required=True)
    ap.add_argument("--tol", type=float, default=2.0); ap.add_argument("--bcc"); ap.add_argument("--video")
    ap.add_argument("--to", nargs="*"); ap.add_argument("--cc", nargs="*"); ap.add_argument("--subject"); ap.add_argument("--out")
    a = ap.parse_args()
    txt = open(a.file, encoding="utf-8").read()
    try: obj = json.loads(txt)
    except Exception: obj = txt
    raw = find_raw(obj)
    if not raw:
        res = {"ok": False, "attachment": [], "checks": {}, "why": "no raw MIME found in the saved result"}
    else:
        name, size = a.want.rsplit(":", 1)
        res = check(parse(raw), name, int(size), a.tol, a.bcc, a.video, a.to, a.cc, a.subject)
    s = json.dumps(res, ensure_ascii=False)
    if a.out: open(a.out, "w", encoding="utf-8").write(s + "\n")
    print(s)
    sys.exit(0 if res["ok"] else 2)


if __name__ == "__main__":
    main()
