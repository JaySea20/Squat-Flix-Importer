#!/usr/bin/env python3

# =============================================================================
# File: autobrr.py
# Purpose: Handle Autobrr webhook payloads for Squat-Flix Importer
# Author: Joshua
# Created: 2025-10-02
# =============================================================================

__version__ = "v0.1.0-beta"

# ============================== Imports ======================================
import os, json, requests, dns.resolver
from modules.logger import setup_logger
from modules.db import store_json
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional

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




#def validateJSON(payload: dict):
#    """
#    Minimal validation for complete Autobrr data.
#    This is NOT meant to be useable with any other JSON objects. 
#    We are trying to be specific to autobrr api json here
#    type checks
#    null checks
#    scope checks ( is there a year that is 0? That cant be right)
#    """
#    return the full json object

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


# ============================== Schema =======================================

# This still needs alot of work to get it into a JSON object that can be worked with out JSON functions
'''
class autobrrData(BaseModel):
    Artists: Optional[str]
    Audio: Optional[List[str]]
    AudioChannels: Optional[str]
    AudioFormat: Optional[str]
    Bitrate: Optional[str]
    Bonus: Optional[List[str]]
    Categories: Optional[List[str]]
    Category: Optional[str]
    Codec: Optional[List[str]]
    Container: Optional[str]
    CurrentDay: Optional[int]
    CurrentHour: Optional[int]
    CurrentMinute: Optional[int]
    CurrentMonth: Optional[int]
    CurrentSecond: Optional[int]
    CurrentYear: Optional[int]
    Day: Optional[int]
    Description: Optional[str]
    DownloadURL: Optional[str]
    Episode: Optional[int]
    FilterID: Optional[int]
    FilterName: Optional[str]
    Freeleech: Optional[bool]
    FreeleechPercent: Optional[int]
    Group: Optional[str]
    GroupID: Optional[str]
    HasCue: Optional[bool]
    HasLog: Optional[bool]
    HDR: Optional[str]
    Implementation: Optional[str]
    Indexer: Optional[str]
    IndexerIdentifier: Optional[str]
    IndexerIdentifierExternal: Optional[str]
    IndexerName: Optional[str]
    InfoUrl: Optional[str]
    IsDuplicate: Optional[bool]
    Language: Optional[List[str]]
    Leechers: Optional[int]
    LogScore: Optional[int]
    MagnetURI: Optional[str]
    MetaIMDB: Optional[str]
    Month: Optional[int]
    Origin: Optional[str]
    Other: Optional[List[str]]
    PreTime: Optional[str]
    Proper: Optional[bool]
    Protocol: Optional[str]
    RecordLabel: Optional[str]
    Region: Optional[str]
    Repack: Optional[bool]
    Resolution: Optional[str]
    Season: Optional[int]
    Seeders: Optional[int]
    Size: Optional[int]
    SizeString: Optional[str]
    SkipDuplicateProfileID: Optional[int]
    SkipDuplicateProfileName: Optional[str]
    Source: Optional[str]
    Tags: Optional[str]
    Title: Optional[str]
    TorrentDataRawBytes: Optional[str]
    TorrentHash: Optional[str]
    TorrentID: Optional[str]
    TorrentName: Optional[str]
    TorrentPathName: Optional[str]
    TorrentTmpFile: Optional[str]
    TorrentUrl: Optional[str]
    Type: Optional[str]
    Uploader: Optional[str]
    Website: Optional[str]
    Year: Optional[int]
'''
