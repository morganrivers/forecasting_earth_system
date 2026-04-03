# Section: Baseline Methods

## Tex content summary
Five baselines described:
1. **Mode baseline:** Predict the most common rating per reporting organization
2. **Ridge regression (risks + org):** Ridge trained on LLM-extracted risk score + org dummy variable
3. **gemini-2.5-flash-lite summary of risks:** Submit risk summary to grading LLM; compare to proper LLM forecasts
4. **deepseek-V3.2 with activity summary only:** Only activity ID, title, gemini summary, and base-rate statistics provided
5. **Constant base-rate prediction for outcome tags:** Always predict training-set positive rate $\bar{p}_{\text{train}}$; defines Brier skill score = 0 reference

## Relevant code files
- `C_forecast_outcomes/C_run_GLM_rating.py` — implements baselines 1 and 2; `add_per_org_mode_baseline` function for mode baseline; `run_ridge_glm_median_impute` for ridge baseline
- `outcome_tags/D_train_staged.py` — implements baseline 5 (`CONST_BASE_BRIER_THRESH = 0.0`, `CONST_BASE_POP_THRESH = 0.55`); tags failing these thresholds are set to constant baseline

## Alignment
- ✅ Mode baseline: `add_per_org_mode_baseline` function in C_run_GLM_rating.py computes per-org training-set mode and applies as constant prediction — matches tex.
- ✅ Ridge baseline (risks + org): `run_ridge_glm_median_impute` available in C_run_GLM_rating.py; the feature set would use risk grade + org dummies.
- ✅ Constant base-rate baseline for tags: D_train_staged.py applies `const_base` model type when neither Brier skill nor accuracy exceeds threshold; `CONST_BASE_BRIER_THRESH = 0.0` matches the tex criterion "BSS strictly positive."
- ✅ `CONST_BASE_POP_THRESH = 0.55` (pairwise ordering probability ≥ 0.55) as second criterion for baseline adoption in D_train_staged.py.

## Misalignment / gaps
- Baseline 3 (gemini grading of risk summaries) and baseline 4 (deepseek-V3.2 with summary only) are LLM-based baselines handled in `B_forecast_baseline_and_with_context.py` and `C_evaluate_LLM.py` in C_forecast_outcomes/. Loaded into C_run_GLM_rating.py via `load_predictions_from_jsonl` / `get_llm_prediction_configs`. These are compared downstream in C_run_GLM_rating.py output but their generation code is in separate scripts.
- The tex says baseline 2 (ridge + risks + org) requires the LLM to successfully extract risk grade — this missingness handling is described but the code in C_run_GLM_rating.py imputes missing values (median imputation), so activities with missing risk grades are still included in this baseline.
