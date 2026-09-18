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
- The prior cleaning validation was run in an isolated copy from the supplied
  deidentified raw exports. The survey files and cleaning scripts are unchanged
  in this synchronization, and their hashes were rechecked. All four rebuilt analysis datasets match all numeric variables and
  row counts of the released files (`rtol=1e-6, atol=1e-8`).
- All nine released Stata datasets match the active source files in row count
  and retained numeric values at those tolerances. Writing-task byte lengths
  match the original text lengths; saved demand classifications match; release
  identifier mappings are consistent across files. Follow-up counts are
  2,176 raw, 2,132 cleaned, 2,130 matched motivation and 2,119 matched time use.
- All 21 default table fragments match the released references after
  whitespace normalization. Twenty agree numerically with the inspected
  manuscript; the updated MITI stability table instead matches today's source
  output exactly. The package also corrects “Technolgy-based” to “Technology-based.”
  PDF text matches all 27 manuscript figures; 23 are pixel-identical at 1,000
  pixels. Topic-count diagnostics, topic seed stability and pros/cons counts
  retain equivalent plotted values with minor rendering differences. The
  updated MITI violin differs from the earlier manuscript figure and is
  pixel-identical to today's source output. All four differences were reviewed.
- Every experimental MITI run covers the complete eligible survey sample:
  2,048 treated participants and 671 controls. Stability/robustness summaries
  and treatment means match six current source CSVs at `rtol=atol=1e-12`.
  The human-validation sample remains 14 sessions. See
  `manifest/miti_sample_validation.json` and `REPRODUCIBILITY_NOTES.md`.
- All 69 Appendix D prompt blocks match after removing wrapping and alltt
  typesetting wrappers. The four-arm configuration and all routing links pass
  verification; existing routing metadata is preserved. The configuration has
  an empty API key and contains no executable model client.
- The updated question-sequence figure matches its manuscript reference
  pixel-for-pixel. The source's new pros/cons mean labels were verified visually.
- All distributed Python sources parse. Public execution paths do not import
  API/HTTP clients or restricted-input scripts. The archival runner uses
  local Stata and saved numeric validation scores only.
- The release excludes raw transcripts, participant excerpts, model
  explanations, external participant IDs and screenshot-upload metadata.
  Required open-text fields are blanked. Previously checked derived files are
  unchanged; the added original-validation input has only anonymous session
  keys, four named score dimensions and numeric model/human scores.
- All 151 original-code files inventoried before this synchronization remain
  byte-for-byte unchanged. Only the replication package is updated.
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
