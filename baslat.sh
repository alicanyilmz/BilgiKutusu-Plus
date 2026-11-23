#!/usr/bin/env bash
# BilgiKutusu Plus — yerel deneme, sistem ayarlarını değiştirmez.
set -euo pipefail
PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$PROJECT_DIR/uygulama/app.py" "$@"
