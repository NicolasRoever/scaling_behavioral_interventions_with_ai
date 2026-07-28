# Interview-content analysis (R3 and the editor): differential word-frequency /
# keyness analysis of the AI interviewer's *questions*, by treatment arm.
#
# Method: log-odds-ratio with an informative Dirichlet prior (Monroe, Colaresi &
# Quinn 2008, "Fightin' Words", eq. 16-22). For each treatment arm vs. Control we
# compare word counts in the interviewer's questions, using the pooled word
# frequencies across all four arms as the informative background prior. This
# down-weights common/function words automatically (they get a large prior
# count, so their z-scores stay near zero) while flagging words that are
# genuinely over/under-represented in a given arm's questions.
#
# Please sync with Felix on this before it goes in the paper.

from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer, ENGLISH_STOP_WORDS

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = Path(__file__).parent / "output"
FIGURE_PATH = PACKAGE_ROOT / "results/figures/fig_keyness_interviewer_questions.pdf"

# Words must appear at least this many times (combined, arm + control) to be
# eligible for the plot -- rare words have noisy z-scores even with the prior.
MIN_COMBINED_COUNT = 5
N_WORDS_PER_SIDE = 12  # top words shown on each side of a panel

TREATMENT_LABELS = {0: "Control", 1: "Change Talk", 2: "Decisional Balance", 3: "Direct Persuasion"}
ARM_COLORS = {1: "#b83232", 2: "#777777", 3: "#4c4c86"}  # Change Talk, Decisional Balance, Direct Persuasion


##########################################
#  Step 1: Load & filter data            #
##########################################

def load_interviewer_questions():
    chats = pd.read_csv(
        PACKAGE_ROOT / "data/private/chats_raw.csv",
        usecols=["session_id", "type", "content", "question_name", "order"],
    )
    chats = chats.dropna(subset="content")
    chats["user_id_raw"] = chats["session_id"].str[11:].astype(int)

    survey = pd.read_stata(
        PACKAGE_ROOT / "data/processed/main_social_media/clean_data.dta",
        convert_categoricals=False,
        columns=["user_id_raw", "T"],
    )
    data = chats.merge(survey, on="user_id_raw", how="left").dropna(subset="T")
    data["T"] = data["T"].astype(int)
    data["treatment"] = data["T"].map(TREATMENT_LABELS)

    questions = data.loc[(data["type"] == "question") & (data["content"].str.len() >= 3)].copy()
    return questions


##########################################
#  Step 2: Tokenize & count words        #
##########################################

def word_counts(texts, vectorizer):
    """Return {word: count} for a list of documents, using a fitted-vocab vectorizer."""
    doc_term = vectorizer.transform(texts)
    counts = np.asarray(doc_term.sum(axis=0)).ravel()
    return dict(zip(vectorizer.get_feature_names_out(), counts))


##########################################
#  Step 3: Log-odds ratio w/ Dirichlet prior (Monroe et al. 2008) #
##########################################

def fightin_words(counts_i, counts_j, background_counts, min_combined_count=MIN_COMBINED_COUNT):
    """Log-odds-ratio with an informative Dirichlet prior.

    counts_i, counts_j: word -> count dicts for the two corpora being compared
    background_counts: word -> count dict used as the (informative) prior,
        i.e. a_w in Monroe et al. (2008); we use the pooled corpus across all
        arms so the prior is constant across pairwise comparisons.

    Returns a DataFrame with one row per word: count_i, count_j, delta (log
    odds ratio, positive = more associated with corpus i), zscore.
    """
    vocab = [w for w in (set(counts_i) | set(counts_j)) if background_counts.get(w, 0) > 0]
    a0 = sum(background_counts.values())
    n_i = sum(counts_i.values())
    n_j = sum(counts_j.values())

    rows = []
    for w in vocab:
        y_i = counts_i.get(w, 0)
        y_j = counts_j.get(w, 0)
        if y_i + y_j < min_combined_count:
            continue
        a_w = background_counts[w]

        delta = np.log((y_i + a_w) / (n_i + a0 - y_i - a_w)) - np.log(
            (y_j + a_w) / (n_j + a0 - y_j - a_w)
        )
        variance = 1.0 / (y_i + a_w) + 1.0 / (y_j + a_w)
        rows.append((w, y_i, y_j, delta, delta / np.sqrt(variance)))

    return pd.DataFrame(rows, columns=["word", "count_i", "count_j", "delta", "zscore"])


##########################################
#  Step 4: Plot                          #
##########################################

def plot_panel(ax, keyness, arm_label, arm_color, n_words=N_WORDS_PER_SIDE):
    top_arm = keyness.sort_values("zscore", ascending=False).head(n_words)
    top_control = keyness.sort_values("zscore", ascending=True).head(n_words)
    panel = pd.concat([top_control, top_arm]).sort_values("zscore")

    colors = [arm_color if z > 0 else "#bdbdbd" for z in panel["zscore"]]
    y = np.arange(len(panel))
    ax.barh(y, panel["zscore"], color=colors, edgecolor="none")
    ax.set_yticks(y)
    ax.set_yticklabels(panel["word"])
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_title(f"{arm_label} vs. Control", weight="bold", fontsize=13)
    ax.set_xlabel("Log-odds z-score", fontsize=11)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)


def main():
    questions = load_interviewer_questions()

    vectorizer = CountVectorizer(
        lowercase=True,
        token_pattern=r"(?u)\b[a-zA-Z']+\b",
        stop_words=list(ENGLISH_STOP_WORDS),
    )
    vectorizer.fit(questions["content"])

    counts_by_arm = {
        t: word_counts(questions.loc[questions["T"] == t, "content"], vectorizer)
        for t in TREATMENT_LABELS
    }
    background_counts = word_counts(questions["content"], vectorizer)

    plt.rcParams["font.family"] = "Arial"
    fig, axes = plt.subplots(1, 3, figsize=(16, 7))

    results = {}
    for ax, t in zip(axes, [1, 2, 3]):
        keyness = fightin_words(counts_by_arm[t], counts_by_arm[0], background_counts)
        results[TREATMENT_LABELS[t]] = keyness
        plot_panel(ax, keyness, TREATMENT_LABELS[t], ARM_COLORS[t])

    fig.suptitle(
        "Differential word frequency in interviewer questions, by treatment arm\n"
        "(log-odds ratio with informative Dirichlet prior; positive = more associated with arm)",
        fontsize=12,
    )
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    FIGURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURE_PATH)

    # Save full keyness tables for reference / appendix use
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for arm_label, keyness in results.items():
        fname = arm_label.lower().replace(" ", "_")
        keyness.sort_values("zscore", ascending=False).to_csv(
            OUTPUT_DIR / f"keyness_interviewer_questions_{fname}_vs_control.csv", index=False
        )


if __name__ == "__main__":
    main()
