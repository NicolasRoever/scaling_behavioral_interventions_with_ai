raise RuntimeError("Restricted-input source only. Raw interview data are not distributed. API execution is disabled in this $0-API replication package; use code/python/run_public.py for saved-result reproduction.")
"""Join saved MITI batch responses and regenerate Tables C.1 and C.2 offline.

Uses the explicit files in benchmark_config.json, never credentials or network.
Fails on missing, duplicate, failed, or mismatched scores before writing tables.
Overwrites the two table fragments in the configured manuscript tables folder.
Use --local-only to skip that copy, or --pdf to also compile a two-page preview.
"""

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from build_campaign_exhibits import comparison_rows, fmt_number, latex_table
from miti_benmchmarking.prepare_validation_batch import validation_conditions
from miti_benmchmarking.run_validation_batch import BatchRunnerError, atomic_bytes, digest, load_manifest, local_path, parse_result
from robustness_run_scoring import ABLATED_LINE


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def file_evidence(path, base):
    return {"path": str(path.relative_to(base)), "sha256": digest(path.read_bytes())}


def validate_inputs(manifest_path):
    """Check the frozen inputs and complete design before reading any scores."""
    manifest, checksum = load_manifest(manifest_path)
    folder = manifest_path.parent
    expected_conditions = validation_conditions(
        "gpt-5.6-luna", "gpt-5.4-2026-03-05", "gpt-5.5-2026-04-23", "low")
    dimensions = ["Cultivating Change Talk", "Softening Sustain Talk", "Partnership", "Empathy"]
    if (manifest["conditions"] != expected_conditions or manifest["interviews"] != 14 or
            manifest["dimensions"] != dimensions or manifest["requests"] != 504):
        raise ValueError("Expected the specified nine-condition, 14-interview, four-dimension design")
    for item in manifest["source_files"].values():
        if digest(local_path(folder, item["snapshot"]).read_bytes()) != item["sha256"]:
            raise ValueError(f"Frozen source changed: {item['snapshot']}")
    subset = pd.read_csv(local_path(folder, manifest["source_files"]["subset"]["snapshot"]))
    selected = set(subset.source_pdf)
    sessions = read_json(local_path(folder, manifest["sessions_file"]))
    by_session = {session["source_pdf"]: session for session in sessions}
    if len(selected) != 14 or len(sessions) != 14 or set(by_session) != selected:
        raise ValueError("Frozen transcripts do not match the previous 14-interview subset")
    for session in sessions:
        if digest(session["transcript"].encode()) != session["transcript_sha256"]:
            raise ValueError(f"Transcript checksum mismatch: {session['source_pdf']}")
    prompts = read_json(local_path(folder, manifest["prompt_file"]))
    if ("# Change Goal" in prompts["standard"] or "social media" in prompts["standard"].lower() or
            prompts["standard"].count(ABLATED_LINE) != 1 or
            prompts["ablation"] != prompts["standard"].replace(ABLATED_LINE, "")):
        raise ValueError("Expected a topic-neutral prompt and only the conservative-rule ablation")
    conditions = {condition["id"]: condition for condition in manifest["conditions"]}
    metadata = {row["custom_id"]: row for row in manifest["request_index"]}
    expected_keys = {(condition, source_pdf, dimension) for condition in conditions
                     for source_pdf in selected for dimension in dimensions}
    keys = [(row["condition_id"], row["source_pdf"], row["miti_dimension"])
            for row in metadata.values()]
    if len(set(keys)) != len(keys) or set(keys) != expected_keys:
        raise ValueError("Missing or duplicate interview/dimension/condition combinations")
    for batch in manifest["batches"]:
        for line in local_path(folder, batch["file"]).read_text(encoding="utf-8").splitlines():
            request = json.loads(line)
            row = metadata[request["custom_id"]]
            condition = conditions[row["condition_id"]]
            if any(row[key] != condition[key] for key in ["model", "condition", "replicate", "reasoning_effort"]):
                raise ValueError(f"Condition metadata mismatch: {row['custom_id']}")
            variant = "ablation" if condition["ablation"] else "standard"
            session = by_session[row["source_pdf"]]
            prompt = prompts[variant].format(transcript=session["transcript"],
                component_name=row["miti_dimension"], coding_instructions=prompts["guide"][row["miti_dimension"]])
            body = request["body"]
            if (body["input"] != prompt or row["prompt_variant"] != variant or
                    row["transcript_sha256"] != session["transcript_sha256"] or
                    body.get("reasoning", {}).get("effort") != condition["reasoning_effort"] or
                    body.get("text", {}).get("verbosity") != "medium" or body.get("store") is not False or
                    body.get("max_output_tokens") != manifest["max_output_tokens"]):
                raise ValueError(f"Prompt or settings mismatch: {row['custom_id']}")
    human = pd.read_csv(local_path(folder, manifest["source_files"]["human_scores"]["snapshot"]))
    if human.source_pdf.duplicated().any() or selected - set(human.source_pdf):
        raise ValueError("Missing or duplicate human-reference interviews")
    human = human[human.source_pdf.isin(selected)].copy()
    dimension_map = dict(zip(["CCT", "SST", "PAR", "EMP"], dimensions))
    human = human.melt(id_vars="source_pdf", value_vars=list(dimension_map),
                       var_name="dimension_code", value_name="score")
    if not human.score.isin([1, 2, 3, 4, 5]).all():
        raise ValueError("Human-reference scores must be integers from 1 to 5")
    human["miti_dimension"] = human.dimension_code.map(dimension_map)
    human["session_id"] = human.source_pdf
    return manifest, checksum, human


def join_results(manifest, result_paths, human, base):
    """Match by custom_id, independently of download filename or result order."""
    index = {row["custom_id"]: row for row in manifest["request_index"]}
    returned = {}
    for path in result_paths:
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            record = json.loads(line)
            identifier = record.get("custom_id")
            if identifier not in index or identifier in returned:
                raise ValueError(f"Unknown or duplicate result ID: {identifier}")
            result = parse_result(record)
            if result["error"]:
                raise ValueError(f"Unusable response {identifier}: {result['error']}")
            metadata = index[identifier]
            body = record["response"]["body"]
            if (result["response_model"] != metadata["model"] or
                    body.get("reasoning", {}).get("effort") != metadata["reasoning_effort"] or
                    body.get("error")):
                raise ValueError(f"Response model or reasoning mismatch: {identifier}")
            returned[identifier] = {**metadata, **result,
                "raw_result_file": str(path.relative_to(base)), "raw_result_line": line_number,
                "batch_request_id": record.get("id", "")}
    missing = set(index) - set(returned)
    if missing:
        raise ValueError(f"Missing {len(missing)} expected responses; no tables generated")
    scores = pd.DataFrame([returned[identifier] for identifier in index])
    if scores.response_id.eq("").any() or scores.response_id.duplicated().any():
        raise ValueError("Missing or duplicate response IDs")
    scores["session_id"] = scores.source_pdf
    scores["run_id"] = scores.condition_id
    scores = scores.merge(human[["session_id", "miti_dimension", "score"]].rename(
        columns={"score": "human_score"}), on=["session_id", "miti_dimension"],
        how="left", validate="many_to_one")
    if scores.human_score.isna().any():
        raise ValueError("A response has no matching human rating")
    scores["difference"] = scores.score - scores.human_score
    return scores


def summaries(scores, human, dimensions):
    groups = [("Benchmark", scores[scores.condition.eq("benchmark")]),
              ("Stochastic reruns", scores[scores.condition.eq("rerun")]),
              ("Prompt ablation", scores[scores.condition.eq("ablation")])]
    # Preserve the manuscript's ordering of the two model-comparison sections.
    for model in sorted(scores.loc[scores.condition.eq("model_comparison"), "model"].unique(), reverse=True):
        groups.append(("Different model: " + model, scores[scores.model.eq(model)]))
    rows = []
    per_run = []
    for label, frame in groups:
        rows.extend(comparison_rows(human, frame, label, "Human", dimensions, lambda ref, cmp: {}))
        for run_id, run in frame.groupby("run_id", sort=False):
            values = comparison_rows(human, run, label, "Human", dimensions, lambda ref, cmp: {})
            for row in values:
                row.update(condition_id=run_id, replicate=int(run.replicate.iloc[0]),
                           model=run.model.iloc[0], reasoning_effort=run.reasoning_effort.iloc[0])
            per_run.extend(values)
    return pd.DataFrame(rows), pd.DataFrame(per_run)


def load_behavioral_reference(config, base):
    path = local_path(base, config["behavioral_reference"])
    if digest(path.read_bytes()) != config["behavioral_reference_sha256"]:
        raise ValueError("The preserved behavioral-count reference changed")
    frame = pd.read_csv(path)
    categories = ["Share Complex Reflections", "Reflection-to-Question Ratio",
                  "Total MI-Adherent Behavior", "Total MI Non-Adherent Behavior", "Reflection Correlation"]
    if (frame.Category.duplicated().any() or set(frame.Category) != set(categories) or
            list(frame.columns) != ["Category", "Bias", "Correlation"]):
        raise ValueError("Unexpected behavioral-count reference structure")
    return frame.set_index("Category").loc[categories].reset_index()


def write_tables(summary, behavioral, output):
    baseline = summary[summary.Analysis.eq("Benchmark")]
    global_rows = baseline.rename(columns={"MITI outcome": "Score category", "Mean difference": "Bias"})[
        ["Score category", "Bias", "Correlation"]].assign(Panel="A")
    behavioral_rows = behavioral.rename(columns={"Category": "Score category"}).assign(Panel="B")
    c1 = pd.concat([global_rows, behavioral_rows], ignore_index=True)[["Panel", "Score category", "Bias", "Correlation"]]
    c1.to_csv(output / "table_c1.csv", index=False)
    c1_rows = []
    for label, panel in [("A. Global metrics (Luna)", "A"), ("B. Behavioral counts (existing results)", "B")]:
        c1_rows.append([label, "", ""])
        for _, row in c1[c1.Panel.eq(panel)].iterrows():
            # The historical reflection-correlation row has no bias statistic.
            bias = "" if panel == "B" and pd.isna(row.Bias) else fmt_number(row.Bias)
            c1_rows.append([row["Score category"], bias, fmt_number(row.Correlation)])
    latex_table(["Score category", "Bias", "Correlation"], c1_rows,
                output / "mi_validation_results_table.tex", "p{10cm}rr",
                section_headings=True, letter_sections=False)
    summary.to_csv(output / "table_c2.csv", index=False)
    c2_rows = []
    for label, group in summary.groupby("Analysis", sort=False):
        c2_rows.append([label, "", "", ""])
        for _, row in group.iterrows():
            c2_rows.append([row["MITI outcome"], str(row["Unique sessions"]),
                            fmt_number(row["Mean difference"]), fmt_number(row.Correlation)])
    latex_table(["Procedure / score", "Sessions", "Bias", "Correlation"], c2_rows,
                output / "robustness_handcoded_latex_table.tex", "p{9cm}rrr", section_headings=True)


def write_wide_scores(scores, dimensions, path):
    keys = ["condition_id", "condition", "replicate", "model", "reasoning_effort", "source_pdf"]
    llm = scores.pivot(index=keys, columns="miti_dimension", values="score").reindex(columns=dimensions)
    human = scores.pivot(index=keys, columns="miti_dimension", values="human_score").reindex(columns=dimensions)
    human.columns = ["Human: " + dimension for dimension in dimensions]
    llm.join(human).reset_index().to_csv(path, index=False)


def write_preview(output):
    text = r"""\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage{booktabs,threeparttable}
\pagestyle{empty}
\renewcommand{\thetable}{C.\arabic{table}}
\begin{document}
\begin{table}[ht]
\centering\footnotesize
\begin{threeparttable}
\caption{Validation of LLM measurement for the MITI 4.2.1 coding manual}
\input{mi_validation_results_table.tex}
\begin{tablenotes}\footnotesize
\item Panel A compares \texttt{gpt-5.6-luna} with expert ratings on 14 interviews.
Bias is LLM minus human; correlation is Pearson's $r$. Global pools the four
dimensions (56 score pairs). Panel B preserves the previous behavioral-count
results and their original scoring procedure; it was not rerun.
\end{tablenotes}
\end{threeparttable}
\end{table}
\clearpage
\begin{table}[ht]
\centering\scriptsize
\begin{threeparttable}
\caption{Robustness of LLM measurement to stochastic reruns, model choice, and prompt design}
\input{robustness_handcoded_latex_table.tex}
\begin{tablenotes}\scriptsize
\item Each condition is compared with the same human ratings on 14 unique interviews.
Global pools four dimensions. Stochastic summaries pool five additional runs
(280 global score pairs; 70 per dimension), not 70 independent interviews.
Luna uses low reasoning; GPT-5.4 and GPT-5.5 use none. The validation prompt
omits the Change Goal passage. Ablation removes only the conservative-scoring
sentence. A dash indicates an undefined correlation. Per-run estimates are
provided in \texttt{summary\_per\_run.csv}.
\end{tablenotes}
\end{threeparttable}
\end{table}
\end{document}
"""
    (output / "tables_preview.tex").write_text(text, encoding="utf-8")


def publish_table_fragments(output, tables_dir, filenames):
    published = []
    for name in filenames:
        source = output / name
        destination = tables_dir / name
        content = source.read_bytes()
        previous_sha256 = digest(destination.read_bytes()) if destination.exists() else None
        atomic_bytes(destination, content)
        if destination.read_bytes() != content:
            raise ValueError(f"Manuscript table copy differs from generated output: {destination}")
        published.append(dict(source=str(source), destination=str(destination),
                              previous_sha256=previous_sha256, sha256=digest(content)))
    return published


def build_tables(config_path, output_override=None, pdf=False, publish=True):
    base = config_path.resolve().parent
    config = read_json(config_path)
    tables_dir = Path(config["manuscript_tables_dir"]).expanduser().resolve() if publish else None
    if tables_dir is not None and not tables_dir.is_dir():
        raise ValueError(f"Manuscript tables directory does not exist: {tables_dir}")
    manifest_path = local_path(base, config["manifest"])
    manifest, checksum, human = validate_inputs(manifest_path)
    paths = [local_path(base, relative) for relative in config["results"]]
    if len(set(paths)) != len(paths):
        raise ValueError("Duplicate result files in configuration")
    behavioral = load_behavioral_reference(config, base)
    scores = join_results(manifest, paths, human, base)
    summary, per_run = summaries(scores, human, manifest["dimensions"])
    output = output_override.resolve() if output_override else local_path(base, config["output_dir"])
    if output == base or output == manifest_path.parent or output in {path.parent for path in paths}:
        raise ValueError("Choose a separate derived-output folder")
    if pdf and shutil.which("pdflatex") is None:
        raise ValueError("pdflatex is unavailable; omit --pdf to create CSV and LaTeX outputs")
    # All data validation precedes creation/replacement of any derived outputs.
    output.mkdir(parents=True, exist_ok=True)
    scores.to_csv(output / "global_scores_joined.csv", index=False)
    write_wide_scores(scores, manifest["dimensions"], output / "interview_scores_wide.csv")
    per_run.to_csv(output / "summary_per_run.csv", index=False)
    write_tables(summary, behavioral, output)
    write_preview(output)
    if pdf:
        result = subprocess.run(["pdflatex", "-no-shell-escape", "-interaction=nonstopmode", "-halt-on-error",
                                 "tables_preview.tex"], cwd=output, capture_output=True, text=True)
        if result.returncode:
            raise ValueError(f"PDF compilation failed; inspect {output / 'tables_preview.log'}")
    input_paths = [config_path.resolve(), manifest_path, *paths,
                   local_path(base, config["behavioral_reference"])]
    input_paths += [local_path(manifest_path.parent, item["snapshot"])
                    for item in manifest["source_files"].values()]
    input_paths += [local_path(manifest_path.parent, manifest[key]) for key in
                    ["sessions_file", "prompt_file", "transcript_audit_file"]]
    table_names = ["mi_validation_results_table.tex", "robustness_handcoded_latex_table.tex"]
    output_names = ["global_scores_joined.csv", "interview_scores_wide.csv", "summary_per_run.csv",
                    "table_c1.csv", "table_c2.csv", *table_names, "tables_preview.tex"]
    if pdf:
        output_names.append("tables_preview.pdf")
    published = publish_table_fragments(output, tables_dir, table_names) if publish else []
    audit = dict(created_at_unix=int(time.time()), api_calls_made=0, additional_api_compute_cost_usd=0,
                 manifest_sha256=checksum, expected_requests=manifest["requests"], valid_scores=len(scores),
                 unique_interviews=int(scores.source_pdf.nunique()),
                 scores_per_condition={key: int(value) for key, value in scores.condition_id.value_counts().items()},
                 behavioral_reference_source=config["behavioral_reference_source"],
                 inputs=[file_evidence(path, base) for path in input_paths],
                 outputs=[file_evidence(output / name, output) for name in output_names],
                 manuscript_tables=published,
                 analysis_script_sha256=digest(Path(__file__).read_bytes()),
                 notes=["Bias = LLM minus human; Pearson correlation on paired scores.",
                        "Global pools four dimensions. Stochastic results pool five additional runs.",
                        "Repeated score pairs do not increase the number of unique interviews.",
                        "C.1 Panel B is copied from the preserved historical summary, not rescored.",
                        "Only the two manuscript table fragments are overwritten when publishing; captions, notes and prose are maintained in the manuscript."])
    (output / "analysis_manifest.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    return output, audit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path(__file__).resolve().parent / "benchmark_config.json")
    parser.add_argument("--output-dir", type=Path, help="Override the configured derived-output directory")
    parser.add_argument("--pdf", action="store_true", help="Also compile the two-page preview with pdflatex")
    parser.add_argument("--local-only", action="store_true", help="Build local outputs without overwriting manuscript tables")
    args = parser.parse_args()
    try:
        output, audit = build_tables(args.config, args.output_dir, args.pdf, publish=not args.local_only)
    except (BatchRunnerError, ValueError, KeyError, OSError) as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
