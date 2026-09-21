"""Manual question-sequence figure from the appendix protocols; no private inputs."""
import matplotlib.pyplot as plt
from matplotlib.patches import Patch


def configuration():
    panels = {
        "Change Talk": [
            ("Opening question", "Opener/Conclusion"),
            ("Follow-up: past negatives", "Change-Eliciting"),
            ("Deepen: negative impacts", "Change-Eliciting"),
            ("Follow-up 2: past negatives", "Change-Eliciting"),
            ("Values & future vision", "Change-Eliciting"),
            ("Summary check-in", "Reflective Summary"),
            ("First scaling question", "Scaling"),
            ("Follow-up: first scaling question", "Change-Eliciting"),
            ("Dig deeper: first scaling question", "Change-Eliciting"),
            ("Second scaling question", "Scaling"),
            ("Follow-up: second scaling question", "Change-Eliciting"),
            ("Strengths & abilities", "Plan Commitment"),
            ("Confidence: past success", "Change-Eliciting"),
            ("Menu of choices", "Plan Commitment"),
            ("Action step", "Plan Commitment"),
            ("Interview review", "Reflective Summary"),
            ("Wrap-up", "Opener/Conclusion"),
        ],
        "Decisional Balance": [
            ("Opening question", "Opener/Conclusion"),
            ("Follow-up: past positives", "Ambivalence-Balancing"),
            ("Deepen: positives", "Ambivalence-Balancing"),
            ("Follow-up: past negatives", "Ambivalence-Balancing"),
            ("Deepen: negatives", "Change-Eliciting"),
            ("Values discrepancy", "Change-Eliciting"),
            ("Summary check-in", "Reflective Summary"),
            ("First scaling question", "Scaling"),
            ("Follow-up: lower importance", "Change-Eliciting"),
            ("Follow-up: higher importance", "Ambivalence-Balancing"),
            ("Imagine consequences", "Ambivalence-Balancing"),
            ("Second scaling question", "Scaling"),
            ("Follow-up: lower confidence", "Change-Eliciting"),
            ("Follow-up: higher confidence", "Ambivalence-Balancing"),
            ("Strengths & past success", "Change-Eliciting"),
            ("Menu of choices", "Plan Commitment"),
            ("Action step", "Plan Commitment"),
            ("Interview review", "Reflective Summary"),
            ("Wrap-up", "Opener/Conclusion"),
        ],
        "Direct Persuasion": [
            ("Opening question", ("Opener/Conclusion", "Information Provision")),
            ("Reaction & relevance", "Change-Eliciting"),
            ("Habits mapping", "Change-Eliciting"),
            ("Direct harms", "Change-Eliciting"),
            ("Perceived benefits", "Ambivalence-Balancing"),
            ("Counter benefits", "Change-Eliciting"),
            ("Importance scale", "Scaling"),
            ("Importance to plan", "Plan Commitment"),
            ("Plan / benchmarks", "Plan Commitment"),
            ("Commitment rule", "Plan Commitment"),
            ("Enforcement", "Plan Commitment"),
            ("Confidence scale", "Scaling"),
            ("Strengthen confidence", "Change-Eliciting"),
            ("Barriers & solutions", "Information Provision"),
            ("Closing summary", "Opener/Conclusion"),
        ],
        "Control (Time Use)": [
            # Fixed opener, then appendix D.4 turns 1--11. Navigation/termination
            # messages are not additional interview questions and are not plotted.
            ("Opening question: morning routine", "Opener/Conclusion"),
            ("Follow-up on morning routine", "Other"),
            ("Midday routine", "Other"),
            ("Evening routine", "Other"),
            ("Follow-up on evening routine", "Other"),
            ("Planning", "Other"),
            ("Daily routines", "Other"),
            ("Seasonal variation", "Other"),
            ("Follow-up on seasonal variation", "Other"),
            ("Weekday versus weekend routines", "Other"),
            ("Final reflection", "Opener/Conclusion"),
            ("Closing summary", "Opener/Conclusion"),
        ],
    }
    category_colors = {
        "Change-Eliciting": "#b83232",
        "Ambivalence-Balancing": "#4f8a7b",
        "Scaling": "#8b6a9e",
        "Information Provision": "#9a762f",
        "Plan Commitment": "#4c4c86",
        "Reflective Summary": "#b76e8a",
        "Opener/Conclusion": "#b56a45",
        "Other": "#777777",
    }
    return panels, category_colors


def plot_question_sequence(panels, category_colors, out_path):
    """Draw the four panels; mixed categories get equal-width segments."""
    with plt.rc_context({"font.family": "Arial", "font.size": 10}):
        fig, axes = plt.subplots(2, 2, figsize=(12, 10.5))
        for ax, (arm, questions) in zip(axes.flat, panels.items()):
            y = list(range(len(questions)))[::-1]
            for yi, (_, categories) in zip(y, questions):
                assigned = (categories,) if isinstance(categories, str) else categories
                width = 1 / len(assigned)
                for segment, category in enumerate(assigned):
                    ax.barh(yi, width, left=segment * width, height=0.72,
                            color=category_colors[category], edgecolor="white", linewidth=1.2)
                ax.text(0.5, yi, " +\n".join(assigned), ha="center", va="center",
                        color="white", fontsize=7.5 if len(assigned) > 1 else 8.5,
                        fontweight="bold")

            ax.set_yticks(y)
            ax.set_yticklabels([f"{i}. {name}" for i, (name, _) in enumerate(questions, 1)],
                               fontsize=8)
            ax.set_xlim(0, 1)
            ax.set_xticks([])
            ax.set_title(arm, fontsize=12, fontweight="bold", loc="left", pad=6)
            ax.tick_params(axis="y", length=0, pad=5)
            for spine in ax.spines.values():
                spine.set_visible(False)

        fig.legend(handles=[Patch(facecolor=color, label=category)
                            for category, color in category_colors.items()],
                   ncol=4, fontsize=9, frameon=False, loc="lower center",
                   bbox_to_anchor=(0.5, 0.005))
        fig.tight_layout(rect=(0, 0.08, 1, 1), h_pad=2.0, w_pad=3.0)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_path, bbox_inches="tight", facecolor="white")
        plt.close(fig)
