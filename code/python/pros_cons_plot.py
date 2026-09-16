from __future__ import annotations
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import seaborn as sns

def treatment_labels(values: pd.Series) -> pd.Series:
    """Map internal arm names to the labels displayed in the manuscript."""
    return values.replace(
        {
            "Ambivalence": "Decisional Balance",
            "Persuasion": "Direct Persuasion",
        }
    )

def set_plot_style() -> tuple[str, str]:
    """Apply the manuscript style and return the two series colors."""
    sns.set_theme(style="white", font="Arial", font_scale=1.3)
    colors = ("#800000", "#1a476f")
    plt.rcParams.update(
        {
            "legend.frameon": False,
            "axes.grid": False,
            "figure.figsize": (10, 8),
        }
    )
    return colors

def create_figure(results: pd.DataFrame) -> plt.Figure:
    """Plot means and bootstrap 95% CIs from locally counted aspect strings."""
    data = results.copy()
    data["treatment"] = treatment_labels(data["T"])
    order = ["Change Talk", "Decisional Balance", "Direct Persuasion"]
    colors = set_plot_style()
    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True, sharey=True)

    plot_specs = (
        ("number_positive_aspects", "Positive aspects", colors[0]),
        ("number_negative_aspects", "Negative aspects", colors[1]),
    )
    for ax, (column, label, color) in zip(axes, plot_specs):
        sns.barplot(
            data=data,
            x=column,
            y="treatment",
            order=order,
            errorbar=("ci", 95),
            seed=142,
            color=color,
            errcolor="black",
            capsize=0.1,
            ax=ax,
        )
        ax.set_xlabel("")
        ax.set_ylabel("")
        sns.despine(ax=ax)

    handles = [
        mlines.Line2D([], [], color=color, linewidth=8, label=label)
        for _, label, color in plot_specs
    ]
    fig.legend(
        handles=handles,
        bbox_to_anchor=(1, 0.5),
        loc="center left",
        frameon=False,
    )
    axes[1].set_xlabel("Number of distinct aspects mentioned by participant")
    axes[0].set_xlim(0, 10)
    fig.tight_layout()
    return fig
