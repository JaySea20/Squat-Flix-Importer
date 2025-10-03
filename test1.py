#!/usr/bin/env python3
# =============================================================================
# File: test_json_utils.py
# Purpose: Brutally test all JSON utilities in json.py
# Author: Joshua
# Created: 2025-10-02
# =============================================================================

import os
import asyncio
from modules import json as jutil

TEST_PATH = "/home/joshua/scripts/squat_flix_importer/.test/test.json"
TEST_STRING = '{"foo": "bar", "baz": [1, 2, 3]}'
TEST_OBJECT = {"foo": "bar", "baz": [1, 2, 3]}

os.makedirs(os.path.dirname(TEST_PATH), exist_ok=True)

# ============================== Test: Dump ==============================

print("🔧 Dumping JSON to file...")
jutil.dump(TEST_OBJECT, TEST_PATH)
assert os.path.isfile(TEST_PATH), "Dump failed: file not created"

# ============================== Test: Exists ==============================

print("🔍 Checking file existence...")
assert jutil.exists(TEST_PATH), "Exists failed: file not found"

# ============================== Test: Load ==============================

print("📥 Loading JSON from file...")
loaded = jutil.load(TEST_PATH)
assert loaded == TEST_OBJECT, "Load failed: data mismatch"

# ============================== Test: Parse ==============================

print("🧠 Parsing JSON string...")
parsed = jutil.parse(TEST_STRING)
assert parsed == TEST_OBJECT, "Parse failed: data mismatch"

# ============================== Test: Stringify ==============================

print("🧾 Stringifying Python object...")
stringified = jutil.stringify(TEST_OBJECT)
assert isinstance(stringified, str), "Stringify failed: not a string"
assert '"foo": "bar"' in stringified, "Stringify failed: content mismatch"

# ============================== Test: Pretty ==============================

print("🖨️ Pretty-printing JSON...")
jutil.pretty(TEST_OBJECT)

# ============================== Test: API Call ==============================

async def test_api_call():
    print("🌐 Testing external API call...")
    result = await jutil.call_external_api("https://httpbin.org/get")
    assert isinstance(result, dict), "API call failed: no dict returned"
    assert "url" in result, "API call failed: missing 'url' key"

asyncio.run(test_api_call())

# ============================== Cleanup ==============================

print("🧹 Cleaning up test file...")
os.remove(TEST_PATH)
assert not os.path.exists(TEST_PATH), "Cleanup failed: file still exists"

print("✅ All JSON utility tests passed.")
