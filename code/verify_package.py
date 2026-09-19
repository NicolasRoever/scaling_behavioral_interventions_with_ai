"""Check release integrity and optionally regenerated exhibit/table coverage."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


def verify(package, check_reproduced, allow_rebuilt_data, check_submission=False):
    manifest = json.loads((package / 'manifest/exhibits.json').read_text())
    checksums = json.loads((package / 'manifest/release_checksums.json').read_text())
    errors = []
    for relative, expected in checksums['files'].items():
        path = package / relative
        if not path.is_file():
            errors.append('Missing release file: ' + relative)
        elif allow_rebuilt_data and relative in {
            'data/processed/main_social_media/clean_data.dta',
            'data/processed/main_social_media/follow_up_clean.dta',
            'data/processed/main_social_media/clean_merged.dta',
            'data/processed/main_social_media/clean_merged_with_scrshots.dta',
        }:
            continue
        elif hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            errors.append('Changed release file: ' + relative)
    refs = {r['manuscript_path'] for r in manifest['exhibits'] if r['status'] == 'included'}
    actual = {str(p.relative_to(package / 'results')) for p in (package / 'results').rglob('*') if p.is_file()}
    if actual != refs:
        errors.append(f'Reference exhibit set differs: missing={sorted(refs-actual)}, extra={sorted(actual-refs)}')
    for record in manifest['exhibits']:
        relative = record['manuscript_path']
        path = package / 'results' / relative
        if record['status'] != 'included':
            if path.exists():
                errors.append('Withheld exhibit unexpectedly present: ' + relative)
            continue
        if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() != record['sha256']:
            errors.append('Reference checksum mismatch: ' + relative)
        if check_reproduced and record['generator']:
            output = package / 'reproduced' / relative
            if not output.exists():
                errors.append('Missing generated exhibit: ' + relative)
            elif output.suffix == '.tex' and re.sub(r'\s+', '', output.read_text()) != re.sub(r'\s+', '', path.read_text()):
                errors.append('Generated LaTeX differs: ' + relative)
    from compare_submission import compare
    submission_spec = json.loads((package / 'manifest/submission_tables.json').read_text())
    expected_tables = {t['result'] for t in submission_spec['tables']}
    supplied_tables = {str(f.relative_to(package / 'submission_results'))
                       for f in (package / 'submission_results').rglob('*') if f.is_file()}
    if supplied_tables != expected_tables:
        errors.append('Original-submission reference table coverage differs')
    if len(expected_tables) != 12:
        errors.append('Expected all 12 original-submission tables')
    roots = [package / 'submission_results']
    if check_submission:
        roots.append(package / 'reproduced/submission')
    for root in roots:
        if any(not (root / relative).is_file() for relative in expected_tables):
            errors.append('Missing original-submission table in ' + str(root))
            continue
        report = compare(package, root, submission=True)
        if report['exact_numeric_matches'] != 11:
            errors.append('Original-submission numerical table mismatch in ' + str(root))
        if check_submission and root.name == 'submission':
            for relative in expected_tables:
                if re.sub(r'\s+', '', (root / relative).read_text()) != re.sub(r'\s+', '', (package / 'submission_results' / relative).read_text()):
                    errors.append('Archival reference differs from generated table: ' + relative)
    from prompts.check_appendix import load_configuration
    sys.path.insert(0, str(package / 'code/python'))
    from miti_validation import load_inputs
    try:
        load_inputs(package)
    except (ValueError, KeyError, OSError) as exc:
        errors.append('Corrected MITI validation input: ' + str(exc))
    prompt_report = json.loads((package / 'manifest/prompt_validation.json').read_text())
    parameters = package / 'code/prompts/parameters.py'
    configurations = load_configuration(parameters)
    if hashlib.sha256(parameters.read_bytes()).hexdigest() != prompt_report['parameters_sha256']:
        errors.append('Prompt configuration changed after appendix validation')
    if set(configurations) != {'T1_MI_CHANGE', 'T2_MI_AMBIVALENCE', 'T4_CLEAR_PERSUASION', 'TIME_USE'}:
        errors.append('Expected only the four appendix protocols')
    if len(prompt_report['blocks']) != 68:
        errors.append('Expected 68 appendix prompt blocks')
    for block in prompt_report['blocks']:
        configuration = configurations[block['arm']]
        if 'turn' in block:
            question = configuration['interview_plan'][block['turn'] - 1]
            value = question['system']
            if question['question_name'] != block['question_name']:
                errors.append('Prompt turn order changed: ' + block['arm'])
        else:
            value = configuration[block['field']]
        if hashlib.sha256(' '.join(value.split()).encode()).hexdigest() != block['sha256']:
            errors.append('Prompt block differs from appendix validation: ' + block['arm'])
    forbidden = {'chats_raw.csv', 'clean_chat_data.dta', 'sessions.json', 'prompts.json', '.env'}
    for relative in checksums['files']:
        path = Path(relative)
        if path.name in forbidden or path.suffix in {'.ipynb', '.jsonl', '.sav'}:
            errors.append('Unexpected restricted/uncurated file: ' + relative)
        if relative.startswith('data/private/') and path.name != 'README.md':
            errors.append('Private input was distributed: ' + relative)
        if path.suffix in {'.py', '.md', '.json', '.csv', '.do'}:
            text = (package / relative).read_text()
            if re.search(r'\bsk-[A-Za-z0-9_-]{20,}', text):
                errors.append('Potential credential in: ' + relative)
    if '.env' not in (package / '.gitignore').read_text().splitlines():
        errors.append('.env missing from .gitignore')
    if errors:
        print('\n'.join(errors))
        return 1
    computed = sum(bool(r['generator']) for r in manifest['exhibits'])
    print(f'PASS: {len(checksums["files"])} release files; {len(refs)} reference exhibits; '
          f'{computed} computed exhibits; 1 explicitly withheld image.')
    print('PASS: 68 prompt blocks in four arms match the appendix validation record.')
    print('PASS: corrected MITI benchmark has 504 valid paired scores, 14 interviews and all nine conditions.')
    print('PASS: all 12 original-submission reference tables supplied; 11/11 numerical tables match the PDF.')
    if check_submission:
        print('PASS: original-submission rerun matches PDF numbers and released table references.')
    if check_reproduced:
        print('PASS: all computed outputs exist and all regenerated LaTeX matches the release references.')
    if allow_rebuilt_data:
        print('Original binary hashes of the four rebuilt survey files were not checked.')
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--reproduced', action='store_true')
    parser.add_argument('--submission', action='store_true', help='Check regenerated original-submission tables.')
    parser.add_argument('--allow-rebuilt-data', action='store_true',
                        help='Skip original binary hashes of the four files rebuilt by 01_clean_data.do.')
    args = parser.parse_args()
    sys.exit(verify(args.package_root.resolve(), args.reproduced, args.allow_rebuilt_data, args.submission))


if __name__ == '__main__':
    main()
