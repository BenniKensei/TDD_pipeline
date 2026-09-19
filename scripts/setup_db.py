"""Populates scenarios.db with telecom chaos scenarios."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "scenarios.db"


def setup_database() -> None:
    """Create and populate the telecom_chaos table in scenarios.db."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS telecom_chaos (
            id INTEGER PRIMARY KEY,
            protocol TEXT,
            error_pattern TEXT
        )
    """)

    # Clear existing rows to avoid duplicates on multiple runs
    cursor.execute("DELETE FROM telecom_chaos")

    scenarios = [
        ("SIP", "Fragmented header with missing boundary tags"),
        ("ASN.1", "Hex-Dump with mismatched length indicators"),
        ("5G JSON", "Invalid string data type in the mandatory numeric SignalStrength field"),
    ]
    cursor.executemany(
        "INSERT INTO telecom_chaos (protocol, error_pattern) VALUES (?, ?)",
        scenarios,
    )

    conn.commit()
    conn.close()
    print(f"scenarios.db successfully set up at {DB_PATH}")


if __name__ == "__main__":
    setup_database()
