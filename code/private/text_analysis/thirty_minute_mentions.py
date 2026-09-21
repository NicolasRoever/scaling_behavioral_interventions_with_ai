"""Regex mentions of 30 minutes / half an hour, as percentages of chats by arm.

Matches 30/thirty minutes/mins and half an/a hour (including hyphenated forms).
These are lexical mentions in social-media interviews, not a semantic check
that the speaker proposes a restriction. Before/after can overlap when a
participant mentions the duration on both sides of the first interviewer mention.
All chats with a known treatment are included, even those without a mention.
Summary tables omit the control arm; Overall still includes all eligible arms.
Posterior results report exactly 30 minutes conditional on each mention group,
excluding missing responses separately for predicted and ideal time.
Writes CSV results and a LaTeX table of chat percentages to text_analysis/outputs.
Also exports the table body to the Overleaf figures folder for inclusion in the paper.
"""
raise RuntimeError("Restricted-input source only. Raw interview data are not distributed. API execution is disabled in this $0-API replication package; use code/python/run_public.py for saved-result reproduction.")

import argparse
from pathlib import Path

import pandas as pd


def chat_measures(turns):
    turns = turns.sort_values(["session_id", "order"]).copy()
    pattern = r"\b(?:(?:30|thirty)[\s-]*(?:minutes?|mins?)|half[\s-]+(?:an?[\s-]+)?hour)\b"
    mention = turns["content"].str.contains(pattern, case=False, na=False)
    interviewer = mention & turns["type"].eq("question")
    participant = mention & turns["type"].eq("answer")
    seen_interviewer = interviewer.groupby(turns["session_id"]).cummax()
    # Speakers are disjoint, so cummax includes only earlier interviewer turns
    # whenever the current turn is a participant answer.
    return turns[["session_id", "T"]].assign(**{
        "Interviewer mentions 30 minutes / half an hour": interviewer,
        "Participant mentions 30 minutes / half an hour": participant,
        "Participant mentions before any interviewer mention, or without one": participant & ~seen_interviewer,
        "Participant mentions after an interviewer mention": participant & seen_interviewer,
    }).groupby(["session_id", "T"]).any()


def posterior_measures(people, mention_columns, outcomes, labels):
    groups = people[mention_columns].copy()
    groups["Either speaker mentions 30 minutes / half an hour"] = groups.any(axis=1)
    rows = []
    for group, mentions in groups.items():
        for outcome, column in outcomes.items():
            for arm, label in {**labels, None: "Overall"}.items():
                values = people.loc[mentions & (people["T"].eq(arm) if arm is not None else True), column].dropna()
                rows.append({"Mention group": group, "Posterior outcome": outcome,
                             "Treatment": label, "N": len(values), "N exactly 30": int(values.eq(30).sum()),
                             "Percent exactly 30": 100 * values.eq(30).mean()})
    return pd.DataFrame(rows)


def overleaf_table(percentages):
    headers = [r"\shortstack{" + label.replace(" ", r"\\") + "}" for label in percentages.columns]
    lines = [
        r"\begin{tabularx}{\textwidth}{@{}>{\raggedright\arraybackslash}X" + "r" * len(headers) + "@{}}",
        r"\toprule",
        "Chat measure & " + " & ".join(headers) + r" \\",
        r"\midrule",
    ]
    for measure, values in percentages.iterrows():
        if measure.startswith("Participant mentions before"):
            measure = r"\quad Before any interviewer mention, or without one"
        elif measure.startswith("Participant mentions after"):
            measure = r"\quad After an interviewer mention"
        cells = [f"{value:.1f}" + r"\%" if pd.notna(value) else "--" for value in values]
        lines.append(measure + " & " + " & ".join(cells) + r" \\")
        if measure.startswith("Interviewer mentions"):
            lines.append(r"\addlinespace[0.7em]")
    return "\n".join([*lines, r"\bottomrule", r"\end{tabularx}", ""])


def main(project_dir, output_dir, overleaf_dir=None):
    turns = pd.read_csv(
        project_dir / "data/raw/main_socialmedia/chats_raw.csv",
        usecols=["session_id", "type", "content", "order"],
    )
    turns["user_id_raw"] = turns["session_id"].str[11:].astype(int)
    outcomes = {"Predicted": "posterior_actual_social_min", "Ideal": "posterior_ideal_social_min"}
    survey = pd.read_stata(
        project_dir / "data/processed/main_social_media/clean_data.dta",
        columns=["user_id_raw", "T", *outcomes.values()], convert_categoricals=False,
    )
    turns = turns.merge(survey, on="user_id_raw", validate="many_to_one").dropna(subset=["T"])
    turns["order"] = pd.to_numeric(turns["order"], errors="raise")
    if turns["order"].isna().any() or turns.duplicated(["session_id", "order"]).any():
        raise ValueError("Each chat must have a unique, nonmissing turn order.")
    chats = chat_measures(turns)
    labels = {1: "Change Talk", 2: "Decisional Balance", 3: "Direct Persuasion"}
    percentages = chats.groupby("T").mean().mul(100).T.reindex(columns=labels).rename(columns=labels)
    percentages.index.name = "Chat measure"
    output_dir.mkdir(parents=True, exist_ok=True)
    chats.to_csv(output_dir / "thirty_minute_mentions_by_chat.csv")
    percentages.to_csv(output_dir / "thirty_minute_mentions_percentages.csv", float_format="%.1f")
    latex_path = output_dir / "thirty_minute_mentions_percentages.tex"
    with pd.option_context("display.max_colwidth", None):
        percentages.to_latex(
            latex_path, float_format="%.1f", na_rep="--", escape=True,
            caption="Percentage of chats mentioning 30 minutes or half an hour, by treatment arm.",
            label="tab:thirty_minute_mentions",
        )
    print(f"LaTeX table saved to {latex_path}")
    if overleaf_dir is not None:
        overleaf_dir.mkdir(parents=True, exist_ok=True)
        overleaf_path = overleaf_dir / "tab_thirty_minute_mentions.tex"
        overleaf_path.write_text(overleaf_table(percentages))
        print(f"Overleaf table saved to {overleaf_path}")
    print("Chats per arm:", chats.groupby("T").size().reindex(labels).rename(index=labels).to_dict())
    print(percentages.to_string(float_format=lambda value: f"{value:.1f}%"))
    # Aggregate mentions per person so multiple chats never duplicate a respondent.
    mention_columns = list(chats.columns[:2])
    people = chats.reset_index().merge(
        turns[["session_id", "user_id_raw"]].drop_duplicates(), on="session_id", validate="one_to_one",
    ).groupby(["user_id_raw", "T"])[mention_columns].any().reset_index()
    people = people.merge(survey, on=["user_id_raw", "T"], validate="one_to_one")
    posterior = posterior_measures(people, mention_columns, outcomes, labels)
    posterior.to_csv(output_dir / "thirty_minute_mentions_posterior.csv", index=False, float_format="%.1f")
    print("\nPosterior time = exactly 30 minutes, conditional on mention (nonmissing responses):")
    print(posterior.to_string(index=False, float_format=lambda value: f"{value:.1f}%"))


if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--overleaf-dir", type=Path,
        default=script_dir.parents[3] / "analysis_NR/6731ca401220dcd3b28dc2ec/figures",
        help="Destination for the table body included by the Overleaf paper.",
    )
    args = parser.parse_args()
    main(script_dir.parents[4], script_dir / "outputs", args.overleaf_dir)
