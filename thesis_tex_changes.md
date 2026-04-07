# thesis.tex Changes Summary

**Date:** 2026-04-07  
**Branch:** `claude/sync-thesis-docs-H1A7B`  
**Source discrepancy files:** `discrepancies.md`, `discrepancies (1).md`, `discrepancies (2).md`, `discrepancies (3).md`

All changes include a `%claudesuggests` comment in the LaTeX source with the discrepancy ID and rationale.

---

## Changes by Source File

### From `discrepancies.md` — Overall Ratings & Outcome Tags Audit

| ID | Line (approx.) | Severity | Change Made |
|---|---|---|---|
| DISC-T-01 | ~654 | HIGH | **Unsigned/signed tag counts corrected:** "11 unsigned, 12 signed" → "12 unsigned, 11 signed". Code (`final_tags.json`) has 12 `signed=false` entries and 11 `signed=true` entries. |
| DISC-R-09 | ~289 | MEDIUM | **Test-set definition clarified:** "held-out test set of 200 latest-starting activities" → "activities with start dates after a fixed date cutoff (2016-06-06), yielding approximately 200 activities". The ~200 count is an empirical outcome of the date cutoff, not a count-based selection. |
| DISC-R-07 | ~705 | MEDIUM | **WGI replacement clarified:** Added note that when `governance_composite` is present, the 5 individual WGI columns are **removed** (replaced, not supplemented). |
| DISC-R-08 | ~760 | MEDIUM | **LLM grade features model corrected:** `\emph{gemini-2.5-flash}` → `\emph{gpt-3.5-turbo}` for the 7 grade features. Code (`A_grade_baseline_features_gpt3p5.py` line 463) uses `model="chatgpt"`. |
| DISC-R-06 | ~772 | HIGH | **governance×complexity removed from ratings interaction list:** Only `expenditure_x_complexity` is present in `C_run_GLM_rating.py`; `governance_x_complexity` does not appear in the ratings model. |
| DISC-T-04 | ~824 | HIGH | **Accuracy eligibility threshold corrected:** "accuracy skill strictly positive" → "accuracy skill exceeded 0.5 percentage points (0.005 absolute) above the majority-class baseline". Code uses `ACC_SKILL_MIN_IMPROVEMENT = 0.005`. |
| DISC-T-08 | ~849 | LOW | **Feature count corrected:** "63 independent features" → "approximately 62 independent features (47 explicit base features plus 15 sector cluster columns)". |
| DISC-T-07 | ~855 | LOW | **Feature selection strategies corrected:** "top-5, top-10, top-30" → "full baseline (all features), top-5, top-10, top-30" (4 strategies, not 3). Code `RF_STRATS = ["baseline", "top5_feat", "top10_feat", "top30_feat"]`. |
| DISC-T-06 | ~891–898 | MEDIUM | **Third factor group (factor_rescoping) added:** Added description of `factor_rescoping` (Project Restructured, Targets Revised, Closing Date Extended, Funds Reallocated) and clarified it influences other tags via OLS reconstruction without being directly blended. |
| DISC-T-09 | ~894 | MEDIUM | **"Signed tags" label corrected in success group:** Changed "six success-related signed tags" to "six outcome tags" with a note that Improved Financial Performance is actually an **unsigned** tag (`signed=false` in `final_tags.json`). |
| DISC-T-05 | ~908 | MEDIUM | **Tag LLM correction model corrected:** `\emph{deepseek-V3.2}` → `\emph{deepseek-reasoner}`. Code (`K_llm_tag_forecasts.py` line 65) uses `MODEL = "deepseek-reasoner"`, which is DeepSeek's chain-of-thought reasoning model, distinct from the chat model. |
| DISC-R-04 | ~1244 | LOW | **RF n_estimators documented:** Added `n_estimators=638` as the actual tuned value. Code (`C_run_GLM_rating.py` line 1643) uses 638, not the sklearn default of 100. |
| DISC-R-10/11 | ~1149 | LOW | **LLM corrector fit set clarified:** Removed the hard "n=300" claim; explained that the ~300 count reflects LLM coverage sparsity, not a programmatic cap. No `hard limit of 300` is enforced in `C_run_GLM_rating.py`. |
| DISC-R-02/03 | ~1147 | MEDIUM | **Clipping note added:** Clarified that the LLM corrector clips to [0,5] (mode-demeaned residual space), final RF+ET clips to [1.0, 6.0]; year correction for ratings (OLS/linregress) applies no clip after adding the correction. |
| DISC-T-03 | ~1432 | MEDIUM | **Year correction exception list corrected:** Added `tag_high_disbursement` to the list of tags skipping the start-year correction. Code `SKIP_START_YEAR_CORRECTION_TAGS` contains both `tag_monitoring_and_evaluation_challenges` AND `tag_high_disbursement`. |
| DISC-T-11 | ~1434 | LOW | **Ensemble correction halving documented:** Added explicit note that applying correction to RF only (before averaging with ET) means the net effect on the RF+ET ensemble is correction ÷ 2. Multiplier sweep of {0…2.0} is equivalent to ensemble-level magnitudes {0…1.0}. |

---

### From `discrepancies (1).md` — Results Outcome Tags (second file, same tags)

This file overlaps with `discrepancies.md` for the tags audit. Changes above also cover: Discrepancy 1 (tag counts, DISC-T-01), Discrepancy 2 (Section 3.1 vs 2.3 internal consistency, resolved by fixing the count), Discrepancy 3 (WGI 5 not 7 features — the thesis at line 705 correctly lists 5 WGI indicators; no additional change needed), Discrepancy 4 (primary/comparison model designation — thesis at line 1226 correctly says homogeneous model is used for primary results; `%claudesuggests` note added about code default being per-tag), Discrepancy 5 (per-tag hyperparameter overrides, documented), Discrepancy 6 (DISC-T-03, done), Discrepancy 7 (DISC-T-05, done), Discrepancy 8 (DISC-T-04 / accuracy threshold, done), Discrepancy 9 (success group signed/unsigned, done), Discrepancy 10 (factor_rescoping, done), Discrepancy 11 (DISC-T-11, halving, done).

Additional change for Discrepancy 5:

| ID | Line (approx.) | Severity | Change Made |
|---|---|---|---|
| Disc5 (tags) | ~1426 | MEDIUM | **Per-tag RF hyperparameter overrides documented:** Added note that 10 tags have parameter overrides (e.g., `max_depth=10` for 3 tags, `min_samples_leaf` 10–40 for others). Code `TAG_RF_PARAMS_OVERRIDES` in `D_train_staged.py`. |

---

### From `discrepancies (2).md` — Cost-Effectiveness Audit

| ID | Line (approx.) | Severity | Change Made |
|---|---|---|---|
| Disc1 | ~595 | HIGH | **Extraction model corrected:** `\emph{gemini-2.5-flash}` → `\emph{gemini-2.5-flash-lite}` for initial quantitative extraction. Code (`C_extract_quantitative_information.py` line 116) `MODEL_NAME = "gemini-2.5-flash-lite"`. Gemini-2.5-flash is only used for the aggregation step. |
| Disc2 | ~622 | MEDIUM | **Gemini aggregation scope corrected:** Clarified that Gemini is called for **all** groups (including single-record groups), not only for multi-value conflicts. Single-record passthrough is commented out in `E_gemini_aggregate_quantitative_outcomes.py`. |
| Disc3 | ~606–620 | HIGH | **Outcome category count corrected:** Expanded from 5 to all 10 categories actually used in the forecasting pipeline. Code (`C_predict_outcomes_saves_model.py` `ONLY_USE_THESE_AND_ASSERT_EXIST_WITH_COUNTS`) includes 16 categories including all previously "excluded" ones (yield, forest indicators, pollution load, stoves, trees). Minimum count threshold is 1 (not 10 as previously stated). |
| Disc4 | ~634 | MEDIUM | **Log₁₀ exception list corrected:** Added agricultural yield to the exceptions alongside B/C ratios and rates of return. Code uses `is_yield` flag to apply linear scale to yields. |
| Disc5 | ~626 | MEDIUM | **Monetary allocation for yield clarified:** Yield does receive a proportional funding allocation; the DPU column is excluded downstream, not the allocation itself. `split_up_activity_funding.py`: yield is NOT in `NO_MULTIPLIER`. |
| Disc6 | ~632 | LOW | **CO₂ substitute list completed:** Added `area_reforested` and `area_under_management` to the CO₂ substitute list. Code `CO2_SUBS = {"stoves","generation_capacity","trees_planted","area_reforested","area_under_management"}`. |
| Disc7 | ~1224 | MEDIUM | **Z-score standardization note added:** Clarified that Z-scores are standardised using training-set mean and SD (population stddev, ddof=0), not global statistics. |
| Disc8 | ~1398 | HIGH | **Correct cost-effectiveness model stated:** Noted that cost-effectiveness is forecast with a Random Forest (not the same logit/ordinal model used for ratings). |
| Disc9 | ~1224 | HIGH | **Pearson r population corrected:** Clarified that the correlation is computed over the **full dataset** (train + val + test), not just the held-out set. Code comment in `C_predict_outcomes_saves_model.py` explicitly states "ALL activities (not just test)". |
| Disc11 | ~1224 | MEDIUM | **Recency weighting documented:** Added note that the most recent 20% of training observations receive 3× sample weight in the RF for cost-effectiveness. Code `sample_weights[cutoff_idx:] = 3.0`. |
| Disc14 | ~626, ~1398 | LOW | **Denominator field name corrected:** Changed "total disbursement" to "total expenditure (`actual_total_expenditure`)" throughout. IATI distinguishes disbursements from expenditure. |

---

### From `discrepancies (3).md` — Narrative Forecasts Audit

| ID | Line (approx.) | Severity | Change Made |
|---|---|---|---|
| D1 | ~644 | MEDIUM | **Outcome summary format corrected:** "3–10 paragraphs" → "bullet-point format (no introductory or concluding prose)". Code (`L_summarize_expost.py`) instructs "Output only bullet points". |
| D4 | ~938 | MEDIUM | **Metadata block org field corrected:** "participating and implementing organisations" → "reporting organisation". Code (`B_forecast_with_few_shot.py`) uses `meta.get("reporting_orgs")` in the KNN prompt. |
| D5 | ~943 | HIGH | **S2 threshold corrected:** "Moderately Satisfactory or better" → "Satisfactory or Highly Satisfactory". Code S2 stage skips Moderately Satisfactory entirely; S2 is asymmetric with S1. |
| D6 | ~944 | MEDIUM | **7-block structure note added:** `%claudesuggests` note that rating distribution is prepended inside the scratchpad block, not appended as a terminal block 7; S1/S2 are injected inline at s3. |
| D7 | ~726 | HIGH | **KNN embeddings corrected:** Added that KNN uses embeddings of "title + LLM-generated summary", not targets text. Code (`get_similar_activities.py`) uses `activity_text_embeddings_gemini.jsonl`; the targets embeddings file is commented out. |
| D8 | ~726 | HIGH | **KNN k values tested corrected:** "1, 3, 7, 10, 15, 20; optimal=15" → "1, 7, 20" (tested values). Code `FEW_SHOT_KS = [1, 7, 20]`; values 3, 10, 15 were not tested and 15 was not the optimum. |
| D9 | ~950 | MEDIUM | **Few-shot k sweep values corrected:** "tested 1, 5, 7" → "tested 1, 7, 20". Value 5 does not appear in the code sweep. |
| D10 | ~952 | MEDIUM | **KNN example contents corrected:** Location and brief summary are **not** included in the few-shot block. Code `build_few_shot_block` appends only title, risk summary, mock forecast text, rating options, and outcome label. |
| D11 | ~921 | HIGH | **Mock forecast model corrected:** `\emph{gemini-2.5-pro}` → `\emph{gemini-2.5-flash}` for mock forecast generation. No call to `gemini-2.5-pro` found in the pipeline; default in `extracting_and_grading_helper_functions.py` is `gemini-2.5-flash`. |
| D12 | ~922 | HIGH | **Baseline page relevance threshold corrected:** "minimum score of 9" → "minimum score of 3". All code uses `min_score=3`; no instance of `min_score=9` found anywhere. |
| D13 | ~922 | MEDIUM | **Outcome page count corrected:** "up to 10 outcome/evaluation pages" → "up to 5 outcome/evaluation pages". Code (`B_fine_tune_2p5_pro.py`) uses `top_k_per_activity=5`. |
| D14 | ~957 | MEDIUM | **Response format corrected:** "4-step format" → "6-step scratchpad format". Code defines 6 steps: reasons for lower rating, reasons for higher rating, initial forecast, extremity check, reconsider and finalize, FORECAST line. |
| D15 | ~1198 | LOW | **Grade intervals corrected:** "even intervals" → "approximately even intervals (alternating 3-point gaps within sub-grades, 4-point gaps between main letter grades)". Code `GRADE_TO_PCT` mapping shows non-uniform intervals. |
| D16 | ~1196 | MEDIUM | **Grading criteria corrected:** Drivers and outcomes inform a **single combined letter grade**, not two separate scores. Code (`compare_forecast_grades.py`) produces one `GRADE: X` response. |
| D17 | ~1360 | HIGH | **Evaluation set size corrected:** "n=300" → "approximately 200 training activities and the full validation set". Code uses `.tail(200)` for training activities; active `target_ids` is the validation set only, not combined with training activities. |
| D18 | ~1123 | LOW | **Fine-tuning objective clarified:** Added "(analogous to Direct Preference Optimization, DPO)"; code uses `"method": "PREFERENCE_TUNING"` (Vertex AI API term), not DPO specifically. |

---

## Summary Counts

| Severity | Count Fixed |
|---|---|
| HIGH | 13 |
| MEDIUM | 19 |
| LOW | 7 |
| **Total** | **39** |

All changes are marked with `%claudesuggests` inline comments in `tex/thesis.tex` for easy review and diffing.
