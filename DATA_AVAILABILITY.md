# Data availability

## Distributed

- Baseline and follow-up survey exports (`main_raw.dta`, `follow_up_raw.dta`).
  These are **deidentified exports**, not unmodified Qualtrics exports.
- The current cleaned baseline file (2,719 participants), follow-up file (2,304
  records), and merged survey/screen-time files.
- `clean_scr_data.dta`: structured screenshot measures and week-level validity
  indicators. Raw images, upload metadata and screenshot filenames are absent.
- `interview_scores_extracted.dta`: numeric importance/confidence ratings.
- Numeric MITI scores for the actual September 2026 campaign, including its
  benchmark, five stochastic replicates, prompt ablation and two comparison
  models. Only the 14 validation sessions used in the paper are released.
- Human global ratings for those 14 validation sessions; saved aggregate
  behavioral-validation statistics used by Panel B.
- Topic assignments without text, topic diagnostic metrics, pros/cons counts,
  fixed-category strategy selections, per-chat 30-minute mention indicators,
  aggregate interviewer-question positions and cosine similarities, and the
  frequent words/phrases displayed in the published word clouds.

`manifest/data_dictionary.csv` documents the Stata variables. The manifest and
code explain the definitions of the derived CSV fields.

## Removed or withheld

- All raw interview transcripts and participant-level transcript excerpts.
- Generated model explanations, raw responses, rendered prompts, request
  payloads, named pros/cons excerpts and free-form model output.
- All raw screenshots and upload filenames, IDs, sizes and MIME types, for all
  three screenshot questions.
- Prolific and Qualtrics response identifiers. These are consistently replaced
  by release IDs across survey files; the linking crosswalk is not distributed.
- Unused free-text survey answers, feedback and technical/browser metadata.
  Original fields are blanked where their presence is required by cleaning code.
- Credentials, `.env` files, notebook execution outputs and private caches.
- The manuscript's chat-interface screenshot, because it displays dialogue.

For the writing-task exclusion, `writing_chars` retains the original Stata
UTF-8 byte length; the writing response is blanked. This preserves sample
selection without distributing the text. Source survey timestamps keep their
original Stata units because the cleaning code depends on them. New run and
manifest timestamps are Unix seconds.

Study-internal numeric participant IDs and `MI-MAINEXP-<number>` session keys
remain in derived score files to allow audit joins; these are not external
recruitment-platform identifiers. Training-material session labels identify
MITI benchmark sessions, not study participants.

## What cannot be regenerated without restricted data

Refitting BERTopic, rerunning transcript classification/scoring, recomputing
interviewer-language similarities, finding 30-minute mentions in the original
turns, and re-extracting or adjudicating screenshot images require the omitted
source data. The public workflow starts from the saved text-free measurements.
The MITI behavioral-count validation panel starts from saved aggregate results;
it does not redo utterance-level coding or validation.

The restricted-input methods are included under `code/private/` with their
required filenames documented in its README. No private upstream workflow was
executed while preparing this release. API-capable Python sources are disabled
at import/execution in this package under the project's $0 OpenAI API policy.
