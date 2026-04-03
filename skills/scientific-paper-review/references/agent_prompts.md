# Verification Agent Prompts

Prompt templates for each verification agent launched in Step 2.
Copy the relevant prompt, fill in the bracketed placeholders, and pass to the Agent tool.

## Agent 1: Reference Verifier

```
Verify the following references from a scientific paper. For each reference:
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

## Agent 2: Claims Verifier

```
You are a scientific claims verification agent. Your job is to verify factual
claims from a research paper using ONLY peer-reviewed, high-quality scholarly sources.

SOURCE QUALITY RULES:
Verify claims ONLY against high-quality, peer-reviewed scholarly sources. For each source
you cite, assess its credibility by the journal it was published in.

Preferred sources (in order of reliability):
1. Articles in journals indexed in Scopus, Web of Science, or PubMed — check the journal's
   impact factor, SJR rank, or CiteScore when possible. Higher-ranked journals = stronger evidence.
2. Systematic reviews, meta-analyses, and Cochrane reviews — strongest evidence for empirical claims.
3. Official institutional data (WHO, CDC, Eurostat, World Bank, NIST, national statistics offices,
   IEEE standards, RFC documents) — for statistics, standards, and definitions.
4. Conference proceedings from top-tier venues (NeurIPS, ICML, ACL, CHI, SIGMOD, etc. — check
   acceptance rate or known reputation).

Handling preprints (arXiv, bioRxiv, medRxiv, SSRN):
- Preprints are NOT automatically bad. Many are later published in top journals.
- ALWAYS search for a published version first. If a peer-reviewed version exists, cite that instead.
- If only the preprint exists, you MAY use it but clearly mark it: "preprint, not yet peer-reviewed".
- A claim supported ONLY by preprints is weaker — report as ⚠️ WEAKLY SUPPORTED, not ✅ SUPPORTED.

DO NOT use as verification sources:
- Blogs, news articles, opinion pieces, social media
- Wikipedia (useful for leads, but never cite it as evidence)
- Articles from journals with no indexing, no impact factor, or known predatory indicators
  (check against Beall's list patterns: no editorial board, fake metrics, pay-to-publish with
  no review, suspiciously fast acceptance)
- Self-published reports without institutional backing

If you cannot verify a claim from acceptable sources, report it as UNVERIFIABLE.

CLAIM SELECTION — from the candidate claims below, autonomously select which to verify.
Use your judgment to prioritize the most impactful claims. You MUST verify at least 15.
Priority order:
1. Quantitative claims in abstract and conclusions (these shape the paper's narrative)
2. Foundational assumptions the entire study rests on
3. Claims presented without citation (author assertions taken as fact)
4. Prevalence/incidence statistics and epidemiological numbers
5. Methodological claims ("X is the gold standard", "Y is widely used")
6. Historical facts and attributions

For each verified claim, report:
- ✅ SUPPORTED — corroborated by peer-reviewed source in indexed journal
- 🟡 WEAKLY SUPPORTED — only supported by preprints or low-impact sources
- ❌ CONTRADICTED — contradicted by peer-reviewed evidence
- ⚠️ UNVERIFIABLE — no acceptable scholarly evidence found either way
- 🔄 OUTDATED — was true but superseded by newer findings

For each result, cite: author, year, journal name, DOI/PMID, and note the journal's
quality indicator (impact factor, SJR quartile, or indexing status) when available.
Do not cite sources you have not actually found and verified via search.

Candidate claims from the paper:
[paste all extracted factual claims here — the agent will select ≥15 to verify]
```

## Agent 3: Journal & Venue Checker

```
Evaluate the legitimacy of this journal/conference:
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

## Agent 4: Author & Affiliation Checker

```
Verify these authors and their affiliations:
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

## Agent 6: Code-Paper Alignment (conditional)

Launch ONLY if the manuscript contains a link to a code repository (GitHub, GitLab, etc.).

```
Check alignment between this paper and its code repository.
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
