# Data availability and privacy

## Included

- Baseline survey: `data/raw/main_socialmedia/main_raw.dta`
- Follow-up survey: `data/raw/main_socialmedia/follow_up_raw.dta`
- Cleaned survey and merged analysis files in
  `data/processed/main_social_media/`
- Structured app-use and screen-time measures extracted from screenshots in
  `data/processed/main_social_media/screenshot_data/`
- Text-free topic assignments and text-free MITI scores

## Deliberately excluded

- Raw interview/chat transcripts (`chats_raw.csv` and all equivalents)
- Participant-level pros/cons transcript input
  (`df_clean_with_llm_themes_pros_cons_v001.csv`)
- Participant-level strategy-classification excerpt input
  (`df_clean_with_llm_themes_strategies_v003.csv`)
- Example interview text
- Screenshot image files
- Screenshot filenames and exclusion logs
- Screenshot-upload file IDs, names, sizes, and MIME types
- Rendered per-interview API payloads, free-text justifications, and model
  responses that could echo transcript content
- Credentials and `.env` files

`data/private/interview_transcripts.txt` is a zero-byte placeholder marking the
location of the unavailable private interview data.

Because transcripts are unavailable, BERTopic fitting, interviewer-language
classification, and fresh MITI scoring cannot be rerun publicly. Their analysis
code is included for transparency, and the package supplies only the minimized
derived inputs needed to inspect downstream calculations where possible.

Fresh positive/negative-aspect extraction likewise requires the excluded
participant-level transcript input. `code/python/fig_pros_cons.py` contains the
complete prompt, structured-output call, local string counting, checkpointing,
audit exports, and figure-generation code.

Fresh strategy classification likewise requires the excluded 1,663-row
participant-level excerpt input. `code/python/fig_strategies.py` contains the
complete 12-category manual, structured-output call, backend Unix timestamp
provenance, resumable checkpointing, local share calculation, and figure code.

All reusable prompt templates are included and indexed in `PROMPTS.md`.
