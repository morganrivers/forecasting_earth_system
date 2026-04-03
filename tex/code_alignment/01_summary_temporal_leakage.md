# Section: Summary + Temporal Information Leakage

## Tex content summary
The thesis implements five forecasting models:
1. Statistical model for overall activity success ratings (LLM features)
2. Statistical model for cost-effectiveness (LLM features)
3. Statistical model for 14 binary outcome tags (LLM features)
4. Pure LLM model for overall activity success ratings
5. Narrative LLM model incorporating statistical model and advanced prompting

Temporal leakage section defines "leakage" as use of information that could not have been known at the start of an activity.

## Relevant code files
- `C_forecast_outcomes/C_run_GLM_rating.py` — items 1 and 4/5 (rating model + LLM integration)
- `C_forecast_outcomes/C_predict_outcomes_saves_model.py` — item 2 (cost-effectiveness model)
- `C_forecast_outcomes/C_do_outcomes_depend_on_ratings.py` — item 2 supplementary analysis
- `outcome_tags/D_train_staged.py` — item 3 (outcome tag model)

## Alignment
- ✅ The five-model summary matches what the code implements: C_run_GLM_rating.py trains the rating statistical model and integrates LLM forecasts; C_predict_outcomes_saves_model.py trains the outcome model; D_train_staged.py trains 14 binary tag classifiers.
- ✅ Leakage prevention: temporal splits in all scripts are date-based with train cutoff ≤ 2013-02-06, ensuring test data post-dates training. `USE_VAL_IN_TRAIN` flag in C_run_GLM_rating.py is used to retrain on train+val before final evaluation.

## Misalignment / gaps
- None identified in this section. The summary is high-level and the code implements all five stated models.
