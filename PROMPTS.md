# Prompt index

This package includes all reusable prompt templates used for the experimental
interviews and the LLM-based exhibit-generation workflows.

## Experimental interviews

`code/prompts/parameters_v018.py`

This is the experimental prompt configuration requested for public release. It
contains:

- the Change Talk global system prompt and every turn-specific instruction;
- the Decisional Balance global system prompt and every turn-specific
  instruction;
- both Direct Persuasion configurations (`T3_DIRECT_PERSUASION` and
  `T4_CLEAR_PERSUASION`), including their global and turn-specific
  instructions;
- the Time Use control global system prompt and every turn-specific
  instruction;
- opening questions, scaling questions, wrap-up instructions, response
  contracts, and interview sequencing metadata.

The file therefore contains five named configurations covering the four study
arms: `TIME_USE`, `T1_MI_CHANGE`, `T2_MI_AMBIVALENCE`,
`T3_DIRECT_PERSUASION`, and `T4_CLEAR_PERSUASION`.

The public copy replaces the hard-coded API key with
`os.getenv("OPENAI_API_KEY")`. No prompt wording was changed.

## MITI measurement

- `code/python/miti_scoring/miti_global_scores.py`
  - `MAIN_PROMPT`: full session-level scoring template.
  - `MITI_GUIDE`: instructions and anchors for the four MITI global dimensions.
- `code/python/miti_scoring/miti_behavioral_counts.py`
  - `MITI_BEHAVIOR_COUNTS_PROMPT`: utterance-level behavioral-count coding
    template and category definitions.

The scoring and robustness scripts import these single-source prompt
definitions rather than duplicating them.

## Topic and qualitative coding

- `code/python/classify_bertopic.py`
  - prompt used to assign concise labels and summaries to BERTopic clusters.
- `code/python/fig_pros_cons.py`
  - `extraction_instructions()`: active prompt used to identify distinct
    positive and negative aspects of social media as short strings. The model
    returns lists of named aspects and is explicitly instructed not to count;
    Python computes the figure inputs from the list lengths.
- `code/python/fig_strategies.py`
  - `coding_instructions()`: active 12-category coding manual used to identify
    strategies for reducing social media use. The model returns only selected
    category names; Python computes participant shares by treatment arm. The
    default model is `gpt-5.6-luna` with low reasoning.
- `code/python/helper.py`
  - `prompt_positive_negative`: legacy count-producing prompt retained only for
    provenance of the superseded analysis.

## Privacy boundary

Prompt templates are public. Rendered prompt payloads are not included when
they contain a participant's private transcript substituted into placeholders
such as `{transcript}`, `{text}`, or `{documents}`. This preserves the exact
instructions while withholding the interview content.
