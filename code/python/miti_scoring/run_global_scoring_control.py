import pandas as pd
from tqdm import tqdm
import json
import os
import asyncio
from pathlib import Path
from openai import AsyncOpenAI
from tqdm.asyncio import tqdm_asyncio
from dotenv import load_dotenv

from miti_global_scores import MAIN_PROMPT, MITI_GUIDE

PACKAGE_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PACKAGE_ROOT / ".env")
api_key = os.getenv("OPENAI_API_KEY")

################################################
##### Interview transcripts   ##################
################################################

data = pd.read_csv(PACKAGE_ROOT / "data/private/chats_raw.csv", low_memory=False)
data = data.sort_values(by=["session_id", "order"], ascending=True)

def construct_transcript(session):
    text = ""
    for _, row in session.iterrows():
        k = row["order"]
        if k % 2 == 1:
            text += f"Clinician: {row['content']}\n"
        else:
            text += f"Client: {row['content']}\n"
    return text

session = data.groupby("session_id", as_index=False).apply(lambda x: construct_transcript(x)).rename(columns={None: "transcript"})

# Control (time-use) sessions only -- the three MI arms are already scored
# in output/w2_miti_global_scores_20251222_v003.csv
prefix = "Clinician: Hi! In this interview I want to learn more about how you spend your time."
control_sessions = session[session["transcript"].str.startswith(prefix, na=False)].reset_index(drop=True)
print(len(control_sessions))

################################################
##### MITI Evaluation Criteria  ################
################################################

id_name = "session_id"
params = {
    "model": "gpt-5-nano-2025-08-07",
    "text": {"verbosity": "medium"},
    "reasoning": {"effort": "low"},
    "store": False,
    "max_output_tokens": 5000,
}

input_data = []
for _, row in tqdm(control_sessions.iterrows(), total=control_sessions.shape[0]):
    for component, instructions in MITI_GUIDE.items():
        identifier = row[id_name]
        prompt = MAIN_PROMPT.format(
            transcript=row["transcript"],
            component_name=component,
            coding_instructions=instructions)
        input_data.append([identifier, component, prompt])

input_data = pd.DataFrame(input_data)
input_data.columns = [id_name, "miti_dimension", "prompt"]

################################################
#####       API Queries         ################
################################################

client = AsyncOpenAI(api_key=api_key)

async def classify_row(row, sem, params):
    async with sem:
        identifier = row[id_name]
        component = row["miti_dimension"]
        prompt = row["prompt"]
        try:
            reply = await client.responses.create(input=prompt, **params)
            response = reply.model_dump()
            response_dict = json.loads(response["output"][1]["content"][0]["text"])
            return [identifier, component, response, response_dict["score"], response_dict["justification"], prompt, "0"]
        except Exception as e:
            return [identifier, component, "", -999, -999, prompt, str(e)]

async def main(data, params, n_workers):
    sem = asyncio.Semaphore(n_workers)
    tasks = [classify_row(row, sem, params) for _, row in data.iterrows()]
    results = []
    errors = []

    for step in tqdm_asyncio.as_completed(tasks, total=len(tasks)):
        result = await step
        if isinstance(result, list):
            results.append(result)
        else:
            errors.append(result)

    return results, errors


if __name__ == "__main__":
    results, errors = asyncio.run(main(input_data, params, n_workers=8))

    df = pd.DataFrame(results)
    df.columns = ["session_id", "miti_dimension", "gpt_response", "score", "justification", "prompt", "error"]

    date = pd.Timestamp.now().strftime("%Y%m%d")
    out_path = f"output/w2_miti_global_scores_control_{date}.csv"
    df.to_csv(out_path, index=False)
    print(f"Wrote {len(df)} rows to {out_path}")
    print(df.groupby("miti_dimension")["score"].value_counts().sort_index())
