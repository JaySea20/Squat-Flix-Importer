
# =============================================================================
# File: db.py
# Purpose: Store and retrieve JSON payloads in SQLite for Squat-Flix Importer
# Author: Joshua
# Created: 2025-10-02
# =============================================================================

# ============================== Imports ======================================

import sqlite3
import os
import json
from modules.Jaylog import mklog

# ============================== Constants ====================================

DB_PATH = os.getenv("SQLITE_DB_PATH", "./logs/squatflix.db")

# ============================== Logging ====================================

logger = mklog(__name__, level="DEBUG", log_path="./../logs/db.log")

# ============================== Initialize ====================================


def init():
    logger.debug("Initializing SQLite database and ensuring events table exists")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                source TEXT NOT NULL,
                imdb_id TEXT,
                payload TEXT NOT NULL
            )
        """)
        conn.commit()
    logger.debug("Database initialized successfully")

# ============================== Store ====================================

def store_json(source: str, payload: dict):
    logger.debug(f"Storing payload from source '{source}' with timestamp {payload.get('timestamp')}")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO events (timestamp, source, imdb_id, payload)
            VALUES (?, ?, ?, ?)
        """, (
            payload.get("timestamp"),
            source,
            payload.get("imdbId"),
            json.dumps(payload)
        ))
        conn.commit()
    logger.debug("Payload stored successfully")


# ============================== Fetch ====================================

def fetch_json(limit: int = 100) -> list:
    logger.debug(f"Fetching up to {limit} recent payloads from database")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT payload FROM events ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
    logger.debug(f"Fetched {len(rows)} payloads")
    return [json.loads(row[0]) for row in rows]


