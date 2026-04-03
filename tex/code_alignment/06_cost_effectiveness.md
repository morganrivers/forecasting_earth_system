# Section: Extracting Cost-Effectiveness Outcomes

## Tex content summary
Cost-effectiveness = quantitative outcomes / activity expenditure. Outcomes extracted from pages categorized as containing quantitative outcomes using gemini-2.5-flash. Not limited to 4 orgs (unlike ratings). Common outcome categories identified via bigram frequency + manual inspection, requiring ≥10 activities in the evaluation date range (2013-02-06 to 2016-06-06).

**Final outcome categories reported:**
- Benefit/cost ratios (B/C)
- Economic rate of return (ERR/EIRR) and financial rate of return (FRR/FIRR)
- CO₂/CO₂e reductions (total or per year, tonnes)
- Water/sanitation connections (counts)
- Energy generation capacity (MW or GWh)

**Excluded (insufficient counts):** pollution load, forest indicators, air quality PM2.5, cooking stoves, agricultural yields.

**Aggregation:** Multiple extracted values per category aggregated via gemini-2.5-flash into single project-level outcome. Budget allocation splits costs across non-overlapping sub-activities. CO₂ treated as special case (inherits allocation from linked mitigation outputs if present). log₁₀ transform applied to all categories except B/C ratios and rates of return.

## Relevant code files
- `C_forecast_outcomes/C_predict_outcomes_saves_model.py` — the outcome prediction model (ZAGG: z-score aggregation across outcome types); trains RF/ridge on log-transformed outcomes
- `C_forecast_outcomes/C_do_outcomes_depend_on_ratings.py` — analyzes correlation between cost-effectiveness outcomes and overall activity ratings (supplementary analysis, same structure as C_predict_outcomes_saves_model.py)

## Alignment
- ✅ `ONLY_USE_THESE_AND_ASSERT_EXIST_WITH_COUNTS` in both scripts defines which outcome columns to use. Includes B/C ratios, ERR, FRR, CO₂ (tonnes and per-year), water connections, generation capacity (MW, GWh) — matching the tex.
- ✅ `EXCLUDE_DPU_DISTS = {"benefit_cost_ratios", "economic_rate_of_return", "financial_rate_of_return"}` in C_predict_outcomes_saves_model.py — excludes these from dollar-per-unit calculations, matching tex statement that these are "inherently unit-free or already normalised".
- ✅ `add_groupwise_z` function implements the group-wise z-score normalization described in the tex (log₁₀ transform happens upstream when constructing `activity_outcomes.csv`).
- ✅ Date-based split in C_predict_outcomes_saves_model.py: LATEST_TRAIN_POINT = "2013-02-06", LATEST_VALIDATION_POINT = "2016-06-06" matches the tex requirement that outcomes have ≥10 activities in the evaluation date range.

## Misalignment / gaps
- **Code includes outcomes the tex excludes:** `ONLY_USE_THESE_AND_ASSERT_EXIST_WITH_COUNTS` in both C_predict_outcomes_saves_model.py and C_do_outcomes_depend_on_ratings.py includes `out_dpu_area_protected__hectares`, `out_dpu_area_reforested__hectares`, `out_dpu_area_under_management__hectares`, `out_dpu_pollution_load_removed__tonnes_per_year`, `out_dpu_stoves__count_stoves`, `out_dpu_trees_planted__count`. The tex explicitly says these (forest indicators, pollution load, stoves) were parsed but "contributed insufficient counts to be useful for further outcome forecasting." These columns are present in code but may be dropped by the `filter_groups_min_counts` function at runtime (requiring ≥10 train and ≥10 test rows). Needs verification whether these are silently dropped at runtime or actually used.
- **C_do_outcomes_depend_on_ratings.py** is not explicitly described in the methodology tex. Its purpose (analyzing whether outcomes depend on ratings) is implied by the broader analysis context but there is no dedicated methodology subsection for this analysis.
- The budget allocation / cost-splitting algorithm described in the tex (HHI-based bucketing, equal share per bucket, CO₂ special case) is an upstream pipeline step not in the listed directories.
