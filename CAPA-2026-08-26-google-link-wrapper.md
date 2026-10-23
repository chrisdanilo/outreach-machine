---
business: Human Skills Training
type: capa
title: "CAPA 2026-08-26 — every video link ships wrapped in a Google redirect, and it survives delivery"
status: open
owner: Chris Danilo
raised_by: Chris (UX concern — recipients may hit a 'you're about to leave this site' warning)
related: ["[[method]]", "[[Cold-Outreach-Sequence-CCR&R]]", "[[sequence-tracker]]", "[[CAPA-2026-08-26-u8-plaintext-template]]"]
---

# CAPA — the video link is not a clean YouTube link, and never has been

**Chris raised it as a UX risk. It is confirmed, it reaches the recipient, and it has been shipping
in every Email 1 and Email 2 the machine has ever sent.**

---

## 1 · PROOF — read from a RECIPIENT's mail system, not from ours

**[Person 0191] ([Org 0188]) replied from Outlook at 2026-08-26T13:07Z and her client
quoted our Email 1 back.** A quote block shows what **arrived**, not what Gmail shows us. Verbatim:

```html
<a href="https://www.google.com/url?q=https://www.youtube.com/watch?v%3DiNCItCda-8g
   &amp;source=gmail&amp;ust=<thread-id>&amp;sa=E" target="_blank">
   https://www.youtube.com/watch?v=iNCItCda-8g</a>
```

🔴 **The wrapper survives delivery.** This is not a compose-window artifact.

**And the plaintext alternative is materially worse** — Outlook renders BOTH, inline:

```
https://www.youtube.com/watch?v=iNCItCda-8g<https://www.google.com/url?q=https://www.youtube.com/watch?v%3DiNCItCda-8g&source=gmail&ust=<thread-id>&sa=E>
```

**Anyone reading in plaintext — common in government, education and locked-down corporate clients,
which is much of this list — sees the raw redirect string in the body of the email.**

## 2 · Three explanations tested. Two are already refuted by evidence in hand.

| # | Hypothesis | Verdict |
|---|---|---|
| **H1** | *"It only looks like that in Gmail; recipients get a clean link."* | 🔴 **REFUTED** — Donna's Outlook copy above is wrapped |
| **H2** | *"Write a clean `href` and it will stay clean."* | 🔴 **REFUTED** — this afternoon's recast wrote `href="https://www.youtube.com/watch?v=iNCItCda-8g"` verbatim. **`get_draft` read it back ALREADY WRAPPED, before any send.** Gmail rewrites at WRITE time |
| **H3** | *"It happens because the anchor text is a bare URL; a phrase would be left alone."* | 🔴 **REFUTED** — Email 2's anchor text is a phrase, *"how to design top notch training that actually changes behavior"*, and **its href is wrapped too** |

🔴 **H2 is the important one.** It means **the fix is not "write a cleaner link."** The machine already
did that today and Gmail overrode it. Any resolution that consists of the machine being more careful
about the `href` it writes is already known not to work.

**One question remains open, and it decides the fix:**
**Does Gmail wrap NON-Google destinations the same way?** There is **no clean sample of a
non-Google `href` in Chris's own sent mail** to test against. Section 5 resolves this.

## 3 · 🔴 The irony, because it is the actual origin

**[[Cold-Outreach-Sequence-CCR&R]] line 235 — the v1→v2 calibration record, change #6, verbatim:**

> | 6 | Video link: `chrisdanilo.com/what-hst-looks-like` → **a bare bolded YouTube URL** |
> **Direct to the video, no landing page in between** |

**The copy previously used a first-party short link and was deliberately changed to a bare YouTube URL
to remove a hop.**

🔴 **The hop was never removed. It was relocated, made uglier, and handed to a third party.**
Every send since has gone `recipient → google.com/url → youtube.com` — **the same two hops, except the
middle one is now Google-branded instead of Chris-branded, and it is visible in plaintext clients.**

## 4 · What the confirmed harm actually is — stated honestly, not inflated

| Harm | Status |
|---|---|
| **Plaintext readers see the raw redirect string inline** | ✅ **CONFIRMED** — quoted above from a real delivered copy |
| **The link is not first-party; no click data exists** | ✅ **CONFIRMED** — Chris cannot tell who watched the video |
| **A "you're about to leave this site" interstitial** | ⚠️ **NOT OBSERVED.** Chris raises it as a risk. `google.com/url?q=` to a **youtube.com** destination is Google-to-Google and would very likely pass straight through. **Not asserted either way — it has not been tested** |

🔴 **The case does not rest on the interstitial.** The plaintext rendering is confirmed, visible, and
ugly on its own. **Overstating the interstitial to strengthen the argument would be the same error as
this morning's U8 — claiming more than the evidence carries.**

---

## 5 · RESOLUTION — what I will do on the next run, unprompted

### S1 · LINK SHAPE TEST — diagnostic only, no copy touched, no permission needed

**[[method]] already carries a standing rule:** *"🔴 FIRST WRITE OF EVERY RUN IS A SHAPE TEST. Make it
a real draft you needed anyway, read it back, and record which shape worked."* **It currently covers
`to`, `cc` and `labelIds`. I will extend it to LINKS.**

**Procedure — one draft, one read-back, one trash:**

1. Create a throwaway draft to `<SENDER_EMAIL>` containing three hrefs, all written clean:
   `https://www.youtube.com/watch?v=iNCItCda-8g` · `https://chrisdanilo.com/what-hst-looks-like` ·
   one neutral non-Google third-party URL
2. Read it back with `get_draft` / `FULL_CONTENT`
3. **Record which hrefs came back wrapped** — in [[verification-log]], with the date
4. Trash the draft
5. **Print the result in the run report**

**This answers the only open question, costs one tool call and zero credits, and it is diagnostic —
it writes no outreach copy.** ✅ **I will run this next run whatever Chris decides below.**

### S2 · Then the fix follows from the result — and THIS needs Chris's ruling

🔴 **The video link is APPROVED COPY. `machine_writes_copy: never` is a level-2 hard limit. The
machine may not change it, and this CAPA does not change it.**

| If the test shows… | Recommended resolution | What it costs |
|---|---|---|
| 🅰 **Only Google-owned destinations get wrapped** | **Restore `chrisdanilo.com/what-hst-looks-like` as a 301 to the video.** Clean href · first-party · brandable · survives a YouTube URL change · **and finally gives Chris click data** | A copy change → **template v7**, and a redirect Chris sets up once on Squarespace |
| 🅱 **Everything gets wrapped regardless of destination** | **The connector cannot emit a clean href. Accept it, or change send path.** A first-party link is still worth it for the click data and the cleaner plaintext string, but it will not remove the wrapper | Nothing, or a send-path change |

🎯 **My recommendation either way is 🅰 — restore the short link.** Even under 🅱 it improves the
plaintext rendering (`chrisdanilo.com/what-hst-looks-like` reads as a human link where a wrapped
YouTube URL does not) and it recovers click tracking that has been lost since v2.
**The v2 rationale — "no landing page in between" — is satisfied by a 301, which is not a landing page.**

---

## 6 · CORRECTIVE ACTIONS

| # | Control | Status |
|---|---|---|
| **C1** | **Extend the first-write shape test to LINKS** (S1 above), recording results in [[verification-log]] | ✅ **I will run this next run** |
| **C2** | **Record in [[method]]'s connector-behaviour section: Gmail REWRITES `href` values at WRITE time.** A clean href written by the machine does not stay clean. This now sits alongside the `update_draft` and `labelIds` quirks as known connector behaviour | Proposed |
| **C3** | 🔴 **The learn-pass body diff must compare HREFs, not just visible text.** Today's U8 check passed a wrapped href because the *display text* was correct. **The defect was one attribute below where anyone was looking** | Proposed |
| **C4** | 🆕 🎯 **VERIFY RENDERING FROM THE RECIPIENT'S COPY, NOT OURS.** Every reply that quotes our message is a **free delivery audit** — it shows what their mail system actually received. **This CAPA exists only because one recipient's Outlook quoted us back.** Make it standing: on every reply, diff the quoted block against what we believe we sent | Proposed |

🔴 **C4 is the one that generalises, and it is free.** The machine has had **11 replies** and has never
once read the quote block as evidence. **It is the only view of the email that is not our own** — and
today it caught a defect that had been shipping since the template was written.
