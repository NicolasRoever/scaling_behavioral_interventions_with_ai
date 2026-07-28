"""
Build the robustness summary table for the handcoded validation set (14 sessions
with human CCT/SST/PAR/EMP scores, matching the paper's behavioral-counts N).

Reuses the metric definitions from robustness_analyze.py (score_metrics, icc_2_1):
  - "Direction changed" = sign(score - 3) differs between the two runs being compared.
  - "Threshold crossing" = (score >= 4) differs between the two runs being compared.
  - ICC is ICC(2,1), two-way random effects, absolute agreement, single rater.

Each of the three robustness conditions is reported against TWO references:
  - "(vs LLM baseline)": self-consistency vs. the original LLM run on this set
    (output/validation_miti_global_scores_20251125.csv, gpt-5-nano-2025-08-07),
    mirroring the full-corpus robustness table.
  - "(vs human)": agreement with the human-coded ground truth
    (output/validation_global_scores_extracted.csv), showing whether each condition
    changes how well the pipeline tracks real MITI coders.
The LLM baseline's own agreement with human is also reported as a reference row.
"""

import numpy as np
import pandas as pd

from robustness_analyze import icc_2_1, score_metrics  # reuse exact metric definitions

DIMENSIONS = [
    "Cultivating Change Talk",
    "Softening Sustain Talk",
    "Partnership",
    "Empathy",
]
DIMENSION_MAP = {
    "Cultivating Change Talk": "CCT",
    "Softening Sustain Talk": "SST",
    "Partnership": "PAR",
    "Empathy": "EMP",
}
LLM_BASELINE_PATH = "output/validation_miti_global_scores_20251125.csv"
HUMAN_PATH = "output/validation_global_scores_extracted.csv"
FOURTEEN_SESSION_PATH = "output/behavioral_counts_validation_2025-11-25.csv"
RERUN_PATHS = [f"output/robustness_handcoded_rerun{i}.csv" for i in range(1, 6)]
MODEL_SWAP_PATH = "output/robustness_handcoded_model_swap.csv"
ABLATION_PATH = "output/robustness_handcoded_ablation.csv"


def fourteen_session_ids():
    fourteen = pd.read_csv(FOURTEEN_SESSION_PATH, low_memory=False)
    return set(fourteen["source_pdf"].unique())


def load_condition_scores(path):
    df = pd.read_csv(path)
    df = df[df["error"].astype(str) == "0"]
    df = df[pd.to_numeric(df["score"], errors="coerce").between(1, 5)]
    df["score"] = df["score"].astype(float)
    return df[["source_pdf", "miti_dimension", "score"]]


def load_llm_baseline(session_ids):
    df = pd.read_csv(LLM_BASELINE_PATH)
    df["error"] = df["error"].astype(str)
    df = df[df["error"] == "0"]
    df = df[pd.to_numeric(df["score"], errors="coerce").between(1, 5)]
    df["score"] = df["score"].astype(float)
    df = df[df["source_pdf"].isin(session_ids)]
    return df[["source_pdf", "miti_dimension", "score"]]


def load_human(session_ids):
    df = pd.read_csv(HUMAN_PATH)
    df = df[df["source_pdf"].isin(session_ids)]
    melted = df.melt(
        id_vars="source_pdf", value_vars=["CCT", "SST", "PAR", "EMP"],
        var_name="dimension_short", value_name="score",
    )
    reverse_map = {v: k for k, v in DIMENSION_MAP.items()}
    melted["miti_dimension"] = melted["dimension_short"].map(reverse_map)
    return melted[["source_pdf", "miti_dimension", "score"]]


def rows_vs_reference(label, comparison_paths_or_dfs, reference, dims=DIMENSIONS, pooled=False, include_global=False):
    rows = []
    if pooled:
        pairs = []
        for path in comparison_paths_or_dfs:
            comp = load_condition_scores(path)
            merged = reference.merge(comp, on=["source_pdf", "miti_dimension"], suffixes=("_ref", "_cmp"))
            pairs.append(merged)
        merged = pd.concat(pairs, ignore_index=True) if pairs else pd.DataFrame()
    else:
        comp = load_condition_scores(comparison_paths_or_dfs) if isinstance(comparison_paths_or_dfs, str) else comparison_paths_or_dfs
        merged = reference.merge(comp, on=["source_pdf", "miti_dimension"], suffixes=("_ref", "_cmp"))

    if include_global and len(merged) > 0:
        # Pooled across all 4 dimensions in one go (not an average of per-dimension
        # bias/corr) -- same method as global_bias/global_corr in global_scores_analysis.ipynb.
        row = {"Analysis": label, "MITI outcome": "Global", "Outcome type": "Global, 1–5"}
        row.update(score_metrics(merged["score_ref"], merged["score_cmp"]))
        rows.append(row)

    for dim in dims:
        sub = merged[merged["miti_dimension"] == dim]
        if len(sub) == 0:
            continue
        row = {"Analysis": label, "MITI outcome": dim, "Outcome type": "Global, 1–5"}
        row.update(score_metrics(sub["score_ref"], sub["score_cmp"]))
        rows.append(row)
    return rows


def main():
    session_ids = fourteen_session_ids()
    llm_baseline = load_llm_baseline(session_ids)
    human = load_human(session_ids)

    rows = []

    # Reference: how well does the original LLM baseline itself agree with human?
    # (reference=human, comparison=llm_baseline, so "Mean difference" = LLM - human,
    # consistent with the sign convention used by every other "(vs human)" row below)
    rows += rows_vs_reference("LLM baseline (vs human)", llm_baseline, human, include_global=True)

    # Self-consistency: each condition vs. the LLM baseline
    rows += rows_vs_reference("Stochastic reruns (vs LLM baseline)", RERUN_PATHS, llm_baseline, pooled=True)
    rows += rows_vs_reference("Different model (vs LLM baseline)", MODEL_SWAP_PATH, llm_baseline)
    rows += rows_vs_reference("Prompt ablation (vs LLM baseline)", ABLATION_PATH, llm_baseline)

    # Human agreement: each condition vs. human ground truth
    rows += rows_vs_reference("Stochastic reruns (vs human)", RERUN_PATHS, human, pooled=True, include_global=True)
    rows += rows_vs_reference("Different model (vs human)", MODEL_SWAP_PATH, human, include_global=True)
    rows += rows_vs_reference("Prompt ablation (vs human)", ABLATION_PATH, human, include_global=True)

    columns = [
        "Analysis", "MITI outcome", "Outcome type", "N", "Original mean", "Comparison mean",
        "Mean difference", "MAE", "Correlation", "Absolute-agreement ICC", "Exact agreement",
        "Agreement within ±1", "Direction changed", "Threshold crossing",
    ]
    table = pd.DataFrame(rows)[columns]
    table.to_csv("output/robustness_summary_table_handcoded.csv", index=False)
    with open("output/robustness_summary_table_handcoded.md", "w") as f:
        f.write(table.to_markdown(index=False))
    print(table.to_markdown(index=False))


if __name__ == "__main__":
    main()
