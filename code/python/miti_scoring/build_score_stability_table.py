"""
Full-corpus "how much does the average score move around" table.

For each of the 5 global metrics (Global pooled + the 4 MITI dimensions) and each
of 5 scoring procedures, pool the relevant score observations and report the mean
plus the empirical [2.5th, 97.5th] percentile interval of the pooled score
distribution (NOT a CI of the mean -- an empirical interval of individual scores,
per discussion). This avoids the pseudo-replication problem of treating repeated
runs of the same session as independent draws for a CI-of-the-mean calculation.

Procedures:
  - Benchmark: the original scoring run only.
  - All runs pooled: benchmark + 5 reruns + model swap + ablation, all stacked.
  - Stochastic reruns only: the 5 reruns only (excludes benchmark).
  - Different model only: the model-swap run only.
  - Prompt ablation only: the ablation run only.

Full-corpus data (2195 treated sessions x 4 dimensions), same files used in
robustness_analyze.py.
"""

import numpy as np
import pandas as pd

DIMENSIONS = [
    "Cultivating Change Talk",
    "Softening Sustain Talk",
    "Partnership",
    "Empathy",
]
ROW_ORDER = ["Global", "Partnership", "Cultivating Change Talk", "Empathy", "Softening Sustain Talk"]

ORIGINAL_PATH = "output/w2_miti_global_scores_20251222_v003.csv"
RERUN_PATHS = [f"output/robustness_rerun{i}.csv" for i in range(1, 6)]
MODEL_SWAP_PATH = "output/robustness_model_swap.csv"
ABLATION_PATH = "output/robustness_ablation.csv"

OUT_CSV = "output/score_stability_table.csv"
OUT_TEX = "output/score_stability_latex_table.tex"

PROCEDURES = ["Benchmark", "All Runs Pooled", "Stochastic Reruns Only", "Different Model Only", "Prompt Ablation Only"]


def load_scores(path):
    df = pd.read_csv(path)
    df = df[df["error"].astype(str) == "0"]
    df = df[pd.to_numeric(df["score"], errors="coerce").between(1, 5)]
    df["score"] = df["score"].astype(float)
    return df[["session_id", "miti_dimension", "score"]]


def build_procedure_frames():
    benchmark = load_scores(ORIGINAL_PATH)
    reruns = pd.concat([load_scores(p) for p in RERUN_PATHS], ignore_index=True)
    model_swap = load_scores(MODEL_SWAP_PATH)
    ablation = load_scores(ABLATION_PATH)
    all_pooled = pd.concat([benchmark, reruns, model_swap, ablation], ignore_index=True)

    return {
        "Benchmark": benchmark,
        "All Runs Pooled": all_pooled,
        "Stochastic Reruns Only": reruns,
        "Different Model Only": model_swap,
        "Prompt Ablation Only": ablation,
    }


def summarize(scores):
    scores = np.asarray(scores, dtype=float)
    return {
        "N": len(scores),
        "Mean": round(scores.mean(), 3),
        "q2.5": round(np.percentile(scores, 2.5), 2),
        "q97.5": round(np.percentile(scores, 97.5), 2),
    }


def build_long_table():
    frames = build_procedure_frames()
    rows = []
    for proc, df in frames.items():
        # Global: pool across all 4 dimensions
        row = {"MITI outcome": "Global", "Procedure": proc}
        row.update(summarize(df["score"]))
        rows.append(row)
        for dim in DIMENSIONS:
            sub = df[df["miti_dimension"] == dim]
            row = {"MITI outcome": dim, "Procedure": proc}
            row.update(summarize(sub["score"]))
            rows.append(row)
    return pd.DataFrame(rows)[["MITI outcome", "Procedure", "N", "Mean", "q2.5", "q97.5"]]


def cell_str(row):
    return f"{row['Mean']:.2f} [{row['q2.5']:.1f}, {row['q97.5']:.1f}]"


def make_latex_table(long_df, out_path=OUT_TEX):
    col_spec = "p{4cm} " + " ".join(["c"] * len(PROCEDURES))
    lines = []
    lines.append(rf"\begin{{tabular}}{{{col_spec}}}")
    lines.append(r"\toprule")
    header = [r"\textbf{Score Category}"] + [rf"\textbf{{{p}}}" for p in PROCEDURES]
    lines.append(" & ".join(header) + r" \\")
    lines.append(r"\midrule")
    for dim in ROW_ORDER:
        cells = [dim]
        for proc in PROCEDURES:
            sub = long_df[(long_df["MITI outcome"] == dim) & (long_df["Procedure"] == proc)]
            cells.append(cell_str(sub.iloc[0]) if len(sub) else "")
        lines.append(" & ".join(cells) + r" \\")
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    with open(out_path, "w") as f:
        f.write("\n".join(lines))
    print(f"LaTeX table saved to {out_path}")


def main():
    long_df = build_long_table()
    long_df.to_csv(OUT_CSV, index=False)
    print(long_df.to_string(index=False))
    make_latex_table(long_df)


if __name__ == "__main__":
    main()
