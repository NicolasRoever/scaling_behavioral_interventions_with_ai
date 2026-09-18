from __future__ import annotations
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from helper import set_plot_theme, finalize_plot

def main(data_dir, output_dir):
    # Load data
    df = pd.read_stata(data_dir / "processed/main_social_media/clean_data.dta")
    df["T"] = df["T"].replace("Ambivalence", "Decisional Balance")
    df["T"].value_counts()
    
    # ---------------------------------------------------------
    # Figure 1: CDF of Importance Score
    # ---------------------------------------------------------
    # Filter: keep non-missing T and importance_score, and importance_score <= 10
    mask_imp = df["T"].notna() & df["importance_score"].notna() & (df["importance_score"] <= 10)
    df_imp = df.loc[mask_imp].copy()
    
    # Plot setup
    plt.figure(figsize=(5, 4))  # xsize(4) ysize(4) in Stata
    set_plot_theme()
    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    
    # ECDF plot
    sns.ecdfplot(
        data=df_imp,
        x="importance_score",
        hue="T",
        linewidth=1.5,
        palette=[colors[0], colors[1], colors[2]],  # Change Talk, Ambivalence, Direct Persuasion
    )
    
    # Legend customization (replicating Stata manual legend)
    # Note: Seaborn auto-generates legend. To manually set labels/position:
    plt.legend(
        title="",
        labels=["Change Talk", "Decisional Balance", "Direct Persuasion"],
        loc="upper left",       # pos(4) in Stata (4 o'clock)
        frameon=True,
        fancybox=False,
        edgecolor="black",       # region(lcolor(black))
        framealpha=1, 
        fontsize=12
    )
    plt.gca().get_legend().get_frame().set_linewidth(0.1) # lwidth(0.1)
    
    plt.xlabel("Importance Score")
    plt.ylabel("Proportion") # Standard CDF label
    plt.title("")
    finalize_plot(ax=plt.gca())
    # Save
    plt.savefig(os.path.join(output_dir, "fig_cdf_importance_score.pdf"), bbox_inches="tight")
    plt.close("all")
    
    
    
    # ---------------------------------------------------------
    # Figure 2: CDF of Confidence Score
    # ---------------------------------------------------------
    # Filter: keep non-missing T and confidence_score, and confidence_score <= 10
    mask_imp = df["T"].notna() & df["confidence_score"].notna() & (df["confidence_score"] <= 10)
    df_imp = df.loc[mask_imp].copy()
    
    # Plot setup
    plt.figure(figsize=(5, 4))  # xsize(4) ysize(4) in Stata
    set_plot_theme()
    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    
    # ECDF plot
    sns.ecdfplot(
        data=df_imp,
        x="confidence_score",
        hue="T",
        linewidth=1.5,
        palette=[colors[0], colors[1], colors[2]],  # Change Talk, Ambivalence, Direct Persuasion
    )
    
    # Legend customization (replicating Stata manual legend)
    # Note: Seaborn auto-generates legend. To manually set labels/position:
    plt.legend(
        title="",
        labels=["Change Talk", "Decisional Balance", "Direct Persuasion"],
        loc="upper left",       # pos(4) in Stata (4 o'clock)
        frameon=True,
        fancybox=False,
        edgecolor="black",       # region(lcolor(black))
        framealpha=1, 
        fontsize=12
    )
    plt.gca().get_legend().get_frame().set_linewidth(0.1) # lwidth(0.1)
    
    plt.xlabel("Confidence Score")
    plt.ylabel("Proportion") # Standard CDF label
    plt.title("")
    finalize_plot(ax=plt.gca())
    # Save
    plt.savefig(os.path.join(output_dir, "fig_cdf_confidence_score.pdf"), bbox_inches="tight")
    plt.close()
    plt.close("all")
    
