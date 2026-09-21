raise RuntimeError("Restricted-input source only. Raw interview data are not distributed. API execution is disabled in this $0-API replication package; use code/python/run_public.py for saved-result reproduction.")
"""Prepare dated Batch API JSONL files for global validation, entirely offline.

Creates inputs only: never reads credentials, uploads files, or calls an API.
Each JSONL contains a single model. Four dimensions are requested separately
for every interview in each of nine conditions; repeats have distinct IDs.
"""

import argparse
import hashlib
import json
import shutil
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

# Direct script execution and package imports both use the shared study prompts.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from miti_global_scores import MITI_GUIDE, VALIDATION_PROMPT
from robustness_run_scoring import ABLATED_LINE
from miti_benmchmarking.validation_transcripts import load_validation_transcripts, read_csv_rows


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def validation_conditions(luna_model, gpt54_model, gpt55_model, luna_reasoning):
    conditions = [dict(id="luna_benchmark", condition="benchmark", replicate=0,
                       model=luna_model, reasoning_effort=luna_reasoning, ablation=False)]
    conditions += [dict(id=f"luna_rerun_{replicate:02d}", condition="rerun", replicate=replicate,
                        model=luna_model, reasoning_effort=luna_reasoning, ablation=False)
                   for replicate in range(1, 6)]
    conditions += [dict(id="luna_ablation", condition="ablation", replicate=0,
                        model=luna_model, reasoning_effort=luna_reasoning, ablation=True)]
    conditions += [dict(id=name, condition="model_comparison", replicate=0,
                        model=model, reasoning_effort="none", ablation=False)
                   for name, model in [("gpt54_minimum", gpt54_model), ("gpt55_minimum", gpt55_model)]]
    return conditions


def build_requests(sessions, guide, prompt, ablated_line, conditions, max_output_tokens):
    if prompt.count(ablated_line) != 1:
        raise ValueError("Expected exactly one conservative-scoring instruction")
    if "# Change Goal" in prompt or "social media" in prompt.lower():
        raise ValueError("Validation template must not prescribe a social-media goal")
    if len(guide) != 4 or len(conditions) != 9:
        raise ValueError("Expected four global dimensions and nine conditions")
    requests = []
    index = []
    for condition in conditions:
        template = prompt.replace(ablated_line, "") if condition["ablation"] else prompt
        for session in sessions:
            for dimension_number, (dimension, instructions) in enumerate(guide.items(), start=1):
                rendered = template.format(transcript=session["transcript"],
                                           component_name=dimension, coding_instructions=instructions)
                custom_id = f"{condition['id']}__{sha256(session['source_pdf'].encode())[:12]}__d{dimension_number}"
                body = dict(model=condition["model"], input=rendered,
                            reasoning={"effort": condition["reasoning_effort"]},
                            text={"verbosity": "medium"}, store=False,
                            max_output_tokens=max_output_tokens)
                requests.append(dict(custom_id=custom_id, method="POST", url="/v1/responses", body=body))
                index.append(dict(custom_id=custom_id, source_pdf=session["source_pdf"],
                                  miti_dimension=dimension, condition_id=condition["id"],
                                  condition=condition["condition"], replicate=condition["replicate"],
                                  model=condition["model"], reasoning_effort=condition["reasoning_effort"],
                                  prompt_variant="ablation" if condition["ablation"] else "standard",
                                  prompt_sha256=sha256(rendered.encode()),
                                  transcript_sha256=session["transcript_sha256"]))
    if len({request["custom_id"] for request in requests}) != len(requests):
        raise ValueError("Batch custom IDs must be unique")
    expected = len(sessions) * len(guide)
    if set(Counter(row["condition_id"] for row in index).values()) != {expected}:
        raise ValueError("Conditions have inconsistent sample coverage")
    return requests, index


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prepare_batch(transcript_path, human_path, subset_path, corrections_path, output_dir,
                  guide, prompt, ablated_line, conditions, max_output_tokens, created_at_unix):
    selected_ids = {row["source_pdf"] for row in read_csv_rows(subset_path)}
    if len(selected_ids) != 14:
        raise ValueError(f"Expected the previous 14-interview subset, found {len(selected_ids)}")
    human = read_csv_rows(human_path)
    human_by_id = {row["source_pdf"]: row for row in human}
    if len(human_by_id) != len(human) or selected_ids - set(human_by_id):
        raise ValueError("Missing or duplicate human-reference interviews")
    for source_pdf in selected_ids:
        for column in ["CCT", "SST", "PAR", "EMP"]:
            if human_by_id[source_pdf][column] not in {"1", "2", "3", "4", "5"}:
                raise ValueError(f"Invalid human reference: {source_pdf}, {column}")
    sessions, audit = load_validation_transcripts(transcript_path, selected_ids, corrections_path)
    requests, request_index = build_requests(sessions, guide, prompt, ablated_line, conditions, max_output_tokens)
    grouped = defaultdict(list)
    for request in requests:
        grouped[request["body"]["model"]].append(request)
    stamp = datetime.fromtimestamp(created_at_unix, timezone.utc).strftime("%Y%m%d")
    output_dir.mkdir(parents=True, exist_ok=False)
    inputs_dir = output_dir / "inputs"
    inputs_dir.mkdir()
    source_files = {}
    for name, path in [("transcripts", transcript_path), ("human_scores", human_path),
                       ("subset", subset_path), ("transcript_corrections", corrections_path)]:
        destination = inputs_dir / (name + path.suffix)
        shutil.copy2(path, destination)
        source_files[name] = dict(source=str(path.resolve()), snapshot=str(destination.relative_to(output_dir)),
                                  sha256=sha256(destination.read_bytes()))
    write_json(inputs_dir / "sessions.json", sessions)
    write_json(inputs_dir / "prompts.json", dict(standard=prompt, ablation=prompt.replace(ablated_line, ""), guide=guide))
    write_json(inputs_dir / "transcript_audit.json", audit)
    batches = []
    for model, records in grouped.items():
        path = output_dir / f"batch_input_{stamp}_{model}.jsonl"
        with path.open("x", encoding="utf-8") as stream:
            for record in records:
                stream.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
        # Parse the serialized records, not just the in-memory representation.
        parsed = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        if parsed != records or {record["body"]["model"] for record in parsed} != {model}:
            raise ValueError(f"Batch serialization validation failed: {path}")
        if len(parsed) > 50000 or path.stat().st_size > 200_000_000:
            raise ValueError(f"Batch exceeds documented upload limits: {path}")
        batches.append(dict(file=path.name, model=model, requests=len(records),
                            bytes=path.stat().st_size, sha256=sha256(path.read_bytes())))
    manifest = dict(schema_version=1, created_at_unix=created_at_unix, status="prepared_not_submitted",
                    preparation_cost_usd=0, api_calls_made=0, interviews=len(sessions),
                    dimensions=list(guide), requests=len(requests), endpoint="/v1/responses",
                    completion_window="24h", max_output_tokens=max_output_tokens,
                    conditions=conditions, batches=batches, source_files=source_files,
                    sessions_file="inputs/sessions.json", prompt_file="inputs/prompts.json",
                    transcript_audit_file="inputs/transcript_audit.json", request_index=request_index,
                    notes=["Only global scoring; no behavioral-count requests.",
                           "P and I map to Clinician; C maps to Client.",
                           "Human reference scores and behavioral codes are never included in prompts.",
                           "Luna baseline plus five repeats use identical bodies and distinct custom IDs; no seed is set.",
                           "The ablation removes only the conservative-scoring sentence.",
                           "Minimum GPT-5.4/GPT-5.5 reasoning is none; Luna uses low.",
                           "No API upload, submission, preflight, or inference is performed."])
    manifest_path = output_dir / f"batch_input_{stamp}_manifest.json"
    write_json(manifest_path, manifest)
    return manifest_path, manifest


def main():
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transcripts", type=Path, default=root.parent / "output/validation_bheavioral_scores_extracted.csv")
    parser.add_argument("--human-scores", type=Path, default=root.parent / "output/validation_global_scores_extracted.csv")
    parser.add_argument("--subset", type=Path, default=root.parent / "output/behavioral_counts_validation_2025-11-25.csv")
    parser.add_argument("--corrections", type=Path, default=root / "validation_transcript_corrections.json")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    created_at_unix = int(time.time())
    stamp = datetime.fromtimestamp(created_at_unix, timezone.utc).strftime("%Y%m%d")
    output_dir = args.output_dir or root / "runs" / f"validation_batch_{stamp}_{created_at_unix}"
    conditions = validation_conditions("gpt-5.6-luna", "gpt-5.4-2026-03-05", "gpt-5.5-2026-04-23", "low")
    manifest_path, manifest = prepare_batch(args.transcripts, args.human_scores, args.subset, args.corrections,
                                            output_dir, MITI_GUIDE, VALIDATION_PROMPT, ABLATED_LINE,
                                            conditions, 9000, created_at_unix)
    print(f"Prepared {manifest['requests']} requests for {manifest['interviews']} interviews. API calls: 0. Preparation cost: $0.")
    for batch in manifest["batches"]:
        print(f"{batch['requests']} requests: {output_dir / batch['file']}")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
