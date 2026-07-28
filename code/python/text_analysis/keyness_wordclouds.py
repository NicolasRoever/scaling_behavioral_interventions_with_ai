"""
Which words does each interviewer arm lean on more than the others? (word clouds)

For every arm we compare its interviewer turns against the pooled turns of the OTHER
THREE arms (a one-vs-rest contrast, all four arms including Control). "More than the
others" is measured with weighted log-odds: a
log-odds ratio smoothed by an informative prior and turned into a z-score, so a word
that is genuinely over-used by an arm scores high while rare, noisy words are pulled
back toward zero. We do this for single words and two-word phrases, and size each term
in the cloud by its z-score - bigger means the arm leans on it more.

Two filters keep the clouds readable: a curated stop-word list removes function words, and
any term used in more than half of all interviewer turns is
dropped as too common - so ubiquitous words such as "social"/"media" don't crowd every arm.

The one figure, outputs/wordclouds_by_arm.png, has one row per n-gram order (single words and
two-word phrases) and one column per arm; only over-represented terms (z > 0) are shown,
word size is the z-score, and word colour is just the arm's colour (a random shade, not a signal).
The underlying scores are also written to outputs/keyness_by_arm.csv.

Sample: interviewer turns from interviews whose survey was completed.

Run it with:  python keyness_wordclouds.py
"""

import re
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, to_rgb
import numpy as np
import pandas as pd
import pyreadstat
from wordcloud import WordCloud

PACKAGE_ROOT = Path(__file__).resolve().parents[3]
CHATS_CSV = PACKAGE_ROOT / "data/private/chats_raw.csv"
MAIN_SAV = PACKAGE_ROOT / "data/raw/main_socialmedia/main_raw.sav"
OUT = PACKAGE_ROOT / "results/figures"
OUT.mkdir(parents=True, exist_ok=True)

ARMS = ["T1_MI_CHANGE", "T2_MI_AMBIVALENCE", "T4_CLEAR_PERSUASION", "TIME_USE"]
ARM_LABELS = {"T1_MI_CHANGE": "Change Talk", "T2_MI_AMBIVALENCE": "Decisional Balance",
              "T4_CLEAR_PERSUASION": "Direct Persuasion", "TIME_USE": "Control (Time Use)"}
ARM_COLORS = {"T1_MI_CHANGE": "#b83232", "T2_MI_AMBIVALENCE": "#777777",
              "T4_CLEAR_PERSUASION": "#4c4c86", "TIME_USE": "#9b9b9b"}

BACKGROUND = "#faf9f6"          

# ALPHA0 is the total weight of the prior in the weighted log-odds. Before taking each word's
# odds we add "pseudo-counts" spread across the vocabulary in proportion to how common each word
# is overall, scaled so they sum to ALPHA0. Those pseudo-counts shrink rare/noisy words toward
# zero, so a word seen 3x in one arm and 0x in another can't fake a huge distinctiveness score.
# Bigger ALPHA0 -> more shrinkage (more conservative); smaller -> rare words spike more easily.
ALPHA0 = 1000.0

# On top of the curated stop-word list, also drop any term that appears in MORE than this fraction
# of interviewer turns - the way ConvoKit's CountVectorizer(max_df=0.5) does. This removes ubiquitous
# words like "social"/"media" that every arm uses constantly and that would otherwise crowd every
# column (stop-words handle function words; max_df handles over-used content words).
MAX_DF = 0.5

# Word clouds by n-gram order. Phrases are rarer than single words, so the count floor and the
# number of terms shown both drop as the phrases get longer.
ORDERS = {
    1: {"label": "Single Words",           "min_count": 15, "max_words": 45, "horizontal": 0.90},
    2: {"label": "Two-Word Phrases", "min_count": 8,  "max_words": 30, "horizontal": 1.00},
}

# A small, transparent stop-word list. Pronouns like "you"/"we" are kept on purpose: who the
# interviewer centres ("you" vs "we") is substantively interesting here.
STOPWORDS = set("""
a an the and or but if then else of to in on at by for with about as into like
through after over between out against during without before under around among
is are was were be been being am do does did doing have has had having will would
shall should can could may might must this that these those there here it its it's
so than too very just also not no nor only own same such off up down again further
i me my mine you your yours he him his she her hers they them their theirs we us our
ours what which who whom whose when where why how all any both each few more most
other some any this that
""".split())

# A wider set of low-content words dropped on top of the basic list above: light/generic verbs,
# filler adverbs, vague nouns, and the pronoun-contractions that survive tokenisation (the tokenizer
# keeps apostrophes, so "you're" is one token and isn't caught by "you" above). Kept deliberately
# moderate - substantive MI vocabulary stays (reduce, social, media, time, sleep, focus, plan, goals,
# values, scale, number, lower, higher, want, confidence, spend, routine, ...). Edit freely.
STOPWORDS |= set("""
get gets got getting go goes going make makes making made give gives given
help helps helped use used using see sees seen look looks looking feel feels feeling
seem seems mean means meaning think thinks thought find finds tend tends come comes
take takes put puts keep keeps say says said tell tells told let lets sound sounds
really already just also even still well right quite pretty actually basically simply
maybe perhaps thing things way ways part parts kind sort bit lot point sense
one ones something someone anything everything good clear able useful
you're you've you'd you'll i'm i've we're we've they're it's that's there's
here's what's let's don't doesn't didn't isn't aren't wasn't won't wouldn't couldn't shouldn't can't
""".split())

# Leftover halves of contractions once the apostrophe is stripped.
CONTRACTION_FRAGMENTS = {"ve", "ll", "re", "don", "didn", "doesn", "isn",
                         "wasn", "aren", "won", "wouldn", "couldn", "shouldn"}

TOKEN_RE = re.compile(r"[a-z]+(?:'[a-z]+)?")


def tokenize(text, drop_stopwords=True):
    """Lower-case the text and return its word tokens (apostrophes kept, e.g. "don't")."""
    if not isinstance(text, str):
        return []
    text = text.replace("’", "'").replace("‘", "'")      # curly -> straight quote
    tokens = []
    for tok in TOKEN_RE.findall(text.lower()):
        if len(tok) < 2:
            continue
        if drop_stopwords and (tok in STOPWORDS or tok in CONTRACTION_FRAGMENTS):
            continue
        tokens.append(tok)
    return tokens


def ngram_counts(texts, n):
    """
    Count n-grams across the texts. Single words drop stop-words.
    """
    counts = Counter()
    for text in texts:
        tokens = tokenize(text, drop_stopwords=(n == 1))
        if n == 1:
            counts.update(tokens)
            continue
        for i in range(len(tokens) - n + 1):
            gram = tokens[i:i + n]
            if all(g in STOPWORDS for g in gram):
                continue
            counts[" ".join(gram)] += 1
    return counts


def document_frequencies(texts, n):
    """For each n-gram, how many of the texts (interviewer turns) it appears in (once per turn)."""
    df = Counter()
    for text in texts:
        tokens = tokenize(text, drop_stopwords=(n == 1))
        if n == 1:
            df.update(set(tokens))
        else:
            df.update({" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)
                       if not all(g in STOPWORDS for g in tokens[i:i + n])})
    return df


def weighted_log_odds(counts_a, counts_b, min_count, drop=frozenset()):
    """
    Weighted log-odds of every term between corpus A and corpus B.

    The prior is the pooled corpus (A+B) rescaled to ALPHA0 (see the note up top), which shrinks
    rare, noisy terms toward zero. `drop` is a set of terms to exclude (the too-common words filtered
    by MAX_DF). Returns the term list, delta (log-odds ratio; positive = more typical of A), its
    z-score (delta / its standard error), and the raw frequency of each term in A.
    """
    combined = counts_a + counts_b
    vocab = sorted(term for term, c in combined.items() if c >= min_count and term not in drop)
    if not vocab:
        empty = np.array([])
        return {"vocab": empty, "delta": empty, "z": empty, "freq_a": empty}

    y_a = np.array([counts_a.get(t, 0) for t in vocab], dtype=float)      # term counts in A
    y_b = np.array([counts_b.get(t, 0) for t in vocab], dtype=float)      # term counts in B
    prior = np.array([combined[t] for t in vocab], dtype=float)          # pooled counts...
    prior = ALPHA0 * prior / prior.sum()                                 # ...rescaled to sum to ALPHA0

    n_a, n_b, a0 = y_a.sum(), y_b.sum(), prior.sum()
    # log-odds of the term within each corpus (smoothed by the prior), then their difference
    delta = (np.log(y_a + prior) - np.log(n_a + a0 - y_a - prior)
             - np.log(y_b + prior) + np.log(n_b + a0 - y_b - prior))
    # divide by the large-sample standard error of the log-odds-ratio -> a z-score
    z = delta / np.sqrt(1.0 / (y_a + prior) + 1.0 / (y_b + prior))
    return {"vocab": np.array(vocab), "delta": delta, "z": z, "freq_a": y_a}


def load_interviewer_turns():
    """Interviewer turns from completed-survey interviews, tagged with their arm."""
    chats = pd.read_csv(CHATS_CSV, dtype=str)

    survey, _ = pyreadstat.read_sav(
        MAIN_SAV, usecols=["user_id", "interview_id", "Progress", "r_status"])
    survey["user_id"] = survey["user_id"].astype(str)
    r_status = survey["r_status"].astype(str).str.strip().str.lower()
    completed = (pd.to_numeric(survey["Progress"], errors="coerce") == 100) | (r_status == "completed")
    arm_of = dict(zip(survey["user_id"], survey["interview_id"]))
    done = set(survey.loc[completed, "user_id"])

    user = chats["session_id"].str.extract(r"(\d+)$")[0]
    chats["arm"] = user.map(arm_of).replace({"DEFAULT": np.nan, "": np.nan})
    chats = chats[user.isin(done)]

    turns = chats[(chats["type"] == "question") & chats["content"].notna()].copy()
    turns["content"] = turns["content"].astype(str).str.strip()
    return turns[turns["content"].str.len() > 0]


def save_csv(df, path, **kw):
    """Save a CSV, falling back to a '_new' copy if the file is locked."""
    try:
        df.to_csv(path, **kw)
        return path
    except PermissionError:
        alt = path.with_name(path.stem + "_new" + path.suffix)
        df.to_csv(alt, **kw)
        return alt


def compute_keyness(turns, n, min_count, drop=frozenset()):
    """One-vs-rest weighted log-odds for every arm at n-gram order n (rest = the other three arms)."""
    per_arm = {arm: ngram_counts(turns.loc[turns["arm"] == arm, "content"], n) for arm in ARMS}
    rows = []
    for arm in ARMS:
        rest = Counter()
        for other in ARMS:
            if other != arm:
                rest.update(per_arm[other])
        res = weighted_log_odds(per_arm[arm], rest, min_count, drop)
        for term, delta, z, freq in zip(res["vocab"], res["delta"], res["z"], res["freq_a"]):
            rows.append({"arm": arm, "ngram": n, "term": term,
                         "delta": delta, "z": z, "freq_in_arm": freq})
    return pd.DataFrame(rows)


def arm_cmap(hex_color):
    """Arm-colour ramp, so more distinctive (higher-z) words render darker."""
    r, g, b = to_rgb(hex_color)
    pale = (0.55 + 0.45 * r, 0.55 + 0.45 * g, 0.55 + 0.45 * b)
    return LinearSegmentedColormap.from_list("arm", [pale, (r, g, b)])


def make_figure(keyness):
    """
    Draw outputs/wordclouds_by_arm.png: a grid of word clouds, one row per n-gram order (single
    words and two-word phrases) and one column per arm. Each word is sized by its
    weighted log-odds z-score (its distinctiveness for that arm versus the pooled other three); only
    over-represented terms (z > 0) appear.
    """
    plt.rcParams.update({"font.family": "Arial", "font.size": 10})
    fig, axes = plt.subplots(len(ORDERS), len(ARMS), figsize=(19, 8))

    for row, (n, settings) in enumerate(ORDERS.items()):
        for col, arm in enumerate(ARMS):
            ax = axes[row][col]
            sub = keyness[(keyness["arm"] == arm) & (keyness["ngram"] == n) & (keyness["z"] > 0)]
            weights = dict(zip(sub["term"], sub["z"]))          # size each word by its z-score

            cloud = WordCloud(width=1000, height=720, background_color=BACKGROUND,
                              colormap=arm_cmap(ARM_COLORS[arm]), max_words=settings["max_words"],
                              prefer_horizontal=settings["horizontal"], relative_scaling=0.5,
                              min_font_size=10, collocations=False, normalize_plurals=False,
                              random_state=0)
            cloud.generate_from_frequencies(weights)
            ax.imshow(cloud, interpolation="bilinear", aspect="auto")
            ax.axis("off")

            if row == 0:
                ax.set_title(ARM_LABELS[arm], fontsize=13, fontweight="bold",
                             color=ARM_COLORS[arm], pad=8)
            if col == 0:
                ax.text(-0.04, 0.5, settings["label"], transform=ax.transAxes, rotation=90,
                        va="center", ha="center", fontsize=12, fontweight="bold")

    # hspace opens a clear gap between the two n-gram rows (words / two-word phrases)
    fig.subplots_adjust(left=0.05, right=0.99, top=0.97, bottom=0.02, wspace=0.04, hspace=0.20)
    fig.savefig(OUT / "wordclouds_by_arm.pdf", bbox_inches="tight", facecolor=BACKGROUND)
    plt.close(fig)


def main():
    turns = load_interviewer_turns()
    turns = turns[turns["arm"].isin(ARMS)]
    n_turns = len(turns)

    frames = []
    for n, s in ORDERS.items():
        # too_common = terms used in more than MAX_DF of all turns
        too_common = {term for term, d in document_frequencies(turns["content"], n).items()
                      if d / n_turns > MAX_DF}
        frames.append(compute_keyness(turns, n, s["min_count"], drop=too_common))
    keyness = pd.concat(frames, ignore_index=True).sort_values(
        ["ngram", "arm", "z"], ascending=[True, True, False])
    save_csv(keyness, OUT / "keyness_by_arm.csv", index=False)

    make_figure(keyness)


if __name__ == "__main__":
    main()
