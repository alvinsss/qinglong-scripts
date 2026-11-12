# qinglong-scripts

Backup of the task scripts running in the Qinglong panel on the platform
serv00 machine (https://ql.platform.serv00.net/, Qinglong v2.24.0).

## Task scripts

| File | Schedule | What it does |
| --- | --- | --- |
| `X_lastMS_tg.py` | daily 08:10 | Fetch the latest 2 original posts for 6 X accounts via twexapi.io and send new ones to a Telegram group. Dedup via `x_sent_ids.json`. |
| `pull_muse_usage.py` | every 15 min | Fetch `muse-usage_all.json`, mask 账号1 with `*`, write `panel/muse_usage.json` for the fleet dashboard. |
| `pull_drive_acount1.sh` | every 15 min | Pull 账号1's Muse usage JSON from Google Drive (URL in `usage_pull/drive_url_acount1.txt`) to `muse-usageAcount1.json`. |
| `pull_drive_acount2.sh` | every 15 min | Pull 账号2's Muse usage JSON from Google Drive (URL in `usage_pull/drive_url.txt`) to `muse-usageAcount2.json`. |
| `pull_drive.sh` | — | Same as `pull_drive_acount2.sh` (generic Drive pull). |

## One-off patch / verify scripts (already applied)

| File | What it did |
| --- | --- |
| `patch_muse_usage.py` | Patched `panel_fleet.py` to merge `muse_usage.json` into `/api/fleet` and render the Muse usage table. |
| `patch_pubwsgi_muse.py` | Patched `public_python/passenger_wsgi.py` the same way (this is the live one). |
| `patch_wsgi_muse.py` | Patched the domain-root `passenger_wsgi.py` the same way. |
| `patch_remain_col.py` | Added the 剩余额度 column to the Muse usage table. |
| `check_fleet_muse2.py` | Verified `/api/fleet` muse_usage twice, 30 s apart. |
| `check_fleet_remain.py` | Verified `/api/fleet` muse_usage and `remaining_percent_text`. |
| `seed_x_sent.py` | Seeded `x_sent_ids.json` with the latest 2 originals per account. |
| `seed_x_sent_rl.py` | Same, rate-limited (one account every 5 min) to avoid the viewer API 429. |

## Notification library

- `notify.py` / `sendNotify.js` — Qinglong notification modules (with custom
  additions). All notification tokens are empty strings here; real tokens live
  only in the panel's `config.sh` / environment, never in this repo.

## Secrets

No tokens, keys, or credentials are stored in this repo. Scripts read secrets
from environment variables or from local files on the server
(`TG_BOT_TOKEN` / `TG_CHAT_ID`, `usage_pull/drive_url*.txt`,
`panel/token.txt`). Do not commit those files.

## Notes

- `x_sent_ids.json` (dedup state, changes every run) is intentionally not
  committed.
- `cryptoTrader_report/` (the TG report project tree) is not included here.
