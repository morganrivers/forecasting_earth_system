# Overall Ratings Forecasting — Results & Specification

This document describes what the overall-rating forecasting code must implement, the precise metrics reported, and the exact numerical results stated in the thesis. It is intended as a checklist for verifying that the code matches the thesis specification.

---

## 1. Context and Goal

The thesis forecasts **overall evaluation ratings** (1–6 scale, World Bank convention) for international aid activities in the IATI database. Ratings are extracted from post-activity evaluation PDFs and rescaled to a common 1–6 range:

- 1 = Highly Unsatisfactory
- 2 = Unsatisfactory
- 3 = Moderately Unsatisfactory
- 4 = Moderately Satisfactory
- 5 = Satisfactory
- 6 = Highly Satisfactory

BMZ/KfW/GIZ ratings are **inverted** to match this scale. Scores given as percentages or fractions are rescaled linearly. Only the top-4 reporting organizations by count are used: **World Bank** (957 activities), **BMZ/KfW/GIZ** (240), **ADB** (156), and **UK FCDO** (127).

---

## 2. Dataset Splits

| Split      | Temporal boundary (activity start date)             | N (approx.) |
|------------|-----------------------------------------------------|-------------|
| Training   | On or before 2013-02-06                             | ~800        |
| Validation | 2013-02-07 – 2016-06-06                             | ~268        |
| Test (held-out) | Latest-starting 200 activities after validation cutoff | 200 |

The held-out test set consists of the **200 latest-starting** evaluated activities in the 1,300-activity, 4-organization dataset. The split is **time-ordered** (out-of-time), not random. Activities are restricted to those with status "completed".

---

## 3. Target Variable Pre-processing

All models are trained on **per-organization mode-demeaned residuals**:

```
ỹ_i = y_i − m_o
```

where `m_o` is the mode of training-set ratings for reporting organization `o`. Predictions are recovered by adding back `m_o`:

```
ŷ_i = ỹ̂_i + m_o
```

This removes the dominant between-organization rating shift so models focus on within-organization variation.

---

## 4. Baselines

### 4.1 Mode of Reporting-Organization Baseline
- Always predicts the most common (mode) rating for the activity's reporting organization.
- This is the intercept against which all other methods are compared.
- **Pairwise ranking** is artificially suppressed for this baseline (all activities get the same prediction, so no ordering is possible for ties).

### 4.2 Ridge Regression: Risks + Organization Only
- Features: LLM-extracted risk grade (0–100 scale) + one-hot reporting-organization indicator.
- Trained only on activities where the LLM successfully extracted a risk grade.
- Serves as the **human-baseline extrapolation** comparison: this is how much can be inferred from stated risks in approval documents alone.
- **Reported test-set within-group pairwise ranking: 51%** (the `\PairwiseHuman` constant).

### 4.3 Plain OLS GLM
- Ordinary Least Squares regression on all features (same feature set as RF+ET).
- Serves to demonstrate that **nonlinear models are necessary** for within-group pairwise ranking skill.

---

## 5. Features

### 5.1 Non-LLM Features (Baseline Statistical Category)

| Feature | Notes |
|---|---|
| Planned activity duration | |
| Planned total disbursement (raw) | |
| log(planned total disbursement) | derived |
| Planned total disbursement per year | derived |
| Finance type: loan vs. grant | binary indicator |
| One-hot reporting organization | top-4 organizations |
| CPIA score (World Bank) | country governance |
| World Governance Indicators | control of corruption, government effectiveness, political stability, regulatory quality, rule of law; plus composite mean |
| Activity scope (1–7, local to global) | |
| log(GDP per capita) | weighted by % of activity per country |
| Region dummy variables | AFE, AFW, EAP, ECA, LAC, MENA, SAS |
| Missingness counts | for features with missing values |
| Interaction: GDP per capita × duration | |

Activity start date is **excluded** (no linear time trend with ratings; adds overfitting risk).  
Implementer type (government/NGO) is **excluded** (did not improve validation performance).

### 5.2 LLM-Generated Grade Features (gemini-2.5-flash, 0–100 scale)

| Feature | Description |
|---|---|
| Finance adequacy | How well-financed the activity is |
| Integratedness | Integration within broader activity ecosystem |
| Implementer performance | Expected implementer quality including ownership |
| Contextual challenge | Degree of external challenge |
| Risk outlook | Overall risk level (100 = low risk) |
| Technical complexity | Overall technical complexity |
| Target achievability | Ease of achieving stated targets (100 = easy) |

Plus two interaction terms:
- Governance score × complexity
- Expenditure × complexity

**Note:** These 7 scores were originally generated with `gpt-3.5-turbo` (to minimize post-September 2021 knowledge leakage); the thesis later adopts `gemini-2.5-flash` for most LLM extraction.

### 5.3 Language Model Embeddings (UMAP)

The LLM-generated **targets** text (summarizing activity objectives) is embedded with `gemini-embedding-001`. The high-dimensional embedding is reduced in two stages:
1. PCA → 50 dimensions
2. UMAP (fitted on training data only; held-out activities projected via `transform()`) → 3 dimensions

Features added:
- `umap3_x` — spectrum: forestry/water/management (low) → energy/financing (high)
- `umap3_y` — spectrum: energy (low) → biodiversity/wastewater/conservation (high)
- `umap3_z` — spectrum: rural/wildlife (low) → urban/sanitation (high)
- Binary indicator for missing UMAP embedding

**3D** outperformed 2D and 4D on the validation set; chosen accordingly.

### 5.4 Embedding Contextualization (Distance Features)

Both vectors are L2-normalized (so Euclidean distance = cosine distance):
- `sector_distance`: distance from activity embedding to centroid of all embeddings in same DAC5 sector + decade group
- `country_distance`: distance from activity embedding to L2-normalized weighted sum of recipient-country centroids (weighted by % of activity per country, decade-stratified)

Centroids are fitted only on training-period activities. Fallback to decade centroid if fewer than a threshold of training examples exist in a group.

### 5.5 Budget Sector Clusters

`gemini-2.5-flash` identifies funding allocation breakdowns from pre-activity document pages tagged as finance/budget (falling back to first 10 pages of highest-ranked document). Budget descriptions are embedded with `gemini-embedding-001` and clustered into **15 sector clusters** (tried 10, 15, 20; 15 optimal on validation set). Each cluster's allocation as a fraction of total is a feature.

Features:
- 15 features (one per cluster, as fraction of total expenditure)
- 1 binary missing indicator (median-imputed to 0 when absent)

~68% of projects have budget breakdowns. HHI of budget allocation was tested but did **not** improve validation performance and was excluded.

---

## 6. Models

### 6.1 Random Forest (RF)
- Ensemble of decision trees trained independently with bootstrap sampling.
- Each split considers a random subset of features.
- Trained on mode-demeaned residuals.

**Optimal hyperparameters (found via sweep + LLM-generated suggestions):**
| Parameter | Value |
|---|---|
| `max_depth` | 14 |
| `min_samples_split` | 20 |
| `min_samples_leaf` | 20 |
| `max_features` | 0.488 |
| `max_samples` | 0.86 |
| `n_estimators` | (not explicitly stated; default=100 baseline) |
| `bootstrap` | True |
| `ccp_alpha` | 0.0 |

### 6.2 Extra Trees (ET)
- Additional randomization: split thresholds drawn uniformly at random (not optimized).
- Trained on the **full dataset** (no bootstrap), so diversity comes from split randomization rather than data resampling.
- Averaged with RF predictions for final output.

### 6.3 XGBoost
- Sequential boosting with L1 and L2 regularization.
- Found to underperform RF+ET overall; especially weaker when combined with LLM Forecast (ridge).

### 6.4 RF+ET Ensemble
- Final prediction is the **simple average** of RF and ET predictions.
- This is the primary experimental model.

---

## 7. LLM Adjustment Ridge Regression

A small ridge regression is layered on top of the statistical model to incorporate LLM Forecast signals:

```
r_i = y_i − ŷ^RF_i                    (RF+ET residual)
r̂_i = β₀ + β₁ŷ^RF_i + β₂ŷ^LF_i      (ridge model, α=5)
ŷ^corr_i = clip[0,5](ŷ^RF_i + λ·r̂_i) (λ=1.0)
```

Fitted on **300 latest-starting validation activities** (training activities for which LLM forecasts were generated). Evaluated on the test set. **This method backfired on the test set** (performed worse than simple average of RF+ET and LLM Forecast).

---

## 8. Scoring Metrics

All metrics are computed on the held-out test set (n=200), except where noted.

| Metric | Definition | Notes |
|---|---|---|
| **Accuracy** | % correct (non-integers rounded) | Not strictly proper |
| **RMSE** | √(mean squared error); scale 0–5, lower better | Penalizes large errors |
| **MAE** | Mean absolute error; scale 0–5, lower better | |
| **R²** | Coefficient of determination; higher better | Can be negative |
| **Adjusted R²** | R² penalized for number of regressors; reported on train+validation only | For comparability with prior literature |
| **Within-Group Pairwise Ranking** | Mean % of correctly ordered pairs within same org+year group | Primary metric; 0.5 = chance |
| **Within-Group Spearman Ranking** | Weighted mean Spearman ρ within org+year groups (midranks for ties) | Secondary metric |

**Within-Group Pairwise Ranking definition (precise):**
- Only pairs sharing the same reporting organization AND start year are compared.
- For pair (i,j) with y_i ≠ y_j: correct if p̂_i > p̂_j when y_i > y_j.
- Ties in predictions (p̂_i = p̂_j) are excluded from numerator and denominator.
- Each group scored independently; final = weighted mean proportional to group size.
- Random chance = 0.50; perfect = 1.00.

---

## 9. Key Numerical Results (Test Set)

All values from thesis constants and results tables:

| Method | R² | RMSE | MAE | Accuracy | WG Spearman | WG Pairwise Rank |
|---|---|---|---|---|---|---|
| **RF+ET all features (no year corr)** | **0.004** | **0.924** | 0.683 | 0.470 | 0.206 | **0.599** |
| RF+ET all features + year corr | -0.002 | 0.927 | 0.704 | **0.485** | 0.206 | **0.599** |
| XGBoost all features | -0.008 | 0.929 | 0.688 | 0.460 | 0.174 | 0.580 |
| RF+ET, no LLM features | -0.026 | 0.938 | 0.680 | 0.475 | 0.070 | 0.541 |
| RF+ET (default params) | -0.036 | 0.942 | 0.706 | 0.465 | **0.206** | 0.597 |
| Ridge Baseline (risks + org only) | -0.048 | 0.948 | 0.696 | 0.465 | 0.008 | 0.508 |
| Mode of rep. org. score baseline | -0.079 | 0.962 | **0.658** | 0.460 | — | — |
| Plain OLS GLM | -0.136 | 0.987 | 0.767 | 0.410 | 0.054 | 0.529 |
| *(orange) RF+ET + LLM Forecast (simple avg)* | *0.004* | *0.924* | *0.683* | *0.470* | *0.206* | ***0.599*** |
| *(orange) RF+ET + LLM Forecast (ridge)* | *-0.002* | *0.927* | *0.704* | *0.485* | *0.206* | ***0.599*** |

Orange rows contain LLM Forecast predictions found to **benefit from future leakage** — treat cautiously.

**Primary result (chosen model, RF+ET all features):**
- Within-group pairwise ranking: **60%** [95% CI: 53%, 66%]  (`\PairwiseModel`, `\PairwiseCILow`, `\PairwiseCIHigh`)
- Baseline (risks + org only, ridge regression): **51%** (`\PairwiseHuman`)

**Training + validation set R²:**
- Full RF+ET: **0.32** (`\RsqTraining`)
- OLS on all features: **0.18** (`\RsqTrainingOLS`); Adjusted R²: **0.13** (`\RsqAdjTrainingOLS`)

**Effect of adding LLM features (validation set):**
- Without LLM features R²: **-0.026** (`\Rsqnollmfrac`)
- With all LLM features R²: **-0.002** (`\Rsqheldoutratingsllmfeatures`)
- Delta R²: **0.024** (`\Rsqdelta = \Rsqheldoutratingsllmfeatures − \Rsqnollmfrac`)

---

## 10. Feature Importance (SHAP and Drop-One)

SHAP analysis on validation set (RF model). Key findings:
- **Planned expenditure** (higher → better ratings) and **planned duration** (shorter → better) are most important.
- **World Bank reporting-org indicator** (negative, World Bank has below-average ratings in dataset) is among the most important.
- **UMAP Z axis** (urban/rural): lower values (rural/less-contextualized) shift ratings down.
- **Contextual challenge**: weakly shifts ratings down.
- **Target achievability**: shifts ratings up.
- **Multi-country activities**: slightly worse performance.

Drop-one feature importance table (validation set, sorted by |Δpred_1sd|):

| Feature | Miss% | ΔR² | ΔPairwise | Δpred_1sd |
|---|---|---|---|---|
| Target achievability (LLM) | 2.0 | +0.0077 | +0.0245 | +0.0920 |
| UMAP Z axis | 8.5 | +0.0076 | +0.0115 | -0.0672 |
| External context (LLM) | 1.5 | +0.0023 | +0.0038 | +0.0565 |
| Sector: capacity building | 47.0 | +0.0026 | +0.0017 | -0.0456 |
| Region: East Asia & Pacific | 0.0 | +0.0132 | +0.0309 | +0.0381 |
| Implementer quality (LLM) | 0.5 | +0.0092 | +0.0162 | +0.0308 |
| Annual expenditure (log) | 8.5 | -0.0009 | -0.0076 | +0.0254 |
| UMAP Y axis | 8.5 | +0.0025 | +0.0029 | +0.0218 |
| Reporting org: World Bank | 0.0 | +0.0285 | -0.0059 | +0.0217 |
| Planned duration | 0.5 | -0.0001 | -0.0018 | -0.0216 |
| Expenditure × complexity | 7.0 | +0.0032 | +0.0070 | +0.0210 |
| UMAP X axis | 8.5 | +0.0034 | +0.0083 | -0.0180 |
| Geographic scope | 0.0 | +0.0007 | -0.0127 | -0.0175 |
| Finance adequacy (LLM) | 4.5 | +0.0074 | +0.0131 | +0.0171 |
| Region: MENA | 0.0 | +0.0013 | +0.0052 | -0.0160 |
| CPIA score | 31.5 | -0.0001 | -0.0020 | +0.0131 |
| Region: Europe & Central Asia | 0.0 | +0.0012 | -0.0014 | +0.0109 |
| Sector: contingencies | 47.0 | +0.0033 | +0.0027 | +0.0096 |
| Sector: project management | 47.0 | +0.0054 | +0.0066 | +0.0093 |
| Finance type: loan | 0.0 | +0.0028 | +0.0045 | -0.0083 |
| Log planned expenditure | 5.5 | +0.0008 | -0.0003 | +0.0002 |
| Risk outlook (LLM) | 1.5 | -0.0015 | -0.0034 | -0.0072 |
| Sector dissimilarity | 8.5 | +0.0043 | +0.0078 | +0.0056 |
| GDP per capita | 7.5 | +0.0033 | -0.0061 | +0.0063 |
| Sector cluster: managed forest land | 47.0 | +0.0048 | +0.0057 | -0.0061 |
| Sector clusters missing | 0.0 | +0.0063 | +0.0116 | -0.0059 |
| Region: Latin America & Caribbean | 0.0 | +0.0022 | -0.0032 | -0.0056 |
| Governance composite index | 7.5 | -0.0025 | -0.0052 | +0.0030 |
| Governance data missing | 0.0 | +0.0071 | +0.0102 | -0.0049 |
| Planned expenditure | 5.5 | -0.0006 | -0.0038 | +0.0047 |

---

## 11. Temporal Trend Correction

A start-year linear trend correction is applied after training:

```
r_i = y_i − p̂_i                     (residual)
r̂_i = γ₀ + γ₁·year_i               (ridge regression, α=50)
p̂^corr_i = clip[0,5](p̂_i + r̂_i)
```

Ridge penalty α=50 shrinks slope toward zero to avoid overcorrecting. Correction multiplier swept over {0, 0.1, 0.2, 0.5, 1.0, 1.5, 2.0}.

**Effect:** Decreases overall accuracy but improves within-group pairwise ranking and Spearman ranking. RF+ET with year correction achieves same pairwise ranking as without (0.599) but slightly worse R² (-0.002 vs 0.004).

---

## 12. Verification Checklist for Code

- [ ] Rating extraction pipeline uses 2-method approach (page-level + keyword fallback)
- [ ] Ratings from all organizations rescaled to 1–6 scale; BMZ/KfW/GIZ ratings inverted
- [ ] Only top-4 organizations by count are used for training/validation/test
- [ ] Mode-demeaned residuals used as training target; mode computed from training set only
- [ ] Time-ordered split: train ≤ 2013-02-06, validation 2013-02-07 – 2016-06-06, test = latest 200
- [ ] PCA (→50 dims) then UMAP (→3 dims) fitted on training data only; held-out projected via `transform()`
- [ ] Sector and country embedding centroids computed on training data only
- [ ] 15 budget sector clusters (k=15 from tries of 10, 15, 20)
- [ ] RF hyperparameters: max_depth=14, min_samples_split=20, min_samples_leaf=20, max_features=0.488, max_samples=0.86
- [ ] RF+ET final prediction = simple average of RF and ET
- [ ] Within-group pairwise ranking excludes between-org/year pairs and excludes tied predictions
- [ ] SHAP computed on validation set (not test set)
- [ ] LLM Adjustment ridge regression: α=5, λ=1.0, clip to [0, 5]
- [ ] Year correction: ridge α=50, correction clipped to [0, 5]
- [ ] Governance + uncertainty missingness features excluded from outcome tag models (18 features dropped)
