#!/usr/bin/env python3
"""Patch passenger_wsgi.py /api/fleet to merge muse_usage.json."""
import shutil
import sys
import py_compile
P = "/usr/home/platform/domains/platform.serv00.net/passenger_wsgi.py"
BAK = P + ".bak-muse-usage-20261111"
shutil.copy(P, BAK)
src = open(P, encoding="utf-8").read()
orig_len = len(src)
anchor = '        if role == "viewer":\n            try:\n                raw = json.dumps(pf.redact_fleet(json.loads(raw.decode("utf-8"))),'
assert src.count(anchor) == 1, "anchor count=%d" % src.count(anchor)
merge = (
    '        # Muse 用量：合并本地 muse_usage.json（青龙每 15 分钟从 muse-usage_all.json 生成，账号1 已脱敏为 *）\n'
    '        try:\n'
    '            with open(os.path.join(PANEL_DIR, "muse_usage.json"), "rb") as _uf:\n'
    '                _mu = json.loads(_uf.read().decode("utf-8"))\n'
    '            _d = json.loads(raw.decode("utf-8"))\n'
    '            _d["muse_usage"] = _mu\n'
    '            raw = json.dumps(_d, ensure_ascii=False).encode("utf-8")\n'
    '        except Exception:\n'
    '            pass\n'
)
src = src.replace(anchor, merge + anchor, 1)
open(P, "w", encoding="utf-8").write(src)
try:
    py_compile.compile(P, doraise=True)
except Exception as e:
    shutil.copy(BAK, P)
    print("PATCH-FAIL compile error, restored backup: %s" % e)
    sys.exit(1)
print("PATCH-OK orig_len=%d new_len=%d backup=%s" % (orig_len, len(src), BAK))
