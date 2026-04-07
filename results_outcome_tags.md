# Outcome Tag Forecasting — Results & Specification

This document describes the exact specification for the outcome tag forecasting code and the precise numerical results reported in the thesis. Use it to verify the code implements exactly what the thesis describes.

---

## 1. Context and Goal

Binary outcome tags are extracted from post-activity evaluation summaries for each activity and used as additional forecast targets beyond the scalar overall rating. Tags capture specific, discrete outcomes (e.g. closing date extended, targets met, funds cancelled) and provide a richer characterization of project execution.

Unlike the scalar rating, outcome tags:
- Are binary (True/False per activity)
- Are forecast probabilistically
- Are independent across tags, enabling stronger methodological claims
- Do not suffer from between-organization rating-scale differences

---

## 2. Tag Taxonomy Development

### 2.1 Generating Outcome Summaries (Reference Text)

For each activity, an outcome summary is generated from post-activity evaluation pages:
- Up to **10 post-activity pages** are selected, prioritizing pages categorized as:
  - `deviation_from_plans`
  - `delays_or_early_completion`
  - `over_or_under_spending`
  - With surrounding pages included when insufficient high-relevance pages are available
- Fallback: if no categorized pages meet the threshold, retrieve highest-scoring uncategorized outcome pages
- A single `gemini-2.5-flash` prompt returns 3–10 paragraphs covering successes, shortfalls, and quantitative outcomes
- The model is instructed **not** to reveal any overall evaluation rating
- These summaries are the input for tag extraction

### 2.2 Tag Discovery

- A random sample of **250 outcome summaries** from completed activities is drawn
- Divided into **25 batches of 10** summaries each
- Each batch submitted to `gemini-2.5-flash` to identify recurring outcome types
- Seed examples from manual inspection anchored the initial vocabulary (e.g. "implementation delays", "high beneficiary satisfaction", "project restructured", "capacity building delivered")
- Model generates additional tags for any outcome type appearing in more than one summary
- 25 batches' results are deduplicated and merged via **manual inspection**
- Result: **23 outcome tags**

### 2.3 Tag Types: Signed vs. Unsigned

**11 unsigned tags (recorded False if not mentioned):**
These apply to any project and would very likely be mentioned in the summary if they occurred (e.g., project delayed → would be mentioned; not mentioned → assumed False).

**12 signed tags (recorded only if explicitly mentioned):**
These are not assumed False if absent (e.g., infrastructure completion status only recorded if explicitly mentioned).

---

## 3. Tag Extraction at Scale

### 3.1 Two-Pass Extraction

Two separate LLM passes over each activity's post-activity outcome summary:
1. **Pass 1:** All 12 unsigned tags evaluated together in one prompt per activity; structured JSON output enforced via schema; each tag → single boolean
2. **Pass 2:** Remaining signed tags

### 3.2 Full Tag Set (23 tags)

Organized into four categories:

**Finance & Budget Outcomes:**
- Funds Cancelled or Unutilized
- Funds Reallocated
- High Disbursement
- Improved Financial Performance
- Over Budget

**Activity Rescoping Outcomes:**
- Project Restructured
- Closing Date Extended
- Targets Revised

**Process & Implementation Challenges:**
- Monitoring and Evaluation Challenges
- Implementation Delays
- External Factors Affected Outcomes
- Design or Appraisal Shortcomings
- Activities Not Completed

**Target Achievement Outcomes:**
- Targets Met or Exceeded
- Policy and Regulatory Reforms
- Capacity Building Delivered
- High Beneficiary Satisfaction or Reach
- Gender-Equitable Outcomes
- Private Sector Engagement
- Improved Livelihoods
- Improved Service Delivery
- Energy Sector Improvements
- Infrastructure Completed

---

## 4. Model: RF+ET Ensemble Classifier

### 4.1 Feature Set

Same initial feature set as the rating model (63 features), **but** 18 features are dropped after ablation:
- Governance indicators: World Governance Indicators (7 features) + CPIA score + governance × complexity interaction = **7 governance features**
- Missingness flag features: 11 uncertainty flags

This leaves **45 features** available for further per-tag feature selection.

The drop of 18 features was confirmed to improve K-fold temporal cross-validation on training set.

### 4.2 Feature Selection Sweep

For each tag, the following were tested on validation set:
- Top-5, top-10, or top-30 features ranked by RF feature importance on the full feature set on training data
- Selection via a **pairwise tournament** across three metrics:
  - Brier skill score
  - Accuracy ratio
  - Within-group pairwise ranking skill
- Forgiveness rule: losses < 1.5 percentage points on one metric forgiven if compensating gain on another is ≥ 20% of the loss
- Candidate with more net wins selected; ties broken by Brier skill score
- K-fold temporal cross-validation on training set used to validate that the reduction is a real generalization benefit (not overfitting to validation period)

### 4.3 Two Models on Test Set

Because it was unclear whether per-tag feature selection or full features would generalize better, **both are evaluated on the held-out test set**:
1. **RF+ET with homogeneous features** (no per-tag selection, 45 features for all tags) — reported as primary
2. **RF+ET with per-tag feature selection** — comparison model

### 4.4 Classifier Configuration

**Optimal hyperparameters:**
| Parameter | RF value | ET value |
|---|---|---|
| `min_samples_leaf` | 5 | 5 |
| `max_features` | "sqrt" | "sqrt" |
| `n_estimators` | 500 | 500 |
| `max_depth` | None | None |
| `min_samples_split` | 2 | 2 |
| `ccp_alpha` | 0 | 0 |
| `bootstrap` | True | False |

The `class_weight` parameter is tag-dependent:
- If ≥65% of training examples are positive → `class_weight=None` (predict near natural base rate)
- Otherwise → `class_weight="balanced"` (prevent collapse to majority class)

XGBoost and LightGBM were tested and found to perform significantly worse; not used further.

### 4.5 Tag Group Averaging

Two groups identified as strongly correlated in training data:
- **Success Group:** average of 6 success-related signed tags: Targets Met or Exceeded, High Beneficiary Satisfaction or Reach, Private Sector Engagement, Capacity Building Delivered, Policy and Regulatory Reforms, Improved Financial Performance
- **Financing Group:** High Disbursement, Funds Cancelled or Unutilized (inverted)

For each group: RF+ET regressor trained on 45 features to predict group score. Per-tag probabilities reconstructed from predicted group scores via OLS linear regression on training data.

**Blending formula:**
```
p̂^final_i = w · p̂^model_i + (1−w) · p̂^group_i
```
where:
```
w = clip((m − 100) / (400 − 100), 0, 1)
```
and `m` is the minority class count in training (min of # true, # false examples).

- m ≤ 100: use group average exclusively (w=0)
- m ≥ 400: use per-tag model exclusively (w=1)
- 100 < m < 400: linear blend

(Sweep over 50 blend options; best linear blend found to be this linear increase from 100 to 400.)

### 4.6 Start-Year Trend Correction

Applied to **all tags except** `tag_monitoring_and_evaluation_challenges`:
```
r_i = y_i − p̂_i                     (residual)
r̂_i = γ₀ + γ₁·year_i               (ridge, α=50)
p̂^corr_i = clip[0,1](p̂_i + r̂_i)
```

**Key detail:** The correction is applied to the **RF model alone** before averaging with ET (not applied to the averaged RF+ET prediction). This was found to outperform correcting the average.

Correction multiplier swept over {0, 0.1, 0.2, 0.5, 1.0, 1.5, 2.0}. Multiplier of **1.0 (full correction)** achieved best pairwise ranking, Brier skill, and accuracy.

### 4.7 LLM Correction (Tested, Discarded)

`deepseek-V3.2` prompted with: activity title, pre-activity summary, tag label and definition, training-set base rate. Instructed to reason like a superforecaster (enumerate reasons true, then false; anchor on base rate; produce final probability).

LLM forecasts generated for 150 recent training activities and all validation activities.

Blending tested: 0%–70% LLM weight, measured on 14 non-baseline tags.

**Findings:**
- Mean accuracy declined monotonically with LLM weight
- Within-group ranking and Brier skill showed marginal gains at 5–10% LLM, then deteriorated
- At 70% LLM, mean BSS turned **negative**
- **LLM correction discarded**; statistical model predictions used as final tag forecasts.

### 4.8 Eligibility for Test-Set Prediction

A tag's RF+ET model is eligible for test-set prediction only if **both**:
- Brier skill score > 0 on validation set
- Accuracy skill > 0 on validation set

If not eligible, the constant baseline (training-set positive rate) is used instead.

---

## 5. Tags Predicted on Test Set (14 tags)

| Tag | Category |
|---|---|
| Closing Date Extended | Activity Rescoping |
| Project Restructured | Activity Rescoping |
| Targets Revised | Activity Rescoping |
| Improved Financial Performance | Finance & Budget |
| High Disbursement | Finance & Budget |
| Funds Reallocated | Finance & Budget |
| Funds Cancelled or Unutilized | Finance & Budget |
| Over Budget | Finance & Budget |
| Policy and Regulatory Reforms | Target Achievement |
| Targets Met or Exceeded | Target Achievement |
| Capacity Building Delivered | Target Achievement |
| High Beneficiary Satisfaction or Reach | Target Achievement |
| Gender-Equitable Outcomes | Target Achievement |
| Private Sector Engagement | Target Achievement |

---

## 6. Tags NOT Predicted (9 tags, poor validation performance)

These tags had very few negative examples or highly imbalanced True/False split:
- Monitoring and Evaluation Challenges
- Energy Sector Improvements
- Improved Livelihoods
- Improved Service Delivery
- Infrastructure Completed
- Activities Not Completed
- Design or Appraisal Shortcomings
- External Factors Affected Outcomes
- Implementation Delays

---

## 7. Scoring Metrics for Outcome Tags

| Metric | Definition |
|---|---|
| **Within-Group Pairwise Ranking** | Same definition as rating model: % correctly ordered within same org+year pairs where outcomes differ; 0.5 = chance |
| **Within-Group Spearman** | Weighted mean Spearman ρ within org+year groups |
| **Brier Score** | BS = (1/N)∑(p̂_i − y_i)²; lower better; 0 = perfect |
| **Brier Skill Score** | BSS = 1 − BS/BS_ref; where BS_ref = constant base-rate forecast; >0 = beats baseline |
| **Accuracy** | % correctly classified (using majority-class or threshold) |
| **Accuracy Ratio** | Model accuracy / majority-class baseline accuracy; >1 = improvement |

---

## 8. Key Numerical Results (Test Set)

### 8.1 Overall Tag Performance

| Method | WG Pairwise Ranking (mean) | Range | Notes |
|---|---|---|---|
| **RF+ET, homogeneous features (no per-tag selection)** | **59%** | 47%–71% | Primary model |
| RF+ET, per-tag feature selection | 57% | 48%–71% | Comparison model |

- `\OutcomeTagPairwiseAvg` = 59
- `\OutcomeTagPairwiseMin` = 47
- `\OutcomeTagPairwiseMax` = 71
- `\OutcomeTagPairwiseAvgFeatSel` = 57
- `\OutcomeTagPairwiseMinFeatSel` = 48
- `\OutcomeTagPairwiseMaxFeatSel` = 71
- `\NumCuratedPredicted` = 14

**Fraction of within-group pairs with differing outcomes:** 45% (`\DifferingOutcomePairsFrac`)
(Only pairs where outcomes differ contribute to pairwise ranking; tied pairs are excluded.)

**Weighted accuracy (all 23 tags, test set):**
- Baseline (majority class): **64.5%** (`\OutcomeTagAccBaseline`)
- Model: **66.9%** (`\OutcomeTagAccModel`)
- Improvement: **+3.3 percentage points** (`\OutcomeTagAccImprovement`)

Weights proportional to number of test-set activities per tag.

### 8.2 Per-Tag Results (Test Set)

| Tag | WG Pair. Prob. | WG Spear. | Brier | Brier Base. | Acc. | Acc. Base. | Frac. True (train, test) | N_test | Tmp. Corr. | Consistent Features |
|---|---|---|---|---|---|---|---|---|---|---|
| **Activity Rescoping** | | | | | | | | | | |
| Closing Date Extended | 0.71 | 0.35 | 0.198 | 0.257 | 0.70 | 0.53 | 0.53, 0.39 | 331 | -0.66 | exp→, scp→ |
| Project Restructured | 0.69 | 0.33 | 0.203 | 0.263 | 0.70 | 0.60 | 0.60, 0.49 | 331 | -0.16 | WB→, exp→, loan→, scp→, dur→ |
| Targets Revised | 0.59 | 0.14 | 0.233 | 0.261 | 0.63 | 0.58 | 0.58, 0.47 | 331 | +0.12 | WB→, exp→, scp→ |
| **Finance & Budget** | | | | | | | | | | |
| Improved Financial Performance | 0.60 | 0.17 | 0.243 | 0.250 | 0.56 | 0.50 | 0.50, 0.42 | 331 | -0.05 | — |
| High Disbursement | 0.60 | 0.16 | 0.234 | 0.230 | 0.62 | 0.57 | 0.43, 0.32 | 331 | None | exp← |
| Funds Reallocated | 0.56 | 0.09 | 0.222 | 0.208 | 0.66 | 0.60 | 0.40, 0.24 | 331 | -0.01 | WB←, exp←, loan←, scp← |
| Funds Cancelled or Unutilized | 0.66 | 0.27 | 0.215 | 0.245 | 0.64 | 0.61 | 0.61, 0.58 | 331 | -0.29 | scp→, exp→ |
| Over Budget | 0.64 | 0.22 | 0.239 | 0.243 | 0.58 | 0.56 | 0.44, 0.42 | 101 | -0.52 | dist←, U_z←, exp← |
| **Target Achievement** | | | | | | | | | | |
| Policy and Regulatory Reforms | 0.61 | 0.13 | 0.161 | 0.165 | 0.80 | 0.73 | 0.73, 0.80 | 221 | +0.50 | — |
| Private Sector Engagement | 0.47 | -0.05 | 0.232 | 0.233 | 0.64 | 0.60 | 0.60, 0.64 | 121 | +0.34 | exp→, dist→ |
| Targets Met or Exceeded | 0.56 | 0.10 | 0.233 | 0.238 | 0.62 | 0.59 | 0.41, 0.39 | 304 | +0.04 | exp← |
| Capacity Building Delivered | 0.54 | 0.06 | 0.125 | 0.126 | 0.85 | 0.85 | 0.85, 0.85 | 263 | +0.48 | — |
| High Beneficiary Satisfaction | 0.56 | 0.09 | 0.194 | 0.197 | 0.73 | 0.78 | 0.78, 0.73 | 256 | +0.10 | — |
| Gender-Equitable Outcomes | 0.48 | -0.03 | 0.266 | 0.265 | 0.62 | 0.79 | 0.79, 0.62 | 201 | +0.41 | — |

**Feature abbreviations:** exp = planned expenditure group (raw/log/log-per-year combined); scp = activity scope; WB = World Bank reporting-org indicator; loan = finance-is-loan indicator; dur = planned duration; dist = similarity distance group (sector + country distance combined); U_z = UMAP Z coordinate. Arrow direction (→/←) indicates positive/negative relationship.

**Strongest-performing tags** by pairwise ranking: Closing Date Extended (0.71), Project Restructured (0.69), Funds Cancelled or Unutilized (0.66).

---

## 9. Tag–Rating Correlations (Pearson r, validation set)

Positive-outcome tags (positively correlated with ratings):
- Targets Met or Exceeded: r = +0.39
- High Beneficiary Satisfaction or Reach: r = +0.34
- Private Sector Engagement: r = +0.32
- Policy and Regulatory Reforms: r = +0.32
- Capacity Building Delivered: r = +0.27
- Improved Financial Performance: r = +0.16

Negative-outcome tags (negatively correlated with ratings):
- Activities Not Completed: r = −0.24
- Implementation Delays: r = −0.19

Neutral tags (not meaningfully correlated):
- Project Restructured: r = −0.04
- Targets Revised: r = +0.004

**When the overall evaluation rating is added as a feature alongside pre-activity predictors, all 14 predictable tags improve on all metrics.** This contradicts the finding of Goldemberg et al. (2025) that ratings do not aid outcome prediction.

---

## 10. SHAP Feature Analysis (Consistent Features)

"Consistent features" are those in the top-10 by |SHAP|, with the same sign, contributing ≥5% of total importance, in every split of 3 equal random training splits (RF and ET averaged).

The table in the thesis (Table `tab:tag_model_results`) reports consistent features per tag. Features absent from any split's top-10 or exhibiting a sign flip are omitted.

---

## 11. Extrapolation to Full IATI Dataset

Using an exponential saturation curve fit of performance improvements with more data:
- Current 14-tag average within-group ranking: **59%**
- Extrapolated to full IATI database (∼5× more data): **65%** (`\OutcomeTagPairwiseAvgExtrapolated`)

---

## 12. Verification Checklist for Code

- [ ] Outcome summaries generated from ≤10 pages prioritizing deviation/delays/spending categories (relevance ≥ 3/10), with fallback to highest-relevance pages
- [ ] Outcome summary instructs model NOT to reveal overall rating
- [ ] Tag taxonomy: 23 tags, 11 unsigned (assume False if not mentioned), 12 signed (only recorded if mentioned)
- [ ] Two-pass LLM extraction: pass 1 = all 12 unsigned in single prompt with structured JSON; pass 2 = signed tags
- [ ] 18 features removed from tag models: 7 governance indicators (WGI + CPIA + governance×complexity) + 11 missingness flags
- [ ] Per-tag feature selection sweep: top-5/10/30 features by RF importance; tournament across BSS, accuracy ratio, WG pairwise; forgiveness rule (1.5pp loss vs 20% gain)
- [ ] K-fold temporal cross-validation on training set used to validate feature selection
- [ ] Both models evaluated on test set: (1) homogeneous 45 features, (2) per-tag feature selection
- [ ] Classifier: RF+ET, min_samples_leaf=5, max_features="sqrt", n_estimators=500, max_depth=None, min_samples_split=2, bootstrap=True(RF)/False(ET)
- [ ] Class weight: tag-dependent (≥65% positive → None; otherwise → "balanced")
- [ ] Tag group averaging: blending formula with w = clip((m-100)/300, 0, 1); OLS reconstruction of per-tag probabilities
- [ ] Start-year trend correction applied to RF only (not averaged model); correction multiplier = 1.0; α=50 for ridge
- [ ] Start-year correction excluded for tag_monitoring_and_evaluation_challenges
- [ ] LLM correction tested and discarded; final forecasts use statistical model only
- [ ] Eligibility check: both BSS > 0 AND accuracy skill > 0 on validation set required for test-set prediction
- [ ] 9 ineligible tags use constant base-rate prediction
- [ ] Weighted accuracy weights proportional to number of test-set activities per tag
- [ ] Pairwise ranking only counts pairs with differing outcomes (tied pairs excluded)
- [ ] Model retrained on train+validation before test-set evaluation
