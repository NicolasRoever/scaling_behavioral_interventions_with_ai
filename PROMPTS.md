# Prompt index

| Purpose | Source |
|---|---|
| Experimental interviews | `code/prompts/parameters.py` |
| MITI global scoring | `code/private/miti_scoring/miti_global_scores.py` |
| MITI behavioral counts | `code/private/miti_scoring/miti_behavioral_counts.py` |
| MITI model/replicate/ablation orchestration | `code/private/miti_scoring/run_campaign.py` |
| BERTopic labeling | `code/private/classify_bertopic.py` |
| Named positive and negative aspects | `code/private/fig_pros_cons.py`: `extraction_instructions()` |
| Twelve-category strategy coding | `code/private/fig_strategies.py`: `coding_instructions()` |
| Rule-based interviewer-question categories | `code/private/text_analysis/classify_manual.py` |
| Regex for 30-minute mentions | `code/private/text_analysis/thirty_minute_mentions.py` |

Experimental configurations are `TIME_USE`, `T1_MI_CHANGE`,
`T2_MI_AMBIVALENCE`, and `T4_CLEAR_PERSUASION`. The last of these corresponds to
`T=3` in the analysis data. The unused earlier persuasion configuration is not
included.

Only reusable instructions are distributed. Per-interview rendered prompts,
payloads and explanations are withheld because they contain transcript text.
Embedded credentials have been removed. No source-only scoring script is
called by the public runners.
