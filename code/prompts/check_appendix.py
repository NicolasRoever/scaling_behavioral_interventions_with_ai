"""Check the released interview configuration against a local revision.tex.

Reads only the Interviewer prompts section. It never executes the configuration,
reads interview examples, calls a model, or modifies the manuscript.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import time


def arm_keys():
    return ['T1_MI_CHANGE', 'T2_MI_AMBIVALENCE', 'T4_CLEAR_PERSUASION', 'TIME_USE']


def evaluate(node, values):
    """Evaluate literal configuration data without executing Python code."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        return values[node.id]
    if isinstance(node, ast.Dict):
        return {evaluate(k, values): evaluate(v, values) for k, v in zip(node.keys, node.values)}
    if isinstance(node, (ast.List, ast.Tuple)):
        result = [evaluate(v, values) for v in node.elts]
        return tuple(result) if isinstance(node, ast.Tuple) else result
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -evaluate(node.operand, values)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return evaluate(node.left, values) + evaluate(node.right, values)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'strip' and not node.args and not node.keywords:
        value = evaluate(node.func.value, values)
        if isinstance(value, str):
            return value.strip()
    raise ValueError('Nonliteral configuration expression: ' + type(node).__name__)


def load_configuration(path):
    values = {}
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.Assign):
            value = evaluate(node.value, values)
            for target in node.targets:
                if not isinstance(target, ast.Name):
                    raise ValueError('Expected a named configuration assignment')
                values[target.id] = value
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            continue  # module documentation
        elif isinstance(node, ast.Import) and all(n.name == 'os' for n in node.names):
            continue  # accepted for older configurations; never imported/executed
        else:
            raise ValueError('Unexpected executable configuration statement')
    return values['INTERVIEW_PARAMETERS']


def brace_group(text, start):
    if text[start] != '{':
        raise ValueError('Expected TeX brace group')
    depth = 1
    for index in range(start + 1, len(text)):
        if text[index] == '{' and text[index - 1] != '\\':
            depth += 1
        elif text[index] == '}' and text[index - 1] != '\\':
            depth -= 1
            if depth == 0:
                return text[start + 1:index], index + 1
    raise ValueError('Unbalanced TeX braces')


def prompt_text(text, environment):
    if environment == 'alltt':
        while r'\Copy{' in text:
            start = text.index(r'\Copy{')
            _, next_index = brace_group(text, start + len(r'\Copy'))
            body, end = brace_group(text, next_index)
            text = text[:start] + body + text[end:]
        text = text.replace(r'\linebreak', ' ')
        if '\\' in text:
            raise ValueError('Unrecognized alltt command; review the prompt extraction')
    # Only wrapping/spacing is normalized. Literal quote/dash notation and the
    # ---END--- routing sentinel are retained exactly as in the appendix blocks.
    return ' '.join(text.split())


def read_appendix(path):
    text = path.read_text()
    start = text.index(r'\section{Interviewer prompts}')
    section = text[start:]
    next_section = section.find(r'\section{', len(r'\section{Interviewer prompts}'))
    if next_section < 0:
        raise ValueError('Expected a following section to bound the prompt appendix')
    section = section[:next_section]
    sections = re.findall(r'\\subsection\*\{(D\.[1-4][^}]+)\}(.*?)(?=\\subsection\*|\Z)', section, re.S)
    if len(sections) != 4:
        raise ValueError('Expected exactly four appendix arms')
    extracted = {}
    for number, ((heading, body), arm) in enumerate(zip(sections, arm_keys()), 1):
        if not heading.startswith(f'D.{number}\\quad '):
            raise ValueError('Unexpected appendix arm ordering')
        blocks = re.findall(r'\\textit\{([^}]+)\}.*?\\begin\{(verbatim|alltt)\}\n(.*?)\\end\{\2\}', body, re.S)
        parsed = [(title, prompt_text(value, env)) for title, env, value in blocks]
        if not parsed[0][0].startswith('Global system prompt') or not parsed[1][0].startswith('Opening message'):
            raise ValueError('Missing global/opening prompt: ' + arm)
        turns = [(title, value) for title, value in parsed[2:] if title.startswith('Turn ')]
        for i, (title, _) in enumerate(turns, 1):
            if not title.startswith(f'Turn {i}---'):
                raise ValueError('Missing or reordered appendix turn: ' + title)
        extra = {title: value for title, value in parsed[2:] if not title.startswith('Turn ')}
        if set(extra) - {'Termination message.', 'End-of-interview message.'}:
            raise ValueError('Unmapped prompt block: ' + arm)
        extracted[arm] = dict(section=f'D.{number}', global_prompt=parsed[0][1],
                              opener=parsed[1][1], turns=turns, extra=extra)
    return extracted


def check(configuration, appendix):
    if list(configuration) != arm_keys():
        raise ValueError('Configuration must contain only the four appendix arms in appendix order')
    records = []
    for arm, spec in appendix.items():
        conf = configuration[arm]
        checks = [('global_mi_system_prompt', spec['global_prompt']), ('first_question', spec['opener'])]
        if len(conf['interview_plan']) != len(spec['turns']):
            raise ValueError('Turn-count mismatch: ' + arm)
        for field, expected in checks:
            actual = ' '.join(conf[field].split())
            if actual != expected:
                raise ValueError('Prompt mismatch: ' + arm + '/' + field)
            records.append(dict(arm=arm, section=spec['section'], field=field, sha256=hashlib.sha256(actual.encode()).hexdigest()))
        for i, (question, (title, expected)) in enumerate(zip(conf['interview_plan'], spec['turns']), 1):
            if ' '.join(question['system'].split()) != expected:
                raise ValueError('Prompt mismatch: ' + arm + '/' + title)
            records.append(dict(arm=arm, section=spec['section'], turn=i, question_name=question['question_name'], title=title, sha256=hashlib.sha256(expected.encode()).hexdigest()))
        names = [q['question_name'] for q in conf['interview_plan']]
        if len(set(names)) != len(names) or conf['first_ai_question_name'] != names[0]:
            raise ValueError('Invalid first question or duplicate turn key: ' + arm)
        for i, question in enumerate(conf['interview_plan']):
            if question['next_question'] != (names[i+1] if i+1 < len(names) else 'last_question'):
                raise ValueError('Broken question routing: ' + arm)
        for title, expected in spec['extra'].items():
            field = {'Termination message.':'termination_message','End-of-interview message.':'end_of_interview_message'}[title]
            if ' '.join(conf[field].split()) != expected or not conf[field].endswith('---END---'):
                raise ValueError('Closing-message mismatch: ' + arm)
            records.append(dict(arm=arm, section=spec['section'], field=field, sha256=hashlib.sha256(expected.encode()).hexdigest()))
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manuscript', required=True, type=Path)
    parser.add_argument('--parameters', type=Path, default=Path(__file__).with_name('parameters.py'))
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    records = check(load_configuration(args.parameters), read_appendix(args.manuscript))
    report = dict(validated_at_unix=int(time.time()), manuscript_sha256=hashlib.sha256(args.manuscript.read_bytes()).hexdigest(),
                  parameters_sha256=hashlib.sha256(args.parameters.read_bytes()).hexdigest(),
                  text_normalization='Remove alltt Copy/linebreak wrappers and collapse whitespace only; preserve literal punctuation and ---END---.',
                  blocks_checked=len(records), arms=4, checks_passed=True, blocks=records)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2)+'\n')
    print(f'PASS: {len(records)} appendix blocks, four arms, and all question-routing links.')


if __name__ == '__main__':
    main()
