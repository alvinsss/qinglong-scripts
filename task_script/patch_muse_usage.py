#!/usr/bin/env python3
"""Patch panel_fleet.py to add Muse usage."""
import shutil
import sys
import py_compile
P = "/usr/home/platform/panel/panel_fleet.py"
BAK = P + ".bak-muse-usage-20261111"
shutil.copy(P, BAK)
src = open(P, encoding="utf-8").read()
orig_len = len(src)
a1 = 'SERV00_FILE = os.environ.get("PANEL_SERV00_FILE", os.path.join(HERE, "serv00.json"))'
assert src.count(a1) == 1, "anchor1 count=%d" % src.count(a1)
src = src.replace(a1, a1 + '\nMUSE_USAGE_FILE = os.environ.get("PANEL_MUSE_USAGE_FILE", os.path.join(HERE, "muse_usage.json"))', 1)
a2 = '            raw = _merge_serv00(raw)\n'
assert src.count(a2) == 1, "anchor2 count=%d" % src.count(a2)
merge = (
    a2 +
    '            # Muse 用量：合并本地 muse_usage.json（青龙每 15 分钟从 muse-usage_all.json 生成，账号1 已脱敏为 *）\n'
    '            try:\n'
    '                with open(MUSE_USAGE_FILE, "rb") as f:\n'
    '                    _mu = json.loads(f.read().decode("utf-8"))\n'
    '                _d = json.loads(raw.decode("utf-8"))\n'
    '                _d["muse_usage"] = _mu\n'
    '                raw = json.dumps(_d, ensure_ascii=False).encode("utf-8")\n'
    '            except Exception:\n'
    '                pass\n'
)
src = src.replace(a2, merge, 1)
start = src.find("function renderMuse(d){")
assert start != -1, "renderMuse not found"
end_marker = "el.innerHTML=h}"
pos = src.find(end_marker, start)
assert pos != -1, "renderMuse innerHTML not found"
table_end = src.rfind("h+='</table>';", start, pos)
assert table_end != -1, "renderMuse table end not found"
insert_at = table_end + len("h+='</table>';")
usage_js = (
    "\n const u=d&&d.muse_usage;\n"
    " if(u&&u.rows&&u.rows.length){\n"
    "  h+='<div class=\"sub\" style=\"margin:14px 0 6px\">Muse 用量'+(u.updated_at?' · 更新于 '+esc(u.updated_at):'')+'</div>';\n"
    "  h+='<table><tr><th>账号</th><th>用量</th><th>重置时间</th></tr>';\n"
    "  u.rows.forEach(function(r){h+='<tr><td>'+esc(r.label||'')+'</td><td>'+esc(r.usage_percent_text||'')+'</td><td>'+esc(r.reset_text||'')+'</td></tr>'});\n"
    "  h+='</table>';\n"
    " }\n "
)
src = src[:insert_at] + usage_js + src[insert_at:]
open(P, "w", encoding="utf-8").write(src)
try:
    py_compile.compile(P, doraise=True)
except Exception as e:
    shutil.copy(BAK, P)
    print("PATCH-FAIL compile error, restored backup: %s" % e)
    sys.exit(1)
print("PATCH-OK orig_len=%d new_len=%d backup=%s" % (orig_len, len(src), BAK))
