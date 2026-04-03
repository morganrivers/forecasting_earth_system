# Section: Extracting and Interpreting Ratings

## Tex content summary

**Extraction:** Two methods. Primary: each post-activity page rated >7/10 for relevance (or with "quantitative targets" category) sent individually to gemini-2.5-flash to extract ratings. Fallback: custom word search (~500 rephrasings of "overall rating") on PDFs to identify pages, then gemini query on those pages. If no match, earliest non-excluded pages used.

**BMZ/KfW/GIZ exception:** Evaluation document used as pre-activity document (due to rare pre-activity docs); model instructed to only describe what could have been known at activity start.

**Interpretation:** World Bank 1–6 scale used as template. BMZ/KfW/GIZ ratings inverted. Percentages rescaled. Only top 4 orgs used for training/validation.

## Relevant code files
- `C_forecast_outcomes/C_run_GLM_rating.py` — loads extracted ratings via `load_ratings` (`MERGED_OVERALL_RATINGS` path); uses `load_grades` to load the LLM-extracted grade features
- `C_forecast_outcomes/C_predict_outcomes_saves_model.py` — same `load_ratings`, `load_grades`
- `outcome_tags/D_train_staged.py` — uses `load_ratings` (merged_overall_ratings.jsonl)

## Alignment
- ✅ Merged ratings JSONL used by all three model scripts matches the tex description of a unified 1–6 scale stored after aggregation.
- ✅ `load_grades` in all scripts loads the LLM-extracted grade features (0–100 scores per dimension), consistent with the tex description.
- ✅ 4-org restriction applied to training/validation in all scripts via `restrict_to_reporting_orgs_exact`.
- ✅ `rating_scheme_from_activity_id` function in helpers (imported in C_predict_outcomes_saves_model.py) handles per-org rating scale interpretation.

## Misalignment / gaps
- Extraction code itself (the two-method rating extraction pipeline and word search fallback) is in B_extract_structured_database/, not in the listed directories.
- The tex describes ~500 rephrasings for the word search; this is not verifiable from the listed scripts.
- BMZ-specific treatment (using evaluation doc as pre-activity) is described in tex but only handled at the data extraction stage upstream; the downstream model scripts treat BMZ activities identically to others once ratings are in the merged file.
