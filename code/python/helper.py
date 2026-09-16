from __future__ import annotations
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def paper_topic_merge_specs():
    """Return the manual topic merges used in the main-text figure."""
    return [
        (12, [12, 16, 27, 14], "Confirmatory Statement"),
        (3, [3, 8], "Confidence in Changing Social Media Use"),
    ]

def paper_unstable_topic_labels(stability_summary: pd.DataFrame) -> frozenset[str]:
    """Return unstable displayed-topic labels from the stability summary."""
    required_columns = {"topic_label", "stable"}
    missing_columns = required_columns - set(stability_summary.columns)
    if missing_columns:
        raise ValueError(
            "Topic-stability summary is missing columns: "
            + ", ".join(sorted(missing_columns))
        )
    stable = stability_summary["stable"]
    if stable.dtype != bool:
        stable = stable.astype(str).str.lower().map({"true": True, "false": False})
    if stable.isna().any():
        raise ValueError("Topic-stability summary contains invalid stable values")
    return frozenset(stability_summary.loc[~stable, "topic_label"])

def apply_paper_topic_merges(df: pd.DataFrame) -> pd.DataFrame:
    """Return topic data with the manual merges used in the main-text figure."""
    merged = df.copy()
    for new_id, old_ids, new_label in paper_topic_merge_specs():
        mask = merged["topic_id"].isin(old_ids)
        merged.loc[mask, "topic_id"] = new_id
        merged.loc[mask, "topic_label"] = new_label
    return merged

def set_plot_theme():
    # base seaborn theme & palette
    sns.set_theme(
        style="white",  # consistent with file_context_0        # or your own list of colors
        font="Arial",  # consistent with file_context_0
        font_scale=1.3,  # Increased font scale for larger text
    )

    palette = ["#800000", "#1a476f", "#bdbdbd", "#5f8f8b", "#f39b7f"]
    sns.set_palette(palette=palette, n_colors=5)

    # tweak matplotlib rcParams you care about
    plt.rcParams.update(
        {
            "text.usetex": False,  # consistent with file_context_0
            #"axes.titlesize": 18,  # Increased title size
            #"axes.labelsize": 16,  # Increased label size
            "legend.frameon": False,
            "figure.figsize": (8, 5),
            "lines.linewidth": 2,
            "lines.markersize": 6,
            "axes.grid": False,  # Disable grid
            # …any other defaults…
        }
    )

def finalize_plot(ax=None, fontsize=10):
    if ax is None:
        ax = plt.gca()

    sns.despine(ax=ax)

    # Set x-axis tick label font size
    ax.tick_params(axis="x", labelsize=fontsize)

    # Set legend font size (if legend exists)
    legend = ax.get_legend()
    if legend is not None:
        legend.get_frame().set_facecolor("white")

    ax.figure.tight_layout()
