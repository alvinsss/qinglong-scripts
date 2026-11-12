#!/bin/sh
# 每 15 分钟把账号1的 Muse 用量 JSON 从 Google Drive 拉下来，写成 usage 站的 muse-usageAcount1.json。
# Drive 直链放在 /usr/home/platform/usage_pull/drive_url_acount1.txt，文件不存在或为空时静默退出。
set -u
DIR="/usr/home/platform/usage_pull"
URL_FILE="$DIR/drive_url_acount1.txt"
DEST="/usr/home/platform/domains/usage.platform.serv00.net/public_html/muse-usageAcount1.json"
[ -s "$URL_FILE" ] || exit 0
URL=$(cat "$URL_FILE")
TMP=$(mktemp "$DIR/pull1.XXXXXXXX") || exit 1
trap 'rm -f "$TMP"' EXIT
curl -sL --max-time 60 "$URL" -o "$TMP" || exit 1
python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); assert isinstance(d,dict) and "weekly_used_pct" in d' "$TMP" || exit 1
chmod 644 "$TMP"
mv "$TMP" "$DEST"
trap - EXIT
echo "pull_drive_acount1: OK -> $DEST"
exit 0
