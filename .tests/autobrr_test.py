#!/usr/bin/env python3
# =========================================================================================================
# =========================================================================================================
#
#    Squat-Flix-Importer Autobrr Behavior Tests
#
# ---------------------------------------------------------------------------------------------------------
#    Validates process_autobrr() under multiple config scenarios and log levels
#    - Configs: valid, missing section, missing keys
#    - Log levels: DEBUG, INFO, WARNING, ERROR
#    - Pass/fail logic based on return code and expected behavior
#
#    Author: Joshua (JaySea20)
#    Created: 2025-10-02
#    License: MIT
#
# ---------------------------------------------------------------------------------------------------------
# =========================================================================================================

import subprocess
import os
import json
import logging
import sys
sys.path.insert(0, os.path.join(SCRIPT_DIR, ".."))
from squat-flix-importer import VERSION

# ------------------------------------------------------------
#              PATH RESOLUTION
# ------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMPORTER_PATH = os.path.join(SCRIPT_DIR, "..", "squat-flix-importer.py")
CONFIG_DIR = os.path.join(SCRIPT_DIR, "configs")
os.makedirs(CONFIG_DIR, exist_ok=True)

# ------------------------------------------------------------
#              LOGGER SETUP
# ------------------------------------------------------------

logging.basicConfig(
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    level=logging.DEBUG
)
logger = logging.getLogger("TestHarness")

# ------------------------------------------------------------
#              CONFIG CASES
# ------------------------------------------------------------

CONFIGS = {
    "valid": {
        "autobrr": {"host": "localhost", "apikey": "abc123"},
        "radarr": {"host": "localhost", "apikey": "xyz789"},
        "qbittorrent": {"host": "localhost", "username": "user", "password": "pass"},
        "filters": {"min_seeders": 5, "quality": "1080p"}
    },
    "missing_autobrr": {
        "radarr": {"host": "localhost", "apikey": "xyz789"},
        "qbittorrent": {"host": "localhost", "username": "user", "password": "pass"},
        "filters": {"min_seeders": 5, "quality": "1080p"}
    },
    "missing_apikey": {
        "autobrr": {"host": "localhost"},
        "radarr": {"host": "localhost", "apikey": "xyz789"},
        "qbittorrent": {"host": "localhost", "username": "user", "password": "pass"},
        "filters": {"min_seeders": 5, "quality": "1080p"}
    }
}

LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR"]

# ------------------------------------------------------------
#              TEST RUNNER
# ------------------------------------------------------------

def write_config(name, data):
    path = os.path.join(CONFIG_DIR, f"{name}.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return path

def run_case(config_name, loglevel, expect_failure=False):
    config_path = write_config(config_name, CONFIGS[config_name])
    label = f"{config_name.upper()} @ {loglevel}"
    print(f"\n=== {label} ===")
    logger.debug(f"Running test: {label}")

    result = subprocess.run([
        "python3", IMPORTER_PATH,
        "--config", config_path,
        "--loglevel", loglevel
    ], capture_output=True, text=True)

    stdout = result.stdout.strip()
    stderr = result.stderr.strip()

    if stdout:
        print(stdout)
    if stderr:
        print(stderr)

    passed = (result.returncode == 0)
    if expect_failure and passed:
        print(f"[FAIL] Expected failure but passed: {label}")
    elif not expect_failure and not passed:
        print(f"[FAIL] Unexpected failure: {label}")
    else:
        print(f"[PASS] {label}")

# ------------------------------------------------------------
#              MAIN EXECUTION
# ------------------------------------------------------------

def main():
    for config_name in CONFIGS:
        for level in LOG_LEVELS:
            expect_fail = config_name != "valid"
            run_case(config_name, level, expect_failure=expect_fail)

if __name__ == "__main__":
    main()

# ------------------------------------------------------------
#              Autobrr Behavior Tests
# ============================================================
