
# package
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
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

# Miti dimensions
miti_dimensions = ['Cultivating Change Talk', 'Softening Sustain Talk', 'Partnership', 'Empathy']
treatment_groups = {0: "Control", 1: "Change Talk", 2: "Ambivalence", 3: "Persuasion"}

means_t0 = data[data["T"] == 0].groupby(["miti_dimension"])["score"].mean()
means_t1 = data[data["T"] == 1].groupby(["miti_dimension"])["score"].mean()
means_t2 = data[data["T"] == 2].groupby(["miti_dimension"])["score"].mean()
means_t3 = data[data["T"] == 3].groupby(["miti_dimension"])["score"].mean()


plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 12

# Ensure identical ordering
miti_dims = means_t1.index.tolist()
m0 = means_t0.loc[miti_dims].to_numpy()
m1 = means_t1.loc[miti_dims].to_numpy()
m2 = means_t2.loc[miti_dims].to_numpy()
m3 = means_t3.loc[miti_dims].to_numpy()

# One panel: grouped horizontal bars (Control vs Change vs Ambivalence vs Persuasion within each dimension)
fig, ax = plt.subplots(figsize=(8, 4.5), constrained_layout=True)
bar_h = 0.2
y = np.arange(len(miti_dims))

# Stack Control on top, then Change, then Ambivalence, then Persuasion
y_control = y - 1.5 * bar_h
y_change = y - 0.5 * bar_h
y_ambiv  = y + 0.5 * bar_h
y_persuasion = y + 1.5 * bar_h

colors = ["#555555", "#a70000", "#000053", "#1b6b1b"]  # Control, Change, Ambivalence, Persuasion
fillcolors = ["#8a8a8a", "#b83232", "#4c4c86", "#4c8a4c"]
ax.barh(
    y_control, m0, height=bar_h,
    color=fillcolors[0],
    edgecolor=colors[0],       # same color family for border
    linewidth=1.5,             # control border width
    label="Control",
)

ax.barh(
    y_change, m1, height=bar_h,
    color=fillcolors[1],
    edgecolor=colors[1],       # same color family for border
    linewidth=1.5,             # control border width
    label="Change Talk",
)

ax.barh(
    y_ambiv, m2, height=bar_h,
    color=fillcolors[2],
    edgecolor=colors[2],
    linewidth=1.5,             # control border width
    label="Ambivalence",
)

ax.barh(
    y_persuasion, m3, height=bar_h,
    color=fillcolors[3],
    edgecolor=colors[3],
    linewidth=1.5,             # control border width
    label="Persuasion",
)

ax.set_xlim(-0.1, 5.1)
ax.set_yticks(y,)
ax.set_yticklabels(miti_dims)
ax.set_xlabel("Average LLM-assigned score", fontsize=12)
# ax.set_title("Average MITI scores by treatment", weight="bold")
# ax.legend(frameon=True)
# Modify the legend to be outside the plot area
ax.legend(frameon=True, loc='upper center', bbox_to_anchor=(1, 0.6), ncol=1)

for spine in ax.spines.values():
    spine.set_visible(False)

# Value labels inside bars (white)
for yi, v in zip(y_control, m0):
    ax.text(0.2, yi, f"{v:.2f}", color="white", va="center", fontweight="bold")
for yi, v in zip(y_change, m1):
    ax.text(0.2, yi, f"{v:.2f}", color="white", va="center", fontweight="bold")
for yi, v in zip(y_ambiv, m2):
    ax.text(0.2, yi, f"{v:.2f}", color="white", va="center", fontweight="bold")
for yi, v in zip(y_persuasion, m3):
    ax.text(0.2, yi, f"{v:.2f}", color="white", va="center", fontweight="bold")

fig.savefig(PACKAGE_ROOT / "results/figures/fig_miti_scores_main_study.pdf")

# Mean global MITI score (pooled across the four global dimensions), by treatment arm
global_miti_means = (
    data[data["miti_dimension"].isin(miti_dimensions)]
    .groupby("T")["score"]
    .mean()
    .reindex(treatment_groups)
)

print("\nMean global MITI score by treatment arm:")
for treatment_id, treatment_name in treatment_groups.items():
    print(f"{treatment_name}: {global_miti_means.loc[treatment_id]:.3f}")
