# Python workflow

Install `requirements.txt` and run scripts from this directory. The exhibit
crosswalk is in `../../EXHIBIT_MANIFEST.md`.

The public package supports two levels of verification:

1. Downstream plotting and tabulation from included survey data and minimized,
   text-free derived files.
2. Inspection of the full topic-modeling, language-analysis, and MITI-scoring
   code.

Fresh BERTopic fitting, interviewer-language analysis, and LLM scoring require
the private interview corpus and therefore cannot be rerun here. The absent
input is marked by `../../data/private/interview_transcripts.txt`.

## Positive and negative aspects

`fig_pros_cons.py` is the single source of truth for
`fig_number_pro_con_statements.pdf`. It asks the model to return two lists of
named aspect strings and computes the plotted counts locally with `len()`; the
model is never asked to count.

To run this private-data workflow:

1. Put the excluded participant-level file at
   `../../data/private/df_clean_with_llm_themes_pros_cons_v001.csv`, or set
   `PROS_CONS_INPUT_PATH` to its location.
2. Copy `.env.example` to `.env` and set `OPENAI_API_KEY`.
3. Run `fig_pros_cons.ipynb` or `python fig_pros_cons.py`.

The run checkpoints to `output/df_clean_with_llm_named_pros_cons_v002.csv`,
saves a one-row-per-aspect audit file and an arm-level summary in `output/`,
and writes the exhibit to `../../results/figures/`.

## Strategies for reducing social media use

`fig_strategies.py` is the single source of truth for `fig_strategies.pdf`.
It applies the prespecified 12-category strategy coding manual to the same
1,663 participant excerpts used by the original analysis. The model selects
zero or more named categories; Python computes treatment-arm shares and draws
the figure. The 1,663-row input excludes participants who quit before answering
one of the strategy-focused planning or wrap-up questions.

To run this private-data workflow:

1. Put the excluded participant-level file at
   `../../data/private/df_clean_with_llm_themes_strategies_v003.csv`, or set
   `STRATEGIES_INPUT_PATH` to its location.
2. Copy `.env.example` to `.env` and set `OPENAI_API_KEY`.
3. Run `python fig_strategies.py`.

The default run uses `gpt-5.6-luna` with low reasoning, checkpoints to
`output/df_clean_with_llm_strategies_luna_v004.csv`, saves a text-free
arm-by-category summary in `output/strategies_by_treatment_luna_v004.csv`, and
writes the exhibit to `../../results/figures/fig_strategies.pdf`.

`fig_strategies_by_treatment.ipynb` is retained as the legacy plotting notebook
for the earlier GPT-5-nano classifications.

All notebooks in this package have had stored outputs and execution counts
removed to prevent accidental disclosure of interview text.
