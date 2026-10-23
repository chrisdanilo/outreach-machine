#!/usr/bin/env python3
"""snapshot.py — change history for the machine's RULES, SETTINGS and SCRIPTS.

Why this exists (2026-09-26): Git is the right tool for this job, but inside Cowork's workspace
Git cannot delete its own lock files after a commit, so every commit after the first fails.
This script gives the same three protections without ever deleting anything:

  1. HISTORY   every changed tracked file is copied to history/<stamp>/<path> when you snapshot
  2. CHANGELOG one dated line per snapshot in CHANGELOG.md: message + which files changed
  3. UNDO      --restore puts any file back the way it was at any earlier snapshot

It replaces the hand-made "<file>.pre-YYYY-MM-DD" copies. If the folder is ever opened in
Claude Code or a terminal, `git init` there takes over cleanly; history/ is in .gitignore.

Usage
  python3 bin/snapshot.py "why this change was made"      # record a snapshot
  python3 bin/snapshot.py --status                        # what changed since the last one
  python3 bin/snapshot.py --diff config.json              # line diff vs the last snapshot
  python3 bin/snapshot.py --restore config.json [--from 2026-09-26T1030]
  python3 bin/snapshot.py --list                          # the snapshots on disk

Tracked (rules/settings/scripts only — never the data ledgers, which change every run):
  method.md · config.json · dossier-template.md · LAUNCHER-*.md · BUILD-QUEUE.md · bin/*.py
"""
import sys, json, hashlib, shutil, difflib, pathlib, datetime, glob, os

ROOT = pathlib.Path(__file__).resolve().parent.parent
HIST = ROOT / "history"
MANIFEST = HIST / "manifest.json"
CHANGELOG = ROOT / "CHANGELOG.md"
TRACK = ["method.md", "config.json", "dossier-template.md", "BUILD-QUEUE.md",
         "LAUNCHER-*.md", "bin/*.py"]


def now():
    os.environ.setdefault("TZ", "America/Denver")
    try:
        import time; time.tzset()
    except Exception:
        pass
    return datetime.datetime.now()


def tracked():
    out = []
    for pat in TRACK:
        out += [pathlib.Path(p) for p in glob.glob(str(ROOT / pat))]
    return sorted(set(p.relative_to(ROOT).as_posix() for p in out if p.is_file()))


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def load_manifest():
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {"last": None, "files": {}}


def changed(man):
    cur = {p: sha(p) for p in tracked()}
    prev = man.get("files", {})
    return cur, [p for p in cur if prev.get(p, {}).get("sha") != cur[p]]


def last_copy(man, path):
    """The history copy of `path` from the most recent snapshot that stored it."""
    stamp = man.get("files", {}).get(path, {}).get("stamp")
    return (HIST / stamp / path) if stamp else None


def line_delta(old, new):
    a = old.read_text(encoding="utf-8", errors="replace").splitlines() if old and old.exists() else []
    b = new.read_text(encoding="utf-8", errors="replace").splitlines()
    plus = minus = 0
    for l in difflib.unified_diff(a, b, lineterm="", n=0):
        if l.startswith("+") and not l.startswith("+++"): plus += 1
        if l.startswith("-") and not l.startswith("---"): minus += 1
    return plus, minus


def snapshot(msg):
    man = load_manifest()
    cur, diff = changed(man)
    if not diff:
        print("nothing changed since the last snapshot (%s)" % man.get("last"))
        return 0
    stamp = now().strftime("%Y-%m-%dT%H%M")
    parts = []
    for p in diff:
        old = last_copy(man, p)
        plus, minus = line_delta(old, ROOT / p)
        dest = HIST / stamp / p
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / p, dest)
        man["files"][p] = {"sha": cur[p], "stamp": stamp}
        parts.append("%s (+%d/-%d)" % (p, plus, minus))
    man["last"] = stamp
    HIST.mkdir(exist_ok=True)
    MANIFEST.write_text(json.dumps(man, indent=2), encoding="utf-8")
    if not CHANGELOG.exists():
        CHANGELOG.write_text("# CHANGELOG — rules, settings and scripts\n\n"
                             "One line per snapshot (bin/snapshot.py). Newest at the bottom.\n\n",
                             encoding="utf-8")
    with CHANGELOG.open("a", encoding="utf-8") as f:
        f.write("- **%s** — %s — %s\n" % (stamp, msg, " · ".join(parts)))
    print("snapshot %s: %d file(s)\n  " % (stamp, len(diff)) + "\n  ".join(parts))
    return 0


def status():
    man = load_manifest()
    _, diff = changed(man)
    print("last snapshot: %s" % man.get("last"))
    print("changed since: " + (", ".join(diff) if diff else "nothing"))
    return 1 if diff else 0


def show_diff(path):
    man = load_manifest()
    old = last_copy(man, path)
    if not old or not old.exists():
        print("no earlier copy of %s" % path); return 1
    a = old.read_text(encoding="utf-8", errors="replace").splitlines()
    b = (ROOT / path).read_text(encoding="utf-8", errors="replace").splitlines()
    for l in difflib.unified_diff(a, b, "last snapshot", "now", lineterm="", n=2):
        print(l)
    return 0


def restore(path, stamp=None):
    man = load_manifest()
    if stamp is None:
        src = last_copy(man, path)
    else:
        src = HIST / stamp / path
    if not src or not src.exists():
        print("no copy of %s at %s" % (path, stamp or "last snapshot")); return 1
    shutil.copy2(src, ROOT / path)
    print("restored %s from %s" % (path, src.parent.relative_to(HIST).as_posix().split('/')[0]))
    return 0


def list_snaps():
    if not HIST.exists():
        print("no snapshots yet"); return 0
    for d in sorted(p for p in HIST.iterdir() if p.is_dir()):
        n = sum(1 for _ in d.rglob("*") if _.is_file())
        print("%s  %d file(s)" % (d.name, n))
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__); sys.exit(0)
    if a[0] == "--status":   sys.exit(status())
    if a[0] == "--list":     sys.exit(list_snaps())
    if a[0] == "--diff":     sys.exit(show_diff(a[1]))
    if a[0] == "--restore":
        stamp = a[a.index("--from") + 1] if "--from" in a else None
        sys.exit(restore(a[1], stamp))
    sys.exit(snapshot(" ".join(a)))
