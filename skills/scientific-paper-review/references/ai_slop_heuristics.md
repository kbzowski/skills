# AI Slop & Paper Mill Detection Heuristics

Three categories of signals: **verifiable** (confirmed by agents), **linguistic** (detected by reading),
and **paper mill** (distinct from LLM generation — see [tortured_phrases.md](tortured_phrases.md)).

## Verifiable Signals (from agent results)

These are hard evidence. Each confirmed finding is a flag.

| Signal | Flag weight | How to confirm |
|--------|------------|----------------|
| Cited reference does not exist | MAJOR | Reference Verifier: ❌ NOT FOUND |
| DOI resolves to a different paper | MAJOR | Reference Verifier: ⚠️ MISMATCH |
| DOI is malformed or invalid | MAJOR | Reference Verifier: DOI syntax check |
| ISBN fails validation checksum | MINOR | Reference Verifier: ISBN check |
| >30% of references unverifiable | MAJOR | Reference Verifier: count ❌ / total |
| Key factual claim contradicted by evidence | MAJOR | Claims Verifier: ❌ CONTRADICTED |
| Journal is on Beall's predatory list | MAJOR | Journal Checker: PREDATORY |
| Author has no online academic presence | MINOR | Author Checker: not found |
| Author affiliation does not match | MINOR | Author Checker: mismatch |
| Statistics internally inconsistent | MAJOR | Manual: percentages don't sum, df vs n mismatch |
| Citation URLs contain UTM/tracking parameters | MINOR | Reference Verifier: utm_source in URL |
| Reference contains AI tool artifacts | MAJOR | See "Citation artifacts" below |
| Cited reference is retracted | MAJOR | Reference Verifier: 🔴 RETRACTED |
| Statcheck gross inconsistency (p crosses .05) | MAJOR | Statistical Integrity Checker |
| GRIM-inconsistent mean | MAJOR | Statistical Integrity Checker |
| Suspicious p-value clustering at .04–.049 | MINOR | Statistical Integrity Checker |
| Tortured phrase found | MAJOR | See [tortured_phrases.md](tortured_phrases.md) |
| Technical term synonym-substitution pattern | MAJOR | See [tortured_phrases.md](tortured_phrases.md) |

## Linguistic Signals (detected during reading)

These are soft indicators. No single one is conclusive — look for **density and co-occurrence**.

### LLM Vocabulary Markers

Phrases disproportionately common in LLM output vs. human academic writing.
These shift across model generations — current list reflects 2023–2025 patterns.

**Tier 1 — Strong indicators** (rare in human academic text):
- "delve into", "delves into"
- "the intricate/nuanced landscape of"
- "a testament to"
- "in the realm of"
- "a myriad of"
- "in today's rapidly evolving"
- "the ever-evolving landscape"
- "tapestry of"
- "indelible mark"
- "nestled" (outside geography contexts)

**Tier 2 — Moderate indicators** (humans use these, but AI overuses them):
- "it is worth noting that", "it should be noted that"
- "a comprehensive overview"
- "plays a crucial/pivotal role"
- "offers valuable insights into"
- "sheds light on", "paves the way for"
- "underscores the importance of"
- "meticulous", "vibrant", "groundbreaking", "profound"
- "showcasing", "exemplifies", "fostering", "enhancing"
- "commitment to [abstract noun]"
- "boasts a" (promotional register)

**Tier 3 — Weak indicators** (only flag if clustered with Tier 1–2):
- "Additionally" as sentence opener (overused by LLMs as transition)
- "Furthermore" / "Moreover" clustering (3+ per page)
- "align with", "highlighting", "ensuring"

**Scoring:** Count Tier 1 as 2 points, Tier 2 as 1 point, Tier 3 as 0.5 points.
Total 0–3 = normal. 4–8 = MINOR flag. 9+ = MAJOR flag.

### Copula Avoidance Pattern

LLMs systematically avoid simple "is/are" constructions, replacing them with:
- "serves as" instead of "is"
- "stands as" instead of "is"
- "represents" instead of "is"
- "features" / "offers" instead of "has"
- "marks a pivotal moment" instead of "is important"

**Flag:** MINOR if 5+ unnecessary copula replacements per page. Especially notable
when simple phrasing would be clearer.

### Negative Parallelism Pattern

LLMs overuse contrastive structures to appear balanced:
- "Not just X, but also Y"
- "It's not... it's..."
- "No X, no Y, just Z"
- "Beyond mere X, this represents Y"

**Flag:** MINOR if 3+ instances in a single paper.

### Rule of Three Overuse

LLMs default to triple structures (three adjectives, three examples, three items):
- "comprehensive, innovative, and groundbreaking"
- Every list has exactly three items
- Triple adjective sequences before nouns

**Flag:** MINOR if pattern is pervasive (5+ instances) and the triples feel mechanical
rather than rhetorical.

### Elegant Variation (Repetition Penalty)

LLMs avoid repeating the same word, cycling through synonyms even when
the original term is the clearest choice:
- A protein becomes "the molecule", "the key player", "the biological agent"
- A method becomes "the approach", "the technique", "the framework", "the paradigm"
- An author's name replaced with "the researcher", "the scholar", "the investigator"

**Flag:** MINOR if terminology inconsistency hinders clarity or introduces ambiguity.

### Structural Signals

- **Uniform paragraph length** — every paragraph is ~150–200 words with identical structure
  (topic sentence → elaboration → concluding sentence). Real academic writing has more variance.
- **No register shifts** — methodology, discussion, and introduction all read in the same tone.
  Human writers naturally shift register between sections.
- **Filler paragraphs** — paragraphs that sound substantive but convey no specific information.
  Test: can you remove the paragraph without losing any concrete claim or data point?
- **Excessive hedging chains** — "It could potentially be argued that this may suggest..."
  One hedge is normal; stacking 3+ in a sentence is a flag.
- **Perfect grammar with zero personality** — no idiolect, no stylistic quirks, no field-specific
  jargon that would indicate domain expertise.
- **"Challenges and Future" formula** — rigid structure where every topic ends with
  "Despite its [positive traits], [subject] faces challenges such as..." followed by
  speculation about future developments. Real papers have more nuanced discussion.
- **Section summaries** — recap paragraphs within sections restating what was just said.
  Human academic writers rarely summarize mid-section.
- **Significance overemphasis** — "marks a significant shift", "pivotal moment",
  "broader implications" attached to routine findings.

### Participle Attachment Pattern

LLMs attach present participles to factual statements to imply deeper meaning:
- "The study found X, **highlighting** the importance of Y"
- "Results showed Z, **underscoring** the need for W"
- "This method achieved 95% accuracy, **demonstrating** its superiority"

Human writers make these connections explicit with reasoning. LLMs use participles
as a shortcut to suggest significance without argument.

**Flag:** MINOR if 4+ instances. MAJOR if participles replace actual analysis.

### Citation Artifacts

Remnants of AI tool internals left in the text — strong evidence of LLM generation:

- `turn0search0`, `contentReference` tags
- `oaicite`, `oai_citation` markers
- `+1` or `attached_file` metadata strings
- `grok_card` references
- Markdown formatting in non-markdown contexts (`*text*`, `**bold**`)
- Knowledge-cutoff disclaimers ("as of my last training data...")
- Collaborative language ("Let me explain...", "As I understand...")

**Flag:** Any single artifact = MAJOR flag. These are definitive markers.

### Methodology Red Flags

- **Described but not executable** — methodology sounds detailed but lacks specific
  parameters, software versions, or exact procedures needed for replication.
- **Generic method names without specifics** — "advanced machine learning techniques" or
  "state-of-the-art deep learning models" without naming the actual architecture, hyperparameters,
  or training details.
- **Claims of novelty without positioning** — "to the best of our knowledge, this is the first
  study to..." without adequately explaining what prior work exists and why it falls short.
- **Vague attribution** — "industry reports suggest", "experts argue", "observers have cited"
  without naming specific sources.

### Results Red Flags

- **Suspiciously clean results** — no outliers, no unexpected findings, everything confirms the
  hypothesis perfectly. Real experiments are messier.
- **Round numbers everywhere** — p = 0.05, r = 0.80, accuracy = 95.0%. Real statistics
  produce irregular numbers.
- **No negative results mentioned** — every analysis supports the thesis. Real research
  encounters null findings.
- **Impossible statistics** — percentages that don't sum to 100, confidence intervals that
  don't contain the point estimate, degrees of freedom inconsistent with sample size.

## Paper Mill Indicators

Paper mills are a SEPARATE threat from AI-generated text. They use older paraphrasing
tools, not LLMs. See [tortured_phrases.md](tortured_phrases.md) for the full phrase list.

**Key paper mill signals:**
- Tortured phrases (machine-paraphrased technical terms)
- Suspiciously fast peer review (submitted and accepted within days)
- Boilerplate author affiliations (hospital + unrelated department)
- Figures with identical panel dimensions across different experiments
- Identical methodology sections across multiple papers by different "authors"
- References that all cluster in a narrow time window (suggesting bulk fabrication)

**Flag:** Any tortured phrase = MAJOR. Combined with predatory journal = HIGH risk.

## Scoring Rules

Count flags from all categories:

| Count | Risk Level |
|-------|-----------|
| 0–1 flags (all minor) | **LOW** |
| 2–4 flags OR 1 major | **MEDIUM** |
| 5+ flags OR >30% refs unfound OR >20% claims contradicted | **HIGH** |

When calculating risk, weight MAJOR flags as 2 and MINOR flags as 1.

## Important Caveats

Do NOT flag as AI slop based solely on:
- Non-native English writing (may resemble LLM patterns but for different reasons)
- Use of Grammarly or similar tools (polishes style but doesn't generate content)
- Standard academic phrases that happen to overlap with LLM patterns
  (e.g., "plays a crucial role" is also used by human researchers)
- Papers in fields with formulaic writing conventions (e.g., clinical trial reports,
  systematic reviews with rigid structure requirements)
- Text predating November 2022 (ChatGPT launch) — cannot be LLM-generated
- Individual occurrences of Tier 2/3 vocabulary — only flag density and co-occurrence

**Temporal note:** LLM vocabulary shifts across model versions. "Delve" peaked in 2023–2024
and declined in 2025+. Newer models are subtler. Weight structural and verifiable signals
more heavily than vocabulary alone, as vocabulary markers will become less reliable over time.

Always consider the **density** of signals, not individual occurrences.
A paper with 2 instances of "furthermore" is normal. A paper with "furthermore", "delve into",
"tapestry", "vibrant", "testament to", and "nestled" in the same introduction is not.
