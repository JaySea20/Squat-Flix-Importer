import json
import os

CONFIG_PATH = os.getenv("CONFIG_PATH", "./config.json")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

# Accessors
AUTOBRR = config.get("autobrr", {})
RADARR = config.get("radarr", {})
QBITTORRENT = config.get("qbittorrent", {})
FILTERS = config.get("filters", {})

# Optional: flatten common keys
AUTOBRR_HOST = AUTOBRR.get("host")
AUTOBRR_APIKEY = AUTOBRR.get("apikey")

RADARR_HOST = RADARR.get("host")
RADARR_APIKEY = RADARR.get("apikey")

QBIT_HOST = QBITTORRENT.get("host")
QBIT_USER = QBITTORRENT.get("username")
QBIT_PASS = QBITTORRENT.get("password")

MIN_SEEDERS = FILTERS.get("min_seeders", 0)
QUALITY = FILTERS.get("quality", [])
