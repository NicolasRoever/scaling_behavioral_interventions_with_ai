# Release validation

Completed September 17, 2026 using local saved inputs only. Additional
API/compute cost was $0; model requests: zero. The original manuscript and
analysis directories were not modified.

- The Stata/SE 17 and Python 3.9.12 public runners completed and regenerated
  all **48 computed exhibits**: 27 PDFs and 21 LaTeX table fragments.
- The separate original-submission runner completed and reproduced **all 11
  numerical tables and all 742 checked entries** in `ssrn-6081126.pdf`.
  All 12 table pages were visually inspected. The static protocol table is
  supplied with its original wording restored. Published reporting errors are
  explicitly documented in `SUBMISSION_TABLE_AUDIT.md`.
- Cleaning was rerun in an isolated copy from the supplied deidentified raw
  exports. All four rebuilt analysis datasets match all numeric variables and
  row counts of the released files (`rtol=1e-6, atol=1e-8`).
- All nine released Stata datasets match the active source files in row count
  and retained numeric values at those tolerances. Writing-task byte lengths
  match the original text lengths; saved demand classifications match; release
  identifier mappings are consistent across files. Follow-up counts are
  2,176 raw, 2,132 cleaned, 2,130 matched motivation and 2,119 matched time use.
- All 21 default table fragments match the released references after
  whitespace normalization. Their numerical results also agree with the
  inspected revised-manuscript tables. Two labels differ: “Technology-based”
  spelling and the escaped WTP dollar sign. PDF text matches for all 27
  figures; 24 are pixel-identical to the inspected manuscript at 1,000 pixels.
  The three remaining comparisons were visually inspected: topic-count
  diagnostics, topic seed stability and pros/cons counts. Their
  plotted results agree; styling, margins, ticks or rendering differ.
- All distributed Python sources parse. Public execution paths do not import
  API/HTTP clients or restricted-input scripts. The new archival runner uses
  local Stata and saved numeric validation scores only.
- The release excludes raw transcripts, participant excerpts, model
  explanations, external participant IDs and screenshot-upload metadata.
  Required open-text fields are blanked. Previously checked derived files are
  unchanged; the added original-validation input has only anonymous session
  keys, four named score dimensions and numeric model/human scores.
- `.env` is ignored. Release checksums cover code, documentation, data and both
  sets of reference results. Regenerated outputs, caches and logs are excluded.

`manifest/` contains source-data, raw-to-clean, privacy, exhibit comparison,
original-submission and checksum reports. Exhibit comparison reports clearly
separate the inspected manuscript files from refreshed released references.

Transcript-derived measures can be reproduced only downstream from saved
measurements. Their extraction requires the withheld interviews. Behavioral
validation starts from saved aggregate statistics. Static assets are supplied,
not estimated. Table matching establishes numerical reproduction; it does not
endorse reporting errors retained solely for the archival reconstruction.
