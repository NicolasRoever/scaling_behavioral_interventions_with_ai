from __future__ import annotations
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb, LinearSegmentedColormap
from wordcloud import WordCloud

def configuration():
    ARMS = ["T1_MI_CHANGE", "T2_MI_AMBIVALENCE", "T4_CLEAR_PERSUASION", "TIME_USE"]
    
    ARM_LABELS = {"T1_MI_CHANGE": "Change Talk", "T2_MI_AMBIVALENCE": "Decisional Balance",
                  "T4_CLEAR_PERSUASION": "Direct Persuasion", "TIME_USE": "Control (Time Use)"}
    
    ARM_COLORS = {"T1_MI_CHANGE": "#b83232", "T2_MI_AMBIVALENCE": "#777777",
                  "T4_CLEAR_PERSUASION": "#4c4c86", "TIME_USE": "#9b9b9b"}
    
    BACKGROUND = "#faf9f6"
    
    ORDERS = {
        1: {"label": "Single Words",           "min_count": 15, "max_words": 45, "horizontal": 0.90},
        2: {"label": "Two-Word Phrases", "min_count": 8,  "max_words": 30, "horizontal": 1.00},
    }
    return {'ARMS': ARMS, 'ARM_LABELS': ARM_LABELS, 'ARM_COLORS': ARM_COLORS, 'BACKGROUND': BACKGROUND, 'ORDERS': ORDERS}



def arm_cmap(hex_color, config):
    """Arm-colour ramp, so more distinctive (higher-z) words render darker."""
    ARMS, ARM_LABELS, ARM_COLORS, BACKGROUND, ORDERS = (config[k] for k in ['ARMS', 'ARM_LABELS', 'ARM_COLORS', 'BACKGROUND', 'ORDERS'])
    r, g, b = to_rgb(hex_color)
    pale = (0.55 + 0.45 * r, 0.55 + 0.45 * g, 0.55 + 0.45 * b)
    return LinearSegmentedColormap.from_list("arm", [pale, (r, g, b)])

def make_figure(keyness, out_path, config):
    """
    Draw outputs/wordclouds_by_arm.png: a grid of word clouds, one row per n-gram order (single
    words and two-word phrases) and one column per arm. Each word is sized by its
    weighted log-odds z-score (its distinctiveness for that arm versus the pooled other three); only
    over-represented terms (z > 0) appear.
    """
    ARMS, ARM_LABELS, ARM_COLORS, BACKGROUND, ORDERS = (config[k] for k in ['ARMS', 'ARM_LABELS', 'ARM_COLORS', 'BACKGROUND', 'ORDERS'])
    plt.rcParams.update({"font.family": "Arial", "font.size": 10})
    fig, axes = plt.subplots(len(ORDERS), len(ARMS), figsize=(19, 8))

    for row, (n, settings) in enumerate(ORDERS.items()):
        for col, arm in enumerate(ARMS):
            ax = axes[row][col]
            sub = keyness[(keyness["arm"] == arm) & (keyness["ngram"] == n) & (keyness["z"] > 0)]
            weights = dict(zip(sub["term"], sub["z"]))          # size each word by its z-score

            cloud = WordCloud(width=1000, height=720, background_color=BACKGROUND,
                              colormap=arm_cmap(ARM_COLORS[arm], config), max_words=settings["max_words"],
                              prefer_horizontal=settings["horizontal"], relative_scaling=0.5,
                              min_font_size=10, collocations=False, normalize_plurals=False,
                              random_state=0)
            cloud.generate_from_frequencies(weights)
            ax.imshow(cloud, interpolation="bilinear", aspect="auto")
            ax.axis("off")

            if row == 0:
                ax.set_title(ARM_LABELS[arm], fontsize=13, fontweight="bold",
                             color=ARM_COLORS[arm], pad=8)
            if col == 0:
                ax.text(-0.04, 0.5, settings["label"], transform=ax.transAxes, rotation=90,
                        va="center", ha="center", fontsize=12, fontweight="bold")

    # hspace opens a clear gap between the two n-gram rows (words / two-word phrases)
    fig.subplots_adjust(left=0.05, right=0.99, top=0.97, bottom=0.02, wspace=0.04, hspace=0.20)
    fig.savefig(out_path, bbox_inches="tight", facecolor=BACKGROUND)
    plt.close(fig)
