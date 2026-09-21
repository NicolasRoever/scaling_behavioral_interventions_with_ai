"""Plot saved aggregate similarities with the current manual question definitions."""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def arm_definitions():
    """Raw identifiers in the manual file's order; display text lives there only.

    Control's wrap_up is the final open reflection, and summarizing_statement
    is its closing message. routine_change_wish/routine_change_followup are
    different questions from seasonal variation and must not be merged with it.
    """
    return {
        "Change Talk": {
            "code": "T1_MI_CHANGE", "color": "#b83232",
            "topics": (
                "opener", "followup_past_negatives", "deepen_negative_impacts",
                "followup_2_past_negatives", "values_future_vision",
                "summary_understanding", "first_scaling_question",
                "followup_first_scaling_question", "dig_deeper_first_scaling_question",
                "second_scaling_question", "followup_second_scaling_question",
                "ability_booster_strengths", "confidence_past_success",
                "menu_of_choices_1", "action_step", "review_interview", "wrap_up",
            ),
        },
        "Decisional Balance": {
            "code": "T2_MI_AMBIVALENCE", "color": "#777777",
            "topics": (
                "opener", "followup_past_positives", "deepen_positives",
                "followup_past_negatives", "deepen_negatives", "values_discrepancy",
                "summary_understanding", "first_scaling_question",
                "importance_followup_lower", "importance_followup_higher",
                "imagine_consequences", "second_scaling_question",
                "confidence_followup_lower", "confidence_followup_higher",
                "strengths_past_success", "menu_of_choices_1", "action_step",
                "review_interview", "wrap_up",
            ),
        },
        "Direct Persuasion": {
            "code": "T4_CLEAR_PERSUASION", "color": "#4c4c86",
            "topics": (
                "opener", "t4_reaction_relevance", "t4_habits_map", "t4_direct_harms",
                "t4_benefits_ask", "t4_benefits_counter", "t4_importance_scale",
                "t4_importance_to_plan", "t4_plan_or_benchmarks", "t4_commitment_rule",
                "t4_enforcement", "t4_confidence_scale2", "t4_confidence_strengthen",
                "t4_barriers_solutions", "t4_closing_summary",
            ),
        },
        "Control (Time Use)": {
            "code": "TIME_USE", "color": "#bdbdbd",
            "topics": (
                "opener", "followup_morning_routine", "question_midday",
                "question_evening", "follow_up_evening", "planning_question",
                "question_routines", "seasonal_variation",
                "seasonal_variation_followup", "question_differences", "wrap_up",
                "summarizing_statement",
            ),
        },
    }


def question_definitions(panels, arms):
    """Attach exact manual labels/categories to each arm's raw identifiers."""
    if set(panels) != set(arms):
        raise ValueError("Manual panels and transcript arms do not match.")
    rows = []
    for arm, questions in panels.items():
        topics = arms[arm]["topics"]
        if len(topics) != len(questions) or len(set(topics)) != len(topics):
            raise ValueError(f"Update the raw-topic mapping for {arm}: manual rows changed.")
        for number, (topic, (name, categories)) in enumerate(zip(topics, questions), 1):
            assigned = (categories,) if isinstance(categories, str) else categories
            rows.append({"arm": arm, "arm_code": arms[arm]["code"],
                         "question_topic": topic, "question_number": number,
                         "question_name": name, "categories": " + ".join(assigned)})
    return pd.DataFrame(rows)


def make_figure(results, references, arms, output_path):
    """Keep the paper's four-panel style, using the exact manual row labels."""
    with plt.rc_context({"font.family": "Arial", "font.size": 10}):
        fig, axes = plt.subplots(2, 2, figsize=(12, 9.5))
        for ax, (arm, rows) in zip(axes.flat, results.items()):
            y = np.arange(len(rows))[::-1]
            ax.barh(y, [row["within_cosine"] for row in rows],
                    color=arms[arm]["color"], height=0.72, zorder=3)
            ax.axvline(references[arm], color="#333333", linestyle="--", linewidth=1.1, zorder=4)
            ax.set_yticks(y)
            ax.set_yticklabels([row["question_name"] for row in rows], fontsize=7.5)
            ax.set_xlim(0, 1)
            ax.set_title(arm, fontsize=12, loc="left", pad=6)
            ax.text(0.98, 1.02, f"reference = {references[arm]:.2f}", transform=ax.transAxes,
                    va="bottom", ha="right", fontsize=8, color="#333333")
            ax.tick_params(length=0)
            ax.grid(axis="x", color="#e8e8e8", linewidth=0.8, zorder=0)
            for side in ("top", "right", "left"):
                ax.spines[side].set_visible(False)
        for ax in axes[1]:
            ax.set_xlabel("Mean cosine similarity of wording across interviews", fontsize=9)
        fig.tight_layout()
        fig.savefig(output_path, dpi=200, bbox_inches="tight", facecolor="white")
        plt.close(fig)


def build(table, panels, output_path):
    """Validate the saved summary and render it in manual question order."""
    arms = arm_definitions()
    definitions = question_definitions(panels, arms)
    keys = ['arm', 'question_topic']
    metadata = ['arm_code', 'question_number', 'question_name', 'categories']
    required = keys + metadata + ['position', 'within_cosine', 'n', 'reference']
    if set(table.columns) != set(required) or table.duplicated(keys).any():
        raise ValueError('Invalid or duplicate similarity summary rows.')
    expected = definitions.set_index(keys).sort_index()
    observed = table.set_index(keys).sort_index()
    if not observed.index.equals(expected.index):
        raise ValueError('Saved similarity topics differ from the manual definitions.')
    for column in metadata:
        if not observed[column].eq(expected[column]).all():
            raise ValueError('Similarity metadata differs from manual definitions: ' + column)
    if not table['position'].eq(2 * table['question_number'] - 1).all():
        raise ValueError('Unexpected question positions in similarity summary.')
    if not table['n'].ge(5).all() or not table['n'].eq(table['n'].round()).all():
        raise ValueError('Similarity topic counts must be integers of at least five.')
    for column in ['within_cosine', 'reference']:
        if not table[column].between(-1e-12, 1 + 1e-12).all():
            raise ValueError('Invalid cosine value: ' + column)
    results, references = {}, {}
    for arm in panels:
        rows = table.loc[table['arm'].eq(arm)].sort_values('question_number')
        if rows['reference'].nunique() != 1:
            raise ValueError('Each arm requires one across-topic reference value.')
        results[arm] = rows.to_dict('records')
        references[arm] = rows['reference'].iloc[0]
    make_figure(results, references, arms, output_path)
