# Stata workflow

Run from this directory using `do 02_run_exhibits.do`. All paths are resolved
by `00_setup.do` relative to this directory. Outputs go to `../../reproduced/`.

Required community packages: `estout`, `coefplot`, `binscatter`, `grstyle`,
`palettes`, `colrspace`, `blindschemes`, `balancetable`, `winsor2`.

`01_clean_data.do` rebuilds current baseline/follow-up/merged survey files from
deidentified raw survey exports and supplied numeric screenshot/scaling-score
inputs. It does not invoke the private transcript or screenshot-image steps.

Five tables use `manuscript_followup_snapshot.dta`; the root
`REPRODUCIBILITY_NOTES.md` explains the historical sample and the two issues
with the baseline-use heterogeneity table. This snapshot is not overwritten by
the cleaning controller.

`stats_quoted_in_text.do` logs the original supporting numerical calculations.
Its demand calculation uses the same current survey merge and saved categories
as the new demand tables, rather than relying on stale survey columns in the
historical classification file.
