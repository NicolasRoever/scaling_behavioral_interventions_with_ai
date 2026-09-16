# Restricted-input method sources

These files document the upstream methods that produced the saved public
measurements. They are not called by either public runner. Re-executing them
requires the original restricted inputs, source dependencies and path
configuration; the original project-relative paths in these method sources
describe that private project layout. Public users should run
`../python/run_public.py` instead.

| Workflow | Required private inputs |
|---|---|
| BERTopic fitting/labeling and seed diagnostics | `data/raw/main_socialmedia/chats_raw.csv` with `session_id`, `type`, `content`, `question_name`, `order`; cleaned survey treatment assignments |
| Pros/cons extraction | `df_clean_with_llm_themes_pros_cons_v001.csv`, including participant `full_content` |
| Strategy classification | `df_clean_with_llm_themes_strategies_v003.csv`, including participant `full_content` |
| Question sequencing, similarity, word clouds | Original `chats_raw.csv` and original survey arm mapping (`main_raw.sav`) |
| Thirty-minute lexical mentions | Original `chats_raw.csv` and `clean_data.dta` |
| MITI global scoring | Full private campaign inputs, including transcript sessions, rendered prompts and human-validation source material |
| Behavioral-count validation | Original annotated training utterances and saved model utterance classifications |
| Screenshot extraction/adjudication | Raw screenshot images and the private invalid-image register |
| Chat cleaning | Raw `chats_raw.csv` |

The Python source files intentionally raise an explanatory error before any
execution. This prevents accidental API requests and private-output creation.
The project's OpenAI API budget is $0; enabling paid calls is not part of the
replication workflow. The `.do` files are method references and likewise lack
their restricted inputs.

Source methods may describe intermediates that contain text; none are
distributed. Public figures start from numeric/categorical saved inputs in
`data/derived`. Only the code paths relevant to the manuscript's pipelines are
included; unrelated exploratory scripts are omitted.
