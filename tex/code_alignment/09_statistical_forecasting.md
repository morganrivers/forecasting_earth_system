# Section: Experimental Methods — Statistical Forecasting

## Tex content summary
Novel components beyond baselines:

**Nearest Neighbor (KNN):** gemini-embedding-001 embeddings of LLM-generated targets text; 15 nearest neighbors found optimal; weighted mean of neighbor ratings. Found to underperform "most common rating" baseline, so not used as standalone predictor (but used for few-shot LLM block).

**Random Forest (RF):** Bootstrap ensemble of decision trees; max_depth and feature fraction controls; averaging reduces overfitting.

**Extra Trees (ET):** Like RF but random split thresholds; trained on full dataset (not bootstrap); combined with RF for complementary diversity.

**XGBoost:** Sequential tree ensemble (boosting); L1+L2 regularization.

**LLM-generated scores (7 features):** gemini-2.5-flash 0–100 scores for: financing, integratedness, implementer performance, contextual challenge, overall risk, technical complexity, ease of targeted outcomes. Plus 2 interaction terms (governance × complexity, expenditure × complexity).

**Embeddings (UMAP):** gemini-embedding-001 on LLM-generated targets text → PCA (50D) → UMAP (3D). 3D found best on validation. 4 features: umap3_x, umap3_y, umap3_z, binary missing indicator.

**Sector clustering:** gemini-2.5-flash extracts funding breakdown → embedding → 15 clusters (15 found optimal over 10, 20). 15 cluster-fraction features + 1 missing indicator = 16 features total.

## Relevant code files
- `C_forecast_outcomes/C_run_GLM_rating.py` — main implementation of all statistical methods
- `C_forecast_outcomes/C_predict_outcomes_saves_model.py` — same statistical methods applied to cost-effectiveness outcomes

## Alignment (C_run_GLM_rating.py)
- ✅ `run_random_forest_median_impute` and `run_random_forest_median_impute_noclip` imported — RF implemented.
- ✅ `run_xgboost_native_missing` imported — XGBoost implemented.
- ✅ `find_similar_activities_semantic` imported — KNN by semantic embedding implemented.
- ✅ `compute_knn_blend` function: uses k=15 (top_n=15), knn_weight=0.2 (80% RF, 20% KNN blend). However the tex says KNN alone underperformed and was not used as a standalone predictor — the code confirms `USE_KNN_BLEND = False` by default.
- ✅ `load_targets_context_maps_features` — loads UMAP coordinates from TARGETS_CONTEXT_MAPS_TRAINVAL; 4 features (umap3_x, umap3_y, umap3_z + missing indicator) match tex.
- ✅ `load_sector_clusters` — loads 15 sector cluster features + missing indicator (16 total) matching tex.
- ✅ `add_enhanced_uncertainty_features` — loads the 7 LLM-generated scores (financing, integratedness, implementer performance, contextual challenge, risk, complexity, ease).
- ✅ `MODEL_TO_USE = "logit_and_ordinal"` — the final model uses `fit_logit_and_ordinal_model_pred`, which is the staged logit+ordinal approach.

## Misalignment / gaps
- **ET not separately listed in code imports:** The tex describes RF and ET as distinct algorithms averaging together. In C_run_GLM_rating.py, `run_random_forest_median_impute` is imported but there is no explicit `run_extratrees_...` import visible in the first 150 lines. The ET may be implemented inside `run_random_forest_median_impute` as a combined RF+ET ensemble, or in `fit_logit_and_ordinal_model_pred`. Cannot confirm from reads so far.
- **XGBoost role:** The tex describes XGBoost as a standalone experimental method, but MODEL_TO_USE = "logit_and_ordinal" in C_run_GLM_rating.py suggests XGBoost is not the final model but was evaluated during development. `run_xgboost_native_missing` is imported but may not be the primary model path.
- **3D UMAP validation claim:** Tex says 3D outperformed 2D and 4D on validation. This selection is done upstream (in a script generating the UMAP coordinates), not in C_run_GLM_rating.py itself.
- **Interaction terms:** Tex lists "governance times complexity" and "expenditure times complexity" as 2 additional interaction features. `ADD_INTERACTION_FEATURES = False` but `ADD_GROUP_INTERACTION_FEATURES = True` in C_predict_outcomes_saves_model.py. Need to verify which flag governs the two specific interaction terms in C_run_GLM_rating.py.
- **HHI not used:** Tex explicitly states HHI for sector funding concentration was tested and not added due to no validation improvement. No HHI code is visible in C_run_GLM_rating.py imports (aligned with it not being in the final model).
