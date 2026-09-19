# Data availability

## Distributed

- Baseline and follow-up survey exports (`main_raw.dta`, `follow_up_raw.dta`).
  These are **deidentified exports**, not unmodified Qualtrics exports.
- The current cleaned baseline file (2,719 participants), follow-up file (2,304
  records), and merged survey/screen-time files. The raw follow-up export has
  2,351 rows; the baseline merge has 2,302 motivation and 2,290 time-use responses.
- Three previously released deidentified analysis files under
  `data/archival/original_submission/`, used only to reproduce the original
  submission. Their older sample has 2,130 motivation and 2,119 time-use responses;
  `manifest/submission_survey_snapshot.json` identifies their versions and hashes.
- `clean_scr_data.dta`: structured screenshot measures and week-level validity
  indicators. Raw images, upload metadata and screenshot filenames are absent.
- `interview_scores_extracted.dta`: numeric importance/confidence ratings.
- Numeric experimental MITI scores from the September 10 campaign: benchmark,
  five stochastic replicates, prompt ablation and two comparison models.
- The corrected September 18 human-validation input: 504 numeric LLM/human
  pairs, 14 anonymous interview keys and fixed scoring-condition metadata.
  Superseded September 10 validation scores are omitted.
- The 80 human/model score pairs from the original 20-session global-score
  validation (November 2025), with anonymous keys and no text, used only to
  reconstruct original-submission Table C.1.
- Human global ratings for the current 14 validation sessions; saved aggregate
  behavioral-validation statistics used by Panel B.
- Topic assignments without text, topic diagnostic metrics, pros/cons counts,
  fixed-category strategy selections, per-chat 30-minute mention indicators,
  aggregate cosine similarities, and the
  frequent words/phrases displayed in the published word clouds.

The question-sequence figure is now drawn from the manually specified appendix
stages in `code/python/question_sequence.py`; it does not read transcript
positions or require interview data.

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
recruitment-platform identifiers. Corrected human-validation interviews use
anonymous `VALIDATION-0001` through `VALIDATION-0014` keys. These are separate
from study participants and the archival validation keys.

## What cannot be regenerated without restricted data

Refitting BERTopic, rerunning transcript classification/scoring, recomputing
interviewer-language similarities, finding 30-minute mentions in the original
turns, and re-extracting or adjudicating screenshot images require the omitted
source data. The public workflow starts from the saved text-free measurements.
The MITI behavioral-count validation panel starts from saved aggregate results;
it does not redo utterance-level coding or validation.

The restricted-input methods are included under `code/private/` with their
required filenames documented in its README. Saved local responses were checked offline while preparing this release;
no interviews were rescored and no model calls were made. API-capable Python sources are disabled
at import/execution in this package under the project's $0 OpenAI API policy.
