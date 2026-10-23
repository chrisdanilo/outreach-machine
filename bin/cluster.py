#!/usr/bin/env python3
"""cluster.py — the cluster a run serves is a SETTINGS BLOCK, not a prose rewrite.

config.json.cluster_profiles holds one profile per cluster (CL-YYYY-QN): its market, message,
copy file, Green Sheet, Gmail labels, target-list source and the machine settings that differ
between clusters. The top-level keys the scripts read are the APPLIED COPY of the active profile's
`settings`. This script keeps the two honest and does the switch.

  python3 bin/cluster.py check              -> the `Cluster:` report line; exit 1 if the applied
                                               copy disagrees with the active profile (profile wins)
  python3 bin/cluster.py show [CL-2026-Q4]  -> print a profile
  python3 bin/cluster.py apply CL-2026-Q4   -> LAUNCH: set active_cluster and rewrite the applied
                                               copy from that profile. REFUSES unless the Green Sheet
                                               and the copy file exist on disk and stage_labels is
                                               set. Snapshots config.json first (bin/snapshot.py).
                                               🔴 Only Chris runs this (method §0.7.2).

Installed 2026-09-26. Reads/writes: config.json only.
"""
import sys, json, pathlib, collections, subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
HST = ROOT.parents[1]
CFG = ROOT / "config.json"
OD = collections.OrderedDict


def load():
    return json.loads(CFG.read_text(encoding="utf-8"), object_pairs_hook=OD)


def save(cfg):
    CFG.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def check(cfg):
    cid = cfg.get("active_cluster")
    prof = cfg.get("cluster_profiles", {}).get(cid)
    if not prof:
        print("Cluster: %s — 🔴 NO PROFILE in config.cluster_profiles" % cid); return 1
    bad = []
    for k, v in prof["settings"].items():
        if cfg.get(k) != v:
            bad.append("%s (applied %s ≠ profile %s)" % (k, json.dumps(cfg.get(k))[:40], json.dumps(v)[:40]))
    gs = HST / prof["green_sheet"] if prof.get("green_sheet") else None
    cp = HST / prof["copy_file"] if prof.get("copy_file") else None
    notes = []
    if not gs or not gs.exists(): notes.append("green sheet MISSING")
    if not cp or not cp.exists(): notes.append("copy file MISSING")
    line = "Cluster: %s · %s · %s × %s × %s · %s" % (
        cid, prof.get("label"), prof.get("method"), prof.get("market"), prof.get("message"),
        "applied settings agree with profile" if not bad else "🔴 DRIFT — " + "; ".join(bad))
    if notes: line += " · 🔴 " + ", ".join(notes)
    print(line)
    return 1 if (bad or notes) else 0


def show(cfg, cid):
    prof = cfg.get("cluster_profiles", {}).get(cid)
    if not prof: print("no profile", cid); return 1
    print(json.dumps(prof, indent=2, ensure_ascii=False)); return 0


def apply(cfg, cid):
    prof = cfg.get("cluster_profiles", {}).get(cid)
    if not prof: print("REFUSED: no profile", cid); return 1
    refuse = []
    if not prof.get("green_sheet") or not (HST / prof["green_sheet"]).exists():
        refuse.append("green_sheet missing on disk — Chris writes the Green Sheet first (ClusterChecklist)")
    if not prof.get("copy_file") or not (HST / prof["copy_file"]).exists():
        refuse.append("copy_file missing on disk — the machine never writes body copy")
    if not prof["settings"].get("stage_labels"):
        refuse.append("stage_labels is null — create the Gmail labels and record their IDs in the profile")
    if not prof.get("gmail_label_parent"):
        refuse.append("gmail_label_parent is null")
    if refuse:
        print("REFUSED to apply %s:\n  - " % cid + "\n  - ".join(refuse)); return 1
    subprocess.run([sys.executable, str(ROOT / "bin" / "snapshot.py"),
                    "cluster.py apply %s (before)" % cid], check=False)
    prev = cfg.get("active_cluster")
    cfg["active_cluster"] = cid
    for k, v in prof["settings"].items():
        cfg[k] = v
    if prof.get("status", "").startswith("ON DECK"):
        prof["status"] = "IN TEST"
    if not prof.get("opened"):
        import datetime; prof["opened"] = datetime.date.today().isoformat()
    save(cfg)
    subprocess.run([sys.executable, str(ROOT / "bin" / "snapshot.py"),
                    "cluster.py apply %s (after) — was %s" % (cid, prev)], check=False)
    print("APPLIED %s (was %s). Now run: python3 bin/replay.py --all" % (cid, prev))
    return check(cfg)


if __name__ == "__main__":
    a = sys.argv[1:]
    cfg = load()
    if not a or a[0] == "check": sys.exit(check(cfg))
    if a[0] == "show":           sys.exit(show(cfg, a[1] if len(a) > 1 else cfg.get("active_cluster")))
    if a[0] == "apply":          sys.exit(apply(cfg, a[1]))
    print(__doc__); sys.exit(2)
