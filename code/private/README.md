# Restricted-input method sources

Reusable MITI prompts are directly available in
[`code/prompts/miti_global_scores.py`](../prompts/miti_global_scores.py) and
[`code/prompts/miti_behavioral_counts.py`](../prompts/miti_behavioral_counts.py);
see the [prompt usage guide](../prompts/README.md). These modules contain only
prompt definitions and can be imported without restricted data or API access.
The matching files here retain the execution guard and point to those shared definitions.

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
| Similarity and word clouds | Original `chats_raw.csv` and original survey arm mapping (`main_raw.sav`) |
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

The updated question-sequence figure is public and manual: see
`../python/question_sequence.py`. Its former transcript-based classifier and
sequence input are no longer part of this release.

The September 18 MITI methods are in `miti_scoring/miti_benmchmarking/`:
`validation_transcripts.py` documents P/I as clinician and C as client, and
content-checked continuation/correction handling. `prepare_validation_batch.py`
defines the topic-neutral prompt design. `run_validation_batch.py` records the
request/response workflow; `build_benchmark_tables.py` records the original
saved-response joining and table calculations. All remain disabled reference
sources. The raw transcripts, correction records, batch payloads, response
JSONLs and human-reference source files required by those methods are withheld.
The supported public entry point is `code/python/run_public.py`, using the
anonymous saved numeric scores. See [docs/MITI_REPLICATION.md](../../docs/MITI_REPLICATION.md).

The similarity method now imports question definitions and plotting from the
shared public modules. Its execution guard remains in place. The updated source
excludes unclassified raw question identifiers from TF-IDF and corrects
self-pair removal for zero vectors. Aggregate results and the exclusion audit
are supplied; reproducing extraction still requires the restricted transcripts
and survey arm mapping.
