raise RuntimeError("Restricted-input source only. Raw interview data are not distributed. API execution is disabled in this $0-API replication package; use code/python/run_public.py for saved-result reproduction.")
# Topic model robustness: elbow across nr_topics + headline-topic stability
#
# Addresses R3 (Topic-a) and R5.7: classify_bertopic.py fixes nr_topics=30
# without justification. This script (a) sweeps nr_topics over a grid to
# show an elbow-style justification for the chosen value, and (b) checks
# whether the three headline contrasts used in the paper survive across
# the grid, flagging fragile topics. No LLM calls anywhere -- matching
# across runs uses BERTopic's own c-TF-IDF keyword representations and
# document-level cluster membership only.
#
# Prerequisite: run this in an env with bertopic/sentence-transformers/umap
# installed (e.g. `sonia_project`) and numpy<2.4 pinned there (umap's numba
# dependency does not support numpy>=2.4 as of writing).

import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.ticker import FormatStrFormatter, PercentFormatter
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import cosine_similarity

from helper import (
    load_topic_model_documents, save_regression_result, load_regression_result,
    jaccard, top_keywords, best_jaccard_matches,
)

from umap import UMAP
from hdbscan import HDBSCAN
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer
from bertopic import BERTopic
from bertopic.vectorizers import ClassTfidfTransformer
from bertopic.representation import MaximalMarginalRelevance


PROJ_DIR = "/Users/nicolasroever/Dropbox/MI"
OUTPUT_DIR = Path(__file__).parent / "output"
CACHE_DIR = Path(__file__).parent / "output" / "cache"
FIG_PATH = (
    Path(PROJ_DIR)
    / "code/analysis_NR/6731ca401220dcd3b28dc2ec/figures"
    / "fig_topic_robustness_elbow.pdf"
)

# Same fixed configuration as classify_bertopic.py -- only nr_topics varies.
NR_TOPICS_GRID = [10, 20, 30, 40, 50]
UMAP_KWARGS = dict(n_neighbors=10, n_components=5, min_dist=0.0, metric="cosine", random_state=142)
HDBSCAN_KWARGS = dict(min_cluster_size=30, min_samples=10, metric="euclidean",
                       cluster_selection_method="eom", prediction_data=True)

# Set to a small integer while iterating on the script itself; None for a full run.
SAMPLE_N = None


##########################################
#  Step 1: Load & filter documents       #
##########################################

def get_documents():
    docs, doc_idx, data = load_topic_model_documents(PROJ_DIR)
    if SAMPLE_N is not None:
        docs, doc_idx = docs[:SAMPLE_N], doc_idx[:SAMPLE_N]
    return docs, doc_idx, data


##########################################
#  Step 2: Compute / cache embeddings    #
##########################################

def get_embeddings(docs):
    key = f"embeddings_n{len(docs)}"
    cache_path = CACHE_DIR / f"{key}.pkl"
    try:
        return load_regression_result(cache_path)
    except KeyError:
        pass
    sentence_model = SentenceTransformer("all-mpnet-base-v2")
    embedding = sentence_model.encode(docs, show_progress_bar=True)
    save_regression_result(CACHE_DIR, key, embedding)
    return embedding


##########################################
#  Step 3: Fit BERTopic per grid value   #
##########################################

def fit_topic_model(docs, embedding, nr_topics, umap_random_state=142):
    # min_df=15 is classify_bertopic.py's setting, tuned for nr_topics=30
    # (i.e. >=30 per-topic pseudo-documents at the c-TF-IDF step). BERTopic
    # re-vectorizes over exactly `nr_topics` pseudo-documents whenever it
    # reduces to a target topic count, so min_df must not exceed nr_topics
    # or sklearn errors ("< documents than min_df"). Scale it down for
    # smaller grid values while keeping it identical (15) at k=30.
    min_df = min(15, max(2, nr_topics // 2))
    vectorizer_model = CountVectorizer(stop_words="english", ngram_range=(1, 2), min_df=min_df)
    ctfidf_model = ClassTfidfTransformer(bm25_weighting=False, reduce_frequent_words=True)
    representation_model = MaximalMarginalRelevance(diversity=0.2)

    umap_kwargs = {**UMAP_KWARGS, "random_state": umap_random_state}
    topic_model = BERTopic(
        min_topic_size=30,
        language="english",
        nr_topics=nr_topics,
        umap_model=UMAP(**umap_kwargs),
        hdbscan_model=HDBSCAN(**HDBSCAN_KWARGS),
        vectorizer_model=vectorizer_model,
        ctfidf_model=ctfidf_model,
        representation_model=representation_model,
    )
    topics, probs = topic_model.fit_transform(docs, embedding)
    return topic_model, np.asarray(topics), probs


##########################################
#  Step 4: Elbow metrics                 #
##########################################

def elbow_metrics(topic_model, topics, embedding):
    n = len(topics)
    # `nr_topics` reduces/merges the initial HDBSCAN topics but does not
    # reassign HDBSCAN's -1 labels. The outlier share is therefore retained
    # in the audit CSV but is not a diagnostic that can vary across this grid.
    outlier_share = float(np.mean(topics == -1))

    keep = topics != -1
    topic_counts = pd.Series(topics[keep]).value_counts()
    largest_topic_share = (
        float(topic_counts.max() / topic_counts.sum())
        if not topic_counts.empty
        else np.nan
    )
    if keep.sum() > 1 and len(set(topics[keep])) > 1:
        sil = float(silhouette_score(embedding[keep], topics[keep], metric="cosine"))
    else:
        sil = np.nan

    sims = []
    for t in sorted(set(topics[keep])):
        idx = np.where(topics == t)[0]
        if len(idx) < 2:
            continue
        sim_matrix = cosine_similarity(embedding[idx])
        iu = np.triu_indices_from(sim_matrix, k=1)
        sims.append(sim_matrix[iu].mean())
    mean_intra_cosine = float(np.mean(sims)) if sims else np.nan

    return dict(
        n_topics_actual=int(len(set(topics[keep]))),
        n_docs=n,
        outlier_share=outlier_share,
        largest_topic_share=largest_topic_share,
        mean_intra_topic_cosine=mean_intra_cosine,
        silhouette=sil,
    )


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


##########################################
#  Step 5: Match k=30 topics to the      #
#  original labeled run                  #
##########################################

def load_original_topic_keywords():
    """Reference keyword sets from the original run, one row per topic_id."""
    ref = pd.read_csv(PROJ_DIR + "/data/processed/main_social_media/bertopic_labeled.csv",
                       usecols=["topic_id", "topic_label", "topic_keywords"])
    ref = ref.drop_duplicates(subset="topic_id")
    ref["keyword_set"] = ref["topic_keywords"].apply(
        lambda s: {w.strip() for w in str(s).split(" - ")}
    )
    return ref.set_index("topic_id")


def match_k30_to_original(topic_model_k30, ref_topics):
    """For each k=30 topic, find its best-matching original topic_id by
    keyword Jaccard overlap. Returns a DataFrame for manual inspection."""
    new_keywords = {
        tid: top_keywords(topic_model_k30, tid)
        for tid in sorted(t for t in set(topic_model_k30.topics_) if t != -1)
    }
    orig_keywords = {tid: row["keyword_set"] for tid, row in ref_topics.iterrows()}
    match_df = best_jaccard_matches(new_keywords, orig_keywords)
    match_df = match_df.rename(columns={"topic_a": "new_topic_id", "best_match_topic_b": "best_match_original_topic_id"})
    match_df["new_keywords"] = match_df["new_topic_id"].map(lambda t: ", ".join(sorted(new_keywords[t])))
    match_df["best_match_original_label"] = match_df["best_match_original_topic_id"].map(
        lambda t: ref_topics.loc[t, "topic_label"] if t is not None else None)
    return match_df[["new_topic_id", "new_keywords", "best_match_original_topic_id",
                      "best_match_original_label", "jaccard"]]


##########################################
#  Step 6: Headline-topic stability      #
##########################################

def headline_stability(topics_by_k, headline_claims, doc_treatment, doc_user):
    """
    topics_by_k: dict[int nr_topics -> np.ndarray of topic ids, aligned to docs]
    headline_claims: dict[label -> {"topic": k=30 topic id, "claim": fn(freq_by_arm) -> bool}]
        `claim` encodes the *specific* directional comparison made in the
        paper text (e.g. Decisional Balance > Change Talk for cost/benefit
        trade-offs), not just "highest of the three arms" -- see main.tex
        line 396 for the exact claims this mirrors.
    doc_treatment: np.ndarray of T (1=Change Talk, 2=Decisional Balance,
        3=Direct Persuasion) aligned to docs.
    doc_user: np.ndarray of user_id_raw aligned to docs, for per-conversation
        (rather than per-document) topic-presence shares, matching how
        fig_bertopic.py aggregates ("share of conversations with topic
        present"), not a per-document rate.

    For each headline topic, tracks (a) merge purity: the share of its k=30
    documents that remain together in a single topic at other k, and
    (b) whether the paper's specific claimed arm comparison still holds at
    other k, following the topic's merge identity.
    """
    base_k = 30
    base_topics = topics_by_k[base_k]
    rows = []
    for label, spec in headline_claims.items():
        base_tid, claim = spec["topic"], spec["claim"]
        base_doc_idx = np.where(base_topics == base_tid)[0]
        if len(base_doc_idx) == 0:
            continue
        base_arm_freq = _topic_presence_by_arm(base_topics, doc_treatment, doc_user, base_tid)
        base_claim_holds = claim(base_arm_freq)

        for k, topics_k in topics_by_k.items():
            assigned = topics_k[base_doc_idx]
            # merge purity: largest single-topic share among the base doc set
            vals, counts = np.unique(assigned, return_counts=True)
            purity = counts.max() / len(assigned)
            majority_topic = vals[counts.argmax()]

            arm_freq = _topic_presence_by_arm(topics_k, doc_treatment, doc_user, majority_topic)
            claim_holds = claim(arm_freq)

            rows.append(dict(
                headline_topic=label,
                base_topic_id=base_tid,
                nr_topics=k,
                merge_purity=purity,
                majority_topic_at_k=int(majority_topic),
                arm_freq_1_changetalk=arm_freq.get(1, np.nan),
                arm_freq_2_decisionalbalance=arm_freq.get(2, np.nan),
                arm_freq_3_directpersuasion=arm_freq.get(3, np.nan),
                claim_holds_at_k=claim_holds,
                base_claim_holds=base_claim_holds,
                claim_stable=(claim_holds == base_claim_holds),
            ))
    return pd.DataFrame(rows)


def _topic_presence_by_arm(topics_k, doc_treatment, doc_user, topic_id):
    """Corpus-wide share of conversations (unique users), by arm, with at
    least one document assigned to topic_id -- mirrors fig_bertopic.py's
    `frequency` measure so arm rankings are comparable to the paper's."""
    df = pd.DataFrame({"user": doc_user, "arm": doc_treatment, "is_topic": topics_k == topic_id})
    has_topic = df.groupby("user").agg(arm=("arm", "first"), is_topic=("is_topic", "max"))
    return has_topic.groupby("arm")["is_topic"].mean()


##########################################
#  Main                                  #
##########################################

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    docs, doc_idx, data = get_documents()
    doc_treatment = data.loc[doc_idx, "T"].to_numpy()
    doc_user = data.loc[doc_idx, "user_id_raw"].to_numpy()
    embedding = get_embeddings(docs)

    elbow_rows = []
    topics_by_k = {}
    model_by_k = {}
    for k in NR_TOPICS_GRID:
        print(f"Fitting BERTopic with nr_topics={k} ...")
        topic_model, topics, probs = fit_topic_model(docs, embedding, nr_topics=k)
        topics_by_k[k] = topics
        model_by_k[k] = topic_model
        elbow_rows.append(dict(nr_topics=k, **elbow_metrics(topic_model, topics, embedding)))

    elbow_df = pd.DataFrame(elbow_rows)
    elbow_df.to_csv(OUTPUT_DIR / "topic_robustness_elbow.csv", index=False)
    print(elbow_df)

    save_elbow_figure(elbow_df, FIG_PATH)

    # Long-format doc-level assignments for auditability
    assign_rows = []
    for k, topics in topics_by_k.items():
        assign_rows.append(pd.DataFrame({
            "doc_idx": doc_idx,
            "nr_topics": k,
            "topic_id": topics,
        }))
    pd.concat(assign_rows, ignore_index=True).to_csv(
        OUTPUT_DIR / "topic_robustness_assignments.csv", index=False)

    # Match k=30 topics to the original labeled run
    ref_topics = load_original_topic_keywords()
    match_df = match_k30_to_original(model_by_k[30], ref_topics)
    match_df.to_csv(OUTPUT_DIR / "topic_robustness_k30_to_original_match.csv", index=False)
    print("\nTop keyword matches, k=30 topics -> original run's topic_id/label "
          "(inspect manually to confirm headline topics before filling in "
          "HEADLINE_NEW_TOPIC_IDS below):")
    print(match_df.to_string(index=False))

    # Headline topics explicitly named in main.tex (line 396) for the three
    # reviewer-flagged contrasts, mapped from their original topic_id (in
    # bertopic_labeled.csv) to this run's k=30 topic id via the keyword
    # match above. `claim` encodes the *specific* directional comparison
    # made in the paper text, not just "highest of the three arms"
    # (T: 1=Change Talk, 2=Decisional Balance, 3=Direct Persuasion).
    NEG_INF = float("-inf")
    HEADLINE_CLAIMS = {
        # orig 0: "DB ~20pp more likely than CT to discuss cost/benefit trade-off"
        "balancing_connection_costs_benefits": dict(
            topic=0, claim=lambda f: f.get(2, NEG_INF) > f.get(1, NEG_INF)),
        # orig 1, 10: "PP focuses considerably more on implementation strategies"
        "physical_strategies_limit_phone": dict(
            topic=18, claim=lambda f: f.get(3, NEG_INF) > f.get(1, NEG_INF) and f.get(3, NEG_INF) > f.get(2, NEG_INF)),
        "app_notification_management": dict(
            topic=10, claim=lambda f: f.get(3, NEG_INF) > f.get(1, NEG_INF) and f.get(3, NEG_INF) > f.get(2, NEG_INF)),
        # orig 3, 8, 9: "MI arms (CT & DB) substantially more likely to discuss
        # confidence / challenges sustaining change than PP"
        "confidence_changing_social_media_use": dict(
            topic=3, claim=lambda f: min(f.get(1, NEG_INF), f.get(2, NEG_INF)) > f.get(3, NEG_INF)),
        "self_confidence_behavior_change": dict(
            topic=9, claim=lambda f: min(f.get(1, NEG_INF), f.get(2, NEG_INF)) > f.get(3, NEG_INF)),
        "challenges_sustaining_personal_change": dict(
            topic=23, claim=lambda f: min(f.get(1, NEG_INF), f.get(2, NEG_INF)) > f.get(3, NEG_INF)),
        # orig 19: "CT shows a distinct spike in this topic"
        "preference_gradual_reduction": dict(
            topic=17, claim=lambda f: f.get(1, NEG_INF) > f.get(2, NEG_INF) and f.get(1, NEG_INF) > f.get(3, NEG_INF)),
    }

    stability_df = headline_stability(topics_by_k, HEADLINE_CLAIMS, doc_treatment, doc_user)
    stability_df.to_csv(OUTPUT_DIR / "topic_robustness_headline_stability.csv", index=False)
    print("\nHeadline topic stability (does the paper's specific claimed arm "
          "comparison hold at each nr_topics, following the topic's merge identity):")
    print(stability_df.to_string(index=False))

    fragile = stability_df.groupby("headline_topic").apply(
        lambda g: (g["merge_purity"] < 0.7).any() or (~g["claim_stable"]).any()
    )
    print("\nFragile headline topics (purity<0.7 at some k, or the claimed "
          "comparison flips relative to k=30):")
    print(fragile[fragile].index.tolist() or "None")

    not_holding_at_base = stability_df.loc[~stability_df["base_claim_holds"], "headline_topic"].unique()
    if len(not_holding_at_base):
        print("\nWARNING -- claim does not even hold at k=30 in this rerun "
              "(check against the paper's reported numbers before trusting "
              "the topic-id mapping above):")
        print(list(not_holding_at_base))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--figure-only",
        action="store_true",
        help="Regenerate the PDF from the existing elbow-metrics CSV.",
    )
    args = parser.parse_args()
    if args.figure_only:
        save_elbow_figure(
            pd.read_csv(OUTPUT_DIR / "topic_robustness_elbow.csv"),
            FIG_PATH,
        )
    else:
        main()
