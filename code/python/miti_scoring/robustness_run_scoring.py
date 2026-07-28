"""
Run one condition of the MITI global-score robustness checks.

Conditions:
  - stochastic reruns: same model/prompt as the original run, repeated (--condition rerun1 .. rerun5)
  - different model:   --condition model_swap --model gpt-5.6-luna
  - prompt ablation:   --condition ablation --ablate-conservative-line

Writes/append-resumes output/robustness_<condition>.csv (columns: session_id, miti_dimension,
score, justification, error, condition).
"""

import argparse
import asyncio
import json
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from openai import AsyncOpenAI
from tqdm.asyncio import tqdm_asyncio

from miti_global_scores import MAIN_PROMPT, MITI_GUIDE

PACKAGE_ROOT = Path(__file__).resolve().parents[3]
ENV_PATH = PACKAGE_ROOT / ".env"
CHATS_PATH = PACKAGE_ROOT / "data/private/chats_raw.csv"
CONTROL_PREFIX = "Clinician: Hi! In this interview I want to learn more about how you spend your time."
ABLATED_LINE = "- If in doubt, assign the lower score if you are uncertain between two scores.\n"


def load_treated_sessions():
    data = pd.read_csv(CHATS_PATH, low_memory=False)
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

    session = (
        data.groupby("session_id", as_index=False)
        .apply(lambda x: construct_transcript(x))
        .rename(columns={None: "transcript"})
    )
    treated = session[~session["transcript"].str.startswith(CONTROL_PREFIX, na=False)].reset_index(drop=True)
    return treated


def build_prompt_template(ablate_conservative_line):
    if not ablate_conservative_line:
        return MAIN_PROMPT
    assert ABLATED_LINE in MAIN_PROMPT, "Ablation line not found in MAIN_PROMPT -- did the prompt text change?"
    return MAIN_PROMPT.replace(ABLATED_LINE, "")


async def classify_row(client, row, sem, params):
    async with sem:
        identifier = row["session_id"]
        component = row["miti_dimension"]
        prompt = row["prompt"]
        try:
            reply = await client.responses.create(input=prompt, **params)
            response = reply.model_dump()
            message_item = next(item for item in response["output"] if item["type"] == "message")
            response_dict = json.loads(message_item["content"][0]["text"])
            return [identifier, component, response_dict["score"], response_dict["justification"], "0"]
        except Exception as e:
            return [identifier, component, -999, str(e), str(e)]


async def run(input_data, params, n_workers, api_key):
    client = AsyncOpenAI(api_key=api_key)
    sem = asyncio.Semaphore(n_workers)
    tasks = [classify_row(client, row, sem, params) for _, row in input_data.iterrows()]
    results = []
    for step in tqdm_asyncio.as_completed(tasks, total=len(tasks)):
        results.append(await step)
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--condition", required=True)
    parser.add_argument("--model", default="gpt-5-nano-2025-08-07")
    parser.add_argument("--ablate-conservative-line", action="store_true")
    parser.add_argument("--n-workers", type=int, default=20)
    parser.add_argument("--max-output-tokens", type=int, default=5000)
    parser.add_argument("--limit-sessions", type=int, default=None, help="For smoke testing only")
    parser.add_argument("--out-dir", default="output")
    args = parser.parse_args()

    load_dotenv(ENV_PATH)
    api_key = os.getenv("OPENAI_API_KEY")

    out_path = os.path.join(args.out_dir, f"robustness_{args.condition}.csv")

    treated_sessions = load_treated_sessions()
    if args.limit_sessions:
        treated_sessions = treated_sessions.head(args.limit_sessions)
    prompt_template = build_prompt_template(args.ablate_conservative_line)

    input_data = []
    for _, row in treated_sessions.iterrows():
        for component, instructions in MITI_GUIDE.items():
            prompt = prompt_template.format(
                transcript=row["transcript"],
                component_name=component,
                coding_instructions=instructions,
            )
            input_data.append([row["session_id"], component, prompt])
    input_data = pd.DataFrame(input_data, columns=["session_id", "miti_dimension", "prompt"])

    if os.path.exists(out_path):
        done = pd.read_csv(out_path)
        done_ok = done[done["error"] == "0"]
        done_keys = set(zip(done_ok["session_id"], done_ok["miti_dimension"]))
        input_data = input_data[
            ~input_data.apply(lambda r: (r["session_id"], r["miti_dimension"]) in done_keys, axis=1)
        ]
        print(f"Resuming: {len(done_ok)} already scored ok, {len(input_data)} remaining")

    if len(input_data) == 0:
        print("Nothing to do.")
        return

    params = {
        "model": args.model,
        "text": {"verbosity": "medium"},
        "reasoning": {"effort": "low"},
        "store": False,
        "max_output_tokens": args.max_output_tokens,
    }

    results = asyncio.run(run(input_data, params, args.n_workers, api_key))
    new_df = pd.DataFrame(results, columns=["session_id", "miti_dimension", "score", "justification", "error"])
    new_df["condition"] = args.condition

    if os.path.exists(out_path):
        old = pd.read_csv(out_path)
        old = old[~old.apply(lambda r: (r["session_id"], r["miti_dimension"]) in
                              set(zip(new_df["session_id"], new_df["miti_dimension"])), axis=1)]
        new_df = pd.concat([old, new_df], ignore_index=True)
    new_df.to_csv(out_path, index=False)
    n_errors = (new_df["error"] != "0").sum()
    print(f"Wrote {len(new_df)} rows to {out_path} ({n_errors} with errors)")


if __name__ == "__main__":
    main()
