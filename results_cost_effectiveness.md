# Cost-Effectiveness Forecasting — Results & Specification

This document describes the exact specification for the cost-effectiveness forecasting code and the precise numerical results reported in the thesis. Use it to verify the code implements exactly what the thesis describes.

---

## 1. Context and Goal

Cost-effectiveness is defined as the ratio of measured **quantitative outcomes** (numerator) to **activity expenditure** (denominator). It is an alternative to the scalar overall rating that is:
- More objective (less susceptible to evaluator bias)
- Less likely to be gamed (not a funding criterion)
- More directly comparable between activities within the same outcome category

The thesis attempts to forecast cost-effectiveness as a third outcome metric, in addition to overall ratings and outcome tags.

---

## 2. Definition and Computation

### 2.1 Numerator: Quantitative Outcome Extraction

Quantitative outcomes are extracted from post-activity evaluation pages categorized as containing outcomes with quantitative information. Extraction is **not** limited to the top-4 reporting organizations (unlike ratings, cost-effectiveness reporting is less susceptible to between-organization variation).

Extraction pipeline:
1. Pages categorized as containing outcomes AND marked as quantitative are selected from post-activity documents
2. `gemini-2.5-flash` extracts quantitative outcome values from these pages
3. Domain-specific filters applied to reduce false positives (e.g. wastewater context for pollution loads, water context for connections, agriculture context for yields)
4. Implausible or non-numeric values are dropped
5. Multiple values per category are **aggregated** via a `gemini-2.5-flash` prompt that:
   - Adjudicates between conflicting, overlapping, or differently aggregated values
   - Distinguishes duplicates from additive components
   - Prioritizes project-level totals over subcomponent figures
   - Aggregates only non-overlapping quantities
   - Returns null when no coherent representative value can be determined

Outcome categories were identified using **manual inspection** and **bigram frequency analysis** of extracted text.

### 2.2 Comparable Outcome Categories

Only outcome categories with values for at least **10 activities** after filtering to evaluation set dates (2013-02-06 to 2016-06-06) are included. The final categories reported are:

| Category | Description | Units |
|---|---|---|
| **Benefit/cost ratios (B/C)** | Benefit-cost ratio outcomes | dimensionless |
| **Rates of return** | Economic rate of return (ERR/EIRR) and financial rate of return (FRR/FIRR) | percent |
| **Emissions reductions** | CO₂ or CO₂e reductions (total or per-year) | tonnes |
| **Water and sanitation connections** | Counts of service connections (new or repaired) | count |
| **Energy outcomes** | Installed generation capacity | MW (or GWh where source reported in energy units) |

**Categories parsed but with insufficient counts for forecasting:**
- Pollution load removed (BOD/COD/nutrients)
- Forest indicators (trees/seedlings planted; area reforested/managed/protected in hectares)
- Irrigation outcomes (increase in irrigated area, hectares)
- Air quality (PM2.5 reductions)
- Clean cooking stoves (counts distributed/installed)
- Agricultural yields (level changes or percent increases)

### 2.3 Denominator: Activity Expenditure

The total disbursement for each activity **as reported by IATI** serves as the cost denominator (in USD).

Exceptions (no monetary allocation):
- Benefit/cost ratios
- Rates of return
- Agricultural yield outcomes (inherently unit-free or already normalized)

### 2.4 Budget Allocation Algorithm

Outcome-level funding splits are not available in IATI. A custom algorithm allocates total expenditure across outcome categories:

1. **Bucketing:** Closely related indicators measuring the same underlying result are grouped into shared conceptual buckets, e.g.:
   - Protected area + area under management
   - Different yield-increase measures
   - Tree planting + reforested area

2. **Equal shares:** Each bucket receives an equal share of the activity's allocatable funding. Every component inside a bucket inherits that same share.

3. **CO₂ special case:**
   - If CO₂ reductions reported **without** closely linked mitigation outputs (improved stoves, added generation capacity, or trees planted): CO₂ receives an equal share like any other bucket
   - If CO₂ reductions reported **alongside** linked mitigation outputs: CO₂ inherits the combined allocation already assigned to the CO₂-mitigating expenditures — preventing CO₂ from inflating allocated spending

4. **Multi-outcome de-duplication:** Non-overlapping funded sub-activities and activity reports are identified, and total expenditure is allocated across these non-overlapping components before distributing to outcome categories.

### 2.5 Distribution and Transformation

Empirical inspection found most cost-per-unit outcomes are approximately **log-normally distributed**. The **log₁₀ transform** is applied to all outcome categories **except** benefit-cost ratios and rates of return, before modelling.

---

## 3. Aggregate Cost-Effectiveness Z-Score

An aggregate cost-effectiveness Z-score is computed by standardizing each outcome category to zero mean and unit variance, then averaging across available categories for each activity. This allows comparison between activities with different outcome types.

---

## 4. Forecasting Cost-Effectiveness

The same statistical forecasting models and feature set as used for ratings are applied to forecast cost-effectiveness (as a regression task on the aggregate Z-score).

The primary metric reported is **R²** (coefficient of determination), used for both ratings and cost-effectiveness.

---

## 5. Results

### 5.1 Rating–Cost-Effectiveness Correlation

**Pearson r between overall rating and aggregate cost-effectiveness Z-score on the held-out set: 0.07** (`\RatingCostCorr`)

This is a **very weak correlation**, indicating that evaluators' overall ratings are largely unrelated to the quantitative cost-effectiveness of activities.

### 5.2 Forecasting Performance

**Cost-effectiveness prediction was not shown to be statistically significant** above the baseline.

- Within-group pairwise ranking on cost-effectiveness: **60%** (`\CostEffect`) [95% CI: 55%, 66%] (`\CostCILow`, `\CostCIHigh`)
- This is the same numeric value as for ratings (60%), but is **not statistically significant** for cost-effectiveness.
- Random chance = 50%; the 60% pairwise ranking for cost-effectiveness does not reach statistical significance at 95% confidence.

### 5.3 Failure Modes Identified

1. **Insufficient data:** Low sample counts after filtering to evaluation date range limit statistical power.
2. **Inconsistency across activities:** Cost-effectiveness metrics are inconsistent in their component indicators between activities, making the aggregate Z-score noisy.
3. **Expenditure noise:** Total IATI disbursement as denominator introduces noise; model learns to predict linearly higher cost-effectiveness correlating with expenditure when denominator is not applied.
4. **Not dividing by expenditure increases predictability:** Failing to divide by total disbursement increases apparent predictability — but the model is learning expenditure correlations, not true cost-effectiveness.
5. **Expert coding needed:** The thesis concludes that expert coding is likely required for robust extraction of quantitative outcomes.
6. **Coarse funding allocation:** The assumption that all project funding goes to all outcomes is too coarse; per-outcome funding breakdowns would be needed for accurate cost-effectiveness.

---

## 6. Comparison with Prior Literature

The thesis notes that obtaining cost-effectiveness metrics was **more challenging** than obtaining ratings, contradicting prior claims by Goldemberg et al. (2025) that cost-effectiveness is easier to extract than ratings.

---

## 7. Recommended Outcome for Future Work

The thesis recommends:
- Larger training set for cost-effectiveness forecasting
- Less noisy data collection methods
- Expert coding for quantitative outcome extraction
- Per-outcome funding breakdowns (not available in IATI currently)
- **Water and sanitation connections** identified as the most clearly comparable outcome category, though systematic cost differences between sanitation connections and water supply may not be disambiguated by the model.

---

## 8. Verification Checklist for Code

- [ ] Quantitative outcome extraction from all pages categorized as containing outcomes AND marked as quantitative
- [ ] Extraction NOT limited to top-4 organizations (unlike ratings)
- [ ] Domain-specific filters reduce false positives (wastewater for pollution, water for connections, agriculture for yields)
- [ ] Implausible/non-numeric values dropped per-category
- [ ] Multiple values per category aggregated by `gemini-2.5-flash` (distinguishing duplicates from additive components, project-level vs. subcomponent)
- [ ] Final outcome categories: B/C ratios, rates of return, CO₂ reductions, water/sanitation connections, energy capacity
- [ ] Threshold: ≥10 activities with values in evaluation date range (2013-02-06 to 2016-06-06) required
- [ ] IATI total disbursement (USD) used as denominator
- [ ] B/C ratios, rates of return, agricultural yields excluded from monetary allocation
- [ ] Closely related indicators bucketed; each bucket receives equal expenditure share
- [ ] CO₂ special case: equal share if no linked mitigation outputs; otherwise inherits linked allocation
- [ ] log₁₀ transform applied to all categories except B/C ratios and rates of return
- [ ] Aggregate Z-score: standardize each category then average across available categories per activity
- [ ] Same feature set and models used for cost-effectiveness as for ratings
- [ ] Primary metric: R² and within-group pairwise ranking
- [ ] Report: rating–cost-effectiveness Pearson r on held-out set = 0.07
- [ ] Report: cost-effectiveness within-group pairwise ranking = 60% [CI: 55%, 66%], not statistically significant
- [ ] Note: not dividing by expenditure artificially increases predictability (expenditure correlation artifact)
