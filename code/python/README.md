# Offline Python workflow

Run `python code/python/run_public.py` from the package root. The runner resolves
paths from its own location and calls only modules in this directory. No API
client is imported. All function inputs are passed explicitly.

`requirements.txt` records the exact plotting stack tested with Python 3.9.12.
This stack can also be installed in Python 3.10. A different stack may render
fonts/spacing slightly differently; reference PDFs remain under `results/`.

The runner rebuilds topic plots from saved assignments/diagnostics; pros/cons
plots from integer counts; strategies from fixed-category selections; question
sequences, wording similarity and word clouds from aggregate inputs; and the
30-minute table from saved Boolean chat-level indicators.

MITI tables and figures use only the explicitly named September 2026 campaign.
The validation benchmark contains 14 sessions and 56 dimension-level ratings.
Five stochastic runs are additional ratings of those same sessions, not 70
independent interviews. Stability ranges are empirical score percentiles,
not confidence intervals for a mean. The existing behavioral-count validation
panel is reproduced from its saved aggregate statistics.

Actual transcript extraction, labeling, model fitting and LLM scoring require
the withheld data; see `../private/README.md`.
