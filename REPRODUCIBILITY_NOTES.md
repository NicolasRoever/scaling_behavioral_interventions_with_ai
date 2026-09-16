# Reproducibility notes and manuscript issues

The package follows the manuscript exhibits after the author's September 16,
2026 analysis rerun. The manuscript itself was not edited by this package update.

## Historical survey-file issue resolved

The five previously stale follow-up tables now reproduce from the current
`clean_merged.dta`, using the original analysis scripts. The historical survey
snapshot and every analysis dependency on it have been removed from the package.
The follow-up motivation regression now uses 2,302 observations; the follow-up
screen-time outcome has 2,290 nonmissing observations. No older survey snapshot
is needed to reproduce the refreshed tables.

`df_merged_llm_category_expdemand_v001.dta` remains only as a two-column file of
anonymous participant IDs and saved demand classifications. The demand helper
joins those classifications onto the current cleaned survey data; it does not
use survey outcomes from the old classification export.

## Follow-up prose still needs synchronization

The regenerated motivation table reports Change Talk 0.137 (p<0.05), Decisional
Balance 0.063 (not significant), and Direct Persuasion 0.141 (p<0.05). The
manuscript's Persistence paragraph still reports 0.15, 0.07 and 0.16, and assigns
p<0.01 to Direct Persuasion. Rounded to two decimals, the refreshed estimates are
0.14, 0.06 and 0.14.

The cost-benefit persistence paragraph says p<0.001 for both Change Talk and
Direct Persuasion. The refreshed table has coefficients 0.151 (p approximately
0.005) and 0.094 (p approximately 0.088), respectively. The follow-up
life-evaluation paragraph still reports a Change Talk effect of 0.09; the
refreshed estimate is 0.052 (0.05 rounded to two decimals).

These are remaining prose/table discrepancies, not a need for historical data.

## Alignment with ideal time

The refreshed table and original source script compare follow-up use with
*post-treatment* `posterior_ideal_social_min_w`. The replication script now uses
that same definition and current data. The manuscript table note still describes
ideal time reported *prior* to the intervention and needs synchronization.

All four columns use an absolute gap (within 5, 10, 20 or 30 minutes). The fourth
column is still labeled “Below 30 min,” and the prose says “below their ideal
plus 30 minutes”; these descriptions suggest a different, one-sided outcome.
The package preserves the refreshed table's labels and calculations for exact
reproduction and records this unresolved interpretation issue here.

## Baseline-use heterogeneity table

The source code and refreshed manuscript numbers still split participants on
the median of **follow-up** `w2_actual_social_min`, even though the table caption
and note call this baseline screen time. Stata's comparison assigns missing
follow-up values to the high group (`. > median`), which also affects the
predicted-time columns. This is not a valid interpretation as heterogeneity by
a pre-treatment baseline measure.

The same script stores the `a=c` p-value immediately after the `b=c` test,
without running `test 1.T = 3.T`. Thus the two reported p-value rows duplicate
each other. The package preserves the refreshed source calculations and flags
them here. These issues are independent of the resolved historical-file issue.

## Reference files and numerical fidelity

`results/` holds the exact refreshed manuscript exhibit files, with SHA-256
hashes. Runners write to `reproduced/`. All computed tables and figures are
regenerated from public survey data or saved text-free measurements. Static
design assets are supplied as-is. The dialogue-containing screenshot remains
withheld explicitly.

The commented-out IRR section and its literature-comparison table, unused
analyses, superseded notebooks and model runs remain excluded.
