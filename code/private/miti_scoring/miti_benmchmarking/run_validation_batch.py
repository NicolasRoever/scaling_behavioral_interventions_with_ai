raise RuntimeError("Restricted-input source only. Raw interview data are not distributed. API execution is disabled in this $0-API replication package; use code/python/run_public.py for saved-result reproduction.")
"""Upload prepared global-validation batches, wait, and download their results.

The normal command makes paid OpenAI API requests. --dry-run is fully offline.
The same command resumes saved batches; it never automatically reruns failures.
"""

import argparse
import csv
import fcntl
import hashlib
import io
import json
import os
import sys
import time
import uuid
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class BatchRunnerError(Exception):
    """A local validation or recovery error safe to display to the user."""


def digest(data):
    return hashlib.sha256(data).hexdigest()


def atomic_bytes(path, data):
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def save_state(path, state):
    atomic_bytes(path, (json.dumps(state, ensure_ascii=False, indent=2) + "\n").encode())


def local_path(folder, name):
    path = (folder / name).resolve()
    if not path.is_relative_to(folder.resolve()):
        raise BatchRunnerError(f"Manifest path is outside the batch folder: {name}")
    return path


def load_manifest(path):
    manifest = json.loads(path.read_text(encoding="utf-8"))
    folder = path.parent
    if manifest.get("endpoint") != "/v1/responses" or manifest.get("completion_window") != "24h":
        raise BatchRunnerError("Expected a Responses API batch manifest with a 24h completion window")
    index = {row["custom_id"]: row for row in manifest["request_index"]}
    if len(index) != len(manifest["request_index"]):
        raise BatchRunnerError("Duplicate request IDs in manifest")
    seen = set()
    filenames = set()
    for batch in manifest["batches"]:
        if batch["file"] in filenames:
            raise BatchRunnerError("Duplicate batch input filename")
        filenames.add(batch["file"])
        content = local_path(folder, batch["file"]).read_bytes()
        if digest(content) != batch["sha256"]:
            raise BatchRunnerError(f"Batch input changed: {batch['file']}")
        rows = [json.loads(line) for line in content.decode().splitlines()]
        if len(rows) != batch["requests"]:
            raise BatchRunnerError(f"Request count mismatch: {batch['file']}")
        for row in rows:
            identifier = row["custom_id"]
            if identifier in seen or identifier not in index:
                raise BatchRunnerError(f"Duplicate or unknown custom_id: {identifier}")
            metadata = index[identifier]
            if (row["method"] != "POST" or row["url"] != manifest["endpoint"] or
                    row["body"]["model"] != batch["model"] or metadata["model"] != batch["model"] or
                    digest(row["body"]["input"].encode()) != metadata["prompt_sha256"]):
                raise BatchRunnerError(f"Request differs from manifest: {identifier}")
            seen.add(identifier)
    if seen != set(index) or len(seen) != manifest["requests"]:
        raise BatchRunnerError("Batch inputs do not cover the complete request index")
    return manifest, digest(path.read_bytes())


def load_or_create_state(path, manifest, manifest_sha256):
    if path.exists():
        state = json.loads(path.read_text(encoding="utf-8"))
        if state["manifest_sha256"] != manifest_sha256:
            raise BatchRunnerError("Saved batch state belongs to a different manifest")
        if set(state["batches"]) != {batch["file"] for batch in manifest["batches"]}:
            raise BatchRunnerError("Saved batch state has a different input-file set")
        return state
    state = dict(schema_version=1, manifest_sha256=manifest_sha256,
                 created_at_unix=int(time.time()),
                 batches={batch["file"]: dict(model=batch["model"], status="not_submitted")
                          for batch in manifest["batches"]})
    save_state(path, state)
    return state


def ensure_submitted(client, folder, manifest, state, state_path, collect_only):
    """Persist IDs before advancing. Recover an uncertain create by metadata.

    SDK retries must be disabled on the supplied client. If a create times out,
    a later invocation searches for the saved submission token instead of
    automatically making another paid batch.
    """
    for batch in manifest["batches"]:
        entry = state["batches"][batch["file"]]
        if entry.get("batch_id"):
            continue
        if entry.get("submission_token"):
            matches = [item for item in client.batches.list(limit=100)
                       if (item.metadata or {}).get("submission_token") == entry["submission_token"]]
            if len(matches) != 1:
                raise BatchRunnerError(
                    f"Uncertain prior submission for {batch['file']}: found {len(matches)} matching batches. "
                    "No replacement was submitted. Check the OpenAI Batch dashboard and rerun later.")
            remote = matches[0]
            if remote.input_file_id != entry["input_file_id"] or remote.endpoint != manifest["endpoint"]:
                raise BatchRunnerError("Recovered batch does not match the saved input file")
            entry.update(batch_id=remote.id, status=remote.status, submitted_at_unix=remote.created_at)
            save_state(state_path, state)
            print(f"Recovered {batch['model']}: {remote.id}", flush=True)
            continue
        if collect_only:
            raise BatchRunnerError("Some batches have not been submitted; omit --collect-only to submit them")
        if not entry.get("input_file_id"):
            with local_path(folder, batch["file"]).open("rb") as stream:
                uploaded = client.files.create(file=stream, purpose="batch")
            entry.update(input_file_id=uploaded.id, status="uploaded", uploaded_at_unix=int(time.time()))
            save_state(state_path, state)
        entry.update(submission_token=uuid.uuid4().hex, status="submitting",
                     submission_started_at_unix=int(time.time()))
        save_state(state_path, state)
        remote = client.batches.create(
            input_file_id=entry["input_file_id"], endpoint=manifest["endpoint"],
            completion_window=manifest["completion_window"],
            metadata={"submission_token": entry["submission_token"],
                      "manifest_sha256": state["manifest_sha256"], "input_sha256": batch["sha256"]})
        entry.update(batch_id=remote.id, status=remote.status, submitted_at_unix=remote.created_at)
        save_state(state_path, state)
        print(f"Submitted {batch['model']}: {remote.id} ({batch['requests']} requests)", flush=True)


def download_file(client, folder, state, state_path, entry, kind, file_id, filename):
    previous = entry.get(kind)
    if previous:
        if previous["file_id"] != file_id:
            raise BatchRunnerError("The server returned a different result file for a completed batch")
        path = local_path(folder, previous["path"])
        if path.exists():
            if digest(path.read_bytes()) != previous["sha256"]:
                raise BatchRunnerError(f"Downloaded result changed locally: {path.name}")
            return
    path = folder / "results" / filename
    path.parent.mkdir(exist_ok=True)
    content = client.files.content(file_id).content
    # Validate JSONL before replacing an existing download.
    for line in content.decode("utf-8").splitlines():
        json.loads(line)
    atomic_bytes(path, content)
    entry[kind] = dict(file_id=file_id, path=str(path.relative_to(folder)),
                       sha256=digest(content), downloaded_at_unix=int(time.time()))
    save_state(state_path, state)


def refresh_batches(client, folder, manifest, state, state_path):
    terminal = {"completed", "failed", "expired", "cancelled"}
    complete = True
    statuses = []
    for batch in manifest["batches"]:
        entry = state["batches"][batch["file"]]
        remote = client.batches.retrieve(entry["batch_id"]).model_dump(mode="json")
        entry.update(status=remote["status"], checked_at_unix=int(time.time()), remote=remote)
        save_state(state_path, state)
        counts = remote.get("request_counts") or {}
        statuses.append(f"{batch['model']}: {remote['status']} "
                        f"({counts.get('completed', 0)}/{batch['requests']}, "
                        f"{counts.get('failed', 0)} failed)")
        if remote["status"] not in terminal:
            complete = False
            continue
        for kind in ["output", "error"]:
            file_id = remote.get(kind + "_file_id")
            if file_id:
                filename = batch["file"].replace("batch_input_", f"batch_{kind}_", 1)
                download_file(client, folder, state, state_path, entry, kind, file_id, filename)
    return complete, statuses


def parse_result(record):
    from run_campaign import parse_score

    result = dict(score="", justification="", error="", raw_output="", response_id="",
                  response_model="", response_created_at_unix="", input_tokens=0,
                  cached_input_tokens=0, output_tokens=0, reasoning_tokens=0)
    if record.get("error"):
        result["error"] = "batch_error:" + str(record["error"].get("code", "unknown"))
        return result
    response = record.get("response") or {}
    if response.get("status_code") != 200:
        result["error"] = f"http_status:{response.get('status_code', 'missing')}"
        return result
    body = response.get("body") or {}
    result.update(response_id=body.get("id", ""), response_model=body.get("model", ""),
                  response_created_at_unix=body.get("created_at", ""))
    usage = body.get("usage") or {}
    result.update(input_tokens=usage.get("input_tokens", 0), output_tokens=usage.get("output_tokens", 0),
                  cached_input_tokens=(usage.get("input_tokens_details") or {}).get("cached_tokens", 0),
                  reasoning_tokens=(usage.get("output_tokens_details") or {}).get("reasoning_tokens", 0))
    result["raw_output"] = "".join(
        part.get("text", "") for item in body.get("output", []) if item.get("type") == "message"
        for part in item.get("content", []) if part.get("type") == "output_text")
    if body.get("status") != "completed":
        result["error"] = "response_status:" + str(body.get("status", "missing"))
    elif any(part.get("type") == "refusal" for item in body.get("output", [])
             if item.get("type") == "message" for part in item.get("content", [])):
        result["error"] = "refusal"
    else:
        try:
            result.update(parse_score(result["raw_output"]))
        except (ValueError, TypeError):
            result["error"] = "invalid_score_json"
    return result


def export_results(folder, manifest, state):
    """Match by custom_id; preserve an explicit row for each missing/failed score."""
    index = {row["custom_id"]: row for row in manifest["request_index"]}
    returned = {}
    for entry in state["batches"].values():
        for kind in ["output", "error"]:
            download = entry.get(kind)
            if not download:
                continue
            content = local_path(folder, download["path"]).read_bytes()
            if digest(content) != download["sha256"]:
                raise BatchRunnerError("Result checksum mismatch")
            for line in content.decode().splitlines():
                record = json.loads(line)
                identifier = record.get("custom_id")
                if identifier not in index or identifier in returned:
                    raise BatchRunnerError(f"Unknown or duplicate result ID: {identifier}")
                if index[identifier]["model"] != entry["model"]:
                    raise BatchRunnerError(f"Result belongs to the wrong model batch: {identifier}")
                returned[identifier] = (record, entry["batch_id"])
    rows = []
    for metadata in manifest["request_index"]:
        identifier = metadata["custom_id"]
        if identifier in returned:
            record, batch_id = returned[identifier]
            result = parse_result(record)
        else:
            result = parse_result({"error": {"code": "not_returned"}})
            batch_id = next(entry.get("batch_id", "") for entry in state["batches"].values()
                            if entry["model"] == metadata["model"])
        rows.append({**metadata, "batch_id": batch_id, **result})
    output = folder / "results"
    output.mkdir(exist_ok=True)
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    atomic_bytes(output / "global_scores.csv", buffer.getvalue().encode())
    summary = dict(updated_at_unix=int(time.time()), expected_requests=len(index),
                   returned_requests=len(returned), valid_scores=sum(not row["error"] for row in rows),
                   missing_requests=len(index) - len(returned),
                   failed_or_missing_scores=sum(bool(row["error"]) for row in rows),
                   input_tokens=sum(row["input_tokens"] for row in rows),
                   cached_input_tokens=sum(row["cached_input_tokens"] for row in rows),
                   output_tokens=sum(row["output_tokens"] for row in rows),
                   reasoning_tokens=sum(row["reasoning_tokens"] for row in rows))
    save_state(output / "summary.json", summary)
    return summary


def run_batches(client, folder, manifest, manifest_sha256, collect_only, no_wait, poll_seconds, sleep_fn):
    state_path = folder / "batch_state.json"
    state = load_or_create_state(state_path, manifest, manifest_sha256)
    ensure_submitted(client, folder, manifest, state, state_path, collect_only)
    previous_statuses = None
    while True:
        complete, statuses = refresh_batches(client, folder, manifest, state, state_path)
        if statuses != previous_statuses:
            print("\n".join(statuses), flush=True)
            previous_statuses = statuses
        if complete or no_wait:
            if complete or any(entry.get("output") or entry.get("error") for entry in state["batches"].values()):
                summary = export_results(folder, manifest, state)
                print(f"Results: {folder / 'results/global_scores.csv'} "
                      f"({summary['valid_scores']}/{summary['expected_requests']} valid scores)", flush=True)
                if complete and (summary["failed_or_missing_scores"] or
                                 any(entry["status"] != "completed" for entry in state["batches"].values())):
                    return 2
            return 0
        sleep_fn(poll_seconds)


def load_api_key(env_path, environment):
    from dotenv import dotenv_values

    # The explicitly selected .env takes precedence over ambient shell keys.
    values = dotenv_values(env_path, interpolate=False) if env_path.is_file() else {}
    key = (values.get("OPENAI_API_KEY") or values.get("API_KEY_OPENAI") or
           environment.get("OPENAI_API_KEY") or environment.get("API_KEY_OPENAI"))
    if not key or not key.strip():
        raise BatchRunnerError(f"Set OPENAI_API_KEY in {env_path}")
    return key.strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True, help="Prepared batch_input_*_manifest.json")
    parser.add_argument("--env", type=Path, default=Path(__file__).resolve().parent.parent / ".env")
    parser.add_argument("--poll-seconds", type=int, default=60)
    parser.add_argument("--no-wait", action="store_true", help="Submit/check once and exit; rerun later to collect")
    parser.add_argument("--collect-only", action="store_true", help="Only resume existing submissions; never create a batch")
    parser.add_argument("--dry-run", action="store_true", help="Check local inputs only; no key or network needed")
    args = parser.parse_args()
    if not 1 <= args.poll_seconds <= 60:
        parser.error("--poll-seconds must be between 1 and 60")
    manifest_path = args.manifest.resolve()
    try:
        manifest, manifest_sha256 = load_manifest(manifest_path)
        print(f"Validated {manifest['requests']} requests across {len(manifest['batches'])} model batches.", flush=True)
        if args.dry_run:
            print("Dry run complete. No credentials read and no API calls made.")
            return 0
        with (manifest_path.parent / ".batch_runner.lock").open("a") as lock:
            try:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise BatchRunnerError("Another runner is already using this batch folder") from None
            api_key = load_api_key(args.env, os.environ)
            from openai import OpenAI
            # No automatic retries of a potentially accepted paid batch creation.
            with OpenAI(api_key=api_key, base_url="https://api.openai.com/v1", max_retries=0, timeout=120) as client:
                return run_batches(client, manifest_path.parent, manifest, manifest_sha256,
                                   args.collect_only, args.no_wait, args.poll_seconds, time.sleep)
    except KeyboardInterrupt:
        print("\nStopped waiting. Submitted batches continue remotely; rerun the same command to resume.")
        return 130
    except BatchRunnerError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        # Do not echo SDK exception strings, which can contain credentials or input.
        print(f"Stopped: {type(exc).__name__} (HTTP status {getattr(exc, 'status_code', 'n/a')}). "
              "Saved batch state is retained; rerun the same command to resume.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
