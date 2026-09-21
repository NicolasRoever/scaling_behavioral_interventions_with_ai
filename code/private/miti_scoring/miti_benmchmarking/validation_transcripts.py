raise RuntimeError("Restricted-input source only. Raw interview data are not distributed. API execution is disabled in this $0-API replication package; use code/python/run_public.py for saved-result reproduction.")
"""Local transcript assembly for MITI validation; no API dependencies."""

import csv
import hashlib
import json
from collections import defaultdict


def read_csv_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def build_validation_transcripts(rows, selected_ids, corrections):
    """Preserve CSV order, correct speaker roles and join page continuations.

    Corrections are explicit, content-checked records, not inferred from human
    scores. Human coding columns and explanations never enter the transcript.
    """
    selected_ids = set(selected_ids)
    groups = defaultdict(list)
    for csv_line, row in enumerate(rows, start=2):
        if row["source_pdf"] in selected_ids:
            groups[row["source_pdf"]].append((csv_line, row))
    if set(groups) != selected_ids:
        raise ValueError(f"Missing transcripts: {sorted(selected_ids - set(groups))}")

    applicable = {item["csv_line"]: item for item in corrections
                  if item["source_pdf"] in selected_ids}
    if len(applicable) != sum(item["source_pdf"] in selected_ids for item in corrections):
        raise ValueError("Duplicate transcript correction line")
    applied = set()
    audit = []
    sessions = []
    labels = {"P": "Clinician", "I": "Clinician", "C": "Client"}
    for source_pdf, source_rows in sorted(groups.items()):
        turns = []
        pages = []
        for csv_line, row in source_rows:
            text = row["Content"].strip()
            speaker = row["P_or_C"].strip()
            pages.append(int(row["page_num"]))
            if not text:
                raise ValueError(f"Empty transcript content at CSV line {csv_line}")
            correction = applicable.get(csv_line)
            if correction:
                if (correction["source_pdf"] != source_pdf or
                        correction["content_sha256"] != hashlib.sha256(row["Content"].encode()).hexdigest()):
                    raise ValueError(f"Transcript correction no longer matches CSV line {csv_line}")
                applied.add(csv_line)
                audit.append(dict(csv_line=csv_line, source_pdf=source_pdf,
                                  action=correction["action"], reason=correction["reason"]))
                if correction["action"] == "exclude_annotation":
                    continue
                if correction["action"] == "remove_header":
                    prefix = correction["prefix"]
                    if not text.startswith(prefix):
                        raise ValueError(f"Missing page header at CSV line {csv_line}")
                    text = text[len(prefix):].strip()
                elif correction["action"] == "continue_previous":
                    speaker = ""
                else:
                    raise ValueError(f"Unknown correction action: {correction['action']}")
            if speaker in labels:
                turns.append({"speaker": labels[speaker], "text": text})
            elif not speaker and not row["Utterance_Number"].strip() and turns:
                turns[-1]["text"] += " " + text
                audit.append(dict(csv_line=csv_line, source_pdf=source_pdf,
                                  action="join_continuation", speaker=turns[-1]["speaker"],
                                  reason="Unnumbered text continues the preceding speaker turn."))
            else:
                raise ValueError(f"Unresolved speaker at CSV line {csv_line}: {speaker!r}")
        if pages != sorted(pages):
            raise ValueError(f"Transcript page order is not monotonic: {source_pdf}")
        if {turn["speaker"] for turn in turns} != {"Clinician", "Client"}:
            raise ValueError(f"Transcript must contain both speakers: {source_pdf}")
        transcript = "\n".join(f"{turn['speaker']}: {turn['text']}" for turn in turns)
        sessions.append(dict(source_pdf=source_pdf, session_id=source_pdf,
                             transcript=transcript, source_rows=len(source_rows),
                             turns=len(turns), transcript_sha256=hashlib.sha256(transcript.encode()).hexdigest()))
    if applied != set(applicable):
        raise ValueError(f"Unapplied transcript corrections: {sorted(set(applicable) - applied)}")
    return sessions, audit


def load_validation_transcripts(transcript_path, selected_ids, corrections_path):
    corrections = json.loads(corrections_path.read_text(encoding="utf-8"))["corrections"]
    return build_validation_transcripts(read_csv_rows(transcript_path), selected_ids, corrections)
