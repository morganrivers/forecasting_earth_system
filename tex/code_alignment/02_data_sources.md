# Section: Data Sources

## Tex content summary
Evaluated and rejected: OpenAlex (no pre-activity docs), AidData (<30% overlap with IATI, fewer records), 3ie (<300 environmental records), IDEAL (<300 records). Selected: IATI database (large volume, pre/post document pairs, reliable temporal metadata, ongoing additions). Country-level covariates from World Bank governance indicators (WGI), CPIA scores, and GDP per capita.

## Relevant code files
- `C_forecast_outcomes/C_run_GLM_rating.py` — loads WGI, CPIA, GDP per capita via `load_world_bank_indicators`, `load_gdp_percap`
- `C_forecast_outcomes/C_predict_outcomes_saves_model.py` — same loaders
- `outcome_tags/D_train_staged.py` — same loaders (`load_world_bank_indicators`, `load_gdp_percap`)

## Alignment
- ✅ World Bank governance indicators used: `load_world_bank_indicators` is imported in all three model scripts.
- ✅ GDP per capita used: `load_gdp_percap` imported in all three scripts.
- ✅ CPIA is referenced in tex as a feature; it is loaded in C_run_GLM_rating.py as part of world bank indicator loading (likely bundled in the same data file).
- ✅ AidData analysis attempted: `analyze_and_merge_aiddata.py` and `aiddata_iati_analysis_summary.json` exist in C_forecast_outcomes/, confirming AidData was explored and rejected.

## Misalignment / gaps
- The tex says CPIA is a separate feature. C_run_GLM_rating.py does not appear to have a dedicated `load_cpia` function; it may be included in `load_world_bank_indicators` or in the info_for_activity_forecasting CSV. Cannot confirm from code reads alone.
- No code files in the listed directories handle the initial IATI data collection (that is upstream in A_collect_database/ and B_extract_structured_database/).
