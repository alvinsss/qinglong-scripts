#!/usr/bin/env python3
"""Verify /api/fleet muse_usage twice, 30s apart (grep -c semantics)."""
import subprocess
import time
import urllib.parse
import urllib.request

tok = open("/usr/home/platform/panel/token.txt", encoding="utf-8").read().strip()
for i in (1, 2):
    url = "https://platform.serv00.net/api/fleet?token=" + urllib.parse.quote(tok)
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            status = r.status
            body = r.read()
        p = "/tmp/fleet_check2_%d.json" % i
        open(p, "wb").write(body)
        out = subprocess.run(["grep", "-c", "muse_usage", p], capture_output=True, text=True)
        print("FLEET%d_HTTP:%d MUSE%d:%s" % (i, status, i, out.stdout.strip()))
    except Exception as e:
        print("FLEET%d_ERR:%s" % (i, e))
    if i == 1:
        time.sleep(30)
