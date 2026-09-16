"""Check release integrity and optionally regenerated exhibit/table coverage."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


def verify(package, check_reproduced, allow_rebuilt_data):
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
            errors.append('Reference differs from manuscript: ' + relative)
        if check_reproduced and record['generator']:
            output = package / 'reproduced' / relative
            if not output.exists():
                errors.append('Missing generated exhibit: ' + relative)
            elif output.suffix == '.tex' and re.sub(r'\s+', '', output.read_text()) != re.sub(r'\s+', '', path.read_text()):
                errors.append('Generated LaTeX differs: ' + relative)
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
    if check_reproduced:
        print('PASS: all computed outputs exist and all regenerated LaTeX matches the manuscript.')
    if allow_rebuilt_data:
        print('Original binary hashes of the four rebuilt survey files were not checked.')
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--reproduced', action='store_true')
    parser.add_argument('--allow-rebuilt-data', action='store_true',
                        help='Skip original binary hashes of the four files rebuilt by 01_clean_data.do.')
    args = parser.parse_args()
    sys.exit(verify(args.package_root.resolve(), args.reproduced, args.allow_rebuilt_data))


if __name__ == '__main__':
    main()
