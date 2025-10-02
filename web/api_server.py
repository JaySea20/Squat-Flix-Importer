#!/usr/bin/env python3
# ============================================================
#   Squat-Flix Webhook Listener for Autobrr
# ============================================================

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging
import time
import os
import json


# ------------------------------------------------------------
#   Lifecycle Logging
# ------------------------------------------------------------

logging.basicConfig(
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("SquatFlixListener")

# ------------------------------------------------------------
#   FastAPI Setup
# ------------------------------------------------------------

app = FastAPI()
templates = Jinja2Templates(directory="web/templates")
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# ------------------------------------------------------------
#   Autobrr Webhook Listener
# ------------------------------------------------------------

#@app.post("/webhook/autobrr")
#async def autobrr_webhook(payload: dict):
#    start = time.time()
#    logger.info("Webhook received from Autobrr")
#
#    # Dry-run: log payload only
#    logger.debug(f"Payload: {payload}")
#
#    # TODO: Validate + push to Radarr here
#    elapsed = time.time() - start
#    logger.info(f"Webhook processed (elapsed: {elapsed:.3f}s)")
#    return JSONResponse(content={"status": "ok", "elapsed": elapsed})

# ------------------------------------------------------------
#   Minimal Dashboard
# ------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})






@app.get("/events", response_class=HTMLResponse)
def events(request: Request):
    event_list = []
    try:
        for fname in sorted(os.listdir("json"), reverse=True):
            if fname.startswith("autobrr_event_") and fname.endswith(".json"):
                with open(os.path.join("json", fname)) as f:
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






@app.get("/config", response_class=HTMLResponse)
def config_view(request: Request):
    try:
        with open("json/config.json") as f:
            config_data = json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load config: {e}")
        config_data = {}

    return templates.TemplateResponse("config.html", {"request": request, "config": config_data})






@app.get("/replay", response_class=HTMLResponse)
def replay_view(request: Request):
    try:
        files = [f for f in os.listdir("json") if f.startswith("autobrr_event_")]
    except Exception as e:
        logger.warning(f"Failed to list replay files: {e}")
        files = []

    return templates.TemplateResponse("replay.html", {"request": request, "files": files})




from fastapi import Form
from fastapi.responses import RedirectResponse

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
