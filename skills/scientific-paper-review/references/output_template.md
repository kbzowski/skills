# Peer Review Report Template

Use this exact structure for the review output.

If Integrity Risk is HIGH, insert the risk banner immediately after the title, before Summary.

```
## Peer Review Report

[If HIGH risk, insert here:]
> ⚠️ **HIGH INTEGRITY RISK** — Automated verification flagged significant integrity concerns.
> See Verification Report below for details. Manual confirmation recommended before
> making a final editorial decision.

### Summary
[1 paragraph]

### Section-by-Section Evaluation

#### Title and Abstract
[assessment]

#### Introduction and Literature Review
[assessment]

#### Methodology
[assessment]

#### Results
[assessment]

#### Discussion and Conclusions
[assessment]

#### References and Citations
[assessment]

#### Writing Quality and Presentation
[assessment]

#### Figures and Tables
[assessment — error bars, axes, legends, data consistency, accessibility]

#### Ethics, Declarations & Open Science
- IRB/Ethics approval: ✅/❌ [details]
- Informed consent: ✅/❌/N/A
- Conflict of interest: ✅/❌
- Funding disclosure: ✅/❌
- Data availability: ✅/❌ [repository if provided]
- Code availability: ✅/❌/N/A [repository if provided]
- Trial registration: ✅/❌/N/A [number if provided]
- Author contributions: ✅/❌
- Animal ethics (ARRIVE): ✅/❌/N/A

#### Reproducibility
[software versions, RRIDs, reagent details, environment specification assessment]

#### Reporting Guideline Compliance: [GUIDELINE NAME if applicable]
Study type: [detected type]
Items assessed: X/Y
[per-item ✅/⚠️/❌/N/A assessment]
Compliance rate: X/Y (Z%)
Critical missing items: [list]

### Verification Report

#### References Verified: X/Y
[For each checked reference, one line:]
- ✅ [Author Year] — Confirmed (URL or DOI)
- ❌ [Author Year] — Not found (search details)
- ⚠️ [Author Year] — Mismatch: cited as "Title A", actual paper is "Title B"
- 🔴 [Author Year] — RETRACTED (Retraction Watch / publisher notice)
- ⏭️ [Author Year] — Skipped (reason)

Self-citation rate: X/Y (Z%)
Reference age: median [year], range [oldest]–[newest]
DOI/ISBN format issues: [list or "none"]
Citation artifacts found: [list or "none"]

#### Key Claims Verified: X/Y
- ✅ "claim text" — Supported by [author, year, journal (IF/SJR), DOI]
- 🟡 "claim text" — Weakly supported, preprint only: [source]
- ❌ "claim text" — Contradicted by [author, year, journal (IF/SJR), DOI]
- ⚠️ "claim text" — Unverifiable (no acceptable scholarly sources found)
- 🔄 "claim text" — Outdated, superseded by [newer finding, DOI]

#### Journal/Venue Assessment
- Indexed in: [list databases]
- Predatory indicators: [none / list findings]
- Assessment: LEGITIMATE / SUSPICIOUS / PREDATORY / UNKNOWN

#### Author Verification
[For each author, one line:]
- [Name] — [affiliation status], [ORCID status], [publication history summary]

#### Statistical Integrity
[For each test performed:]

**Statcheck (p-value recalculation):** PASS / FLAG / FAIL
- [Details of any inconsistencies found, with locations]
- Gross inconsistencies (crossing .05 boundary): [count]

**GRIM Test (mean consistency):** PASS / FLAG / FAIL / N/A
- [Details of any impossible means found]

**Impossible Statistics:** PASS / FLAG / FAIL
- [List any mathematical impossibilities]

**P-Value Distribution:** PASS / FLAG / FAIL
- Distribution: [counts per bin]
- Suspicious clustering at .04–.049: [yes/no]

**Baseline Balance (RCTs only):** PASS / FLAG / FAIL / N/A
- [Assessment of Table 1 balance]

#### Code-Paper Alignment (if repository provided)
- Repository: [URL] — accessible? [yes/no]
- Method alignment: CONSISTENT / PARTIAL / INCONSISTENT
- Reproducibility readiness: HIGH / MEDIUM / LOW
- [Specific discrepancies if any]

#### AI Slop & Paper Mill Scan
- LLM marker phrases: [count by tier] (Tier 1: X, Tier 2: Y, Tier 3: Z)
  Weighted vocabulary score: [number]
- Tortured phrases found: [count] ([list if any — each is MAJOR])
- Copula avoidance instances: [count]
- Negative parallelisms: [count]
- Elegant variation issues: [count]
- Participle attachment pattern: [count]
- Structural signals: [list any detected]
- Methodology red flags: [list any detected]
- Results red flags: [list any detected]
- Citation artifacts: [list any detected]

#### Integrity Risk Assessment: [LOW / MEDIUM / HIGH]
- Verifiable flags: [count] ([list])
- Linguistic flags: [count] ([list])
- Statistical flags: [count] ([list])
- Paper mill indicators: [count] ([list])
- Total weighted score: [number]

[If HIGH:]
> ⚠️ HIGH INTEGRITY RISK — This assessment is based on automated heuristics, statistical checks,
> and web verification. Some flags may have innocent explanations (e.g., very recent preprints not
> yet indexed, niche journals not in major databases, non-native English writing patterns resembling
> LLM output, legitimate rounding differences in statistics). The reviewer recommends manual
> verification of the flagged items before making a final decision.

### Key Strengths
1. ...
2. ...

### Major Concerns
1. **[Short label]** — [Detailed description with manuscript references]
2. ...

### Minor Concerns
1. ...
2. ...

### Questions for Authors
1. ...
2. ...

### Overall Recommendation
[Accept / Minor Revision / Major Revision / Reject] — [justification]
[If HIGH Integrity Risk, explain how verification findings influenced the recommendation]
```
