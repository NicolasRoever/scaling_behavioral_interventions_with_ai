"""
Build a LaTeX table comparing the inter-rater reliability (IRR) of our LLM
MITI scoring procedure with ICC results from MITI 4.x studies.

Our row
-------
ICC(2,1), two-way random effects, absolute agreement, single-rater
reliability. The six full-corpus scoring runs (one benchmark run and five
stochastic reruns using the same model and prompt) are treated as six raters
of the same sessions. ICC is calculated separately for each MITI global
dimension; the table reports the unweighted mean and range of those four ICCs.
Dimensions must not be pooled as rated units because stable differences in
their score distributions would inflate the ICC.

The analysis is restricted to:
  * the four MITI 4.2.1 global dimensions scored by this pipeline; and
  * the Change Talk and Ambivalence treatment arms (T=1 and T=2).

Literature inclusion rule
-------------------------
The hard-coded comparison rows include only MITI 4.x studies for which a
numeric ICC result for all four global ratings, or a directly reported global
ICC summary, could be verified. Studies reporting kappa, Pearson correlation,
qualitative reliability, or only an incomplete subset of global-rating ICCs
are not placed in the compact table.

The ICC specifications remain heterogeneous. Several papers report
average-measures ICCs and use different random/mixed rater models, whereas our
primary statistic is a single-measure ICC. The table therefore supports
descriptive benchmarking, not a like-for-like meta-analysis. Where a row says
"Mean global ICC", it is the unweighted arithmetic mean of the four published
dimension-specific coefficients, not a re-estimated pooled estimate.

Literature sources checked
--------------------------
* Moyers et al. (2016), MITI 4 development paper:
  doi:10.1016/j.jsat.2016.01.001
* Kramer Schmidt et al. (2019), Danish MITI 4.2.1 reliability study:
  doi:10.1016/j.jsat.2018.11.004
* Kramer Schmidt et al. (2022), four Elderly Study rating teams:
  doi:10.1080/15332640.2020.1824838
* Frey et al. (2025), MI skills for coaching feasibility study, MITI 4.2.1:
  doi:10.1080/10474412.2025.2502332
* Jha et al. (2026), MITI 4.2 human-annotation reliability:
  doi:10.1159/000553455

Paranjothy et al. (2017) and Cohen et al. (2024) were reviewed but excluded
because they report kappa and Pearson correlations, respectively, rather than
ICC. Owens et al. (2017), Hurlocker et al. (2021), and Britt et al. (2023) were
reviewed but are not included below because a complete dimension-level numeric
set for all four global-rating ICCs could not be recovered from the accessible
primary text. This is an accessibility/inclusion constraint, not a claim that
those papers did not assess or report inter-rater reliability. The Danish
sample in Kramer Schmidt et al. (2022) overlaps the sample reported in Kramer
Schmidt et al. (2019); the later row is retained because it adds three
independent international rating teams, and the overlap is disclosed in the
table note.
"""

from pathlib import Path

import numpy as np
import pandas as pd


DIMENSIONS = [
    "Cultivating Change Talk",
    "Softening Sustain Talk",
    "Partnership",
    "Empathy",
]
SESSION_PREFIX = "MI-MAINEXP-"

ORIGINAL_PATH = "output/w2_miti_global_scores_20251222_v003.csv"
RERUN_PATHS = [f"output/robustness_rerun{i}.csv" for i in range(1, 6)]
OUT_PATH = "output/irr_comparison_table.tex"
PACKAGE_ROOT = Path(__file__).resolve().parents[3]
MIRROR_PATH = PACKAGE_ROOT / "results/tables/irr_comparison_table.tex"
CLEAN_DATA_PATH = PACKAGE_ROOT / "data/processed/main_social_media/clean_data.dta"
ARMS_TO_KEEP = {1, 2}  # T=1 Change Talk, T=2 Ambivalence


# Values below are transcribed from the cited primary sources. Displayed
# means are calculated from four published global-dimension coefficients.
LITERATURE_ROWS = [
    {
        "study": r"Moyers et al.\ (2016)",
        "description": "MITI 4.0 development study, 4 coders; four global ratings",
        "n": "50 sessions",
        # Published global ICCs: .910, .883, .868, .886; mean=.88675.
        "irr": "Mean global average-measures ICC 0.89 (range 0.87--0.91)",
    },
    {
        "study": r"Kramer Schmidt et al.\ (2019)",
        "description": "MITI 4.2.1 (Danish), 5 raters; four global ratings",
        "n": "52 sessions",
        # Published global ICCs: .80, .50, .84, .73; mean=.7175.
        "irr": (
            "Mean global consistency, average-measures ICC 0.72 "
            "(range 0.50--0.84)"
        ),
    },
    {
        "study": r"Kramer Schmidt et al.\ (2022)",
        "description": (
            "MITI 4.2.1, four international rating teams; "
            "four global ratings"
        ),
        "n": "52 / 12 / 13 / 20 sessions",
        "irr": (
            "Average-measures global ICC ranges by team: DK 0.49--0.84; "
            "Dresden 0.46--0.73; Munich 0.11--0.45; US 0.00--0.25"
        ),
    },
    {
        "study": r"Frey et al.\ (2025)",
        "description": (
            "MITI 4.2.1, independent coding team; school-based coaching"
        ),
        "n": "142 sessions; IRR subset not stated",
        "irr": "Four global-item average-measures ICCs ranged 0.85--1.00",
    },
    {
        "study": r"Jha et al.\ (2026)",
        "description": "MITI 4.2, 2 raters; model and clinical transcripts",
        "n": "100 transcripts",
        # Published global ICCs: .8651, .8623, .8648, .8957; mean=.871975.
        "irr": "Mean global two-way-random ICC 0.87 (range 0.86--0.90)",
    },
]

TABLE_NOTE = (
    r"The first row reports the reliability of our LLM-based scoring procedure, "
    r"computed separately for each MITI 4.2.1 global dimension as ICC(2,1) "
    r"(two-way random effects, absolute agreement, single-rater reliability) "
    r"across six full-corpus scoring runs and restricted to the Change Talk and "
    r"Ambivalence treatment arms. The displayed value is the unweighted mean of "
    r"the four dimension-specific ICCs; dimensions are not pooled as rated units. "
    r"Literature rows are limited to MITI 4.x studies with a verified numeric ICC "
    r"for all four global ratings or a directly reported global ICC summary. ICC "
    r"specifications are not fully harmonized: Moyers et al.\ (2016), Kramer "
    r"Schmidt et al.\ (2019, 2022), and Frey et al.\ (2025) report "
    r"average-measures ICCs, whereas the first row reports single-measure "
    r"reliability; Jha et al.\ (2026) specify a two-way random-effects ICC but do "
    r"not fully state the remaining specification. Average-measures ICCs estimate "
    r"the reliability of the mean of multiple raters and are generally higher "
    r"than single-measure ICCs. Comparisons are therefore descriptive rather than "
    r"like-for-like. For Moyers et al.\ (2016), Kramer Schmidt et al.\ (2019), "
    r"and Jha et al.\ (2026), the displayed mean is the unweighted arithmetic "
    r"mean of the four published dimension-specific coefficients, not a "
    r"re-estimated pooled coefficient. Frey et al.\ (2025) report only the range "
    r"for the four global-item ICCs. The Danish team in Kramer Schmidt et al.\ "
    r"(2022) overlaps the 2019 Danish sample; the 2022 row is included because it "
    r"also reports three additional international rating teams. N is the "
    r"inter-rater sample where stated; otherwise the total session count and the "
    r"missing IRR-subset detail are shown."
)


def load_scores(path):
    """Load, validate, and restrict one scoring run to the four global ratings."""
    df = pd.read_csv(path)
    required = {"session_id", "miti_dimension", "score", "error"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"{path} is missing required columns: {sorted(missing)}")

    error = pd.to_numeric(df["error"], errors="coerce")
    score = pd.to_numeric(df["score"], errors="coerce")

    df = df.loc[error.eq(0)].copy()
    df["score"] = score.loc[df.index]
    df = df[df["score"].between(1, 5, inclusive="both")]
    df = df[df["miti_dimension"].isin(DIMENSIONS)]

    keys = ["session_id", "miti_dimension"]
    duplicate_mask = df.duplicated(keys, keep=False)
    if duplicate_mask.any():
        duplicate_rows = df.loc[duplicate_mask, keys + ["score"]]
        conflicts = duplicate_rows.groupby(keys)["score"].nunique()
        conflicts = conflicts[conflicts > 1]
        if not conflicts.empty:
            examples = conflicts.head().index.tolist()
            raise ValueError(
                f"{path} contains conflicting duplicate scores for "
                f"session/dimension keys, e.g. {examples}"
            )
        df = df.drop_duplicates(keys, keep="first")

    return df[keys + ["score"]]


def multi_rater_icc_2_1(wide):
    """ICC(2,1): two-way random, absolute agreement, single rater."""
    if not isinstance(wide, pd.DataFrame):
        wide = pd.DataFrame(wide)

    data = wide.to_numpy(dtype=float)
    if data.ndim != 2:
        raise ValueError("ICC input must be a two-dimensional matrix.")

    n, k = data.shape
    if n < 2:
        raise ValueError("ICC requires at least two rated units.")
    if k < 2:
        raise ValueError("ICC requires at least two raters/runs.")
    if not np.isfinite(data).all():
        raise ValueError("ICC input contains missing or non-finite values.")

    mean_subjects = data.mean(axis=1)
    mean_raters = data.mean(axis=0)
    grand_mean = data.mean()

    ss_total = np.square(data - grand_mean).sum()
    ss_rows = k * np.square(mean_subjects - grand_mean).sum()
    ss_cols = n * np.square(mean_raters - grand_mean).sum()
    ss_error = ss_total - ss_rows - ss_cols
    if ss_error < 0 and np.isclose(ss_error, 0.0):
        ss_error = 0.0

    ms_rows = ss_rows / (n - 1)
    ms_cols = ss_cols / (k - 1)
    ms_error = ss_error / ((n - 1) * (k - 1))

    denominator = (
        ms_rows
        + (k - 1) * ms_error
        + k * (ms_cols - ms_error) / n
    )
    if np.isclose(denominator, 0.0):
        return np.nan
    return (ms_rows - ms_error) / denominator


def load_arm_assignment():
    """Load one unambiguous treatment-arm assignment per participant."""
    survey = pd.read_stata(CLEAN_DATA_PATH, convert_categoricals=False)
    required = {"user_id_raw", "T"}
    missing = required.difference(survey.columns)
    if missing:
        raise ValueError(
            f"{CLEAN_DATA_PATH} is missing required columns: {sorted(missing)}"
        )

    arms = survey[["user_id_raw", "T"]].dropna().copy()
    arms["user_id_raw"] = pd.to_numeric(
        arms["user_id_raw"], errors="raise"
    ).astype("int64")
    arms["T"] = pd.to_numeric(arms["T"], errors="raise")

    conflicting = arms.groupby("user_id_raw")["T"].nunique()
    conflicting = conflicting[conflicting > 1]
    if not conflicting.empty:
        raise ValueError(
            "Treatment data contain conflicting T assignments for user IDs, "
            f"e.g. {conflicting.head().index.tolist()}"
        )

    return arms.drop_duplicates("user_id_raw", keep="first")


def restrict_to_arms(df, arms, source_name="scores"):
    """Join arm labels from the survey and keep T=1 or T=2."""
    df = df.copy()
    session_ids = df["session_id"].astype(str)
    invalid = ~session_ids.str.startswith(SESSION_PREFIX)
    if invalid.any():
        examples = session_ids[invalid].head().tolist()
        raise ValueError(
            f"{source_name} contains session IDs without the expected "
            f"{SESSION_PREFIX!r} prefix, e.g. {examples}"
        )

    raw_ids = session_ids.str.replace(
        rf"^{SESSION_PREFIX}", "", regex=True
    )
    df["user_id_raw"] = pd.to_numeric(raw_ids, errors="raise").astype("int64")

    merged = df.merge(
        arms,
        on="user_id_raw",
        how="left",
        validate="many_to_one",
        indicator=True,
    )
    unmatched = merged["_merge"].ne("both")
    if unmatched.any():
        n_sessions = merged.loc[unmatched, "session_id"].nunique()
        print(
            f"Warning: dropping {unmatched.sum()} rows from {n_sessions} "
            f"sessions in {source_name} with no treatment-arm match."
        )

    merged = merged[merged["T"].isin(ARMS_TO_KEEP)].copy()
    return merged.drop(columns=["user_id_raw", "T", "_merge"])


def dimension_iccs(complete, run_cols, dimensions):
    """Calculate one ICC across runs for each global dimension."""
    results = {}
    for dimension in dimensions:
        dimension_scores = complete.loc[
            complete["miti_dimension"].eq(dimension), run_cols
        ]
        if dimension_scores.empty:
            raise ValueError(
                f"No complete observations remain for {dimension!r}."
            )
        results[dimension] = multi_rater_icc_2_1(dimension_scores)
    return results


def build_our_row():
    arms = load_arm_assignment()
    paths = [ORIGINAL_PATH, *RERUN_PATHS]
    runs = [
        restrict_to_arms(load_scores(path), arms, source_name=path)
        for path in paths
    ]

    indexed_runs = []
    for i, run in enumerate(runs):
        series = run.set_index(["session_id", "miti_dimension"])["score"]
        if not series.index.is_unique:
            raise ValueError(f"Run {paths[i]} has non-unique session/dimension keys.")
        indexed_runs.append(series.rename(f"run{i}"))

    wide = pd.concat(indexed_runs, axis=1, join="outer").reset_index()
    run_cols = [f"run{i}" for i in range(len(runs))]
    complete = wide.dropna(subset=run_cols).copy()
    n_dropped = len(wide) - len(complete)

    if complete.empty:
        raise ValueError("No complete session/dimension units remain across all runs.")

    missing_dimensions = set(DIMENSIONS).difference(complete["miti_dimension"])
    if missing_dimensions:
        raise ValueError(
            "Complete-case data are missing expected MITI global dimensions: "
            f"{sorted(missing_dimensions)}"
        )

    iccs = dimension_iccs(complete, run_cols, DIMENSIONS)
    icc_values = np.asarray(list(iccs.values()), dtype=float)
    if not np.isfinite(icc_values).all():
        raise ValueError(f"At least one dimension-specific ICC is undefined: {iccs}")

    mean_icc = icc_values.mean()
    min_icc = icc_values.min()
    max_icc = icc_values.max()
    pooled_icc = multi_rater_icc_2_1(complete[run_cols])
    n_sessions = complete["session_id"].nunique()
    dimension_counts = (
        complete["miti_dimension"].value_counts().reindex(DIMENSIONS).to_dict()
    )
    min_dimension_n = min(dimension_counts.values())
    max_dimension_n = max(dimension_counts.values())

    print(
        f"Our mean dimension-specific ICC: {mean_icc:.3f} "
        f"(range {min_icc:.3f}--{max_icc:.3f}) across {len(runs)} runs; "
        f"{n_dropped} session-dimension units dropped for incomplete runs."
    )
    print(f"Dimension-specific ICCs: {iccs}")
    print(
        f"Complete sessions by dimension: {dimension_counts}; "
        f"{n_sessions} unique sessions overall."
    )
    print(
        f"Diagnostic pooled session-dimension ICC: {pooled_icc:.3f} "
        "(not reported because pooling dimensions inflates comparability)."
    )

    return {
        "study": "This Study",
        "description": (
            "LLM MITI 4.2.1 scoring, four dimension-specific ICCs across "
            "6 runs (1 benchmark + 5 stochastic reruns), gpt-5-nano; "
            "Change Talk \\& Ambivalence arms only"
        ),
        "n": (
            f"{min_dimension_n}--{max_dimension_n} sessions per "
            "global dimension"
        ),
        "irr": (
            f"Mean global ICC(2,1) {mean_icc:.2f} "
            f"(range {min_icc:.2f}--{max_icc:.2f})"
        ),
    }


def fmt_row(row):
    fields = [row["study"], row["description"], row["n"], row["irr"]]
    return " & ".join(fields) + r" \\"


def render_latex_table(rows):
    """Render a tabular plus an explanatory note; requires booktabs."""
    lines = [
        r"\begin{tabular}{p{2.8cm} p{4.6cm} p{2.6cm} p{4.3cm}}",
        r"\toprule",
        (
            r"\textbf{Study} & \textbf{Short Description} & \textbf{N} & "
            r"\textbf{Inter-rater Reliability} \\"
        ),
        r"\midrule",
        fmt_row(rows[0]),
        r"\midrule",
    ]
    lines.extend(fmt_row(row) for row in rows[1:])
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\par\smallskip",
            r"\begin{minipage}{\linewidth}",
            r"\footnotesize\textit{Note.} " + TABLE_NOTE,
            r"\end{minipage}",
        ]
    )
    return "\n".join(lines)


def write_text(path, text):
    path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"LaTeX table saved to {path}")


def main():
    our_row = build_our_row()
    rows = [our_row, *LITERATURE_ROWS]
    tex = render_latex_table(rows)

    write_text(OUT_PATH, tex)
    try:
        write_text(MIRROR_PATH, tex)
    except OSError as exc:
        print(f"Warning: could not write mirror table to {MIRROR_PATH}: {exc}")

    print(tex)


if __name__ == "__main__":
    main()
