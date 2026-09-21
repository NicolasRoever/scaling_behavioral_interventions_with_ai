"""Measure consistency of interviewer wording using saved transcripts only.

Question names, order, and functional categories come from the shared public
question_sequence.configuration(), matching source classify_manual.py PANELS. Raw transcript identifiers are linked to those ordered rows
by arm_definitions(). No API calls are made.

The logged question_name identifies the NEXT question, so each interviewer
turn is assigned the preceding question row's identifier (or 'opener'). Topics
absent from the manual classification are reported and excluded, never silently
renamed. All other turns from the affected interviews remain in the analysis.

Within each arm, fit word-level TF-IDF on the classified turns. Report the mean
cosine over distinct turn pairs for each topic, and a turn-pair-weighted mean
over different topics as the reference. Only topics with at least five turns
enter the bars and reference. The audit also includes rarer and unknown topics.

Run: python text_analysis/similarity.py
     python text_analysis/similarity.py --output /path/to/similarity_by_topic.pdf
The PDF, numeric CSV, question-audit CSV, and audit text share an output stem.
"""

raise RuntimeError("Restricted-input source only. Raw interview data are not distributed. API execution is disabled in this $0-API replication package; use code/python/run_public.py for saved-result reproduction.")

import argparse
import sys
import re
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyreadstat
from scipy.sparse import csr_matrix

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
from language_similarity import arm_definitions, question_definitions, make_figure
from question_sequence import configuration








def load_interviewer_turns(chats_csv, main_sav):
    """Read local data; recover the topic of the current text from the log."""
    chats = pd.read_csv(chats_csv, dtype=str, usecols=[
        "session_id", "order", "type", "content", "question_name"])
    chats["order"] = pd.to_numeric(chats["order"], errors="raise")
    turns = chats.loc[chats["type"].eq("question")].copy()
    turns = turns.sort_values(["session_id", "order"])
    if turns.duplicated(["session_id", "order"]).any():
        raise ValueError("Duplicate interviewer positions make topic alignment ambiguous.")
    survey, _ = pyreadstat.read_sav(main_sav, usecols=["user_id", "interview_id"])
    if survey["user_id"].duplicated().any():
        raise ValueError("Survey user IDs must be unique for the arm lookup.")
    arm_of_user = dict(zip(survey["user_id"].astype(str), survey["interview_id"]))
    turns["arm_code"] = turns["session_id"].str.extract(r"(\d+)$")[0].map(arm_of_user)
    turns["question_topic"] = turns.groupby("session_id")["question_name"].shift(1)
    first = turns.groupby("session_id").cumcount().eq(0)
    if not turns.loc[first, "order"].eq(1).all():
        raise ValueError("Some transcripts lack an opening row; topic alignment needs review.")
    turns.loc[first, "question_topic"] = "opener"
    turns["question_topic"] = turns["question_topic"].fillna("<missing identifier>")
    turns["content"] = turns["content"].fillna("")
    if turns["content"].str.strip().eq("").any():
        raise ValueError("Empty interviewer text needs review.")
    return turns


def audit_questions(turns, definitions, min_turns):
    """Compare all observed topics, including low-count topics, to manual rows."""
    observed = turns.groupby(["arm_code", "question_topic"]).agg(
        n=("content", "size"), n_sessions=("session_id", "nunique"),
        position=("order", "median")).reset_index()
    audit = definitions.merge(observed, on=["arm_code", "question_topic"],
                              how="outer", validate="one_to_one")
    code_to_arm = definitions.drop_duplicates("arm_code").set_index("arm_code")["arm"]
    audit["arm"] = audit["arm"].fillna(audit["arm_code"].map(code_to_arm))
    audit[["n", "n_sessions"]] = audit[["n", "n_sessions"]].fillna(0).astype(int)
    audit["status"] = np.select(
        [audit["question_number"].isna(), audit["n"].eq(0), audit["n"].lt(min_turns)],
        ["unclassified", "missing", "below_minimum"], default="included")
    return audit


def audit_report(turns, definitions, audit, min_turns):
    """Produce an aggregate audit without copying participant transcript content."""
    lines = ["Question classification audit", "Source: classify_manual.py PANELS",
             f"Minimum interviewer turns per plotted topic: {min_turns}", ""]
    for arm in definitions["arm"].drop_duplicates():
        block = audit.loc[audit["arm"].eq(arm)]
        expected = block["question_number"].notna().sum()
        observed = block["n"].gt(0).sum()
        arm_code = definitions.loc[definitions["arm"].eq(arm), "arm_code"].iloc[0]
        arm_turns = turns.loc[turns["arm_code"].eq(arm_code)]
        positions = arm_turns["order"].nunique()
        lines.append(f"{arm}: {expected} manual statements; {positions} observed statement "
                     f"positions; {observed} distinct topic identifiers; "
                     f"{block['status'].eq('included').sum()} plotted.")
        for row in block.loc[~block["status"].eq("included")].itertuples():
            lines.append(f"  {row.status}: {row.question_topic} "
                         f"({row.n} turns in {row.n_sessions} interviews)")
    unmatched = turns.loc[~turns["arm_code"].isin(definitions["arm_code"])]
    extras = audit.loc[audit["status"].eq("unclassified"), ["arm_code", "question_topic"]]
    excluded = turns.merge(extras, on=["arm_code", "question_topic"], how="inner")
    classified = turns.merge(definitions[["arm_code", "question_topic"]],
                             on=["arm_code", "question_topic"], how="inner")
    zero_vectors = classified.loc[~classified["content"].str.lower().str.contains(r"[a-z']")]
    lines.extend([
        "", f"Unclassified topics: {len(excluded)} turns in "
        f"{excluded['session_id'].nunique()} interviews; excluded from TF-IDF, bars, and reference.",
        "Alternative topic identifiers at the same position are not additional interview statements.",
        "Other classified turns in those interviews are retained.",
        f"No supported survey arm: {len(unmatched)} turns in "
        f"{unmatched['session_id'].nunique()} interviews; excluded (as in the original script).",
        f"No tokens under the original English-letter tokenizer: {len(zero_vectors)} turns in "
        f"{zero_vectors['session_id'].nunique()} interviews; retained as zero vectors.",
        "Self-pair removal uses actual squared vector lengths, including zero vectors.",
        "", "Names, sequence, and categories in the results CSV come directly from PANELS.",
        "Bars retain the original arm colors; functional categories are recorded in the CSV.",
    ])
    return "\n".join(lines) + "\n"


def tfidf_matrix(texts):
    """Original word tokenization, smoothed IDF, and L2 scaling, stored sparsely."""
    token_counts = [Counter(re.findall(r"[a-z']+", text.lower())) for text in texts]
    vocabulary = sorted({word for counts in token_counts for word in counts})
    columns = {word: index for index, word in enumerate(vocabulary)}
    row_ids, column_ids, values = [], [], []
    for row, counts in enumerate(token_counts):
        for word, count in counts.items():
            row_ids.append(row)
            column_ids.append(columns[word])
            values.append(count)
    counts = csr_matrix((values, (row_ids, column_ids)),
                        shape=(len(texts), len(vocabulary)), dtype=float)
    idf = np.log((1 + len(texts)) / (1 + np.asarray((counts > 0).sum(axis=0)).ravel())) + 1
    vectors = counts.multiply(idf).tocsr()
    lengths = np.sqrt(np.asarray(vectors.multiply(vectors).sum(axis=1)).ravel())
    return vectors.multiply((1 / np.clip(lengths, 1e-9, None))[:, None]).tocsr()


def within_topic_similarity(vectors):
    """Mean pairwise cosine without allocating the full turn-by-turn matrix."""
    n = vectors.shape[0]
    if n < 2:
        raise ValueError("Pairwise similarity requires at least two turns.")
    total = np.asarray(vectors.sum(axis=0)).ravel()
    diagonal = float(vectors.multiply(vectors).sum())
    return float(np.clip((total @ total - diagonal) / (n * (n - 1)), 0, 1))


def across_topic_reference(topic_means, topic_sizes):
    """Mean cosine between different topics, weighted by the number of turn pairs."""
    if len(topic_means) < 2:
        raise ValueError("The across-topic reference requires at least two topics.")
    means = np.vstack(topic_means)
    similarities = means @ means.T
    weights = np.outer(topic_sizes, topic_sizes).astype(float)
    np.fill_diagonal(weights, 0)
    return float((similarities * weights).sum() / weights.sum())


def analyse_arm(turns, definitions, min_turns):
    """Analyze classified turns and return rows in the exact manual sequence."""
    turns = turns.loc[turns["question_topic"].isin(definitions["question_topic"])]
    if turns.duplicated(["session_id", "question_topic"]).any():
        raise ValueError("Repeated topics in an interview need review before cross-interview comparison.")
    vectors = tfidf_matrix(turns["content"].tolist())
    topics = turns["question_topic"].to_numpy()
    rows, means, sizes = [], [], []
    for definition in definitions.to_dict("records"):
        indices = np.flatnonzero(topics == definition["question_topic"])
        if len(indices) < min_turns:
            continue
        positions = turns.iloc[indices]["order"]
        if not positions.eq(2 * definition["question_number"] - 1).all():
            raise ValueError(f"Unexpected transcript position for {definition['question_topic']}.")
        block = vectors[indices]
        rows.append({**definition, "position": float(positions.median()),
                     "within_cosine": within_topic_similarity(block), "n": len(indices)})
        means.append(np.asarray(block.mean(axis=0)).ravel())
        sizes.append(len(indices))
    return rows, across_topic_reference(means, sizes)





def main(panels, script_path):
    data_dir = script_path.parents[5] / "data/raw/main_socialmedia"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chats", type=Path, default=data_dir / "chats_raw.csv")
    parser.add_argument("--survey", type=Path, default=data_dir / "main_raw.sav")
    parser.add_argument("--output", type=Path,
                        default=script_path.parent / "outputs/similarity_by_topic.pdf")
    parser.add_argument("--min-turns", type=int, default=5)
    args = parser.parse_args()
    if args.min_turns < 2:
        parser.error("--min-turns must be at least 2")
    if args.output.suffix.lower() != ".pdf":
        parser.error("--output must be a PDF path")
    arms = arm_definitions()
    definitions = question_definitions(panels, arms)
    turns = load_interviewer_turns(args.chats, args.survey)
    audit = audit_questions(turns, definitions, args.min_turns)
    report = audit_report(turns, definitions, audit, args.min_turns)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    audit.to_csv(args.output.with_name(args.output.stem + "_question_audit.csv"), index=False)
    args.output.with_name(args.output.stem + "_audit.txt").write_text(report)
    print(report)

    results, references, table = {}, {}, []
    for arm in panels:
        rows, reference = analyse_arm(turns.loc[turns["arm_code"].eq(arms[arm]["code"])],
                                      definitions.loc[definitions["arm"].eq(arm)], args.min_turns)
        results[arm], references[arm] = rows, reference
        table.extend({**row, "reference": reference} for row in rows)
    pd.DataFrame(table).to_csv(args.output.with_suffix(".csv"), index=False)
    make_figure(results, references, arms, args.output)
    print(f"Saved {args.output}")


if __name__ == "__main__":
    panels, _ = configuration()
    main(panels, Path(__file__).resolve())
