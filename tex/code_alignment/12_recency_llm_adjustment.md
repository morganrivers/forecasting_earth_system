# Section: Recency and LLM Adjustment Ridge Regression

## Tex content summary
Goal: correct RF model for temporal distribution shift and incorporate LLM forecast signal.

**Formulation:**
- RF+ET residual: $r_i = y_i - \hat{y}^{RF}_i$
- Ridge regression: $\hat{r}_i = \beta_0 + \beta_1 \hat{y}^{RF}_i + \beta_2 \hat{y}^{LF}_i$  (α controls penalty)
- Corrected prediction: $\hat{y}^{corr}_i = \text{clip}_{[0,5]}(\hat{y}^{RF}_i + \lambda \hat{r}_i)$, λ=1.0

**Two variants:**
1. Recency only (β₂=0): intercept + scaling correction on 150 most recent training activities
2. LLM-informed (β₁, β₂): both RF and LLM forecast as inputs; fitted on 150 most recent training activities with LLM forecasts available

## Relevant code files
- `C_forecast_outcomes/C_run_GLM_rating.py` — implements `add_rf_llm_residual_corrector` and `apply_start_year_trend_correction`

## Alignment
- ✅ `add_rf_llm_residual_corrector` in C_run_GLM_rating.py exactly implements the formulation: fits Ridge (alpha=5.0 default, not α from tex — see below) on residuals from RF predictions; `use_llm=True/False` controls whether LLM forecast is included (β₂); `lam=1.0` (λ=1.0 matches tex); `clip_lo=0.0, clip_hi=5.0` (matches tex clip range).
- ✅ `meta_train_idx` in the function is the 150 most recent training activities, matching the tex.
- ✅ The two-variant logic: `use_llm=True` → uses [rf_col, llm_col] as features; `use_llm=False` → uses [rf_col] only. Matches the two variants described.
- ✅ `apply_start_year_trend_correction`: fits linear regression of residuals on start_year (using `linregress`), then applies correction across all rows — consistent with the tex start-year correction described in the Outcome Tag section (similar mechanism applied to both rating and tag models).

## Misalignment / gaps
- **Ridge penalty α discrepancy:** The function default `alpha=5.0` does not match any specific value described in the tex. The tex does not explicitly state α for this residual corrector (the tex states α=50 only for the *outcome tag* start-year correction ridge). The rating residual corrector α=5.0 may be intentional but is undocumented in the tex.
- **"150 most recent training activities":** The tex states the corrector is fitted on the 150 latest training activities. In the code `meta_train_idx` is passed as a parameter from the calling code; the specific 150-activity selection logic is in the main() function of C_run_GLM_rating.py (not read in detail). Should verify that N=150 is actually enforced.
- **λ=1.0 described as a "scaling factor":** The tex mentions λ is set to 1.0 "in the experiments" but leaves open whether it was tuned. The code hard-codes `lam=1.0` which aligns but provides no sweep of λ visible in the listed files.
