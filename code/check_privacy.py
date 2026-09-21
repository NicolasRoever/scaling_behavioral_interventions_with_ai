"""Check anonymous survey identifiers and detect exposed platform-ID patterns.

Checks working files, including untracked files, but never opens .git or follows
symlinks. Error messages contain paths and column names, never identifier values.
Release preparation additionally compares all files and PDF text against known
source identifiers and audits local Git objects; see the privacy manifest.
"""
import argparse
from pathlib import Path
import re
import sys

import pandas as pd


def identifier_pattern_present(payload):
    # The source manuscript's directory key is a document ID, not a participant.
    payload = re.sub(rb'analysis_NR/[0-9a-fA-F]{24}(?=/|["\'\s])', b'analysis_NR/MANUSCRIPT', payload)
    payload = re.sub(rb'["\']analysis_NR["\']\s*/\s*["\'][0-9a-fA-F]{24}["\']', b'MANUSCRIPT_PATH', payload)
    return re.search(rb'(?<![0-9a-fA-F])[0-9a-fA-F]{24}(?![0-9a-fA-F])|R_[A-Za-z0-9]{15}', payload) is not None


def anonymous_identifier_valid(value, family):
    if pd.isna(value) or value == '':
        return True
    return re.fullmatch(family + r'\d{5}', str(value)) is not None or re.fullmatch(r'MISSING_ROW_\d+', str(value)) is not None


def privacy_errors(package):
    errors = []
    for path in sorted(package.rglob('*')):
        relative = path.relative_to(package)
        if '.git' in relative.parts or '__pycache__' in relative.parts:
            continue
        if path.is_symlink():
            errors.append('Review symlink before release: ' + str(relative))
            continue
        if not path.is_file():
            continue
        if path.name == '.env' or path.name.startswith('.env.'):
            errors.append('Credential file must not be distributed: ' + str(relative))
            continue
        if identifier_pattern_present(path.read_bytes()):
            errors.append('Potential platform identifier in: ' + str(relative))
        if path.suffix != '.dta':
            continue
        try:
            data = pd.read_stata(path, convert_categoricals=False, convert_dates=False)
        except (ValueError, OSError) as exc:
            errors.append('Cannot inspect Stata file: ' + str(relative) + ' (' + type(exc).__name__ + ')')
            continue
        for column in data:
            family = 'P' if 'prolific' in column.lower() else 'R' if column in {'responseid', 'response_id', 'w2_response_id'} else None
            if family and not data[column].map(lambda value: anonymous_identifier_valid(value, family)).all():
                errors.append('Nonanonymous identifier values: ' + str(relative) + '/' + column)
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package-root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = privacy_errors(args.package_root.resolve())
    if errors:
        print('\n'.join(errors))
        return 1
    print('PASS: anonymous survey IDs only; no exposed Prolific/Qualtrics ID patterns in working files.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
