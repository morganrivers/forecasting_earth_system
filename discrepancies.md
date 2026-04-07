# Spec vs. Code Audit: `results_overall_ratings.md` and `results_outcome_tags.md`

**Audited against commit:** `a48286d` ("the key runners for getting what matters from the thesis")  
**Spec files added in commit:** `7990a53` ("Add files via upload")  
**Audit date:** 2026-04-07  
**Primary code files checked:**
- `src/C_forecast_outcomes/C_run_GLM_rating.py` — overall ratings model
- `src/outcome_tags/D_train_staged.py` — outcome tags model
- `src/utils/scoring_rules.py` — metric definitions
- `src/utils/statistical_models.py` — RF helpers
- `src/utils/helpers_for_ratings_and_final_activity_features.py` — feature loaders
- `src/B_extract_structured_database/K_generate_embedding_distances_compressions.py` — UMAP/PCA
- `src/C_forecast_outcomes/A_grade_baseline_features_gpt3p5.py` — LLM grade generation
- `src/outcome_tags/K_llm_tag_forecasts.py` — LLM tag correction

---

## Part 1 — Overall Ratings (`results_overall_ratings.md`)

### DISC-R-01 · Year correction uses plain OLS, not Ridge α=50  
**Severity: HIGH**

**Spec (§11):**
> `r̂_i = γ₀ + γ₁·year_i` — ridge regression, α=50

**Code (`C_run_GLM_rating.py`, line 405):**
```python
slope, intercept, r_val, p_val, _ = linregress(years_tr, resid_tr)
```
Uses `scipy.stats.linregress` (ordinary least squares). No ridge penalty.

**Note:** The *outcome tags* model (`D_train_staged.py`, line 1386) correctly uses `Ridge(alpha=50.0)`. The rating model does not. This is either a code inconsistency or the spec is wrong for ratings.

---

### DISC-R-02 · Year correction — no clipping applied  
**Severity: MEDIUM**

**Spec (§11):**
> `p̂^corr_i = clip[0,5](p̂_i + r̂_i)`

**Code (`C_run_GLM_rating.py`, line 412):**
```python
data[pred_col] = data[pred_col].astype(float) + correction
```
No clipping is applied after adding the year correction. The predictions before year correction were already clipped to `[1.0, 6.0]` (see DISC-R-03), but nothing clips the corrected result.

---

### DISC-R-03 · RF+ET and all model predictions clipped to [1, 6], not [0, 5]  
**Severity: MEDIUM**

**Spec (§11 and §7):**
> `clip[0, 5]` mentioned for year correction and LLM adjustment corrected prediction.

**Code:** Every `np.clip` on final predictions uses `[1.0, 6.0]`, matching the actual rating scale:
```python
# C_run_GLM_rating.py, lines 1659–1678 (representative examples)
np.clip(..., 1.0, 6.0)
```
The LLM residual corrector (`add_rf_llm_residual_corrector`) defaults to `clip_lo=0.0, clip_hi=5.0` (lines 339–340), which would cut off valid predictions in the 5–6 range for activities predicted above mode.

The spec's `clip[0,5]` appears to describe the mode-demeaned residual space (which does span ≈ 0–5), not the final prediction. The spec should clarify which space the clip applies to.

---

### DISC-R-04 · RF n_estimators is 638, not "default=100 baseline"  
**Severity: LOW**

**Spec (§6.1):**
> `n_estimators` — (not explicitly stated; default=100 baseline)

**Code (`C_run_GLM_rating.py`, line 1643):**
```python
rf_params = {
    "n_estimators": 638,
    ...
}
```
The actual tuned value is **638**, not the sklearn default of 100. This is an explicit hyperparameter in the final model and should be documented. It also appears in `statistical_models.py` (line 1025) as the CENTER of the LHS sweep.

---

### DISC-R-05 · "GDP per capita × duration" interaction not in rating model  
**Severity: HIGH**

**Spec (§5.1):**
> Interaction: GDP per capita × duration

**Code:** `gdp_x_duration` does **not** appear anywhere in `C_run_GLM_rating.py`. It exists in `C_predict_outcomes_saves_model.py` (quantitative outcomes model) and helper scripts, but not in the rating feature list.

---

### DISC-R-06 · "Governance score × complexity" interaction not in rating model  
**Severity: HIGH**

**Spec (§5.2):**
> Plus two interaction terms:
> - Governance score × complexity
> - Expenditure × complexity

**Code (`C_run_GLM_rating.py`, lines 1499–1505):**
```python
new_features = [f for f in [
    "governance_composite", "expenditure_x_complexity",
    "expenditure_per_year_log", "log_planned_expenditure",
] if f in data.columns]
```
Only `expenditure_x_complexity` (planned_expenditure × complexity) is added. `governance_x_complexity` (governance_composite × complexity) is **absent** from the rating model.

`governance_x_complexity` does appear in the *outcome tags* model's initial feature set (and is then dropped as part of the 18 "noisy" features). But the spec claims it is a feature in the ratings model too.

---

### DISC-R-07 · WGI individual features replaced by composite, not "plus composite mean"  
**Severity: MEDIUM**

**Spec (§5.1):**
> World Governance Indicators: control of corruption, government effectiveness, political stability, regulatory quality, rule of law; **plus composite mean**

**Code (`C_run_GLM_rating.py`, lines 1503–1504):**
```python
if "governance_composite" in new_features:
    feature_cols = [f for f in feature_cols if f not in wgi_cols]
```
When `governance_composite` is added, the 5 individual WGI columns are **removed** from `feature_cols`. The final feature set has `governance_composite` **instead of** the 5 individual WGIs, not in addition to them. The spec description "plus composite mean" implies both are retained, which is incorrect.

---

### DISC-R-08 · LLM grade section header says gemini-2.5-flash; code uses gpt-3.5-turbo (chatgpt)  
**Severity: MEDIUM**

**Spec (§5.2, section header):**
> LLM-Generated Grade Features **(gemini-2.5-flash**, 0–100 scale)

**Spec note below the table:**
> These 7 scores were originally generated with **gpt-3.5-turbo** … the thesis later adopts gemini-2.5-flash for most LLM extraction.

**Code (`A_grade_baseline_features_gpt3p5.py`, e.g. line 463):**
```python
asyncio.run(loop_over_rows_to_call_model(..., model="chatgpt"))
```
All 7 grade prompts use `model="chatgpt"` (OpenAI API). The section header "gemini-2.5-flash" is wrong for the grade features. The note is correct. The header should be "gpt-3.5-turbo".

---

### DISC-R-09 · Test set is date-based, not count-based "latest 200"  
**Severity: MEDIUM**

**Spec (§2 table and §12 checklist):**
> Test (held-out): Latest-starting **200** activities after validation cutoff  
> test = **latest 200**

**Code (`C_run_GLM_rating.py`, line 1441):**
```python
held_idx = _d[_d["start_date"] > pd.to_datetime(LATEST_VALIDATION_POINT)].index
```
Takes **all** activities after `2016-06-06` (and before `TOO_LATE_CUTOFF = 2020-01-01`). There is no cap at 200. The number happens to be approximately 200 given the dataset, but the mechanism is a fixed date cutoff, not "take the 200 latest." Same logic applies in `D_train_staged.py`. The spec description "latest 200" is mechanically inaccurate.

---

### DISC-R-10 · LLM residual corrector fit set: no explicit 300-activity limit in code  
**Severity: LOW**

**Spec (§7):**
> Fitted on **300 latest-starting validation activities** (training activities for which LLM forecasts were generated).

**Code (`C_run_GLM_rating.py`, line 1866):**
```python
model, llm_corrector_fit_idx = add_rf_llm_residual_corrector(
    data=data, y=y, meta_train_idx=train_idx, ...
)
```
`meta_train_idx = train_idx` is the full train+val set (when `USE_VAL_IN_TRAIN=True`). No explicit limit of 300 latest activities is enforced. The effective fit set is filtered to rows where **both** RF and LLM predictions are non-null — if LLM coverage is sparse (≈300), that naturally limits the fit, but this is not enforced programmatically. The spec's "300" should be a measured observation rather than a hard constraint.

---

### DISC-R-11 · Spec states validation set ≈ 268; checklist says "300 validation activities"  
**Severity: LOW (internal spec inconsistency)**

**Spec §2 table:** "Validation: ~268"  
**Spec §7:** "Fitted on 300 latest-starting validation activities"

The two sections give different validation set sizes (268 vs 300). Likely the 300 refers to a combined train+recent-activities window used for LLM corrector fitting, not the pure validation split.

---

## Part 2 — Outcome Tags (`results_outcome_tags.md`)

### DISC-T-01 · Internal inconsistency: 11 vs 12 unsigned tags  
**Severity: HIGH (spec error)**

**Spec §2.3:**
> 11 unsigned tags (recorded False if not mentioned)  
> 12 signed tags (recorded only if explicitly mentioned)

**Spec §3.1 (Two-Pass Extraction):**
> Pass 1: All **12 unsigned** tags evaluated together in one prompt per activity

One of these numbers is wrong. The code dynamically discovers the count from `applied_tags.jsonl` and prints the actual counts at runtime (`D_train_staged.py`, line 609). The spec must be corrected to use one consistent number.

---

### DISC-T-02 · Class weight threshold is strict `> 0.65`, not `≥ 65%`  
**Severity: LOW**

**Spec (§4.4 and checklist):**
> If ≥65% of training examples are positive → `class_weight=None`

**Code (`D_train_staged.py`, line 1414):**
```python
cw = None if pos_rate > 0.65 else "balanced"
```
Uses strict `>` (greater than), not `>=` (greater than or equal to). At exactly 65% positive rate, the code uses `"balanced"` while the spec says `None`. Minor boundary discrepancy.

---

### DISC-T-03 · Year correction also skips `tag_high_disbursement`, not only M&E challenges  
**Severity: MEDIUM**

**Spec (§4.6):**
> Applied to **all tags except** `tag_monitoring_and_evaluation_challenges`

**Code (`D_train_staged.py`, lines 52–55):**
```python
SKIP_START_YEAR_CORRECTION_TAGS = {
    "tag_monitoring_and_evaluation_challenges",
    "tag_high_disbursement",
}
```
**Two** tags skip the year correction: `tag_monitoring_and_evaluation_challenges` AND `tag_high_disbursement`. The spec only mentions one.

---

### DISC-T-04 · Test-set eligibility gate uses POP > 0.50, not accuracy skill > 0  
**Severity: HIGH**

**Spec (§4.8 and checklist):**
> A tag's RF+ET model is eligible for test-set prediction only if **both**:
> - Brier skill score > 0 on validation set
> - **Accuracy skill > 0** on validation set

**Code (`D_train_staged.py`, lines 1983–1986):**
```python
elif _bs <= 0:
    _revert_reason = f"BrierSkl={_bs:+.4f} <= 0"
elif _chosen.get("val_pairwise_ordering_prob", 1.0) <= 0.5:
    _revert_reason = f"POP={...:.4f} <= 0.50"
```
The second criterion is **POP (pairwise ordering probability) > 0.50**, not "accuracy skill > 0." These are different metrics. The spec describes the wrong second criterion.

Note: `CONST_BASE_POP_THRESH = 0.55` (line 38) is defined but not used in this eligibility gate (the gate uses the hardcoded `0.5` threshold).

---

### DISC-T-05 · LLM model for tag correction is `deepseek-reasoner`, not `deepseek-V3.2`  
**Severity: MEDIUM**

**Spec (§4.7):**
> `deepseek-V3.2` prompted with: activity title, pre-activity summary, tag label and definition…

**Code (`K_llm_tag_forecasts.py`, line 65):**
```python
MODEL = "deepseek-reasoner"
```
The actual model used is `deepseek-reasoner`, not `deepseek-V3.2`. These are distinct models (V3.2 is a chat/completion model; `deepseek-reasoner` is the reasoning/chain-of-thought variant).

---

### DISC-T-06 · Three factor groups in code; spec describes only two  
**Severity: MEDIUM**

**Spec (§4.5):**
> Two groups identified as strongly correlated in training data:
> - **Success Group:** average of 6 success-related signed tags
> - **Financing Group:** High Disbursement, Funds Cancelled or Unutilized (inverted)

**Code (`D_train_staged.py`, lines 327–352):**
```python
MANUAL_FACTORS: dict[str, tuple[list[str], list[str]]] = {
    "factor_success":   ([6 tags], []),
    "factor_rescoping": ([project_restructured, targets_revised,
                          closing_date_extended, funds_reallocated], []),
    "factor_finance":   ([tag_high_disbursement], [tag_funds_cancelled_or_unutilized]),
}
```
There are **three** manual factors. `factor_rescoping` (Project Restructured, Targets Revised, Closing Date Extended, Funds Reallocated) is computed and its predicted scores are used as OLS predictors in `_reconstruct_tag_probas_from_factors`. Although its tags are not directly blended (the code comment says "rescoping group disbanded"), the factor still influences per-tag probability reconstruction and is entirely absent from the spec.

---

### DISC-T-07 · Feature selection tests 4 strategies, not 3  
**Severity: LOW**

**Spec (§4.2):**
> Top-5, top-10, or top-30 features ranked by RF feature importance

**Code (`D_train_staged.py`, line 1321):**
```python
RF_STRATS = ["baseline", "top5_feat", "top10_feat", "top30_feat"]
```
Four strategies are tested: `"baseline"` (all 45 features), `top5_feat`, `top10_feat`, `top30_feat`. The "baseline" (full-feature) option is omitted from the spec description and is a valid candidate that can win the tournament.

---

### DISC-T-08 · Feature count "63" not confirmed by code  
**Severity: LOW**

**Spec (§4.1):**
> Same initial feature set as the rating model **(63 features)**

**Code:** The tag model `get_feature_cols()` (`D_train_staged.py`, lines 795–855) lists 47 explicit base features plus a dynamic set of sector cluster columns. With 15 clusters, that yields **62** features, not 63. The rating model `C_run_GLM_rating.py` yields approximately 58 features after replacing individual WGI with governance_composite and adding interaction terms (plus 15 clusters = 73 total). Neither path cleanly produces 63. The spec should document the exact feature list and count.

---

### DISC-T-09 · "WGI (7 features)" label is misleading  
**Severity: LOW (spec wording)**

**Spec checklist (§12):**
> 18 features removed from tag models: 7 governance indicators **(WGI + CPIA + governance×complexity)** + 11 missingness flags

**Spec §4.1:**
> Governance indicators: **World Governance Indicators (7 features)** + CPIA score + governance × complexity interaction = **7 governance features**

The parenthetical "(7 features)" after "World Governance Indicators" is wrong — there are **5** individual WGI indicators in the code (control of corruption, government effectiveness, political stability, regulatory quality, rule of law). The total of 7 governance features (5 WGI + 1 CPIA + 1 interaction) is correct, but the label incorrectly attributes all 7 to WGI alone.

---

### DISC-T-10 · K-fold validation is a separate script, not integrated into training  
**Severity: LOW**

**Spec (§4.2):**
> K-fold temporal cross-validation on training set used to validate that the reduction is a real generalization benefit (not overfitting to validation period)

**Code:** K-fold validation lives in `E_kfold_tag_assessment.py` — a standalone script run independently. `D_train_staged.py` does not call it inline. The spec implies it is part of the training pipeline; in practice it is a separate analysis step whose results inform manual decisions about feature reduction.

---

### DISC-T-11 · CORRECT_RF_BEFORE_ET halves effective correction; spec does not mention this  
**Severity: LOW**

**Spec (§4.6):**
> The correction is applied to the **RF model alone** before averaging with ET (not applied to the averaged RF+ET prediction).

**Code (`D_train_staged.py`, lines 50–51 and 1822–1828):**
```python
# If True (original behaviour): correction applied to RF probas BEFORE averaging with ET,
# so the net effect on the ensemble is correction/2.
CORRECT_RF_BEFORE_ET = True
```
Applying the year correction to RF only, then averaging corrected_RF with uncorrected ET, means the **net effect on the final ensemble prediction is half** the fitted correction. The spec describes the mechanism correctly (correction applied to RF only) but does not state this halving consequence, which is material for understanding calibration.

---

## Summary Table

| ID | File | Section | Severity | Short Description |
|---|---|---|---|---|
| DISC-R-01 | `C_run_GLM_rating.py:405` | §11 | **HIGH** | Year correction uses OLS (`linregress`), spec says Ridge α=50 |
| DISC-R-02 | `C_run_GLM_rating.py:412` | §11 | **MEDIUM** | No clipping after year correction; spec says clip[0,5] |
| DISC-R-03 | `C_run_GLM_rating.py:1659–1678` | §7,§11 | **MEDIUM** | All clips use [1,6] not [0,5]; LLM corrector clips to [0,5] cutting valid values |
| DISC-R-04 | `C_run_GLM_rating.py:1643` | §6.1 | LOW | n_estimators=638 in code; spec says "not explicitly stated; default=100" |
| DISC-R-05 | `C_run_GLM_rating.py` | §5.1 | **HIGH** | `gdp_x_duration` interaction absent from rating model feature list |
| DISC-R-06 | `C_run_GLM_rating.py:1499–1505` | §5.2 | **HIGH** | `governance_x_complexity` absent; only `expenditure_x_complexity` present |
| DISC-R-07 | `C_run_GLM_rating.py:1503–1504` | §5.1 | MEDIUM | Individual WGI cols replaced (not supplemented) by governance_composite |
| DISC-R-08 | `A_grade_baseline_features_gpt3p5.py:463` | §5.2 | MEDIUM | Grade section header says gemini-2.5-flash; code uses gpt-3.5-turbo (chatgpt) |
| DISC-R-09 | `C_run_GLM_rating.py:1441` | §2,§12 | MEDIUM | Test set is all activities after date cutoff, not count-capped at 200 |
| DISC-R-10 | `C_run_GLM_rating.py:1866` | §7 | LOW | No explicit 300-activity limit for LLM corrector fit set in code |
| DISC-R-11 | spec §2 vs §7 | — | LOW | Internal spec inconsistency: val set ≈268 (§2) vs 300 (§7) |
| DISC-T-01 | spec §2.3 vs §3.1 | — | **HIGH** | Spec says 11 unsigned in §2.3 but 12 unsigned in §3.1 |
| DISC-T-02 | `D_train_staged.py:1414` | §4.4,§12 | LOW | Class weight threshold is `> 0.65` (strict); spec says `≥ 65%` |
| DISC-T-03 | `D_train_staged.py:52–55` | §4.6,§12 | MEDIUM | `tag_high_disbursement` also skips year correction; spec omits this |
| DISC-T-04 | `D_train_staged.py:1983–1986` | §4.8,§12 | **HIGH** | Eligibility gate uses POP > 0.50; spec says accuracy skill > 0 |
| DISC-T-05 | `K_llm_tag_forecasts.py:65` | §4.7 | MEDIUM | Model is `deepseek-reasoner`, not `deepseek-V3.2` |
| DISC-T-06 | `D_train_staged.py:327–352` | §4.5 | MEDIUM | Third factor group (`factor_rescoping`) exists in code; absent from spec |
| DISC-T-07 | `D_train_staged.py:1321` | §4.2,§12 | LOW | 4 feature strategies tested (including baseline), spec says 3 |
| DISC-T-08 | `D_train_staged.py:795–855` | §4.1 | LOW | Feature count ~62 in code, spec claims 63 |
| DISC-T-09 | spec §4.1,§12 | — | LOW | Spec says "WGI (7 features)" but WGI has 5 indicators; total of 7 includes CPIA+interaction |
| DISC-T-10 | `E_kfold_tag_assessment.py` | §4.2,§12 | LOW | K-fold CV is standalone script, not inline in D_train_staged.py |
| DISC-T-11 | `D_train_staged.py:50–51` | §4.6 | LOW | Applying correction to RF only halves ensemble net effect; spec doesn't mention this |

**HIGH severity: 5 items** (R-01, R-05, R-06, T-01, T-04)  
**MEDIUM severity: 9 items**  
**LOW severity: 7 items**
