"""
Hand-coded question types for the AI interviewer, and the shares-by-arm bar chart.

The steps are:

1. Load chats_raw.csv and attach the treatment arm to every turn.
2. Fix the off-by-one in the question labels. The interview engine tags each turn
   with the next question's name, so the text you see in a turn is actually the
   previous scripted question. Shifting the name down by one recovers the question
   that was really asked; the first turn of each interview is the fixed opener.
3. Drop each question into one of the eight categories defined in CATEGORIES.
4. Write chats_raw_manual.csv (the transcripts with the arm / question_topic /
   category columns added) plus qtype_shares_manual.csv and a PDF showing how the
   question classifications unfold over the course of each interview arm.

Run it with:  python classify_manual.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import pandas as pd
import pyreadstat

from similarity import TOPIC_LABELS

PACKAGE_ROOT = Path(__file__).resolve().parents[3]
CHATS_CSV = PACKAGE_ROOT / "data/private/chats_raw.csv"
MAIN_SAV = PACKAGE_ROOT / "data/raw/main_socialmedia/main_raw.sav"
OUT = PACKAGE_ROOT / "results/figures"
OUT.mkdir(parents=True, exist_ok=True)

# The four arms we chart, plus the paper's label and colour for each (one panel per arm).
ARMS = ["T1_MI_CHANGE", "T2_MI_AMBIVALENCE", "T4_CLEAR_PERSUASION", "TIME_USE"]
ARM_LABELS = {"T1_MI_CHANGE": "Change Talk", "T2_MI_AMBIVALENCE": "Decisional Balance",
              "T4_CLEAR_PERSUASION": "Direct Persuasion", "TIME_USE": "Control (Time Use)"}
ARM_COLORS = {"T1_MI_CHANGE": "#b83232", "T2_MI_AMBIVALENCE": "#777777",
              "T4_CLEAR_PERSUASION": "#4c4c86", "TIME_USE": "#bdbdbd"}

# Which scripted questions belong to which category. Quick reminder of what each category means:
#   change-eliciting       the participant's own reasons/desire/need to cut back
#   ambivalence-balancing  both sides: benefits, what they'd miss, weighing pros and cons
#   scaling                the 0-10 rating question itself (not the "why not lower/higher" follow-ups)
#   information-provision  facts, research findings, or concrete tools/advice
#   plan-commitment        steps, rules, benchmarks, a commitment, or the strengths to follow through
#   reflective-summary     reflects/summarises the participant's social media use or their plan/
#                          commitment (or asks them to); reflecting on unrelated routines is "other"
#   opener/conclusion      the opening turn and the closing turns (wrap up / thank / end)
#   other                  neutral time-use questions (control arm) or logistics
CATEGORIES = {
    "change-eliciting": [
        "deepen_negative_impacts", "followup_2_past_negatives", "deepen_negatives",
        "values_future_vision", "values_discrepancy", "followup_first_scaling_question",
        "importance_followup_lower", "dig_deeper_first_scaling_question",
        "followup_second_scaling_question", "confidence_followup_lower",
        "confidence_past_success", "strengths_past_success", "t4_reaction_relevance",
        "t4_habits_map", "t4_direct_harms", "t4_benefits_counter", "t4_confidence_strengthen"],
    "ambivalence-balancing": [
        "followup_past_negatives", "followup_past_positives", "deepen_positives",
        "importance_followup_higher", "confidence_followup_higher", "imagine_consequences",
        "t4_benefits_ask"],
    "scaling": [
        "first_scaling_question", "second_scaling_question",
        "t4_importance_scale", "t4_confidence_scale2"],
    "information-provision": ["t4_barriers_solutions"],
    "plan-commitment": [
        "menu_of_choices_1", "action_step", "ability_booster_strengths",
        "t4_importance_to_plan", "t4_plan_or_benchmarks", "t4_commitment_rule", "t4_enforcement"],
    "reflective-summary": ["summary_understanding", "review_interview"],
    "opener/conclusion": [
        "opener", "wrap_up", "summarizing_statement", "t4_closing_summary", "last_question"],
    "other": [
        "followup_morning_routine", "question_midday", "question_evening", "follow_up_evening",
        "planning_question", "question_routines", "seasonal_variation", "seasonal_variation_followup",
        "question_differences", "routine_change_wish", "routine_change_followup",
        "surprise_day_off", "surprise_day_off_followup"],
}

# The order here fixes both the column order in the CSV and the stacking order in the chart.
CATEGORY_ORDER = list(CATEGORIES)
CATEGORY_COLORS = {"change-eliciting": "#b83232", "ambivalence-balancing": "#4f8a7b",
                   "scaling": "#8b6a9e", "information-provision": "#9a762f",
                   "plan-commitment": "#4c4c86", "reflective-summary": "#b76e8a",
                   "opener/conclusion": "#b56a45", "other": "#777777"}
CATEGORY_LABELS = {"change-eliciting": "Change-Eliciting",
                   "ambivalence-balancing": "Ambivalence-Balancing",
                   "scaling": "Scaling",
                   "information-provision": "Information Provision",
                   "plan-commitment": "Plan Commitment",
                   "reflective-summary": "Reflective Summary",
                   "opener/conclusion": "Opener/Conclusion",
                   "other": "Other"}

# Reverse lookup: question name -> its category.
CATEGORY_OF = {}
for category, question_names in CATEGORIES.items():
    for name in question_names:
        CATEGORY_OF[name] = category


def category_weights(arm, topic):
    """
    How much of one turn to credit to each category, as {category: weight}.

    Almost always a single category with weight 1. The one exception is the
    Direct-Persuasion (T4) opener: it both opens the interview and lays out the
    research, so we split it half opener/conclusion, half information-provision.
    """
    if arm == "T4_CLEAR_PERSUASION" and topic == "opener":
        return {"opener/conclusion": 0.5, "information-provision": 0.5}
    return {CATEGORY_OF.get(topic, "other"): 1.0}


def save_csv(df, path, **kw):
    """Save a CSV. If the file is open in Excel it's locked, so fall back to a '_new' copy."""
    try:
        df.to_csv(path, **kw)
        return path
    except PermissionError:
        alt = path.with_name(path.stem + "_new" + path.suffix)
        df.to_csv(alt, **kw)
        return alt


def load_and_classify():
    """Load the chats and add the arm / question_topic / category columns."""
    df = pd.read_csv(CHATS_CSV, dtype=str)
    df["order"] = pd.to_numeric(df["order"], errors="coerce")
    df = df.sort_values(["session_id", "order"]).reset_index(drop=True)

    # Arm comes from the survey file: the session id "MI-MAINEXP-<n>" gives the user
    # id <n>, which maps to an interview_id (the arm).
    sav, _ = pyreadstat.read_sav(MAIN_SAV, usecols=["user_id", "interview_id"])
    arm_of = dict(zip(sav["user_id"].astype(str), sav["interview_id"]))
    df["arm"] = df["session_id"].str.extract(r"(\d+)$")[0].map(arm_of).replace(
        {"DEFAULT": np.nan, "": np.nan})

    # Only interviewer turns get a topic. Shift the name down one to undo the off-by-one,
    # then look up the category. The T4 opener is split, so its label can be two categories
    # joined with "+".
    questions = df[df["type"] == "question"].copy()
    questions["question_topic"] = (
        questions.groupby("session_id")["question_name"].shift(1).fillna("opener"))
    questions["category"] = ["+".join(category_weights(arm, topic))
                             for arm, topic in zip(questions["arm"], questions["question_topic"])]

    df = df.merge(questions[["session_id", "order", "question_topic", "category"]],
                  on=["session_id", "order"], how="left")
    return df


def category_shares(interviewer_turns):
    """Share of each category within each arm."""
    tally = pd.DataFrame(0.0, index=ARMS, columns=CATEGORY_ORDER)
    n_turns = pd.Series(0.0, index=ARMS)
    for arm, topic in zip(interviewer_turns["arm"], interviewer_turns["question_topic"]):
        n_turns[arm] += 1
        for category, weight in category_weights(arm, topic).items():
            tally.loc[arm, category] += weight
    return tally.div(n_turns, axis=0).fillna(0)


def ordered_questions(interviewer_turns):
    """Return each arm's question topics in their typical interview order."""
    questions_by_arm = {}
    for arm in ARMS:
        arm_turns = interviewer_turns[interviewer_turns["arm"] == arm]
        median_order = (
            arm_turns.groupby("question_topic", sort=False)["order"]
            .median()
            .sort_values()
        )
        questions_by_arm[arm] = median_order.index.tolist()
    return questions_by_arm


def plot_question_sequence(interviewer_turns, out_path):
    """
    Show each arm's questions in interview order and the category assigned to each.

    Questions run from top to bottom within each panel. Each bar represents one
    scripted question; its fill and in-bar label identify its category. Questions
    assigned to two categories are split proportionally across the bar.
    """
    plt.rcParams.update({"font.family": "Arial", "font.size": 10})
    fig, axes = plt.subplots(2, 2, figsize=(12, 10.5))
    questions_by_arm = ordered_questions(interviewer_turns)

    for ax, arm in zip(axes.ravel(), ARMS):
        topics = questions_by_arm[arm]
        y = np.arange(len(topics))[::-1]  # first question at the top

        for yi, topic in zip(y, topics):
            weights = category_weights(arm, topic)
            left = 0.0
            for category, weight in weights.items():
                ax.barh(
                    yi,
                    weight,
                    left=left,
                    height=0.72,
                    color=CATEGORY_COLORS[category],
                    edgecolor="white",
                    linewidth=1.2,
                )
                left += weight

            category_text = " +\n".join(CATEGORY_LABELS[category] for category in weights)
            ax.text(
                0.5,
                yi,
                category_text,
                ha="center",
                va="center",
                color="white",
                fontsize=7.5 if len(weights) > 1 else 8.5,
                fontweight="bold",
            )

        question_labels = [
            f"{number}. {TOPIC_LABELS.get(topic, topic.replace('_', ' ').capitalize())}"
            for number, topic in enumerate(topics, start=1)
        ]
        ax.set_yticks(y)
        ax.set_yticklabels(question_labels, fontsize=8)
        ax.set_xlim(0, 1)
        ax.set_xticks([])
        ax.set_title(ARM_LABELS[arm], fontsize=12, fontweight="bold", loc="left", pad=6)
        ax.tick_params(axis="y", length=0, pad=5)
        for spine in ax.spines.values():
            spine.set_visible(False)

    legend_handles = [
        Patch(facecolor=CATEGORY_COLORS[category], label=CATEGORY_LABELS[category])
        for category in CATEGORY_ORDER
    ]
    fig.legend(
        handles=legend_handles,
        ncol=4,
        fontsize=9,
        frameon=False,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.005),
    )
    fig.tight_layout(rect=(0, 0.08, 1, 1), h_pad=2.0, w_pad=3.0)
    fig.savefig(out_path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main():
    df = load_and_classify()
    save_csv(df, OUT / "chats_raw_manual.csv", index=False)

    interviewer_turns = df[(df["type"] == "question") & df["arm"].isin(ARMS)]
    shares = category_shares(interviewer_turns)
    save_csv(shares, OUT / "qtype_shares_manual.csv")

    plot_question_sequence(interviewer_turns, OUT / "qtype_shares_manual.pdf")


if __name__ == "__main__":
    main()
