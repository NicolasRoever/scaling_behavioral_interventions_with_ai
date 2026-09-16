raise RuntimeError("Restricted-input source only. Raw interview data are not distributed. API execution is disabled in this $0-API replication package; use code/python/run_public.py for saved-result reproduction.")
# Topic analysis with BERTopic
import os, sys
import pandas as pd
import numpy as np
from helper import *

# Setup directory paths magic
PROJ_DIR = "/Users/fch/Library/CloudStorage/Dropbox/Projects/MI"

# BERT-related libraries
from umap import UMAP
from hdbscan import HDBSCAN
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer

from bertopic import BERTopic
from bertopic.representation import KeyBERTInspired
from bertopic.vectorizers import ClassTfidfTransformer
from bertopic.representation import MaximalMarginalRelevance
from scipy.cluster import hierarchy as sch
from tqdm import tqdm
import json
from matplotlib import pyplot as plt
# for OpenAI topic classification
from openai import OpenAI
api_key = os.getenv("OPENAI_API_KEY")



##########################################
#  Step 0: Load data                     #
##########################################


scripts = pd.read_csv(PROJ_DIR + "/data/raw/main_socialmedia/chats_raw.csv", usecols=["session_id", "type", "content", "question_name", "order"])
scripts = scripts.dropna(subset="content", how="any")
scripts["user_id_raw"] = scripts["session_id"].str[11:].astype(int)

# Merge treatment
survey = pd.read_stata(PROJ_DIR + "/data/processed/main_social_media/clean_data.dta", convert_categoricals=False)
data = scripts.merge(survey[["user_id_raw", "T"]], on=["user_id_raw"], how="left")
data = data.dropna(subset="T")
del data["session_id"]
data["T"] = data["T"].astype(int)
treatments = {0: "Control", 1: "Change Talk", 2: "Ambivalence", 3: "Direct persuasion"}
data["treatment"] = data["T"].map(treatments)

# Focus on (i) answers (ii) with at least 10 characters (>95% of the data) and (iii) non-control group interviews
docs = data.loc[(data["type"] == "answer") & (data["content"].str.len() >=10) & (data["treatment"] != "Control"), "content"].tolist()
doc_idx = data.loc[(data["type"] == "answer") & (data["content"].str.len() >=10) & (data["treatment"] != "Control")].index.tolist()


##########################################
#  Step 1: Pre-compute embeddings        #
##########################################

# Compute embeddings (takes about 10 minutes)
sentence_model = SentenceTransformer("all-mpnet-base-v2")
embedding = sentence_model.encode(docs, show_progress_bar=True)



##########################################
#  Step 2-6: Def. topic model pipeline   #
##########################################

# Felix: Parameters related to the topic model are set here

# Step 2 - Reduce dimensionality
umap_model = UMAP(
    n_neighbors=10, n_components=5,
    min_dist=0.0, metric='cosine', random_state=142)

# Step 3 - Cluster reduced embeddings
hdbscan_model = HDBSCAN(
    min_cluster_size=30, min_samples=10,
    metric='euclidean', cluster_selection_method='eom',
    prediction_data=True)

# Step 4 - Tokenize topics
vectorizer_model = CountVectorizer(
    stop_words="english", ngram_range=(1, 2), min_df=15)

# Step 5 - Create topic representation
ctfidf_model = ClassTfidfTransformer(
    bm25_weighting=False, reduce_frequent_words=True)

# Step 6 - (Optional) Fine-tune topic representations with a `bertopic.representation` model
representation_model = KeyBERTInspired()
representation_model = MaximalMarginalRelevance(diversity=0.2)


# All steps together
topic_model = BERTopic(
    min_topic_size=30,
    language="english",
    nr_topics=30,
    embedding_model=sentence_model,           # Step 1 - Extract embeddings
    umap_model=umap_model,                    # Step 2 - Reduce dimensionality
    hdbscan_model=hdbscan_model,              # Step 3 - Cluster reduced embeddings
    vectorizer_model=vectorizer_model,        # Step 4 - Tokenize topics
    ctfidf_model=ctfidf_model,                # Step 5 - Extract topic words
    representation_model=representation_model # Step 6 - Fine-tune topic rep.
)


##########################################
#  Estimate topic model                  #
##########################################

# Use pre-computed embeddings
topics, probs = topic_model.fit_transform(docs, embedding)

# Inspect topic distribution
tmp = topic_model.get_topic_info()
junk_topic_share = np.round(tmp.loc[tmp["Topic"] == -1, "Count"][0] / tmp["Count"].sum(), 3)
print(tmp.shape[0])
print(junk_topic_share)


# Get topic representation string 
def merge_words(x):
    s = x[0][0]
    for k in x[1:]:
        s += " - " + k[0]
    return s
topic_rep_str = {key: merge_words(value) for key, value in topic_model.topic_representations_.items()}

# Create dataframe with results
df = pd.DataFrame([doc_idx, docs, topics, probs]).T
df.columns = ["doc_idx", "content", "topic_id", "p_topic"]
df["topic_keywords"] = df["topic_id"].map(topic_rep_str)
df = df.merge(data.reset_index(), how="left", left_on=["doc_idx", "content"], right_on=["index", "content"])
del df["index"], df["doc_idx"]
df["topic_id"] = df["topic_id"].astype(int)
df["p_topic"] = df["p_topic"].astype(float)
df


# Get top N documents by topic, based on the probability of topic assignment. use the df for this with the topn function
top_n = 10
topn = df.groupby("topic_id").apply(
    lambda x: x.nlargest(top_n, "p_topic")["content"]).reset_index()
del topn["level_1"]
topn

# Get topic label and short summary from OpenAI for each topic
client = OpenAI(api_key=api_key)

prompt = """
# CONTEXT:
I conducted interviews about social media use and attempts to change one's social media behavior. I used BERTopic to cluster interview responses into topics. You are a sociologist developing a coding manual for thematic analysis. Your task is to assign a concise topic label and write a short analytical memo that clarifies the unifying theme of the topic.

# INPUT DATA:
The topic is characterized by the following keywords by BERTopic:
{keywords}

Below are responses with the highest probability of belonging to this topic:
{documents}

# TASK (PART 1 - TOPIC LABEL):
Propose a short label for this topic.

The label must satisfy the following requirements.
1. It must be at most 6 words.
2. It must capture a distinct underlying pattern.
3. It must be grounded in the documents, but not be a paraphrase of a single response.
4. It must be specific enough to distinguish this topic from others.

Avoid the following.
1. Generic or catch-all labels such as 'attitudes', 'experiences', or 'concerns'.
2. Overly abstract terms that could apply to many topics.

# TASK (PART 2 - ANALYTICAL NOTE):
Write a 3 to 5 sentence analytical note describing the unifying theme of this topic.

The note should do the following.
1. Explain what brings these responses together analytically.
2. Remain closely grounded in the data, without quoting or listing examples.
3. Use clear, neutral language suitable for a qualitative coding manual.
4. Help another researcher decide whether a new excerpt belongs to this topic.

Do not introduce theory or interpretation that is not supported by the responses. 

RESPONSE FORMAT:
Use the following exact JSON structure.

{{
    "memo": "<3 to 5 sentence analytical note>",
    "label": "<short topic label>",
}}

Respond only in this format. Do not add any additional text or context outside the JSON structure.

YOUR RESPONSE:
""".strip()

topic_labels = {}
topic_summaries = {}
for topic_id in tqdm(df["topic_id"].unique()):
    keywords = topic_rep_str[topic_id]
    documents = "- ''" + "''\n- ''".join(topn.loc[topn["topic_id"] == topic_id, "content"].tolist()) + "''"
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt.format(keywords=keywords, documents=documents)}],
        model="gpt-4.1-mini",
        max_tokens=1200,
        temperature=0,
    )
    response_dump = response.model_dump()

    output = json.loads(response_dump["choices"][0]["message"]["content"].strip())
    topic_labels[topic_id] = output["label"]
    topic_summaries[topic_id] = output["memo"]


df["topic_label"] = df["topic_id"].map(topic_labels)
df["topic_summary"] = df["topic_id"].map(topic_summaries)

# Export
df.to_csv(PROJ_DIR + "/data/processed/main_social_media/bertopic_labeled.csv", index=False)

# test = pd.read_csv(PROJ_DIR + "/data/processed/main_social_media/bertopic_labeled.csv")


counts = df.groupby(["topic_id", "user_id_raw"]).size().reset_index()
counts = counts.rename(columns={0: "topic_count"})
counts["topic_labels"] = counts["topic_id"].map(topic_labels)
counts["topic_summary"] = counts["topic_id"].map(topic_summaries)
counts = counts.merge(df[["user_id_raw", "treatment", "T"]].drop_duplicates(), on="user_id_raw", how="left")
counts["topic_dummy"] = (counts["topic_count"] > 0).astype(int)
counts

counts_by_treatment = counts.groupby(["T", "topic_id"])["topic_dummy"].sum().reset_index()
treatment_group_sizes = counts.groupby("T")["user_id_raw"].nunique().reset_index(name="T_size")

frequencies = counts_by_treatment.merge(treatment_group_sizes, on="T", how="left")
frequencies["frequency"] = frequencies["topic_dummy"] / frequencies["T_size"] * 100.0





# Ensure consistent ordering of topics (by topic_id; change if you prefer by overall frequency)
topic_ids = sorted(frequencies["topic_id"].unique())
topic_names = [topic_labels.get(tid, f"Topic {tid}") for tid in topic_ids]

# Ensure consistent ordering of treatment arms (uses your coding: 1,2,3)
T_order = sorted(frequencies["T"].unique())

# Pivot to a matrix: rows=topic_id, cols=T, values=frequency
pivot = (
    frequencies
    .pivot_table(index="topic_id", columns="T", values="frequency", aggfunc="first")
    .reindex(index=topic_ids, columns=T_order)
    .fillna(0.0)
)

colors = ["#b83232", "#777777", "#4c4c86",]  # Change Talk, Ambivalence, Direct Persuasion
treatment_name_map = {1: "Change Talk", 2: "Decisional Balance", 3: "Direct Persuasion"}
legend_labels = [treatment_name_map.get(t, f"T{t}") for t in T_order]

# ---- Plot: grouped horizontal bar chart ----
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 14

fig, ax = plt.subplots(figsize=(10, 0.3 * len(topic_ids) + 2))
y = np.arange(len(topic_ids))
n_groups = len(T_order)

# Bar geometry: grouped bars around each y position
group_height = 0.8
bar_height = group_height / max(n_groups, 1)
offsets = (np.arange(n_groups) - (n_groups - 1) / 2) * bar_height

for j, t in enumerate(T_order):
    ax.barh(
        y + offsets[j],
        pivot[t].values,
        height=bar_height * 0.95,
        color=colors[j] if j < len(colors) else None,
        label=legend_labels[j],
        edgecolor="none",
    )

# Y-axis labels: topic labels from your dictionary
ax.set_yticks(y)
ax.set_yticklabels(topic_names)

ax.set_xlabel("Share of conversations with topic present (%)", weight="bold", fontsize=14)
ax.grid(axis="x", linestyle="-", linewidth=0.5, alpha=0.3)

ax.set_xticks(np.arange(0, 101, 10))
ax.xaxis.grid(True, which="major", linestyle="-", linewidth=0.5, alpha=0.3)

ax.set_ylim(-0.5, len(topic_ids) - 0.5)
ax.invert_yaxis()  # top-to-bottom ordering; remove if you prefer the opposite
for spine in ax.spines.values():
    spine.set_visible(False)

ax.legend(loc="right", fontsize=14)
plt.tight_layout()
plt.show()
fig.savefig("/Users/fch/Library/CloudStorage/Dropbox/Apps/Overleaf/Which Conversations Motivate Change?/figures/fig_bertopic.pdf")













