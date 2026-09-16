"""Reclassify reduction strategies and reproduce the treatment-arm figure.

The OpenAI model selects zero or more categories from a fixed coding manual.
Python, rather than the model, computes participant shares and draws the figure.
The output CSV is resumable and retains response IDs and backend Unix timestamps.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Sequence

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

from helper import set_plot_theme


Strategy = Literal[
    "Built-in Tracking/Restriction",
    "Curate Feed/Content",
    "Delete or Deactivate",
    "Increase Access Friction",
    "Modify Notifications",
    "Physical Separation",
    "Reduce Overall Phone Use",
    "Replace with Other Activities",
    "Set Rules or Goals",
    "Social Accountability",
    "Third-Party Blocker",
    "Willpower and Discipline",
]


class StrategySelection(BaseModel):
    """Structured model output constrained to the prespecified taxonomy."""

    strategies: list[Strategy]


@dataclass(frozen=True)
class Config:
    input_path: Path
    output_path: Path
    summary_path: Path
    local_figure_path: Path
    paper_figure_path: Path
    model: str
    max_workers: int
    checkpoint_every: int
    max_attempts: int


def make_config(script_dir: Path, environ: dict[str, str]) -> Config:
    """Create explicit configuration without global inputs."""
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
            / "df_clean_with_llm_themes_strategies_v003.csv"
        )
        default_paper_figure_path = (
            replication_root / "results" / "figures" / "fig_strategies.pdf"
        )
    else:
        default_input_path = (
            output_dir / "df_clean_with_llm_themes_strategies_v003.csv"
        )
        default_paper_figure_path = (
            script_dir.parents[2]
            / "analysis_NR"
            / "6731ca401220dcd3b28dc2ec"
            / "figures"
            / "fig_strategies.pdf"
        )
    return Config(
        input_path=Path(
            environ.get(
                "STRATEGIES_INPUT_PATH",
                str(default_input_path),
            )
        ),
        output_path=Path(
            environ.get(
                "STRATEGIES_OUTPUT_PATH",
                str(output_dir / "df_clean_with_llm_strategies_luna_v004.csv"),
            )
        ),
        summary_path=Path(
            environ.get(
                "STRATEGIES_SUMMARY_PATH",
                str(output_dir / "strategies_by_treatment_luna_v004.csv"),
            )
        ),
        local_figure_path=Path(
            environ.get(
                "STRATEGIES_LOCAL_FIGURE_PATH",
                str(output_dir / "fig_strategies_gpt-5.6-luna.pdf"),
            )
        ),
        paper_figure_path=Path(
            environ.get(
                "STRATEGIES_PAPER_FIGURE_PATH",
                str(default_paper_figure_path),
            )
        ),
        model=environ.get("STRATEGIES_OPENAI_MODEL", "gpt-5.6-luna"),
        max_workers=int(environ.get("STRATEGIES_MAX_WORKERS", "6")),
        checkpoint_every=int(environ.get("STRATEGIES_CHECKPOINT_EVERY", "20")),
        max_attempts=int(environ.get("STRATEGIES_MAX_ATTEMPTS", "3")),
    )


def coding_instructions() -> str:
    """Return the single source of truth for the strategy coding manual."""
    return """
You are coding interview excerpts about strategies for reducing social media use.
Select every category that is explicitly mentioned or clearly described. Select
no category when the excerpt contains no reduction strategy.

Categories:
- Built-in Tracking/Restriction: device or platform screen-time tracking, app
  limits, timers, downtime, focus modes, parental controls, or passcodes.
- Curate Feed/Content: unfollow, mute, filter, or otherwise improve the feed.
- Delete or Deactivate: uninstall an app or delete/deactivate an account.
- Increase Access Friction: log out, remove shortcuts, use a less convenient
  device, or add deliberate steps that make access harder.
- Modify Notifications: disable, silence, limit, or schedule notifications.
- Physical Separation: put the phone away, leave it in another room, or keep it
  physically out of reach.
- Reduce Overall Phone Use: reduce or avoid phone/screen use generally rather
  than targeting only a particular social-media platform.
- Replace with Other Activities: substitute offline activities, hobbies,
  exercise, work, reading, or in-person interaction for social media.
- Set Rules or Goals: set schedules, time windows, quotas, boundaries, gradual
  targets, or other explicit rules and goals.
- Social Accountability: enlist another person, make a shared commitment, or
  use social support/accountability.
- Third-Party Blocker: use a separate blocking or productivity application.
- Willpower and Discipline: rely on self-control, resisting urges, awareness,
  mindfulness, or a personal decision to stop without a concrete tool.

Coding rules:
1. Code strategies mentioned anywhere in the excerpt, whether already tried,
   planned, suggested, accepted, or rejected as an option.
2. Do not infer strategies from harms, benefits, motivation, or confidence alone.
3. Multiple categories may apply to the same statement.
4. Do not duplicate a category.
5. Use only the required category names.
""".strip()


def load_source(path: Path) -> pd.DataFrame:
    """Load the same participant excerpts used by the prior strategy analysis."""
    columns = ["user_id_raw", "T", "full_content"]
    source = pd.read_csv(path, usecols=columns)
    if source[columns].isna().any().any():
        raise ValueError(f"Missing required values in {path}")
    if source.duplicated(["user_id_raw", "T"]).any():
        raise ValueError("Participant/treatment keys are not unique")
    result = source.copy()
    result["transcript_sha256"] = result["full_content"].map(
        lambda text: hashlib.sha256(str(text).encode("utf-8")).hexdigest()
    )
    return result


def get_api_key(environ: dict[str, str]) -> str:
    """Read an API key without writing it to code or outputs."""
    key = environ.get("OPENAI_API_KEY") or environ.get("API_KEY_OPENAI")
    if not key:
        raise RuntimeError("Set OPENAI_API_KEY or API_KEY_OPENAI in python/.env")
    return key


def safety_id(user_id: object) -> str:
    """Create a stable pseudonymous safety identifier."""
    return hashlib.sha256(f"strategies:{user_id}".encode("utf-8")).hexdigest()


def classify_excerpt(
    client: OpenAI,
    model: str,
    excerpt: str,
    user_id: object,
    max_attempts: int,
) -> tuple[list[str], str, int]:
    """Classify one excerpt and return categories plus API provenance."""
    last_error: Exception | None = None
    for attempt in range(max_attempts):
        try:
            response = client.responses.parse(
                model=model,
                instructions=coding_instructions(),
                input=str(excerpt),
                text_format=StrategySelection,
                reasoning={"effort": "low"},
                max_output_tokens=800,
                safety_identifier=safety_id(user_id),
                store=False,
            )
            parsed = response.output_parsed
            if parsed is None:
                raise ValueError("The API returned no parsed structured output")
            strategies = list(dict.fromkeys(parsed.strategies))
            return strategies, response.id, int(response.created_at)
        except Exception as exc:
            last_error = exc
            if attempt + 1 < max_attempts:
                time.sleep(2**attempt)
    raise RuntimeError(f"Classification failed after {max_attempts} attempts") from last_error


def parse_saved_list(value: object) -> list[str] | None:
    """Parse a valid saved JSON list."""
    if not isinstance(value, str):
        return None
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, list) or not all(isinstance(x, str) for x in parsed):
        return None
    return parsed


def add_checkpoint(source: pd.DataFrame, path: Path, model: str) -> pd.DataFrame:
    """Reuse rows only when participant, transcript hash, and model match."""
    result = source.copy()
    result["llm_strategies_openai"] = pd.NA
    result["classification_model"] = pd.NA
    result["openai_response_id"] = pd.NA
    result["classification_timestamp_unix"] = pd.NA
    if not path.exists():
        return result

    checkpoint = pd.read_csv(path)
    needed = {
        "user_id_raw",
        "T",
        "transcript_sha256",
        "llm_strategies_openai",
        "classification_model",
        "openai_response_id",
        "classification_timestamp_unix",
    }
    if not needed.issubset(checkpoint.columns):
        return result
    reusable = checkpoint[
        checkpoint["classification_model"].eq(model)
        & checkpoint["llm_strategies_openai"].map(parse_saved_list).notna()
    ].set_index(["user_id_raw", "T", "transcript_sha256"])
    result_index = result.set_index(["user_id_raw", "T", "transcript_sha256"]).index
    matched = reusable.reindex(result_index)
    columns = [
        "llm_strategies_openai",
        "classification_model",
        "openai_response_id",
        "classification_timestamp_unix",
    ]
    result.loc[:, columns] = matched[columns].to_numpy()
    return result


def atomic_write_csv(data: pd.DataFrame, path: Path) -> None:
    """Write a complete checkpoint atomically."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    data.to_csv(temporary, index=False)
    os.replace(temporary, path)


def pending_indices(data: pd.DataFrame) -> list[int]:
    """Return rows without a valid classification."""
    complete = data["llm_strategies_openai"].map(parse_saved_list).notna()
    return data.index[~complete].tolist()


def run_classification(
    data: pd.DataFrame,
    client: OpenAI,
    config: Config,
) -> pd.DataFrame:
    """Classify missing rows concurrently and checkpoint progress."""
    pending = pending_indices(data)
    if not pending:
        print(f"All {len(data):,} excerpts already have reusable results.")
        return data
    print(f"Classifying {len(pending):,} excerpts with {config.model} (low reasoning)...")

    def submit(index: int) -> tuple[int, list[str], str, int]:
        row = data.loc[index]
        strategies, response_id, timestamp = classify_excerpt(
            client=client,
            model=config.model,
            excerpt=row["full_content"],
            user_id=row["user_id_raw"],
            max_attempts=config.max_attempts,
        )
        return index, strategies, response_id, timestamp

    failures: list[tuple[int, str]] = []
    completed = 0
    with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
        futures = {executor.submit(submit, index): index for index in pending}
        for future in as_completed(futures):
            index = futures[future]
            try:
                row_index, strategies, response_id, timestamp = future.result()
                data.at[row_index, "llm_strategies_openai"] = json.dumps(strategies)
                data.at[row_index, "classification_model"] = config.model
                data.at[row_index, "openai_response_id"] = response_id
                data.at[row_index, "classification_timestamp_unix"] = timestamp
                completed += 1
                print(f"Completed {completed:,}/{len(pending):,}")
            except Exception as exc:
                failures.append((index, str(exc)))
            if completed and completed % config.checkpoint_every == 0:
                atomic_write_csv(data, config.output_path)

    atomic_write_csv(data, config.output_path)
    if failures:
        examples = "; ".join(f"row {index}: {error}" for index, error in failures[:5])
        raise RuntimeError(f"{len(failures)} rows failed. Examples: {examples}")
    return data


def make_share_table(data: pd.DataFrame) -> pd.DataFrame:
    """Compute treatment shares from the structured category lists."""
    labels = {
        "Ambivalence": "Decisional Balance",
        "Persuasion": "Direct Persuasion",
    }
    working = data[["user_id_raw", "T", "llm_strategies_openai"]].copy()
    working["T"] = working["T"].replace(labels)
    working["strategy"] = working["llm_strategies_openai"].map(
        lambda value: parse_saved_list(value) or []
    )
    long = working.explode("strategy").dropna(subset=["strategy"])
    counts = (
        long.groupby(["strategy", "T"])["user_id_raw"]
        .nunique()
        .rename("participants_mentioning")
        .reset_index()
    )
    totals = working.groupby("T")["user_id_raw"].nunique().rename("participants")
    result = counts.merge(totals, on="T")
    result["share"] = result["participants_mentioning"] / result["participants"]
    return result


def create_figure(summary: pd.DataFrame) -> plt.Figure:
    """Draw the same grouped horizontal-bar design as the original notebook."""
    order = ["Change Talk", "Decisional Balance", "Direct Persuasion"]
    table = summary.pivot(index="strategy", columns="T", values="share").fillna(0)
    table = table.reindex(columns=order, fill_value=0)
    table.index = table.index.str.capitalize()
    table = table.sort_values("Change Talk", ascending=True)

    set_plot_theme()
    fontsize = 18
    plt.rcParams.update(
        {
            "font.size": fontsize,
            "axes.titlesize": fontsize,
            "axes.labelsize": fontsize,
            "xtick.labelsize": fontsize,
            "ytick.labelsize": fontsize,
            "legend.fontsize": fontsize - 2,
        }
    )
    cycle = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    colors = {
        "Change Talk": cycle[0],
        "Direct Persuasion": cycle[1],
        "Decisional Balance": cycle[2],
    }
    figure, axis = plt.subplots(figsize=(11, 8))
    group_height = 0.8
    bar_height = group_height / len(order)
    positions = np.arange(len(table))
    for offset, treatment in enumerate(order):
        y = positions - group_height / 2 + offset * bar_height + bar_height / 2
        axis.barh(
            y,
            table[treatment].to_numpy(),
            height=bar_height,
            label=treatment,
            color=colors[treatment],
        )
    axis.set_yticks(positions)
    axis.set_yticklabels(table.index)
    axis.set_xlabel("Share of participants mentioning strategy")
    axis.legend(
        title=None,
        frameon=True,
        loc="lower right",
        fancybox=False,
        edgecolor="black",
        facecolor="white",
        framealpha=1.0,
    )
    sns.despine(ax=axis)
    return figure


def save_figure(figure: plt.Figure, paths: Sequence[Path]) -> None:
    """Save identical local and manuscript figure copies."""
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(path, bbox_inches="tight")
        print(f"Saved figure: {path}")


def main() -> None:
    """Run classification, summary generation, and figure creation."""
    script_dir = Path(__file__).resolve().parent
    load_dotenv(script_dir / ".env")
    config = make_config(script_dir, dict(os.environ))
    source = load_source(config.input_path)
    results = add_checkpoint(source, config.output_path, config.model)
    if pending_indices(results):
        client = OpenAI(api_key=get_api_key(dict(os.environ)), max_retries=2)
        results = run_classification(results, client, config)
    atomic_write_csv(results, config.output_path)
    summary = make_share_table(results)
    atomic_write_csv(summary, config.summary_path)
    figure = create_figure(summary)
    save_figure(figure, (config.local_figure_path, config.paper_figure_path))
    plt.close(figure)


if __name__ == "__main__":
    main()
