# Release validation

Validation used local saved inputs only. Additional API/compute cost was $0;
there were zero model requests. The original manuscript and analysis
directories were not modified.

## Completed checks

- Both public runners completed: Stata/SE 17 and Python 3.9.12 with the pinned
  plotting stack.
- All **48 computed exhibits** were regenerated: 27 PDFs and 21 LaTeX fragments.
- All 21 generated table fragments match the manuscript after whitespace
  normalization, including coefficients, standard errors, p-values, sample
  sizes, labels and notes present in the fragments.
- Extracted text matches for all 27 generated PDFs.
- At a 1,000-pixel rendering dimension, 22 of 27 figures are pixel-identical.
  The other five were visually compared with their references: topic seed
  stability, topic-count diagnostics, pros/cons counts, baseline actual vs.
  ideal time, and interview duration. Their differences concern margins,
  ticks, strokes or rendering; the plotted results agree. Exact manuscript
  PDFs are retained under `results/` for publication fidelity.
- Survey cleaning was executed in an isolated copy. It reproduced row counts
  and all numeric variables in `clean_data.dta`, `follow_up_clean.dta`,
  `clean_merged.dta` and `clean_merged_with_scrshots.dta`, using numerical
  tolerances `rtol=1e-6, atol=1e-8` for Stata storage precision.
- All distributed Python files parse. The public modules do not import API or
  HTTP clients, or any restricted-input source.
- Data checks found no raw transcript fields, free-form model explanations,
  external participant IDs or screenshot-upload metadata. Fixed strategy
  selections contain only the 12 named categories. Survey open-text fields are
  blanked; the writing-task exclusion uses saved numeric byte lengths.
- All 50 distributed reference assets match the active manuscript's hashes.
  The dialogue-containing screenshot is withheld explicitly. Commented-out and
  unused exhibits are absent from the release.

The machine-readable exhibit text, rendered-figure and privacy check summaries
are in `manifest/`. `release_checksums.json` protects the delivered source,
data, documentation and reference files. Regenerated outputs and local logs
are excluded from release checksums and the distributable archive.

## Scope and limits

Transcript-derived measures are reproduced downstream from saved numeric or
categorical results. Their extraction from raw interviews cannot be verified
without the withheld data. Behavioral-count validation uses its saved aggregate
results. Static experimental-design assets are supplied, not regenerated.

The validation establishes reproduction of the supplied manuscript files; it
does not resolve the mixed follow-up samples or heterogeneity-specification
issues documented in `REPRODUCIBILITY_NOTES.md`, and it is not a claim that every
number in the prose has been independently audited.
