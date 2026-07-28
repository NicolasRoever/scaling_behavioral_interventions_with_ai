# Precompile the pattern to find any \roever{var}{old_value}
import re
import textwrap
from pathlib import Path
import pickle
from typing import Iterable
import ast

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy import stats
import numpy as np
from collections import Counter
import statsmodels.formula.api as smf


def calculate_mannwhitneyu_pvalue(df, ordinal_variable, alternative="two-sided"):
    assert "sonia_treatment" in df.columns, df.columns

    # Split samples
    x0 = df.loc[df["sonia_treatment"] == 0, ordinal_variable].dropna()
    x1 = df.loc[df["sonia_treatment"] == 1, ordinal_variable].dropna()

    # Mann–Whitney U test (two-sided)
    u_stat, p_value = stats.mannwhitneyu(x0, x1, alternative=alternative)

    return round(p_value, 2)


def fix_pandas_append_error():
    # Fix pandas append error
    if not hasattr(pd.DataFrame, "append"):

        def _append(self, other, ignore_index=False, sort=False):
            return pd.concat([self, other], ignore_index=ignore_index, sort=sort)

        pd.DataFrame.append = _append


def wrap_labels(labels, width=25):
    """Wrap category labels to multiple lines."""
    return [textwrap.fill(str(l), width) for l in labels]


def paper_topic_merge_specs():
    """Return the manual topic merges used in the main-text figure."""
    return [
        (12, [12, 16, 27, 14], "Confirmatory Statement"),
        (3, [3, 8], "Confidence in Changing Social Media Use"),
    ]


def paper_unstable_topic_labels(stability_summary: pd.DataFrame) -> frozenset[str]:
    """Return unstable displayed-topic labels from the stability summary."""
    required_columns = {"topic_label", "stable"}
    missing_columns = required_columns - set(stability_summary.columns)
    if missing_columns:
        raise ValueError(
            "Topic-stability summary is missing columns: "
            + ", ".join(sorted(missing_columns))
        )
    stable = stability_summary["stable"]
    if stable.dtype != bool:
        stable = stable.astype(str).str.lower().map({"true": True, "false": False})
    if stable.isna().any():
        raise ValueError("Topic-stability summary contains invalid stable values")
    return frozenset(stability_summary.loc[~stable, "topic_label"])


def apply_paper_topic_merges(df: pd.DataFrame) -> pd.DataFrame:
    """Return topic data with the manual merges used in the main-text figure."""
    merged = df.copy()
    for new_id, old_ids, new_label in paper_topic_merge_specs():
        mask = merged["topic_id"].isin(old_ids)
        merged.loc[mask, "topic_id"] = new_id
        merged.loc[mask, "topic_label"] = new_label
    return merged


def paper_topic_label_map(df: pd.DataFrame) -> dict:
    """Map every original topic ID to the label displayed in the paper."""
    label_map = dict(zip(df["topic_id"], df["topic_label"]))
    return {
        topic_id: next(
            (
                label
                for _, topic_ids, label in paper_topic_merge_specs()
                if topic_id in topic_ids
            ),
            original_label,
        )
        for topic_id, original_label in label_map.items()
    }


def inject_values(tex_path: Path, **variables):
    """Reads a .tex file, finds all \roever{var}{...} placeholders,
    replaces the ... with the provided variables[var], and writes back.

    Parameters:
    - tex_path: pathlib.Path to the .tex file
    - variables: kwargs mapping var names to their replacement values

    Raises:
    - KeyError: if a var placeholder isn't found or if any remain afterward
    """
    path = Path(tex_path)
    content = path.read_text(encoding="utf-8")
    ROEVER_PATTERN = re.compile(r"\\roever\{(?P<var>\w+)\}\{[^}]*\}")

    # Replace each variable's placeholder via regex substitution
    for var, val in variables.items():
        pattern = re.compile(rf"\\roever\{{{var}\}}\{{[^}}]*\}}")
        replacement = rf"\\roever{{{var}}}{{{val}}}"
        content, count = pattern.subn(replacement, content)
        # if count == 0:
        #     raise KeyError(
        #         f"No placeholder \\roever{{{var}}}{{...}} found in {tex_path}"
        #     )

    # Check for any unreplaced placeholders
    # leftovers = ROEVER_PATTERN.findall(content)
    # if leftovers:
    #    raise KeyError(f"Unreplaced placeholders remain for variables: {set(leftovers)}")

    # Write the updated content back to the file
    path.write_text(content, encoding="utf-8")


# --- Helper functions -----------------------------------------------------
def mean_ttest(var, df):
    """Return (mean_treat, mean_control, pvalue) for a numeric variable."""
    x_t = df.loc[df["research_arm"] == "sonia", var].dropna()
    x_c = df.loc[df["research_arm"] == "webapp", var].dropna()
    # t-test
    tstat, pval = stats.ttest_ind(x_t, x_c, equal_var=False, nan_policy="omit")
    return x_t.mean(), x_c.mean(), pval


def set_plot_theme():
    # base seaborn theme & palette
    sns.set_theme(
        style="white",  # consistent with file_context_0        # or your own list of colors
        font="Arial",  # consistent with file_context_0
        font_scale=1.3,  # Increased font scale for larger text
    )

    palette = ["#800000", "#1a476f", "#bdbdbd", "#5f8f8b", "#f39b7f"]
    sns.set_palette(palette=palette, n_colors=5)

    # tweak matplotlib rcParams you care about
    plt.rcParams.update(
        {
            "text.usetex": False,  # consistent with file_context_0
            #"axes.titlesize": 18,  # Increased title size
            #"axes.labelsize": 16,  # Increased label size
            "legend.frameon": False,
            "figure.figsize": (8, 5),
            "lines.linewidth": 2,
            "lines.markersize": 6,
            "axes.grid": False,  # Disable grid
            # …any other defaults…
        }
    )


def finalize_plot(ax=None, fontsize=10):
    if ax is None:
        ax = plt.gca()

    sns.despine(ax=ax)

    # Set x-axis tick label font size
    ax.tick_params(axis="x", labelsize=fontsize)

    # Set legend font size (if legend exists)
    legend = ax.get_legend()
    if legend is not None:
        legend.get_frame().set_facecolor("white")

    ax.figure.tight_layout()


def validate_column_range(
    col: pd.Series, min_val: float = -1000, max_val: float = 1000
) -> None:
    """Checks that all non-NaN values in the Series `col` lie between `min_val` and `max_val` (inclusive).
    NaNs are ignored. Raises a ValueError if any non-NaN value is outside this range.

    Parameters
    ----------
    col : pd.Series
        The column to validate.
    min_val : float
        Minimum allowable value (default: -1000).
    max_val : float
        Maximum allowable value (default: 1000).

    Raises:
    ------
    ValueError
        If any non-NaN value in `col` is < min_val or > max_val.
    """
    # Mask of entries that are non-NaN but out of range
    out_of_range_mask = col.notna() & ~col.between(min_val, max_val, inclusive="both")

    if out_of_range_mask.any():
        bad_vals = col.loc[out_of_range_mask].unique()
        sample = bad_vals[:10].tolist()
        ellipsis = "…" if len(bad_vals) > 10 else ""
        raise ValueError(
            f"Column contains values outside [{min_val}, {max_val}]: {sample}{ellipsis}"
        )

    def plot_missing_heatmap(df, figsize=(10, 6)):
        """Plot a heatmap showing missing values in a DataFrame.

        Parameters
        ----------
        df : pandas.DataFrame
            Input dataframe.
        figsize : tuple
            Size of the matplotlib figure.
        """
        plt.figure(figsize=figsize)
        sns.heatmap(df.isnull(), cbar=False)
        plt.title("Missing Values Heatmap")
        plt.xlabel("Columns")
        plt.ylabel("Rows")
        plt.show()


def _path_for_key(base_path: Path, key: str) -> Path:
    """
    Construct the file path where a regression with the given key is stored.
    """
    return base_path / f"{key}.pkl"


def save_regression_result(base_path: Path, key: str, result) -> Path:
    """
    Save (or overwrite) a statsmodels result under `key` inside `base_path`.

    Parameters
    ----------
    base_path : Path
        Root directory under which regression results are stored.
    key : str
        Name of the regression result.
    result :
        A picklable regression object (statsmodels result) to save.
    """
    base_path.mkdir(parents=True, exist_ok=True)
    path = _path_for_key(base_path, key)
    with path.open("wb") as f:
        pickle.dump(result, f)
    return path


def load_regression_result(path):
    """
    Load a regression result that was saved under `key` in `base_path`.

    Raises
    ------
    KeyError if the file does not exist.
    """
    if not path.exists():
        raise KeyError(f"No regression saved at {path}")
    with path.open("rb") as f:
        return pickle.load(f)


def list_results(base_path: Path) -> list[str]:
    """
    Return a sorted list of regression keys available in `base_path`.
    """
    if not base_path.exists():
        return []
    return sorted(p.stem for p in base_path.glob("*.pkl"))


def load_topic_model_documents(proj_dir: str):
    """
    Load and filter the interview-response corpus used for BERTopic
    topic modeling: answers of at least 10 characters from non-control
    treatment arms, merged with each respondent's treatment assignment.

    Mirrors the loading/filtering logic in classify_bertopic.py so both
    the original pipeline and any robustness/stability analysis operate
    on an identical corpus.

    Parameters
    ----------
    proj_dir : str
        Project root containing data/raw/main_socialmedia/chats_raw.csv
        and data/processed/main_social_media/clean_data.dta.

    Returns
    -------
    docs : list[str]
        Filtered response texts, in corpus order.
    doc_idx : list[int]
        Row indices into `data` (the merged scripts+survey frame)
        corresponding to each entry in `docs`.
    data : pd.DataFrame
        The full merged scripts+survey frame (pre-filtering), for
        downstream joins (e.g. user_id_raw, treatment, T).
    """
    scripts = pd.read_csv(
        proj_dir + "/data/raw/main_socialmedia/chats_raw.csv",
        usecols=["session_id", "type", "content", "question_name", "order"],
    )
    scripts = scripts.dropna(subset="content", how="any")
    scripts["user_id_raw"] = scripts["session_id"].str[11:].astype(int)

    survey = pd.read_stata(
        proj_dir + "/data/processed/main_social_media/clean_data.dta",
        convert_categoricals=False,
    )
    data = scripts.merge(survey[["user_id_raw", "T"]], on=["user_id_raw"], how="left")
    data = data.dropna(subset="T")
    del data["session_id"]
    data["T"] = data["T"].astype(int)
    treatments = {0: "Control", 1: "Change Talk", 2: "Ambivalence", 3: "Direct persuasion"}
    data["treatment"] = data["T"].map(treatments)

    mask = (
        (data["type"] == "answer")
        & (data["content"].str.len() >= 10)
        & (data["treatment"] != "Control")
    )
    docs = data.loc[mask, "content"].tolist()
    doc_idx = data.loc[mask].index.tolist()

    return docs, doc_idx, data


def jaccard(a: set, b: set) -> float:
    """Jaccard similarity between two keyword sets (0 if either is empty)."""
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def top_keywords(topic_model, topic_id, n=10):
    """Top-n c-TF-IDF keywords for a BERTopic topic, as a set."""
    return {w for w, _ in topic_model.get_topic(topic_id)[:n]}


def best_jaccard_matches(keywords_a: dict, keywords_b: dict) -> pd.DataFrame:
    """
    For each topic in `keywords_a`, find its best-matching topic in
    `keywords_b` by keyword Jaccard overlap. Used to re-identify "the same"
    topic across two separate BERTopic fits, since topic ids are not
    stable across runs (different seeds, corpora, or library versions).

    Parameters
    ----------
    keywords_a, keywords_b : dict[int topic_id -> set[str] keywords]

    Returns
    -------
    pd.DataFrame with columns topic_a, best_match_topic_b, jaccard,
    sorted by jaccard descending.
    """
    rows = []
    for tid_a, kw_a in keywords_a.items():
        best_b, best_score = None, -1.0
        for tid_b, kw_b in keywords_b.items():
            score = jaccard(kw_a, kw_b)
            if score > best_score:
                best_b, best_score = tid_b, score
        rows.append(dict(topic_a=tid_a, best_match_topic_b=best_b, jaccard=best_score))
    return pd.DataFrame(rows).sort_values("jaccard", ascending=False)


def plot_distribution_categorical(df, col):
    set_plot_theme()

    # Count categories
    counts = df[col].value_counts(dropna=False)
    total = counts.sum()

    # Wrap labels before plotting
    wrapped_index = wrap_labels(counts.index)

    # Plot
    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.barh(
        wrapped_index,
        counts.values,
        color=plt.rcParams["axes.prop_cycle"].by_key()["color"][0],
    )

    ax.set_xlabel("Count")
    ax.tick_params(axis="y", labelsize=11)

    # Dynamic right-hand offset relative to max value (2% of range)
    xmax = counts.max()
    offset = 0.02 * xmax

    # Add percentages next to bars
    for bar, count in zip(bars, counts.values, strict=False):
        pct = 100 * count / total
        x = bar.get_width()
        y = bar.get_y() + bar.get_height() / 2
        ax.text(
            x + offset,
            y,
            f"{pct:.1f}\\%",
            va="center",
            ha="left",
            fontsize=11,
        )

    # Add right margin to ensure labels never get clipped
    ax.set_xlim(0, xmax * 1.12)

    finalize_plot(ax=ax)
    plt.close()
    return fig


def plot_distribution_categorical_split(
    df, col, split_col, legend_labels=None, show_percent=True
):
    """
    Horizontal grouped bar chart:
    - Categories of `col` on y-axis
    - Split into side-by-side bars by `split_col`
    - Optional custom legend labels
    - Percentages printed next to each bar (within each split group)
    """

    set_plot_theme()

    # Count combinations
    counts = df[[col, split_col]].dropna().value_counts().rename("count").reset_index()

    # Pivot to table: rows = categories of `col`, columns = values of `split_col`
    table = counts.pivot(index=col, columns=split_col, values="count").fillna(0)

    # Wrap y-axis labels
    wrapped_index = wrap_labels(table.index)

    n_main = len(table)  # number of categories (rows)
    n_split = len(table.columns)  # number of split groups (columns)

    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

    fig, ax = plt.subplots(figsize=(8, 6))

    # Bar spacing parameters
    group_height = 0.8
    bar_height = group_height / n_split
    y_positions = np.arange(n_main)

    # -------- COLUMN-WISE PERCENTAGES (within each split group) --------
    col_totals = table.sum(axis=0).replace(0, np.nan)
    pct_table = table.div(col_totals, axis=1)

    # Plot bars
    for i, split_cat in enumerate(table.columns):
        values = table[split_cat].values
        pct_values = pct_table[split_cat].values

        ypos = y_positions - group_height / 2 + i * bar_height + bar_height / 2

        ax.barh(
            ypos,
            values,
            height=bar_height,
            label=(
                legend_labels.get(split_cat, split_cat) if legend_labels else split_cat
            ),
            color=colors[i % len(colors)],
        )

        # Add percentages (if available)
        if show_percent:
            for x, y, pct in zip(values, ypos, pct_values, strict=False):
                if not np.isnan(pct):
                    ax.text(
                        x + 0.01 * table.values.max(),
                        y,
                        f"{pct*100:.1f}\\%",
                        va="center",
                        fontsize=10,
                    )

    # Y-axis labels
    ax.set_yticks(y_positions)
    ax.set_yticklabels(wrapped_index)
    ax.set_xlabel("Count")

    # Legend without frame/title
    ax.legend(title=None, frameon=False, fontsize=12)

    # Add right margin so labels don't overlap
    ax.set_xlim(0, table.values.max() * 1.15)

    finalize_plot(ax=ax)
    plt.close(fig)
    return fig


def plot_histogram(
    df,
    column,
    bins=10,
    xlabel=None,
    split_by=None,
    labels=None,
    alpha=0.6,
    add_density_lines=True,
    kde_bw=None,
    kde_points=300,
    density_linewidth=2.0,
    density_linestyle="-",
):
    """
    General-purpose histogram helper.

    - Sets plot theme
    - Drops missing values
    - Computes mean + median (overall; and per-group if split_by is used)
    - Plots histogram with your style
    - Writes mean & median on the plot (overall; and per-group if split_by is used)
    - (Optional) overlays KDE "density fit" lines for each group when split_by is used
    - Returns {"mean": ..., "median": ...} (or per-group dict if split_by is used)

    Parameters
    ----------
    split_by : str or None
        Column name to split into two groups and overlay two histograms.
        If None, behaves exactly like the original function.
    labels : tuple/list of length 2 or None
        Legend labels for the two groups (in the same order as the two group values).
        If None, uses the split values as labels.
    alpha : float
        Transparency for overlaid histograms when split_by is used.
    add_density_lines : bool
        If True and split_by is used, overlays KDE lines scaled to histogram counts.
    kde_bw : str | float | callable | None
        Passed to scipy.stats.gaussian_kde(bw_method=...).
    kde_points : int
        Number of x points for KDE line.
    """

    import numpy as np

    # Theme
    set_plot_theme()

    fig, ax = plt.subplots(figsize=(7, 5))
    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    primary = colors[0]

    if split_by is None:
        # Data
        d = df[column].dropna()

        # Stats
        mean_val = d.mean()
        median_val = d.median()

        # Plot
        ax.hist(d, bins=bins, color=primary)

        # Labels
        ax.set_xlabel(xlabel if xlabel is not None else column)
        ax.set_ylabel("Count")

        # Mean & median text
        textstr = f"Mean: {mean_val:.2f}\nMedian: {median_val:.2f}"
        ax.text(
            0.97,
            0.97,
            textstr,
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=10,
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.7),
        )

        finalize_plot(ax=ax)
        return fig

    # -------------------------
    # Split-by: two histograms
    # -------------------------
    d = df[[column, split_by]].dropna()

    # Determine the two groups (most frequent two levels)
    group_counts = d[split_by].value_counts(dropna=True)
    group_vals = list(group_counts.index[:2])

    if len(group_vals) < 2:
        # Fallback: plot single histogram (keeps function usable)
        d1 = d[column]
        mean_val = d1.mean()
        median_val = d1.median()

        ax.hist(d1, bins=bins, color=primary)
        ax.set_xlabel(xlabel if xlabel is not None else column)
        ax.set_ylabel("Count")

        textstr = f"Mean: {mean_val:.2f}\nMedian: {median_val:.2f}"
        ax.text(
            0.97,
            0.97,
            textstr,
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=10,
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.7),
        )

        finalize_plot(ax=ax)
        return fig

    g0, g1 = group_vals[0], group_vals[1]
    d0 = d.loc[d[split_by] == g0, column]
    d1 = d.loc[d[split_by] == g1, column]

    # Stats per group
    stats = {
        g0: {
            "mean": float(d0.mean()),
            "median": float(d0.median()),
            "n": int(d0.shape[0]),
        },
        g1: {
            "mean": float(d1.mean()),
            "median": float(d1.median()),
            "n": int(d1.shape[0]),
        },
    }

    c0 = colors[0]
    c1 = colors[1] if len(colors) > 1 else primary

    # Overlaid histograms (counts)
    ax.hist(d0, bins=bins, color=c0, alpha=alpha)
    ax.hist(d1, bins=bins, color=c1, alpha=alpha)

    # Labels + legend
    ax.set_xlabel(xlabel if xlabel is not None else column)
    ax.set_ylabel("Count")

    if labels is None:
        label0, label1 = str(g0), str(g1)
    else:
        label0, label1 = labels[0], labels[1]

    ax.legend([label0, label1], frameon=True)

    # Optional KDE "density fit" lines (scaled to counts)
    if add_density_lines:
        try:
            from scipy.stats import gaussian_kde

            # Determine bin width for scaling KDE -> counts
            # If bins is an array of edges, use its spacing; else infer from hist output
            if hasattr(bins, "__len__") and not isinstance(bins, (str, bytes)):
                bin_edges = np.asarray(bins, dtype=float)
            else:
                # Create edges spanning the pooled data for consistent scaling
                pooled = pd.concat([d0, d1]).astype(float)
                bin_edges = np.histogram_bin_edges(pooled, bins=bins)

            bin_width = float(np.median(np.diff(bin_edges)))
            x_min = float(bin_edges[0])
            x_max = float(bin_edges[-1])
            x_grid = np.linspace(x_min, x_max, int(kde_points))

            def _plot_kde(series, color, n):
                vals = series.astype(float).to_numpy()
                vals = vals[np.isfinite(vals)]
                if vals.size < 2:
                    return
                kde = gaussian_kde(vals, bw_method=kde_bw)
                y = (
                    kde(x_grid) * n * bin_width
                )  # scale density to expected counts per bin
                ax.plot(
                    x_grid,
                    y,
                    color=color,
                    linewidth=density_linewidth,
                    linestyle=density_linestyle,
                )

            _plot_kde(d0, c0, stats[g0]["n"])
            _plot_kde(d1, c1, stats[g1]["n"])

        except Exception:
            # If scipy isn't available or KDE fails, just skip lines gracefully
            pass

    # Mean/median text (both groups)
    textstr = (
        f"{label0} (n={stats[g0]['n']}): Mean {stats[g0]['mean']:.2f}, Median {stats[g0]['median']:.2f}\n"
        f"{label1} (n={stats[g1]['n']}): Mean {stats[g1]['mean']:.2f}, Median {stats[g1]['median']:.2f}"
    )
    ax.text(
        0.97,
        0.97,
        textstr,
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=10,
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.7),
    )

    finalize_plot(ax=ax)
    return fig


def _to_list(val):
    """Normalize a cell value to a list of categories."""
    # Missing
    if pd.isna(val):
        return []

    # Already list/tuple/set
    if isinstance(val, (list, tuple, set)):
        return list(val)

    # Strings
    if isinstance(val, str):
        s = val.strip()
        if s == "" or s.lower() in {"nan", "none"}:
            return []

        # Looks like a Python list: '["a", "b"]'
        if s.startswith("[") and s.endswith("]"):
            try:
                parsed = ast.literal_eval(s)
                if isinstance(parsed, (list, tuple, set)):
                    return list(parsed)
                return [parsed]
            except (ValueError, SyntaxError):
                # Fallback: split by comma
                return [x.strip() for x in s.strip("[]").split(",") if x.strip()]

        # Otherwise, maybe comma-separated string: "a, b"
        if "," in s:
            return [x.strip() for x in s.split(",") if x.strip()]

        # Just a single string
        return [s]

    # Any other scalar type
    return [val]


def plot_category_counts(
    df,
    column_name,
    title="Count of Each Theme Across All Rows",  # kept for backwards compatibility, not used
    count_limit=5,
    research_arm_col=None,
):
    """
    Plots category counts from a column whose cells are lists or strings
    that represent lists / multiple categories.

    If research_arm_col is provided, bars are side-by-side by research arm.
    """
    set_plot_theme()

    if research_arm_col is None:
        all_cats = []
        for val in df[column_name]:
            all_cats.extend(_to_list(val))

        counts = Counter(all_cats)
        # Filter categories by total count
        filtered = {cat: c for cat, c in counts.items() if c > count_limit}

        if not filtered:
            print("No categories above count_limit.")
            return None

        sorted_items = sorted(filtered.items(), key=lambda x: x[1], reverse=True)
        categories, values = zip(*sorted_items)

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.barh(categories, values)

        ax.set_xlabel("Count")
        ax.set_ylabel("")

        finalize_plot(ax=ax)
        return fig


def run_main_waitlist_model(df, y_var, baseline_var):
    """
    Runs an OLS regression of y_var on treatment, baseline, and fixed controls,
    returning a HC3-robust statsmodels result object.

    Parameters
    ----------
    df : pandas.DataFrame
    y_var : str
        Dependent variable, e.g. "gad7_score_std_w3"
    baseline_var : str
        Baseline score variable, e.g. "gad7_score_std_w1"
    """

    controls = [
        "sonia_treatment",
        baseline_var,
        "therapy_history_w1",
        "efficacy_human_therapy_w2",
        # add more controls here if needed, once
    ]

    formula = f"{y_var} ~ " + " + ".join(controls)
    model = smf.ols(formula=formula, data=df).fit(cov_type="HC3")
    return model


def plot_treatment_effects_from_coefs(
    x,
    coefs1,
    ses1,
    coefs2=None,
    ses2=None,
    error_mult: float = 1.96,  # 1.0 = ±1 SE; 1.96 ≈ 95% CI
    offset: float = 0.25,  # horizontal dodge if two series
    labels=None,  # x-tick labels; if None, uses x
    ylabel: str = "Treatment Effect",
    series1_label: str = "Series 1",
    series2_label: str = "Series 2",
):
    """
    Plot 1 or 2 time series of treatment effects with standard error bars.

    Parameters
    ----------
    x : array-like
        Positions on the x-axis (e.g., [0, 7, 14]).
    coefs1 : array-like
        Point estimates for the first series.
    ses1 : array-like
        Standard errors for the first series.
    coefs2 : array-like, optional
        Point estimates for the second series (or None to omit).
    ses2 : array-like, optional
        Standard errors for the second series (must match coefs2 if given).
    error_mult : float
        Multiplier for standard errors (1.0 = ±1 SE; 1.96 ≈ 95% CI).
    offset : float
        Horizontal offset applied when plotting two series:
        first series at x - offset, second at x + offset.
        Ignored if only one series is plotted.
    labels : list of str, optional
        Tick labels for x-axis; if None, uses `x` values.
    ylabel : str
        Y-axis label.
    series1_label : str
        Legend label for the first series.
    series2_label : str
        Legend label for the second series (if plotted).

    Returns
    -------
    fig : matplotlib.figure.Figure
    """

    set_plot_theme()

    x = np.asarray(x)
    coefs1 = np.asarray(coefs1)
    ses1 = np.asarray(ses1)

    if coefs1.shape != x.shape or ses1.shape != x.shape:
        raise ValueError("x, coefs1, and ses1 must have the same shape.")

    has_second = coefs2 is not None and ses2 is not None

    if has_second:
        coefs2 = np.asarray(coefs2)
        ses2 = np.asarray(ses2)
        if coefs2.shape != x.shape or ses2.shape != x.shape:
            raise ValueError("x, coefs2, and ses2 must have the same shape.")

    # X positions for plotting
    if has_second:
        x1 = x - offset
        x2 = x + offset
    else:
        x1 = x
        x2 = None

    # Colors from current theme
    color_cycle = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    c1 = color_cycle[0]  # primary
    c2 = color_cycle[1] if len(color_cycle) > 1 else "C1"

    fig, ax = plt.subplots(figsize=(7, 5))

    # Zero line
    ax.axhline(0, color="grey", linewidth=1, linestyle="--", alpha=0.7)

    # --- Series 1 ---
    ax.plot(x1, coefs1, color=c1, marker="o", label=series1_label)
    ax.errorbar(
        x1,
        coefs1,
        yerr=error_mult * ses1,
        fmt="none",
        ecolor=c1,
        elinewidth=1.5,
        capsize=4,
        alpha=0.9,
    )

    # --- Series 2 (optional) ---
    if has_second:
        ax.plot(
            x2,
            coefs2,
            color=c2,
            marker="s",
            label=series2_label,
        )
        ax.errorbar(
            x2,
            coefs2,
            yerr=error_mult * ses2,
            fmt="none",
            ecolor=c2,
            elinewidth=1.5,
            capsize=4,
            alpha=0.9,
        )

    # X-axis ticks at the "true" time points
    ax.set_xticks(x)
    if labels is not None:
        ax.set_xticklabels(labels)

    ax.set_xlabel("")
    ax.set_ylabel(ylabel)

    if has_second:
        ax.legend(title="")
    else:
        # Optional: you can comment this out if you don't want a legend
        ax.legend(title="")

    finalize_plot(ax=ax)

    return fig


def build_full_strategy_content_df(df: pd.DataFrame) -> pd.DataFrame:
    required_cols = {"user_id_raw", "T", "question_name", "type", "content"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Input df is missing required columns: {sorted(missing)}")

    persuasion_qs = {
        "t4_closing_summary",
        "t4_barriers_solutions",
        "t4_enforcement",
        "t4_commitment_rule",
        "t4_plan_or_benchmarks",
    }
    change_amb_qs = {"wrap_up", "review_interview", "action_step"}

    d = df.copy()

    # 1) Only type == 'answer'
    d = d[d["type"].eq("answer")]

    # 2) Only T != "Control"
    d = d[~d["T"].eq("Control")]

    # content cleanup
    d["content"] = d["content"].fillna("").astype(str)

    # 3) Filter by the question_name sets conditioned on T
    mask_persuasion = d["T"].eq("Persuasion") & d["question_name"].isin(persuasion_qs)
    mask_change_amb = d["T"].isin(["Change Talk", "Ambivalence"]) & d["question_name"].isin(change_amb_qs)
    d = d[mask_persuasion | mask_change_amb]

    # Deterministic ordering
    d = d.sort_values(["user_id_raw", "T", "question_name"], kind="mergesort")

    out = (
        d.groupby(["user_id_raw", "T"], as_index=False)
        .agg(
            full_content=(
                "content",
                lambda s: "\n\n".join(
                    f" --- {x.strip()}"
                    for x in s
                    if str(x).strip()
                )
            )
        )
    )

    return out





def build_positive_negative_content_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build per-(user_id_raw, T) concatenated content from all non-Control answers,
    excluding specific scaling questions.

    Output columns: user_id_raw, T, full_content
    """
    required_cols = {"user_id_raw", "T", "question_name", "type", "content"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Input df is missing required columns: {sorted(missing)}")

    excluded_qs = {
        "t4_confidence_strengthen",
        "t4_importance_to_plan",
        "importance_followup_lower"
        "confidence_followup_lower"
    }

    d = df.copy()

    # 1) Only type == 'answer'
    d = d[d["type"].eq("answer")]

    # 2) Only T != "Control"
    d = d[~d["T"].eq("Control")]

    # content cleanup
    d["content"] = d["content"].fillna("").astype(str)

    # Keep all questions except the excluded ones
    d = d[~d["question_name"].isin(excluded_qs)]

    # Deterministic ordering (preserves relative order under ties)
    d = d.sort_values(["user_id_raw", "T", "question_name"], kind="mergesort")

    out = (
        d.groupby(["user_id_raw", "T"], as_index=False)
        .agg(
            full_content=(
                "content",
                lambda s: "\n\n".join(
                    f" --- {x.strip()}"
                    for x in s
                    if str(x).strip()
                ),
            )
        )
    )

    return out



prompt_positive_negative = prompt = """
You are a qualitative data analyst. Your task is to analyze interview excerpts regarding social media usage. 
You must identify and count the number of **unique** positive and negative components related to social media use mentioned in the text.

**Definitions:**
- **Positive Components:** Mentions of benefits derived from social media, such as learning, social connection, entertainment, relaxation, fun, coping mechanisms, or specific features the user enjoys (e.g., shopping, crafts).
- **Negative Components:** Mentions of harms or costs, such as wasting time, sleep disruption, financial loss, addiction/habit, interfering with work/chores, frustration, or negative impacts on mental health.

**Rules:**
- Count **unique** concepts only. If a user mentions "wasting time" in two different sentences, count it as 1 negative component.
- Ignore descriptions of *strategies* (e.g., "I set a timer") unless they explicitly mention a pro/con reasoning.
- Return ONLY a Python dictionary in the format: {{'positive': int, 'negative': int}}

---

**Few-Shot Examples:**

**Input:**
"i think it would be best to just try straight away... its an enormous time waster, thats the downside of social media! when i think of the amount of time i waste every single day on social media, it feels frustrating to me... i actually really enjoy learning new information on social media i learn something almost every day, usually about everyday things but sometimes about history or science... it makes my day, especially the hum drum ones, more interesting. i guess i see myself as slightly wiser... that using social media is fun and interesting... i think the enjoyment i get from using SM somewhat balances out the problematic side of things... because having written it down and therefore confronting the facts head-on, i can see that it is actually a problem!... it definitely affects the amount of jobs i can get done in a day."

**Output:**
{{'positive': 4, 'negative': 3}}
*(Reasoning for training: Positive = 1. Learning/History, 2. Makes day interesting, 3. Feeling wiser, 4. Fun. Negative = 1. Time waster/Frustrating, 2. Recognized as a "problem"/Addiction, 3. Affects ability to do jobs.)*

**Input:**
"My sleep is affected plus I end up spending money on stuff I don't really need... On facebook I would miss catching up with family and friends and on tiktok I would miss watching the craft videos... tiktok and facebook are my two time sinks. I like to look at facebook as my family and friends are on there so it is a way of seeing what they are up to and tiktok is just interesting as I enjoy crafts and there are many really helpful videos on there. plus I like shopping from tiktok... bedtime because I could relax and turn off my brain and probably have healthier sleep... I definately use social media way to much, especially at night. I struggle to sleep anyway so often play games on my phone or scroll through social media which I know probably makes matters worse."

**Output:**
{{'positive': 3, 'negative': 3}}
*(Reasoning for training: Positive = 1. Social connection (Family/Friends), 2. Entertainment (Crafts/Helpful videos), 3. Shopping. Negative = 1. Sleep disruption, 2. Financial cost/Spending money, 3. Time sink/Overuse.)*

---

**Analyze the following text:**

{text}
"""
