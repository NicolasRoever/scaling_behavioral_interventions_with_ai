"""
Build a LaTeX table comparing each robustness condition's agreement with human
ground truth on the handcoded validation set (N=14 sessions), one Bias/Correlation
column-pair per LLM scoring approach: Benchmark | Stochastic Reruns | Different
Model | Prompt Ablation.

Source: output/robustness_summary_table_handcoded.csv (the four "... (vs human)"
rows, produced by robustness_analyze_handcoded.py). Style follows the existing
mi_validation_results_table.tex built in create_latex_table.ipynb (booktabs,
2-decimal rounding, blank cell for missing values).
"""

import pandas as pd

SUMMARY_PATH = "output/robustness_summary_table_handcoded.csv"
OUT_PATH = "output/robustness_handcoded_latex_table.tex"

ROW_ORDER = ["Global", "Partnership", "Cultivating Change Talk", "Empathy", "Softening Sustain Talk"]

APPROACHES = [
    ("LLM baseline (vs human)", "Benchmark"),
    ("Stochastic reruns (vs human)", "Stochastic Reruns"),
    ("Different model (vs human)", "Different Model"),
    ("Prompt ablation (vs human)", "Prompt Ablation"),
]


def fmt(x):
    return "" if pd.isna(x) else f"{x:.2f}"


def make_latex_table(summary, out_path=OUT_PATH):
    n_groups = len(APPROACHES)
    col_spec = "p{4cm} " + " ".join(["cc"] * n_groups)

    lines = []
    lines.append(rf"\begin{{tabular}}{{{col_spec}}}")
    lines.append(r"\toprule")

    header_top = [""]
    for i, (_, label) in enumerate(APPROACHES):
        header_top.append(rf"\multicolumn{{2}}{{c}}{{\textbf{{{label}}}}}")
    lines.append(" & ".join(header_top) + r" \\")

    cmidrules = []
    for i in range(n_groups):
        start = 2 + 2 * i
        end = start + 1
        cmidrules.append(rf"\cmidrule(lr){{{start}-{end}}}")
    lines.append(" ".join(cmidrules))

    header_bottom = [r"\textbf{Score Category}"]
    for _ in APPROACHES:
        header_bottom += [r"\textbf{Bias}", r"\textbf{Correlation}"]
    lines.append(" & ".join(header_bottom) + r" \\")
    lines.append(r"\midrule")

    for dim in ROW_ORDER:
        cells = [dim]
        for analysis_label, _ in APPROACHES:
            sub = summary[(summary["Analysis"] == analysis_label) & (summary["MITI outcome"] == dim)]
            if len(sub) == 0:
                cells += ["", ""]
            else:
                cells += [fmt(sub["Mean difference"].iloc[0]), fmt(sub["Correlation"].iloc[0])]
        lines.append(" & ".join(cells) + r" \\")

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")

    with open(out_path, "w") as f:
        f.write("\n".join(lines))
    print(f"LaTeX table saved to {out_path}")
    return "\n".join(lines)


def main():
    summary = pd.read_csv(SUMMARY_PATH)
    tex = make_latex_table(summary)
    print(tex)


if __name__ == "__main__":
    main()
