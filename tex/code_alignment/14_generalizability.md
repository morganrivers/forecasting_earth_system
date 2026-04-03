# Section: Generalizability Analyses

## Tex content summary (inferred from code — no dedicated methodology subsection)
The methodology does not have an explicit "Generalizability" subsection, but the analyses described in this section are run to validate that the validation set results will transfer to the held-out test set, without ever looking at the test set.

For the **rating model** (use_val_and_train_to_estimate_generalizability_to_test.py):
- Overfitting diagnostic (train vs. val metric gap)
- Per-org heterogeneity breakdown
- Calibration check (predicted vs. actual per bin)
- Stratified pairwise probability (within org × year × expenditure tercile)
- K-fold cross-validation on train+val (temporal folds)
- Leave-one-org-out cross-validation

For the **tag model** (Z_tag_generalizability_thurs_noon_backwards.py):
- Per-org POP heterogeneity table
- Calibration reliability diagrams
- Learning curve (14 tags overlaid)
- Sliding window distance analysis
- Val check mirroring E_kfold

## Relevant code files
- `D_data_analysis/use_val_and_train_to_estimate_generalizability_to_test.py` — rating model generalizability
- `outcome_tags/Z_tag_generalizability_thurs_noon_backwards.py` — tag model generalizability

## Alignment (use_val_and_train_to_estimate_generalizability_to_test.py)
- ✅ All 6 analyses described (Analyses 2–7) are either IMPLEMENTED or commented as NOT IMPLEMENTED. Analysis 8 (bootstrap CI on val advantage) is marked NOT IMPLEMENTED.
- ✅ Context block in the file shows completed validation values consistent with thesis results: "Overall val R²: per_org_mode=0.102, ridge_baseline=0.017, RF+ET=0.192, RF+ET+LLM=0.255. Pairwise: 0.712, 0.669, 0.724, 0.724."
- ✅ Stratified pairwise: RF+ET+LLM=0.642, RF+ET=0.645 — the ~0.08 drop from unstratified (0.72) is documented in the code comments and should appear in the thesis results.
- ✅ LOOO: within-WB R²=0.15, pairwise=0.65; within-BMZ pairwise=0.66 despite negative R² — calibration bias documented.
- ✅ Val set composition documented: WB=186, BMZ=67, ADB=24, FCDO=23.
- ✅ Held-out set = most recent 200 activities by start_date — same 4 orgs, temporally later.

## Alignment (Z_tag_generalizability_thurs_noon_backwards.py)
- ✅ 4 analyses (A–D) exactly matching: per-org POP table, calibration, learning curve, sliding window.
- ✅ RUN_E = True runs the val check mirroring E_kfold.
- ✅ Imports all functions from D_train_staged, ensuring exact same feature matrix and split.
- ✅ EVAL_ON_VAL = True by default (safe; test set never touched unless flag flipped).

## Misalignment / gaps
- **No dedicated methodology section for these analyses.** The tex describes them implicitly (some results appear in results sections), but there is no explicit "Generalizability Validation" subsection in the methods chapter. Consider adding one.
- **Analysis 8 (bootstrap CI) marked NOT IMPLEMENTED** in use_val_and_train_to_estimate_generalizability_to_test.py. The tex describes the bootstrap CI method in the Scoring Metrics section but it is unclear if bootstrap CI on the validation advantage is reported.
- **Learning curve and sliding window for the rating model** are in D_data_analysis/ (`plot_learning_curve.py`, `sliding_window_combined.png` exists), but the analogous script to Z_tag_generalizability is not listed as a "final form" file for the rating model. Verify whether learning curve and sliding window analyses are reported for the rating model or only for the tag model.
- **Sliding window N_WINDOW_SIZE = 300**: The code uses 300 activities as a fixed training window. This design choice is not described in the tex.
