"""Extract named positive/negative aspects and reproduce the pros/cons figure.

This script intentionally does not ask the language model to count anything.
The model returns two lists of short aspect names. Python saves those lists and
computes the plotted counts with ``len()``.

Run from an editor, a terminal, or the companion ``fig_pros_cons.ipynb``:

    python fig_pros_cons.py

The script resumes from its output CSV after interruption. Set
``PROS_CONS_OPENAI_MODEL`` to override the default model and
``PROS_CONS_MAX_WORKERS`` to change API concurrency.
"""

from __future__ import annotations
raise RuntimeError("Restricted-input source only. Raw interview data are not distributed. API execution is disabled in this $0-API replication package; use code/python/run_public.py for saved-result reproduction.")

import hashlib
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import matplotlib.lines as mlines
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel


class NamedAspects(BaseModel):
    """Structured LLM output: names only, with no model-generated counts."""

    positive_aspects: list[str]
    negative_aspects: list[str]


@dataclass(frozen=True)
class Config:
    input_path: Path
    output_path: Path
    long_output_path: Path
    summary_output_path: Path
    local_figure_path: Path
    paper_figure_path: Path
    model: str
    max_workers: int
    checkpoint_every: int
    max_attempts: int


def make_config(script_dir: Path, environ: dict[str, str]) -> Config:
    """Construct all configuration explicitly from the script location and env."""
    output_dir = script_dir / "output"
    replication_root = script_dir.parents[1]
    in_replication_package = (
        replication_root / "EXHIBIT_MANIFEST.md"
    ).exists()
    if in_replication_package:
        default_input_path = (
            replication_root
            / "data"
            / "private"
            / "df_clean_with_llm_themes_pros_cons_v001.csv"
        )
        default_paper_figure_path = (
            replication_root / "results" / "figures"
            / "fig_number_pro_con_statements.pdf"
        )
    else:
        default_input_path = (
            output_dir / "df_clean_with_llm_themes_pros_cons_v001.csv"
        )
        default_paper_figure_path = (
            script_dir.parents[2]
            / "analysis_NR"
            / "6731ca401220dcd3b28dc2ec"
            / "figures"
            / "fig_number_pro_con_statements.pdf"
        )

    return Config(
        input_path=Path(
            environ.get("PROS_CONS_INPUT_PATH", str(default_input_path))
        ),
        output_path=output_dir / "df_clean_with_llm_named_pros_cons_v002.csv",
        long_output_path=output_dir / "pros_cons_named_aspects_long_v002.csv",
        summary_output_path=output_dir / "pros_cons_named_aspects_summary_v002.csv",
        local_figure_path=output_dir / "fig_number_pro_con_statements.pdf",
        paper_figure_path=Path(
            environ.get(
                "PROS_CONS_PAPER_FIGURE_PATH",
                str(default_paper_figure_path),
            )
        ),
        model=environ.get("PROS_CONS_OPENAI_MODEL", "gpt-5.6-luna"),
        max_workers=int(environ.get("PROS_CONS_MAX_WORKERS", "10")),
        checkpoint_every=int(environ.get("PROS_CONS_CHECKPOINT_EVERY", "20")),
        max_attempts=int(environ.get("PROS_CONS_MAX_ATTEMPTS", "3")),
    )


def get_api_key(environ: dict[str, str]) -> str:
    """Read the API key without embedding it in code or output files."""
    api_key = environ.get("OPENAI_API_KEY") or environ.get("API_KEY_OPENAI")
    if not api_key:
        raise RuntimeError(
            "No OpenAI API key found. Set OPENAI_API_KEY in python/.env "
            "(the existing API_KEY_OPENAI name is also supported)."
        )
    return api_key


def load_transcripts(input_path: Path) -> pd.DataFrame:
    """Load exactly the participant-level transcripts used by the old analysis."""
    required = ["user_id_raw", "T", "full_content"]
    source = pd.read_csv(input_path, usecols=required)
    if source[required].isna().any().any():
        raise ValueError(f"Missing required values in {input_path}")
    if source.duplicated(["user_id_raw", "T"]).any():
        raise ValueError("Participant/treatment keys are not unique")

    result = source.copy()
    result["transcript_sha256"] = result["full_content"].map(
        lambda text: hashlib.sha256(str(text).encode("utf-8")).hexdigest()
    )
    return result


def extraction_instructions() -> str:
    """Return the single source of truth for the qualitative coding task."""
    return """
You are a qualitative researcher coding interview excerpts about social media.

Identify the distinct positive and negative aspects of social media use that the
participant explicitly mentions.

Definitions:
- Positive aspects are perceived benefits or valued features, such as staying
  connected with friends, learning useful information, entertainment, relaxation,
  creative inspiration, or access to communities.
- Negative aspects are perceived harms or costs, such as lost time, disrupted
  sleep, compulsive use, reduced focus, interference with work, financial costs,
  social comparison, or worse mental health.

Coding rules:
1. Return each aspect as a short, concrete noun phrase, normally 2–8 words
   (for example, "staying connected with friends" or "disrupted sleep").
2. Include only aspects grounded in the participant's text. Do not infer an
   unstated benefit or harm.
3. Consolidate repetitions and close paraphrases into one aspect. For example,
   repeated mentions of wasting time should yield one string.
4. Keep meaningfully different aspects separate.
5. Do not include strategies for reducing social media use unless the participant
   explicitly states the benefit or harm motivating the strategy.
6. Use an empty list when no aspect of a given type is mentioned.
7. Do not count the aspects. Return the named aspect strings only in the required
   structured fields.
""".strip()


def normalize_aspects(aspects: Sequence[str]) -> list[str]:
    """Clean and case-insensitively deduplicate aspect names without counting."""
    cleaned: list[str] = []
    seen: set[str] = set()
    for value in aspects:
        aspect = " ".join(str(value).strip().split()).strip(" .;,")
        key = aspect.casefold()
        if aspect and key not in seen:
            cleaned.append(aspect)
            seen.add(key)
    return cleaned


def pseudonymous_safety_id(user_id: object) -> str:
    """Return a stable pseudonymous identifier rather than sending the raw ID."""
    return hashlib.sha256(f"pros-cons:{user_id}".encode("utf-8")).hexdigest()


def extract_named_aspects(
    client: OpenAI,
    model: str,
    transcript: str,
    user_id: object,
    max_attempts: int,
) -> tuple[NamedAspects, str, int]:
    """Call the model and return named lists plus API response provenance."""
    error: Exception | None = None
    for attempt in range(max_attempts):
        try:
            response = client.responses.parse(
                model=model,
                instructions=extraction_instructions(),
                input=str(transcript),
                text_format=NamedAspects,
                reasoning={"effort": "low"},
                max_output_tokens=1200,
                safety_identifier=pseudonymous_safety_id(user_id),
                store=False,
            )
            parsed = response.output_parsed
            if parsed is None:
                raise ValueError("The API returned no parsed structured output")
            normalized = NamedAspects(
                positive_aspects=normalize_aspects(parsed.positive_aspects),
                negative_aspects=normalize_aspects(parsed.negative_aspects),
            )
            return normalized, response.id, int(response.created_at)
        except Exception as exc:  # API and validation errors are retried uniformly
            error = exc
            if attempt + 1 < max_attempts:
                time.sleep(2**attempt)
    raise RuntimeError(f"Aspect extraction failed after {max_attempts} attempts") from error


def json_list(value: object) -> list[str] | None:
    """Parse a saved JSON list, returning None for absent or invalid values."""
    if not isinstance(value, str):
        return None
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, list) or not all(isinstance(x, str) for x in parsed):
        return None
    return parsed


def add_checkpoint_results(
    transcripts: pd.DataFrame,
    checkpoint_path: Path,
    model: str,
) -> pd.DataFrame:
    """Attach reusable results only when key, transcript hash, and model match."""
    result = transcripts.copy()
    result["positive_aspects_json"] = pd.NA
    result["negative_aspects_json"] = pd.NA
    result["extraction_model"] = pd.NA
    result["openai_response_id"] = pd.NA
    result["extraction_timestamp_unix"] = pd.NA

    if not checkpoint_path.exists():
        return result

    checkpoint = pd.read_csv(checkpoint_path)
    required = {
        "user_id_raw",
        "T",
        "transcript_sha256",
        "positive_aspects_json",
        "negative_aspects_json",
        "extraction_model",
        "openai_response_id",
        "extraction_timestamp_unix",
    }
    if not required.issubset(checkpoint.columns):
        return result

    reusable = checkpoint[
        checkpoint["extraction_model"].eq(model)
        & checkpoint["positive_aspects_json"].map(json_list).notna()
        & checkpoint["negative_aspects_json"].map(json_list).notna()
    ]
    lookup = reusable.set_index(["user_id_raw", "T", "transcript_sha256"])
    result_index = result.set_index(["user_id_raw", "T", "transcript_sha256"]).index
    matched = lookup.reindex(result_index)
    columns = [
        "positive_aspects_json",
        "negative_aspects_json",
        "extraction_model",
        "openai_response_id",
        "extraction_timestamp_unix",
    ]
    result.loc[:, columns] = matched[columns].to_numpy()
    return result


def count_saved_aspects(results: pd.DataFrame) -> pd.DataFrame:
    """Compute counts locally from the saved strings; the LLM supplies no counts."""
    counted = results.copy()
    counted["number_positive_aspects"] = counted["positive_aspects_json"].map(
        lambda value: len(json_list(value) or [])
    )
    counted["number_negative_aspects"] = counted["negative_aspects_json"].map(
        lambda value: len(json_list(value) or [])
    )
    return counted


def atomic_write_csv(data: pd.DataFrame, path: Path) -> None:
    """Write a checkpoint atomically so an interruption cannot corrupt it."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    data.to_csv(temporary_path, index=False)
    os.replace(temporary_path, path)


def save_checkpoint(results: pd.DataFrame, path: Path) -> None:
    """Save named aspects and Python-derived counts."""
    atomic_write_csv(count_saved_aspects(results), path)


def pending_indices(results: pd.DataFrame) -> list[int]:
    """Return rows that do not yet have two valid saved aspect lists."""
    complete = results["positive_aspects_json"].map(json_list).notna() & results[
        "negative_aspects_json"
    ].map(json_list).notna()
    return results.index[~complete].tolist()


def run_extraction(
    results: pd.DataFrame,
    client: OpenAI,
    config: Config,
) -> pd.DataFrame:
    """Extract missing rows concurrently and checkpoint progress."""
    pending = pending_indices(results)
    if not pending:
        print(f"All {len(results):,} transcripts already have reusable results.")
        return results

    print(
        f"Extracting named aspects for {len(pending):,} transcripts "
        f"with {config.model}..."
    )

    def submit_row(row_index: int) -> tuple[int, NamedAspects, str, int]:
        row = results.loc[row_index]
        aspects, response_id, timestamp = extract_named_aspects(
            client=client,
            model=config.model,
            transcript=row["full_content"],
            user_id=row["user_id_raw"],
            max_attempts=config.max_attempts,
        )
        return row_index, aspects, response_id, timestamp

    failures: list[tuple[int, str]] = []
    completed = 0
    with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
        futures = {executor.submit(submit_row, index): index for index in pending}
        for future in as_completed(futures):
            index = futures[future]
            try:
                row_index, aspects, response_id, timestamp = future.result()
                results.at[row_index, "positive_aspects_json"] = json.dumps(
                    aspects.positive_aspects, ensure_ascii=False
                )
                results.at[row_index, "negative_aspects_json"] = json.dumps(
                    aspects.negative_aspects, ensure_ascii=False
                )
                results.at[row_index, "extraction_model"] = config.model
                results.at[row_index, "openai_response_id"] = response_id
                results.at[row_index, "extraction_timestamp_unix"] = timestamp
                completed += 1
                print(f"Completed {completed:,}/{len(pending):,}")
            except Exception as exc:
                failures.append((index, str(exc)))

            if completed and completed % config.checkpoint_every == 0:
                save_checkpoint(results, config.output_path)

    save_checkpoint(results, config.output_path)
    if failures:
        examples = "; ".join(f"row {i}: {message}" for i, message in failures[:5])
        raise RuntimeError(
            f"{len(failures)} rows failed and remain resumable. Examples: {examples}"
        )
    return results


def make_long_aspect_data(results: pd.DataFrame) -> pd.DataFrame:
    """Create one auditable row per named aspect."""
    records: list[dict[str, object]] = []
    for row in results.itertuples(index=False):
        for valence, column in (
            ("positive", "positive_aspects_json"),
            ("negative", "negative_aspects_json"),
        ):
            for position, aspect in enumerate(json_list(getattr(row, column)) or [], 1):
                records.append(
                    {
                        "user_id_raw": row.user_id_raw,
                        "T": row.T,
                        "valence": valence,
                        "aspect_position": position,
                        "aspect": aspect,
                        "extraction_model": row.extraction_model,
                        "openai_response_id": row.openai_response_id,
                        "extraction_timestamp_unix": row.extraction_timestamp_unix,
                    }
                )
    return pd.DataFrame.from_records(records)


def treatment_labels(values: pd.Series) -> pd.Series:
    """Map internal arm names to the labels displayed in the manuscript."""
    return values.replace(
        {
            "Ambivalence": "Decisional Balance",
            "Persuasion": "Direct Persuasion",
        }
    )


def make_summary(results: pd.DataFrame) -> pd.DataFrame:
    """Return arm-level descriptive statistics used in the figure."""
    counted = count_saved_aspects(results)
    counted["treatment"] = treatment_labels(counted["T"])
    return (
        counted.groupby("treatment", as_index=False)
        .agg(
            participants=("user_id_raw", "nunique"),
            mean_positive_aspects=("number_positive_aspects", "mean"),
            sd_positive_aspects=("number_positive_aspects", "std"),
            mean_negative_aspects=("number_negative_aspects", "mean"),
            sd_negative_aspects=("number_negative_aspects", "std"),
        )
    )


def set_plot_style() -> tuple[str, str]:
    """Apply the manuscript style and return the two series colors."""
    sns.set_theme(style="white", font="Arial", font_scale=1.3)
    colors = ("#800000", "#1a476f")
    plt.rcParams.update(
        {
            "legend.frameon": False,
            "axes.grid": False,
            "figure.figsize": (10, 8),
        }
    )
    return colors


def create_figure(results: pd.DataFrame) -> plt.Figure:
    """Plot means and bootstrap 95% CIs from locally counted aspect strings."""
    data = count_saved_aspects(results)
    data["treatment"] = treatment_labels(data["T"])
    order = ["Change Talk", "Decisional Balance", "Direct Persuasion"]
    colors = set_plot_style()
    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True, sharey=True)

    plot_specs = (
        ("number_positive_aspects", "Positive aspects", colors[0]),
        ("number_negative_aspects", "Negative aspects", colors[1]),
    )
    for ax, (column, label, color) in zip(axes, plot_specs):
        sns.barplot(
            data=data,
            x=column,
            y="treatment",
            order=order,
            errorbar=("ci", 95),
            seed=142,
            color=color,
            errcolor="black",
            capsize=0.1,
            ax=ax,
        )
        ax.bar_label(
            ax.containers[0],
            fmt="Mean: %.2f",
            label_type="center",
            color="white",
            fontsize=12,
            fontweight="bold",
        )
        ax.set_xlabel("")
        ax.set_ylabel("")
        sns.despine(ax=ax)

    handles = [
        mlines.Line2D([], [], color=color, linewidth=8, label=label)
        for _, label, color in plot_specs
    ]
    fig.legend(
        handles=handles,
        bbox_to_anchor=(1, 0.5),
        loc="center left",
        frameon=False,
    )
    axes[1].set_xlabel("Number of distinct aspects mentioned by participant")
    axes[0].set_xlim(0, 10)
    fig.tight_layout()
    return fig


def save_figure(figure: plt.Figure, paths: Iterable[Path]) -> None:
    """Save the same figure to the analysis output and manuscript directories."""
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(path, bbox_inches="tight")
        print(f"Saved figure: {path}")


def main() -> None:
    """Run extraction, local counting, audit exports, and figure generation."""
    script_dir = Path(__file__).resolve().parent
    load_dotenv(script_dir / ".env")
    config = make_config(script_dir, dict(os.environ))
    transcripts = load_transcripts(config.input_path)
    results = add_checkpoint_results(transcripts, config.output_path, config.model)

    if pending_indices(results):
        client = OpenAI(api_key=get_api_key(dict(os.environ)), max_retries=2)
        results = run_extraction(results, client, config)

    save_checkpoint(results, config.output_path)
    atomic_write_csv(make_long_aspect_data(results), config.long_output_path)
    atomic_write_csv(make_summary(results), config.summary_output_path)
    figure = create_figure(results)
    save_figure(
        figure,
        (config.local_figure_path, config.paper_figure_path),
    )
    plt.show()


if __name__ == "__main__":
    main()
