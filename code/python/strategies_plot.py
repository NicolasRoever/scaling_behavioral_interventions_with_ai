from __future__ import annotations
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from helper import set_plot_theme

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
