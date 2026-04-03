# Section: Outcome Tag Forecasting

## Tex content summary
RF+ET ensemble classifier per outcome tag. Same features and time-ordered split as rating model. Model eligible for test-set prediction only if Brier skill score and accuracy skill are strictly positive on validation; otherwise constant baseline used.

**Tags NOT predicted on test set (poor validation):** High Disbursement, Energy Sector Improvements, Improved Livelihoods, Improved Service Delivery, Infrastructure Completed, Activities Not Completed, Design or Appraisal Shortcomings, External Factors Affected Outcomes, Implementation Delays.

**Feature selection:** Ablation on validation set. Features grouped into: llm grades, governance indicators, regions, budget, org structure, UMAP, sector clusters, economic context, missingness flags. Feature sweep across top-5, top-10, top-30 by RF importance. Pairwise tournament on Brier skill, accuracy ratio, pairwise ordering probability. Selected subset validated in 3-fold temporal CV on train only.

**RF+ET ensemble:** Classifiers (not regressors). XGBoost and LightGBM tested and rejected. `class_weight` scheme: balanced when <65% positive, none when ≥65%.

**Hyperparameter search:** 20 LLM-generated sets (first 10 broad, second 10 near maximum).

**Start-year trend correction:** Ridge (α=50) on training residuals ~ start_year. Applied where it improved validation. Multiplier swept over {0, 0.1, 0.2, 0.5, 1.0, 1.5, 2.0}.

**Tag group averaging:** Success Group (6 tags) and Financing Group (2 tags). RF+ET regressor predicts group score; per-tag probabilities reconstructed via OLS. Threshold for blend based on minority class count; 50 blend options swept.

**LLM correction:** deepseek-V3.2 prompted with activity title, pre-activity summary, tag definition, and base rate. Blend sweep 0–70% LLM; found 80% statistical / 20% LLM optimal on validation.

## Relevant code files
- `outcome_tags/D_train_staged.py` — primary training script (final form)
- `outcome_tags/E_kfold_tag_assessment.py` — 3-fold temporal cross-validation for feature selection validation
- `outcome_tags/E_plot_staged.py` — visualization of tag model results
- `outcome_tags/Z_tag_generalizability_thurs_noon_backwards.py` — generalizability analyses (per-org, calibration, learning curve, sliding window)

## Alignment (D_train_staged.py)
- ✅ Same temporal split (LATEST_TRAIN_POINT = "2013-02-06", LATEST_VALIDATION_POINT = "2016-06-06").
- ✅ `CONST_BASE_BRIER_THRESH = 0.0`, `CONST_BASE_POP_THRESH = 0.55` — model deployed only if both criteria strictly positive on validation.
- ✅ `RF_N_ESTIMATORS = 500`, `RF_PARAMS_BASE` with `min_samples_leaf=5`, `max_features="sqrt"` — matches the tuned parameters.
- ✅ `ADD_START_YEAR_CORRECTION = True` — start-year correction enabled.
- ✅ `CORRECT_RF_BEFORE_ET = True` — correction applied to RF before averaging with ET (so net ensemble correction is correction/2), which matches the tex description of halved effect.
- ✅ `SKIP_START_YEAR_CORRECTION_TAGS = {"tag_monitoring_and_evaluation_challenges", "tag_high_disbursement"}` — matches tex list of tags where correction was not adopted.
- ✅ `USE_PER_TAG_STRATEGY = True` — uses per-tag feature subsets from F_regularization_strategies.py results.
- ✅ `DROP_NOISY_FEATURE_GROUPS = True`, `NOISY_FEATURE_GROUPS` — removes governance and uncertainty_flags groups that hurt performance in ablation.
- ✅ `apply_manual_factor_blend` imported — implements the tag group averaging.
- ✅ `PARAM_SETS` dict in D_train_staged.py contains 10 named parameter sets. The tex says 20 sets (first 10 broad, second 10 near maximum); Z_sweep_rf_params.py handles the sweep.

## Misalignment / gaps
- **LLM correction disabled in final model:** `ADD_LLM_CORRECTION = False` in D_train_staged.py, with comment "removed: LLM averaging doesn't generalise to kfold." The tex describes the LLM correction (80% statistical / 20% LLM) as a method that was tested but does NOT explicitly state it is used in the final submitted model. However, the tex section reads as if it were adopted — **the tex description of the LLM correction needs to clarify that this was explored but not used in the final model due to failure to generalise in k-fold CV.**
- **20 vs 10 hyperparameter sets:** Tex says 20 LLM-generated sets; D_train_staged.py PARAM_SETS only defines 10. The other 10 are in Z_sweep_rf_params.py. The tex description of "20 sets" refers to the full sweep process, not just what is in D_train_staged.py — this is internally consistent but could be clearer.
- **XGBoost and LightGBM rejection not reflected:** Tex says both were tested and significantly underperformed. No LightGBM import visible in D_train_staged.py; LightGBM testing was likely in an earlier experimental script (D_train_staged_old.py or D_train_working.py).
- **Multiplier sweep {0, 0.1, 0.2, 0.5, 1.0, 1.5, 2.0}:** This is in Z_sweep_year_correction.py, not in D_train_staged.py itself.

## Alignment (E_kfold_tag_assessment.py)
- ✅ 3-fold temporal CV on train+val only (never touches held-out test) — matches tex.
- ✅ Uses per-tag strategy from D_train_staged results JSON — consistent with tex feature selection validation procedure.
- ✅ Plots: val_check_plots.png, per-tag fold plots, summary box-whisker.

## Alignment (E_plot_staged.py)
- ✅ 4 plot types: POP vs AUC scatter, Brier skill bar, POP bar, minority class size vs POP scatter.
- ✅ TAG_GROUPS matches the 4 category structure in the tex.
- ✅ Bootstrap CI computed for metrics.
- ✅ Color/shape scheme (green = BSS ≥ 0.1; orange = BSS < 0.1 but model chosen; grey = const_base).

## Alignment (Z_tag_generalizability_thurs_noon_backwards.py)
- ✅ 4 analyses: (A) per-org POP table, (B) calibration reliability diagrams, (C) learning curve, (D) sliding window.
- ✅ Also runs (E) val check mirroring E_kfold (RUN_E = True).
- ✅ EVAL_ON_VAL = True (flip to False for test evaluation).
- ✅ Imports all key functions from D_train_staged, ensuring the same feature matrix and split logic.
