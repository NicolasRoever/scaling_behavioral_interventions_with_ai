# Reproducibility notes

Updated September 19, 2026 for the fully updated follow-up data. Original
analysis code and manuscript files were read-only inputs. Release provenance
and validation records use Unix timestamps and SHA-256 hashes.

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
(`rtol=1e-6`, `atol=1e-8`). The cleaning specifications and baseline numeric
observations are unchanged. Existing anonymous release IDs are preserved.

Every default survey analysis uses the current cleaned data. There is no
`manuscript_followup_snapshot.dta` override. The file named
`df_merged_llm_category_expdemand_v001.dta` contains only anonymous IDs and
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
The static Table 1 is also supplied. See `SUBMISSION_TABLE_AUDIT.md` for the
historical sample and reporting errors retained solely for reconstruction.
Differences from current follow-up estimates reflect the updated input sample
as well as the documented specification corrections; they are not rounding
issues. The archive is needed only when reconstructing the original submission.

## Current manuscript and code

All 21 computed LaTeX fragments agree with the revised manuscript after
whitespace normalization. All 48 computed exhibits regenerate successfully.
The refreshed persistence estimates are 0.137 for Change Talk and 0.141 for
Direct Persuasion (both p<0.05), and 0.063 for Decisional Balance (not significant
at 10%). The manuscript's rounded 0.14/0.14/0.06 motivation effects agree.

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
are unchanged; no interviews were rescored. See `MITI_REPLICATION.md`.

The manuscript appendix now has **68 prompt blocks**, all verified against
`code/prompts/parameters.py`. The control termination/navigation message is no
longer printed in the appendix and is retained only as existing routing
metadata. See `PROMPTS.md` for the exact verification scope.

All 27 released figures match their regenerated renderings. Eighteen are
pixel-identical to the manuscript at 1,000 pixels; nine differ in layout,
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
