# MITI replication inputs

Updated September 21, 2026. All public processing is offline: $0 additional
API/compute cost and zero model requests. Raw transcripts, transcript correction
records, request/response payloads and model explanations are not distributed.

## Scoring prompts

The reusable [global scoring templates and four coding rubrics](../code/prompts/miti_global_scores.py)
and [behavioral-count instructions](../code/prompts/miti_behavioral_counts.py) are in
`code/prompts/`. The [usage guide](../code/prompts/README.md) explains how to render
study, topic-neutral validation, and conservative-sentence ablation prompts.
The standard and ablated global prompts and coding rubrics were checked against
the frozen September 10 study campaign and September 18 validation inputs.

## Corrected human validation: Tables C.1 and C.2

`data/derived/miti_validation_20260918/scores.csv` contains 504 saved score pairs
on 14 anonymous interviews: four dimensions in each of nine conditions. Its
manifest names the exact source batch and records source/release checksums.
The input contains only anonymous session key, condition ID/type, replicate,
model, reasoning setting, prompt variant, dimension, LLM score and human score.

The September 18 source workflow corrects transcript roles (P/I = clinician;
C = client), handles documented extraction/continuation corrections, and uses
a topic-neutral validation prompt with no Change Goal passage. The conditions
are one Luna baseline, five additional independent Luna runs, one Luna ablation
removing only the conservative-scoring sentence, and one run each of
GPT-5.5-2026-04-23 and GPT-5.4-2026-03-05. Luna uses low reasoning; the two other
models use none. These are existing saved results, not new scoring requests.

`code/python/miti_validation.py` checks the input hash, full 14-by-4-by-9 design,
condition metadata, integer score ranges and consistency of human ratings.
It uses the original builder's condition definitions, summary calculations and
table rendering. Bias is LLM minus human; correlation is Pearson's correlation
of paired scores. Global pools four dimensions. Pooled stochastic results use
280 pairs across five runs but still represent 14 unique interviews.

C.1 Panel B is read from the unchanged
`data/derived/miti/inputs/behavioral_results.csv`; no behavioral scoring is rerun.
The baseline global bias is -0.142857 and correlation 0.732832, printed as
-0.14 and 0.73. C.1 panel headings and C.2 lettered procedure headings follow
the updated source formatting. Superseded campaign validation scores are removed.

Run `python code/python/run_public.py`. The two table fragments are written to
`reproduced/tables/`; `table_c1.csv`, `table_c2.csv` and `summary_per_run.csv`
are written to `reproduced/audit/`. Release checks compare these results with
all current source tables and summaries and independently check the original
saved-response join (`manifest/miti_benchmark_validation.json`).

## Experimental study exhibits

`data/derived/miti/manifest.json` retains only the ten experimental scoring runs
from the September 10 campaign: nine treated runs and the control baseline.
All experimental comparisons first merge with the released cleaned survey and
check complete coverage of 2,048 treated participants and 671 controls. The
builder explicitly rejects a different treated-sample size. The stability
percentiles describe individual scores, not confidence intervals of means.

The corrected human-validation results do not replace or rescore experimental
interviews. The frozen experimental scoring inputs remain unchanged, including
their historical transcript construction. This separates the two input versions
explicitly; neither older human-validation results nor incomplete runs are used
as a fallback.

## Original submission

`code/reproduce_submission.py` continues to use the separate 80 numeric pairs
from the original 20-interview validation. It reconstructs original Table C.1,
including its historical values, and does not substitute the corrected benchmark.
See [SUBMISSION_TABLE_AUDIT.md](SUBMISSION_TABLE_AUDIT.md) for that archival route.

## Manuscript status

The refreshed manuscript C.1/C.2 and stability tables match the package exactly.
The stability violin is also pixel-identical at the checked rendering resolution.
The manuscript now reports the corrected -0.14/0.73 human-validation benchmark
and the 2,048-person eligible experimental sample, so the earlier discrepancy
notes are obsolete. The saved scoring inputs are unchanged by the survey update.
The new cleaned merge retains the same 2,048 treated participants and 671 controls.

The all-arm score distribution now follows the latest source palette: light
gray Control, red Change Talk, gray Decisional balance and purple Persuasion.
The labels, compact legend and layout match the current manuscript; its
regenerated rendering is pixel-identical at 1,000 pixels. The two-arm histogram
retains the separate manuscript exhibit's red/purple styling and the package
label “Decisional Balance” (the manuscript prints “Decisional-Balance”).
The source and manuscript all-arm update does not change scores or estimates.
All seven numeric summaries and three MITI table fragments were rebuilt locally
and agree with the saved source outputs. The stability violin and two-arm
histogram regenerate unchanged. No API or transcript-processing runs were made.
Source manuscript hashes and rendering comparisons are recorded separately.
Only the replication package is updated; original analysis and manuscript files
are read-only inputs.
