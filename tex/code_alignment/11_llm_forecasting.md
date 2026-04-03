# Section: LLM Forecasting Methods

## Tex content summary
Models: deepseek-V3.2 (performance + low cost, leakage guard), gemini-3-pro (performance), gemini-2.5-flash (fine-tuning assessment only).

**Mock forecast generation:** gemini-2.5-pro generates retrospective "mock forecasts" for training activities. These use 10 baseline + 10 evaluation pages, with the known rating as ground truth. Used as few-shot examples.

**Multi-stage prompt (final method):** 7 blocks assembled in order:
1. Activity metadata (title, dates, scope, disbursement, location, GDP per capita, orgs)
2. Baseline description and targets (7 LLM-generated texts: description, targets, context, complexity, integratedness, financing, implementer performance)
3. Risk summary
4. RAG synthesis (additional retrieved info)
5. KNN few-shot block (3 most similar training activities, one from each rating tier)
6. S1/S2 multi-stage outputs (reasons for lower / higher than midpoint)
7. Rating distribution prior

**KNN few-shot block:** k=3 found best (over 1, 5, 7). One example per broad rating tier (low/mid/high).

**Ensembling:** Weak but robust; reserved for final held-out set (high API cost).

**Fine-tuning:** DPO on gemini-2.5-flash via Vertex AI. 50 pairs from 100 training activities × 5 forecasts each. Cosine similarity of embeddings used to break ties. 20 epochs, LR multiplier=1, adapter size=4, β=0.1.

## Relevant code files
- `C_forecast_outcomes/C_run_GLM_rating.py` — loads LLM forecast predictions and blends with RF via `add_rf_llm_residual_corrector`; `C_evaluate_LLM.py` and `load_predictions_from_jsonl` / `get_llm_prediction_configs` are used to load pre-computed LLM forecasts
- `C_forecast_outcomes/B_forecast_with_few_shot.py`, `B_run_many_different_forecast_with_fewshot.py` — generate the LLM forecasts (not "final form" files per user, but referenced by C_run_GLM_rating.py)

## Alignment
- ✅ C_run_GLM_rating.py imports `load_predictions_from_jsonl, get_llm_prediction_configs` from `C_evaluate_LLM` — LLM forecast scores are loaded as features for the recency corrector.
- ✅ `find_similar_activities_semantic` used for KNN; 15 neighbors for retrieving similar activities (confirmed in compute_knn_blend); k=3 for few-shot block is in the LLM prompting scripts.
- ✅ `mean_all_llm_preds` column in C_run_GLM_rating.py is the aggregated LLM forecast used in the residual corrector.

## Misalignment / gaps
- The multi-stage prompt generation (B scripts) is not in the "final form" listed files; only the downstream integration in C_run_GLM_rating.py is in scope.
- The tex mentions `gemini-3-pro` — this model designation may refer to `gemini-2.5-pro` (gemini-3 does not exist as of knowledge cutoff). This should be verified/corrected in the tex.
- Ensembling is described as "reserved for final held-out set" — no ensembling code is visible in C_run_GLM_rating.py or the listed files, consistent with this being future work.
- Fine-tuning (DPO via Vertex AI) is handled in `B_fine_tune_2p5_pro.py` in C_forecast_outcomes/; not in the final model pipeline of C_run_GLM_rating.py.
- The tex mentions `gemini-2.5-flash` for fine-tuning only; `deepseek-V3.2` for main forecasting — this is consistent with the model-specific notes in C_run_GLM_rating.py but cannot be fully verified from the listed files.
