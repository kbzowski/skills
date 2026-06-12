---
name: leapspace
description: >
  Drive Elsevier LeapSpace (ScienceDirect's AI research assistant, powered by
  Scopus data and Elsevier full text) through Chrome browser automation to run
  literature research: ask grounded research questions, run Deep Research
  reports, verify citations via Trust Cards, find experts and funding, and
  export references as BibTeX/RIS/CSV. Use when the user asks to "do research
  with LeapSpace", "search literature via LeapSpace/ScienceDirect AI",
  "run deep research on <topic>", "find papers/experts/funding through
  LeapSpace", or mentions "leapspace". Requires institutional access (e.g. AGH
  library proxy) and the claude-in-chrome browser tools.
---

# LeapSpace — AI literature research via ScienceDirect

LeapSpace is Elsevier's conversational research assistant. Every answer is
grounded in Scopus metadata and Elsevier full-text content, with numbered
citations that can be verified down to the exact source passage. It is the
right tool when the user needs *citable, peer-reviewed evidence*, not a
general web search.

## Access

| Route | URL |
|---|---|
| AGH library proxy (user's default) | `https://www-1sciencedirect-1com-1000027ga0157.wbg2.bg.agh.edu.pl/leapspace` |
| Direct (on-campus / entitled network) | `https://www.sciencedirect.com/leapspace` |

- The AGH proxy (`wbg2.bg.agh.edu.pl`) rewrites the domain; conversation URLs
  look like `…/leapspace/conversation/<uuid>` and are stable/bookmarkable.
  The `1000027gaXXXX` hostname segment varies per proxy session — the URL
  above still works as an entry point (the proxy rewrites it).
- Footer disclaimer: "AI responses may vary in quality… verify independently."
  Treat answers as leads backed by sources, not ground truth.

## Browser automation workflow

Load the Chrome tools (one ToolSearch call), get tab context, create a new
tab, navigate to the LeapSpace URL.

### 0. Verify login state (do this BEFORE submitting anything)

Navigating to the proxy URL in a fresh tab triggers an auth redirect chain
even when another tab has a live session. Expect, in order:

1. A blank `login.wbg2.bg.agh.edu.pl/login/login.html` interstitial for
   ~10 s. The extension cannot read this page (`get_page_text` fails with a
   host-permission error) — just wait, don't treat the error as failure.
2. An OAuth redirect chain (~25 s total), possibly ending in an Elsevier
   "Welcome / Enter your email" modal. **Do not enter anything — click the
   modal's X.** That dismisses the personal-login prompt; institutional SSO
   then completes automatically.

Then confirm you are actually logged in — take a screenshot and check ALL of:

- the tab URL contains `/leapspace` (not `login`, `authorization`, or
  `auth`),
- the query textbox "What would you like to learn more about?" (or
  "Ask a follow-up question") is present,
- the bottom-left sidebar shows the user's account button (initials + name).

**If any check fails** — the URL is stuck on a login/SSO page, the email
modal reappears after dismissing it, or the page asks for credentials —
STOP. Never type credentials or pick an institution yourself. Tell the
user which page you see and ask them to log in manually in that Chrome tab
(AGH library proxy / Elsevier SSO), then wait for their confirmation and
re-run this check before continuing. The same applies mid-session: if a
query suddenly lands on a login page, the proxy session expired — repeat
this step.

### 1. Submit a query (standard mode)

1. Click the textbox (placeholder: "What would you like to learn more about?").
2. Type a **specific research question** — full sentence, with domain terms.
   LeapSpace converts it into several Scopus boolean + natural-language +
   full-text searches, so specificity directly improves retrieval.
3. Press Enter (or click "Submit query").
4. Wait ~20–40 s. The page shows "Copilot steps" with live progress
   (plan → keyword search on Scopus → natural-language search → full-text
   search → foundational documents → Done). Poll with short waits +
   screenshots; the answer streams in below.
5. Extract the answer with `get_page_text` — it returns the full answer
   `<article>` including tables and the "Confidence level" line.
   **Caveat:** `get_page_text` captures ONLY the answer article — side
   panels (Reference details, All references, Trust Cards) are invisible to
   it; read those via screenshots, `read_page`, or `find`.

A survey popup ("We would love to hear how you search…") may occasionally
appear — dismiss it via its X button before clicking anything else.

### 2. Anatomy of a standard answer

- Structured prose with **bold key claims**, comparison tables, a
  "Bottom line" and a "Confidence level: High/Medium/Low — <reason>" line.
- Numbered citation chips `[1] [2] …` after each claim.
- `Show all N references` button (roughly 10–20 refs in standard mode).
- Action icons: copy answer, thumbs up/down.
- "Follow-up Suggestions" — 3 clickable next questions.
- A follow-up input box keeps the conversation context.

### 3. Verify citations (Trust Cards)

Citation chips are tiny (~14 px) — click them via `find` (e.g. "citation
chip 1") / element refs rather than raw coordinates; an off-by-25-px click
silently does nothing. Clicking a chip opens the right-hand **Reference
details** panel:

- Full metadata: title, authors (each links to a Scopus profile), journal,
  publisher, year, citation count, **FWCI** (Field-Weighted Citation Impact).
- `View at publisher` / `View Scopus document` external links.
- **"Supports claim" Trust Card** — an explanation of how this reference
  supports the highlighted statement (the supported sentence is highlighted
  in the answer body). It loads asynchronously ("Link to statement is
  loading", ~2–4 s) and **shifts the content below it ~100 px down when it
  renders** — wait for it before clicking the tabs.
- Tabs: **Abstract** (full abstract) and **Excerpts** ("Found in *X*
  section" — the exact quoted passages the answer was built from).
  **Tabs exist only on references labelled "Full text".** References
  labelled "Scopus abstract" have no tabs — verify those against the
  Abstract section shown below the Trust Card instead.

Use this when the user asks "is that claim actually supported?" — read the
Excerpts tab (or Abstract for abstract-only refs) rather than trusting the
summary. Panels are not visible to `get_page_text`; read them with
screenshots or `read_page`.

### 4. Export references

`Show all N references` → "All references" panel lists every source with
Show abstract / View at publisher / View Scopus document. The **download
icon** at the top of the panel offers: **CSV, RIS, BibTeX, Plain Text**
(press Escape to close the menu without downloading).
Downloading a file requires explicit user permission — ask first, stating
format and filename. Alternatively transcribe references from the panel —
note it is NOT captured by `get_page_text`; use `read_page` or screenshots.

### 5. Deep Research mode

For survey/state-of-the-art questions, toggle the **telescope icon** next to
the input (a "Deep research ×" chip appears), then submit the question.

- Runtime ~2–5 min. Status shows "Processing for Ns" plus a live note
  (e.g. "Gathering twenty sources…"). Poll with 20–30 s waits.
- Internally it generates a research plan, ~4 primary queries, then explores
  each at 3 levels of depth (visible later via "Show deep research steps").
- Output is a full report: **Quick Reference / Key Findings Table → Direct
  Answer → Study Scope → Assumptions & Limitations → Suggested Further
  Research → numbered sections → Conclusion**, with far more references
  (~80 vs ~20) and two extras at the top:
  - `View Deep research response as PDF` (download — ask permission first),
  - `Show deep research steps` (audit trail panel).

Choose deep research when the user wants a literature review, gap analysis,
or report; use standard mode for focused questions (it's 5–10× faster).

### 6. Special query patterns

The home-page buttons are prompt templates, not separate tools — you can
type the pattern directly:

- **Explore topics**: "What are the main research themes in <field>?",
  "Key open questions in <topic>?"
- **Find experts**: "Who are the authors in <topic> research today?",
  "Latest publications by authors on <topic>"
- **Find funding**: "Which grants fund <topic> research?", "Which funders
  support <area>?"

### 7. Conversation management

- Left sidebar: history of conversations; "New conversation" starts fresh
  (always start a new conversation for a new topic — context carries over).
- Chevron next to the conversation title: **Rename / Delete**.
- "Temporary conversation" toggle (top right of home page): session is not
  saved to history.
- Paperclip button: upload files to ask questions about a document
  (file-picker opens an OS dialog — ask the user to attach manually if
  needed, or use the `file_upload` tool).

## Reporting results to the user

When relaying LeapSpace findings:

1. Quote the Confidence level line and lead with the "Bottom line".
2. Keep citation numbers mapped to real references — pull titles/authors/
   years from the references panel, never invent them.
3. Mention that the answer is Scopus/Elsevier-grounded but flag the
   built-in disclaimer; for load-bearing claims, open the citation's
   Excerpts tab and confirm the quoted passage.
4. Offer BibTeX/RIS export if the user is writing a paper.

## Pitfalls

- Long waits: never assume failure before ~60 s (standard) / ~6 min (deep).
- Proxy sessions expire; a sudden login page means re-authentication is
  needed — hand control back to the user and re-run step 0.
- Coverage is Scopus + Elsevier full text: strong for peer-reviewed STEM
  literature, weak for preprints, books, and grey literature — say so if
  the topic depends on those.
- Each submitted query consumes institutional quota; batch what you need
  into well-formed questions instead of many trivial ones.
