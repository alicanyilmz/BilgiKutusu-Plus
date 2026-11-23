#!/usr/bin/env bash
set -euo pipefail
systemctl --no-pager status bilgikutusu-plus.service || true
echo 'Cihaz IP adresleri:'
hostname -I
python3 - <<'PY'
import json, urllib.request
try:
    with open('/etc/bilgikutusu-plus/config.json', encoding='utf-8') as f: cfg=json.load(f)
    host=cfg.get('host','127.0.0.1')
    if host == '0.0.0.0': host='127.0.0.1'
    with urllib.request.urlopen(f"http://{host}:{cfg.get('port',8091)}/api/health",timeout=5) as r:
        print('Uygulama yanıtı:',json.load(r))
except Exception as exc:
    raise SystemExit('Durum denetlenemedi: '+str(exc))
PY
