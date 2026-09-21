"""Reproduce Python manuscript exhibits offline from text-free saved results.

Run from any directory: python code/python/run_public.py
No source in code/private is imported, and no network/API client is used.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import time

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import bertopic_plot
import cdf_scores
import language_similarity
import mentions_table
import miti_metrics
import miti_tables
import miti_validation
import pros_cons_plot
import question_sequence
import strategies_plot
import topic_diagnostics
import wordcloud_plot


def build_miti(folder, survey_path, out):
    manifest = json.loads((folder / 'manifest.json').read_text())
    runs = manifest['runs']
    frames = {}
    for run in runs:
        path = folder / run['file']
        if hashlib.sha256(path.read_bytes()).hexdigest() != run['sha256']:
            raise ValueError(f"Saved MITI score file changed: {run['file']}")
        frame = pd.read_csv(path, dtype={'session_id': str})
        if len(frame) != run['rows'] or frame.duplicated(['session_id', 'miti_dimension']).any():
            raise ValueError('Incomplete or duplicate score keys')
        if not frame.score.isin([1, 2, 3, 4, 5]).all():
            raise ValueError('Invalid MITI score')
        for key in ['run_id', 'dataset', 'model', 'condition', 'replicate', 'prompt_variant']:
            if not frame[key].eq(run[key]).all():
                raise ValueError(f'Mixed metadata: {key}')
        frames[run['run_id']] = frame
    arms = miti_tables.arm_assignments(survey_path)
    treated_n = int(arms['T'].isin([1, 2, 3]).sum())
    if treated_n != 2048:
        raise ValueError(f'Expected 2,048 eligible treated participants; found {treated_n:,}')
    sample_audit = {
        'file': 'data/processed/main_social_media/clean_merged_with_scrshots.dta',
        'sha256': hashlib.sha256(survey_path.read_bytes()).hexdigest(),
        'runs': {},
    }
    # Apply the current source's survey eligibility rule before all experimental
    # comparisons. Human validation retains its separate 14-session sample.
    for run in runs:
        if run['dataset'] in ['treated', 'control']:
            frame = frames[run['run_id']]
            eligible, audit = miti_tables.attach_arms(frame, arms)
            arm_mask = arms['T'].eq(0) if run['dataset'] == 'control' else arms['T'].isin([1, 2, 3])
            expected = set(arms.loc[arm_mask, 'user_id_raw'])
            if set(eligible.user_id_raw) != expected:
                raise ValueError(f"Eligible sample coverage mismatch: {run['run_id']}")
            frames[run['run_id']] = eligible[frame.columns].copy()
            sample_audit['runs'][run['run_id']] = dict(
                audit, eligible_sessions=eligible.session_id.nunique())
    plt.rcParams.update({'font.family': 'Arial', 'font.size': 10,
                         'axes.spines.top': False, 'axes.spines.right': False})
    procedures = miti_tables.procedure_frames(runs, frames, 'treated')
    rows = []
    for label, comparison in procedures.items():
        if label != 'Benchmark':
            rows += miti_tables.comparison_rows(procedures['Benchmark'], comparison, label,
                'Luna benchmark', manifest['dimensions'], miti_metrics.score_metrics)
    for run in runs:
        if run['dataset'] == 'treated' and run['condition'] == 'rerun':
            rows += miti_tables.comparison_rows(procedures['Benchmark'], frames[run['run_id']],
                f"Stochastic rerun {run['replicate']}", 'Luna benchmark', manifest['dimensions'], miti_metrics.score_metrics)
    miti_tables.write_table(pd.DataFrame(rows), out, 'robustness_summary_table')
    control = next(frames[r['run_id']] for r in runs if r['dataset'] == 'control')
    data, audit = miti_tables.attach_arms(pd.concat([procedures['Benchmark'], control]), arms)
    (out / 'survey_sample_audit.json').write_text(
        json.dumps(dict(audit, eligible_sample=sample_audit), indent=2) + '\n')
    miti_tables.build_main_figures(data, manifest['dimensions'], out)
    miti_tables.build_stability(procedures, manifest['dimensions'], out)


def build_all(package, out):
    derived = package / 'data/derived'
    cdf_scores.main(package / 'data', out)
    plt.rcdefaults()
    bertopic_plot.main(derived, out)
    metrics = pd.read_csv(derived / 'topic_seed_stability_metrics.csv')
    summary = topic_diagnostics.summarize_metrics(metrics, .5, .7)
    supplied = pd.read_csv(derived / 'topic_seed_stability_summary.csv')
    pd.testing.assert_frame_equal(summary, supplied, check_dtype=False, rtol=1e-10)
    plt.rcdefaults()
    topic_diagnostics.save_stability_figure(summary, out / 'fig_topic_seed_stability.pdf', .7, .5, metrics.seed.nunique())
    plt.rcdefaults()
    topic_diagnostics.save_elbow_figure(pd.read_csv(derived / 'topic_robustness_elbow.csv'), out / 'fig_topic_robustness_elbow.pdf')
    plt.rcdefaults()
    counts = pd.read_csv(derived / 'pros_cons_counts.csv')
    figure = pros_cons_plot.create_figure(counts)
    figure.savefig(out / 'fig_number_pro_con_statements.pdf', bbox_inches='tight')
    plt.close(figure)
    plt.rcdefaults()
    strategies = pd.read_csv(derived / 'strategy_categories.csv')
    shares = strategies_plot.make_share_table(strategies)
    shares.to_csv(out / 'strategy_shares.csv', index=False)
    figure = strategies_plot.create_figure(shares)
    figure.savefig(out / 'fig_strategies.pdf', bbox_inches='tight')
    plt.close(figure)
    plt.rcdefaults()
    panels, category_colors = question_sequence.configuration()
    question_sequence.plot_question_sequence(panels, category_colors, out / 'qtype_shares_manual.pdf')
    table = pd.read_csv(derived / 'similarity_by_topic.csv')
    plt.rcdefaults()
    language_similarity.build(table, panels, out / 'similarity_by_topic.pdf')
    plt.rcdefaults()
    wordcloud_plot.make_figure(pd.read_csv(derived / 'keyness_by_arm.csv'), out / 'wordclouds_by_arm.pdf', wordcloud_plot.configuration())
    mentions = pd.read_csv(derived / 'thirty_minute_mentions_by_chat.csv')
    columns = list(mentions.columns[2:])
    labels = {1: 'Change Talk', 2: 'Decisional Balance', 3: 'Direct Persuasion'}
    percentages = mentions.groupby('T')[columns].mean().mul(100).T.reindex(columns=labels).rename(columns=labels)
    (out / 'tab_thirty_minute_mentions.tex').write_text(mentions_table.overleaf_table(percentages))
    percentages.to_csv(out / 'thirty_minute_mentions_percentages.csv')
    plt.rcdefaults()
    build_miti(derived / 'miti',
               package / 'data/processed/main_social_media/clean_merged_with_scrshots.dta', out)
    miti_validation.build_validation(package, out)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package-root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--output-root', type=Path)
    args = parser.parse_args()
    package = args.package_root.resolve()
    destination = args.output_root or package / 'reproduced'
    print('Additional API/compute cost: $0. Model requests: 0.', flush=True)
    with tempfile.TemporaryDirectory(prefix='mi_public_') as temporary:
        out = Path(temporary)
        build_all(package, out)
        refs = json.loads((package / 'manifest/exhibits.json').read_text())['exhibits']
        by_name = {Path(r['manuscript_path']).name:r['manuscript_path'] for r in refs}
        written = []
        for path in out.iterdir():
            relative = by_name.get(path.name, 'audit/' + path.name)
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
            written.append(relative)
    report = {'completed_at_unix': int(time.time()), 'api_requests': 0,
              'additional_cost_usd': 0, 'files': sorted(written)}
    (destination / 'python_run.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f'REPLICATION_PYTHON_COMPLETE: {len(written)} files in {destination}', flush=True)


if __name__ == '__main__':
    main()
