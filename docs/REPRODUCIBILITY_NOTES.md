# Reproducibility notes

Updated September 21, 2026 for the current source code and manuscript. Original
analysis code and manuscript files were read-only inputs. Release provenance
and validation records use Unix timestamps and SHA-256 hashes.

## Latest MITI presentation and table-label update

The four-arm MITI score distribution now follows the current source and
manuscript colors, treatment labels and compact legend. Its regenerated PDF
matches the manuscript pixels at a 1,000-pixel rendering. The two-arm histogram
retains its existing styling, matching the separate manuscript exhibit; its
unhyphenated package label remains a documented presentation difference.
The saved scores, all seven checked numeric summaries and the three MITI table
fragments agree with current source outputs. No interviews were rescored.

The source now includes the Technology-based spelling and escaped currency
label fixes already present in the package. Both Stata scripts and their table
fragments are byte-identical to the source. Twenty of the 21 current table
fragments now match the manuscript text after whitespace normalization; only
the existing Within 30 min label correction remains. All 21 agree numerically.
Survey inputs, demand classifications and original-submission materials are
unchanged. See `manifest/latest_refresh_validation.json`.

## Earlier app-use control correction

The baseline app-use indicators now equal one when the app-minute midpoint
is greater than 2.5, matching the latest source. Previously the cutoff was zero.
Only these seven controls changed in `clean_data.dta`, `clean_merged.dta` and
`clean_merged_with_scrshots.dta`. Raw survey outcomes, participant/response keys,
follow-up sample sizes, screenshot values and saved classifications are unchanged.
Several other source DTA files were resaved but have identical released values.
The public cleaning pipeline reproduces all four cleaned files numerically.
The original-submission inputs remain frozen and reproduce the published tables.

Fourteen table fragments and eight figures have been refreshed. Every current
computed table has matching numeric entries and significance marks. The latest
source incorporates two earlier package label corrections; only “Within 30 min”
remains different, as described above. All eight figures refreshed for the
app-use correction match the manuscript pixels and were visually checked.

The six previously flagged manuscript prose discrepancies have been corrected.
The revised baseline and follow-up motivation effects, demand SUR p-values
(0.54 and 0.19), and screenshot-versus-self-report SUR p-value (0.375) agree
with the package. Exact comparisons are in
`manifest/app_use_controls_validation.json`. This checks the selected statements
affected by the corrected controls, not every sentence in the manuscript.

The manuscript's two-arm legend uses “Decisional-Balance”; the package retains
“Decisional Balance”. The later four-arm figure update is described above.
Score inputs and estimates remain unchanged.

## Earlier September 21 source update

The baseline writing filter now drops responses shorter than 20 characters
(`writing_chars < 20`), matching the source correction. The package continues
to use the supplied byte lengths instead of distributing the writing text.
The writing-cutoff correction alone leaves the participant keys, sample sizes
and numeric results unchanged. The later app-use correction above changes
covariates and adjusted estimates.

The manual question figure now places mixed-category labels inside their
respective colored segments and uses the source question labels. Language
similarity uses those same labels, sequence and categories. Its saved summary
now contains 63 classified questions (17/19/15/12 across the four arms).
Fourteen turns with `routine_change_wish` or `routine_change_followup` identifiers
from seven control interviews are excluded from TF-IDF and similarity;
other classified turns from those interviews remain. The source also corrects
self-pair removal for 11 zero-vector turns. The control different-topic reference
is 0.1216730023. This is an analysis correction, not only a rendering change.

The updated aggregate summary, question audit and audit text are distributed
under `data/derived/similarity_by_topic*`. Re-extracting them requires withheld
transcripts and the private survey arm mapping. Both refreshed figures match
the current manuscript's text and rendered pixels; binary PDF metadata can
differ. See `manifest/similarity_validation.json`.

## Experimenter-demand update

The demand analyses now use the saved **Luna v002** classifications for all
2,719 participants. Compared with v001, 192 category assignments changed.
The old classification file is removed from the working release. The new file
contains only anonymous release keys and the five-category code; all other
source columns, including the open-ended answers, are omitted.

The shared data loader, pooled figure and conditional-outcome tables follow
the updated source. `stats_expdemand.do` and its shared helper reproduce the
subgroup SUR tests with the corrected controls: p=0.539266 for motivation and
p=0.194554 for cost-benefit beliefs. The current manuscript prose now agrees
with the rounded values 0.54 and 0.19. Current category
counts are 253, 787, 286, 1,106 and 287. The binary reduction-hypothesis split
still totals 1,040 versus 1,679 participants, although membership has changed.
The unused by-arm figure and auxiliary demand table remain excluded.

Current release files contain no original Prolific or Qualtrics identifiers.
Legacy column names such as `prolific_id` contain anonymous P-number keys.
**Older Git commits still contain original identifiers.** This is separate
from the clean working files; committing these changes will not erase those
copies. See [PRIVACY.md](PRIVACY.md) and `manifest/identifier_validation.json`.

## Current survey inputs

The active raw follow-up export has **2,351 records** and the cleaned follow-up
file has **2,304**. The baseline merge contains **2,719 participants**, including
**2,302 nonmissing follow-up motivation responses** and **2,290 nonmissing
follow-up time-use responses**. There are 2,080 completed follow-up surveys.
The prior release's 2,130/2,119 counts no longer describe the default analyses.

The package includes deidentified versions of the updated raw follow-up,
cleaned survey, merged survey and adjudicated screenshot-measure files.
All nine distributed current survey inputs were checked against their source
numeric values. Running the public cleaning pipeline reproduced all numeric
variables in its four cleaned outputs at Stata storage precision
(`rtol=1e-6`, `atol=1e-8`). The corrected writing cutoff does not change the rebuilt baseline numeric
observations. Existing anonymous release IDs are preserved.

Every default survey analysis uses the current cleaned data. There is no
`manuscript_followup_snapshot.dta` override. The file named
`df_merged_llm_category_expdemand_luna_v002.dta` contains only anonymous IDs and
saved demand classifications. The public helper joins those categories onto
current survey data, including for supporting in-text statistics.

## Original-submission reconstruction

The original submission predates this expanded follow-up export. To preserve
its reproducibility, three already deidentified analysis files from the prior
release are frozen under `data/archival/original_submission/`. Only
`code/reproduce_submission.py` reads them, after checking their recorded hashes.
The default runners and public cleaning pipeline do not read this archive.

With these inputs and the documented archival specifications, all **11
numerical original-submission tables and 742 checked entries** reproduce.
The optional runner also generates static Table 1 with its original wording. See [SUBMISSION_TABLE_AUDIT.md](SUBMISSION_TABLE_AUDIT.md) for the
historical sample and reporting errors retained solely for reconstruction.
Differences from current follow-up estimates reflect the updated input sample
as well as the documented specification corrections; they are not rounding
issues. The archive is needed only when reconstructing the original submission.

## Current manuscript and code

All 21 computed tables agree numerically with the current manuscript exhibits;
one retains the label correction documented above. All 48 computed exhibits
regenerate successfully. The persistence estimates are now 0.136 for Change Talk
and 0.133 for Direct Persuasion (both p<0.05), and 0.055 for Decisional Balance
(not significant at 10%). The current manuscript prose, figure and table now
agree on the rounded 0.13 Direct Persuasion effect.

The questionnaire-change figure now labels effects in **raw scale points**,
matching the source correction. Its newly added source-only `tab_sm_change.tex`
export is excluded because it is not an active manuscript exhibit. Supporting
screen-time statistics retain the source's updated p-value display precision.
The ideal-time table retains the pre-treatment ideal and “Within 30 min” label;
attrition reports the control-group completion mean and explicit Control base.

The corrected September 18 MITI benchmark remains the input for C.1/C.2.
The manuscript now quotes its pooled global bias of -0.14 and correlation 0.73.
Its experimental stability table, violin and captions now use the same 2,048
eligible treated participants as the package. The earlier MITI prose and
full-corpus discrepancy notes are therefore removed. Saved scoring inputs
are unchanged; no interviews were rescored. See [MITI_REPLICATION.md](MITI_REPLICATION.md).

The manuscript appendix now has **67 prompt blocks**, all verified against
`code/prompts/parameters.py`. The control termination and end-of-interview
messages are no longer printed in the appendix; both are retained only as
existing routing metadata. See [PROMPTS.md](PROMPTS.md) for the exact verification scope.

All 27 released figures match their validated regenerated renderings. Twenty-one
are pixel-identical to the manuscript at 1,000 pixels; six differ in layout,
axis ticks, margins or rendering. Numeric table results agree. CDF colors and
legend handles remain tied explicitly to numeric treatment codes; the
Confidence Score label is preserved. No claim is made here to have audited
every manuscript sentence. `manifest/exhibit_text_validation.json` and
`manifest/figure_render_validation.json` record the comparisons.

## Restricted inputs

Raw interview transcripts, participant excerpts, screenshot images, request
payloads and model explanations are withheld. Public runners use deidentified
survey data, saved text-free measurements and manually specified question
stages. Re-extracting transcript measures requires the restricted data.
API-capable source methods remain disabled in the public package. Additional
API/compute cost for these local checks was $0; model requests were zero.
