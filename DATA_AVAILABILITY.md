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

All reusable prompt templates are included and indexed in `PROMPTS.md`.
