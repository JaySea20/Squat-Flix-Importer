# =============================================================================
# File: json.py
# Purpose: Minimal JSON utilities for Squat-Flix Importer
# Author: Joshua
# Created: 2025-10-02
# =============================================================================

# ============================== Imports ======================================
import json
import httpx
import os
from typing import Any
from modules.Jaylog import mklog
# ============================== Logger =======================================

logger = mklog(__name__, level="DEBUG", logfile="../logs/json.log")
logger.debug("Initialized JSON logger at ../logs/json.log")

#===================================================================
#      Exists?
#===================================================================

def exists(path: str) -> bool:
    result = os.path.isfile(path)
    logger.debug(f"Checked existence of {path}: {result}")
    return result


#===================================================================
#      Validate
#===================================================================

def validate_json(text: str) -> bool:
    try:
        json.loads(text)
        logger.debug(f"JSON passes validation")
        return True
    except json.JSONDecodeError:
        logger.error(f"JSON FAILED validation")
        return False


#===================================================================
#      Load
#===================================================================

def load(path: str) -> Any:
    """
    Load JSON from file and return native Python object.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    logger.debug(f"Loaded JSON from {path}")
    return data

#===================================================================
#      Dump
#===================================================================

def dump(data: Any, path: str, indent: int = 2):
    """
    Write Python object to file as JSON.
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent)
    logger.debug(f"Dumped JSON to {path}")

#===================================================================
#      Parse
#===================================================================

def parse(text: str) -> Any:
    """
    Parse JSON string into Python object.
    """
    result = json.loads(text)
    logger.debug("Parsed JSON string")
    return result

#===================================================================
#      Stringify
#===================================================================

def stringify(data: Any, indent: int = 2) -> str:
    """
    Convert Python object to JSON string.
    """
    result = json.dumps(data, indent=indent)
    logger.debug("Stringified Python object to JSON")
    return result

#===================================================================
#      Pretty
#===================================================================

def pretty(data: Any):
    """
    Print JSON to console in readable format.
    """
    print(json.dumps(data, indent=2))
    logger.debug("Printed JSON to console")


#===================================================================
#      API-Call
#===================================================================

async def call_external_api(
    url: str,
    method: str = "GET",
    headers: dict = None,
    payload: dict = None,
    timeout: int = 10) -> dict:
    """
    Make an outbound API call.
    Supports GET/POST with optional headers and JSON payload.
    """
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            logger.debug(f"Calling {method} {url} with timeout={timeout}")
            if method.upper() == "POST":
                response = await client.post(url, headers=headers, json=payload)
            else:
                response = await client.get(url, headers=headers, params=payload)

            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            logger.warning(f"API call failed: {e}")
            return {"error": str(e), "status_code": getattr(e.response, "status_code", None)}
