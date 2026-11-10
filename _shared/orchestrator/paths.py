#!/usr/bin/env python3
"""paths.py — THE ONE FILE that knows where the outreach system's root is and what every folder is called (migration 2026-11-03).

Every program imports this first and never computes a folder from its own location again. The layout:

  Automations/                         ROOT (README.md = start here)
    0_Design-and-Purpose/              CHARTER · RULEBOOK · VOCABULARY · decisions/rulings.jsonl · capa/ · diagrams/
    1_Read-the-Inbox/  2_Discover/  3_Qualify/  4_People/  5_Draft/  6_Report/  7_Send/     the seven phases, in clock order
        PhasePurpose/   programfiles/   ledgers/   runs/      — the same four drawers inside every phase
    _shared/master/                    orgs.jsonl · master-list.csv · settings.json (THE one settings file) · overrides.json · build_master.py · seeds/
    _shared/machines/OM-1, OM-2        each machine's data + ledgers only; no programs
    _shared/orchestrator/              run.py · nightrun.py · lock.py · invariants.py · rulings.py · paths.py · night/ · lock files · version log · the two task launchers
    publish/   archive/                GitHub export · everything not in use (nothing live reads archive/)

How a program finds this file: every program sits exactly two folders below ROOT (<phase>/programfiles/x.py, _shared/orchestrator/x.py,
_shared/master/build_master.py), so each one starts with
    import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_shared", "orchestrator")); import paths
Tests point everything at a scratch copy by setting the environment variable OUTREACH_ROOT before importing.
Importing this module also puts every programfiles/ folder on sys.path, so `import seqrules` works from any phase.
"""
import json, os, sys

CODE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # the tree this file sits in: where the programs are
ROOT = os.path.normpath(os.environ.get("OUTREACH_ROOT") or CODE)                     # where the data is (tests point it at a scratch root)
_CORCH = os.path.join(CODE, "_shared", "orchestrator")
MARKETING = os.path.dirname(ROOT)                     # Marketing/   (do-not-contact/ and Lists/ live here)
HST = os.path.dirname(MARKETING)                      # 3.Human Skills Training/  (Ops/Reference/ICP lives here)

def _j(*a): return os.path.join(ROOT, *a)

# ---- 0_Design-and-Purpose
DESIGN = _j("0_Design-and-Purpose")
CHARTER = os.path.join(DESIGN, "CHARTER.md"); RULEBOOK = os.path.join(DESIGN, "RULEBOOK.md"); VOCABULARY = os.path.join(DESIGN, "VOCABULARY.md")
RULINGS = os.path.join(DESIGN, "decisions", "rulings.jsonl")       # THE one rulings log (machine column), 2026-11-03
CAPA = os.path.join(DESIGN, "capa"); DIAGRAMS = os.path.join(DESIGN, "diagrams")

# ---- the seven phases (clock order: a failed step maps to a folder)
PHASES = {"read": "1_Read-the-Inbox", "discover": "2_Discover", "qualify": "3_Qualify", "people": "4_People",
          "draft": "5_Draft", "report": "6_Report", "send": "7_Send"}
def phase(name): return _j(PHASES[name])
def programs(name): return os.path.join(phase(name), "programfiles")
def ledgers(name): return os.path.join(phase(name), "ledgers")
def runs(name): return os.path.join(phase(name), "runs")
def purpose(name): return os.path.join(phase(name), "PhasePurpose")

# ---- _shared
SHARED = _j("_shared")
MASTER = os.path.join(SHARED, "master"); SEEDS = os.path.join(MASTER, "seeds")
SETTINGS = os.path.join(MASTER, "settings.json"); ORGS = os.path.join(MASTER, "orgs.jsonl"); MASTER_CSV = os.path.join(MASTER, "master-list.csv")
OVERRIDES = os.path.join(MASTER, "overrides.json"); BUILD_REPORT = os.path.join(MASTER, "build-report.md"); BUILD_MASTER = os.path.join(CODE, "_shared", "master", "build_master.py")
MACHINES_DIR = os.path.join(SHARED, "machines")
def machine_dir(m): return os.path.join(MACHINES_DIR, m)
ORCH = os.path.join(SHARED, "orchestrator")
NIGHT = os.path.join(ORCH, "night"); NIGHT_RUNS = os.path.join(NIGHT, "runs"); NIGHT_CUR = os.path.join(NIGHT, "current.json")
SUPPLY = os.path.join(ORCH, "supply"); SUPPLY_RUNS = os.path.join(SUPPLY, "runs"); SUPPLY_CUR = os.path.join(SUPPLY, "current.json")   # the Supply Run (Chris 2026-11-08)
LOCK = os.path.join(ORCH, ".outreach-lock"); LOCK_SEND = os.path.join(ORCH, ".outreach-send-lock"); VERSIONS_LOG = os.path.join(ORCH, ".program-versions.log")
# the programs themselves always come from the tree THIS file sits in (tests point OUTREACH_ROOT at a scratch root for data only)
LOCK_PY = os.path.join(_CORCH, "lock.py"); NIGHTRUN_PY = os.path.join(_CORCH, "nightrun.py"); RUN_PY = os.path.join(_CORCH, "run.py")
RULINGS_PY = os.path.join(_CORCH, "rulings.py"); INVARIANTS_PY = os.path.join(_CORCH, "invariants.py")
PUBLISH = _j("publish"); ARCHIVE = _j("archive")

# ---- the standing orders (LAUNCHER-*.md). The two task launchers live with the orchestrator; each step's with its phase.
LAUNCHERS = {"night": os.path.join(ORCH, "LAUNCHER-night-run.md"), "send": os.path.join(ORCH, "LAUNCHER-send.md"), "supply": os.path.join(ORCH, "LAUNCHER-supply.md"),
             "read": os.path.join(programs("read"), "LAUNCHER-read.md"), "discover": os.path.join(programs("discover"), "LAUNCHER-discover.md"),
             "qualify": os.path.join(programs("qualify"), "LAUNCHER-qualify.md"), "people": os.path.join(programs("people"), "LAUNCHER-people.md"),
             "draft": os.path.join(programs("draft"), "LAUNCHER-draft.md"), "report": os.path.join(programs("report"), "LAUNCHER-report.md")}

# ---- the files each phase keeps (ledgers) and works in (runs)
GMAIL_STATE = os.path.join(ledgers("read"), "gmail-state.json")                # what the inbox read knows about every thread
SUCCESSORS = os.path.join(ledgers("read"), "successors.jsonl"); SUCCESSOR_VALIDATION = os.path.join(ledgers("read"), "successor-validation.jsonl")
GMAIL_RAW = os.path.join(runs("read"), "gmail")                                # raw Gmail pulls, by date (pruned after 3 days)
SOURCES = os.path.join(ledgers("discover"), "sources.jsonl"); KEYNOTERS = os.path.join(ledgers("discover"), "keynoters.jsonl")
SEARCH_LOG = os.path.join(ledgers("discover"), "search-log.jsonl"); FINDS = os.path.join(ledgers("discover"), "finds.jsonl")   # was master/discovery-inbox.jsonl
QUALIFY_LEDGER = os.path.join(ledgers("qualify"), "ledger.jsonl"); QUALIFY_DECISIONS = os.path.join(ledgers("qualify"), "decisions.jsonl")   # was master/qualify-inbox.jsonl
PEOPLE_DECISIONS = os.path.join(ledgers("people"), "decisions.jsonl")          # was master/people-inbox.jsonl + people/ledger.jsonl (merged 2026-11-03)
SWEEP_LEDGER = os.path.join(ledgers("people"), "sweep-ledger.jsonl")
DRAFTS = os.path.join(ledgers("draft"), "drafts.jsonl")                        # was master/drafts-inbox.jsonl
DOSSIERS = os.path.join(ledgers("draft"), "dossiers"); TEMPLATES = os.path.join(programs("draft"), "templates")
REPORTS = os.path.join(ledgers("report"), "reports")
SEND_LISTS = os.path.join(ledgers("send"), "send-lists")

# ---- outside this folder (read-only)
DNC_REGISTER = os.path.join(MARKETING, "do-not-contact", "register.jsonl"); DNC_CANDIDATES = os.path.join(MARKETING, "do-not-contact", "candidates.jsonl")
ICP_DIR = os.path.join(HST, "Ops", "Reference", "ICP")

# ---- settings
_S = None
def settings(reload=False):
    """The one settings file, parsed once per process."""
    global _S
    if _S is None or reload: _S = json.load(open(SETTINGS, encoding="utf-8"))
    return _S
def machines(): return tuple(settings()["machines"])
def machine(m): return settings()["machines"][m]
def mset(key): return {m: settings()["machines"][m][key] for m in machines()}      # {OM-1: value, OM-2: value} for one machine setting
def expand(s):
    """Settings paths use {root} (this folder), {master} (_shared/master) and {marketing} (Marketing/)."""
    return os.path.normpath(str(s).replace("{root}", ROOT).replace("{master}", MASTER).replace("{storage_root}", MASTER).replace("{marketing}", MARKETING))
def inp(key): return expand(settings()["inputs"][key])

# ---- every program folder on sys.path, so `import seqrules` works from any phase or test.
# The CODE always comes from the tree this file sits in, even when OUTREACH_ROOT points data at a scratch root (tests).
for _d in [_CORCH, os.path.join(CODE, "_shared", "master")] + [os.path.join(CODE, PHASES[p], "programfiles") for p in PHASES]:
    if _d not in sys.path: sys.path.insert(0, _d)

DOMAIN_PAIRS = os.path.join(MASTER, "domain-pairs.jsonl")   # Rulebook B4 (Chris 2026-11-10, ENG-R012): same-org domain pairs the machine PROVED (E1.8 page proof, Apollo same-org check). Append-only.

if __name__ == "__main__":
    for k, v in sorted(globals().items()):
        if k.isupper() and isinstance(v, str): print("%-22s %s" % (k, v))
