#!/usr/bin/env python3

# =========================================================================================================
# =========================================================================================================
#
#    Squat-Flix-Importer Test Harness
#
# ---------------------------------------------------------------------------------------------------------
#    Validates CLI flags, config loading, and logging behavior for squat-flix-importer.py
#    - Tests default run, interactive mode, custom config, missing config, and log levels
#    - Uses absolute path resolution and dummy config injection
#    - Lifecycle-logged and failure-aware
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
from datetime import datetime

# ------------------------------------------------------------
#              PATH RESOLUTION
# ------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMPORTER_PATH = os.path.join(SCRIPT_DIR, "..", "squat-flix-importer.py")
CONFIG_PATH = os.path.join(SCRIPT_DIR, "test-config.json")

# ------------------------------------------------------------
#              LOGGER SETUP
# ------------------------------------------------------------

logging.basicConfig(
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    level=logging.DEBUG
)
logger = logging.getLogger("TestHarness")

# ------------------------------------------------------------
#              CONFIG PREP
# ------------------------------------------------------------

def ensure_test_config():
    if not os.path.exists(CONFIG_PATH):
        logger.info("Creating dummy config for test runs")
        dummy = {
            "autobrr": {"host": "localhost", "apikey": "abc123"},
            "radarr": {"host": "localhost", "apikey": "xyz789"},
            "qbittorrent": {"host": "localhost", "username": "user", "password": "pass"},
            "filters": {"min_seeders": 5, "quality": "1080p"}
        }
        with open(CONFIG_PATH, "w") as f:
            json.dump(dummy, f, indent=2)

# ------------------------------------------------------------
#              TEST RUNNER
# ------------------------------------------------------------

def run_test(description, args, expect_failure=False):
    print(f"\n=== {description} ===")
    logger.debug(f"Running test: {description}")
    result = subprocess.run(["python3", IMPORTER_PATH] + args, capture_output=True, text=True)

    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip())

    if expect_failure and result.returncode == 0:
        logger.warning(f"Expected failure but test passed: {description}")
    elif not expect_failure and result.returncode != 0:
        logger.error(f"Unexpected failure: {description}")

# ------------------------------------------------------------
#              TEST CASES
# ------------------------------------------------------------

ensure_test_config()

tests = [
    ("Default run", []),
    ("Interactive mode", ["--interactive"]),
    ("Custom config path", ["--config", CONFIG_PATH]),
    ("Missing config file", ["--config", "missing.json"], True),
    ("Log level DEBUG", ["--loglevel", "DEBUG"]),
    ("Log level ERROR", ["--loglevel", "ERROR"]),
    ("All flags combined", ["--interactive", "--config", CONFIG_PATH, "--loglevel", "DEBUG"]),
]

for desc, args, *flags in tests:
    expect_failure = flags[0] if flags else False
    run_test(desc, args, expect_failure)

# ------------------------------------------------------------
#              CLI FLAG TEST SUITE
# ============================================================
