"""
Shared plotting style for the robustness-check figures, matching the house style
used in the paper's other figures (fig_miti_scores_main_study.py,
fig_miti_score_distributions_main_study.py, keyness_wordclouds.py): Arial font,
white background, muted/desaturated color families, top/right/left spines hidden.
"""

import matplotlib.pyplot as plt

FONT_FAMILY = "Arial"
FONT_SIZE = 10

TEXT_PRIMARY = "#222222"
TEXT_SECONDARY = "#555555"
TEXT_MUTED = "#777777"

# Muted palette, same families used elsewhere in the paper for treatment arms
# (dark red = Change Talk, navy = Ambivalence, dark green = Persuasion, gray = Control).
PROCEDURE_COLORS = {
    "Benchmark": "#333333",                # dark gray -- the reference/baseline run
    "All Runs Pooled": "#4c4c86",          # navy
    "Stochastic Reruns Only": "#b83232",   # dark red
    "Different Model Only": "#1b6b1b",     # dark green
    "Prompt Ablation Only": "#8a6d3b",     # muted ochre
}
MARKERS = {
    "Benchmark": "o",
    "All Runs Pooled": "s",
    "Stochastic Reruns Only": "D",
    "Different Model Only": "^",
    "Prompt Ablation Only": "v",
}


def apply_style():
    plt.rcParams.update({"font.family": FONT_FAMILY, "font.size": FONT_SIZE})


def strip_spines(ax, keep=("bottom",)):
    for spine in ["top", "right", "left", "bottom"]:
        ax.spines[spine].set_visible(spine in keep)
