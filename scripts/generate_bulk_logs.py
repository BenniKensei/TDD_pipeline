"""Generates telecom_traffic.jsonl with valid and malformed records."""

import json
import random
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "scenarios.db"
OUTPUT_FILE = Path(__file__).parent.parent / "data" / "telecom_traffic.jsonl"
TOTAL_RECORDS = 10_000
VALID_RATIO = 0.8


def generate_valid_telemetry() -> dict:
    """Generate a valid 5G telemetry JSON object."""
    return {
        "device_id": f"UE-{random.randint(1000, 9999)}",
        "timestamp": 1726740000 + random.randint(0, 100000),
        "SignalStrength": random.randint(-120, -50),
        "status": "ok",
        "cell_id": f"CELL-{random.randint(10, 99)}",
    }


def generate_malformed_payload(pattern: str) -> str:
    """Generate a concrete malformed payload based on the DB error pattern."""
    if "SIP" in pattern or "Fragmented header" in pattern:
        return "INVITE sip:alice@atlanta.com SIP/2.0\r\nCall-ID: 987654321"
    elif "ASN.1" in pattern or "Hex-Dump" in pattern:
        return "30a2ff02010101020304050607"
    elif "5G JSON" in pattern or "string data type" in pattern:
        return json.dumps({
            "device_id": "UE-9999",
            "SignalStrength": "excellent",
            "status": "error",
        })
    return "UNRECOGNIZED_MALFORMED_PAYLOAD"


def main() -> None:
    """Generate the bulk traffic JSONL file."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT error_pattern FROM telecom_chaos")
        scenarios = [row[0] for row in cursor.fetchall()]
        conn.close()
    except sqlite3.Error:
        scenarios = []

    if not scenarios:
        scenarios = [
            "Fragmented header with missing boundary tags",
            "Hex-Dump with mismatched length indicators",
            "Invalid string data type in the mandatory numeric SignalStrength field",
        ]

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for _ in range(TOTAL_RECORDS):
            if random.random() < VALID_RATIO:
                f.write(json.dumps(generate_valid_telemetry()) + "\n")
            else:
                pattern = random.choice(scenarios)
                f.write(generate_malformed_payload(pattern) + "\n")

    print(f"Successfully generated {TOTAL_RECORDS:,} logs in {OUTPUT_FILE}.")
    print(f" - ~{int(TOTAL_RECORDS * VALID_RATIO):,} valid 5G telemetry objects.")
    print(f" - ~{int(TOTAL_RECORDS * (1 - VALID_RATIO)):,} malformed records from scenarios.db.")


if __name__ == "__main__":
    main()
