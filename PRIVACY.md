# Identifier audit

The current release files contain **no original Prolific IDs**. Survey joins
use anonymous `P00001`-style keys, and response joins use `R00001`-style keys.
Some columns retain legacy names such as `prolific_id` or `prolific_pid` for
compatibility with the cleaning scripts; their values are anonymous release
keys. `MISSING_ROW_...` values are internal placeholders, not platform IDs.
The linking crosswalk is not distributed.

The release audit compared working files, DTA metadata, CSVs, code, and extracted
PDF text against 3,264 known source Prolific IDs and 5,662 Qualtrics response IDs:
zero were found. All 12 current and archival DTA files passed the anonymous-key
checks. Raw interview text, free-form demand answers and model explanations
remain excluded.

Before committing, run:

```bash
python code/check_privacy.py
python code/verify_package.py
```

The identifier check inspects working files, including untracked files. It
rejects nonanonymous values in survey ID columns and recognizable exposed
platform-ID patterns elsewhere, including binary DTA metadata. It does not
inspect compressed PDF text or Git objects; those were checked separately
when preparing this release. The full source-ID crosswalk is never required
by or distributed with the public checks.
