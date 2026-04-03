# Section: Extracting Outcome Tags

## Tex content summary

**Outcome summaries:** Up to 10 post-activity pages selected per activity (prioritizing deviation/delay/spending pages), submitted to gemini-2.5-flash to produce 3–10 paragraph outcome summary. Rating withheld from summary.

**Tag discovery:** 250 outcome summaries sampled, divided into batches of 10, each batch submitted to gemini-2.5-flash to identify recurring outcome types. Seed tags from manual inspection provided. 25 batches deduplicated/merged manually → 23 outcome tags.

**Tag types:** 11 "unsigned" tags (false if not mentioned, e.g., delays) + 12 "signed" tags (recorded only if explicitly mentioned, e.g., infrastructure completion). Two LLM passes per activity to extract all tags.

**Categories:** Finance & budget, Activity rescoping, Process/implementation, Target achievement.

## Relevant code files
- `outcome_tags/C_apply_tags_at_scale.py` — applies finalized tags at scale (upstream extraction, not a listed "final form" file)
- `outcome_tags/D_train_staged.py` — loads applied tags via `load_applied_tags` from `applied_tags.jsonl` (`APPLIED_TAGS` path)
- `outcome_tags/E_plot_staged.py` — defines `TAG_GROUPS` dict with the 4 categories and all tag names

## Alignment
- ✅ TAG_GROUPS in E_plot_staged.py defines exactly 4 categories: "Finance & budget", "Activity Rescoping", "Target achievement", and "Process & implementation" — matching the tex.
- ✅ The tag names in E_plot_staged.py (e.g., `tag_funds_cancelled_or_unutilized`, `tag_closing_date_extended`, `tag_targets_met_or_exceeded_success`, `tag_high_disbursement`) match the tex description of 23 tags across 4 categories.
- ✅ D_train_staged.py loads from `applied_tags.jsonl` which is the output of C_apply_tags_at_scale.py.
- ✅ D_train_staged.py EXCLUDE_ATTEMPTED_TAGS = True flag excludes _attempted tag columns, consistent with the two-type tag distinction described in the tex.

## Misalignment / gaps
- The tex says 23 outcome tags total; E_plot_staged.py TAG_GROUPS lists all tag entries — need to count: Finance (4) + Rescoping (3) + Target achievement (8 visible) + Process entries = verify total adds to 23. (E_plot_staged.py read was truncated at line 80; full tag list not confirmed.)
- Tag discovery/application code (A_discover_candidate_tags.py, B_consolidate_taxonomy.py, C_apply_tags_at_scale.py) is in the outcome_tags directory but not in the "final form" files specified by the user. The extraction pipeline is upstream of D_train_staged.py.
