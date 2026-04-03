# Section: Data Filtering

## Tex content summary
~800,000 IATI activities → 3,225 completed environment/sustainability projects. Filtering steps:
1. Sector code selection + manual topic review
2. Downloadable documents with valid temporal ordering (baseline ≤ end of Q1 of implementation; evaluation ≥ start of Q4)
3. PDF metadata validation (median 22-day discrepancy vs. document date; Gemini-assisted check of 400 PDFs)
4. Keyword search (6,800 terms) for leakage — excluded 21 activities with substantive progress
5. Restricted to 4 reporting orgs with sufficient data (World Bank 957, BMZ/KfW/GIZ 240, ADB 156, FCDO 127)
6. Activity status = completed only

## Relevant code files
- `C_forecast_outcomes/C_run_GLM_rating.py` — enforces the 4-org restriction (`restrict_to_reporting_orgs_exact`, `KEEP_REPORTING_ORGS`), `DROP_INCOMPLETE = True` flag
- `C_forecast_outcomes/C_predict_outcomes_saves_model.py` — same org restriction and `DROP_INCOMPLETE` logic
- `outcome_tags/D_train_staged.py` — same org restriction (`restrict_to_reporting_orgs_exact`, `NUM_ORGS_KEEP = 4`)

## Alignment
- ✅ 4 reporting orgs enforced in all three scripts via `restrict_to_reporting_orgs_exact`. KEEP_REPORTING_ORGS lists exactly World Bank, BMZ, ADB, FCDO.
- ✅ Completed-only filter: `DROP_INCOMPLETE = True` in C_predict_outcomes_saves_model.py; `load_is_completed` imported in D_train_staged.py.
- ✅ Temporal split boundaries (train ≤ 2013-02-06, val ≤ 2016-06-06, test cutoff < 2020-01-01) are consistent with the filtering described.

## Misalignment / gaps
- **Split definition discrepancy**: C_run_GLM_rating.py uses **count-based** splits (`HELDOUT_SET_SIZE = 200`, `VALIDATION_SET_SIZE = 300`) via `split_latest_by_date_with_cutoff`, while C_predict_outcomes_saves_model.py and D_train_staged.py use **date-based** splits (`LATEST_TRAIN_POINT = "2013-02-06"`, `LATEST_VALIDATION_POINT = "2016-06-06"`). The tex describes only date-based splits. These should produce similar boundaries given the dataset size, but the two approaches may not be exactly equivalent.
- The upstream PDF filtering, temporal ordering checks, and keyword leakage search are not in the listed code directories (they are in A_collect_database/ and B_extract_structured_database/).
