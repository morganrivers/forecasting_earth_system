# Audit: `results_outcome_tags.md` vs. Code

**Date:** 2026-04-07  
**Branch audited:** `claude/audit-results-documentation-PTQXK`  
**Commit:** `7990a53` (uploaded `results_outcome_tags.md`)  
**Files cross-checked:**
- `src/outcome_tags/final_tags.json`
- `src/outcome_tags/D_train_staged.py`
- `src/outcome_tags/F_regularization_strategies.py`
- `src/outcome_tags/K_llm_tag_forecasts.py`
- `src/outcome_tags/A_discover_candidate_tags.py`
- `src/outcome_tags/print_tag_results_table.py`

---

## Summary

11 discrepancies found, ranging from factual errors (wrong counts, wrong model name) to important omissions (undocumented per-tag overrides, a third factor group, a halved correction magnitude). Two issues involve an internal self-contradiction within the MD itself.

---

## Discrepancy 1 — Unsigned/Signed tag counts swapped (CRITICAL)

**Section 2.3 of MD states:**
> "**11 unsigned tags** (recorded False if not mentioned)"  
> "**12 signed tags** (recorded only if explicitly mentioned)"

**Code (`final_tags.json`):**  
Counting `"signed":"false"` entries: `funds_cancelled_or_unutilized`, `funds_reallocated`, `high_disbursement`, `external_factors_affected_outcomes`, `activities_not_completed`, `design_or_appraisal_shortcomings`, `monitoring_and_evaluation_challenges`, `improved_financial_performance`, `project_restructured`, `implementation_delays`, `closing_date_extended`, `targets_revised` = **12 unsigned**.  
Counting `"signed":"true"` entries: `policy_regulatory_reforms_success`, `targets_met_or_exceeded`, `over_budget`, `capacity_building_delivered`, `infrastructure_completed`, `high_beneficiary_satisfaction_or_reach`, `gender_equitable_outcomes`, `improved_service_delivery`, `improved_livelihoods`, `energy_sector_improvements`, `private_sector_engagement` = **11 signed**.

**Fix:** Swap the counts — 12 unsigned, 11 signed.

---

## Discrepancy 2 — Section 3.1 internally contradicts Section 2.3

**Section 3.1 of MD states:**
> "**Pass 1:** All **12** unsigned tags evaluated together in one prompt per activity"

This is internally inconsistent with Section 2.3 which claims 11 unsigned. Section 3.1 is correct (matches the code); Section 2.3 is wrong (see Discrepancy 1).

`C_apply_tags_at_scale.py` confirms: unsigned pass uses all `signed="false"` tags = 12.

---

## Discrepancy 3 — WGI feature count wrong in Section 4.1

**Section 4.1 of MD states:**
> "World Governance Indicators (**7 features**) + CPIA score + governance × complexity interaction = **7 governance features**"

This implies 7 WGI + 1 CPIA + 1 interaction, which sums to 9 — not 7. The parenthetical "(7 features)" on "World Governance Indicators" is incorrect.

**Code (`D_train_staged.py`, `NOISY_FEATURE_GROUPS`):**
```python
# governance (7) — WGI indicators + CPIA + interaction term
"wgi_control_of_corruption_est",
"wgi_government_effectiveness_est",
"wgi_political_stability_est",
"wgi_regulatory_quality_est",
"wgi_rule_of_law_est",       # 5 WGI indicators
"cpia_score",                 # 1 CPIA
"governance_x_complexity",    # 1 interaction
```
Total: 7 governance features = **5 WGI** + 1 CPIA + 1 interaction.

**Fix:** Change "World Governance Indicators (7 features)" → "World Governance Indicators (5 features)".

The same error appears in the Section 12 verification checklist:
> "7 governance indicators (WGI + CPIA + governance×complexity)"

---

## Discrepancy 4 — Primary vs. comparison model designation is reversed (Section 4.3)

**Section 4.3 of MD states:**
> "1. **RF+ET with homogeneous features** (no per-tag selection, 45 features for all tags) — **reported as primary**"  
> "2. **RF+ET with per-tag feature selection** — comparison model"

**Code (`D_train_staged.py`):**
```python
USE_PER_TAG_STRATEGY = True   # default: per-tag feature selection IS applied
```
The default run (no flags) uses per-tag feature selection. The `--nolimits` CLI flag disables it:
```python
if args.nolimits:
    USE_PER_TAG_STRATEGY = False
    ...
    print("[nolimits] All tags use 45 non-noisy features, leaf=5, no depth limits.")
```
The nolimits run (homogeneous 45 features) writes to `tag_model_results_nolimits.json` — the non-default, secondary output file. `print_tag_results_table.py` also requires `--nolimits` to load those results.

**Implication:** The code's default run is the per-tag feature selection model, not the homogeneous one. The MD has the primary/comparison labels swapped relative to which is the code default. If the thesis intends to call the nolimits run "primary," both the code and this document need to make that explicit.

---

## Discrepancy 5 — Per-tag RF hyperparameter overrides entirely absent from Section 4.4

**Section 4.4 of MD** presents a single clean hyperparameter table implying all tags use the same `max_depth=None` and `min_samples_leaf=5`.

**Code (`D_train_staged.py`, `TAG_RF_PARAMS_OVERRIDES`):**
```python
TAG_RF_PARAMS_OVERRIDES: dict[str, dict] = {
    "tag_high_disbursement":                              {"min_samples_leaf": 20},
    "tag_policy_regulatory_reforms_success_success":      {"min_samples_leaf": 20},
    "tag_over_budget_success":                            {"min_samples_leaf": 40},
    "tag_capacity_building_delivered_success":            {"min_samples_leaf": 20},
    "tag_high_beneficiary_satisfaction_or_reach_success": {"max_depth": 10},
    "tag_targets_met_or_exceeded_success":                {"max_depth": 10},
    "tag_private_sector_engagement_success":              {"min_samples_leaf": 20},
    "tag_monitoring_and_evaluation_challenges":           {"max_depth": 10},
    "tag_gender_equitable_outcomes_success":              {"min_samples_leaf": 20},
    "tag_funds_reallocated":                              {"min_samples_leaf": 10},
}
```
10 tags have overrides: 3 tags have `max_depth=10` (not None), and multiple tags have `min_samples_leaf` ranging from 10 to 40 (not always 5).

**Fix:** Add a footnote or supplementary table documenting these per-tag overrides, or note that the table shows base parameters that are overridden per-tag.

---

## Discrepancy 6 — `tag_high_disbursement` also excluded from start-year correction (Section 4.6)

**Section 4.6 of MD states:**
> "Applied to **all tags except** `tag_monitoring_and_evaluation_challenges`"

**Code (`D_train_staged.py`):**
```python
SKIP_START_YEAR_CORRECTION_TAGS = {
    "tag_monitoring_and_evaluation_challenges",
    "tag_high_disbursement",      # ← also excluded, absent from MD
}
```

This is confirmed by the per-tag results table in Section 8.2 of the MD itself: the `High Disbursement` row shows `Tmp. Corr.: None` — consistent with the code — but Section 4.6 text fails to mention this exclusion.

**Fix:** Change "all tags except `tag_monitoring_and_evaluation_challenges`" to include `tag_high_disbursement` in the exception list.

---

## Discrepancy 7 — LLM model name incorrect (Section 4.7)

**Section 4.7 of MD states:**
> "`deepseek-V3.2` prompted with: activity title, pre-activity summary, tag label and definition..."

**Code (`K_llm_tag_forecasts.py`):**
```python
MODEL = "deepseek-reasoner"
```

`deepseek-V3.2` and `deepseek-reasoner` are distinct model identifiers. `deepseek-reasoner` is DeepSeek's reasoning model (chain-of-thought), not DeepSeek-V3.

**Fix:** Change `deepseek-V3.2` → `deepseek-reasoner`.

---

## Discrepancy 8 — Accuracy eligibility threshold is 0.5 pp, not strictly > 0 (Section 4.8)

**Section 4.8 of MD states:**
> "A tag's RF+ET model is eligible for test-set prediction only if both:
> - Brier skill score > 0 on validation set
> - **Accuracy skill > 0** on validation set"

**Code (`D_train_staged.py`):**
```python
ACC_SKILL_MIN_IMPROVEMENT = 0.005  # model val_acc must beat majority baseline by at least this
...
qualified = [
    (name, r) for name, r in candidates
    if r.get("val_brier_skill", float("-inf")) > 0.0
    and acc_skill(r) > ACC_SKILL_MIN_IMPROVEMENT   # > 0.005, not > 0
]
```
`acc_skill(r) = val_acc - majority_acc`. The threshold is **> 0.005** (0.5 percentage points above baseline), not simply `> 0`.

The same error appears verbatim in the Section 12 verification checklist.

**Fix:** "Accuracy skill > 0" → "Accuracy skill > 0.5 percentage points (0.005 absolute)".

---

## Discrepancy 9 — Improved Financial Performance is unsigned, not signed (Section 4.5)

**Section 4.5 of MD states:**
> "**Success Group:** average of 6 success-related **signed** tags: Targets Met or Exceeded, High Beneficiary Satisfaction or Reach, Private Sector Engagement, Capacity Building Delivered, Policy and Regulatory Reforms, **Improved Financial Performance**"

**Code (`final_tags.json`):**
```json
{"tag": "improved_financial_performance", "signed":"false", ...}
```
Improved Financial Performance is **unsigned** (`signed="false"`), not signed. The success group in the code (`MANUAL_FACTORS["factor_success"]`) correctly includes it, but the MD's description of the group as "6 success-related **signed** tags" is inaccurate.

**Fix:** Change "signed tags" to "outcome tags" (or clarify that the group mixes unsigned and signed).

---

## Discrepancy 10 — Third factor group (`factor_rescoping`) absent from Section 4.5

**Section 4.5 of MD** describes only two groups: Success Group and Financing Group.

**Code (`D_train_staged.py`, `MANUAL_FACTORS`):**
```python
MANUAL_FACTORS: dict[str, tuple[list[str], list[str]]] = {
    "factor_success":   ([6 tags], []),
    "factor_rescoping": (["tag_project_restructured", "tag_targets_revised",
                          "tag_closing_date_extended", "tag_funds_reallocated"], []),
    "factor_finance":   (["tag_high_disbursement"], ["tag_funds_cancelled_or_unutilized"]),
}
```
`factor_rescoping` IS trained (an RF+ET regressor is fit for it) and its predictions enter the OLS regression used to reconstruct per-tag probabilities for all blended tags. Omitting it gives an incomplete picture of the group averaging pipeline.

The code comment explains: `factor_rescoping is kept here for factor computation (its signal helps other tags via OLS) even though those tags are not in TAGS_FACTOR_BLEND and are not blended.`

**Fix:** Add `factor_rescoping` to Section 4.5 with a note that rescoping-group tags are NOT directly blended but the factor IS used as an OLS predictor input when reconstructing per-tag probabilities.

---

## Discrepancy 11 — Start-year correction net effect on ensemble is halved, not full (Section 4.6)

**Section 4.6 of MD states:**
> "The correction is applied to the **RF model alone** before averaging with ET (not applied to the averaged RF+ET prediction)."
> "Correction multiplier swept over {0, 0.1, 0.2, 0.5, 1.0, 1.5, 2.0}. Multiplier of **1.0 (full correction)** achieved best..."

The wording "full correction" is misleading. Applying the correction to RF only and then averaging with uncorrected ET means the **net effect on the ensemble is correction ÷ 2**, not the full correction magnitude.

**Code comment (`D_train_staged.py`, line 48–51):**
```python
# If True (original behaviour): correction applied to RF probas BEFORE averaging with ET,
# so the net effect on the ensemble is correction/2.
CORRECT_RF_BEFORE_ET = True
```

The multiplier sweep (`Z_sweep_year_correction.py`) scales the stored `year_corr_vec` before applying it, so a multiplier of 1.0 means: apply the fitted correction to RF, then average. The ensemble sees half the correction magnitude.

**Fix:** Clarify that "multiplier 1.0 (full correction to RF)" results in a half-magnitude correction in the RF+ET ensemble, and that sweeping over multipliers {0…2.0} is equivalent to sweeping ensemble-level correction magnitudes {0…1.0}.

---

## Minor Notes (no code discrepancy, but worth flagging)

- **Factor regressor hyperparameters** (Section 4.5): MD says "RF+ET regressor trained on 45 features" but the factor regressors use different parameters than the classifiers: `max_depth=8, min_samples_leaf=25` vs. classifiers' `max_depth=None, min_samples_leaf=5`. This is not wrong (45 features is accurate when DROP_NOISY_FEATURE_GROUPS=True), but the differing params are undocumented.
- **`oob_score=True` in RF**: The code sets `"oob_score": True` in `RF_PARAMS_BASE`. This is omitted from the hyperparameter table in Section 4.4, though it does not affect fitted predictions.
- **Seed examples in tag discovery** (Section 2.2): MD says "seed examples from manual inspection anchored the initial vocabulary." The code's `make_discovery_prompt()` does provide seed examples inline in the prompt (e.g., "implementation delays", "project was restructured", "capacity building training was delivered"). These examples were presumably from manual inspection, so the claim is directionally correct, but the examples are hardcoded in the prompt rather than loaded from a separate file or pass.
