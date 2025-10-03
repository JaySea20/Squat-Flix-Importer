#!/usr/bin/env python3
# ============================================================
#   Squat-Flix Webhook Listener for Autobrr
# ============================================================

__version__ = "v0.6.5-beta"

#from pathlib import Path
#from fastapi import FastAPI, Request, Form
#from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse, StreamingResponse
#from fastapi.staticfiles import StaticFiles
#from fastapi.templating import Jinja2Templates
import fastapi
from pydantic import BaseModel
from typing import List, Optional
import modules.Jaylog
import modules.autobrr
import sys
import subprocess
import logging
import time
import os
import json
import httpx
import asyncio

sys.dont_write_bytecode = True

app = FastAPI()

# ===========================================================================================
#  PATH HELPERS
# ===========================================================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

TEMPLATES_DIR = os.path.join(SCRIPT_DIR, "templates")
STATIC_DIR = os.path.join(SCRIPT_DIR, "static")
LOG_DIR = os.path.join(SCRIPT_DIR, "logs")
JSON_DIR = os.path.join(PROJECT_ROOT, "json")

CONFIG_PATH = os.getenv("SQUATFLIX_CONFIG", os.path.join(JSON_DIR, "config.json"))
LOG_PATH = os.getenv("SQUATFLIX_LOG", os.path.join(LOG_DIR, "squatflix.log"))

templates = Jinja2Templates(directory=TEMPLATES_DIR)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# --------------------------------------------------------------- PATH HELPERS
# ===========================================================================================


# ------------------------------------------------------------
#   Lifecycle Logging
# ------------------------------------------------------------

ApiLogger = setup_logger(level="DEBUG", log_path=LOG_PATH)


log_queue = asyncio.Queue()

class QueueHandler(logging.Handler):
    def emit(self, record):
        asyncio.create_task(log_queue.put(self.format(record)))

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

queue_handler = QueueHandler()
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
queue_handler.setFormatter(formatter)
root_logger.addHandler(queue_handler)

# Attach to uvicorn loggers as well
uvicorn_access = logging.getLogger("uvicorn.access")
uvicorn_error = logging.getLogger("uvicorn.error")

uvicorn_access.addHandler(queue_handler)
uvicorn_error.addHandler(queue_handler)

# ------------------------------------------------------------
#   FastAPI Setup
# ------------------------------------------------------------



# ------------------------------------------------------------
#   Autobrr Webhook Listener
# ------------------------------------------------------------

class AutoBRRPayload(BaseModel):
    Artists: Optional[str] = None
    Audio: Optional[List[str]] = None
    AudioChannels: Optional[str] = None
    AudioFormat: Optional[str] = None
    Bitrate: Optional[str] = None
    Bonus: Optional[List[str]] = None
    Categories: Optional[List[str]] = None
    Category: Optional[str] = None
    Codec: Optional[List[str]] = None
    Container: Optional[str] = None
    CurrentDay: Optional[int] = None
    CurrentHour: Optional[int] = None
    CurrentMinute: Optional[int] = None
    CurrentMonth: Optional[int] = None
    CurrentSecond: Optional[int] = None
    CurrentYear: Optional[int] = None
    Day: Optional[int] = None
    Description: Optional[str] = None
    DownloadURL: Optional[str] = None
    Episode: Optional[int] = None
    FilterID: Optional[int] = None
    FilterName: Optional[str] = None
    Freeleech: Optional[bool] = None
    FreeleechPercent: Optional[int] = None
    Group: Optional[str] = None
    GroupID: Optional[str] = None
    HasCue: Optional[bool] = None
    HasLog: Optional[bool] = None
    HDR: Optional[str] = None
    Implementation: Optional[str] = None
    Indexer: Optional[str] = None
    IndexerIdentifier: Optional[str] = None
    IndexerIdentifierExternal: Optional[str] = None
    IndexerName: Optional[str] = None
    InfoUrl: Optional[str] = None
    IsDuplicate: Optional[bool] = None
    Language: Optional[List[str]] = None
    Leechers: Optional[int] = None
    LogScore: Optional[int] = None
    MagnetURI: Optional[str] = None
    MetaIMDB: Optional[str] = None
    Month: Optional[int] = None
    Origin: Optional[str] = None
    Other: Optional[List[str]] = None
    PreTime: Optional[str] = None
    Proper: Optional[bool] = None
    Protocol: Optional[str] = None
    RecordLabel: Optional[str] = None
    Region: Optional[str] = None
    Repack: Optional[bool] = None
    Resolution: Optional[str] = None
    Season: Optional[int] = None
    Seeders: Optional[int] = None
    Size: Optional[int] = None
    SizeString: Optional[str] = None
    SkipDuplicateProfileID: Optional[int] = None
    SkipDuplicateProfileName: Optional[str] = None
    Source: Optional[str] = None
    Tags: Optional[str] = None
    Title: Optional[str] = None
    TorrentDataRawBytes: Optional[str] = None
    TorrentHash: Optional[str] = None
    TorrentID: Optional[str] = None
    TorrentName: Optional[str] = None
    TorrentPathName: Optional[str] = None
    TorrentTmpFile: Optional[str] = None
    TorrentUrl: Optional[str] = None
    Type: Optional[str] = None
    Uploader: Optional[str] = None
    Website: Optional[str] = None
    Year: Optional[int] = None


@app.post("/webhook/autobrr")
async def autobrr_webhook(payload: AutoBRRPayload):
    result = acceptPayload(payload)
    logger.info(f"DATA has arrived VIA Autobrr API")
    logger.info(f"It has been handed off to autobrr.py")
    return {
        "status": result.get("status", "error"),
        "title": payload.Title,
        "year": payload.Year
    }

# ------------------------------------------------------------
#   WebSocket Log Streaming
# ------------------------------------------------------------


#from fastapi import WebSocket
#from modules.logging import log_queue

@app.websocket("/ws/logs")
async def stream_logs(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            line = await log_queue.get()
            await websocket.send_text(line)
    except Exception:
        await websocket.close()


# ------------------------------------------------------------
#   Web Log Console
# ------------------------------------------------------------

@app.get("/logs/stream")
async def stream_logs():
    async def event_generator():
        while True:
            line = await log_queue.get()
            yield f"data: {line}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")

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
        for fname in sorted(os.listdir(JSON_DIR), reverse=True):
            if fname.startswith("autobrr_event_") and fname.endswith(".json"):
                with open(os.path.join(JSON_DIR, fname)) as f:
                    data = json.load(f)
                    event_list.append({
                        "filename": fname,
                        "title": data.get("releaseName", "Unknown"),
                        "indexer": data.get("indexer", "Unknown"),
                        "timestamp": fname.replace("autobrr_event_", "").replace(".json", "")
                    })
    except Exception as e:
        ApiLogger.warning(f"Failed to load events: {e}")

    return templates.TemplateResponse("events.html", {"request": request, "events": event_list})

# ------------------------------------------------------------
#   Config
# ------------------------------------------------------------


@app.get("/config", response_class=HTMLResponse)
def config_view(request: Request):
    try:
        with open(CONFIG_PATH) as f:
            config_data = json.load(f)
    except Exception as e:
        ApiLogger.warning(f"Failed to load config: {e}")
        config_data = {}

    return templates.TemplateResponse("config.html", {"request": request, "config": config_data})

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
            if method.upper() == "POST":
                response = await client.post(url, headers=headers, json=payload)
            else:
                response = await client.get(url, headers=headers, params=payload)

            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            return {"error": str(e), "status_code": getattr(e.response, "status_code", None)}
