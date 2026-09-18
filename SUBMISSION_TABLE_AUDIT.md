# Original-submission table audit

All 12 tables in `ssrn-6081126.pdf` are covered: 11 numerical tables and the
static interview-structure table. The original-submission runner reproduces
all **742 checked entries in all 11 numerical tables**, including reported
standard errors, significance stars, sample sizes and hypothesis tests.
Table 1 is supplied with its original wording restored. The PDF's table pages
were visually inspected; the PDF itself is not distributed because it also
contains example interviews.

## Run the original-submission tables

After installing the Stata and Python dependencies described in `README.md`,
run from the package root (substitute your Stata executable):

```bash
python code/reproduce_submission.py --stata /Applications/Stata/StataSE.app/Contents/MacOS/stata-se
python code/compare_submission.py --submission
python code/verify_package.py --submission
```

The runner costs $0, makes zero API requests, and uses the same current public
survey snapshot as the default analyses. It constructs temporary copies of
the public scripts, applies the documented archival specifications below, and
writes only to `reproduced/submission/`. It requires no prior default run.
Success is marked by `SUBMISSION_REPRODUCTION_COMPLETE`; mismatched numerical
tables cause the runner to fail. `submission_results/` contains the verified
reference tables. These are archival reconstructions, not recommended updates
to the revised manuscript's analyses.

## Table-by-table results

Page numbers below count from the first PDF page, including the title page.
“Current” refers to the corrected default package analysis using the new survey
snapshot. “Original” refers to the separate archival runner.

| PDF table | PDF page | Subject | Current matching entries | Original matching entries |
|---|---:|---|---:|---:|
| 1 | 11 | Interview structures | Minor wording edits | Original wording restored |
| 2 | 35 | Follow-up strategies | 39/39 | 39/39 |
| A.1 | 43 | Baseline balance | 161/181 | 181/181 |
| A.2 | 44 | Follow-up attrition | 8/9 | 9/9 |
| A.3 | 45 | Follow-up balance | 161/181 | 181/181 |
| A.4 | 46 | Main mechanisms | 78/78 | 78/78 |
| A.5 | 47 | Social-media minutes | 39/39 | 39/39 |
| A.6 | 48 | Follow-up motivation and perceptions | 39/39 | 39/39 |
| A.7 | 49 | Alignment with ideal time | 52/52 | 52/52 |
| A.8 | 50 | Heterogeneity by baseline wedge | 49/52 | 52/52 |
| A.9 | 51 | Heterogeneity labeled baseline use | 6/52 | 52/52 |
| C.1 | 69 | Human/model MITI validation | 10/20 | 20/20 |

Comparisons use printed precision, retain significance stars and normalize
signed zero. “Controls: Yes” and the intentionally blank bias cell are checked
as well. Headers, captions and surrounding prose are not numerical cells.
The current A.2 analysis now reports a single completed-follow-up column,
matching the original table layout.

## Why the default analysis differs

- **A.1 and A.3:** The original social-media-use row and joint balance tests use
  `baseline_actual_social_min_w` (winsorized). Current source scripts explicitly
  use raw `baseline_actual_social_min`. Reinstating winsorization reproduces
  every original entry.
- **A.2:** The original printed “Control group mean” of 0.712 is the **overall**
  completion mean (0.7116586981). The actual control-group mean is 0.7183308495,
  or 0.718 rounded. All regression estimates, standard errors, N and R-squared
  already agree. The archival route reproduces the mislabeled overall mean;
  the default route reports the control mean correctly.
- **A.7:** The current source has now restored pre-treatment
  `baseline_ideal_social_min_w`, so all 52 numerical entries match the PDF.
  The archival route only restores the original “Within 30 min” heading; the
  current exporter still says “Below 30 min,” despite computing absolute gaps.
- **A.8:** The PDF's `a=c` row repeats the `b=c` test. Three rounded entries
  differ from a correctly calculated `test 1.T = 3.T`. The archival route
  retains the duplicated test solely to reconstruct the printed table.
- **A.9:** Despite its baseline-use description, the original numbers come from
  splitting on the median of **follow-up** `w2_actual_social_min`, with missing
  values entering the high-use group under Stata's comparison rules. Its
  `a=c` row also repeats `b=c`. The corrected default uses baseline use,
  excludes missing baseline values, and calculates the correct tests. The
  archival route explicitly reconstructs the old behavior.
- **C.1:** The original global-score panel uses the saved November 25, 2025
  model scores and **20** human-rated validation sessions, despite the PDF
  note saying 14. The current revised analysis uses the September 2026 Luna
  campaign on 14 sessions. Recomputing bias and Pearson correlations from
  80 released, text-free model/human score pairs reproduces all ten original
  global-panel entries. Panel B already matches; it uses the saved aggregate
  behavioral-validation statistics from 14 sessions.

These differences are not rounding problems or evidence that another survey
snapshot is needed. Reconstructing a published error does not validate its
interpretation. The archival adapters leave the default corrected scripts intact.

## Audit files and scope

- `manifest/submission_tables.json`: PDF hash, page/table crosswalk, verified
  printed cells, and reference hashes.
- `manifest/submission_comparison.json`: current-analysis differences from the PDF.
- `manifest/submission_archival_comparison.json`: the successful original-table
  comparison produced by the archival run.
- `reproduced/submission/comparison.json`: fresh comparison after each rerun.
- `data/derived/submission_miti_global_pairs.csv`: anonymous validation keys,
  score dimension, and numeric human/model scores only.

No raw interviews, model explanations, participant excerpts or private
identifier crosswalks are included. Re-extracting transcript measures requires
the withheld interview data. This audit checks all original-submission tables;
it does not claim to audit every sentence or figure in the original PDF.
