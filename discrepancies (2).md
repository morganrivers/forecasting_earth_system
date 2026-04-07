# Audit: `results_narrative_forecasts.md` vs. Source Code

**Date:** 2026-04-07  
**Branch audited:** main (commit 4b6369e)  
**MD file:** `results_narrative_forecasts.md`  
**Primary code files examined:**
- `src/C_forecast_outcomes/B_forecast_with_few_shot.py`
- `src/C_forecast_outcomes/B_generate_rag_forecasts.py`
- `src/C_forecast_outcomes/B_run_many_different_forecast_with_fewshot.py`
- `src/C_forecast_outcomes/B_fine_tune_2p5_pro.py`
- `src/C_forecast_outcomes/C_generate_reasons_for_ratings.py`
- `src/C_forecast_outcomes/C_evaluate_LLM.py`
- `src/D_data_analysis/compare_forecast_grades.py`
- `src/D_data_analysis/forecast_grading_utils.py`
- `src/utils/extracting_and_grading_helper_functions.py`
- `src/utils/get_similar_activities.py`
- `src/B_extract_structured_database/L_summarize_expost.py`

---

## Discrepancies

### D1 — §2: Outcome summary format: "paragraphs" vs. "bullet points"

**MD says:** The post-activity outcome summary covers "3–10 paragraphs covering successes, shortfalls, and quantitative outcomes."

**Code says:** `L_summarize_expost.py` prompt instructs the model to "Output only bullet points (no intro, no conclusion, no rating)."

**Impact:** The reference text submitted to the grader is in bullet-point format, not paragraph format. The word "paragraphs" in the MD and checklist item is incorrect.

---

### D2 — §2: Who "selects" pages — LLM vs. Python filter

**MD says:** "`gemini-2.5-flash` selects up to 10 pages from post-activity documents."

**Code says:** Page selection is done entirely in Python via `load_and_filter_rows` using category and score filters (`min_score=3`, `top_k_per_activity=10`). The LLM only summarizes the pre-selected pages; it does not choose them.

**Impact:** The MD implies an LLM-driven selection step that does not exist. Python code does the filtering; the LLM receives the already-filtered pages.

---

### D3 — §3.1: Model name `deepseek-V3.2` vs. API string `deepseek-chat`

**MD says:** Primary forecasting model is `deepseek-V3.2`.

**Code says:** `B_generate_rag_forecasts.py` line 93: `"model_s3": "deepseek-chat"` (annotated `# DeepSeek V3, no reasoning`). The API call string throughout is `"deepseek-chat"`.

**Impact:** Minor naming mismatch — `deepseek-V3.2` is a marketing name not used anywhere in the code. Any reader checking the code will not find `deepseek-V3.2`.

---

### D4 — §3.2.1: "Participating and implementing organisations" vs. `reporting_orgs`

**MD says:** Block 1 (Activity metadata) includes "participating and implementing organisations."

**Code says:** The main KNN prompt builder in `B_forecast_with_few_shot.py` uses `meta.get("reporting_orgs")` — the reporting organisation, not participating/implementing organisations. (The baseline `get_everything_prompt` in `B_forecast_baseline_and_with_context.py` does use `participating_orgs`, so this discrepancy may only apply to the KNN prompt path.)

**Impact:** The prompt content differs from what the MD describes for the KNN-based forecast runs.

---

### D5 — §3.2.6 / Checklist item 4: S2 threshold — "Moderately Satisfactory or better" vs. "Satisfactory or Highly Satisfactory"

**MD says:** S2 asks for "reasons it may have been rated 'Moderately Satisfactory' or **better**."

**Code says:** `B_forecast_with_few_shot.py` (S2 stage): `"provide a few reasons why the forecast might be \"Satisfactory\" or \"Highly Satisfactory\""`. The bar is higher — it skips "Moderately Satisfactory" entirely and only looks for reasons for the two top ratings.

**Impact:** The S2 prompt is not symmetric with S1 as the MD implies. S1 asks for MS-or-worse, but S2 asks for S-or-HS (not MS-or-better).

---

### D6 — §3.2 / Checklist item 2: 7-block prompt ordering

**MD says:** The prompt follows a sequential 7-block structure: metadata → description → risks → RAG → KNN → S1+S2 → rating distribution (last).

**Code says:** The rating distribution (`rating_text_dist`) is prepended to the `scratchpad_method` instruction block — it is not a terminal block. S1 and S2 outputs are injected inline as prior text during stage `s3` (not as a distinctly preceding block). The ordering in the code is not a clean sequential 7-block structure as described.

**Impact:** The checklist item "follows 7-block structure" is not accurate as stated.

---

### D7 — §3.3.1 / Checklist item 3: Embeddings of "targets text" vs. "title+summary"

**MD says:** KNN similarity is based on `gemini-embedding-001` semantic embeddings of the "LLM-generated **targets text**."

**Code says:** `get_similar_activities.py` line 22: `EMBEDDINGS_PATH = Path("../../data/activity_text_embeddings_gemini.jsonl")`. This file embeds **title + LLM-generated summary** (not targets). A separate targets embeddings file (`outputs_targets_embeddings.jsonl`, from `J_generate_targets_embeddings.py`) exists but is commented out in `get_similar_activities.py`.

**Impact:** The embeddings used for KNN are of title+summary, not targets text. The MD's claim is incorrect.

---

### D8 — §3.3.2: KNN weighting k values tested — different set

**MD says:** "15 nearest neighbors were found optimal for weighting (tested 1, 3, 7, 10, 15, 20)."

**Code says:** `B_forecast_with_few_shot.py` line 64: `FEW_SHOT_KS = [1, 7, 20]`. The values 3, 10, and 15 do not appear in this list. The claimed optimal value of 15 is not in the tested set.

**Impact:** The tested k-values and the stated optimum do not match the code.

---

### D9 — §3.3.3: Few-shot k values tested

**MD says:** "For the few-shot block: k=3 summarized mock forecasts (tested 1, 5, 7; k=3 best)."

**Code says:** `B_run_many_different_forecast_with_fewshot.py` and `B_generate_rag_forecasts.py` show `FEWSHOT_K = 3` and the broader sweep uses `FEW_SHOT_KS = [1, 7, 20]`. The value 5 does not appear in any tested set.

**Impact:** The stated tested values (1, 5, 7) do not match the code (1, 7, 20).

---

### D10 — §3.3.5: KNN example contents — missing "location" and "brief summary"

**MD says:** Each KNN few-shot example includes "key metadata (title, location, brief summary), risk summary, retrospective mock forecast analysis, and final outcome label."

**Code says:** `build_few_shot_block` (in `B_forecast_with_few_shot.py`) appends only: title, risk summary, mock forecast text, rating scale options, and final outcome label. Location and brief summary are loaded into variables but are **not** added to the few-shot block text.

**Impact:** The few-shot examples contain less context than the MD describes.

---

### D11 — §3.4.1 / Checklist item 8: Mock forecast model — `gemini-2.5-pro` vs. `gemini-2.5-flash`

**MD says:** "Mock forecasts for training examples are generated by `gemini-2.5-pro`."

**Code says:** No call to `gemini-2.5-pro` is found in the mock forecast generation path (`C_generate_reasons_for_ratings.py`). The default model in `extracting_and_grading_helper_functions.py` line 100 is `gemini-2.5-flash`. No override to `gemini-2.5-pro` is visible in the mock forecast pipeline.

**Impact:** Either the wrong model name is stated in the MD, or the model override happens externally and is not visible in the audited code.

---

### D12 — §3.4.2 / Checklist item 8: Baseline page relevance threshold — ≥9 vs. ≥3

**MD says:** "Up to 10 baseline pages (from forecast-informative categories with relevance **≥ 9**)."

**Code says:** The code consistently uses `min_score=3` throughout all page filtering calls (including `L_summarize_expost.py`, `B_fine_tune_2p5_pro.py`). No instance of `min_score=9` is found anywhere.

**Impact:** The relevance threshold stated for mock forecast baseline pages (≥9) appears to be wrong; the actual threshold used everywhere is ≥3.

---

### D13 — §3.4.3 / Checklist item 8: Outcome page count — 10 vs. 5

**MD says:** "Up to **10** outcome/evaluation pages (prioritizing deviation/delays/spending, relevance ≥ 3)."

**Code says:** `load_outcome_text_by_aid` in `B_fine_tune_2p5_pro.py` uses `top_k_per_activity=5`, not 10.

**Impact:** The stated cap of 10 outcome pages for mock forecasts does not match the code's cap of 5.

---

### D14 — §3.6: Response format — 4-step vs. 6-step scratchpad

**MD says:** The model produces a 4-step structured response: (1) reasons for lower rating, (2) reasons for higher rating, (3) aggregate and choose outcome, (4) final `FORECAST:` line.

**Code says:** `B_forecast_with_few_shot.py` (scratchpad method) defines 6 numbered steps: (1) reasons for MS or worse, (2) reasons for S or HS, (3) initial forecast, (4) check extremity of forecast, (5) reconsider and finalize, (6) `FORECAST:` on last line.

**Impact:** The MD understates the complexity of the response format by omitting the extremity check and refinement steps (steps 4–5 in the code).

---

### D15 — §4.2 / Checklist item 11: Grade scale intervals — "even" is incorrect

**MD says:** "Grades span from approximately 55 to 97, in even intervals between letter grades."

**Code says:** `forecast_grading_utils.py` GRADE_TO_PCT:
- Within sub-grades: 3-point intervals (e.g., D-=62, D=65, D+=68; C-=72, C=75, C+=78)
- Between main grade groups: 4-point gap (D+=68 to C-=72; C+=78 to B-=82; B+=88 to A-=92)

The intervals are **not** even — they alternate between 3 and 4 points.

**Impact:** The "even intervals" claim is factually incorrect based on the actual mapping in the code.

---

### D16 — §4.1.3 / Checklist item 10: Grading dimensions evaluated "separately"

**MD says:** "Grading criteria: two key dimensions: (1) accurate identification of likely drivers; (2) accurate identification of likely outcomes." Checklist: "Grading evaluates drivers and outcomes separately."

**Code says:** `compare_forecast_grades.py` grading prompt asks about both drivers and outcomes in one prompt but produces a **single combined letter grade** (`GRADE: X`). There are no two separate scores returned — the grader gives one unified grade.

**Impact:** The word "separately" in the checklist is misleading; both dimensions inform a single grade, not two distinct scores.

---

### D17 — §5.3 / Checklist item 12: Evaluation set size — n=300 vs. n=200 (or val only)

**MD says:** "All combinations are evaluated on **n=300 activities** (the 300 latest-starting training activities, same as used for LLM Adjustment ridge regression calibration, plus the full validation set of 268 activities)."

**Code says:** `B_generate_rag_forecasts.py`:
- `latest_train_200` is built using `.tail(200)` — 200 training activities, not 300.
- The active `target_ids` at line 508 is set to `set(val_ids_all)` — the validation set only, not combined with any training activities.

Also: 300 + 268 = 568, which contradicts the "n=300" claim in the same sentence.

**Impact:** The claimed evaluation set size and composition are inconsistent both internally (300 ≠ 300+268) and with the code (`.tail(200)`, val-only target_ids).

---

### D18 — §7.2: Fine-tuning objective — "DPO" vs. "PREFERENCE_TUNING"

**MD says:** "Objective: DPO (Direct Preference Optimization, intended to improve within-group pairwise ranking)."

**Code says:** `B_fine_tune_2p5_pro.py` line 950 (commented-out tuning job): `"method": "PREFERENCE_TUNING"`. This is Google Vertex AI's preference fine-tuning API; the code does not use the term "DPO" anywhere.

**Impact:** Minor — preference tuning is related to DPO but is not identical. The MD uses DPO as the precise technical term when the actual API is Vertex AI preference tuning, which may or may not be exactly DPO under the hood.

---

## Confirmed Items (no discrepancy)

- §2: Page categories (`deviation_from_plans`, `delays_or_early_completion`, `over_or_under_spending`), `min_score=3`, `top_k=10` — confirmed in `L_summarize_expost.py`
- §2: `gemini-2.5-flash` used for post-activity summarization — confirmed
- §2: Fallback uses `max_pages=10` — confirmed
- §3.2.3: Risk summary injected from pre-generated file — confirmed
- §3.2.4: RAG answers injected into prompt — confirmed
- §3.2.5: KNN k=3 with one example per LOW/MID/HIGH tier — confirmed
- §3.2.6: S1 wording ("Moderately Satisfactory or worse") — confirmed
- §3.2.7: Rating distribution prior injected to prevent mode-collapse — confirmed
- §3.3.4: Tier boundaries (low ≤2, mid =3, high ≥4 on 0–5 scale = 1–3 / 4 / 5–6 on 1–6 scale) — confirmed
- §3.4.4: Mock forecast prompt writes ex-ante and names known rating — confirmed
- §3.4.5: Returns `NO RESPONSE` if evaluation excerpts insufficient — confirmed
- §3.5.1: RF-forced variant injects statistical model rating into prompt — confirmed
- §3.6.2: "Think like a superforecaster" in all prompts — confirmed
- §4.1.1: Grader model `gemini-2.5-flash-lite` — confirmed (`compare_forecast_grades.py` line 418)
- §4.1.2: Grader inputs are forecast text + outcome summary — confirmed
- §4.1.3: Both drivers and outcomes are addressed in grading prompt — confirmed
- §4.2: Exact grade-to-number mapping (F=55 … A+=97) — confirmed in `forecast_grading_utils.py`
- §4.3: Risks-only baseline submitted to same grader — confirmed (`grade_risks` function)
- §7.1: Fine-tuned base model is `gemini-2.5-flash` — confirmed
- Checklist item 4: S1 and S2 as separate prior LLM call stages — confirmed
- Checklist item 6: Superforecaster instruction present — confirmed
- Checklist item 7: RF-forced rating injection — confirmed
- Checklist item 13: Risk-only baseline submitted to grader — confirmed
- Checklist item 14: Scatter plot of narrative grade vs. R² and pairwise ranking — confirmed

---

## Summary Table

| # | Section | MD Claim | Code Reality | Severity |
|---|---------|----------|--------------|----------|
| D1 | §2 | Outcome summary: "3–10 paragraphs" | Code prompts for bullet points | Medium |
| D2 | §2 | LLM "selects" pages | Python pre-filters; LLM only summarizes | Medium |
| D3 | §3.1 | Model named `deepseek-V3.2` | API string is `deepseek-chat` | Low |
| D4 | §3.2.1 | "Participating and implementing organisations" | Code uses `reporting_orgs` | Medium |
| D5 | §3.2.6 | S2: "Moderately Satisfactory or better" | Code: "Satisfactory or Highly Satisfactory" | High |
| D6 | §3.2 | Sequential 7-block structure, rating dist last | Rating dist inside scratchpad; S1/S2 injected inline at s3 | Medium |
| D7 | §3.3.1 | Embeddings of "targets text" | Embeddings of title+summary; targets file commented out | High |
| D8 | §3.3.2 | k tested: 1,3,7,10,15,20; optimal=15 | Code: `FEW_SHOT_KS = [1, 7, 20]`; no 3,10,15 | High |
| D9 | §3.3.3 | Few-shot k tested: 1,5,7 | Code: [1, 7, 20]; no 5 | Medium |
| D10 | §3.3.5 | Each KNN example has location + brief summary | `build_few_shot_block` omits both | Medium |
| D11 | §3.4.1 | Mock forecasts by `gemini-2.5-pro` | No `gemini-2.5-pro` found; default is `gemini-2.5-flash` | High |
| D12 | §3.4.2 | Baseline pages for mocks: relevance ≥ 9 | All code uses `min_score=3` | High |
| D13 | §3.4.3 | Up to 10 outcome/eval pages | `top_k_per_activity=5` in code | Medium |
| D14 | §3.6 | 4-step response format | 6-step scratchpad (includes extremity check + refinement) | Medium |
| D15 | §4.2 | "Even intervals between letter grades" | 3-pt within sub-grades, 4-pt between main grades | Low |
| D16 | §4.1.3 | Drivers and outcomes graded "separately" | Single combined letter grade produced | Medium |
| D17 | §5.3 | n=300 (300 training + 268 val) | Code: `.tail(200)` training; active target_ids = val only | High |
| D18 | §7.2 | Fine-tuning objective: "DPO" | Vertex AI "PREFERENCE_TUNING" API; DPO not mentioned | Low |
