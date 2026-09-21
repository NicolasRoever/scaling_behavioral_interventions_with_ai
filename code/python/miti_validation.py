"""Offline corrected MITI validation from deidentified saved numeric scores."""
import hashlib
import json
from pathlib import Path
import pandas as pd
from miti_tables import comparison_rows, fmt_number, latex_table

def validation_conditions(luna_model, gpt54_model, gpt55_model, luna_reasoning):
    conditions = [dict(id="luna_benchmark", condition="benchmark", replicate=0,
                       model=luna_model, reasoning_effort=luna_reasoning, ablation=False)]
    conditions += [dict(id=f"luna_rerun_{replicate:02d}", condition="rerun", replicate=replicate,
                        model=luna_model, reasoning_effort=luna_reasoning, ablation=False)
                   for replicate in range(1, 6)]
    conditions += [dict(id="luna_ablation", condition="ablation", replicate=0,
                        model=luna_model, reasoning_effort=luna_reasoning, ablation=True)]
    conditions += [dict(id=name, condition="model_comparison", replicate=0,
                        model=model, reasoning_effort="none", ablation=False)
                   for name, model in [("gpt54_minimum", gpt54_model), ("gpt55_minimum", gpt55_model)]]
    return conditions

def summaries(scores, human, dimensions):
    groups = [("Benchmark", scores[scores.condition.eq("benchmark")]),
              ("Stochastic reruns", scores[scores.condition.eq("rerun")]),
              ("Prompt ablation", scores[scores.condition.eq("ablation")])]
    # Preserve the manuscript's ordering of the two model-comparison sections.
    for model in sorted(scores.loc[scores.condition.eq("model_comparison"), "model"].unique(), reverse=True):
        groups.append(("Different model: " + model, scores[scores.model.eq(model)]))
    rows = []
    per_run = []
    for label, frame in groups:
        rows.extend(comparison_rows(human, frame, label, "Human", dimensions, lambda ref, cmp: {}))
        for run_id, run in frame.groupby("run_id", sort=False):
            values = comparison_rows(human, run, label, "Human", dimensions, lambda ref, cmp: {})
            for row in values:
                row.update(condition_id=run_id, replicate=int(run.replicate.iloc[0]),
                           model=run.model.iloc[0], reasoning_effort=run.reasoning_effort.iloc[0])
            per_run.extend(values)
    return pd.DataFrame(rows), pd.DataFrame(per_run)

def write_tables(summary, behavioral, output):
    baseline = summary[summary.Analysis.eq("Benchmark")]
    global_rows = baseline.rename(columns={"MITI outcome": "Score category", "Mean difference": "Bias"})[
        ["Score category", "Bias", "Correlation"]].assign(Panel="A")
    behavioral_rows = behavioral.rename(columns={"Category": "Score category"}).assign(Panel="B")
    c1 = pd.concat([global_rows, behavioral_rows], ignore_index=True)[["Panel", "Score category", "Bias", "Correlation"]]
    c1.to_csv(output / "table_c1.csv", index=False)
    c1_rows = []
    for label, panel in [("A. Global metrics (Luna)", "A"), ("B. Behavioral counts (existing results)", "B")]:
        c1_rows.append([label, "", ""])
        for _, row in c1[c1.Panel.eq(panel)].iterrows():
            # The historical reflection-correlation row has no bias statistic.
            bias = "" if panel == "B" and pd.isna(row.Bias) else fmt_number(row.Bias)
            c1_rows.append([row["Score category"], bias, fmt_number(row.Correlation)])
    latex_table(["Score category", "Bias", "Correlation"], c1_rows,
                output / "mi_validation_results_table.tex", "p{10cm}rr",
                section_headings=True, letter_sections=False)
    summary.to_csv(output / "table_c2.csv", index=False)
    c2_rows = []
    for label, group in summary.groupby("Analysis", sort=False):
        c2_rows.append([label, "", "", ""])
        for _, row in group.iterrows():
            c2_rows.append([row["MITI outcome"], str(row["Unique sessions"]),
                            fmt_number(row["Mean difference"]), fmt_number(row.Correlation)])
    latex_table(["Procedure / score", "Sessions", "Bias", "Correlation"], c2_rows,
                output / "robustness_handcoded_latex_table.tex", "p{9cm}rrr", section_headings=True)


def validate_scores(scores, conditions, dimensions):
    """Require the complete paired design and consistent expert ratings."""
    columns = ['session_id', 'condition_id', 'condition', 'replicate', 'model',
               'reasoning_effort', 'prompt_variant', 'miti_dimension', 'score', 'human_score']
    if list(scores.columns) != columns or len(scores) != 504:
        raise ValueError('Expected 504 text-free validation scores and the documented columns')
    ids = set(scores.session_id)
    if ids != {f'VALIDATION-{i:04d}' for i in range(1, 15)}:
        raise ValueError('Expected the 14 anonymous validation interviews')
    keys = ['condition_id', 'session_id', 'miti_dimension']
    expected = {(condition['id'], session, dimension) for condition in conditions
                for session in ids for dimension in dimensions}
    if scores.duplicated(keys).any() or set(scores[keys].itertuples(index=False, name=None)) != expected:
        raise ValueError('Missing, duplicate or unexpected validation score keys')
    if not scores[['score', 'human_score']].isin([1, 2, 3, 4, 5]).all().all():
        raise ValueError('Validation scores must be integers from 1 to 5')
    for condition in conditions:
        frame = scores[scores.condition_id.eq(condition['id'])]
        for key in ['condition', 'replicate', 'model', 'reasoning_effort']:
            if not frame[key].eq(condition[key]).all():
                raise ValueError('Validation condition metadata mismatch: ' + key)
        variant = 'ablation' if condition['ablation'] else 'standard'
        if not frame.prompt_variant.eq(variant).all():
            raise ValueError('Validation prompt variant mismatch')
    human_keys = ['session_id', 'miti_dimension']
    if not scores.groupby(human_keys).human_score.nunique().eq(1).all():
        raise ValueError('Expert ratings differ between scoring conditions')
    human = scores[human_keys + ['human_score']].drop_duplicates().rename(columns={'human_score': 'score'})
    return scores.assign(run_id=scores.condition_id), human


def load_inputs(package):
    folder = package / 'data/derived/miti_validation_20260918'
    manifest = json.loads((folder / 'manifest.json').read_text())
    conditions = validation_conditions('gpt-5.6-luna', 'gpt-5.4-2026-03-05', 'gpt-5.5-2026-04-23', 'low')
    dimensions = ['Cultivating Change Talk', 'Softening Sustain Talk', 'Partnership', 'Empathy']
    if (manifest['conditions'] != conditions or manifest['dimensions'] != dimensions or
            manifest['expected_scores'] != 504 or manifest['expected_interviews'] != 14 or
            manifest['file'] != 'scores.csv' or
            manifest['behavioral_reference'] != 'data/derived/miti/inputs/behavioral_results.csv'):
        raise ValueError('Unexpected corrected MITI validation design')
    path = folder / manifest['file']
    if hashlib.sha256(path.read_bytes()).hexdigest() != manifest['sha256']:
        raise ValueError('Corrected MITI scores changed')
    scores, human = validate_scores(pd.read_csv(path), conditions, dimensions)
    path = package / manifest['behavioral_reference']
    if hashlib.sha256(path.read_bytes()).hexdigest() != manifest['behavioral_reference_sha256']:
        raise ValueError('Preserved behavioral-count reference changed')
    behavioral = pd.read_csv(path)
    categories = ['Share Complex Reflections', 'Reflection-to-Question Ratio',
                  'Total MI-Adherent Behavior', 'Total MI Non-Adherent Behavior', 'Reflection Correlation']
    if (list(behavioral.columns) != ['Category', 'Bias', 'Correlation'] or
            behavioral.Category.duplicated().any() or set(behavioral.Category) != set(categories)):
        raise ValueError('Unexpected behavioral-count reference structure')
    return scores, human, dimensions, behavioral.set_index('Category').loc[categories].reset_index()


def build_validation(package, output):
    scores, human, dimensions, behavioral = load_inputs(package)
    summary, per_run = summaries(scores, human, dimensions)
    write_tables(summary, behavioral, output)
    per_run.to_csv(output / 'summary_per_run.csv', index=False)
