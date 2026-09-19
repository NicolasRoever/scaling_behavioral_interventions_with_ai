# Release validation

Updated September 19, 2026 using local saved inputs only. Additional API/compute
cost was $0; model requests were zero. Original analysis code and manuscript
files were read-only inputs.

- Stata/SE 17 and Python 3.9.12 public runners completed: **48 computed exhibits**
  (27 PDFs and 21 LaTeX fragments), plus supporting audit summaries. Completion
  markers and Stata logs were checked, as well as process exit codes.
- All **21 generated table fragments match the revised manuscript** after
  whitespace normalization. References were refreshed where outputs changed.
  The nine changed tables were compiled into a local preview for visual review.
- All **27 released figures match their regenerated renderings**. Eighteen
  are pixel-identical to the manuscript at 1,000 pixels; nine comparisons were
  visually reviewed. Differences concern rendering/layout and MITI treatment
  labels/axis ticks. Both CDFs additionally match all three manuscript curves
  at normalized PDF-vector tolerance 1e-7. The five changed figures were reviewed.
- The archival runner reproduced **11/11 original numerical tables and 742/742
  checked entries**. All 12 archived reference tables are unchanged. Three
  already deidentified prior-release survey files are frozen for this route;
  their hashes are checked before each archival run. Default runners use the
  fully updated data. See `SUBMISSION_TABLE_AUDIT.md`.
- All nine current survey datasets were checked against original source numeric
  values (`rtol=1e-6`, `atol=1e-8`), with consistent anonymous participant/response
  IDs and privacy exclusions. All derived CSV inputs retain their validated hashes.
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
- All **68 current Appendix D prompt blocks** and four-arm routing links were
  rechecked. The control termination message is no longer printed in the appendix;
  it is retained as existing routing metadata, outside the 68-block claim.
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
comparisons. `REPRODUCIBILITY_NOTES.md` explains the updated follow-up data;
`MITI_REPLICATION.md` documents the distinct saved MITI campaigns. These checks
cover the supplied analyses and exhibits, not every statement in the manuscript.
