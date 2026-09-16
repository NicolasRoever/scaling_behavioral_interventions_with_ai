from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt

def configuration():
    ARMS = ["T1_MI_CHANGE", "T2_MI_AMBIVALENCE", "T4_CLEAR_PERSUASION", "TIME_USE"]
    
    ARM_LABELS = {"T1_MI_CHANGE": "Change Talk", "T2_MI_AMBIVALENCE": "Decisional Balance",
                  "T4_CLEAR_PERSUASION": "Direct Persuasion", "TIME_USE": "Control (Time Use)"}
    
    ARM_COLORS = {"T1_MI_CHANGE": "#b83232", "T2_MI_AMBIVALENCE": "#777777",
                  "T4_CLEAR_PERSUASION": "#4c4c86", "TIME_USE": "#bdbdbd"}
    
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
    return {'ARMS': ARMS, 'ARM_LABELS': ARM_LABELS, 'ARM_COLORS': ARM_COLORS, 'TOPIC_LABELS': TOPIC_LABELS}



def make_figure(results, references, out_path, config):
    ARMS, ARM_LABELS, ARM_COLORS, TOPIC_LABELS = (config[k] for k in ['ARMS', 'ARM_LABELS', 'ARM_COLORS', 'TOPIC_LABELS'])
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
    fig.savefig(out_path, dpi=200, bbox_inches="tight", facecolor="white")

def topic_labels():
    return configuration()["TOPIC_LABELS"]
