#!/usr/bin/env python3
"""Seed x_sent_ids.json with current latest 2 originals per account."""
import json, os, urllib.request
ACCOUNTS = ["DtDt666", "UltraGavin", "PhyrexNi", "KillaXBT", "Jackyi_ld", "youtubercrypto_"]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "x_sent_ids.json")
def is_repost(text):
    t = (text or "").lstrip()
    return t.startswith("RT @") or t.startswith("RT@")
ids = set()
for handle in ACCOUNTS:
    try:
        url = f"https://twexapi.io/api/tools/twitter-viewer?username={handle}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read())
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
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(sorted(ids), f, ensure_ascii=False, indent=2)
print("SEED-OK total=" + str(len(ids)))
