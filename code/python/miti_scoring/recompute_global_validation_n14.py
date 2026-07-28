"""
Recompute the "Global Metrics" panel of the human-vs-LLM validation table
(output/validation_global_scores_results.csv -> tables/mi_validation_results_table.tex)
restricted to the same 14-session subset used everywhere else (the paper's
behavioral-counts N, output/behavioral_counts_validation_2025-11-25.csv).

Previously this panel was computed on the full 20-session
validation_global_scores_extracted.csv, even though the table's own footnote
already claimed N=14 -- this script makes the underlying numbers match the
footnote.

Bias = LLM - human (same convention as global_scores_analysis.ipynb and
robustness_analyze_handcoded.py). Global row pools all 4 dimensions before
computing bias/correlation (not an average of the per-dimension values).

Panel B (behavioral counts) is untouched -- it already uses the 14-session set.
"""

from pathlib import Path

import pandas as pd

from robustness_analyze_handcoded import DIMENSIONS, fourteen_session_ids, load_human, load_llm_baseline

RESULTS_PATH = "output/validation_global_scores_results.csv"
PACKAGE_ROOT = Path(__file__).resolve().parents[3]
TEX_PATH = PACKAGE_ROOT / "results/tables/mi_validation_results_table.tex"
BEHAVIORAL_RESULTS_PATH = "output/behavioral_scores_validation_results.csv"

ROW_ORDER = ["Global", "Partnership", "Cultivating Change Talk", "Empathy", "Softening Sustain Talk"]
BEHAVIORAL_ROW_ORDER = [
    "Share Complex Reflections",
    "Reflection-to-Question Ratio",
    "Total MI-Adherent Behavior",
    "Total MI Non-Adherent Behavior",
    "Reflection Correlation",
]


def compute_global_metrics_n14():
    session_ids = fourteen_session_ids()
    llm = load_llm_baseline(session_ids)
    human = load_human(session_ids)
    merged = llm.merge(human, on=["source_pdf", "miti_dimension"], suffixes=("_llm", "_human"))

    rows = []
    rows.append({
        "Dimension": "Global",
        "Bias": (merged["score_llm"] - merged["score_human"]).mean(),
        "Correlation": merged["score_llm"].corr(merged["score_human"]),
    })
    for dim in DIMENSIONS:
        sub = merged[merged["miti_dimension"] == dim]
        rows.append({
            "Dimension": dim,
            "Bias": (sub["score_llm"] - sub["score_human"]).mean(),
            "Correlation": sub["score_llm"].corr(sub["score_human"]),
        })
    df = pd.DataFrame(rows)
    return df.set_index("Dimension").loc[ROW_ORDER].reset_index()


def row_to_latex(name, bias, corr):
    corr_str = "" if pd.isna(corr) else f"{corr:.2f}"
    bias_str = "" if pd.isna(bias) else f"{bias:.2f}"
    return f"{name} & {bias_str} & {corr_str} \\\\"


def make_latex_table(df_global, df_behavioral, out_path=TEX_PATH):
    lines = []
    lines.append(r"\begin{tabular}{p{10cm} c c}")
    lines.append(r"\toprule")
    lines.append(r"\textbf{Score Category} & \textbf{Bias} & \textbf{Correlation} \\")
    lines.append(r"\midrule")

    lines.append(r"\textit{A. Global Metrics} \\")
    for _, row in df_global.iterrows():
        lines.append(row_to_latex(row["Dimension"], row["Bias"], row["Correlation"]))

    lines.append(r"\addlinespace")
    lines.append(r"\textit{B. Behavioral Counts} \\")
    for _, row in df_behavioral.iterrows():
        lines.append(row_to_latex(row["Category"], row["Bias"], row["Correlation"]))

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")

    with open(out_path, "w") as f:
        f.write("\n".join(lines))
    print(f"LaTeX table saved to {out_path}")


def main():
    df_global = compute_global_metrics_n14()
    df_global.to_csv(RESULTS_PATH, index=False)
    print(df_global)

    df_behavioral = pd.read_csv(BEHAVIORAL_RESULTS_PATH)
    df_behavioral = df_behavioral.set_index("Category").loc[BEHAVIORAL_ROW_ORDER].reset_index()
    make_latex_table(df_global, df_behavioral)


if __name__ == "__main__":
    main()
