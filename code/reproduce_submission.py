"""Reconstruct the original submission's table specifications using saved inputs.

This archival route deliberately retains the published reporting errors listed
in SUBMISSION_TABLE_AUDIT.md. It does not alter the corrected default scripts.
No API requests are made. Requires Stata 17 and the public Python dependencies.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from compare_submission import compare


def replace_checked(text, old, new, count=1):
    if text.count(old) != count:
        raise ValueError('Source changed; review archival adaptation: ' + old)
    return text.replace(old, new)


def submission_script(name, text):
    if name in {'tab_balance.do', 'tab_balance_followup.do'}:
        text = replace_checked(text, 'rename baseline_actual_social_min actual_social_short',
                               'rename baseline_actual_social_min_w actual_social_short')
    elif name == 'tab_attrition_sm.do':
        # The published "control group mean" was the overall completion mean.
        text = replace_checked(text, 'summarize followup_finished if e(sample) & T == 0, meanonly',
                               'summarize followup_finished if e(sample), meanonly')
    elif name == 'tab_heterogeneity_timeuse_by_basetime.do':
        # Published split used follow-up use, including missing values in high.
        text = replace_checked(text, 'summ baseline_actual_social_min, de', 'summ w2_actual_social_min, de')
        text = replace_checked(text,
            'gen high = baseline_actual_social_min > r(p50) if !missing(baseline_actual_social_min)',
            'gen high = w2_actual_social_min > r(p50)')
    if name in {'tab_heterogeneity_timeuse_by_basetime.do', 'tab_heterogeneity_timeuse_by_wedge.do'}:
        # Reproduce the published duplicated b=c p-values under the a=c label.
        # Correct tests remain in the default analysis scripts.
        text = replace_checked(text, '    test 1.T = 3.T\n', '', 2)
    return '* ARCHIVAL SPECIFICATION: see SUBMISSION_TABLE_AUDIT.md\n' + text


def run_stata_tables(package, stata, output):
    specification = json.loads((package / 'manifest/submission_tables.json').read_text())
    exhibits = json.loads((package / 'manifest/exhibits.json').read_text())['exhibits']
    by_path = {r['manuscript_path']: r for r in exhibits}
    generators = list(dict.fromkeys(by_path[t['result']]['generator'] for t in specification['tables']
                                   if t['table'] not in {'1', 'C.1'}))
    with tempfile.TemporaryDirectory(prefix='submission_tables_') as directory:
        work = Path(directory)
        code = work / 'code/stata'
        shutil.copytree(package / 'code/stata', code)
        # The original submission predates the fully updated follow-up export.
        # Use only its explicitly frozen deidentified analysis inputs.
        snapshot = json.loads((package / 'manifest/submission_survey_snapshot.json').read_text())
        data = work / 'data/processed/main_social_media'
        data.mkdir(parents=True)
        expected = {'clean_data.dta', 'clean_merged.dta', 'clean_merged_with_scrshots.dta'}
        if {row['analysis_filename'] for row in snapshot['files']} != expected:
            raise ValueError('Incomplete original-submission survey snapshot')
        for row in snapshot['files']:
            source = package / row['file']
            if hashlib.sha256(source.read_bytes()).hexdigest() != row['sha256']:
                raise ValueError('Original-submission input changed: ' + row['file'])
            (data / row['analysis_filename']).symlink_to(source)

        (work / 'ado').mkdir()
        for generator in generators:
            name = Path(generator).name
            path = code / name
            path.write_text(submission_script(name, path.read_text()))
        wrapper = work / 'submission.do'
        wrapper.write_text(f'sysdir set PERSONAL "{work}/ado"\ncd "{code}"\ndo 00_setup.do\n'
                           + ''.join(f'do {Path(g).name}\n' for g in generators)
                           + 'display "SUBMISSION_STATA_COMPLETE"\n')
        process = subprocess.run([stata, '-b', 'do', str(wrapper)], cwd=work, capture_output=True, text=True)
        log_path = work / 'submission.log'
        log = log_path.read_text(errors='replace') if log_path.exists() else process.stdout + process.stderr
        (output / 'stata.log').write_text(log)
        if process.returncode or 'SUBMISSION_STATA_COMPLETE\n' not in log:
            raise RuntimeError('Stata did not complete; inspect reproduced/submission/stata.log')
        for table in specification['tables']:
            if table['table'] in {'1', 'C.1'}:
                continue
            target = output / table['result']
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(work / 'reproduced' / table['result'], target)


def build_original_validation(package, output):
    import pandas as pd
    sys.path.insert(0, str(package / 'code/python'))
    from miti_tables import latex_table
    data = pd.read_csv(package / 'data/derived/submission_miti_global_pairs.csv')
    if len(data) != 80 or data.session_id.nunique() != 20 or data.duplicated(['session_id', 'miti_dimension']).any():
        raise ValueError('Expected 20 original validation sessions and four score pairs per session')
    if not data[['human_score', 'model_score']].isin(range(1, 6)).all().all():
        raise ValueError('Invalid validation scores')
    rows = [['A. Global Metrics', '', '']]
    metrics = []
    for dimension in ['Global', 'Partnership', 'Cultivating Change Talk', 'Empathy', 'Softening Sustain Talk']:
        values = data if dimension == 'Global' else data[data.miti_dimension.eq(dimension)]
        bias = (values.model_score - values.human_score).mean()
        correlation = values.model_score.corr(values.human_score)
        rows.append([dimension, f'{bias:.2f}', f'{correlation:.2f}'])
        metrics.append(dict(dimension=dimension, score_pairs=len(values), bias=bias, correlation=correlation))
    rows.append(['B. Behavioral Counts', '', ''])
    behavioral = pd.read_csv(package / 'data/derived/miti/inputs/behavioral_results.csv').set_index('Category')
    for category in ['Share Complex Reflections', 'Reflection-to-Question Ratio', 'Total MI-Adherent Behavior',
                     'Total MI Non-Adherent Behavior', 'Reflection Correlation']:
        row = behavioral.loc[category]
        rows.append([category, f'{row.Bias:.2f}' if pd.notna(row.Bias) else '', f'{row.Correlation:.2f}'])
    latex_table(['Score Category', 'Bias', 'Correlation'], rows,
                output / 'tables/mi_validation_results_table.tex', 'p{10cm}rr')
    (output / 'validation_metrics.json').write_text(json.dumps(metrics, indent=2) + '\n')


def build_protocol_table(package, output):
    source = package / 'results/tables/manual/tab_treatment_description.tex'
    text = replace_checked(source.read_text(), 'Actively counter-argues', 'Actively counter-argue')
    text = replace_checked(text, 'Actively pushes the participant to commit', 'Actively push the participant to committing')
    text = replace_checked(text, 'judgment from the interviewer', 'judgement from the interviewer')
    target = output / 'tables/manual/tab_treatment_description.tex'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--stata', required=True, help='Path to the Stata 17+ command-line executable')
    args = parser.parse_args()
    package = args.package_root.resolve()
    output = package / 'reproduced/submission'
    output.mkdir(parents=True, exist_ok=True)
    print('Archival original-submission tables; expected API/compute cost $0; zero model requests.', flush=True)
    run_stata_tables(package, args.stata, output)
    build_original_validation(package, output)
    build_protocol_table(package, output)
    report = compare(package, output, submission=True)
    (output / 'comparison.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f"Original submission: {report['exact_numeric_matches']}/{report['numeric_tables']} numeric tables match.")
    if report['exact_numeric_matches'] != report['numeric_tables']:
        raise SystemExit('Original submission mismatch; inspect reproduced/submission/comparison.json')
    print('SUBMISSION_REPRODUCTION_COMPLETE')


if __name__ == '__main__':
    main()
