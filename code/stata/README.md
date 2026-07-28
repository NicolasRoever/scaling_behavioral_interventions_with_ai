# Stata workflow

Run from this directory with Stata 17 or later:

```stata
do 02_run_exhibits.do
```

The scripts use the included processed survey datasets and write to
`../../results/`.

Community commands used by the exhibit code include `estout`/`esttab`,
`coefplot`, `binscatter`, `grstyle`, `blindschemes`, and `balancetable`.
Install missing commands from SSC before running the master file.

`01_clean_data.do` controls the raw-data cleaning pipeline. Baseline and
follow-up survey cleaning can be rerun from the supplied survey files. The
chat-cleaning and screenshot-source stages are retained for transparency but
their private raw inputs are not included.

`00_setup.do` contains the portable replication-package path configuration.
`99_sanitize_public_data.do` documents the removal of screenshot-upload file
metadata from the public survey copies.
