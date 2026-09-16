"""Versioned MITI global-scoring campaigns. See README_campaign.md for commands.

Inputs, prompts, settings and code are frozen before scoring. Each run has an
append-only attempt journal and an atomically replaced, one-row-per-key CSV.
No successful response is sampled again on resume. No automatic model fallback.
"""
raise RuntimeError("Restricted-input source only. Raw interview data are not distributed. API execution is disabled in this $0-API replication package; use code/python/run_public.py for saved-result reproduction.")

import argparse
import asyncio
import csv
import fcntl
import hashlib
import json
import os
import re
import shutil
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from dotenv import dotenv_values
from openai import AsyncOpenAI


def digest(value):
    return hashlib.sha256(value).hexdigest()


def json_bytes(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False).encode()


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(json_bytes(value))
    temporary.replace(path)


def read_json(path):
    return json.loads(path.read_text())


def build_sessions(chats_path, transcript_path, human_path, subset_path, prefix):
    chats = pd.read_csv(chats_path, low_memory=False).sort_values(
        ["session_id", "order"], kind="stable")
    if chats[["session_id", "order"]].isna().any().any():
        raise ValueError("Missing transcript ordering metadata")
    # Match historical transcript construction, including literal 'nan' for the
    # 35 empty turns in 19 sessions. Changing this would confound the model swap.
    if chats.duplicated(["session_id", "order"]).any():
        raise ValueError("Duplicate transcript turn keys")
    sessions = []
    for identifier, group in chats.groupby("session_id", sort=True):
        transcript = "".join(
            f"{'Clinician' if row.order % 2 else 'Client'}: {row.content}\n"
            for row in group.itertuples())
        sessions.append({"session_id": str(identifier), "transcript": transcript,
                         "dataset": "control" if transcript.startswith(prefix) else "treated"})
    scripts = pd.read_csv(transcript_path)
    human = pd.read_csv(human_path)
    subset = set(pd.read_csv(subset_path, low_memory=False).source_pdf)
    if len(subset) != 14 or human.source_pdf.nunique() != 20:
        raise ValueError("Human validation sample changed")
    # Preserve the extracted CSV row order used by the existing validation runner.
    for identifier, group in scripts.groupby("source_pdf", sort=True):
        if identifier not in set(human.source_pdf):
            continue
        if group.Content.isna().any():
            raise ValueError("Missing human-validation content")
        labels = {"P": "Client:", "C": "Clinician:"}
        transcript = "\n".join(
            f"{labels.get(row.P_or_C, '')} {row.Content}"
            for row in group.itertuples())
        sessions.append({"session_id": identifier, "source_pdf": identifier,
                         "dataset": "validation20", "transcript": transcript})
        if identifier in subset:
            sessions.append({"session_id": identifier, "source_pdf": identifier,
                             "dataset": "validation14", "transcript": transcript})
    return sessions


def campaign_matrix(benchmark_model, comparison_models):
    conditions = [("benchmark", 0, benchmark_model, "standard")]
    conditions += [("rerun", i, benchmark_model, "standard") for i in range(1, 6)]
    conditions += [("ablation", 0, benchmark_model, "ablation")]
    conditions += [("model_swap", 0, model, "standard") for model in comparison_models]
    runs = []
    for condition, replicate, model, prompt_variant in conditions:
        datasets = ["treated", "control", "validation20"] if condition == "benchmark" else ["treated", "validation14"]
        for dataset in datasets:
            runs.append(dict(dataset=dataset, condition=condition, replicate=replicate,
                             model=model, prompt_variant=prompt_variant))
    return runs


def initialize(root, output, chats, survey, benchmark_model, comparison_models):
    from miti_global_scores import MAIN_PROMPT, MITI_GUIDE
    from robustness_run_scoring import CONTROL_PREFIX, ABLATED_LINE
    files = {"chats": chats, "survey": survey,
             "transcripts": root / "output/validation_bheavioral_scores_extracted.csv",
             "human": root / "output/validation_global_scores_extracted.csv",
             "subset": root / "output/behavioral_counts_validation_2025-11-25.csv",
             "behavioral_results": root / "output/behavioral_scores_validation_results.csv"}
    sessions = build_sessions(files["chats"], files["transcripts"], files["human"],
                              files["subset"], CONTROL_PREFIX)
    counts = {dataset: sum(s["dataset"] == dataset for s in sessions)
              for dataset in ["treated", "control", "validation14", "validation20"]}
    if counts != dict(treated=2195, control=737, validation14=14, validation20=20):
        raise ValueError(f"Unexpected sample counts: {counts}")
    # Verify exact corpus membership against historical scores, not just counts.
    for dataset, name in [("treated", "w2_miti_global_scores_20251222_v003.csv"),
                          ("control", "w2_miti_global_scores_control_20260703.csv")]:
        expected = set(pd.read_csv(root / "output" / name, usecols=["session_id"]).session_id)
        if expected != {s["session_id"] for s in sessions if s["dataset"] == dataset}:
            raise ValueError(f"Historical {dataset} sample membership changed")
    if MAIN_PROMPT.count(ABLATED_LINE) != 1:
        raise ValueError("Expected exactly one conservative-scoring instruction")
    prompts = {"standard": MAIN_PROMPT,
               "ablation": MAIN_PROMPT.replace(ABLATED_LINE, ""), "guide": MITI_GUIDE}
    output.mkdir(parents=True, exist_ok=False)
    (output / "inputs").mkdir()
    (output / "code").mkdir()
    atomic_json(output / "inputs/sessions.json", sessions)
    atomic_json(output / "inputs/prompts.json", prompts)
    inputs = {name: {"source": str(path), "sha256": digest(path.read_bytes())}
              for name, path in files.items()}
    for name in ["human", "subset", "survey", "behavioral_results"]:
        path = files[name]
        destination = output / "inputs" / (name + path.suffix)
        shutil.copy2(path, destination)
        inputs[name]["snapshot"] = str(destination.relative_to(output))
    for name in ["sessions", "prompts"]:
        path = output / "inputs" / (name + ".json")
        inputs[name] = {"snapshot": str(path.relative_to(output)), "sha256": digest(path.read_bytes())}
    code_hashes = {}
    for path in sorted(root.glob("*.py")):
        shutil.copy2(path, output / "code" / path.name)
        code_hashes[path.name] = digest(path.read_bytes())
    now = int(time.time())
    stamp = datetime.fromtimestamp(now, timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    campaign_id = f"{stamp}_{uuid.uuid4().hex[:8]}"
    runs = campaign_matrix(benchmark_model, comparison_models)
    for run in runs:
        tag = run["condition"] + (f'-{run["replicate"]:02d}' if run["replicate"] else "")
        run_id = f'{campaign_id}__{run["dataset"]}__{run["model"]}__{tag}'
        run.update(run_id=run_id, file=f"{run_id}.csv", status="pending",
                   expected_rows=counts[run["dataset"]] * len(MITI_GUIDE))
    manifest = dict(schema_version=1, campaign_id=campaign_id, created_at_unix=now,
                    benchmark_model=benchmark_model, comparison_models=comparison_models,
                    transcript_note="Historical construction preserved: empty raw content becomes literal nan; extracted validation CSV order preserved.",
                    dimensions=list(MITI_GUIDE), sample_counts=counts, inputs=inputs,
                    code_hashes=code_hashes, provider="openai", base_url="https://api.openai.com/v1",
                    settings={"reasoning": {"effort": "low"}, "text": {"verbosity": "medium"},
                              "store": False, "max_output_tokens": 9000}, runs=runs)
    atomic_json(output / "manifest.json", manifest)
    print(f"Created {output / 'manifest.json'}; {sum(r['expected_rows'] for r in runs)} scoring requests", flush=True)
    return manifest


def verify_inputs(folder, manifest):
    for item in manifest["inputs"].values():
        if "snapshot" in item and digest((folder / item["snapshot"]).read_bytes()) != item["sha256"]:
            raise ValueError(f"Frozen input changed: {item['snapshot']}")
    runner = Path(__file__)
    if digest(runner.read_bytes()) != manifest["code_hashes"][runner.name]:
        raise ValueError("Runner differs from frozen campaign code; execute code/run_campaign.py")


def tasks_for_run(sessions, prompts, run):
    template = prompts[run["prompt_variant"]]
    return [dict(session_id=s["session_id"], source_pdf=s.get("source_pdf", ""),
                 miti_dimension=dim,
                 prompt=template.format(transcript=s["transcript"], component_name=dim,
                                        coding_instructions=instructions))
            for s in sessions if s["dataset"] == run["dataset"]
            for dim, instructions in prompts["guide"].items()]


def parse_score(text):
    # Accommodate a complete fenced JSON object, never salvage truncated JSON.
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    result = json.loads(cleaned)
    if not isinstance(result, dict) or type(result.get("score")) is not int or not 1 <= result["score"] <= 5:
        raise ValueError("score must be an integer from 1 to 5")
    if not isinstance(result.get("justification"), str) or not result["justification"].strip():
        raise ValueError("Missing score justification")
    return {"score": result["score"], "justification": result["justification"]}


def load_journal(path):
    if not path.exists():
        return []
    lines = path.read_bytes().splitlines(keepends=True)
    records = []
    valid_bytes = 0
    for index, line in enumerate(lines):
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            if index != len(lines) - 1 or line.endswith(b"\n"):
                raise
            # A process killed mid-write may leave only the final record incomplete.
            with path.open("r+b") as stream:
                stream.truncate(valid_bytes)
            break
        records.append(record)
        valid_bytes += len(line)
    return records


def latest_records(records):
    latest = {}
    for record in records:
        key = (record["session_id"], record["miti_dimension"])
        if key in latest and latest[key]["error"] == "0":
            raise ValueError("Journal contains another attempt after a successful score")
        latest[key] = record
    return latest


def save_scores(path, latest):
    if not latest:
        return
    temporary = path.with_suffix(".csv.tmp")
    pd.DataFrame([latest[k] for k in sorted(latest)]).to_csv(temporary, index=False)
    temporary.replace(path)


async def request_score(client, task, manifest, run, attempt):
    started = time.time()
    row = {key: value for key, value in task.items() if key != "prompt"}
    row.update(run_id=run["run_id"], campaign_id=manifest["campaign_id"],
               dataset=run["dataset"], model=run["model"], provider=manifest["provider"],
               condition=run["condition"], replicate=run["replicate"],
               prompt_variant=run["prompt_variant"], prompt_sha256=digest(task["prompt"].encode()),
               settings_sha256=digest(json_bytes(manifest["settings"])), attempt=attempt,
               started_at_unix=int(started), score=None, justification="", error="0",
               response_id="", response_model="", response_created_at_unix=None,
               input_tokens=0, cached_input_tokens=0, output_tokens=0, reasoning_tokens=0)
    fatal = False
    try:
        response = await client.responses.create(model=run["model"], input=task["prompt"], **manifest["settings"])
        row.update(response_id=response.id, response_model=response.model,
                   response_created_at_unix=response.created_at)
        if response.usage:
            usage = response.usage.model_dump()
            row.update(input_tokens=usage.get("input_tokens", 0), output_tokens=usage.get("output_tokens", 0),
                       cached_input_tokens=(usage.get("input_tokens_details") or {}).get("cached_tokens", 0),
                       reasoning_tokens=(usage.get("output_tokens_details") or {}).get("reasoning_tokens", 0))
        row["raw_output"] = response.output_text
        if response.status != "completed":
            raise ValueError(f"Response status {response.status}: {response.incomplete_details}")
        row.update(parse_score(response.output_text))
    except Exception as exc:
        # API exception strings can echo request content or credentials. Persist only type/code.
        code = getattr(exc, "status_code", None)
        row["error"] = f"{type(exc).__name__}:{code or ''}"
        fatal = code in (400, 401, 403, 404) or getattr(exc, "code", None) == "insufficient_quota"
    row.setdefault("raw_output", "")
    row.update(completed_at_unix=int(time.time()), elapsed_seconds=round(time.time() - started, 3))
    return row, fatal


async def execute_run(client, folder, manifest, run, sessions, prompts, workers, max_attempts):
    tasks = tasks_for_run(sessions, prompts, run)
    journal_path = folder / run["file"].replace(".csv", ".attempts.jsonl")
    records = load_journal(journal_path)
    latest = latest_records(records)
    expected = {(t["session_id"], t["miti_dimension"]) for t in tasks}
    if set(latest) - expected:
        raise ValueError("Journal contains keys outside frozen sample")
    for row in records:
        if row["run_id"] != run["run_id"] or row["settings_sha256"] != digest(json_bytes(manifest["settings"])):
            raise ValueError("Journal configuration mismatch")
    run["status"] = "running"
    run.setdefault("started_at_unix", int(time.time()))
    atomic_json(folder / "manifest.json", manifest)
    for retry_round in range(max_attempts):
        pending = [t for t in tasks if latest.get((t["session_id"], t["miti_dimension"]), {}).get("error") != "0"]
        if not pending:
            break
        queue = asyncio.Queue()
        for task in pending:
            queue.put_nowait(task)
        stop = asyncio.Event()
        done_count = 0
        async def worker():
            nonlocal done_count
            while not stop.is_set():
                try:
                    task = queue.get_nowait()
                except asyncio.QueueEmpty:
                    return
                key = (task["session_id"], task["miti_dimension"])
                row, fatal = await request_score(client, task, manifest, run, latest.get(key, {}).get("attempt", 0) + 1)
                with journal_path.open("a") as journal:
                    journal.write(json.dumps(row, ensure_ascii=False) + "\n")
                    journal.flush()
                    os.fsync(journal.fileno())
                latest[key] = row
                done_count += 1
                if done_count % 100 == 0:
                    save_scores(folder / run["file"], latest)
                    print(f'{run["dataset"]}/{run["model"]}/{run["condition"]}{run["replicate"]}: '
                          f'{sum(r["error"] == "0" for r in latest.values())}/{len(tasks)} valid', flush=True)
                if fatal:
                    stop.set()
        await asyncio.gather(*(worker() for _ in range(workers)))
        save_scores(folder / run["file"], latest)
        if stop.is_set():
            break
        if any(r["error"] != "0" for r in latest.values()) and retry_round + 1 < max_attempts:
            await asyncio.sleep(min(30, 2 ** (retry_round + 1)))
    valid = sum(r["error"] == "0" for r in latest.values())
    run.update(valid_rows=valid, status="complete" if valid == len(tasks) else "incomplete",
               updated_at_unix=int(time.time()))
    if run["status"] == "complete":
        run["output_sha256"] = digest((folder / run["file"]).read_bytes())
    atomic_json(folder / "manifest.json", manifest)
    print(f'{run["run_id"]}: {run["status"]} ({valid}/{len(tasks)})', flush=True)
    return run["status"] == "complete"


async def preflight(client, folder, manifest, sessions, prompts):
    results = []
    for model in [manifest["benchmark_model"], *manifest["comparison_models"]]:
        run = next(r for r in manifest["runs"] if r["model"] == model and r["dataset"] == "treated")
        # Four dimensions on two frozen sessions. Kept separate from production runs.
        tasks = tasks_for_run(sessions, prompts, run)[:8]
        rows = await asyncio.gather(*(request_score(client, t, manifest, {**run, "run_id": "smoke__" + run["run_id"]}, 1) for t in tasks))
        for row, fatal in rows:
            row["production"] = False
            results.append(row)
        print(f'Smoke {model}: {sum(row["error"] == "0" for row, _ in rows)}/{len(rows)} valid', flush=True)
    pd.DataFrame(results).to_csv(folder / "preflight.csv", index=False)
    passed = all(r["error"] == "0" for r in results)
    manifest["preflight"] = dict(passed=passed, completed_at_unix=int(time.time()),
                                  file="preflight.csv", sha256=digest((folder / "preflight.csv").read_bytes()))
    atomic_json(folder / "manifest.json", manifest)
    if not passed:
        raise RuntimeError("Preflight failed; inspect preflight.csv before launching production")


async def run_selected(folder, manifest, env_path, command, workers, selectors, max_attempts):
    verify_inputs(folder, manifest)
    sessions = read_json(folder / "inputs/sessions.json")
    prompts = read_json(folder / "inputs/prompts.json")
    env = {**dotenv_values(env_path), **os.environ}
    key = env.get("API_KEY_OPENAI") or env.get("OPENAI_API_KEY")
    if not key:
        raise ValueError("No OpenAI API credential configured")
    async with AsyncOpenAI(api_key=key, base_url=manifest["base_url"], timeout=180, max_retries=2) as client:
        if command == "preflight":
            await preflight(client, folder, manifest, sessions, prompts)
            return
        if not manifest.get("preflight", {}).get("passed"):
            raise ValueError("Successful preflight required before production")
        runs = [r for r in manifest["runs"] if not selectors or r["run_id"] in selectors]
        if selectors and len(runs) != len(set(selectors)):
            raise ValueError("Unknown run ID")
        # Small validation runs first so human comparisons are available early.
        runs = sorted(runs, key=lambda r: (not r["dataset"].startswith("validation"), r["condition"] != "benchmark"))
        for run in runs:
            if run["status"] == "complete":
                if digest((folder / run["file"]).read_bytes()) != run["output_sha256"]:
                    raise ValueError("Completed output changed")
                continue
            if not await execute_run(client, folder, manifest, run, sessions, prompts, workers, max_attempts):
                raise RuntimeError("Run incomplete; successful rows are saved. Resume after resolving errors.")


def main():
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["init", "preflight", "run", "status"])
    parser.add_argument("--campaign", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument("--env", type=Path, default=root.parent / ".env")
    parser.add_argument("--chats", type=Path, default=Path("/Users/nicolasroever/Dropbox/MI/data/raw/main_socialmedia/chats_raw.csv"))
    parser.add_argument("--survey", type=Path, default=Path("/Users/nicolasroever/Dropbox/MI/data/processed/main_social_media/clean_data.dta"))
    parser.add_argument("--benchmark-model", default="gpt-5.6-luna")
    parser.add_argument("--comparison-models", nargs="+", default=["gpt-5.5-2026-04-23", "gpt-5.4-2026-03-05"])
    parser.add_argument("--workers", type=int, default=40)
    parser.add_argument("--max-attempts", type=int, default=3, help="Retry rounds per invocation; successful scores never retried")
    parser.add_argument("--run-id", action="append", default=[])
    args = parser.parse_args()
    if args.workers < 1 or args.max_attempts < 1:
        parser.error("workers and max-attempts must be positive")
    folder = args.campaign.resolve()
    if args.command == "init":
        initialize(args.root.resolve(), folder, args.chats, args.survey, args.benchmark_model, args.comparison_models)
        return
    if args.command == "status":
        manifest = read_json(folder / "manifest.json")
        for run in manifest["runs"]:
            path = folder / run["file"]
            valid = 0
            if path.exists():
                frame = pd.read_csv(path, dtype={"error": str})
                valid = int(frame.error.eq("0").sum())
            print(run["dataset"], run["condition"], run["replicate"], run["model"], run["status"], f'{valid}/{run["expected_rows"]}')
        return
    with (folder / ".run.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        manifest = read_json(folder / "manifest.json")
        asyncio.run(run_selected(folder, manifest, args.env, args.command, args.workers, args.run_id, args.max_attempts))


if __name__ == "__main__":
    main()
