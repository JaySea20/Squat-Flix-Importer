# 🎬 Squat-Flix Importer

Minimalist webhook listener and importer for *Arr ecosystem tools. Built for Autobrr, wired for Radarr, and scaffolded for auditability.

## 🚀 Features

- FastAPI server with modular endpoints
- Webhook listener for Autobrr POST payloads
- Replay interface for saved events
- Config viewer with live rendering
- Lifecycle logging on all major routes
- Dry-run support for safe testing

## 📦 Routes

| Endpoint              | Method | Description                          |
|-----------------------|--------|--------------------------------------|
| `/`                   | GET    | Dashboard landing page               |
| `/events`            | GET    | View archived Autobrr payloads       |
| `/config`            | GET    | Render current config from JSON      |
| `/replay`            | GET/POST | Replay saved event via form        |
| `/webhook/autobrr`   | POST   | Accept Autobrr payloads              |

## 🧰 Requirements

- Python 3.10+
- `uvicorn`, `fastapi`, `jinja2`, `python-multipart`

Install with:

```bash
pip install "uvicorn[standard]" fastapi jinja2 python-multipart
