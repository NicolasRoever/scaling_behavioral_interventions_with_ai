# Stata workflow

Run from this directory using `do 02_run_exhibits.do`. All paths are resolved
by `00_setup.do` relative to this directory. Outputs go to `../../reproduced/`.

Required community packages: `estout`, `coefplot`, `binscatter`, `grstyle`,
`palettes`, `colrspace`, `blindschemes`, `balancetable`, `fre`, `winsor2`.

`01_clean_data.do` rebuilds current baseline/follow-up/merged survey files from
deidentified raw survey exports and supplied numeric screenshot/scaling-score
inputs. It does not invoke the private transcript or screenshot-image steps.

All follow-up tables use `clean_merged.dta` from the current cleaning
pipeline, now using the September 17 snapshot (2,130 matched motivation
responses and 2,119 matched time-use responses). No separate historical survey
snapshot is used. The root
`REPRODUCIBILITY_NOTES.md` records the corrected baseline split and coefficient tests, and identifies
remaining manuscript prose/interpretation discrepancies.

The separate `../reproduce_submission.py` runner constructs the original
submission specifications in temporary copies. It leaves these corrected
default scripts intact; see `../../SUBMISSION_TABLE_AUDIT.md`.

`stats_quoted_in_text.do` logs the original supporting numerical calculations.
Its demand calculation uses the same current survey merge and saved categories
as the new demand tables, rather than relying on stale survey columns in the
historical classification file.
