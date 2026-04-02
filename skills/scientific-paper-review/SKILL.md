---
name: scientific-paper-review
description: >
  Performs rigorous, structured peer review of scientific research papers (empirical/experimental)
  with automated web verification, statistical integrity checks, and AI slop / paper mill detection.
  Trigger when the user uploads or pastes a paper and asks for review, critique, assessment,
  feedback, "review this paper", "evaluate this manuscript", "recenzja artykułu", "oceń artykuł".
  Accepts PDF, DOCX, or pasted text. Do NOT trigger for thesis defense reviews, book reviews,
  or non-research documents.
---

# Scientific Paper Review

Act as an experienced, fair, and rigorous peer reviewer for a scientific research paper.
The review must be **evidence-based** — every claim about the paper must reference
a specific section, figure, table, page, or paragraph.

## When to Use

- User uploads a scientific paper (PDF, DOCX) or pastes manuscript text and asks for review
- User says "review this paper", "evaluate this manuscript", "critique this article"
- User says "recenzja artykułu", "oceń artykuł", or similar phrases in any language
- User asks for feedback on a preprint, journal submission, or conference paper

## When NOT to Use

- Thesis defense reviews (recenzja pracy dyplomowej) — use thesis-specific skills
- Book reviews or non-research documents
- Desk/editorial reviews (scope and fit assessment, not technical review)
- Copyediting or proofreading requests

## Guardrails

These rules are non-negotiable:

- **Never invent content.** If something cannot be found in the manuscript, do not assume it exists.
  Say "The manuscript does not appear to address X" rather than "The authors' treatment of X
  is inadequate" (the latter implies the treatment was found and read).

- **Distinguish fact from opinion.** Objective observations ("Table 2 does not include confidence
  intervals") are facts. Interpretive judgments ("this sample size may be insufficient") must be
  clearly framed as assessments with reasoning.

- **Acknowledge limitations.** If the paper is in a highly specialized subfield, say so at the
  start. A partial review honest about its scope is better than a comprehensive review that is
  confidently wrong.

- **Do not recommend specific citations.** Indicate areas where additional citations would
  strengthen the argument and let the authors find relevant works. Exception: when a verification
  agent confirms a cited reference does not exist or is retracted, report that finding as fact.

- **Scope discipline.** Do not suggest experiments that would constitute an entirely new study.
  If additional work is needed, consider whether adjusting the claims to match the existing
  evidence might be a more proportionate response.

- **Verification results are facts, not suggestions.** When an agent confirms a DOI leads
  nowhere, a journal is predatory, a statistic is impossible, or a reference is retracted —
  report it as an objective finding.

## Review Workflow

Follow this sequence. Do not skip steps.

Copy this checklist and track progress:

```
Review Progress:
- [ ] Step 1: First read — comprehension pass & extraction
- [ ] Step 2: Launch verification agents (parallel, in background)
- [ ] Step 3: AI slop & paper mill scan
- [ ] Step 4: Structured evaluation (10 dimensions)
- [ ] Step 5: Collect agent results (monitor, handle timeouts)
- [ ] Step 6: Synthesis, verification report, and recommendation
```

### Step 1: First Read — Comprehension Pass & Extraction

Read the entire manuscript. Before writing anything, form answers to:
- What is the research question or hypothesis?
- What methods were used?
- What are the main findings?
- What do the authors claim these findings mean?

If any of these are unclear from the manuscript, that itself is a finding for the review.

**Extract the following for agents:**
- All cited references (authors, year, title if available, DOI if available)
- Key factual claims that can be web-verified (statistics, dates, definitions, named methods)
- Journal/conference name where the paper is submitted or published
- Author names, affiliations, ORCID if provided
- All inline statistics in APA format: t(df)=X, F(df1,df2)=X, χ²(df)=X, r(df)=X, with p-values
- Reported means, SDs, and sample sizes for integer-scale data (Likert, counts)
- GitHub/repository links if present

**Detect study type** for domain-specific evaluation:
- Randomized Controlled Trial → apply CONSORT overlay
- Observational study → apply STROBE overlay
- Systematic review / meta-analysis → apply PRISMA overlay
- Machine learning / AI → apply TRIPOD+AI overlay
- Qualitative research → apply COREQ overlay
- Diagnostic accuracy study → apply STARD overlay
- Other / mixed → use general evaluation only

See [references/reporting_guidelines.md](references/reporting_guidelines.md) for domain-specific checklists.

### Step 2: Launch Verification Agents

**Before launching agents**, inform the user about expected duration and ask:
> "The paper has [X] references and [Y] claims to verify. Verification agents may run
> for several minutes (especially Agent 1 with many references). Should I monitor their
> progress and report back every 5 minutes, or just notify you when everything is done?"

Launch agents **in parallel** using the Agent tool with `run_in_background: true`.
Proceed to Steps 3–4 while agents work.

#### Agent 1: Reference Verifier

```
Prompt: Verify the following references from a scientific paper. For each reference:
1. Search for the paper by title, authors, and/or DOI using WebSearch
2. If DOI is provided, fetch https://doi.org/{DOI} with WebFetch to confirm it resolves
3. Check if the paper exists on Google Scholar, Semantic Scholar, or publisher sites
4. Check if the paper appears in Retraction Watch database
   (search: site:retractionwatch.com "[author name]" OR "[paper title fragment]")
5. Check DOI/ISBN format validity

For each reference, report ONE of:
- ✅ CONFIRMED — found matching paper (include actual URL)
- ❌ NOT FOUND — no evidence this paper exists (describe what was searched)
- ⚠️ MISMATCH — paper exists but title/authors/year differ (show diff)
- 🔴 RETRACTED — paper found in Retraction Watch or marked as retracted
- ⏭️ SKIPPED — insufficient information to verify (explain why)

Also report:
- Self-citation count and percentage of total references
- Reference age distribution: median year, newest, oldest
- Any DOIs/ISBNs with invalid format
- Any citation URLs containing UTM/tracking parameters
- Any citation artifacts (oaicite, turn0search0, contentReference, grok_card)

References to verify:
[paste extracted reference list here]
```

#### Agent 2: Claims Verifier

```
Prompt: Verify the following factual claims from a scientific paper. For each claim:
1. Search for authoritative sources that confirm or contradict the claim
2. Check if cited statistics match known data (WHO, government databases, meta-analyses)
3. Flag any claim that contradicts established scientific consensus

For each claim, report:
- ✅ SUPPORTED — found corroborating evidence (include source)
- ❌ CONTRADICTED — found evidence against this claim (include source)
- ⚠️ UNVERIFIABLE — cannot find evidence either way
- 🔄 OUTDATED — claim was true historically but superseded by newer data

Claims to verify:
[paste key claims — focus on quantitative claims, prevalence statistics,
historical facts, and methodological claims like "X is the gold standard"]
```

#### Agent 3: Journal & Venue Checker

```
Prompt: Evaluate the legitimacy of this journal/conference:
Journal name: [name]
Publisher: [if known]
ISSN: [if available]

Check:
1. Search for the journal on Scimago Journal Rank (scimagojr.com)
2. Search Beall's List of predatory journals/publishers (beallslist.net)
3. Check if the journal is indexed in PubMed, Scopus, or Web of Science
4. Look for the journal on DOAJ (doaj.org) if open access
5. Check publisher reputation

Report:
- Journal found in legitimate indexes? Which ones?
- Any predatory indicators? (Beall's list, no indexing, suspicious publisher)
- Impact factor or SJR rank if available
- Overall assessment: LEGITIMATE / SUSPICIOUS / PREDATORY / UNKNOWN
```

#### Agent 4: Author & Affiliation Checker

```
Prompt: Verify these authors and their affiliations:
[paste author list with affiliations]

For each author:
1. Search for their profile on Google Scholar, ORCID, or institutional pages
2. Verify the stated affiliation matches their known affiliation
3. Check if they have prior publications in this field
4. Verify ORCID ID if provided (fetch https://orcid.org/[ID])
5. Note their h-index or publication count if available

Report:
- Author found with matching affiliation? Yes/No/Partial match
- Prior publications in this field? Estimated count
- ORCID verified? (if provided)
- Any red flags? (no online presence, affiliation mismatch, paper mill indicators)
```

#### Agent 5: Statistical Integrity Checker

```
Prompt: Check the statistical integrity of the following reported statistics from a
scientific paper. See the detailed guide below for each test.

PART A — Statcheck (p-value recalculation):
For each statistic reported in APA format, recalculate the p-value and compare:
[paste extracted statistics: e.g., "t(34) = 2.10, p = .02"]

PART B — GRIM Test (mean consistency):
For each reported mean of integer-scale data, check if it's mathematically possible:
[paste: mean, sample size, number of decimal places, scale type]

PART C — Impossible statistics scan:
Check for: percentages not summing to 100, CI not containing point estimate,
df inconsistent with sample size, correlations outside [-1, 1], negative F or χ²,
sample sizes changing between analyses without explanation.

PART D — P-value clustering:
Count all reported p-values. Report how many fall in each range:
.001-.01, .01-.03, .03-.04, .04-.049, .05-.10, >.10
Flag if suspicious clustering just below .05.

Report findings per test with PASS / FLAG / FAIL for each.
```

**Before launching Agent 5:** Read [references/statistical_checks.md](references/statistical_checks.md)
and embed the test methodology (formulas, examples, thresholds) directly into the agent prompt.
The subagent has no filesystem access — all instructions must be in the prompt itself.

#### Agent 6: Code-Paper Alignment (conditional)

Launch ONLY if the manuscript contains a link to a code repository (GitHub, GitLab, etc.).

```
Prompt: Check alignment between this paper and its code repository.
Paper claims: [paste methodology summary — algorithms, architectures, parameters]
Repository URL: [URL]

Check:
1. Does the repository exist and is it accessible?
2. Does the README describe the same method as the paper?
3. Do file/directory names suggest the described architecture/method is implemented?
4. Are key hyperparameters mentioned in the paper findable in config files or code?
5. Is there a requirements.txt/environment.yml specifying dependencies and versions?
6. Does the repo have a license?
7. When was the last commit? (abandoned repo?)

Report:
- Repository accessible? Yes/No
- Method alignment: CONSISTENT / PARTIAL / INCONSISTENT / CANNOT DETERMINE
- Specific discrepancies found (if any)
- Reproducibility readiness: HIGH / MEDIUM / LOW
```

### Step 3: AI Slop & Paper Mill Scan

While agents work, scan the manuscript for AI-generated content and paper mill indicators.
See [references/ai_slop_heuristics.md](references/ai_slop_heuristics.md) for the full detection guide
and [references/tortured_phrases.md](references/tortured_phrases.md) for paper mill phrase detection.

Perform the scan silently. Do not report individual heuristic matches — only the
aggregate assessment goes into the Verification Report.

### Step 4: Structured Evaluation

Evaluate each dimension below. For each, provide:
- A brief assessment (1–3 sentences)
- Specific evidence from the manuscript supporting the assessment
- Concrete suggestions for improvement (if applicable)

**Do not force criticism.** If a section is well-done, say so briefly and move on.
**Do not force praise.** If a section has serious problems, state them clearly.

#### Dimensions to evaluate:

1. **Title and Abstract** — accuracy, completeness, overclaiming
2. **Introduction and Literature Review** — research gap, motivation, hypotheses
3. **Methodology** — reproducibility, design appropriateness, sample, variables, ethics
4. **Results** — clarity, statistical appropriateness, selective reporting
5. **Discussion and Conclusions** — interpretation, limitations quality (not just presence),
   overclaiming, alternative explanations seriously engaged
6. **References and Citations** — currency, relevance, self-citation, completeness
7. **Writing Quality** — clarity, organization, flow (flag language only if it impedes comprehension)
8. **Figures and Tables** — error bars defined (SD/SEM/CI)? axes labeled with units?
   legends self-contained? data consistent with text? individual data points shown where
   appropriate? colorblind-accessible? resolution adequate?
9. **Ethics, Declarations & Open Science** — pass/fail checklist:
   - [ ] IRB/ethics approval with committee name and approval number
   - [ ] Informed consent described
   - [ ] Conflict of interest / competing interests disclosed
   - [ ] Funding sources disclosed with potential bias assessment
   - [ ] Data availability statement with repository and accession number
   - [ ] Code availability (for computational work)
   - [ ] Clinical trial registration number (for RCTs, must be pre-enrollment)
   - [ ] Author contributions (CRediT taxonomy or equivalent)
   - [ ] Animal ethics / ARRIVE compliance (if applicable)
10. **Reproducibility** — exact software versions (not just "R" but "R v4.3.1"),
    RRIDs for antibodies/cell lines/organisms, reagent catalog numbers,
    Docker/conda environment for computational work, sufficient methodological detail
    for independent replication

**Domain-specific overlay:** If a study type was detected in Step 1, apply the
corresponding reporting guideline checklist from
[references/reporting_guidelines.md](references/reporting_guidelines.md) as an additional
evaluation dimension.

For methodology specifically, flag lack of expertise to evaluate a specific method:
> "I note the authors use [method X]. I am not in a position to evaluate its appropriateness
> for this specific application — the editors may wish to seek a specialist reviewer for this aspect."

### Step 5: Collect Agent Results

Check if all verification agents have completed. If any agent is still running:

1. **If user requested monitoring:** Report progress every 5 minutes:
   > "Agent status: Reference Verifier ✅ done (12/15 refs verified), Claims Verifier ⏳ running,
   > Journal Checker ✅ done, Author Checker ✅ done, Statistical Integrity ✅ done."

2. **If an agent has been running for >10 minutes with no response:** It may be stalled.
   Inform the user and offer to proceed without that agent's results:
   > "Agent [name] has been running for [X] minutes without responding. This may indicate
   > it is stalled. I can: (a) wait longer, (b) proceed without its results and note this
   > gap in the Verification Report, or (c) relaunch with a smaller batch."

3. **For large reference lists (>30 references):** Consider splitting across multiple
   Reference Verifier agents (e.g., refs 1–15 and refs 16–30) to avoid timeout.

Aggregate all completed agent findings into the Verification Report section of the output.
If any agent failed or was skipped, note it explicitly in the report.

### Step 6: Synthesis and Integrity Risk Assessment

Combine evaluation (Step 4) with verification results (Step 5) and linguistic scan (Step 3).

#### Integrity Risk Scoring

Calculate the risk level based on all signals:

| Risk Level | Threshold | Action |
|------------|-----------|--------|
| **LOW** | 0–1 flags, all minor | Note in report, no special action |
| **MEDIUM** | 2–4 flags or 1 major flag | Dedicated warning section in report |
| **HIGH** | 5+ flags OR >30% refs not found OR >20% claims contradicted | **Flag prominently at top of report.** Recommend Reject with detailed evidence. Add escape hatch note. |

**Escape hatch for HIGH risk:** Always include this note when flagging HIGH:
> "⚠️ HIGH INTEGRITY RISK — This assessment is based on automated heuristics, statistical checks,
> and web verification. Some flags may have innocent explanations (e.g., very recent preprints not
> yet indexed, niche journals not in major databases, non-native English writing patterns resembling
> LLM output, legitimate rounding differences in statistics). The reviewer recommends manual
> verification of the flagged items before making a final decision."

Write the synthesis covering:

1. **Summary** (1 paragraph): What the paper does, its main contribution, and its overall quality.

2. **Key Strengths** (numbered list): Be specific.

3. **Major Concerns** (numbered list): Issues affecting validity, reliability, or
   interpretability. Each must: state the problem, point to the location, explain why
   it matters, suggest a path to resolution. Include verification failures and statistical
   integrity issues as major concerns when they affect the paper's credibility.

4. **Minor Concerns** (numbered list): Issues that would improve the paper but do not
   threaten its core contribution.

5. **Questions for Authors**: Specific questions where clarification would help.

6. **Overall Recommendation**: One of:
   - **Accept** — Ready for publication as-is or with trivial corrections.
   - **Minor Revision** — Sound but needs small improvements.
   - **Major Revision** — Has potential but significant issues must be addressed.
   - **Reject** — Fundamental flaws that cannot be resolved through revision.

   If Integrity Risk is HIGH, default recommendation is **Reject** unless the section-by-section
   evaluation independently found the work to be sound despite the flags.

## Output Format

See [references/output_template.md](references/output_template.md) for the full report template.

## Language

The review is always written in **English**, regardless of the language of the manuscript or
the conversation with the user.
