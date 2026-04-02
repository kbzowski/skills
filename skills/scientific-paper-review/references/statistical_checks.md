# Statistical Integrity Checks

Detailed instructions for Agent 5: Statistical Integrity Checker.
These tests work from paper text alone — no raw data access needed.

## Test A: Statcheck (P-Value Recalculation)

**What:** Recalculate p-values from reported test statistics and degrees of freedom.
**Accuracy:** 96.2–99.9% in validation studies.

### How to perform

1. Extract all APA-formatted statistics from the text:
   - `t(df) = value, p = value`
   - `F(df1, df2) = value, p = value`
   - `χ²(df) = value, p = value`
   - `r(df) = value, p = value`
   - `Z = value, p = value`

2. For each, recalculate the p-value:
   - t-test: p from t-distribution with stated df
   - F-test: p from F-distribution with stated df1, df2
   - Chi-square: p from χ² distribution with stated df
   - Correlation: convert r to t = r × sqrt(df / (1 - r²)), then use t-distribution

3. Compare recalculated p with reported p. Flag:
   - **MINOR inconsistency:** reported and recalculated p differ but both on the same side of .05
   - **GROSS inconsistency:** reported p < .05 but recalculated p > .05 (or vice versa)
     This is the critical finding — it means significance was misreported.

4. Account for rounding: test statistic may be rounded, so recalculate with ±0.5
   in the last decimal place and check if any value in that range produces a matching p.

### Limitations
- Cannot determine one-tailed vs. two-tailed (assume two-tailed by default)
- Only catches inline statistics, not those only in tables
- Rounding of test statistics introduces uncertainty

## Test B: GRIM Test (Granularity-Related Inconsistency of Means)

**What:** Check if a reported mean is mathematically possible given the sample size,
for integer-valued data (Likert scales, counts, yes/no).
**Sensitivity:** >83%. **Specificity:** >96%.

### How to perform

1. Identify means reported for integer-scale variables:
   - Likert scales (1–5, 1–7, etc.)
   - Count data
   - Binary (0/1) data
   - Age in whole years

2. For each: multiply the reported mean by the sample size N.
   The result must be an integer (within rounding tolerance).

3. Rounding tolerance: if mean is reported to D decimal places,
   acceptable deviation = 0.5 × 10^(-D).

**Example:** Mean = 3.47, N = 10, Likert 1–5 scale.
3.47 × 10 = 34.7 → not an integer → **GRIM INCONSISTENT**.
Possible means for N=10: 3.0, 3.1, 3.2, ..., 3.4, 3.5, ... (steps of 0.1).
3.47 cannot arise from 10 integers.

### When GRIM applies
- Only for integer-valued underlying data
- Most useful when N < 100 (for 2 decimal places)
- N < 1000 for 3 decimal places
- Does NOT apply to continuous measurements (height, weight, reaction time)

### GRIMMER extension (SD check)
Same principle applied to standard deviations. The variance × (N-1) must be
an integer for integer data. More complex to compute but catches additional fabrication.

## Test C: Impossible Statistics Scan

Check for values that are mathematically impossible or highly implausible.

| Check | What's impossible |
|-------|------------------|
| Correlation | r > 1.0 or r < -1.0 |
| F-statistic | F < 0 |
| Chi-square | χ² < 0 |
| Percentages | Do not sum to 100% (±1% rounding tolerance) |
| Confidence interval | Does not contain the point estimate |
| Degrees of freedom | df inconsistent with N (e.g., independent t-test: df should be N₁+N₂-2) |
| Sample size drift | N changes between analyses without explanation (e.g., N=120 in methods, N=108 in results with no mention of exclusions) |
| SD = 0 | Zero variance in a measured variable (possible but needs explanation) |
| Negative variance | Reported SD² < 0 or negative variance components |

## Test D: P-Value Distribution Analysis

**What:** Check if the distribution of p-values suggests p-hacking (selective reporting,
optional stopping, or analytical flexibility to achieve p < .05).

### How to perform

1. Extract ALL reported p-values from the paper (including non-significant ones).

2. Count p-values in each bin:
   - .001–.01 (highly significant)
   - .01–.03 (significant)
   - .03–.04 (significant)
   - .04–.049 (barely significant — the "p-hacking zone")
   - .05–.10 (marginally significant / non-significant)
   - > .10 (non-significant)

3. Red flags:
   - **Cluster at .04–.049:** If >30% of significant results fall here, flag.
   - **No results above .05:** If paper reports 10+ tests and ALL are significant,
     selective reporting is likely.
   - **All key results barely significant:** If every hypothesis test yields
     p = .04x, this is extremely unlikely by chance.

### Limitations
- A few p-values near .05 can happen legitimately
- Some extracted p-values may be from manipulation checks, covariates, or control analyses
  (not all are hypothesis tests)
- More reliable with more p-values (10+)
- Single-paper analysis is suggestive, not definitive

## Test E: Baseline Balance Check (for RCTs only)

**What:** In randomized controlled trials, check if baseline characteristics across
groups are suspiciously perfectly balanced (suggests data fabrication or failed randomization).

### How to perform

1. Find Table 1 (usually baseline characteristics by group).
2. Check group-comparison p-values. If ALL p-values are very high (>.50) across
   many variables (10+), this is suspicious — genuine randomization produces
   some imbalance by chance.
3. Also flag if ALL p-values are very low (<.05) — suggests systematic difference
   between groups (failed randomization or fabrication).

### Carlisle method
For each baseline variable: calculate the probability of observing the reported
difference given the reported means, SDs, and Ns. If the combined probability across
all variables is extremely low, flag.

## Reporting Format

For each test, report:

```
### Statistical Integrity: [Test Name]
Status: PASS / FLAG / FAIL
Findings: [specific details]
Affected statistics: [list with locations in manuscript]
```

Severity guide:
- **PASS:** No issues found
- **FLAG:** Potential issue, could be rounding or reporting error (MINOR)
- **FAIL:** Clear mathematical impossibility or gross inconsistency (MAJOR)
