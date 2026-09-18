# Reproducibility notes

This release incorporates the source-code and manuscript updates inspected on
September 17, 2026. Only the replication package was changed; the original
analysis code and manuscript were read-only. Provenance and validation records
use Unix timestamps and SHA-256 hashes.

## Today's updates

- Interview prompts now follow Appendix D.1--D.4: all 69 blocks and four arm
  configurations were verified. Existing routing metadata for those arms is
  preserved. See `PROMPTS.md` and `manifest/prompt_validation.json`.
- The ideal-time table now compares follow-up use with **pre-treatment**
  `baseline_ideal_social_min_w`, matching the manuscript's intended definition.
  Its numerical entries also reproduce original-submission Table A.7. The old
  note about using the post-treatment ideal is no longer applicable.
- The attrition table now reports only completed follow-up, uses Control as
  the explicit reference arm, and calculates the control mean in the estimation
  sample. It matches the manuscript's one-column table.
- The question-sequence figure uses the manual appendix-stage specification
  from the updated source. Its Control panel has the fixed opener and 11
  interview turns; navigation messages are not plotted as interview questions.
  The obsolete transcript-based sequence input and method were removed.
- MITI robustness and stability calculations now filter every experimental
  scoring run to the cleaned survey sample: 2,048 treated participants and 671
  controls. Human validation retains its separate 14 sessions. Arm assignments
  come directly from the released cleaned survey; the redundant CSV was removed.
- The pros/cons figure now includes the source's mean labels inside each bar.
- The original-submission adapters were updated for the changed current
  scripts; all 11 numerical original tables continue to reproduce.

## Survey inputs

The survey datasets are unchanged by this synchronization. The active follow-up
export has 2,176 records and the cleaned follow-up file has 2,132. The baseline
merge has 2,719 participants, including 2,130 nonmissing follow-up motivation
responses and 2,119 nonmissing follow-up social-media-time responses.

Every default survey analysis uses the active cleaned data. No separate
`manuscript_followup_snapshot.dta` is required. The file named
`df_merged_llm_category_expdemand_v001.dta` contains only anonymous participant
IDs and saved demand classifications. The public helper joins those categories
onto current survey data, including for supporting in-text statistics. This
preserves the public data boundary when the original script refers to its
full private classification merge.

The prior raw-to-clean checks remain applicable: unchanged raw exports and
cleaning code reproduce all four cleaned datasets at Stata storage precision.
The earlier 2,302/2,290 follow-up counts remain superseded by the active snapshot.

## Revised manuscript and original submission

The Persistence paragraph now agrees with the refreshed motivation estimates:
0.147 for Change Talk (p<0.05), 0.161 for Direct Persuasion (p<0.01), and 0.068 for
Decisional Balance (not significant at 10%). The cost-benefit persistence prose
now uses the correct significance levels (p<0.01 and p<0.05), and the rounded
follow-up life-evaluation effect of 0.09 agrees with the table. The corresponding
obsolete discrepancy notes have been removed.

One wording issue remains: the current absolute-gap table's fourth column is
labeled “Below 30 min,” and the Change Talk sentence still says “below 30
minutes.” The calculation is **within 30 minutes of the baseline ideal**.
The source code/manuscript were not edited to resolve that label.

The manuscript's MITI stability table and violin figure still use the earlier
full scored corpus (2,195 treated interviews). The updated package follows
today's source code and exactly reproduces its new outputs for the 2,048
eligible treated participants. The manuscript captions still say “all treated”
or “full corpus.” Its robustness paragraph also needs the updated rounded
mean-difference/MAE pairs: stochastic reruns +0.01/0.23; prompt ablation
+0.07/0.25; gpt-5.5 +0.32/0.42; gpt-5.4 -0.19/0.39. The package records these
source-versus-manuscript differences without editing the manuscript.

`SUBMISSION_TABLE_AUDIT.md` distinguishes current analyses from the separate
archival runner, which reproduces all original printed numerical table entries.
The archival route retains documented published errors solely for reconstruction:
a mislabeled overall mean, duplicated hypothesis-test p-values, a follow-up
split labeled as baseline use, and the older 20-session global-validation panel.
The default analyses retain the corrected calculations.

`results/` contains verified default references, with inspected manuscript
hashes recorded separately. `submission_results/` contains archival references.
The validation report records any remaining rendering or label differences;
this synchronization does not claim a complete audit of every prose statement.

## Restricted inputs

Public runners use deidentified survey data and saved numeric/categorical
measurements, plus the manually specified question stages. Raw interview
transcripts, participant excerpts, screenshot images and model explanations
remain withheld. Re-extracting transcript measures requires the private data.
No APIs or private upstream workflows were run. The dialogue-containing
screenshot remains withheld, and static design assets are supplied as-is.
