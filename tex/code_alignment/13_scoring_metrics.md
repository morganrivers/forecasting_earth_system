# Section: Scoring Metrics

## Tex content summary
- **Non-parametric bootstrap:** 95% CI via percentile bootstrap (2.5th/97.5th percentiles) resampling prediction-outcome pairs.
- **Accuracy:** % correct rating predicted (non-integers rounded).
- **Side Accuracy:** % correctly predicted above/below 3.5 boundary (~50/50 split in training).
- **RMSE:** Root mean square error; lower is better; penalizes large errors.
- **MAE:** Mean absolute error; lower is better; does not penalize large errors heavily.
- **R²:** Coefficient of determination; can be negative; higher is better.
- **Adjusted R²:** Penalizes extra parameters; reported on training set only.
- **Pairwise Probability:** Proportion of correctly ordered pairs; insensitive to global shifts; integer scale suppresses performance vs continuous predictions.
- **Brier Skill Score:** BSS = 1 - BS/BS_ref; reference = constant base-rate forecast; strictly proper scoring rule.

## Relevant code files
- `C_forecast_outcomes/C_run_GLM_rating.py` — imports all metrics from `scoring_rules`
- `C_forecast_outcomes/C_predict_outcomes_saves_model.py` — imports same metrics
- `outcome_tags/D_train_staged.py` — imports `pairwise_ordering_prob_excl_ties` from scoring_rules; uses `brier_score_loss` from sklearn; `roc_auc_score`, `average_precision_score`

## Alignment
- ✅ `from scoring_rules import rmse, mae, r2, true_hit_accuracy, side_accuracy, brier_side, spearman_correlation, pairwise_ordering_prob_excl_ties` — all tex-described metrics imported.
- ✅ `bootstrap_ci` from `statistical_models` — implements the percentile bootstrap described in the tex.
- ✅ `side_accuracy` with `threshold=3.5` — matches tex description of the 3.5 boundary.
- ✅ `pairwise_ordering_prob_excl_ties` — excludes tied pairs, consistent with tex note "pairwise probability does not reward ties."
- ✅ `within_group_pairwise_ordering_prob` and `org_year_pairwise_ordering_prob` imported in C_run_GLM_rating.py — enables stratified pairwise probability for within-org/year analysis.
- ✅ Brier Skill Score: BSS = 1 - BS/BS_ref where ref = constant base-rate forecast. In D_train_staged.py, `brier_score_loss` from sklearn is used and BSS computed relative to the constant baseline.

## Misalignment / gaps
- **Spearman correlation:** Imported in C_run_GLM_rating.py and C_predict_outcomes_saves_model.py but not described in the Scoring Metrics section of the tex. May appear in results tables.
- **AUC / average precision:** D_train_staged.py imports `roc_auc_score` and `average_precision_score` from sklearn for outcome tag evaluation (E_plot_staged.py shows AUC in scatter plots). These metrics are not described in the Scoring Metrics section of the tex, which only describes metrics for the continuous rating model. The tag model evaluation metrics (AUC, BSS, accuracy skill) should be described in the Scoring Metrics section or in the Outcome Tag Forecasting section.
- **Adjusted R²:** Implemented in C_run_GLM_rating.py as `adjusted_r2` function but the formula is standard; consistent with tex.
