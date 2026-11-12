#!/usr/bin/env python3
"""Add remaining column to renderMuse usage table in panel_fleet.py."""
import shutil
import sys
import py_compile
P = "/usr/home/platform/panel/panel_fleet.py"
BAK = P + ".bak-remain-20261111"
shutil.copy(P, BAK)
src = open(P, encoding="utf-8").read()
orig_len = len(src)
a1 = "h+='<table><tr><th>账号</th><th>用量</th><th>重置时间</th></tr>';"
assert src.count(a1) == 1, "anchor1 count=%d" % src.count(a1)
src = src.replace(a1, "h+='<table><tr><th>账号</th><th>用量</th><th>剩余额度</th><th>重置时间</th></tr>';", 1)
a2 = "u.rows.forEach(function(r){h+='<tr><td>'+esc(r.label||'')+'</td><td>'+esc(r.usage_percent_text||'')+'</td><td>'+esc(r.reset_text||'')+'</td></tr>'});"
assert src.count(a2) == 1, "anchor2 count=%d" % src.count(a2)
src = src.replace(a2, "u.rows.forEach(function(r){h+='<tr><td>'+esc(r.label||'')+'</td><td>'+esc(r.usage_percent_text||'')+'</td><td>'+esc(r.remaining_percent_text||'')+'</td><td>'+esc(r.reset_text||'')+'</td></tr>'});", 1)
open(P, "w", encoding="utf-8").write(src)
try:
    py_compile.compile(P, doraise=True)
except Exception as e:
    shutil.copy(BAK, P)
    print("PATCH-FAIL compile error, restored backup: %s" % e)
    sys.exit(1)
print("PATCH-OK orig_len=%d new_len=%d backup=%s" % (orig_len, len(src), BAK))
