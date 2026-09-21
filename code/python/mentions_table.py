from __future__ import annotations
import pandas as pd

def overleaf_table(percentages):
    headers = [r"\shortstack{" + label.replace(" ", r"\\") + "}" for label in percentages.columns]
    lines = [
        r"\begin{tabularx}{\textwidth}{@{}>{\raggedright\arraybackslash}X" + "r" * len(headers) + "@{}}",
        r"\toprule",
        "Chat measure & " + " & ".join(headers) + r" \\",
        r"\midrule",
    ]
    for measure, values in percentages.iterrows():
        if measure.startswith("Participant mentions before"):
            measure = r"\quad Before any interviewer mention, or without one"
        elif measure.startswith("Participant mentions after"):
            measure = r"\quad After an interviewer mention"
        cells = [f"{value:.1f}" + r"\%" if pd.notna(value) else "--" for value in values]
        lines.append(measure + " & " + " & ".join(cells) + r" \\")
        if measure.startswith("Interviewer mentions"):
            lines.append(r"\addlinespace[0.7em]")
    return "\n".join([*lines, r"\bottomrule", r"\end{tabularx}", ""])
