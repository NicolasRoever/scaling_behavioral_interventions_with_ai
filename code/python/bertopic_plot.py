from __future__ import annotations
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from helper import apply_paper_topic_merges, paper_unstable_topic_labels

def main(derived, output_dir):
    df = pd.read_csv(
        derived / "bertopic_labeled.csv"
    )
    df = apply_paper_topic_merges(df)
    stability_summary = pd.read_csv(derived / "topic_seed_stability_summary.csv")
    unstable_topic_labels = paper_unstable_topic_labels(stability_summary)
    
    topics = df[["topic_label", "topic_id"]].drop_duplicates()
    topic_labels = dict(zip(topics["topic_id"], topics["topic_label"]))
    
    
    # Focus on non-junk topics
    counts = df.groupby(["topic_id", "user_id_raw"]).size().reset_index()
    counts = counts.rename(columns={0: "topic_count"})
    counts["topic_labels"] = counts["topic_id"].map(topic_labels)
    counts = counts.merge(df[["user_id_raw", "treatment", "T"]].drop_duplicates(), on="user_id_raw", how="left")
    counts["topic_dummy"] = (counts["topic_count"] > 0).astype(int)
    counts
    
    counts_by_treatment = counts.groupby(["T", "topic_id"])["topic_dummy"].sum().reset_index()
    treatment_group_sizes = counts.groupby("T")["user_id_raw"].nunique().reset_index(name="T_size")
    
    frequencies = counts_by_treatment.merge(treatment_group_sizes, on="T", how="left")
    frequencies["frequency"] = frequencies["topic_dummy"] / frequencies["T_size"] * 100.0

    # Match the source: exclude the outlier after fixing all-conversation denominators.
    frequencies = frequencies.loc[frequencies["topic_id"] != -1].copy()
    
    
    
    
    
    
    
    # Ensure consistent ordering of topics (by topic_id; change if you prefer by overall frequency)
    topic_ids = sorted(frequencies["topic_id"].unique())
    topic_names = [topic_labels.get(tid, f"Topic {tid}") for tid in topic_ids]
    
    # Ensure consistent ordering of treatment arms (uses your coding: 1,2,3)
    T_order = sorted(frequencies["T"].unique())
    
    # Pivot to a matrix: rows=topic_id, cols=T, values=frequency
    pivot = (
        frequencies
        .pivot_table(index="topic_id", columns="T", values="frequency", aggfunc="first")
        .reindex(index=topic_ids, columns=T_order)
        .fillna(0.0)
    )
    
    # Color plus redundant hatch encodings keep treatment arms distinguishable
    # both on screen and when printed in black and white.
    facecolors = ["#b83232", "#777777", "#4c4c86"]
    hatches = ["", "///", "xxx"]
    treatment_name_map = {1: "Change Talk", 2: "Decisional Balance", 3: "Direct Persuasion"}
    legend_labels = [treatment_name_map.get(t, f"T{t}") for t in T_order]
    
    # ---- Plot: grouped horizontal bar chart ----
    plt.rcParams['font.family'] = 'Arial'
    plt.rcParams['font.size'] = 14
    
    fig, ax = plt.subplots(figsize=(10, 0.3 * len(topic_ids) + 2))
    y = np.arange(len(topic_ids))
    n_groups = len(T_order)
    
    # Bar geometry: grouped bars around each y position
    group_height = 0.8
    bar_height = group_height / max(n_groups, 1)
    offsets = (np.arange(n_groups) - (n_groups - 1) / 2) * bar_height
    
    for j, t in enumerate(T_order):
        ax.barh(
            y + offsets[j],
            pivot[t].values,
            height=bar_height * 0.95,
            color=facecolors[j],
            hatch=hatches[j],
            label=legend_labels[j],
            edgecolor="black",
            linewidth=0.7,
        )
    
    # Y-axis labels: topic labels from your dictionary
    ax.set_yticks(y)
    ax.set_yticklabels(topic_names)
    for tick_label, topic_name in zip(ax.get_yticklabels(), topic_names):
        if topic_name in unstable_topic_labels:
            tick_label.set_color("#8c8c8c")
    
    ax.set_xlabel("Share of conversations with topic present (%)", weight="bold", fontsize=14)
    ax.grid(axis="x", linestyle="-", linewidth=0.5, alpha=0.3)
    
    ax.set_xticks(np.arange(0, 101, 10))
    ax.xaxis.grid(True, which="major", linestyle="-", linewidth=0.5, alpha=0.3)
    
    ax.set_ylim(-0.5, len(topic_ids) - 0.5)
    ax.invert_yaxis()  # top-to-bottom ordering; remove if you prefer the opposite
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    ax.legend(loc="lower right", fontsize=14, frameon=True, edgecolor="black")
    plt.tight_layout()
    fig.savefig(output_dir / "fig_bertopic.pdf")
    plt.close(fig)
