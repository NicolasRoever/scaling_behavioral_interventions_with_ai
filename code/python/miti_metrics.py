from __future__ import annotations
import numpy as np
import pandas as pd

def icc_2_1(x, y):
    """ICC(2,1): two-way random, absolute agreement, single rater (Shrout & Fleiss 1979)."""
    data = np.column_stack([x, y]).astype(float)
    n, k = data.shape
    mean_subjects = data.mean(axis=1)
    mean_raters = data.mean(axis=0)
    grand_mean = data.mean()

    ss_total = ((data - grand_mean) ** 2).sum()
    ss_rows = k * ((mean_subjects - grand_mean) ** 2).sum()
    ss_cols = n * ((mean_raters - grand_mean) ** 2).sum()
    ss_error = ss_total - ss_rows - ss_cols

    ms_rows = ss_rows / (n - 1)
    ms_cols = ss_cols / (k - 1)
    ms_error = ss_error / ((n - 1) * (k - 1))

    denom = ms_rows + (k - 1) * ms_error + k * (ms_cols - ms_error) / n
    if denom == 0:
        return np.nan
    return (ms_rows - ms_error) / denom

def score_metrics(original, comparison, count_outcome=False):
    original = np.asarray(original, dtype=float)
    comparison = np.asarray(comparison, dtype=float)
    n = len(original)
    diff = comparison - original

    row = {
        "N": n,
        "Original mean": round(original.mean(), 2),
        "Comparison mean": round(comparison.mean(), 2),
        "Mean difference": round(diff.mean(), 2),
        "MAE": round(np.abs(diff).mean(), 2),
        "Correlation": round(np.corrcoef(original, comparison)[0, 1], 2),
        "Absolute-agreement ICC": round(icc_2_1(original, comparison), 2),
        "Exact agreement": round((original == comparison).mean(), 2),
        "Agreement within ±1": round((np.abs(diff) <= 1).mean(), 2),
    }
    if count_outcome:
        row["Direction changed"] = "—"
        row["Threshold crossing"] = "—"
    else:
        dir_orig = np.sign(original - 3)
        dir_cmp = np.sign(comparison - 3)
        row["Direction changed"] = round((dir_orig != dir_cmp).mean(), 2)
        row["Threshold crossing"] = round(((original >= 4) != (comparison >= 4)).mean(), 2)
    return row
