# Reproducibility notes

This release uses the active follow-up snapshot and source code inspected on
September 17, 2026. The original analysis directories and manuscript were not
modified. All released results are tied to this snapshot by SHA-256 hashes.

## Survey snapshot

The supplied follow-up export has 2,176 records. Cleaning yields 2,132 records;
the 2,719-person baseline merge contains 2,130 nonmissing follow-up motivation
responses and 2,119 nonmissing follow-up social-media-time responses.
Rebuilding all four cleaned survey files from the supplied deidentified
exports reproduces every numeric variable within Stata storage precision.

All default survey analyses read the active cleaned data. There is no separate
`manuscript_followup_snapshot.dta`, and no table requires the survey columns
from an old demand-classification file. The file named
`df_merged_llm_category_expdemand_v001.dta` contains only anonymous participant
IDs and saved demand classifications, joined onto the current survey data.

The prior release's 2,302/2,290 follow-up counts and its resulting coefficient
comparisons are superseded by the newly supplied snapshot. Matching the original
submission's sample counts now does not imply that every current analysis uses
the original specification.

## Original submission

`SUBMISSION_TABLE_AUDIT.md` covers every table in `ssrn-6081126.pdf`.
The separate archival runner reproduces all 11 numerical tables exactly at
printed precision, and restores the original static Table 1 wording. It
explicitly reconstructs the published specifications and reporting errors;
the default scripts retain the corrected baseline split and hypothesis tests.

The differences include raw versus winsorized balance measures, baseline
versus post-treatment ideal time, a mislabeled overall mean, duplicated test
p-values, a follow-up split labeled as baseline, and the old 20-session global
validation panel. These are documented specification/reporting differences,
not a need to restore stale survey outcomes.

## Current revised manuscript

The 48 computed default exhibits were regenerated. `results/` now contains
references consistent with those calculations. `manifest/exhibits.json`
records both the released reference hashes and the separately inspected source
manuscript exhibit hashes. All numerical table entries agree with the inspected
revised manuscript's current table files; two text differences are the
package's corrected “Technology-based” spelling and escaped WTP dollar sign.

Twenty-four of 27 figures match the inspected manuscript pixel-for-pixel at
1,000 pixels. Three have visual rendering differences with matching plotted results:
topic-count diagnostics, topic seed stability and pros/cons counts. Released
references use the public runners' output for these figures. The BERTopic
figure also incorporates the source update excluding the outlier category
after fixing the full-conversation denominators.

Some prose remains inconsistent with the refreshed analyses:

- The Persistence paragraph still gives motivation effects of 0.14, 0.14 and
  0.06. The new table reports 0.147 for Change Talk (p<0.05), 0.161 for Direct
  Persuasion (p<0.01), and 0.068 for Decisional Balance (not significant at 10%).
  The introduction's rounded 0.15/0.16/0.07 now agrees with the table.
- The cost-benefit paragraph still says p<0.001 for both treatments. The new
  table reports 0.167 for Change Talk (p<0.01) and 0.118 for Direct Persuasion
  (p<0.05). The former release's 0.151/0.094 discussion is obsolete.
- The alignment prose describes a pre-treatment ideal and gives the original
  A.7 estimates. The current default script instead uses the post-treatment
  ideal: Direct Persuasion effects are 1.5, 2.6, 3.6 and 4.0 percentage points,
  all insignificant at 10%. Decisional Balance has effects of 4.4 and 5.0
  percentage points at 20 and 30 minutes (both p<0.10). The absolute-gap fourth
  column remains labeled “Below 30 min”; that label suggests a one-sided
  threshold, while the actual calculation is within 30 minutes.

The follow-up life-evaluation estimate is 0.088, so the prose's rounded 0.09
now agrees. These notes do not claim a complete audit of all manuscript prose.

## Restricted inputs

Public runners use deidentified survey data and saved numeric/categorical
measurements. Raw interview transcripts and participant-level excerpts remain
withheld. Recomputing upstream transcript measures requires the private data;
no API calls or private upstream workflows were executed. Static design assets
are supplied as-is, and the dialogue-containing screenshot remains withheld.
