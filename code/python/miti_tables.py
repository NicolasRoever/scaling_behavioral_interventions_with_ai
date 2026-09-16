from __future__ import annotations
import numpy as np
import pandas as pd

def label_for(run):
    if run["condition"] == "model_swap":
        return "Different model: " + run["model"]
    return {"benchmark": "Benchmark", "rerun": "Stochastic reruns", "ablation": "Prompt ablation"}[run["condition"]]


def procedure_frames(runs, frames, dataset, subset_ids=None):
    chosen = [r for r in runs if r["dataset"] == dataset or (
        dataset == "validation14" and r["dataset"] == "validation20" and r["condition"] == "benchmark")]
    groups = {}
    for run in chosen:
        frame = frames[run["run_id"]]
        if subset_ids is not None:
            frame = frame[frame.session_id.isin(subset_ids)]
        groups.setdefault(label_for(run), []).append(frame)
    return {label: pd.concat(parts, ignore_index=True) for label, parts in groups.items()}


def comparison_rows(reference, comparison, label, reference_label, dimensions, metric_fn):
    keys = ["session_id", "miti_dimension"]
    if reference.duplicated(keys).any():
        raise ValueError("Reference must have exactly one score per session and dimension")
    merged = comparison.merge(reference[keys + ["score"]], on=keys, how="left",
                              suffixes=("_cmp", "_ref"), validate="many_to_one")
    if merged.score_ref.isna().any():
        raise ValueError("Comparison has observations absent from reference")
    rows = []
    for dim in ["Global", *dimensions]:
        sub = merged if dim == "Global" else merged[merged.miti_dimension.eq(dim)]
        row = dict(Analysis=label, Reference=reference_label,
                   **{"MITI outcome": dim, "Outcome type": "Global, 1–5",
                      "Unique sessions": sub.session_id.nunique(), "Score pairs": len(sub),
                      "Runs": sub.run_id.nunique()})
        row.update(metric_fn(sub.score_ref, sub.score_cmp))
        # Preserve unrounded means, bias, MAE and correlation in CSVs.
        row.update({"Original mean": sub.score_ref.mean(), "Comparison mean": sub.score_cmp.mean(),
                    "Mean difference": (sub.score_cmp - sub.score_ref).mean(),
                    "MAE": (sub.score_cmp - sub.score_ref).abs().mean(),
                    "Correlation": sub.score_ref.corr(sub.score_cmp)})
        rows.append(row)
    return rows


def write_table(frame, directory, name):
    frame.to_csv(directory / f"{name}.csv", index=False)
    (directory / f"{name}.md").write_text(frame.to_markdown(index=False, floatfmt=".3f"))


def tex_escape(value):
    return str(value).replace("\\", r"\textbackslash{}").replace("&", r"\&").replace("%", r"\%").replace("_", r"\_")


def latex_table(headers, rows, path, spec=None, section_headings=False):
    lines = [r"\begin{tabular}{" + (spec or "l" + "r" * (len(headers) - 1)) + "}", r"\toprule",
             " & ".join(tex_escape(x) for x in headers) + r" \\", r"\midrule"]
    section_index = 0
    for row in rows:
        if section_headings and all(value == "" for value in row[1:]):
            if section_index:
                lines.append(r"\addlinespace[1em]")
            label = f"{chr(ord('a') + section_index)}. {row[0]}"
            lines.append(r"\multicolumn{" + str(len(headers)) + r"}{l}{\textit{" + tex_escape(label) + r"}} \\[0.25em]")
            section_index += 1
        else:
            lines.append(" & ".join(tex_escape(x) for x in row) + r" \\")
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    path.write_text("\n".join(lines))


def fmt_number(value):
    return "--" if pd.isna(value) else f"{value:.2f}"


def human_scores(folder, subset_ids, dimensions):
    human = pd.read_csv(folder / "inputs/human.csv")
    dim_map = dict(zip(["CCT", "SST", "PAR", "EMP"],
                       ["Cultivating Change Talk", "Softening Sustain Talk", "Partnership", "Empathy"]))
    human = human.melt(id_vars="source_pdf", value_vars=list(dim_map), var_name="short", value_name="score")
    human["miti_dimension"] = human["short"].map(dim_map)
    human["session_id"] = human["source_pdf"]
    if subset_ids is not None:
        human = human[human.session_id.isin(subset_ids)]
    if human.duplicated(["session_id", "miti_dimension"]).any() or not human.score.isin([1, 2, 3, 4, 5]).all():
        raise ValueError("Invalid human scores")
    return human


def build_validation(folder, manifest, runs, frames, out, metric_fn):
    ids = set(pd.read_csv(folder / "inputs/subset.csv", usecols=["source_pdf"]).source_pdf)
    procedures = procedure_frames(runs, frames, "validation14", ids)
    human = human_scores(folder, ids, manifest["dimensions"])
    baseline = procedures["Benchmark"]
    rows = []
    for label, comparison in procedures.items():
        rows += comparison_rows(human, comparison, label, "Human", manifest["dimensions"], metric_fn)
        if label != "Benchmark":
            rows += comparison_rows(baseline, comparison, label, "Luna benchmark", manifest["dimensions"], metric_fn)
    for run in runs:
        if run["dataset"] == "validation14" and run["condition"] == "rerun":
            for reference_label, reference in [("Human", human), ("Luna benchmark", baseline)]:
                rows += comparison_rows(reference, frames[run["run_id"]], f'Stochastic rerun {run["replicate"]}',
                                        reference_label, manifest["dimensions"], metric_fn)
    summary = pd.DataFrame(rows)
    write_table(summary, out, "robustness_summary_table_handcoded")
    global_metrics = summary[summary.Analysis.eq("Benchmark") & summary.Reference.eq("Human")].rename(
        columns={"MITI outcome": "Dimension", "Mean difference": "Bias"})[["Dimension", "Bias", "Correlation"]]
    global_metrics.to_csv(out / "validation_global_scores_results.csv", index=False)
    behavioral = pd.read_csv(folder / "inputs/behavioral_results.csv")
    behavioral = behavioral.assign(_last=behavioral.Category.eq("Reflection Correlation")).sort_values("_last", kind="stable").drop(columns="_last")
    table_rows = [["A. Global metrics (Luna)", "", ""]]
    table_rows += [[r.Dimension, f"{r.Bias:.2f}", f"{r.Correlation:.2f}"] for r in global_metrics.itertuples()]
    table_rows += [["B. Behavioral counts (existing results)", "", ""]]
    table_rows += [[r.Category, f"{r.Bias:.2f}" if pd.notna(r.Bias) else "",
                    f"{r.Correlation:.2f}" if pd.notna(r.Correlation) else ""] for r in behavioral.itertuples()]
    latex_table(["Score category", "Bias", "Correlation"], table_rows,
                out / "mi_validation_results_table.tex", "p{10cm}rr")
    table_rows = []
    for label in procedures:
        selected = summary[summary.Analysis.eq(label) & summary.Reference.eq("Human")]
        table_rows.append([label, "", "", ""])
        for _, row in selected.iterrows():
            table_rows.append([row["MITI outcome"], str(row["Unique sessions"]),
                               fmt_number(row["Mean difference"]), fmt_number(row["Correlation"])])
    latex_table(["Procedure / score", "Sessions", "Bias", "Correlation"], table_rows,
                out / "robustness_handcoded_latex_table.tex", "p{9cm}rrr", section_headings=True)
    return summary


def arm_assignments(folder):
    return pd.read_csv(folder / "inputs/arms.csv")


def attach_arms(scores, arms):
    scores = scores.copy()
    scores["user_id_raw"] = pd.to_numeric(scores.session_id.str.replace(r"^MI-MAINEXP-", "", regex=True), errors="raise")
    merged = scores.merge(arms, on="user_id_raw", how="left", validate="many_to_one")
    # Original paper exhibits use the cleaned survey sample, not every raw interview.
    excluded = merged.loc[~merged["T"].isin([0, 1, 2, 3])]
    audit = dict(scored_sessions=scores.session_id.nunique(), excluded_without_clean_survey=excluded.session_id.nunique())
    return merged[merged["T"].isin([0, 1, 2, 3])].copy(), audit


def save_figure(fig, out, name):
    fig.savefig(out / f"{name}.pdf", bbox_inches="tight")
    import matplotlib.pyplot as plt
    plt.close(fig)


def build_main_figures(data, dimensions, out):
    import matplotlib.pyplot as plt
    arms = {0: "Control", 1: "Change Talk", 2: "Ambivalence", 3: "Persuasion"}
    colors = {0: "#8a8a8a", 1: "#b83232", 2: "#4c4c86", 3: "#4c8a4c"}
    means = data.groupby(["T", "miti_dimension"]).agg(Mean=("score", "mean"), N=("session_id", "nunique")).reset_index()
    means.to_csv(out / "miti_means_by_treatment.csv", index=False)
    pooled = data.groupby("T").agg(Mean=("score", "mean"), N=("session_id", "nunique")).reset_index()
    pooled.to_csv(out / "miti_global_means_by_treatment.csv", index=False)
    for selected_arms, filename in [(list(arms), "fig_miti_score_distributions_main_study"),
                                    ([1, 2], "fig_miti_score_histograms")]:
        fig, axes = plt.subplots(2, 2, figsize=(10, 7), constrained_layout=True)
        for ax, dim in zip(axes.flat, dimensions):
            width = .8 / len(selected_arms)
            for i, arm in enumerate(selected_arms):
                values = data.loc[data["T"].eq(arm) & data.miti_dimension.eq(dim), "score"]
                percentages = values.value_counts(normalize=True).reindex(range(1, 6), fill_value=0) * 100
                ax.bar(np.arange(1, 6) + (i - (len(selected_arms) - 1) / 2) * width,
                       percentages, width=width, color=colors[arm], label=f'{arms[arm]} (mean {values.mean():.2f})')
            ax.set(title=dim, xticks=range(1, 6), xlabel="MITI score", ylabel="Percent")
            ax.legend(fontsize=8)
        save_figure(fig, out, filename)


def build_stability(procedures, dimensions, out):
    import matplotlib.pyplot as plt
    frames = {"Benchmark": procedures["Benchmark"],
              "All runs pooled": pd.concat(list(procedures.values()), ignore_index=True),
              **{k: v for k, v in procedures.items() if k != "Benchmark"}}
    rows = []
    for label, frame in frames.items():
        for dimension in ["Global", *dimensions]:
            sub = frame if dimension == "Global" else frame[frame.miti_dimension.eq(dimension)]
            rows.append({"MITI outcome": dimension, "Procedure": label, "N": len(sub),
                         "Unique sessions": sub.session_id.nunique(), "Mean": sub.score.mean(),
                         "q2.5": sub.score.quantile(.025), "q97.5": sub.score.quantile(.975)})
    table = pd.DataFrame(rows)
    write_table(table, out, "score_stability_table")
    latex_rows = []
    for dimension in ["Global", *dimensions]:
        values = table[table["MITI outcome"].eq(dimension)]
        cells = []
        for label in frames:
            row = values[values.Procedure.eq(label)].iloc[0]
            cells.append(f'{row["Mean"]:.2f} [{row["q2.5"]:.1f}, {row["q97.5"]:.1f}]')
        latex_rows.append([dimension, *cells])
    short_labels = [label.replace("Different model: ", "").replace("-2026-04-23", "").replace("-2026-03-05", "") for label in frames]
    latex_table(["Score", *short_labels], latex_rows, out / "score_stability_latex_table.tex")
    palette = ["#333333", "#4c4c86", "#b83232", "#8a6d3b", "#1b6b1b", "#557b99"]
    for kind in ["violin"]:
        panel_dimensions = dimensions if kind == "violin" else ["Global", *dimensions]
        panel_rows = (len(panel_dimensions) + 1) // 2
        fig, axes = plt.subplots(panel_rows, 2, figsize=(8, 2.85 * panel_rows), constrained_layout=True)
        for ax, dimension in zip(axes.flat, panel_dimensions):
            for pos, ((label, frame), color) in enumerate(zip(frames.items(), palette)):
                sub = frame if dimension == "Global" else frame[frame.miti_dimension.eq(dimension)]
                values = sub.score.to_numpy()
                if kind == "violin" and np.std(values) > 0:
                    parts = ax.violinplot([values], positions=[pos], vert=False, widths=.75,
                                          showextrema=False, bw_method=.25)
                    parts["bodies"][0].set_facecolor(color)
                    parts["bodies"][0].set_alpha(.55)
                elif kind == "forest":
                    lo, hi = np.quantile(values, [.025, .975])
                    ax.plot([lo, hi], [pos, pos], color=color, linewidth=2)
                ax.plot([values.mean()], [pos], marker="|" if kind == "violin" else "o", color="black", markersize=8)
            ax.set(title=dimension, xlim=(.7, 5.3), xticks=range(1, 6), xlabel="MITI score")
            ax.set_yticks(range(len(frames)))
            ax.set_yticklabels(short_labels)
            if not ax.yaxis_inverted():
                ax.invert_yaxis()
        for ax in list(axes.flat)[len(panel_dimensions):]:
            ax.axis("off")
        save_figure(fig, out, f"score_stability_{kind}_plot")
    return table


