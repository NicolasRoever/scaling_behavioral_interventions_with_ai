# Scaling Behavioral Interventions with AI: replication package

This is the replication package for the paper: 
This repository contains the replication materials for:

> **Felix Chopra, Ingar Haaland, Nicolas Roever, and Christopher Roth.**  
> *Evaluating Behavioral Interventions at Scale with AI.*  
The manuscript hash and current exhibit inventory are in `manifest/exhibits.json`.

To protect the privacy of our experimental subjects, we do not provide the raw interview transcripts. 



## Reproduce the results

### Stata

Use Stata 17 or newer. The validation used Stata/SE 17. Install the required
community packages once: `estout`, `coefplot`, `binscatter`, `grstyle`,
`palettes`, `colrspace`, `blindschemes`, `balancetable`, `fre`, and `winsor2`.

From Stata, change to this package's `code/stata` directory, then run:

```stata
do 02_run_exhibits.do
```

To reconstruct the current survey analysis files from the supplied survey
exports, run `do 01_clean_data.do` first. It uses the supplied, adjudicated
numeric screenshot measures and extracted scaling-question scores; it does
not require raw screenshot images or transcript text. 

### Python

The public workflow was tested with Python 3.9.12 and the exact versions in
`code/python/requirements.txt`. Use a dedicated Python 3.9 or 3.10 environment:

```bash
python -m pip install -r code/python/requirements.txt
python code/python/run_public.py
```
The runner works from any directory and generates 17 Python exhibit files plus
numeric audit summaries in `reproduced/audit/`.


### Reproduce the original-submission tables

After installing the same dependencies, run from the package root:

```bash
python code/reproduce_submission.py --stata /path/to/stata-executable
python code/compare_submission.py --submission
```

For macOS Stata/SE, the executable is commonly
`/Applications/Stata/StataSE.app/Contents/MacOS/stata-se`. The original-table
runner works independently of the default runners and writes to
`reproduced/submission/`. Its reference tables are in `submission_results/`.
It uses the three deidentified analysis files frozen under
`data/archival/original_submission/` and checks their hashes before reconstructing
the published specifications, including documented reporting errors. 


## Contents

| Location | Contents |
|---|---|
| `code/stata/` | Public survey cleaning, tables, figures, and supporting statistics |
| `code/python/` | Offline plotting and tabulation from saved derived results |
| `code/private/` | Restricted-input methods and prompts; never invoked by public runners |
| `code/prompts/parameters.py` | All four appendix protocols; 68 checked prompt blocks |
| `data/raw/` | Deidentified baseline and follow-up survey exports |
| `data/processed/` | Current survey files and text-free screenshot measures |
| `data/archival/original_submission/` | Frozen deidentified inputs used only for the original-submission tables |
| `data/derived/` | Numeric/categorical inputs for transcript-derived exhibits |
| `results/` | Current-analysis reference exhibits refreshed for the supplied snapshot |
| `submission_results/` | Original-submission tables reconstructed with the documented archival specifications |
| `reproduced/` | Fresh outputs written by the public runners; not part of the release |
| `manifest/` | Exhibit crosswalk, data dictionary, redaction record and checksums |

There are 51 active external exhibit references: 48 computed exhibits, two
static assets, and one withheld chat-interface screenshot containing dialogue.
The two static assets are supplied as-is. 

`T=0` is Control (time-use interview); `T=1` is Change Talk; `T=2` is Decisional
Balance (called Ambivalence in some source data); `T=3` is Direct Persuasion.

Read `PROMPTS.md` for the appendix prompt text and verification command,
`EXHIBIT_MANIFEST.md` for every exhibit's generating code,
`DATA_AVAILABILITY.md` for the privacy boundary, and
`REPRODUCIBILITY_NOTES.md` for input-version details and remaining presentation differences. 


### Note for Developer: How to Verify the distribution

```bash
python code/check_privacy.py
python code/verify_package.py
python code/verify_package.py --reproduced
python code/verify_package.py --submission
```

The first command verifies the reference-file hashes, release checksums and
restricted-file exclusions. The second additionally requires every generated
exhibit and compares all regenerated LaTeX table bodies with the released
references. The third checks the freshly regenerated archival tables against
the original PDF entries. The initial check also verifies the supplied archival
reference tables against the PDF entries.
See `VALIDATION.md` for the completed release checks and their limits.

Run the initial checksum check before cleaning. Stata rewrites binary metadata
when saving rebuilt datasets, so after running `01_clean_data.do` use
`python code/verify_package.py --reproduced --allow-rebuilt-data`. This still
checks all other release hashes and all generated table bodies; it skips the
original binary hashes of the four reconstructed survey files.
