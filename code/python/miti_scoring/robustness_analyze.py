"""
Build the robustness summary table described in robustness_notes.md.

Assumptions made explicit here (no single standard exists for these on a 1-5 MITI
global scale):
  - "Direction changed" = sign(score - 3) differs between the original and the
    comparison run. 3 is the scale's explicit default/anchor per MAIN_PROMPT.
  - "Threshold crossing" = (score >= 4) differs between runs, i.e. crossing the
    conventional "good practice" cutoff on the 1-5 global scale.
  - Both are undefined ("--") for count-type outcomes (Human validation rows).
  - ICC is ICC(2,1), two-way random effects, absolute agreement, single rater
    (Shrout & Fleiss 1979), computed manually since pingouin isn't installed.
"""

import numpy as np
import pandas as pd

DIMENSIONS = [
    "Cultivating Change Talk",
    "Softening Sustain Talk",
    "Partnership",
    "Empathy",
]
ORIGINAL_PATH = "output/w2_miti_global_scores_20251222_v003.csv"
RERUN_PATHS = [f"output/robustness_rerun{i}.csv" for i in range(1, 6)]
MODEL_SWAP_PATH = "output/robustness_model_swap.csv"
ABLATION_PATH = "output/robustness_ablation.csv"
BEHAVIORAL_VALIDATION_PATH = "output/behavioral_counts_validation_2025-11-25.csv"

# Copied from behavioral_scores_validation.ipynb so Question / Reflection Complex
# counts are derived identically to the existing human-validation analysis.
FINAL_TO_LLM = {
    'Q': 'Question', 'Q (reflection only setup)': 'Question', 'Q, CR': 'Question', 'GI Q': 'Question',
    'SR Q': 'Question', 'NC Q': 'Question', 'NC Q(ruled out SEEK)': 'Question', 'Q (Did-not-meet-the-bar-for SEEK)': 'Question',
    'SR': 'Reflection Simple', 'SR*': 'Reflection Simple', 'SR; Q': 'Reflection Simple', 'SR GI': 'Reflection Simple',
    'SR AF': 'Reflection Simple', 'SR; SEEK': 'Reflection Simple', 'SR; Q (Did-not-reach-bar-for-Seek)': 'Reflection Simple',
    'CR': 'Reflection Complex', 'CR;AF': 'Reflection Complex', 'CR (+ Emp)': 'Reflection Complex', 'CR +CULTIVATE': 'Reflection Complex',
    'CR*': 'Reflection Complex', 'CR; SEEK': 'Reflection Complex', 'SEEK;CR': 'Reflection Complex',
    'AF': 'Affirm', 'Affirm': 'Affirm', 'AFF': 'Affirm', 'AF SEEK': 'Affirm', 'AF Q': 'Affirm', 'AF Persuade': 'Affirm',
    'AFF GI': 'Affirm', 'Seek Affirm': 'Affirm', 'Seek AF': 'Affirm', 'GI Support, NC AF': 'Affirm', 'AF; Seek': 'Affirm',
    'SEEK': 'Seeking Collaboration', 'Seek': 'Seeking Collaboration', 'Seeking Collaboration': 'Seeking Collaboration', 'Seek; GI': 'Seeking Collaboration',
    'GI SEEK': 'Seeking Collaboration', 'Persuade with Seek': 'Seeking Collaboration', 'SEEK EMPHASIZE': 'Seeking Collaboration',
    'SR; SEEK': 'Seeking Collaboration', 'CR; SEEK': 'Seeking Collaboration', 'GI PWP Seek': 'Seeking Collaboration',
    'SEEK;CR': 'Seeking Collaboration', 'EmpHASIZE': 'Seeking Collaboration', 'EMP': 'Seeking Collaboration', 'Emp 1': 'Seeking Collaboration',
    'GI': 'Giving Information', 'GI;': 'Giving Information', 'GI SEEK': 'Giving Information', 'GI Support, NC AF': 'Giving Information',
    'GI PERSUADE Q': 'Giving Information', 'GI EMPHASIZE SEEK': 'Giving Information', 'GI PWP Seek': 'Giving Information',
    'GI Emphasize Seek': 'Giving Information', 'GI; SR': 'Giving Information', 'GI PERSUADE (Q is part of the Persuade)': 'Giving Information',
    'Persuade': 'Persuade', 'PERSUADE': 'Persuade', 'AF Persuade': 'Persuade', 'GI PERSUADE Q': 'Persuade',
    'GI PERSUADE (Q is part of the Persuade)': 'Persuade', 'Persuade with': 'Persuade', 'Persuade with Seek': 'Persuade',
    'PERSUADE WITH': 'Persuade', 'PERSUADE (could include a GI) Q': 'Persuade', 'Emphasize; Persuade': 'Persuade', 'AFF Persuade': 'Persuade',
    'Persuade with Permission': 'Persuade with Permission',
    'Emphasize': 'Emphasizing Autonomy', 'EMPHASIZE': 'Emphasizing Autonomy', 'Emphasizing Autonomy': 'Emphasizing Autonomy',
    'Emphasize Q': 'Emphasizing Autonomy',
    'Confront': 'Confront', 'CONFRONT': 'Confront', 'CONFRONT warn Q': 'Confront',
    'NOT CODED': '', 'NC': '', 'Structure not coded': '', 'SAME': '', '': '', 'nan': '', '""': '', None: '',
}


def icc_2_1(x, y):
    """ICC(2,1): two-way random, absolute agreement, single rater (Shrout & Fleiss 1979)."""
    data = np.column_stack([x, y]).astype(float)
    n, k = data.shape
    mean_subjects = data.mean(axis=1)
    mean_raters = data.mean(axis=0)
    grand_mean = data.mean()

    ss_total = ((data - grand_mean) ** 2).sum()
    ss_rows = k * ((mean_subjects - grand_mean) ** 2).sum()
    ss_cols = n * ((mean_raters - grand_mean) ** 2).sum()
    ss_error = ss_total - ss_rows - ss_cols

    ms_rows = ss_rows / (n - 1)
    ms_cols = ss_cols / (k - 1)
    ms_error = ss_error / ((n - 1) * (k - 1))

    denom = ms_rows + (k - 1) * ms_error + k * (ms_cols - ms_error) / n
    if denom == 0:
        return np.nan
    return (ms_rows - ms_error) / denom


def score_metrics(original, comparison, count_outcome=False):
    original = np.asarray(original, dtype=float)
    comparison = np.asarray(comparison, dtype=float)
    n = len(original)
    diff = comparison - original

    row = {
        "N": n,
        "Original mean": round(original.mean(), 2),
        "Comparison mean": round(comparison.mean(), 2),
        "Mean difference": round(diff.mean(), 2),
        "MAE": round(np.abs(diff).mean(), 2),
        "Correlation": round(np.corrcoef(original, comparison)[0, 1], 2),
        "Absolute-agreement ICC": round(icc_2_1(original, comparison), 2),
        "Exact agreement": round((original == comparison).mean(), 2),
        "Agreement within ±1": round((np.abs(diff) <= 1).mean(), 2),
    }
    if count_outcome:
        row["Direction changed"] = "—"
        row["Threshold crossing"] = "—"
    else:
        dir_orig = np.sign(original - 3)
        dir_cmp = np.sign(comparison - 3)
        row["Direction changed"] = round((dir_orig != dir_cmp).mean(), 2)
        row["Threshold crossing"] = round(((original >= 4) != (comparison >= 4)).mean(), 2)
    return row


def load_scores(path):
    df = pd.read_csv(path)
    df = df[df["error"].astype(str) == "0"]
    df = df[pd.to_numeric(df["score"], errors="coerce").between(1, 5)]
    df["score"] = df["score"].astype(float)
    return df[["session_id", "miti_dimension", "score"]]


def build_score_rows():
    original = load_scores(ORIGINAL_PATH)
    rows = []

    # Stochastic reruns: pool all 5 reruns against the original (long format)
    rerun_pairs = []
    for path in RERUN_PATHS:
        rerun = load_scores(path)
        merged = original.merge(rerun, on=["session_id", "miti_dimension"], suffixes=("_orig", "_cmp"))
        rerun_pairs.append(merged)
    rerun_pooled = pd.concat(rerun_pairs, ignore_index=True) if rerun_pairs else pd.DataFrame()

    for dim in DIMENSIONS:
        sub = rerun_pooled[rerun_pooled["miti_dimension"] == dim]
        if len(sub) == 0:
            continue
        row = {"Analysis": "Stochastic reruns", "MITI outcome": dim, "Outcome type": "Global, 1–5"}
        row.update(score_metrics(sub["score_orig"], sub["score_cmp"]))
        rows.append(row)

    for label, path in [("Different model", MODEL_SWAP_PATH), ("Prompt ablation", ABLATION_PATH)]:
        comparison = load_scores(path)
        merged = original.merge(comparison, on=["session_id", "miti_dimension"], suffixes=("_orig", "_cmp"))
        for dim in DIMENSIONS:
            sub = merged[merged["miti_dimension"] == dim]
            if len(sub) == 0:
                continue
            row = {"Analysis": label, "MITI outcome": dim, "Outcome type": "Global, 1–5"}
            row.update(score_metrics(sub["score_orig"], sub["score_cmp"]))
            rows.append(row)

    return rows


def build_human_validation_rows():
    df = pd.read_csv(BEHAVIORAL_VALIDATION_PATH, low_memory=False)
    df["llm_category"] = df["llm_category"].astype(str).str.replace('"', '')
    df["human_category"] = df["Final_Code"].map(FINAL_TO_LLM).fillna("")
    df["llm_category"] = df["llm_category"].replace(["", '""', "nan"], "")

    behaviors = {"Questions": "Question", "Complex reflections": "Reflection Complex"}
    human_counts = (
        df.groupby(["source_pdf", "human_category"]).size().unstack(fill_value=0)
    )
    llm_counts = (
        df.groupby(["source_pdf", "llm_category"]).size().unstack(fill_value=0)
    )

    rows = []
    for label, category in behaviors.items():
        h = human_counts[category] if category in human_counts.columns else pd.Series(0, index=human_counts.index)
        l = llm_counts[category] if category in llm_counts.columns else pd.Series(0, index=llm_counts.index)
        aligned = pd.concat([h, l], axis=1, keys=["human", "llm"]).fillna(0)
        row = {"Analysis": "Human validation", "MITI outcome": label, "Outcome type": "Count"}
        row.update(score_metrics(aligned["human"], aligned["llm"], count_outcome=True))
        rows.append(row)
    return rows


def main():
    rows = build_score_rows() + build_human_validation_rows()
    columns = [
        "Analysis", "MITI outcome", "Outcome type", "N", "Original mean", "Comparison mean",
        "Mean difference", "MAE", "Correlation", "Absolute-agreement ICC", "Exact agreement",
        "Agreement within ±1", "Direction changed", "Threshold crossing",
    ]
    table = pd.DataFrame(rows)[columns]
    table.to_csv("output/robustness_summary_table.csv", index=False)
    with open("output/robustness_summary_table.md", "w") as f:
        f.write(table.to_markdown(index=False))
    print(table.to_markdown(index=False))


if __name__ == "__main__":
    main()
