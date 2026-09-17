"""Compare numeric table entries with the original submission (offline).

Expected cells were extracted from ssrn-6081126.pdf and visually checked.
The comparison preserves significance stars, normalizes signed zero, and
reports differences without changing the analysis to fit published numbers.
"""
import argparse
from decimal import Decimal
import json
from pathlib import Path
import re
import time
import unicodedata


def label_key(text):
    text=unicodedata.normalize('NFKC',text)
    text=re.sub(r'\\(?:textsuperscript|textit|textbf)\{([^}]+)\}',r'\1',text)
    text=re.sub(r'\([abc]\)','',text)
    return re.sub(r'[^a-z0-9]','',text.lower())


def parse_cell(text):
    text=re.sub(r'\\sym\{(\*+)\}',r'\1',text).strip()
    if text in {'','--','-'}:return None
    if text=='Yes':return 'Yes'
    match=re.fullmatch(r'\(?([-+]?\d[\d,]*(?:\.\d+)?)(\**)(?:\))?',text)
    if not match:raise ValueError(text)
    number=Decimal(match.group(1).replace(',',''))
    if number==0:number=Decimal(0)
    return format(number,'f')+match.group(2)


def equal_cell(left,right):
    if left is None or right is None or left=='Yes' or right=='Yes':return left==right
    return Decimal(left.rstrip('*'))==Decimal(right.rstrip('*')) and left.count('*')==right.count('*')


def tex_rows(text):
    rows={};last=''
    for chunk in re.split(r'\\\\',text):
        if '&' not in chunk:continue
        cells=chunk.split('&');label=cells[0].strip()
        label=re.sub(r'\\(?:toprule|midrule|bottomrule|addlinespace)\s*','',label).strip()
        label=re.sub(r'\\cmidrule(?:\([^)]*\))?\{[^}]*\}\s*','',label).strip()
        try:values=[parse_cell(c) for c in cells[1:]]
        except ValueError:continue
        if not any(v is not None for v in values):continue
        if not label:
            if not last or not all(c.strip().startswith('(') for c in cells[1:] if c.strip()):continue
            key=last+'__se'
        else:key=label_key(label);last=key
        # The PDF omits the blank sample-mean cell in the joint-test row.
        if key == 'pvalueofjointftest' and values[0] is None:
            values = values[1:]
        rows[key]=values
    return rows


def compare_table(expected,actual,column_indices=None):
    differences=[];checked=0
    for row,values in expected.items():
        observed=actual.get(row)
        if observed is not None and column_indices is not None:
            observed=[observed[i] if i<len(observed) else None for i in column_indices]
        for index,value in enumerate(values):
            checked+=1;got=observed[index] if observed is not None and index<len(observed) else None
            if not equal_cell(value,got):differences.append({'row':row,'column':index+1,'pdf':value,'replicated':got})
        if observed is not None and len(observed)!=len(values):
            differences.append({'row':row,'pdf_columns':len(values),'replicated_columns':len(observed)})
    return {'checked_cells':checked,'matching_cells':checked-sum('column' in d for d in differences),'numeric_match':not differences,'differences':differences}


def compare(package,output_root,submission=False):
    expected=json.loads((package/'manifest/submission_tables.json').read_text())
    tables=[]
    for table in expected['tables']:
        r={k:table[k] for k in ['table','pdf_page','result']}
        if table['table']=='1':
            r.update(status=('static protocol table; original wording restored' if submission else 'static protocol table supplied; wording has minor edits'),numeric_match=None)
        else:
            file=output_root/table['result'];r.update(compare_table(table['rows'],tex_rows(file.read_text()),None if submission else table.get('column_indices')))
            r['status']='matches PDF numeric entries' if r['numeric_match'] else 'differs from PDF; see differences'
        tables.append(r)
    return {'compared_at_unix':int(time.time()),'mode':'original_submission' if submission else 'current_analysis','submission_pdf_sha256':expected['submission_pdf_sha256'],'tables':tables,'numeric_tables':sum('checked_cells' in t for t in tables),'exact_numeric_matches':sum(t.get('numeric_match') is True for t in tables)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package-root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--reproduced',action='store_true',help='Compare freshly generated outputs instead of released results.')
    parser.add_argument('--output',type=Path)
    parser.add_argument('--submission',action='store_true',help='Compare archival outputs under reproduced/submission.')
    args=parser.parse_args();root=args.package_root.resolve()
    result=compare(root,root/('reproduced/submission' if args.submission else 'reproduced' if args.reproduced else 'results'),submission=args.submission)
    if args.output:args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n')
    for table in result['tables']:
        print('Table '+table['table']+': '+table['status']+(f" ({table['matching_cells']}/{table['checked_cells']} cells)" if 'checked_cells' in table else ''))
    print(f"Exact numeric matches: {result['exact_numeric_matches']}/{result['numeric_tables']}. Table 1 is static.")


if __name__=='__main__':main()
