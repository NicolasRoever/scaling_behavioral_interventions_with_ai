"""Document-level topic reproducibility across UMAP random seeds.

The labeled assignments used in the paper are the reference. This is
important because BERTopic topic IDs are local to a fitted model and cannot
be carried over to a new fit. Each original topic is matched to the
non-outlier reseeded topic with the greatest document-membership Jaccard
overlap. For displayed topics that manually combine original topics, the
matched reseeded topics are combined before reproducibility is calculated.

The primary metric retains the paper's original criterion:
  * reproduced in a seed: at least 50% of the reference documents are
    recovered by the matched non-outlier topic(s);
  * stable overall: reproduced in at least 70% of the nine reseeds.

Precision, F1, and Jaccard are also saved as stricter diagnostics.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from helper import apply_paper_topic_merges


OUTPUT_DIR = Path(__file__).parent / "output"
PACKAGE_ROOT = Path(__file__).resolve().parents[2]
FIG_PATH = PACKAGE_ROOT / "results/figures/fig_topic_seed_stability.pdf"
GRANULAR_FIG_PATH = OUTPUT_DIR / "fig_topic_seed_stability_f1_by_seed.pdf"
NR_TOPICS = 30
RESEEDS = [7, 13, 21, 42, 99, 123, 256, 314, 500]
RETENTION_THRESHOLD = 0.5
STABLE_FRACTION = 0.7


def load_reference_assignments(package_root, docs, doc_idx, data):
    """Load and verify the exact labeled document assignments used in the paper."""
    reference = pd.read_csv(
        package_root / "data/processed/main_social_media/bertopic_labeled.csv"
    )
    expected_content = reference["content"].astype(str).tolist()
    expected_users = reference["user_id_raw"].to_numpy()
    expected_treatment = reference["T"].to_numpy()
    current_users = data.loc[doc_idx, "user_id_raw"].to_numpy()
    current_treatment = data.loc[doc_idx, "T"].to_numpy()

    if len(reference) != len(docs) or expected_content != list(docs):
        raise ValueError(
            "The saved labeled BERTopic rows do not align with the current corpus"
        )
    if not np.array_equal(expected_users, current_users):
        raise ValueError("Respondent IDs do not align with the labeled BERTopic rows")
    if not np.array_equal(expected_treatment, current_treatment):
        raise ValueError("Treatment assignments do not align with the labeled rows")
    return reference


def displayed_topic_specs(reference):
    """Return displayed topic IDs, labels, and their original component IDs."""
    unique_topics = reference[["topic_id", "topic_label"]].drop_duplicates()
    displayed_topics = apply_paper_topic_merges(unique_topics)
    crosswalk = pd.DataFrame(
        {
            "original_topic_id": unique_topics["topic_id"].astype(int),
            "topic_id": displayed_topics["topic_id"].astype(int),
            "topic_label": displayed_topics["topic_label"],
        }
    )
    crosswalk = crosswalk.loc[crosswalk["topic_id"] != -1]

    return [
        {
            "topic_id": int(topic_id),
            "topic_label": group["topic_label"].iloc[0],
            "component_topic_ids": tuple(
                sorted(group["original_topic_id"].astype(int))
            ),
        }
        for topic_id, group in crosswalk.groupby("topic_id", sort=True)
    ]


def best_document_match(reference_topics, seed_topics, reference_topic_id):
    """Find the non-outlier seed topic with greatest document Jaccard overlap."""
    reference_mask = reference_topics == reference_topic_id
    best_topic_id = None
    best_jaccard = 0.0
    for seed_topic_id in sorted(set(seed_topics) - {-1}):
        seed_mask = seed_topics == seed_topic_id
        intersection = np.count_nonzero(reference_mask & seed_mask)
        if intersection == 0:
            continue
        union = np.count_nonzero(reference_mask | seed_mask)
        score = intersection / union
        if score > best_jaccard:
            best_topic_id = int(seed_topic_id)
            best_jaccard = score
    return best_topic_id


def binary_overlap(reference_mask, matched_mask):
    """Return document-overlap diagnostics for two binary memberships."""
    intersection = np.count_nonzero(reference_mask & matched_mask)
    reference_n = np.count_nonzero(reference_mask)
    matched_n = np.count_nonzero(matched_mask)
    union = np.count_nonzero(reference_mask | matched_mask)
    retention = intersection / reference_n if reference_n else np.nan
    precision = intersection / matched_n if matched_n else 0.0
    f1 = (
        2 * precision * retention / (precision + retention)
        if precision + retention
        else 0.0
    )
    jaccard = intersection / union if union else 0.0
    return {
        "n_reference_docs": int(reference_n),
        "n_matched_docs": int(matched_n),
        "retention": retention,
        "precision": precision,
        "f1": f1,
        "jaccard": jaccard,
    }


def evaluate_displayed_topic(reference_topics, seed_topics, topic_spec):
    """Match a displayed topic's components and evaluate their combined overlap."""
    component_matches = {
        component_id: best_document_match(
            reference_topics,
            seed_topics,
            component_id,
        )
        for component_id in topic_spec["component_topic_ids"]
    }
    matched_topic_ids = sorted(
        {
            matched_id
            for matched_id in component_matches.values()
            if matched_id is not None
        }
    )
    reference_mask = np.isin(
        reference_topics,
        topic_spec["component_topic_ids"],
    )
    matched_mask = np.isin(seed_topics, matched_topic_ids)
    return {
        **binary_overlap(reference_mask, matched_mask),
        "matched_seed_topic_ids": ",".join(map(str, matched_topic_ids)),
        "component_matches": ";".join(
            f"{component_id}:{component_matches[component_id]}"
            for component_id in topic_spec["component_topic_ids"]
        ),
    }


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


def save_metric_matrix(metrics, value_column, output_path):
    """Save a topic-by-seed matrix for one document-overlap metric."""
    matrix = metrics.pivot(
        index=["topic_id", "topic_label"],
        columns="seed",
        values=value_column,
    )
    matrix.to_csv(output_path)


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


def save_granular_stability_figure(metrics, figure_path):
    """Plot seed-level F1 overlap, which penalizes splits and mergers."""
    topic_stats = (
        metrics.groupby(["topic_id", "topic_label"], sort=False)
        .agg(
            n_docs=("n_reference_docs", "first"),
            mean_f1=("f1", "mean"),
        )
        .reset_index()
        .sort_values(["mean_f1", "topic_id"])
    )
    matrix = (
        metrics.pivot(
            index="topic_id",
            columns="seed",
            values="f1",
        )
        .reindex(topic_stats["topic_id"])
    )
    topic_labels = topic_stats.set_index("topic_id")["topic_label"]
    topic_sizes = topic_stats.set_index("topic_id")["n_docs"]
    y_labels = [
        f"{topic_labels.loc[topic_id]} (n={topic_sizes.loc[topic_id]:,})"
        for topic_id in matrix.index
    ]
    color_map = LinearSegmentedColormap.from_list(
        "paper_navy",
        ["#f2f2f2", "#b9b9cf", "#4c4c86"],
    )

    plt.rcParams.update({"font.family": "Arial", "font.size": 10})
    fig, ax = plt.subplots(figsize=(11, 0.36 * len(matrix) + 1.8))
    image = ax.imshow(
        matrix.to_numpy(),
        aspect="auto",
        cmap=color_map,
        vmin=0,
        vmax=1,
        interpolation="nearest",
    )
    ax.set_xticks(
        np.arange(len(matrix.columns)),
        labels=[str(seed) for seed in matrix.columns],
    )
    ax.set_yticks(np.arange(len(matrix.index)), labels=y_labels)
    ax.set_xlabel("UMAP random seed")
    ax.set_title(
        "Document-membership overlap across UMAP reseeds",
        fontweight="bold",
        pad=10,
    )
    ax.tick_params(length=0)
    for row_index, row in enumerate(matrix.to_numpy()):
        for column_index, value in enumerate(row):
            ax.text(
                column_index,
                row_index,
                f"{value:.2f}",
                ha="center",
                va="center",
                fontsize=7,
                color="white" if value >= 0.62 else "#222222",
            )
    for spine in ax.spines.values():
        spine.set_visible(False)
    colorbar = fig.colorbar(image, ax=ax, fraction=0.025, pad=0.02)
    colorbar.set_label("F1 document overlap")
    colorbar.outline.set_visible(False)
    fig.tight_layout()
    figure_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(figure_path, bbox_inches="tight")
    plt.close(fig)


def main(
    output_dir,
    figure_path,
    granular_figure_path,
    proj_dir,
    nr_topics,
    reseeds,
    retention_threshold,
    stable_fraction,
    figure_only=False,
    granular_figure_only=False,
):
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "topic_seed_stability_summary.csv"

    if granular_figure_only:
        metrics = pd.read_csv(
            output_dir / "topic_seed_stability_metrics.csv"
        )
        save_granular_stability_figure(metrics, granular_figure_path)
        return

    if figure_only:
        summary = pd.read_csv(summary_path)
        save_stability_figure(
            summary,
            figure_path,
            stable_fraction,
            retention_threshold,
            len(reseeds),
        )
        return

    from topic_model_robustness import (
        fit_topic_model,
        get_documents,
        get_embeddings,
    )

    docs, doc_idx, data = get_documents()
    embeddings = get_embeddings(docs)
    reference = load_reference_assignments(
        proj_dir,
        docs,
        doc_idx,
        data,
    )
    reference_topics = reference["topic_id"].to_numpy()
    topic_specs = displayed_topic_specs(reference)

    seed_rows = []
    assignment_rows = []
    for seed in reseeds:
        print(f"Fitting reseeded model (seed={seed}, nr_topics={nr_topics}) ...")
        _, seed_topics, _ = fit_topic_model(
            docs,
            embeddings,
            nr_topics=nr_topics,
            umap_random_state=seed,
        )
        assignment_rows.append(
            pd.DataFrame(
                {
                    "doc_position": np.arange(len(seed_topics)),
                    "doc_idx": doc_idx,
                    "seed": seed,
                    "topic_id": seed_topics,
                }
            )
        )
        for topic_spec in topic_specs:
            seed_rows.append(
                {
                    "seed": seed,
                    "topic_id": topic_spec["topic_id"],
                    "topic_label": topic_spec["topic_label"],
                    "component_topic_ids": ",".join(
                        map(str, topic_spec["component_topic_ids"])
                    ),
                    **evaluate_displayed_topic(
                        reference_topics,
                        seed_topics,
                        topic_spec,
                    ),
                }
            )

    metrics = pd.DataFrame(seed_rows)
    metrics.to_csv(
        output_dir / "topic_seed_stability_metrics.csv",
        index=False,
    )
    pd.concat(assignment_rows, ignore_index=True).to_csv(
        output_dir / "topic_seed_stability_assignments.csv",
        index=False,
    )
    for metric in ("retention", "precision", "f1", "jaccard"):
        save_metric_matrix(
            metrics,
            metric,
            output_dir / f"topic_seed_stability_{metric}_matrix.csv",
        )
    # Preserve the previous filename for downstream code while correcting its
    # contents: it now contains outlier-excluding document retention.
    save_metric_matrix(
        metrics,
        "retention",
        output_dir / "topic_seed_stability_purity_matrix.csv",
    )

    summary = summarize_metrics(
        metrics,
        retention_threshold,
        stable_fraction,
    )
    summary.to_csv(summary_path, index=False)

    stable_count = int(summary["stable"].sum())
    print(
        f"\n{stable_count}/{len(summary)} displayed topics are stable "
        f"(retention >= {retention_threshold:.0%} in at least "
        f"{stable_fraction:.0%} of reseeds)."
    )
    print(
        summary[
            [
                "topic_id",
                "topic_label",
                "mean_retention",
                "min_retention",
                "frac_seeds_reproduced",
                "mean_f1",
                "mean_jaccard",
                "stable",
            ]
        ].to_string(index=False)
    )
    print("\nTopics to gray out:")
    print(summary.loc[~summary["stable"], "topic_label"].tolist())

    save_stability_figure(
        summary,
        figure_path,
        stable_fraction,
        retention_threshold,
        len(reseeds),
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--figure-only",
        action="store_true",
        help="Regenerate the PDF from the corrected stability summary CSV.",
    )
    parser.add_argument(
        "--granular-figure-only",
        action="store_true",
        help="Create the seed-level F1 heatmap from the saved metrics CSV.",
    )
    arguments = parser.parse_args()
    main(
        output_dir=OUTPUT_DIR,
        figure_path=FIG_PATH,
        granular_figure_path=GRANULAR_FIG_PATH,
        proj_dir=PACKAGE_ROOT,
        nr_topics=NR_TOPICS,
        reseeds=RESEEDS,
        retention_threshold=RETENTION_THRESHOLD,
        stable_fraction=STABLE_FRACTION,
        figure_only=arguments.figure_only,
        granular_figure_only=arguments.granular_figure_only,
    )
