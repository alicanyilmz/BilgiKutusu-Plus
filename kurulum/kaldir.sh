#!/usr/bin/env bash
set -euo pipefail
[[ ${EUID} -eq 0 ]] || { echo 'sudo bash kurulum/kaldir.sh ile çalıştırın.'; exit 1; }
systemctl disable --now bilgikutusu-plus.service 2>/dev/null || true
# Keep content, config and service account so ownership and user data are preserved.
rm -f -- /etc/systemd/system/bilgikutusu-plus.service
rm -rf -- /opt/bilgikutusu-plus
systemctl daemon-reload
echo 'Plus hizmeti kaldırıldı. İçerikler, ayarlar, hizmet kullanıcısı ve Wi-Fi profilleri korundu.'
echo 'İçerikler: /srv/bilgikutusu-plus/icerik ; ayarlar: /etc/bilgikutusu-plus'
