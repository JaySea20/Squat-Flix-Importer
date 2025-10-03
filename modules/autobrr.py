#!/usr/bin/env python3

# =============================================================================
# File: autobrr.py
# Purpose: Handle Autobrr webhook payloads for Squat-Flix Importer
# Author: Joshua
# Created: 2025-10-02
# =============================================================================

__version__ = "v0.1.0-beta"

# ============================== Imports ======================================
import os
import json
import request
import dns.resolver
import modules.Jaylog
import modules.db
from pydantic import BaseModel
#from typing import Optional

# ============================== Globals ======================================

autobrr_logger = setup_logger(level="DEBUG", log_path="../logs/autobrr.log")

# ============================== Functions ====================================

def isAlive() -> bool:
    """
    Return True if Autobrr is alive and DNS resolves via external query.
    """
    try:
        with open("../json/config.json", "r") as f:
            config = json.load(f)
            autobrr_cfg = config.get("autobrr", {})
            host_url = autobrr_cfg.get("host", "")
            token = autobrr_cfg.get("apikey", "")
    except Exception:
        return False

    try:
        hostname = host_url.split("//")[-1].split(":")[0]
        answers = dns.resolver.resolve(hostname, "A", lifetime=3)
    except Exception:
        return False

    try:
        res = requests.get(
            f"{host_url}/api/healthz/liveness",
            headers={"X-API-Token": token},
            timeout=3
        )
        return res.status_code == 200
    except requests.RequestException:
        return False





_payload_buffer = None  # Internal memory store

def acceptPayload(payload: dict) -> dict:
    """
    Entry point for raw Autobrr payload.
    Takes possession of the incoming JSON and stores it in memory.
    Returns success status.
    """
    global _payload_buffer

    if not isinstance(payload, dict):
        return {"status": "error", "reason": "Payload must be a dictionary"}

    _payload_buffer = payload
    return {"status": "accepted"}


def logJSON(payload: dict):
    """
    Log the JSON object to console or file or both.
    """
    logger.debug(f"Autobrr payload: {json.dumps(payload, indent=2)}")

def storeJSON(payload: dict):
    """
    This is mainly just an abstraction
    Store the validated payload in SQLite.
    I want this to mainly just call the db.py function. 
    This is NOT the place for db code
    """
    store_json(source="autobrr", payload=payload)

def singleKey(payload: dict) -> dict:
    """
    returns the value of a specified key within the provided JSON object
    returns the value in an appropriate type.
    """

    return {k: payload.get(k) for k in keys if k in payload}

def keyGroup():
    """
    a very basic array of keys that can be used to select multiple keys from JSON objects.
    """
    return {True}


