#!/usr/bin/env python3
"""Fetch muse-usage_all.json, mask 账号1, write panel muse_usage.json with remaining."""
import json
import ssl
import urllib.request
BASE = "https://usage.platform.serv00.net/muse-usage_all.json"
OUT = "/usr/home/platform/panel/muse_usage.json"
CTX = ssl._create_unverified_context()
def fmt_pct(v):
    if v is None:
        return None
    try:
        return "%.1f%%" % float(v)
    except Exception:
        return None
def main():
    req = urllib.request.Request(BASE, headers={"User-Agent": "QL/1.0"})
    with urllib.request.urlopen(req, timeout=20, context=CTX) as r:
        if r.status != 200:
            print("HTTP", r.status)
            raise SystemExit(10)
        data = json.loads(r.read().decode("utf-8"))
    accounts = data.get("accounts", [])
    rows = []
    masked = False
    for a in accounts:
        label = a.get("label")
        if label == "账号1":
            rows.append({"label": label, "usage_percent": None, "usage_percent_text": "*", "reset_text": "*", "reset_at": "*", "remaining_percent": None, "remaining_percent_text": "*"})
            masked = True
        else:
            rows.append({"label": label, "usage_percent": a.get("weekly_used_pct"), "usage_percent_text": fmt_pct(a.get("weekly_used_pct")), "reset_text": a.get("reset_text"), "reset_at": a.get("reset_at"), "remaining_percent": a.get("weekly_remaining_pct"), "remaining_percent_text": fmt_pct(a.get("weekly_remaining_pct"))})
    if not masked and rows:
        rows[0]["usage_percent"] = None
        rows[0]["usage_percent_text"] = "*"
        rows[0]["reset_text"] = "*"
        rows[0]["reset_at"] = "*"
        rows[0]["remaining_percent"] = None
        rows[0]["remaining_percent_text"] = "*"
    out = {"updated_at": data.get("updated_at"), "updated_hm": data.get("updated_hm"), "source": "muse-usage_all.json", "rows": rows}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("MUSE-USAGE-OK rows=" + str(len(rows)))
if __name__ == "__main__":
    main()
