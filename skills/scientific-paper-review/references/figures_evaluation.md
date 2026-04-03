# Figures & Tables Evaluation Checklist

Evaluate every figure and table in the manuscript across these five categories.
Report issues with specific figure/table numbers.

## 1. Data Integrity (figure↔text consistency)

- [ ] **Values match** — do numbers visible on charts/in tables match what the text reports?
      (e.g., text says "35% increase" but bar chart shows ~20%)
- [ ] **Sample sizes consistent** — does N in table headers match N reported in methods/results?
- [ ] **No duplicate panels** — are any panels reused across different figures? Look for
      identical noise patterns, identical shapes, identical axis tick values in panels that
      claim to show different experiments or conditions.
- [ ] **Figures referenced in text** — is every figure/table cited at least once in the body?
      Are there any orphan figures never mentioned?
- [ ] **Sequential numbering** — are figure/table numbers in order? Gaps or jumps may indicate
      removed figures or copy-paste assembly.

## 2. Visual Honesty (no misleading presentation)

- [ ] **Y-axis starts at zero** (for bar charts and area charts) — or if truncated, is there
      a clear axis break indicator? Truncated axes exaggerate small differences.
- [ ] **Consistent scales** — when comparing panels side by side, do they use the same axis
      range? Different scales across panels can make similar effects look dramatically different.
- [ ] **No cherry-picked ranges** — does the time range or data window seem selected to show
      only favorable results? Check if extending the range would change the interpretation.
- [ ] **No 3D distortion** — 3D bar charts, pie charts, and perspective plots distort
      proportions. Flag if 2D would communicate the same data more accurately.
- [ ] **Aspect ratio appropriate** — is the chart stretched vertically or horizontally in a way
      that exaggerates trends? Particularly relevant for time series.
- [ ] **Dual axes used honestly** — if two Y-axes are present, do they create a misleading
      visual correlation between unrelated variables?

## 3. Statistical Presentation

- [ ] **Error bars defined** — are error bars explicitly labeled in the legend as SD, SEM,
      95% CI, or range? Unlabeled error bars are uninterpretable.
- [ ] **Individual data points shown** — for small sample sizes (N < 30), are individual data
      points overlaid on bar/box charts? Bar charts alone hide the distribution.
- [ ] **Box/violin plots preferred** — for distributions, are box plots or violin plots used
      instead of bar charts with error bars? Bar charts with SEM hide bimodal distributions,
      outliers, and skewness.
- [ ] **Significance markers correct** — are asterisks (*) or p-values placed between the
      correct comparison groups? Are multiple comparison corrections reflected?
- [ ] **Confidence intervals shown** — for effect estimates, are CIs visualized (e.g., forest
      plots, error bars on point estimates)?
- [ ] **No selective display** — are all conditions/groups shown, or are some omitted?
      Missing groups may indicate selective reporting.

## 4. Technical Quality

### Resolution & Readability
- [ ] **Resolution adequate** — are figures sharp at print size (minimum 300 DPI for print,
      150 DPI for screen)? Look for pixelation, blurry text, or JPEG compression artifacts.
- [ ] **Text legible** — are axis labels, tick marks, and legend text readable without zooming?
      Minimum ~8pt equivalent at final print size.
- [ ] **Line weight visible** — are plot lines, borders, and markers distinguishable?
      Thin lines may disappear in print.
- [ ] **Not a screenshot** — are figures actual vector graphics or high-resolution rasters,
      not screenshots of software windows (with OS chrome, menus, or toolbars visible)?

### Color & Accessibility
- [ ] **Colorblind-accessible** — does the figure rely solely on red/green distinction?
      Approximately 8% of male readers have red-green color vision deficiency. Use
      colorblind-safe palettes (viridis, cividis) or add pattern/shape differentiation.
- [ ] **Meaningful in grayscale** — would the figure be interpretable if printed in black
      and white? Color should enhance, not be the only differentiator.
- [ ] **Consistent color coding** — does the same color mean the same thing across all figures?
      (e.g., if blue = control in Fig. 1, blue should = control in Fig. 3)

### Labels & Legends
- [ ] **Axes labeled with units** — every axis has a label describing what it shows and
      the unit of measurement (e.g., "Time (seconds)", not just "Time").
- [ ] **Legend self-contained** — can the figure be understood from its caption and legend
      alone, without reading the main text?
- [ ] **Caption informative** — does the caption describe what the figure shows, not just
      "Results of experiment 3"? A good caption includes: what was measured, key conditions,
      sample size, and what statistical test is reflected in error bars/markers.
- [ ] **Table formatting** — consistent decimal places, appropriate significant figures,
      aligned columns, clear headers.

## 5. Integrity Red Flags (potential fabrication/manipulation)

These are soft signals — flag for attention, not definitive evidence:

- **Suspiciously identical noise** — in microscopy, gel, or blot images: identical background
  patterns in panels that should be independent experiments.
- **Unnaturally smooth data** — data points that follow a perfect curve with no scatter.
  Real experimental data has noise.
- **Recycled figures** — same figure appearing in multiple publications by the same group
  (cannot verify from single manuscript, but note if panels look unusually similar).
- **AI-generated figure indicators** — perfect symmetry, no imperfections, oddly uniform
  coloring, anatomical impossibilities in medical images, text in figures that is garbled
  or nonsensical.

## Reporting Format

```
#### Figures and Tables
Figures reviewed: [count]
Tables reviewed: [count]

Data integrity: [PASS / issues found]
- [list any figure↔text inconsistencies with specific numbers]

Visual honesty: [PASS / issues found]
- [list any misleading presentation with specific figures]

Statistical presentation: [PASS / issues found]
- [list any issues: missing error bar labels, bar charts hiding distributions, etc.]

Technical quality: [PASS / issues found]
- Resolution: [adequate / low — specify which figures]
- Accessibility: [colorblind-safe / not — specify which figures]
- Labels/legends: [complete / incomplete — specify gaps]

Integrity flags: [none / flagged]
- [list any suspicious patterns with specific figure numbers]
```
