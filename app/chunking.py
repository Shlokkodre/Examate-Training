"""
Chunking module for HealthLabelCheck
Splits regulation documents into searchable chunks
keeping source, page, and title metadata
"""

import json
import os
from typing import List, Dict


def chunk_regulation_record(record: Dict) -> List[Dict]:
    """
    Turn one regulation record into one or more chunks.
    Each chunk carries source, page, and title metadata.
    """
    chunks = []

    # Main chunk: requirement + details
    main_text = (
        f"Regulation {record['regulation_no']}: {record['requirement']}. "
        f"{record['details']}"
    )
    chunks.append({
        "id": f"reg_{record['regulation_no']}_main",
        "text": main_text,
        "source": record["source_doc"],
        "page": "Regulation " + record["regulation_no"],
        "title": record["requirement"],
        "regulation_no": record["regulation_no"],
        "applies_to": record["applies_to"],
    })

    # Extra chunk for exemption if it is not trivial
    if record.get("exemption") and record["exemption"].lower() != "none":
        ex_text = (
            f"Regulation {record['regulation_no']} exemption: {record['exemption']}"
        )
        chunks.append({
            "id": f"reg_{record['regulation_no']}_exemption",
            "text": ex_text,
            "source": record["source_doc"],
            "page": "Regulation " + record["regulation_no"],
            "title": record["requirement"] + " — Exemption",
            "regulation_no": record["regulation_no"],
            "applies_to": record["applies_to"],
        })

    return chunks


def chunk_all_records(records: List[Dict]) -> List[Dict]:
    """
    Convert every regulation record into chunks.
    Returns a flat list of chunk dicts.
    """
    all_chunks = []
    for record in records:
        all_chunks.extend(chunk_regulation_record(record))
    return all_chunks


def load_records() -> List[Dict]:
    """Load records from data/records.json"""
    path = "data/records.json"
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found — run app/ingest.py first")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    records = load_records()
    chunks = chunk_all_records(records)

    print(f"Records  : {len(records)}")
    print(f"Chunks   : {len(chunks)}")
    print("\nFirst chunk:")
    for k, v in chunks[0].items():
        print(f"  {k}: {v}")
    print("\nSecond chunk (exemption example):")
    exemption_chunks = [c for c in chunks if "exemption" in c["id"]]
    if exemption_chunks:
        for k, v in exemption_chunks[0].items():
            print(f"  {k}: {v}")
