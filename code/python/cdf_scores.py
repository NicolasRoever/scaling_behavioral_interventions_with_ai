"""Scaling-question CDFs with explicit numeric treatment/color mapping."""
from __future__ import annotations
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from helper import set_plot_theme, finalize_plot


def plot_cdf(data, outcome, xlabel, output):
    arms = {1: 'Change Talk', 2: 'Decisional Balance', 3: 'Direct Persuasion'}
    selected = data.loc[data['T'].isin(arms) & data[outcome].notna() & data[outcome].le(10)].copy()
    set_plot_theme()
    palette = plt.rcParams['axes.prop_cycle'].by_key()['color']
    colors = {1: palette[0], 2: palette[2], 3: palette[1]}
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.ecdfplot(data=selected, x=outcome, hue='T', hue_order=list(arms),
                 palette=colors, linewidth=1.5, legend=False, ax=ax)
    handles = [Line2D([0], [0], color=colors[arm], linewidth=1.5, label=label)
               for arm, label in arms.items()]
    legend = ax.legend(handles=handles, title='', loc='upper left', frameon=True,
                       fancybox=False, edgecolor='black', framealpha=1, fontsize=12)
    legend.get_frame().set_linewidth(0.1)
    ax.set(xlabel=xlabel, ylabel='Proportion', title='')
    finalize_plot(ax=ax)
    fig.savefig(output, bbox_inches='tight')
    plt.close(fig)


def main(data_dir, output_dir):
    # Numeric codes avoid unused categorical levels changing the palette order.
    data = pd.read_stata(data_dir / 'processed/main_social_media/clean_data.dta',
                        convert_categoricals=False)
    for outcome, label in [('importance_score', 'Importance Score'),
                           ('confidence_score', 'Confidence Score')]:
        plot_cdf(data, outcome, label, output_dir / ('fig_cdf_' + outcome + '.pdf'))
