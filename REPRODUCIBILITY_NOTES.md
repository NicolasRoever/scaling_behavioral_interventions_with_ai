# Reproducibility notes

This package follows the source code and manuscript inspected on September 17,
2026. The manuscript and original analysis code were not edited by this update.

## Resolved items

- All five previously stale follow-up tables use current `clean_merged.dta`.
  The historical survey snapshot remains removed. The motivation regression
  uses 2,302 observations; follow-up screen time has 2,290 nonmissing values.
- The baseline-use heterogeneity analysis now splits on
  `baseline_actual_social_min`. Observations with missing baseline use are
  excluded from the split. The script now runs `test 1.T = 3.T` separately in
  each subgroup, so the `a=c` p-values are calculated correctly.
- The main-text Persistence paragraph now reports the current motivation
  estimates: 0.14 for Change Talk and Direct Persuasion (both p<0.05), and 0.06
  for Decisional Balance (not statistically significant).
- The packaged table exporters match the manuscript's corrected
  “Technology-based” spelling and escaped WTP dollar sign. These are label-only
  adjustments to the original exporters.

`df_merged_llm_category_expdemand_v001.dta` remains only as anonymous participant
IDs and saved demand classifications. Its categories are joined onto current
survey data; none of its old survey outcomes are used.

## Remaining prose discrepancies

These statements remain in the supplied `revision.tex`:

- The introduction still reports follow-up motivation effects of 0.15 for
  Change Talk, 0.16 for Direct Persuasion (p<0.01), and 0.07 for Decisional
  Balance. The current table gives 0.137, 0.141 (both p<0.05), and 0.063.
- The cost-benefit persistence paragraph still says p<0.001 for both Change
  Talk and Direct Persuasion. Their current estimates are 0.151 (p approximately
  0.005) and 0.094 (p approximately 0.088), respectively.
- The follow-up life-evaluation paragraph still quotes a Change Talk effect of
  0.09 standard deviations. The current estimate is 0.052 (0.05 rounded).

## Remaining ideal-time interpretation and prose discrepancies

The original script and reproduced table compare follow-up use with
*post-treatment* `posterior_ideal_social_min_w`. The alignment paragraph and
its table note still describe a *pre-treatment* ideal. Adding “absolute minutes”
to the table note does not resolve this timing difference.

The four outcomes are absolute gaps within 5, 10, 20 and 30 minutes. Column 4 is
still labeled “Below 30 min,” and the prose says “below their ideal plus 30
minutes,” which suggests a one-sided threshold instead.

The alignment paragraph also retains older estimates and conclusions. It quotes
Direct Persuasion effects of 5.3, 7.0, 8.2 and 9.9 percentage points, all with
p<0.01. The current table reports 1.3, 2.5, 3.1 and 3.6 percentage points, none
statistically significant at 10%. It says Decisional Balance has no significant
effects, while the current table reports 4.2 percentage points at 20 minutes
(p<0.10) and 5.4 at 30 minutes (p<0.05). The Change Talk effects in the current
table are also not statistically significant at 10%.

The package preserves the current source calculations and manuscript table
labels. These remaining issues concern the manuscript's interpretation and
prose, not a requirement for historical survey data.

## Reproduction scope

`results/` contains the exact current manuscript exhibits, with SHA-256 hashes.
The runners generate fresh outputs under `reproduced/` using public survey data
and saved text-free measurements. Raw interview transcripts remain withheld;
recomputing upstream transcript measures requires those private inputs.

Static design assets are supplied as-is. The dialogue-containing screenshot is
withheld explicitly. Commented-out exhibits, unused analyses, superseded
notebooks and model runs remain excluded.
