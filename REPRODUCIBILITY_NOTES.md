# Reproducibility notes and manuscript issues

The package reproduces the supplied manuscript's results. The following
inconsistencies were found while tracing those results; the manuscript was not
edited as part of this package update.

## Different follow-up snapshots

Five tables use a historical survey snapshot, whereas several newer figures
and tables use the current cleaned data. The older values are recoverable from
the survey columns retained in the original
`df_merged_llm_category_expdemand_v001.dta` (January 2026). The release contains
that deidentified snapshot as `manuscript_followup_snapshot.dta`.

It contains 2,130 nonmissing follow-up motivation responses and 2,119 nonmissing
follow-up screen-time responses. The current cleaned merge contains 2,302 and
2,290, respectively. For overlapping participants, raw outcomes agree, but
standardization and winsorization can differ because their reference samples
differ. This is an input-version difference, not a replication rounding issue.

The historical snapshot is used explicitly by:

- `tab_treatment_effect_motivation_followup.do`
- `tab_mechanism_strategies_followup.do`
- `tab_heterogeneity_timeuse_by_wedge.do`
- `tab_heterogeneity_timeuse_by_basetime.do`
- `tab_treatment_effects_closetoideal_followup.do`

Using this snapshot reproduces their manuscript numbers. The raw-to-clean
controller rebuilds the **current** survey files and deliberately does not
replace this historical snapshot. Resolving the manuscript's mixed samples
would require an author decision followed by consistent updates to its tables,
figures and prose.

## Alignment with ideal time

The supplied source script compared follow-up use with *post-treatment* ideal
time. The manuscript describes *pre-treatment* ideal time. Using
`baseline_ideal_social_min_w` with the historical snapshot exactly reproduces
the manuscript table. The replication script therefore uses the baseline
definition and labels column 4 “Within 30 min,” matching its actual absolute-gap
definition and the table. The manuscript prose's phrase “below their ideal plus
30 minutes” describes a different, one-sided outcome and needs review.

## Baseline-use heterogeneity table

The source code and reproduced manuscript numbers split participants on the
median of **follow-up** `w2_actual_social_min`, even though the table caption and
note call this baseline screen time. Stata's comparison assigns missing
follow-up values to the high group (`. > median`), which also affects the
predicted-time columns. This is not a valid interpretation as heterogeneity by
a pre-treatment baseline measure.

The same script stores the `a=c` p-value immediately after the `b=c` test,
without running `test 1.T = 3.T`. Thus the two reported p-value rows duplicate
each other. The release preserves these calculations for exact reproduction
and flags them here; changing them would change a published exhibit. This
table needs an author review before publication.

## Reference files and numerical fidelity

`results/` holds the exact source manuscript files, with SHA-256 hashes.
Runners write to `reproduced/`, so a local run cannot overwrite the references.
All analytic figures are regenerated from data or saved measurements, and all
table numbers are calculated by code. Static design assets are copied as-is.
The sole withheld image is explicitly recorded in the exhibit manifest.

The commented-out IRR section and its literature-comparison table are not
included. Alternative analyses, superseded notebooks and model runs not used
in the active revision are also excluded.
