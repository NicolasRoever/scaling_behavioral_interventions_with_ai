# Release validation

Updated September 21, 2026 using local saved inputs only. Additional API/compute
cost was $0; model requests were zero. Original analysis code and manuscript
files were read-only inputs.

- Package layout: supporting Markdown files now live in `docs/`, leaving only
  `README.md` at the root. All 45 local Markdown links resolve. The duplicate
  archival output folder was removed, and the original-submission workflow was
  rerun successfully with numeric checks and fingerprints for all 12 outputs.
- Latest MITI refresh: regenerated the current four-arm distribution with the
  source colors, labels and compact legend; it matches the manuscript pixels.
  The two-arm histogram and stability violin regenerate unchanged. Three MITI
  table fragments and seven numeric summaries agree with source outputs. Scores
  were checked against all ten frozen experimental runs and the corrected
  benchmark. All six previously flagged numerical prose statements still agree
  with the results. Survey data and original-submission materials are unchanged.
- Latest app-use correction: all seven baseline use controls follow the source
  midpoint cutoff `> 2.5`. Three deidentified analysis datasets changed; raw
  outcomes, anonymous keys and sample sizes did not. The 14 affected table
  fragments and eight affected figures were regenerated in the preceding update.
  The resolved prose comparisons are recorded in [REPRODUCIBILITY_NOTES.md](REPRODUCIBILITY_NOTES.md) and
  `manifest/app_use_controls_validation.json`.
- Earlier September 21 refresh: baseline writing filter matches `< 20`; rebuilding
  four cleaned files reproduces every numeric variable and anonymous join key.
  Manual-question and similarity renderers follow current source definitions.
  The similarity input has 63 classified questions; its summary and aggregate
  audit agree, including the exclusion of 14 unclassified control turns and
  corrected self-pair handling for zero vectors. The two refreshed PDFs were
  visually inspected and match the current manuscript's text and pixels.
- Experimenter-demand update: Luna v002 codes cover all 2,719 participants;
  192 assignments differ from v001. The pooled figure and two conditional
  regression tables were refreshed and match the current manuscript. The source
  subgroup tests now give p=0.539266 and p=0.194554 with the corrected controls.
  Classification inputs and MITI scores are unchanged.
- Current-file identifier audit: zero matches to 3,264 source Prolific IDs and
  5,662 Qualtrics response IDs, including DTA metadata and extracted PDF text.
  All 12 survey/archival DTA files have anonymous ID values. The public verifier
  now checks identifier fields and exposed platform-ID patterns. **Git history
  has 14 affected older file versions and has not been rewritten**; see [PRIVACY.md](PRIVACY.md).
- Stata/SE 17 and Python 3.9.12 public runners completed: **48 computed exhibits**
  (27 PDFs and 21 LaTeX fragments), plus supporting audit summaries. Completion
  markers and Stata logs were checked, as well as process exit codes.
- All **21 generated table fragments match the manuscript numerically**,
  including significance marks. Twenty match after whitespace normalization;
  only the existing Within 30 min label correction remains. The latest source
  incorporates the other two previous label corrections. No numeric table
  results or table references changed in this refresh.
- All **27 released figures match their validated regenerated renderings**.
  Twenty-one are pixel-identical to the current manuscript at 1,000 pixels; six
  retain reviewed presentation differences in layout, labels or axis ticks.
  All 27 manuscript comparisons were refreshed. The newly updated MITI figure
  was visually inspected; both CDFs retain their earlier three-curve comparison
  at normalized PDF-vector tolerance 1e-7.
- The archival runner reproduced **11/11 original numerical tables and 742/742
  checked entries**. The optional archival runner generates all 12 tables; the
  redundant output folder is removed. Expected table entries and normalized
  output hashes remain in `manifest/submission_tables.json`. Three
  already deidentified prior-release survey files are frozen for this route;
  their hashes are checked before each archival run. Default runners use the
  fully updated data. See [SUBMISSION_TABLE_AUDIT.md](SUBMISSION_TABLE_AUDIT.md).
- All nine current survey datasets were checked against original source numeric
  values (`rtol=1e-6`, `atol=1e-8`), with consistent anonymous participant/response
  IDs and privacy exclusions. All derived inputs, including the refreshed
  similarity summary from the earlier update, retain their validated hashes.
- Running the public cleaning pipeline from deidentified raw data reproduced
  all numeric variables in four cleaned files at the same tolerance. Counts are
  **2,351 raw follow-up, 2,304 cleaned follow-up, 2,302 matched motivation and
  2,290 matched time-use responses**. The baseline sample remains 2,719.
- Corrected MITI validation inputs retain all 504 paired scores on 14 interviews
  across nine conditions. Both table fragments match the source builder and
  manuscript byte-for-byte; three full-precision audit CSVs match source results
  at `rtol=atol=1e-12`. Existing saved-response provenance checks remain valid.
- All ten experimental scoring runs match their frozen source scores. Each
  treated run covers 2,048 eligible participants; the control run covers 671.
  Four summary CSVs match current source outputs at `rtol=atol=1e-12`.
  The stability table and violin now agree with the manuscript's updated sample.
- All **67 current Appendix D prompt blocks** and four-arm routing links were
  rechecked. The control termination and end-of-interview messages are no longer
  printed in the appendix; both remain routing metadata outside this claim.
- Python files parse; public paths process local inputs only. Restricted methods
  retain execution guards. Raw transcripts, participant excerpts, screenshot
  uploads, payloads, explanations, external IDs and credentials are excluded.
  The three archived survey files are byte-for-byte copies of previously verified
  deidentified files. `.env` remains ignored.
- The active manuscript inventory remains 51 external references: 48 computed,
  two static assets and one withheld dialogue screenshot. Unused source outputs
  such as `tab_sm_change.tex` and commented-out robustness analyses are excluded.
- Release checksums cover code, documentation, data and references. Rerun outputs,
  logs and caches are excluded. Installation also checks for concurrent edits.

The manifests record numeric, privacy, input-version, prompt, figure and table
comparisons. [REPRODUCIBILITY_NOTES.md](REPRODUCIBILITY_NOTES.md) explains the updated follow-up data;
[MITI_REPLICATION.md](MITI_REPLICATION.md) documents the distinct saved MITI campaigns. These checks
cover the supplied analyses and exhibits, not every statement in the manuscript.
