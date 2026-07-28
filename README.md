# Replication package

This package contains the code, public survey data, and published exhibit files
for **“Evaluating Behavioral Interventions at Scale with AI.”**


## Directory guide

- `code/stata/`: all code written in stata; survey cleaning, analysis, figures, and tables.
- `code/python/`: all code written in python; topic model, text, and MITI analyses.
- `code/prompts/`: prompts used to conduct the experimental interviews.
- `data/raw/main_socialmedia/`: baseline and follow-up survey files.
- `data/processed/main_social_media/`: cleaned analysis files and public,
  text-free derived measures.
- `results/figures/` and `results/tables/`: the exact exhibit files referenced
  by the manuscript, except the excluded screenshot.
- `EXHIBIT_MANIFEST.md`: manuscript exhibit-to-code crosswalk.
- `DATA_AVAILABILITY.md`: included and excluded data.
- `PROMPTS.md`: complete prompt-location index.

## Prompts used in this project

The complete prompt index is in `PROMPTS.md`.

- **Experimental interview prompts:** `code/prompts/parameters.py`.
  This is the requested copy of
  `/Users/nicolasroever/Dropbox/MI/code/prompts/Prompts_SocialMedia/parameters_v018.py`
  and contains the global system prompts, opening questions, and turn-specific
  instructions for all four experimental arms.
- **MITI global-score prompt:** `code/python/miti_scoring/miti_global_scores.py`.
- **MITI behavioral-count prompt:** `code/python/miti_scoring/miti_behavioral_counts.py`.
- **BERTopic labeling prompt:** `code/python/classify_bertopic.py`.
- **Positive/negative-aspect coding prompt:** `code/python/helper.py`.


## Quick start

To run the analyses made in stata:

1. Open Stata 17 or later.
2. Install the community packages listed in `code/stata/README.md`.
3. Change the working directory to `code/stata`.
4. Run `do 02_run_exhibits.do`.

Generated files are written to `results/figures` and `results/tables`.

The raw-to-clean survey pipeline can be started with `do 01_clean_data.do`.
The screenshot-cleaning and chat-cleaning stages cannot be reconstructed from
raw images/transcripts because those private sources are deliberately absent.
The corresponding cleaned, non-image analysis files are supplied.

For Python, create an environment and install:

```bash
python -m pip install -r code/python/requirements.txt
```

Then follow `code/python/README.md`. Analyses that require conversation text
cannot be rerun from this public package; their text-free derived inputs and
published outputs are provided for auditability.

## Treatment coding

- `T = 0`: time-use interview control
- `T = 1`: Change Talk
- `T = 2`: Decisional Balance
- `T = 3`: Direct Persuasion

## Privacy

The raw interview transcripts and screenshot images are private and are not
included. `data/private/interview_transcripts.txt` is intentionally empty.
Transcript-derived topic assignments and MITI scores are included without the
underlying conversation text or model justifications. All reusable prompt
templates are included. Rendered per-interview API payloads are not included
because they contain the private transcript inserted into the template.
Structured screen-time measures extracted from screenshots are included, but
the screenshot images and screenshot filenames are not.
