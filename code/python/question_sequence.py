from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from language_similarity import topic_labels

def configuration():
    ARMS = ["T1_MI_CHANGE", "T2_MI_AMBIVALENCE", "T4_CLEAR_PERSUASION", "TIME_USE"]
    
    ARM_LABELS = {"T1_MI_CHANGE": "Change Talk", "T2_MI_AMBIVALENCE": "Decisional Balance",
                  "T4_CLEAR_PERSUASION": "Direct Persuasion", "TIME_USE": "Control (Time Use)"}
    
    ARM_COLORS = {"T1_MI_CHANGE": "#b83232", "T2_MI_AMBIVALENCE": "#777777",
                  "T4_CLEAR_PERSUASION": "#4c4c86", "TIME_USE": "#bdbdbd"}
    
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
    CATEGORY_OF = {topic: category for category, topics in CATEGORIES.items() for topic in topics}
    return {'ARMS': ARMS, 'ARM_LABELS': ARM_LABELS, 'ARM_COLORS': ARM_COLORS, 'CATEGORIES': CATEGORIES, 'CATEGORY_ORDER': CATEGORY_ORDER, 'CATEGORY_COLORS': CATEGORY_COLORS, 'CATEGORY_LABELS': CATEGORY_LABELS, 'CATEGORY_OF': CATEGORY_OF}



def category_weights(arm, topic, config):
    """
    How much of one turn to credit to each category, as {category: weight}.

    Almost always a single category with weight 1. The one exception is the
    Direct-Persuasion (T4) opener: it both opens the interview and lays out the
    research, so we split it half opener/conclusion, half information-provision.
    """
    ARMS, ARM_LABELS, ARM_COLORS, CATEGORIES, CATEGORY_ORDER, CATEGORY_COLORS, CATEGORY_LABELS, CATEGORY_OF = (config[k] for k in ['ARMS', 'ARM_LABELS', 'ARM_COLORS', 'CATEGORIES', 'CATEGORY_ORDER', 'CATEGORY_COLORS', 'CATEGORY_LABELS', 'CATEGORY_OF'])
    if arm == "T4_CLEAR_PERSUASION" and topic == "opener":
        return {"opener/conclusion": 0.5, "information-provision": 0.5}
    return {CATEGORY_OF.get(topic, "other"): 1.0}

def ordered_questions(interviewer_turns, config):
    """Return each arm's question topics in their typical interview order."""
    ARMS, ARM_LABELS, ARM_COLORS, CATEGORIES, CATEGORY_ORDER, CATEGORY_COLORS, CATEGORY_LABELS, CATEGORY_OF = (config[k] for k in ['ARMS', 'ARM_LABELS', 'ARM_COLORS', 'CATEGORIES', 'CATEGORY_ORDER', 'CATEGORY_COLORS', 'CATEGORY_LABELS', 'CATEGORY_OF'])
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

def plot_question_sequence(interviewer_turns, out_path, config):
    """
    Show each arm's questions in interview order and the category assigned to each.

    Questions run from top to bottom within each panel. Each bar represents one
    scripted question; its fill and in-bar label identify its category. Questions
    assigned to two categories are split proportionally across the bar.
    """
    ARMS, ARM_LABELS, ARM_COLORS, CATEGORIES, CATEGORY_ORDER, CATEGORY_COLORS, CATEGORY_LABELS, CATEGORY_OF = (config[k] for k in ['ARMS', 'ARM_LABELS', 'ARM_COLORS', 'CATEGORIES', 'CATEGORY_ORDER', 'CATEGORY_COLORS', 'CATEGORY_LABELS', 'CATEGORY_OF'])
    plt.rcParams.update({"font.family": "Arial", "font.size": 10})
    fig, axes = plt.subplots(2, 2, figsize=(12, 10.5))
    questions_by_arm = ordered_questions(interviewer_turns, config)

    for ax, arm in zip(axes.ravel(), ARMS):
        topics = questions_by_arm[arm]
        y = np.arange(len(topics))[::-1]  # first question at the top

        for yi, topic in zip(y, topics):
            weights = category_weights(arm, topic, config)
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
            f"{number}. {topic_labels().get(topic, topic.replace('_', ' ').capitalize())}"
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
