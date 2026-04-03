# Section: Data Processing — PDF Ranking and Page Categorization

## Tex content summary

**PDF document ranking:** Documents sorted into pre-activity (created ≤ 1/4 through activity) and post-activity (created ≥ 3/4 through). Preliminary ranking by proximity to start/end date and page length (3–20 pages preferred). Final ranking via gemini-2.5-flash: first 3 pages of each document uploaded together with activity metadata, returning a JSON of ranked docs with letter grades (A+ to F) and include/exclude flags. Result: 2,312 documents retained after ranking.

**Page categorization:** Highest-ranked documents split into 3-page chunks sent to gemini-2.5-flash. Two category assignments per page: (1) content category (23 pre-activity options, 8 post-activity options) and (2) exclusion category (glossary, blank, TOC, etc.). Used for later page retrieval and filtering.

## Relevant code files
None of the listed directories (C_forecast_outcomes/, D_data_analysis/, outcome_tags/) contain document ranking or page categorization code. This pipeline is upstream in `B_extract_structured_database/`.

## Alignment
- ✅ The categorization output (page relevance scores, content categories) is consumed downstream: C_run_GLM_rating.py and D_train_staged.py load `outputs_targets_context_maps.jsonl` (`TARGETS_CONTEXT_MAPS` path) which is the output of the categorization/extraction pipeline.
- ✅ The pre/post activity document separation is enforced by the date logic in the data filtering.

## Misalignment / gaps
- Document ranking and page categorization code is not in the listed directories; cannot perform direct code-to-tex alignment for this section from the listed files.
- The tex says "2,312 documents had sufficiently informative activity information and activity evaluation documents" after ranking — this count is not verifiable from the listed scripts.
