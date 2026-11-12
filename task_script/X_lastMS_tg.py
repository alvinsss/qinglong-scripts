#!/usr/bin/env python3
"""Fetch the latest 2 original posts for 6 X accounts and send new ones to Telegram.

Dynamic version: each run fetches the latest posts via the free
twexapi.io Twitter Viewer API (no login, no API key), then sends only
posts that have not been sent before (tracked in x_sent_ids.json).

Timeline source:
  GET https://twexapi.io/api/tools/twitter-viewer?username={handle}
  returns JSON {"tweets": [{"id","text","createdAt","url",...}, ...]} (latest 10).

Usage:
  export TG_BOT_TOKEN='...'   # never hard-code the token in this file
  export TG_CHAT_ID='-100...' # e.g. -1003761406027
  python3 X_lastMS_tg.py

Notes:
  - Reposts (text starting with "RT @") are skipped; latest 2 originals per account.
  - Long posts are sent as an excerpt (~120 chars) + original link.
    Short posts are sent in full.
  - Already-sent tweet IDs are recorded in x_sent_ids.json next to this
    script; a run sends nothing for an account with no new posts.
"""

import json
import os
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

TG_BOT_TOKEN = os.environ["TG_BOT_TOKEN"]
TG_CHAT_ID = os.environ["TG_CHAT_ID"]

ACCOUNTS = ["DtDt666", "UltraGavin", "PhyrexNi", "KillaXBT", "Jackyi_ld", "youtubercrypto_"]

VIEWER_URL = "https://twexapi.io/api/tools/twitter-viewer?username={handle}"
EXCERPT_LEN = 120
BEIJING = timezone(timedelta(hours=8))
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "x_sent_ids.json")
# Rate limit: the free viewer API returns 429 when accounts are fetched
# back-to-back. Request one account every 5 minutes.
REQUEST_INTERVAL = 300
FETCH_RETRIES = 3
RETRY_WAIT = 60


def fetch_latest(handle):
    """Latest tweets for one account via the free viewer API. Returns list of dicts."""
    url = VIEWER_URL.format(handle=handle)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    last_err = None
    for attempt in range(FETCH_RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read())
            return data.get("tweets", []) or []
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code == 429 and attempt < FETCH_RETRIES - 1:
                wait = RETRY_WAIT * (attempt + 1)
                print(handle, "429, retry in", wait, "s")
                time.sleep(wait)
                continue
            raise
        except Exception as e:
            last_err = e
            if attempt < FETCH_RETRIES - 1:
                time.sleep(RETRY_WAIT)
                continue
            raise
    raise last_err


def is_repost(text):
    t = (text or "").lstrip()
    return t.startswith("RT @") or t.startswith("RT@")


def beijing_date(created_at):
    """'Wed Nov 11 03:01:46 +0000 2026' (UTC) -> '11月11日' (Beijing)."""
    try:
        dt = datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")
    except Exception:
        return ""
    bj = dt.astimezone(BEIJING)
    return f"{bj.month}月{bj.day}日"


def excerpt(text):
    text = " ".join((text or "").split())
    if len(text) <= EXCERPT_LEN:
        return text
    return text[:EXCERPT_LEN] + "……全文见链接"


def send_with_retry(text, attempts=2):
    payload = json.dumps(
        {"chat_id": TG_CHAT_ID, "text": text, "disable_web_page_preview": False}
    ).encode()
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    last_err = None
    for _ in range(attempts):
        req = urllib.request.Request(
            url, data=payload, headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read())["result"]["message_id"]
        except Exception as e:  # TimeoutError etc. - server may still have sent it
            last_err = e
            time.sleep(2)
    raise last_err


def load_sent():
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return set(str(x) for x in data)
        return set()
    except Exception:
        return set()


def save_sent(sent):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(sent), f, ensure_ascii=False, indent=2)


def main():
    sent = load_sent()
    new_sent = set(sent)
    for idx, handle in enumerate(ACCOUNTS):
        try:
            tweets = fetch_latest(handle)
        except Exception as e:
            print(handle, "fetch failed:", e)
            if idx < len(ACCOUNTS) - 1:
                print("waiting", REQUEST_INTERVAL, "s before next account")
                time.sleep(REQUEST_INTERVAL)
            continue
        originals = []
        for t in tweets:
            text = t.get("text") or ""
            if is_repost(text):
                continue
            originals.append(t)
            if len(originals) >= 2:
                break
        fresh = [t for t in originals if str(t.get("id")) not in sent]
        if not fresh:
            print(handle, "no new posts")
        else:
            lines = [f"@{handle} 最新{len(fresh)}条", ""]
            for t in fresh:
                date = beijing_date(t.get("createdAt") or "")
                lines.append(date)
                lines.append(excerpt(t.get("text") or ""))
                lines.append(f"https://x.com/{handle}/status/{t.get('id')}")
                lines.append("")
            message_id = send_with_retry("\n".join(lines).strip())
            print(handle, "ok", message_id)
            for t in fresh:
                new_sent.add(str(t.get("id")))
        if idx < len(ACCOUNTS) - 1:
            print("waiting", REQUEST_INTERVAL, "s before next account")
            time.sleep(REQUEST_INTERVAL)
    if new_sent != sent:
        save_sent(new_sent)


if __name__ == "__main__":
    main()
