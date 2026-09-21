from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter, FormatStrFormatter

def save_elbow_figure(elbow_df, figure_path, selected_nr_topics=30):
    """Save the topic-count diagnostics where the paper compiles figures."""
    navy = "#4c4c86"
    text_color = "#222222"
    grid_color = "#d9d9d9"
    plt.rcParams.update({"font.family": "Arial", "font.size": 12})

    figure_path.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6), sharex=True)
    panels = zip(
        axes,
        ["largest_topic_share", "mean_intra_topic_cosine", "silhouette"],
        [
            "Largest-topic share",
            "Within-topic similarity",
            "Cluster separation",
        ],
    )
    for ax, col, title in panels:
        ax.plot(
            elbow_df["nr_topics"],
            elbow_df[col],
            color=navy,
            marker="o",
            markersize=6,
            linewidth=2,
            markeredgecolor="white",
            markeredgewidth=0.8,
            zorder=3,
        )
        ax.axvline(
            selected_nr_topics,
            color="#777777",
            linestyle="--",
            linewidth=1.2,
            zorder=2,
        )
        ax.set_title(title, color=text_color, fontweight="bold", pad=8)
        ax.set_xticks(elbow_df["nr_topics"])
        ax.tick_params(colors="#555555")
        ax.grid(axis="y", color=grid_color, linewidth=0.7, alpha=0.8)
        ax.set_axisbelow(True)
        for spine in ("top", "right", "left"):
            ax.spines[spine].set_visible(False)
        ax.spines["bottom"].set_color("#aaaaaa")

    axes[0].set_ylabel("Share of assigned documents")
    axes[0].yaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=0))
    axes[1].set_ylabel("Mean cosine similarity")
    axes[1].yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
    axes[2].set_ylabel("Silhouette score")
    axes[2].yaxis.set_major_formatter(FormatStrFormatter("%.3f"))
    fig.supxlabel("Target number of topics", y=0.02, color=text_color)
    fig.tight_layout(rect=(0, 0.06, 1, 1), w_pad=2.2)
    fig.savefig(figure_path, bbox_inches="tight")
    plt.close(fig)


def summarize_metrics(metrics, retention_threshold, stable_fraction):
    """Summarize seed-level diagnostics and apply the stability criterion."""
    grouped = metrics.groupby(["topic_id", "topic_label"], sort=False)
    summary = grouped.agg(
        n_docs=("n_reference_docs", "first"),
        mean_retention=("retention", "mean"),
        min_retention=("retention", "min"),
        mean_precision=("precision", "mean"),
        min_precision=("precision", "min"),
        mean_f1=("f1", "mean"),
        min_f1=("f1", "min"),
        mean_jaccard=("jaccard", "mean"),
        min_jaccard=("jaccard", "min"),
    ).reset_index()
    reproduced = (
        metrics.assign(
            reproduced=metrics["retention"] >= retention_threshold
        )
        .groupby(["topic_id", "topic_label"], sort=False)["reproduced"]
        .mean()
        .rename("frac_seeds_reproduced")
        .reset_index()
    )
    summary = summary.merge(
        reproduced,
        on=["topic_id", "topic_label"],
        validate="one_to_one",
    )
    summary["stable"] = summary["frac_seeds_reproduced"] >= stable_fraction
    return summary.sort_values(
        ["frac_seeds_reproduced", "mean_retention", "topic_id"]
    ).reset_index(drop=True)

def save_stability_figure(
    summary,
    figure_path,
    stable_fraction,
    retention_threshold,
    n_reseeds,
):
    """Plot the fraction of reseeds that reproduce each displayed topic."""
    ordered = summary.sort_values(
        ["frac_seeds_reproduced", "mean_retention", "topic_id"]
    )
    colors = np.where(ordered["stable"], "#4c4c86", "#b83232")
    y_positions = np.arange(len(ordered))

    plt.rcParams.update({"font.family": "Arial", "font.size": 11})
    fig, ax = plt.subplots(figsize=(11, 0.34 * len(ordered) + 1.8))
    ax.barh(
        y_positions,
        ordered["frac_seeds_reproduced"],
        color=colors,
        edgecolor="white",
        linewidth=0.5,
    )
    ax.set_yticks(y_positions, labels=ordered["topic_label"])
    ax.axvline(
        stable_fraction,
        color="#666666",
        linestyle="--",
        linewidth=1.2,
    )
    ax.set_xlim(0, 1.02)
    ax.set_xticks(np.linspace(0, 1, 6))
    ax.set_xticklabels([f"{int(value * 100)}%" for value in np.linspace(0, 1, 6)])
    ax.set_xlabel(
        f"Share of {n_reseeds} reseeds retaining at least "
        f"{int(retention_threshold * 100)}% of reference documents"
    )
    ax.set_title("Displayed-topic reproducibility under UMAP reseeding")
    ax.grid(axis="x", color="#d9d9d9", linewidth=0.7, alpha=0.8)
    ax.set_axisbelow(True)
    ax.invert_yaxis()
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#aaaaaa")
    fig.tight_layout()
    figure_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(figure_path, bbox_inches="tight")
    plt.close(fig)
