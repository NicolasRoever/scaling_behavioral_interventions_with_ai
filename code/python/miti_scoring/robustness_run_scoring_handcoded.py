"""
Run one condition of the MITI global-score robustness checks on the handcoded
validation set (14 sessions with human CCT/SST/PAR/EMP scores, matching the
paper's behavioral-counts validation N).

Conditions:
  - repeated runs:      the configured model/prompt, repeated (--condition rerun1 .. rerun5);
                        the default model is gpt-5-nano-2025-08-07
  - different model:   --condition model_swap --model gpt-5.6-luna
  - prompt ablation:   --condition ablation --ablate-conservative-line

Writes/append-resumes output/robustness_handcoded_<condition>.csv (columns: source_pdf,
miti_dimension, score, justification, error, condition).
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
BEHAVIORAL_SCRIPTS_PATH = "output/validation_bheavioral_scores_extracted.csv"
FOURTEEN_SESSION_PATH = "output/behavioral_counts_validation_2025-11-25.csv"
ABLATED_LINE = "- If in doubt, assign the lower score if you are uncertain between two scores.\n"


def load_handcoded_sessions():
    """Build one full transcript per source_pdf, restricted to the 14-session subset."""
    scripts = pd.read_csv(BEHAVIORAL_SCRIPTS_PATH)
    label_map = {"P": "Client:", "C": "Clinician:"}
    prefixed_content = scripts.apply(
        lambda row: f"{label_map.get(row['P_or_C'], '')} {row['Content']}", axis=1
    )
    full_transcript = prefixed_content.groupby(scripts["source_pdf"]).apply(lambda x: "\n".join(x))
    session = pd.DataFrame(
        {"source_pdf": full_transcript.index, "transcript": full_transcript.values}
    )

    fourteen = pd.read_csv(FOURTEEN_SESSION_PATH, low_memory=False)
    fourteen_ids = set(fourteen["source_pdf"].unique())
    session = session[session["source_pdf"].isin(fourteen_ids)].reset_index(drop=True)
    assert len(session) == 14, f"Expected 14 sessions, got {len(session)}"
    return session


def build_prompt_template(ablate_conservative_line):
    if not ablate_conservative_line:
        return MAIN_PROMPT
    assert ABLATED_LINE in MAIN_PROMPT, "Ablation line not found in MAIN_PROMPT -- did the prompt text change?"
    return MAIN_PROMPT.replace(ABLATED_LINE, "")


async def classify_row(client, row, sem, params):
    async with sem:
        identifier = row["source_pdf"]
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
    parser.add_argument("--out-dir", default="output")
    args = parser.parse_args()

    load_dotenv(ENV_PATH)
    api_key = os.getenv("OPENAI_API_KEY")

    out_path = os.path.join(args.out_dir, f"robustness_handcoded_{args.condition}.csv")

    sessions = load_handcoded_sessions()
    prompt_template = build_prompt_template(args.ablate_conservative_line)

    input_data = []
    for _, row in sessions.iterrows():
        for component, instructions in MITI_GUIDE.items():
            prompt = prompt_template.format(
                transcript=row["transcript"],
                component_name=component,
                coding_instructions=instructions,
            )
            input_data.append([row["source_pdf"], component, prompt])
    input_data = pd.DataFrame(input_data, columns=["source_pdf", "miti_dimension", "prompt"])

    if os.path.exists(out_path):
        done = pd.read_csv(out_path)
        done_ok = done[done["error"] == "0"]
        done_keys = set(zip(done_ok["source_pdf"], done_ok["miti_dimension"]))
        input_data = input_data[
            ~input_data.apply(lambda r: (r["source_pdf"], r["miti_dimension"]) in done_keys, axis=1)
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
        "max_output_tokens": 5000,
    }

    results = asyncio.run(run(input_data, params, args.n_workers, api_key))
    new_df = pd.DataFrame(results, columns=["source_pdf", "miti_dimension", "score", "justification", "error"])
    new_df["condition"] = args.condition

    if os.path.exists(out_path):
        old = pd.read_csv(out_path)
        old = old[~old.apply(lambda r: (r["source_pdf"], r["miti_dimension"]) in
                              set(zip(new_df["source_pdf"], new_df["miti_dimension"])), axis=1)]
        new_df = pd.concat([old, new_df], ignore_index=True)
    new_df.to_csv(out_path, index=False)
    n_errors = (new_df["error"] != "0").sum()
    print(f"Wrote {len(new_df)} rows to {out_path} ({n_errors} with errors)")


if __name__ == "__main__":
    main()
