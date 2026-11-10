---
business: Human Skills Training
type: template
title: Dossier — outline (binding)
status: binding
owner: Chris Danilo
created: 2026-11-04
built_by: 5_Draft/programfiles/dossier.py (the code fills this; nobody types a dossier by hand)
supersedes: retired/dossier-template-OM-1-2026-09-03.md
---

# Dossier — outline

**Purpose:** Chris reads this to VERIFY who each draft goes to and why, before he sends. It is not a sending checklist.
**The outline is the structure. Every repeating part repeats as often as the data needs** — bullets, table rows and cards are placeholders, not counts.

```
📤 Dossier — <date>

## ⚠️ Requires Decisions / Judgement
- ⚠️ <machine #position org> — <what needs Chris> · <link>        ← one line per org that needs him; as many as there are
  (none → "Nothing needs you tonight.")

# 📧 2️⃣ OM2 — Position 1 · <Org> · <ST>   [⚠️ see decisions]
- 🏢 Org: <name> — <website>
- 👥 Staff page(s): <link> · <link> …
- 📅 Event / training page(s): <link> · <link> …   (none → "none read")
- ✉️ Subject · Greeting · open draft in Gmail
| Name | Title | Email | Source |                          ← one row per recipient
- 🧠 Reasoning: who is on the draft and why · who is NOT and why · why OM1 vs OM2 · fit
- 🔗 Supporting pages: <link> · <link> …
… Position 2, 3 … (OM2 cards first)

# 📧 1️⃣ OM1 — Position 1 · … same card
… Position 2, 3 …

✅ Gate 7 line · records links
```

## Rules

| Rule | |
|---|---|
| Position | Position N = Nth draft from the top of that machine's /0 Drafts view (newest first). Each machine counts from 1. |
| Emojis | ⚠️ needs a decision (matches the Gmail ⚠ label) · 📧 an email card · 1️⃣ OM1 · 2️⃣ OM2 · 🏢 org · 👥 staff pages · 📅 event/training pages · 📄 address printed on the org's page · 🔍 Apollo-verified · 📮 general inbox · 🧠 reasoning · 🔗 sources · ✅ checks passed |
| Top section = exceptions only | Only things that change whether or how Chris sends THIS draft. Nothing routine (no GIF reminder, no standing rules). One line per org; several reasons on one line. |
| Decision triggers (code) | domain or address on the HubSpot block list (§A/§B/§D read straight from the seed file) · master-list exclusion · ⚠ flags (e.g. doubtful fit) · To is a general inbox · no leader on the draft while a named leader has no address · no leader/PD role among recipients · same address under another org record · catch-all · departed · Gate 7 failed · mail domain ≠ website |
| Not on the draft | Every named person left off is listed with why: "Apollo: no email", "Apollo address held", or "never looked up". |
| Links | Every page is a clickable link. Apollo-verified rows link the page that names the person. |
| Sources | Records only (drafts ledger, master list, people results, H7 sweep ledger, Gate 7 verify.json, HubSpot suppression seed). Nothing is looked up or retyped. |

## Change log
- 2026-11-04 — Chris's outline (notebook sketch) replaces the 2026-09-03 template. Lessons carried over: exceptions-only top table; "should not send" trigger; everyone left off is accounted for; links on every row. Dropped: follow-ups, standing numbers, decisions-for-you (those live in the night report).
