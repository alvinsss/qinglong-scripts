#!/usr/bin/env python3
"""Verify /api/fleet: HTTP status, grep -c counts of muse_usage and remaining_percent_text."""
import subprocess
import urllib.parse
import urllib.request
tok = open("/usr/home/platform/panel/token.txt", encoding="utf-8").read().strip()
url = "https://platform.serv00.net/api/fleet?token=" + urllib.parse.quote(tok)
try:
    with urllib.request.urlopen(url, timeout=30) as r:
        status = r.status
        body = r.read()
    p = "/tmp/fleet_remain.json"
    open(p, "wb").write(body)
    m = subprocess.run(["grep", "-c", "muse_usage", p], capture_output=True, text=True)
    rem = subprocess.run(["grep", "-c", "remaining_percent_text", p], capture_output=True, text=True)
    print("FLEET_HTTP:%d MUSE_USAGE:%s REMAINING:%s" % (status, m.stdout.strip(), rem.stdout.strip()))
    print("OCC_MUSE:%d OCC_REMAIN:%d" % (body.count(b"muse_usage"), body.count(b"remaining_percent_text")))
except Exception as e:
    print("FLEET_ERR:%s" % e)
