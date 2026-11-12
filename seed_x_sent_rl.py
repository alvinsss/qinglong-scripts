#!/usr/bin/env python3
"""Seed x_sent_ids.json with current latest 2 originals per account.

Rate-limited version: one account every 5 minutes (REQUEST_INTERVAL=300)
to avoid the free viewer API 429. Existing IDs are kept (union), so a
failed fetch never erases previously seeded IDs.
"""
import json, os, time, urllib.request
ACCOUNTS = ["DtDt666", "UltraGavin", "PhyrexNi", "KillaXBT", "Jackyi_ld", "youtubercrypto_"]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "x_sent_ids.json")
REQUEST_INTERVAL = 300
def is_repost(text):
    t = (text or "").lstrip()
    return t.startswith("RT @") or t.startswith("RT@")
def load_existing():
    try:
        with open(OUT, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return set(str(x) for x in data)
    except Exception:
        pass
    return set()
def fetch(handle):
    url = f"https://twexapi.io/api/tools/twitter-viewer?username={handle}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())
ids = load_existing()
print("existing total=" + str(len(ids)))
for idx, handle in enumerate(ACCOUNTS):
    try:
        data = fetch(handle)
        n = 0
        for t in data.get("tweets", []) or []:
            if is_repost(t.get("text") or ""):
                continue
            ids.add(str(t.get("id")))
            n += 1
            if n >= 2:
                break
        print(handle, "seeded", n)
    except Exception as e:
        print(handle, "seed failed:", str(e)[:80])
    if idx < len(ACCOUNTS) - 1:
        print("waiting", REQUEST_INTERVAL, "s before next account")
        time.sleep(REQUEST_INTERVAL)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(sorted(ids), f, ensure_ascii=False, indent=2)
print("SEED-OK total=" + str(len(ids)))
