# Prompt index

- [Interviewer prompts](../code/prompts/parameters.py)
- [MITI global scoring prompts](../code/prompts/miti_global_scores.py)
- [MITI behavioral-count prompts](../code/prompts/miti_behavioral_counts.py)
- [Prompt usage guide](../code/prompts/README.md)

## Interviewer prompts

`code/prompts/parameters.py` contains the interview prompts in Appendix D.1--D.4
of the inspected `revision.tex`. The appendix is the authority for their text.
All **67 blocks** were checked: four global prompts, four fixed opening
messages and 59 turn-specific prompts printed in the current appendix.

| Appendix | Arm | Configuration key | Generated turns |
|---|---|---|---:|
| D.1 | Change Talk | `T1_MI_CHANGE` | 16 |
| D.2 | Decisional Balance | `T2_MI_AMBIVALENCE` | 18 |
| D.3 | Direct Persuasion | `T4_CLEAR_PERSUASION` | 14 |
| D.4 | Control (time use) | `TIME_USE` | 11 |

`T4_CLEAR_PERSUASION` corresponds to treatment `T=3` in the analysis data.
The unused earlier `T3_DIRECT_PERSUASION` configuration is omitted because it
is not one of the four appendix protocols.

Only line wrapping/spacing and the `alltt` typesetting wrappers (`\Copy` and
`\linebreak`) are normalized. Literal punctuation in the appendix blocks is
retained, including their quote/dash notation and the `---END---` sentinel.
The existing routing keys, history windows, global-prompt overrides, fallback
settings and other engine metadata for the four retained arms are preserved.
Those metadata are not inferred from the appendix's prose. The existing control
`termination_message` and `end_of_interview_message` are retained as routing
metadata. The current appendix no longer prints either, so both are outside
the 67 verified appendix blocks. The latter matched the prior appendix version;
none of the remaining printed prompt text changed in this update.

The file contains configuration data only. Its API-key value remains empty;
no client is loaded and no interviews or model requests are run. Updating the
released prompt text does not regenerate or alter the experimental observations.

## Verify against the manuscript

The manuscript is not distributed because other appendices contain interview
examples. If you have a local copy, run:

```bash
python code/prompts/check_appendix.py --manuscript /path/to/revision.tex
```

This reads the bounded interviewer-prompt section, compares every block, and
checks the question order and routing links. It parses the Python configuration
as literal data without executing it. `manifest/prompt_validation.json` records
the manuscript/configuration hashes, block hashes and successful checks.

## Other reusable instructions

| Purpose | Source |
|---|---|
| Experimental interviews | `code/prompts/parameters.py` |
| MITI corrected validation preparation | `code/private/miti_scoring/miti_benmchmarking/prepare_validation_batch.py` |
| MITI global scoring | [`code/prompts/miti_global_scores.py`](../code/prompts/miti_global_scores.py) |
| MITI behavioral counts | [`code/prompts/miti_behavioral_counts.py`](../code/prompts/miti_behavioral_counts.py) |
| MITI model/replicate/ablation orchestration | `code/private/miti_scoring/run_campaign.py` |
| BERTopic labeling | `code/private/classify_bertopic.py` |
| Named positive and negative aspects | `code/private/fig_pros_cons.py`: `extraction_instructions()` |
| Twelve-category strategy coding | `code/private/fig_strategies.py`: `coding_instructions()` |
| Manual question-stage categories from the appendix | `code/python/question_sequence.py`: `configuration()` |
| Regex for 30-minute mentions | `code/private/text_analysis/thirty_minute_mentions.py` |

Only reusable instructions are distributed. Per-interview rendered prompts,
payloads, model explanations and transcripts remain withheld. No restricted
scoring workflow is called by the public runners.

MITI global-scoring definitions now distinguish `MAIN_PROMPT` (the study's
social-media goal) from `VALIDATION_PROMPT` (topic-neutral, with the Change Goal
passage removed). The corrected September 18 validation uses the latter.
This change does not rescore the frozen experimental campaign. Its conservative
sentence ablation and model reasoning settings are documented in
[MITI_REPLICATION.md](MITI_REPLICATION.md).
