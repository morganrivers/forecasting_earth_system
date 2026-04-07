# Audit: `results_cost_effectiveness.md` vs. Code

**Audited against**: most recent `main` commit (4b6369e).
**Primary files examined**:
- `src/B_extract_structured_database/C_extract_quantitative_information.py`
- `src/B_extract_structured_database/E_gemini_aggregate_quantitative_outcomes.py`
- `src/B_extract_structured_database/E_process_quantitative_results_with_keywords.py`
- `src/C_forecast_outcomes/C_predict_outcomes_saves_model.py`
- `src/D_data_analysis/print_key_results.py`
- `src/utils/split_up_activity_funding.py`

---

## DISCREPANCY 1 — Wrong model name for quantitative outcome extraction

**MD claims (§2.1):** "`gemini-2.5-flash` extracts quantitative outcome values from these pages"

**Code reality:** `C_extract_quantitative_information.py`, line 116:
```python
MODEL_NAME = "gemini-2.5-flash-lite"
```
The initial extraction step uses **`gemini-2.5-flash-lite`**, not `gemini-2.5-flash`. The more powerful `gemini-2.5-flash` is used only in the *aggregation* step (`E_gemini_aggregate_quantitative_outcomes.py`, line 39), which runs after extraction and adjudicates multi-value groups.

**Severity:** High — affects description of which model does what.

---

## DISCREPANCY 2 — Gemini aggregation is called for ALL records, not just multi-value groups

**MD claims (§2.1):** "Multiple values per category are **aggregated** via a `gemini-2.5-flash` prompt that…"

**Code reality:** `E_gemini_aggregate_quantitative_outcomes.py`, lines 196–218 — the single-record passthrough branch is **commented out**:
```python
# if len(records) == 1:
#     # Single record - pass through without calling Gemini
#     single_record.append(records[0])
# else:
# Multiple records - need Gemini aggregation
```
Every `(activity_id, which_distribution)` group — including those with only one record — is sent to Gemini. The MD implies Gemini is called only when there are multiple conflicting values.

**Severity:** Medium — architecture differs from description; cost and behavior implications.

---

## DISCREPANCY 3 — Outcome categories used for forecasting do not match what MD describes

**MD claims (§2.2):** Only these **5 categories** are included for forecasting:
- Benefit/cost ratios
- Rates of return
- Emissions reductions
- Water and sanitation connections
- Energy outcomes

**MD also says (§2.2)** these categories have "insufficient counts for forecasting" and are excluded:
> Pollution load removed, Forest indicators (trees/seedlings, reforested/managed/protected area), Irrigation outcomes, Air quality (PM2.5), Clean cooking stoves, Agricultural yields.

**Code reality:** `C_predict_outcomes_saves_model.py`, lines 38–72 — the hardcoded list `ONLY_USE_THESE_AND_ASSERT_EXIST_WITH_COUNTS` actually includes **all of the following** in the forecasting pipeline:
```python
'out_raw_yield_increases_percent__percent',       # yield — MD says excluded
'out_raw_yield_increases_t_per_ha__t_per_hectare',# yield — MD says excluded
'out_dpu_area_protected__hectares',               # forest/area — MD says excluded
'out_dpu_area_reforested__hectares',              # forest — MD says excluded
'out_dpu_area_under_management__hectares',        # area management — MD says excluded
'out_dpu_pollution_load_removed__tonnes_per_year',# pollution — MD says excluded
'out_dpu_stoves__count_stoves',                   # stoves — MD says excluded
'out_dpu_trees_planted__count',                   # trees — MD says excluded
```
Plus the 5 categories the MD says are included. **16 total categories are used**, not 5.

**Severity:** High — the MD misdescribes the scope of what is actually modelled.

---

## DISCREPANCY 4 — Log₁₀ transform exception list is incomplete

**MD claims (§2.5):** "The **log₁₀ transform** is applied to all outcome categories **except** benefit-cost ratios and rates of return, before modelling."

**Code reality:** `C_predict_outcomes_saves_model.py`, line 1003–1033:
```python
is_yield = dist_l.map(is_yield_dist)
is_ror   = dist_l.isin({"economic_rate_of_return", "financial_rate_of_return"})
# yield + RoR use linear; everything else uses log10
raw["_val"] = np.where(is_yield | is_ror, raw["outcome_norm"], raw["outcome_norm_log10"])
```
**Yield categories also use linear scale** (not log₁₀), alongside benefit-cost ratios and rates of return. The MD omits yield from the exception list.

The same logic applies in `E_process_quantitative_results_with_keywords.py`, line 550:
```python
df["log_plot"] = (~dist_lower.str.contains("yield_increase")) & (~dist_lower.str.contains("rate_of_return"))
```
Yield is explicitly excluded from log-plotting alongside rate-of-return.

**Severity:** Medium — incomplete description of transformation logic.

---

## DISCREPANCY 5 — Agricultural yield is not in the "no monetary allocation" set

**MD claims (§2.3 / verification checklist item):** "B/C ratios, rates of return, agricultural yields excluded from monetary allocation"

**Code reality:** `split_up_activity_funding.py`, line 5:
```python
NO_MULTIPLIER = {"benefit_cost_ratios", "economic_rate_of_return", "financial_rate_of_return"}
```
**Yield is NOT in `NO_MULTIPLIER`**. It receives a proportional funding multiplier like any other outcome. Yield is excluded from the per-dollar-per-unit (DPU) *output column* in `C_predict_outcomes_saves_model.py` via `~dpu_is_yield`, but the funding multiplier is still computed and applied during `E_process_quantitative_results_with_keywords.py` (line 571). The MD claim that yield has "no monetary allocation" misrepresents this: yield does get a budget fraction computed — that fraction is simply not used to build a cost-effectiveness ratio column.

**Severity:** Medium — architecturally inaccurate; yield allocation is computed even though the resulting DPU column isn't used for zagg.

---

## DISCREPANCY 6 — CO₂ substitutes list undocumented (`area_under_management`)

**MD claims (§2.4):** "If CO₂ reductions reported **alongside** linked mitigation outputs: CO₂ inherits the combined allocation already assigned to the CO₂-mitigating expenditures"
The MD implies the CO₂-mitigating outputs are things like improved stoves, added generation capacity, or trees planted.

**Code reality:** `split_up_activity_funding.py`, line 14:
```python
CO2_SUBS = {"stoves", "generation_capacity", "trees_planted", "area_reforested", "area_under_management"}
```
`area_under_management` (sustainably managed land area) is also a CO₂ substitute that triggers the CO₂ special case. The MD does not mention this. The MD only loosely paraphrases "improved stoves, added generation capacity, or trees planted" without listing `area_reforested` or `area_under_management`.

**Severity:** Low-medium — incomplete enumeration of CO₂ substitutes.

---

## DISCREPANCY 7 — Z-score normalization uses training-set statistics, not global statistics

**MD claims (§3):** "An aggregate cost-effectiveness Z-score is computed by standardizing each outcome category to zero mean and unit variance, then averaging across available categories for each activity."

**Code reality:** `C_predict_outcomes_saves_model.py`, lines 524–556 (`add_groupwise_z`):
```python
is_train = long_df["activity_id"].isin(train_aids)
g = long_df.loc[is_train].groupby(group_col)[y_col]
mu = g.mean()
sd = g.std(ddof=0)
long_df[z_col] = (long_df[y_col].astype(float) - long_df["mu_g"]) / long_df["sd_g"]
```
Mean and standard deviation are computed on **training data only** and then applied to all rows (train + val + test). The MD implies a simple global standardization. This is a methodologically important distinction that prevents data leakage but is not described.

Also: `sd = g.std(ddof=0)` uses population standard deviation (not sample/ddof=1), which is non-standard and unmentioned.

**Severity:** Medium — important methodological detail omitted.

---

## DISCREPANCY 8 — Forecasting model is not "the same" as used for ratings

**MD claims (§4):** "The same statistical forecasting models and feature set as used for ratings are applied to forecast cost-effectiveness (as a regression task on the aggregate Z-score)."

**Code reality:**
- Ratings model (`C_predict_outcomes_saves_model.py`, line 162): `MODEL_TO_USE = "logit_and_ordinal"` — logistic + ordinal regression pipeline.
- Zagg (cost-effectiveness) model (lines 4645–4652): `run_random_forest_median_impute_noclip` — a **Random Forest** on the long-form z-score.

The feature set is the same, but the model type is different. Cost-effectiveness is forecast with a Random Forest regression on z-scores; ratings are forecast with logit/ordinal models. These are not the same models.

**Severity:** High — the claim of "same models" is directly contradicted by code.

---

## DISCREPANCY 9 — Pearson r between rating and zagg is computed on ALL activities, not the held-out set

**MD claims (§5.1):** "Pearson r between overall rating and aggregate cost-effectiveness Z-score **on the held-out set**: 0.07"

**Code reality:** `C_predict_outcomes_saves_model.py`, lines 4822–4841:
```python
# zagg_true for ALL activities (not just test), honoring rating exclusion
if SKIP_RATINGS_WHEN_REPORTING:
    _zagg_all = long_df.loc[long_df["which_group"] != "rating__rating"].groupby("activity_id")["y_z"].mean()
else:
    _zagg_all = long_df.groupby("activity_id")["y_z"].mean()

_rating_all = pd.to_numeric(data["out_rating"], errors="coerce").astype(float)
_merged_pr = pd.DataFrame({"zagg": _zagg_all, "rating": _rating_all}).dropna()
```
The comment **explicitly states** this is "ALL activities (not just test)". The correlation is computed over the entire dataset (train + val + test), not just the held-out set. If the number 0.07 is correct, it refers to a full-dataset Pearson r, not a held-out-set statistic.

**Severity:** High — the description of what population this statistic is computed on is incorrect.

---

## DISCREPANCY 10 — Minimum activity count threshold of ≥10 is not programmatically enforced

**MD claims (§2.2):** "Only outcome categories with values for at least **10 activities** after filtering to evaluation set dates (2013-02-06 to 2016-06-06) are included."

**Code reality:** `C_predict_outcomes_saves_model.py`, lines 221–222:
```python
MIN_TRAIN_ROWS_PER_GROUP = 1  # Min rows in training set per outcome group
MIN_TEST_ROWS_PER_GROUP = 1   # Min rows in test set per outcome group
```
The actual minimum enforced for including an outcome group in the zagg model is **1 row** in train and **1 row** in test, not 10. The `ONLY_USE_THESE_AND_ASSERT_EXIST_WITH_COUNTS` list is hardcoded (presumably chosen by manual inspection), but the code does not programmatically filter by a ≥10 threshold.

**Severity:** Medium — process description does not match implementation.

---

## DISCREPANCY 11 — Recency weighting of training data is unmentioned

**MD claims:** No mention anywhere of sample weighting.

**Code reality:** `C_predict_outcomes_saves_model.py`, lines 4641–4652:
```python
# Create recency weights: recent 20% gets 3x weight
cutoff_idx = int(len(train_index_long) * 0.8)
sample_weights = np.ones(len(train_index_long))
sample_weights[cutoff_idx:] = 3.0

yhat_all, rf_model = run_random_forest_median_impute_noclip(
    ...
    sample_weight=sample_weights,
)
```
The most recent 20% of training observations receive **3× sample weight** when training the Random Forest for cost-effectiveness. This is not documented at all.

**Severity:** Medium — undocumented methodological choice that affects results.

---

## DISCREPANCY 12 — Primary metric description is inconsistent

**MD claims (§4):** "The primary metric reported is **R²** (coefficient of determination), used for both ratings and cost-effectiveness."

**MD claims (§5.2):** The headline result is "Within-group pairwise ranking on cost-effectiveness: **60%**" — not R².

**Code reality:** For ratings, the primary metric throughout the codebase is the **pairwise ordering probability** (ranking skill); R² is secondary. For zagg, R², pairwise, within-group pairwise, and Spearman are all computed (lines 4902–4925). The assertion that R² is "the primary metric" is internally inconsistent with the MD's own §5.2 and inconsistent with the ratings code.

**Severity:** Low — minor inconsistency in framing within the document itself, but also inconsistent with how ratings primary metric is described in codebase.

---

## DISCREPANCY 13 — Log₁₀ denominator transform uses `log_plot` flag, not a uniform per-DPU rule

**MD claims (§2.5):** Implies a single, uniform rule: log₁₀ applied to all except B/C and RoR.

**Code reality:** `E_process_quantitative_results_with_keywords.py`, lines 596–601:
```python
for c in VAL_COLS:
    dpu = c + "_dollars_per_unit_split"
    out = c + "_dollars_per_unit_split_log10"
    df[out] = np.where(df["log_plot"] & df["per_dollar_ok"] & df["has_exp"] &
                       df[dpu].notna() & (df[dpu] > 0),
                       np.log10(df[dpu]),
                       np.nan)
```
The `log_plot` flag (line 550) is `False` for yield AND rate-of-return, so neither gets a log₁₀ DPU column. Additionally, `per_dollar_ok` is `False` for B/C ratios AND RoR, so those never get a DPU column at all (log or otherwise). The MD's single-rule description obscures the two-layer flag system.

**Severity:** Low — logical equivalent but description is oversimplified.

---

## DISCREPANCY 14 — Denominator labeled "total disbursement" but column is `actual_total_expenditure`

**MD claims (§2.3):** "The total **disbursement** for each activity **as reported by IATI** serves as the cost denominator (in USD)."

**Code reality:** `E_process_quantitative_results_with_keywords.py`, line 442:
```python
df_info = pd.read_csv(INFO_CSV, usecols=["activity_id", "actual_total_expenditure"])
```
The denominator column is `actual_total_expenditure`, not a disbursement-specific field. The distinction between "expenditure" and "disbursement" matters in IATI data (disbursements are outflows to implementing partners; expenditure is final spending). Using "disbursement" as synonymous with `actual_total_expenditure` may be inaccurate.

**Severity:** Low-medium — terminology mismatch; the actual field may include more than just disbursements.

---

## SUMMARY TABLE

| # | Section | Claim | Actual | Severity |
|---|---------|-------|--------|----------|
| 1 | §2.1 | Extraction uses `gemini-2.5-flash` | Uses `gemini-2.5-flash-lite` | **High** |
| 2 | §2.1 | Gemini only called for multiple values | Gemini called for all groups (single-record passthrough commented out) | Medium |
| 3 | §2.2 | 5 categories used for forecasting; others excluded | 16 categories used including all "excluded" ones | **High** |
| 4 | §2.5 | log₁₀ except B/C and RoR | log₁₀ except B/C, RoR, AND yield | Medium |
| 5 | §2.3 | Yield has "no monetary allocation" | Yield gets a funding multiplier; DPU column is just unused | Medium |
| 6 | §2.4 | CO₂ substitutes not fully listed | `area_under_management` is also a CO₂ substitute (unlisted) | Low-Med |
| 7 | §3 | Z-score: global standardization | Z-score uses train-only mean/SD; population stddev (ddof=0) | Medium |
| 8 | §4 | Same models as ratings | Ratings = logit+ordinal; zagg = Random Forest | **High** |
| 9 | §5.1 | Pearson r on held-out set | Pearson r on entire dataset | **High** |
| 10 | §2.2 | ≥10 activity threshold enforced | Minimum is 1; list is hardcoded manually | Medium |
| 11 | N/A | No mention of sample weighting | Recent 20% of training gets 3× weight | Medium |
| 12 | §4/§5.2 | R² is primary metric | R² and pairwise both reported; pairwise is the headline result in §5.2 | Low |
| 13 | §2.5 | Single rule for log₁₀ DPU | Two-layer flag system (`log_plot` + `per_dollar_ok`) | Low |
| 14 | §2.3 | "Total disbursement" | Column is `actual_total_expenditure` (not purely disbursements) | Low-Med |
