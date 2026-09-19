# Offline Python workflow

Run `python code/python/run_public.py` from the package root. The runner resolves
paths from its own location and calls only modules in this directory. No API
client is imported. All function inputs are passed explicitly.

`requirements.txt` records the exact plotting stack tested with Python 3.9.12.
This stack can also be installed in Python 3.10. A different stack may render
fonts/spacing slightly differently; reference PDFs remain under `results/`.

The runner rebuilds topic plots from saved assignments/diagnostics; pros/cons
plots from integer counts; strategies from fixed-category selections; question
sequences from the manually specified appendix stages; wording similarity and
word clouds from aggregate inputs; and the
30-minute table from saved Boolean chat-level indicators.

MITI study-sample exhibits use the September 10 experimental campaign and
filter every run to the cleaned survey: 2,048 treated participants and 671
controls. Treatment assignments come directly from the released survey, and
each run must cover the complete eligible sample. Counts are recorded in
`reproduced/audit/survey_sample_audit.json`.

Tables C.1/C.2 instead use the corrected September 18 validation via
`miti_validation.py`: 504 scores from 14 interviews, four dimensions and nine
conditions. Luna uses low reasoning; GPT-5.4 and GPT-5.5 use none. Five stochastic
runs repeat the same 14 interviews; they are not 70 independent interviews.
The behavioral-count panel remains the saved historical summary. The old
September 10 human-validation scores and unused inputs have been removed.
See the package's `MITI_REPLICATION.md` for exact inputs and audit outputs.

Actual transcript extraction, labeling, model fitting and LLM scoring require
the withheld data; see `../private/README.md`.
