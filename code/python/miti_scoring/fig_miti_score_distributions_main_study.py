
# package
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = Path(__file__).parent / "output"

# LLM-based MITI 4.2.1 scores for individual interviews
scores_treated = pd.read_csv(OUTPUT_DIR / "w2_miti_global_scores_20251222_v003.csv")
scores_control = pd.read_csv(OUTPUT_DIR / "w2_miti_global_scores_control_20260703.csv")
scores = pd.concat([scores_treated, scores_control], ignore_index=True)
scores = scores[scores["error"].astype(str) == "0"]

# Cleaned survey data for getting treatment assignment
survey = pd.read_stata(PACKAGE_ROOT / "data/processed/main_social_media/clean_data.dta", convert_categoricals=False)

# Merge data
scores["user_id_raw"] = scores["session_id"].str[11:].astype(int)
data = survey[["user_id_raw", "T"]].merge(scores, on=["user_id_raw"], how="left")
data = data[data["T"].isin([0, 1, 2, 3])]

miti_dimensions = ['Cultivating Change Talk', 'Softening Sustain Talk', 'Partnership', 'Empathy']
treatment_groups = {0: "Control", 1: "Change Talk", 2: "Ambivalence", 3: "Persuasion"}
# Same arm colors as the wordclouds (text_analysis/keyness_wordclouds.py ARM_COLORS).
colors = {0: "#c4c4c4", 1: "#b83232", 2: "#777777", 3: "#4c4c86"}

plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 11

score_levels = [1, 2, 3, 4, 5]
n_groups = len(treatment_groups)
bar_w = 0.8 / n_groups

fig, axes = plt.subplots(2, 2, figsize=(11, 8), constrained_layout=True)

for ax, dimension in zip(axes.flat, miti_dimensions):
    dim_data = data[data["miti_dimension"] == dimension]
    x = np.arange(len(score_levels))

    for i, (T, label) in enumerate(treatment_groups.items()):
        group_scores = dim_data[dim_data["T"] == T]["score"]
        counts = group_scores.value_counts(normalize=True).reindex(score_levels, fill_value=0) * 100
        offset = (i - (n_groups - 1) / 2) * bar_w
        ax.bar(
            x + offset, counts.to_numpy(), width=bar_w,
            color=colors[T], edgecolor=colors[T], label=label,
        )

    ax.set_title(f"Dimension: {dimension}", fontsize=11, weight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(score_levels)
    ax.set_xlabel("MITI-Score")
    ax.set_ylabel("Percent")

    text_lines = []
    for T, label in treatment_groups.items():
        mean_score = dim_data[dim_data["T"] == T]["score"].mean()
        text_lines.append((f"{label} Mean: {mean_score:.2f}", colors[T]))

    for j, (line, color) in enumerate(text_lines):
        ax.text(
            0.03, 0.92 - j * 0.07, line, transform=ax.transAxes,
            color=color, fontweight="bold", fontsize=9, va="top",
            bbox=dict(facecolor="white", edgecolor="none", alpha=0.75, pad=1.5),
        )

    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

handles, labels = axes.flat[0].get_legend_handles_labels()
fig.legend(handles, labels, loc="upper center", ncol=n_groups, bbox_to_anchor=(0.5, 1.06), frameon=True)

fig.savefig(PACKAGE_ROOT / "results/figures/fig_miti_score_distributions_main_study.pdf", bbox_inches="tight")
