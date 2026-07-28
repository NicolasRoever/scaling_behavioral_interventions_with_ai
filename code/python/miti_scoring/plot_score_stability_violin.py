"""
Violin plot version of the score-stability comparison: same layout as
plot_score_stability.py (faceted by MITI metric, one row per procedure), but
showing the full pooled score distribution per procedure as a violin instead of
just mean + percentile interval.

Styled to match the paper's other figures (see paper_plot_style.py).
"""

import matplotlib.pyplot as plt
import numpy as np

from build_score_stability_table import ROW_ORDER, build_procedure_frames
from paper_plot_style import PROCEDURE_COLORS, TEXT_MUTED, TEXT_PRIMARY, TEXT_SECONDARY, apply_style, strip_spines

OUT_PNG = "output/score_stability_violin_plot.png"
OUT_PDF = "output/score_stability_violin_plot.pdf"

PROCEDURES = ["Benchmark", "All Runs Pooled", "Stochastic Reruns Only", "Different Model Only", "Prompt Ablation Only"]


def scores_for(frames, dim, proc):
    df = frames[proc]
    if dim == "Global":
        return df["score"].to_numpy(dtype=float)
    return df[df["miti_dimension"] == dim]["score"].to_numpy(dtype=float)


def main():
    apply_style()
    frames = build_procedure_frames()

    fig, axes = plt.subplots(len(ROW_ORDER), 1, figsize=(6.5, 9), sharex=True)

    rng = np.random.default_rng(0)

    for ax, dim in zip(axes, ROW_ORDER):
        positions = range(len(PROCEDURES))
        data = [scores_for(frames, dim, proc) for proc in PROCEDURES]

        parts = ax.violinplot(
            data, positions=positions, vert=False, widths=0.8,
            showmeans=False, showmedians=False, showextrema=False,
        )
        for body, proc in zip(parts["bodies"], PROCEDURES):
            color = PROCEDURE_COLORS[proc]
            body.set_facecolor(color)
            body.set_edgecolor(color)
            body.set_alpha(0.45)
            body.set_linewidth(1.2)

        # jittered raw-score scatter, subsampled so dense integer scores don't
        # just paint a solid bar
        for y, proc in zip(positions, PROCEDURES):
            scores = data[y]
            n_show = min(len(scores), 400)
            sample = rng.choice(scores, size=n_show, replace=False)
            jitter = rng.uniform(-0.28, 0.28, size=n_show)
            ax.scatter(sample, np.full(n_show, y) + jitter, s=4, color=PROCEDURE_COLORS[proc],
                       alpha=0.25, linewidths=0, zorder=2)

        means = [d.mean() for d in data]
        ax.scatter(means, positions, marker="|", color=TEXT_PRIMARY, s=220, linewidths=1.6, zorder=3)

        ax.set_yticks(list(positions))
        ax.set_yticklabels(PROCEDURES, fontsize=9, color=TEXT_SECONDARY)
        ax.tick_params(axis="y", length=0)
        ax.set_ylim(len(PROCEDURES) - 0.5, -0.5)
        ax.set_xlim(0.3, 5.7)
        ax.set_xticks([1, 2, 3, 4, 5])
        strip_spines(ax, keep=("bottom",))
        ax.spines["bottom"].set_color(TEXT_MUTED)
        ax.tick_params(axis="x", colors=TEXT_MUTED, labelsize=9)
        ax.set_title(dim, loc="left", fontsize=10, color=TEXT_PRIMARY, fontweight="bold", pad=6)

    axes[-1].set_xlabel("Score (1-5)", fontsize=10, color=TEXT_SECONDARY)
    fig.suptitle(
        "Distribution of scores by scoring procedure\n(full corpus, N=2195 sessions; short tick = mean)",
        fontsize=11, color=TEXT_PRIMARY, y=0.985, fontweight="bold",
    )
    fig.subplots_adjust(left=0.26, right=0.97, top=0.9, bottom=0.055, hspace=0.65)

    fig.savefig(OUT_PNG, dpi=200)
    fig.savefig(OUT_PDF)
    print(f"Saved {OUT_PNG} and {OUT_PDF}")


if __name__ == "__main__":
    main()
