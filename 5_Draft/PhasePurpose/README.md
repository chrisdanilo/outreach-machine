---
business: Human Skills Training
type: phase-purpose
title: Phase 5 — Draft: write Email 1 as a Gmail draft, exactly from the frozen template
updated: 2026-11-03
---

# 5 · Draft

**What it does.** For every org with a ready recipient set, writes Email 1 as a Gmail draft — and only a draft; Chris adds the GIF and sends it by hand. The code fills the owning machine's approved template word for word (only the greeting and the org's short name vary); Zapier creates the draft with the machine's PDF attached and labels it `<machine>/0`; Gate 7 reads the raw draft back (attachment bytes, clean links, HubSpot Bcc, recipients, subject) before the draft counts. Immediately before each draft, Gmail is searched for the org and every recipient domain, so no org ever gets a second thread. Each machine has a nightly minimum to aim for (OM-1 10, OM-2 35) and a ceiling (15 / 50); a shortfall is reported with its reason, never met by lowering a gate.

**In → out.**
- In: the master list, the two templates in `programfiles/templates/`, the machine's attachment settings, this pass's allowance from the night run.
- Out: Gmail drafts; `ledgers/drafts.jsonl` (every draft made or held, with its draft id and thread — the builder registers them as E1-draft threads); `ledgers/dossiers/` (the dossier Chris opens to send from); tonight's candidates, verification results and raw Zapier replies in `runs/<run>/`.

**Rulebook it applies.** C1 (Email 1 is never sent by a machine) · C2 (one thread per org) · C6 (copy is frozen) · C7 (links never Google-wrapped) · G7 (greeting) · I1 · L · M6.

**How to tell it worked.** The morning report: "Email 1 drafts made tonight — N of minimum". Gmail Drafts shows them under `<machine>/0`. The dossier for the date exists. A REHEARSAL run addresses every draft only to Chris, labels it OM-TEST, and deletes them at the end.

**Its CAPAs.** 2026-08-11 unapproved copy · 2026-08-26 Google link wrapper · 2026-08-26 plaintext template · 2026-09-01 missing dossier · 2026-09-03 floor overshoot · 2026-09-30 two drafts on one thread · 2026-10-26 missing attachment (not a defect) · 2026-10-30 35 floor.

**Programs.** `programfiles/draft.py`, `programfiles/gate7.py` (the read-back check), `programfiles/templates/` (the frozen copy + the old OM-1 dossier template), `programfiles/LAUNCHER-draft.md`, `programfiles/test_draft.py`.
