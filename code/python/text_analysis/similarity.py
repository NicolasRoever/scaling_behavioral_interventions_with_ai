"""
How consistently does the AI word each interviewer question across interviews?

Every scripted question gets re-worded a little in each interview. This script
measures how similar those wordings are, per arm, and compares that against how
similar two *different* questions are (a baseline).

The measure has three steps, one function each:

1. TF-IDF. Turn each interviewer turn into a vector, one entry per word, weighting
   common words down (inverse document frequency) and scaling to unit length. Two
   turns are then compared with the cosine (dot product) of their vectors: 1 means
   identical wording, 0 means no shared words.

2. Within-topic similarity. For one question, average the cosine over every pair of
   its turns. That is the "same question, different interviews" number. A high value
   means the AI words that question almost the same way every time, i.e. it is
   basically templated.

3. Across-topic reference. The baseline: the average cosine between turns of
   different questions in the same arm. If step 2 sits well above this, the
   question really is templated rather than just sharing generic words.

Topics are the content-corrected question names (a turn's text is really the
previous interviewer question). Each interview is tagged with its arm from the
survey. Output goes to outputs/similarity_by_topic.{png,csv}.

Run it with:  python similarity.py
"""

import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyreadstat

PACKAGE_ROOT = Path(__file__).resolve().parents[3]
CHATS_CSV = PACKAGE_ROOT / "data/private/chats_raw.csv"
MAIN_SAV = PACKAGE_ROOT / "data/raw/main_socialmedia/main_raw.sav"
OUT = PACKAGE_ROOT / "results/figures"
OUT.mkdir(parents=True, exist_ok=True)

# Skip any question with fewer turns than this: too few pairs to average over.
MIN_TURNS_PER_TOPIC = 5

# Arms, their chart labels, and colours picked to match the paper.
ARMS = ["T1_MI_CHANGE", "T2_MI_AMBIVALENCE", "T4_CLEAR_PERSUASION", "TIME_USE"]
ARM_LABELS = {"T1_MI_CHANGE": "Change Talk", "T2_MI_AMBIVALENCE": "Decisional Balance",
              "T4_CLEAR_PERSUASION": "Direct Persuasion", "TIME_USE": "Control (Time Use)"}
ARM_COLORS = {"T1_MI_CHANGE": "#b83232", "T2_MI_AMBIVALENCE": "#777777",
              "T4_CLEAR_PERSUASION": "#4c4c86", "TIME_USE": "#bdbdbd"}

# Raw question_topic strings -> human-readable labels, for the figure's y-axis.
TOPIC_LABELS = {
    "opener": "Opening question",
    "wrap_up": "Wrap-up",
    "summary_understanding": "Summary check-in",
    "first_scaling_question": "First scaling question",
    "second_scaling_question": "Second scaling question",
    "menu_of_choices_1": "Menu of choices",
    "action_step": "Action step",
    "review_interview": "Interview review",
    # Change Talk
    "followup_past_negatives": "Follow-up: past negatives",
    "deepen_negative_impacts": "Deepen: negative impacts",
    "followup_2_past_negatives": "Follow-up 2: past negatives",
    "values_future_vision": "Values & future vision",
    "followup_first_scaling_question": "Follow-up: first scaling question",
    "dig_deeper_first_scaling_question": "Dig deeper: first scaling question",
    "followup_second_scaling_question": "Follow-up: second scaling question",
    "ability_booster_strengths": "Strengths & abilities",
    "confidence_past_success": "Confidence: past success",
    # Control (Time Use)
    "followup_morning_routine": "Follow-up: morning routine",
    "question_midday": "Midday routine",
    "question_evening": "Evening routine",
    "follow_up_evening": "Follow-up: evening routine",
    "planning_question": "Planning question",
    "question_routines": "Daily routines",
    "seasonal_variation": "Seasonal variation",
    "routine_change_wish": "Wish to change routine",
    "seasonal_variation_followup": "Follow-up: seasonal variation",
    "routine_change_followup": "Follow-up: routine change",
    "question_differences": "Weekday/weekend differences",
    "summarizing_statement": "Summary statement",
    # Decisional Balance
    "followup_past_positives": "Follow-up: past positives",
    "deepen_positives": "Deepen: positives",
    "deepen_negatives": "Deepen: negatives",
    "values_discrepancy": "Values discrepancy",
    "importance_followup_lower": "Follow-up: lower importance",
    "importance_followup_higher": "Follow-up: higher importance",
    "imagine_consequences": "Imagine consequences",
    "confidence_followup_lower": "Follow-up: lower confidence",
    "confidence_followup_higher": "Follow-up: higher confidence",
    "strengths_past_success": "Strengths & past success",
    # Direct Persuasion
    "t4_reaction_relevance": "Reaction & relevance",
    "t4_habits_map": "Habits mapping",
    "t4_direct_harms": "Direct harms",
    "t4_benefits_ask": "Perceived benefits",
    "t4_benefits_counter": "Counter benefits",
    "t4_importance_scale": "Importance scale",
    "t4_importance_to_plan": "Importance to plan",
    "t4_plan_or_benchmarks": "Plan / benchmarks",
    "t4_commitment_rule": "Commitment rule",
    "t4_enforcement": "Enforcement",
    "t4_confidence_scale2": "Confidence scale",
    "t4_confidence_strengthen": "Strengthen confidence",
    "t4_barriers_solutions": "Barriers & solutions",
    "t4_closing_summary": "Closing summary",
}


# Step 1: turns -> vectors.
def tfidf_matrix(texts):
    """
    Turn each interviewer turn into a TF-IDF vector (one row per turn).

    TF-IDF ("term frequency x inverse document frequency") gives every word a weight that is
    high when the word is used a lot in this turn but is rare across all turns, so distinctive
    words carry more weight than common filler ("the", "you", "social"). The five steps below:

      1. Tokenise each turn into lowercase words (letters/apostrophes only; punctuation and
         digits are dropped).
      2. Build the shared vocabulary - every distinct word - and give each word a fixed column.
      3. Count how often each word appears in each turn: counts[i, j] is the term frequency of
         word j in turn i.
      4. Down-weight common words by their inverse document frequency: idf = log(total turns /
         turns containing the word). The +1s smooth it so nothing divides by zero or explodes;
         a word that shows up in every turn gets idf near 1, a rare word gets a large idf.
      5. Multiply counts by idf to get the TF-IDF weights, then rescale each row to unit length.
         After that, the dot product of two rows IS their cosine similarity (1 = identical
         direction/wording, 0 = no shared words), independent of how long each turn is.
    """
    # 1. tokenise: lowercase, keep only runs of letters and apostrophes.
    tokenised = [re.findall(r"[a-z']+", str(t).lower()) for t in texts]
    # 2. vocabulary: every distinct word, each pinned to a column index.
    vocab = sorted({word for words in tokenised for word in words})
    column = {word: i for i, word in enumerate(vocab)}

    # 3. term frequency: how many times each word occurs in each turn.
    counts = np.zeros((len(texts), len(vocab)))
    for row, words in enumerate(tokenised):
        for word in words:
            counts[row, column[word]] += 1

    # 4. inverse document frequency: (counts > 0).sum(axis=0) is the number of turns each word
    #    appears in; rarer words get a larger idf.
    idf = np.log((1 + len(texts)) / (1 + (counts > 0).sum(axis=0))) + 1
    # 5. tf-idf, then L2-normalise each row so a dot product equals the cosine similarity
    #    (clip guards the divide against an empty turn with no vocabulary words).
    vectors = counts * idf
    lengths = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / np.clip(lengths, 1e-9, None)


# Step 2: how similar are turns of the same question?
def within_topic_similarity(vectors):
    """Average cosine similarity over every pair of turns that share a topic."""
    similarities = vectors @ vectors.T          # cosine of every pair; the diagonal is all 1s
    n = len(vectors)
    off_diagonal_sum = similarities.sum() - n   # subtract the n self-pairs on the diagonal
    return off_diagonal_sum / (n * n - n)       # divide by the number of genuine pairs


# Step 3: how similar are turns of different questions (the baseline)?
def across_topic_reference(topic_means, topic_sizes):
    """
    Average cosine similarity between turns of different topics.

    A handy shortcut: the average cosine between all turns of topic a and all turns
    of topic b is just mean_vector(a) . mean_vector(b). So we take the dot product of
    the topic mean vectors and average it over all topic pairs a != b, weighting each
    pair by the number of turn-pairs it stands for (size_a * size_b).
    """
    means = np.vstack(topic_means)                       # one mean vector per topic
    pair_similarity = means @ means.T                    # mean_a . mean_b for every topic pair
    pair_weight = np.outer(topic_sizes, topic_sizes)     # how many turn-pairs each stands for
    np.fill_diagonal(pair_similarity, 0.0)               # keep only the different-topic pairs
    np.fill_diagonal(pair_weight, 0.0)
    return float((pair_similarity * pair_weight).sum() / pair_weight.sum())


# Put the three steps together for one arm.
def analyse_arm(turns):
    """Return (per-topic rows in interview order, across-topic reference) for one arm."""
    vectors = tfidf_matrix(turns["content"].tolist())
    topics = turns["question_topic"].to_numpy()
    interview_position = turns.groupby("question_topic")["order"].median()

    rows, topic_means, topic_sizes = [], [], []
    for topic in pd.unique(topics):
        idx = np.where(topics == topic)[0]
        if len(idx) < MIN_TURNS_PER_TOPIC:
            continue
        block = vectors[idx]
        rows.append({"question_topic": topic,
                     "position": float(interview_position[topic]),
                     "within_cosine": within_topic_similarity(block),
                     "n": len(idx)})
        topic_means.append(block.mean(axis=0))
        topic_sizes.append(len(idx))

    reference = across_topic_reference(topic_means, topic_sizes)
    rows.sort(key=lambda r: r["position"])               # first question ends up at the top
    return rows, reference


# Load the transcripts, tag the arm, and content-correct the topic.
def load_interviewer_turns():
    chats = pd.read_csv(CHATS_CSV, dtype=str)
    chats["order"] = pd.to_numeric(chats["order"], errors="coerce")
    chats = chats.sort_values(["session_id", "order"])

    survey, _ = pyreadstat.read_sav(MAIN_SAV, usecols=["user_id", "interview_id"])
    arm_of_user = dict(zip(survey["user_id"].astype(str), survey["interview_id"]))
    chats["arm"] = chats["session_id"].str.extract(r"(\d+)$")[0].map(arm_of_user)

    turns = chats[chats["type"] == "question"].copy()
    # A turn's text is really the previous interviewer question (see the note up top).
    turns["question_topic"] = turns.groupby("session_id")["question_name"].shift(1).fillna("opener")
    return turns


# The figure, styled to sit next to the paper.
def make_figure(results, references):
    plt.rcParams.update({"font.family": "Arial", "font.size": 10})
    fig, axes = plt.subplots(2, 2, figsize=(12, 9.5))

    for ax, arm in zip(axes.ravel(), ARMS):
        rows = results[arm]
        y = np.arange(len(rows))[::-1]                   # first topic at the top
        ax.barh(y, [r["within_cosine"] for r in rows], color=ARM_COLORS[arm],
                height=0.72, zorder=3)

        ax.axvline(references[arm], color="#333333", linestyle="--", linewidth=1.1, zorder=4)
        ax.set_yticks(y)
        ax.set_yticklabels([TOPIC_LABELS.get(r["question_topic"], r["question_topic"]) for r in rows],
                           fontsize=7.5)
        ax.set_xlim(0, 1)
        ax.set_title(ARM_LABELS[arm], fontsize=12, loc="left", pad=6)
        # show the reference (different-question baseline) value next to its dashed line
        ax.text(0.98, 1.02, f"reference = {references[arm]:.2f}", transform=ax.transAxes,
                va="bottom", ha="right", fontsize=8, color="#333333")
        ax.tick_params(length=0)
        ax.grid(axis="x", color="#e8e8e8", linewidth=0.8, zorder=0)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)

    for ax in axes[1]:                                   # x-label only on the bottom row
        ax.set_xlabel("Mean cosine similarity of wording across interviews", fontsize=9)

    fig.tight_layout()
    fig.savefig(OUT / "similarity_by_topic.pdf", dpi=200, bbox_inches="tight", facecolor="white")


def main():
    turns = load_interviewer_turns()

    results, references, table = {}, {}, []
    for arm in ARMS:
        rows, reference = analyse_arm(turns[turns["arm"] == arm])
        results[arm], references[arm] = rows, reference
        for r in rows:
            table.append({"arm": ARM_LABELS[arm], **r, "reference": reference})

    pd.DataFrame(table).to_csv(OUT / "similarity_by_topic.csv", index=False)
    make_figure(results, references)


if __name__ == "__main__":
    main()
