# Evaluation Scenarios

Test the skill against these scenarios to verify correct behavior.

## Eval 1: Paper with known statistical errors

**Input:** A paper containing:
- `t(34) = 2.10, p = .02` (correct)
- `t(34) = 1.80, p = .02` (gross inconsistency — recalculated p ≈ .08)
- A mean of 3.47 with N=10 on a Likert scale (GRIM-inconsistent)

**Expected behavior:**
- statcheck detects the gross inconsistency on the second statistic
- GRIM test flags the impossible mean
- Both appear as MAJOR flags in the Integrity Risk Assessment
- Overall recommendation reflects the statistical integrity issues

## Eval 2: Paper with tortured phrases and LLM markers

**Input:** A paper containing:
- "profound learning" (tortured phrase for "deep learning")
- "sham neural system" (tortured phrase for "artificial neural network")
- Multiple Tier 1 LLM markers: "delves into", "tapestry of", "a testament to"
- A `turn0search0` citation artifact

**Expected behavior:**
- scan_phrases detects both tortured phrases as MAJOR flags
- Citation artifact detected as MAJOR flag
- LLM vocabulary score ≥ 9 (MAJOR)
- Integrity Risk = HIGH
- Escape hatch note included in report
- Default recommendation is Reject

## Eval 3: Clean, well-written paper

**Input:** A methodologically sound paper with:
- Valid statistics (all p-values recalculate correctly)
- Real, verifiable references
- Legitimate journal venue
- No tortured phrases or LLM markers
- Complete ethics declarations

**Expected behavior:**
- All statistical checks PASS
- No tortured phrases or citation artifacts found
- Integrity Risk = LOW
- Recommendation based purely on scientific merit (not integrity flags)
- Self-verification audit returns CLEAN
- Review does not force criticism on well-done sections

## Eval 4: Paper with false-positive-prone content

**Input:** An oceanography paper legitimately discussing:
- "warm water currents in the Pacific"
- "natural forces driving tidal patterns"
- Geographic features "nestled in the valley"

**Expected behavior:**
- "warm water" and "natural forces" are NOT flagged by scan_phrases
- "nestled in the valley" is NOT flagged (geography exemption)
- No false MAJOR flags from these legitimate phrases
- Integrity Risk reflects actual issues only

## Eval 5: Paper with p = 1.0

**Input:** A paper containing `F(1, 48) = 0.00, p = 1.0` (legitimate result
from a Fisher's exact test or ANOVA with identical group means).

**Expected behavior:**
- statcheck correctly parses p = 1.0 as a real p-value (not mangled to 0.1)
- Recalculated p ≈ 1.0 matches reported p
- Status = PASS (no inconsistency)
