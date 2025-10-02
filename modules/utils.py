#!/usr/bin/env python3

# ======================================================================================== #
# ======================================================================================== #
#                                                                                          #
#                                     Squat-Flix-Importer                                  #
#                                                                                          #
# ======================================================================================== #
# ======================================================================================== #


# CLI-first Python tool to automate movie ingestion between
# Autobrr, qBittorrent, and Radarr.

# Author: Joshua (JaySea20)
# Repo: https://github.com/JaySea20/squat-flix-importer
# Created: 2025-10-02
# License: MIT

# Description:
#   - Supports interactive and autonomous modes
#   - Modular, minimal, and expandable
#   - Logs to both console and file
#   - Configurable via JSON


# ========================================================================================= #
#                                                                                           #
#                           "Fixin the Flix that transfix, Dude!"                           #
#                                           Whoa!                                           #
#                                                                                           #
# ========================================================================================= #

VERSION = "0.5.0-beta"

# ===========================================================================================
#   IMPORTS
# ===========================================================================================

import sys, argparse, json, os, time
from web.logger import setup_logger


sys.dont_write_bytecode = True

# ---------------------------------------------------------------------------------- IMPORTS
# ===========================================================================================



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



# ===========================================================================================
#   CLI ARGUMENT PARSER
# ===========================================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description="Squat-Flix-Importer: Autobrr → Radarr bridge tool"
    )

    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Enable interactive mode with prompts and decisions"
    )

    parser.add_argument(
        "--config",
        type=str,
        default=CONFIG_PATH,
        help="Path to config file (default: $SQUATFLIX_CONFIG or script-relative)"
    )

    parser.add_argument(
        "--loglevel",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging verbosity level"
    )

    parser.add_argument(
        "--logpath",
        type=str,
        default=None,
        help="Path can be relative or absolute. Example /home/me/logs or ./../../logs"
    )

    return parser.parse_args()

# -------------------------------------------------------- CLI ARGUMENT PARSER
# ===========================================================================================


# ===========================================================================================
#    LOGGER SETUP
# ===========================================================================================






# ===========================================================================================
#    CONFIG LOADER
# ===========================================================================================

def load_config(path="config.json", logger=None):
    if not os.path.exists(path):
        if logger:
            logger.error(f"Config file not found: {path}")
        raise FileNotFoundError(f"Config file not found: {path}")

    try:
        with open(path, "r") as f:
            config = json.load(f)
        if logger:
            logger.info(f"Loaded config from {path}")
        return config
    except json.JSONDecodeError as e:
        if logger:
            logger.error(f"Invalid JSON in config file: {e}")
        raise


# --------------------------------------------- CONFIG LOADER
# ===========================================================================================




# ===========================================================================================
#     CONFIG VALIDATOR
# ===========================================================================================

def validate_config(config, logger=None):
    required = {
        "autobrr": ["host", "apikey"],
        "radarr": ["host", "apikey"],
        "qbittorrent": ["host", "username", "password"],
        "filters": ["min_seeders", "quality"]
    }

    for section, keys in required.items():
        if section not in config:
            msg = f"Missing section: {section}"
            if logger: logger.error(msg)
            raise ValueError(msg)

        for key in keys:
            if key not in config[section]:
                msg = f"Missing key in '{section}': {key}"
                if logger: logger.error(msg)
                raise ValueError(msg)

    if logger:
        logger.info("Config structure validated successfully")


# ------------------------------------------ CONFIG VALIDATOR
# ===========================================================================================




# ===========================================================================================
#     TASK LIFECYCLE WRAPPER
# ===========================================================================================


def run_task(label, func, *args, logger=None, **kwargs):
    if logger:
        logger.debug(f"Starting: {label}")
    start = time.time()
    result = func(*args, **kwargs)
    elapsed = time.time() - start
    if logger:
        logger.debug(f"Finished: {label} (elapsed: {elapsed:.3f}s)")
    return result


# ------------------------------------------------------------------- TASK LIFECYCLE WRAPPER
# ===========================================================================================



# =========================================================================================================
# =========================================================================================================
#
#    AUTOBRR INTAKE STUB
#
# ---------------------------------------------------------------------------------------------------------
#    Simulates intake from Autobrr with lifecycle logging
#    - Validates config presence
#    - Logs at multiple levels based on verbosity
#
# ---------------------------------------------------------------------------------------------------------
# =========================================================================================================

def process_autobrr(config, logger):

    autobrr = config.get("autobrr")
    if not autobrr:
        if logger: logger.error("Missing 'autobrr' section in config")
        raise ValueError("Missing 'autobrr' section in config")

    host = autobrr.get("host")
    apikey = autobrr.get("apikey")

    if not host or not apikey:
        if logger: logger.error("Missing required Autobrr keys: host or apikey")
        raise ValueError("Missing required Autobrr keys: host or apikey")

    if logger:
        logger.info(f"Autobrr host: {host}")
        logger.debug(f"Autobrr API key: {apikey}")
        logger.warning("Autobrr intake stub completed (no real action taken)")

# ------------------------------------------------------------------------------------------- Autobrr Stub
# =========================================================================================================


# =========================================================================================================
#   RADARR INTAKE
# =========================================================================================================

def process_radarr(config, logger):
    radarr = config.get("radarr")
    if not radarr:
        if logger: logger.error("Missing 'radarr' section in config")
        raise ValueError("Missing 'radarr' section in config")

    host = radarr.get("host")
    apikey = radarr.get("apikey")

    if not host or not apikey:
        if logger: logger.error("Missing required Radarr keys: host or apikey")
        raise ValueError("Missing required Radarr keys: host or apikey")

    if logger:
        logger.info(f"Radarr host: {host}")
        logger.debug(f"Radarr API key: {apikey}")
        logger.warning("Radarr intake stub completed (no real action taken)")

# ------------------------------------------------------------------------------------------- Radarr Intake
# =========================================================================================================

# =========================================================================================================
# =========================================================================================================
#
#    MAIN Logic
#
# ---------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------

def main():
    args = parse_args()
    logger = setup_logger(level="DEBUG",log_path=LOG_PATH)

    logger.info(f"Squat-Flix-Importer started (v{VERSION})")
    logger.info(f"Mode selected: {'Interactive' if args.interactive else 'Autonomous'}")

    try:
        config = run_task("Load config", load_config, args.config, logger=logger)
        run_task("Validate config", validate_config, config, logger=logger)
        run_task("Autobrr intake", lambda: process_autobrr(config, logger), logger=logger)
        run_task("Radarr intake", lambda: process_radarr(config, logger), logger=logger)

    except Exception as e:
        logger.critical(f"Initialization failed: {e}")
        exit(1)

    logger.debug("Initialization complete. Ready to begin processing.")

# ---------------------------------------------------------------------------------------------- MAIN Logic
# =========================================================================================================

if __name__ == "__main__":
    main()
