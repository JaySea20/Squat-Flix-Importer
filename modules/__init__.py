# modules/__init__.py

__version__ = "v0.6.5-beta"

from .db import init as init_db, store_json, fetch_recent
from .json import load_json, dump_json
from .Jaylog import mklog
