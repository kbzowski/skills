# Domain-Specific Reporting Guidelines

Apply the relevant checklist based on the study type detected in Step 1.
Only evaluate items that can be assessed from the manuscript text.

## How to Use

1. Detect study type during Step 1 (First Read)
2. Load the corresponding checklist below
3. Add a "Reporting Guideline Compliance" section to the evaluation (Step 4)
4. Report as pass/fail for each applicable item
5. If study type is unclear or mixed, use only General Evaluation

## CONSORT — Randomized Controlled Trials

Essential items to check:

- [ ] **Trial registration** — registration number and registry name, registered BEFORE enrollment
- [ ] **Protocol** — published or available? Deviations from protocol described?
- [ ] **Randomization sequence** — method of generation described (computer-generated, etc.)
- [ ] **Allocation concealment** — mechanism described (sealed envelopes, central pharmacy, etc.)
- [ ] **Implementation** — who generated sequence, who enrolled, who assigned
- [ ] **Blinding** — who was blinded (participants, caregivers, assessors)? How was blinding maintained?
- [ ] **CONSORT flow diagram** — enrollment, allocation, follow-up, analysis numbers at each stage
- [ ] **Attrition** — dropouts per group with reasons
- [ ] **Intention-to-treat analysis** — primary analysis includes all randomized participants
- [ ] **Per-protocol analysis** — reported alongside ITT as sensitivity analysis
- [ ] **Sample size calculation** — a priori power analysis with assumed effect size, alpha, power
- [ ] **Primary outcome** — clearly defined, pre-specified, timepoint stated
- [ ] **Harms** — adverse events reported per group
- [ ] **Baseline table** — participant characteristics by group with no p-values (CONSORT discourages them)

## STROBE — Observational Studies (cohort, case-control, cross-sectional)

Essential items to check:

- [ ] **Study design** — stated in title or abstract (cohort, case-control, cross-sectional)
- [ ] **Setting** — locations, dates of recruitment/follow-up/data collection
- [ ] **Participants** — eligibility criteria, sources, methods of selection
- [ ] **Participation rate** — number at each stage with reasons for non-participation
- [ ] **Variables** — all variables defined: outcomes, exposures, predictors, confounders, effect modifiers
- [ ] **Bias** — efforts to address potential sources of bias described
- [ ] **Confounders** — which confounders considered, how measured, how adjusted for
- [ ] **Missing data** — number with missing data per variable, methods for handling
- [ ] **Sensitivity analyses** — performed to assess robustness
- [ ] **Selection bias discussion** — acknowledged and assessed in limitations

## PRISMA 2020 — Systematic Reviews & Meta-Analyses

Essential items to check:

- [ ] **Protocol registration** — PROSPERO number or other registry, deviations noted
- [ ] **Eligibility criteria** — PICO(S) clearly stated
- [ ] **Search strategy** — full search string for at least one database, reproducible
- [ ] **Databases searched** — all sources listed with dates of coverage
- [ ] **Study selection** — independent screening by 2+ reviewers? Disagreement resolution?
- [ ] **Data extraction** — process described, independent by 2+ reviewers?
- [ ] **Risk of bias assessment** — tool named (RoB 2, ROBINS-I, Newcastle-Ottawa, etc.)
- [ ] **Risk of bias results** — per-study assessments shown (not just summary)
- [ ] **PRISMA flow diagram** — identification, screening, eligibility, included counts
- [ ] **Synthesis method** — fixed vs. random effects model justified
- [ ] **Heterogeneity** — I², Q statistic, prediction intervals
- [ ] **Publication bias** — assessed (funnel plot, Egger's test, trim-and-fill)
- [ ] **Certainty of evidence** — GRADE or equivalent applied
- [ ] **Excluded studies** — list with reasons (or in supplement)

## TRIPOD+AI — Machine Learning / AI Studies

Essential items to check:

- [ ] **Task definition** — clearly specified prediction task, target variable
- [ ] **Data source** — origin, collection dates, inclusion/exclusion criteria
- [ ] **Data splitting** — train/validation/test split described, temporal or random?
- [ ] **Data leakage prevention** — preprocessing fit on training set only? No target leakage?
- [ ] **Model architecture** — specific model named (not just "deep learning" or "ML")
- [ ] **Hyperparameters** — reported with selection strategy (grid search, Bayesian, etc.)
- [ ] **Cross-validation** — strategy described if used (k-fold, LOOCV, etc.)
- [ ] **Performance metrics** — appropriate for task (not just accuracy for imbalanced data)
- [ ] **Confidence intervals / uncertainty** — reported for performance metrics
- [ ] **Comparison baselines** — compared against relevant existing methods
- [ ] **Code availability** — code and environment shared for reproducibility
- [ ] **Class distribution** — reported for classification tasks
- [ ] **Feature importance / interpretability** — provided for non-trivial models
- [ ] **Failure analysis** — where does the model fail? Error analysis provided?
- [ ] **External validation** — tested on independent dataset (not just test split)?

## COREQ — Qualitative Research

Essential items to check:

- [ ] **Researcher positionality** — relationship to participants, credentials, assumptions stated
- [ ] **Theoretical framework** — methodological orientation described (grounded theory, IPA, etc.)
- [ ] **Sampling strategy** — purposive, snowball, theoretical? Justified?
- [ ] **Sample size justification** — saturation described? How determined?
- [ ] **Data collection** — method (interviews, focus groups, observations), duration, setting
- [ ] **Interview guide** — provided or described? Pilot tested?
- [ ] **Recording and transcription** — audio/video recorded? Transcription method?
- [ ] **Coding process** — who coded, how many coders, inter-coder reliability
- [ ] **Themes derivation** — inductive, deductive, or hybrid? Process described?
- [ ] **Member checking** — findings verified with participants?
- [ ] **Reflexivity** — researcher's influence on findings discussed?
- [ ] **Transferability** — thick description provided for readers to assess applicability?

## STARD — Diagnostic Accuracy Studies

Essential items to check:

- [ ] **Index test** — described in sufficient detail to replicate
- [ ] **Reference standard** — described, justified as appropriate gold standard
- [ ] **Blinding** — were index test assessors blinded to reference results and vice versa?
- [ ] **Participants** — consecutive or random sample from relevant clinical population?
- [ ] **2×2 table** — true positives, false positives, true negatives, false negatives reported
- [ ] **Sensitivity and specificity** — with confidence intervals
- [ ] **Predictive values** — PPV and NPV reported with prevalence context
- [ ] **Indeterminate results** — how handled? Excluded or included?
- [ ] **STARD flow diagram** — eligible, enrolled, index test, reference standard, analyzed

## Reporting Format

Add this section to the evaluation output:

```
### Reporting Guideline Compliance: [GUIDELINE NAME]
Study type: [detected type]
Items assessed: X/Y
- ✅ [Item] — Present and adequate
- ⚠️ [Item] — Present but insufficient ([what's missing])
- ❌ [Item] — Missing entirely
- N/A [Item] — Not applicable to this study

Compliance rate: X/Y assessed items (Z%)
Critical missing items: [list items whose absence threatens validity]
```
