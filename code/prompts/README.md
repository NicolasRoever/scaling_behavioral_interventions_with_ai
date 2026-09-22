# Interviewer and MITI scoring prompts

All prompt definitions in this directory can be inspected and imported without
an API key. The examples below only format text locally and make no model requests.

| File | Contents |
|---|---|
| [parameters.py](parameters.py) | Interviewer prompts for the four experimental arms |
| [miti_global_scores.py](miti_global_scores.py) | Full MITI 4.2.1 global scoring templates and all four coding rubrics |
| [miti_behavioral_counts.py](miti_behavioral_counts.py) | Behavioral coding instructions and the utterance-classification prompt |

## Global scores

`MITI_GUIDE` contains the rubrics for **Cultivating Change Talk**, **Softening
Sustain Talk**, **Partnership**, and **Empathy**. Each dimension is scored
separately using the full interview transcript.

- `MAIN_PROMPT` is the study template, with reducing social media time as the change goal.
- `VALIDATION_PROMPT` omits the study-specific Change Goal passage for the expert-scored training interviews, which concern different behaviors.
- Both templates include the conservative-scoring instruction. The ablation removes only that sentence; repeated runs and model comparisons use the same standard prompt text.

From the package root, render the four study prompts with Python's standard library:

```python
import sys
sys.path.insert(0, "code/prompts")
from miti_global_scores import MAIN_PROMPT, MITI_GUIDE, VALIDATION_PROMPT

transcript = "<insert the complete interview transcript here>"
template = MAIN_PROMPT  # Use VALIDATION_PROMPT for the human-validation design.
prompts = {
    dimension: template.format(
        component_name=dimension,
        coding_instructions=instructions,
        transcript=transcript,
    )
    for dimension, instructions in MITI_GUIDE.items()
}
print(prompts["Empathy"])
```

For the conservative-sentence ablation, replace `template` before formatting:

```python
conservative_sentence = "- If in doubt, assign the lower score if you are uncertain between two scores.\n"
assert template.count(conservative_sentence) == 1
ablated_template = template.replace(conservative_sentence, "")
```

The global prompts request a JSON object containing an integer `score` from 1
to 5 and a short `justification`. The standard and ablated study templates,
validation templates, and all four rubrics match the saved September 10 study
campaign and September 18 corrected validation inputs exactly. See
[MITI_REPLICATION.md](../../docs/MITI_REPLICATION.md) for models, settings, and the
saved results used in the paper.

## Behavioral counts

`MITI_MAIN_BEHAVIOR` contains the behavioral coding instructions, including
utterance segmentation. `MITI_BEHAVIOR_COUNTS_PROMPT` is the reusable classifier
prompt, with one `{text}` placeholder for an interviewer utterance:

```python
from miti_behavioral_counts import MITI_BEHAVIOR_COUNTS_PROMPT, MITI_MAIN_BEHAVIOR

utterance = "<insert an interviewer utterance here>"
prompt = MITI_BEHAVIOR_COUNTS_PROMPT.format(text=utterance)
print(prompt)
```

This is the separate behavioral-count procedure reported in Table C.1,
Panel B; it was not rerun in the corrected global-score validation exercise.
The prompt definitions preserve the source wording and output examples.

Only reusable templates and manual instructions are supplied here. Raw
interviews and prompts filled with participant transcripts are not distributed.
To reproduce the paper's exhibits from the released saved scores, use
`python code/python/run_public.py`; it does not call a model.
