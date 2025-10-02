#!/usr/bin/env python3
# ============================================================
#   Squat-Flix Webhook Listener for Autobrr
# ============================================================

from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
from modules.logger import setup_logger
import sys
import subprocess
import logging
import time
import os
import json

sys.dont_write_bytecode = True

# ===========================================================================================
#  PATH HELPERS
# ===========================================================================================

# Dynamically resolve the directory where this script lives
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Main script path (not critical unless used externally)
SCRIPT_PATH = os.path.join(SCRIPT_DIR, "squat_flix_importer.py")

# Config path: env override or default to script-relative
CONFIG_PATH = os.getenv("SQUATFLIX_CONFIG", os.path.join(SCRIPT_DIR, "json", "config.json"))

# Log path: env override or default to script-relative
LOG_PATH = os.getenv("SQUATFLIX_LOG", os.path.join(SCRIPT_DIR, "logs", "squatflix.log"))

# --------------------------------------------------------------- PATH HELPERS
# ===========================================================================================


# ------------------------------------------------------------
#   Lifecycle Logging
# ------------------------------------------------------------

logger = setup_logger(level="DEBUG", log_path=LOG_PATH)


# ------------------------------------------------------------
#   FastAPI Setup
# ------------------------------------------------------------

app = FastAPI()
templates = Jinja2Templates(directory="web/templates")
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# ------------------------------------------------------------
#   Autobrr Webhook Listener
# ------------------------------------------------------------

class AutoBRRPayload(BaseModel):
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


@app.post("/webhook/autobrr")
async def autobrr_webhook(payload: AutoBRRPayload):
    with open("json/autobrr_payload.json", "w") as f:
        json.dump(payload.dict(), f, indent=2)
    return {"status": "ok", "title": payload.Title, "year": payload.Year}

    # Log each field explicitly
    logger.debug(f"Title: {payload.Title}")
    logger.debug(f"Year: {payload.Year}")
    logger.debug(f"Resolution: {payload.Resolution}")
    logger.debug(f"Codec: {payload.Codec}")
    logger.debug(f"IMDB: {payload.IMDB}")
    logger.debug(f"Bytes: {payload.Bytes}")
    logger.debug(f"Size: {payload.Size}")
    logger.debug(f"FilterName: {payload.FilterName}")
    logger.debug(f"TorrentURL: {payload.TorrentURL}")
    logger.debug(f"TimeStamp: {payload.TimeStamp}")


# ------------------------------------------------------------
#   Index
# ------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ------------------------------------------------------------
#   Events
# ------------------------------------------------------------

@app.get("/events", response_class=HTMLResponse)
def events(request: Request):
    event_list = []
    try:
        for fname in sorted(os.listdir("json"), reverse=True):
            if fname.startswith("autobrr_event_") and fname.endswith(".json"):
                with open(os.path.join("..", "json", fname)) as f:
                    data = json.load(f)
                    event_list.append({
                        "filename": fname,
                        "title": data.get("releaseName", "Unknown"),
                        "indexer": data.get("indexer", "Unknown"),
                        "timestamp": fname.replace("autobrr_event_", "").replace(".json", "")
                    })
    except Exception as e:
        logger.warning(f"Failed to load events: {e}")

    return templates.TemplateResponse("events.html", {"request": request, "events": event_list})



# ------------------------------------------------------------
#   Config
# ------------------------------------------------------------


@app.get("/config", response_class=HTMLResponse)
def config_view(request: Request):
    try:
        with open("json/config.json") as f:
            config_data = json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load config: {e}")
        config_data = {}

    return templates.TemplateResponse("config.html", {"request": request, "config": config_data})



# ------------------------------------------------------------
#   Replay
# ------------------------------------------------------------


@app.get("/replay", response_class=HTMLResponse)
def replay_view(request: Request):
    try:
        files = [f for f in os.listdir("json") if f.startswith("autobrr_event_")]
    except Exception as e:
        logger.warning(f"Failed to list replay files: {e}")
        files = []

    return templates.TemplateResponse("replay.html", {"request": request, "files": files})


# ------------------------------------------------------------
#   Replay Trigger
# ------------------------------------------------------------


@app.post("/replay/trigger")
def replay_trigger(request: Request, event_file: str = Form(...)):
    start = time.time()
    logger.info(f"Replay triggered for {event_file}")

    json_path = os.path.join("json", event_file)
    if not os.path.exists(json_path):
        logger.error(f"Replay file not found: {json_path}")
        return templates.TemplateResponse("replay.html", {
            "request": request,
            "files": [],
            "error": f"File not found: {event_file}"
        })

    try:
        result = subprocess.run([
            "python3", "squat_flix_importer.py",
            "--json", json_path,
            "--loglevel", "INFO"
        ], capture_output=True, text=True, timeout=30)

        output = result.stdout.strip() + "\n" + result.stderr.strip()
        status = "success" if result.returncode == 0 else "error"
        logger.info(f"Replay completed with status: {status}")

    except Exception as e:
        output = f"Exception during replay: {e}"
        status = "error"
        logger.exception("Replay failed")

    elapsed = time.time() - start
    return templates.TemplateResponse("replay.html", {
        "request": request,
        "files": os.listdir("json"),
        "output": output,
        "status": status,
        "elapsed": f"{elapsed:.2f}s"
    })
