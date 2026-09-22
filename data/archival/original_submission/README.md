# Original-submission survey inputs

These three files are byte-for-byte copies of already deidentified analysis
inputs from the September 17 release. They preserve the original submission's
survey sample after the September 19 follow-up update. They contain 2,719
baseline participants, 2,130 matched motivation responses and 2,119 matched
time-use responses. No external participant IDs or interview text are included.

Only `code/reproduce_submission.py` reads these files. The default runners and
cleaning pipeline use `data/processed/` and `data/raw/` with the current export.
File versions and checksums are recorded in
`manifest/submission_survey_snapshot.json`; see [submission audit](../../../docs/SUBMISSION_TABLE_AUDIT.md)
for reconstruction instructions and the archival specification corrections.
