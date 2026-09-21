from pathlib import Path
import pandas as pd
import numpy as np
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

def paper_topic_label_map(df: pd.DataFrame) -> dict:
    """Map every original topic ID to the label displayed in the paper."""
    label_map = dict(zip(df["topic_id"], df["topic_label"]))
    return {
        topic_id: next(
            (
                label
                for _, topic_ids, label in paper_topic_merge_specs()
                if topic_id in topic_ids
            ),
            original_label,
        )
        for topic_id, original_label in label_map.items()
    }

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

def load_topic_model_documents(proj_dir: str):
    """
    Load and filter the interview-response corpus used for BERTopic
    topic modeling: answers of at least 10 characters from non-control
    treatment arms, merged with each respondent's treatment assignment.

    Mirrors the loading/filtering logic in classify_bertopic.py so both
    the original pipeline and any robustness/stability analysis operate
    on an identical corpus.

    Parameters
    ----------
    proj_dir : str
        Project root containing data/raw/main_socialmedia/chats_raw.csv
        and data/processed/main_social_media/clean_data.dta.

    Returns
    -------
    docs : list[str]
        Filtered response texts, in corpus order.
    doc_idx : list[int]
        Row indices into `data` (the merged scripts+survey frame)
        corresponding to each entry in `docs`.
    data : pd.DataFrame
        The full merged scripts+survey frame (pre-filtering), for
        downstream joins (e.g. user_id_raw, treatment, T).
    """
    scripts = pd.read_csv(
        proj_dir + "/data/raw/main_socialmedia/chats_raw.csv",
        usecols=["session_id", "type", "content", "question_name", "order"],
    )
    scripts = scripts.dropna(subset="content", how="any")
    scripts["user_id_raw"] = scripts["session_id"].str[11:].astype(int)

    survey = pd.read_stata(
        proj_dir + "/data/processed/main_social_media/clean_data.dta",
        convert_categoricals=False,
    )
    data = scripts.merge(survey[["user_id_raw", "T"]], on=["user_id_raw"], how="left")
    data = data.dropna(subset="T")
    del data["session_id"]
    data["T"] = data["T"].astype(int)
    treatments = {0: "Control", 1: "Change Talk", 2: "Ambivalence", 3: "Direct persuasion"}
    data["treatment"] = data["T"].map(treatments)

    mask = (
        (data["type"] == "answer")
        & (data["content"].str.len() >= 10)
        & (data["treatment"] != "Control")
    )
    docs = data.loc[mask, "content"].tolist()
    doc_idx = data.loc[mask].index.tolist()

    return docs, doc_idx, data

def jaccard(a: set, b: set) -> float:
    """Jaccard similarity between two keyword sets (0 if either is empty)."""
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)

def top_keywords(topic_model, topic_id, n=10):
    """Top-n c-TF-IDF keywords for a BERTopic topic, as a set."""
    return {w for w, _ in topic_model.get_topic(topic_id)[:n]}

def best_jaccard_matches(keywords_a: dict, keywords_b: dict) -> pd.DataFrame:
    """
    For each topic in `keywords_a`, find its best-matching topic in
    `keywords_b` by keyword Jaccard overlap. Used to re-identify "the same"
    topic across two separate BERTopic fits, since topic ids are not
    stable across runs (different seeds, corpora, or library versions).

    Parameters
    ----------
    keywords_a, keywords_b : dict[int topic_id -> set[str] keywords]

    Returns
    -------
    pd.DataFrame with columns topic_a, best_match_topic_b, jaccard,
    sorted by jaccard descending.
    """
    rows = []
    for tid_a, kw_a in keywords_a.items():
        best_b, best_score = None, -1.0
        for tid_b, kw_b in keywords_b.items():
            score = jaccard(kw_a, kw_b)
            if score > best_score:
                best_b, best_score = tid_b, score
        rows.append(dict(topic_a=tid_a, best_match_topic_b=best_b, jaccard=best_score))
    return pd.DataFrame(rows).sort_values("jaccard", ascending=False)
