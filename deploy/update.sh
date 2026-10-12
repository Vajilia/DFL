#!/usr/bin/env bash
# Pull the latest league code and rebuild the page. Run as root:  bash /opt/dfl/deploy/update.sh
set -euo pipefail
[ "$(id -u)" -eq 0 ] || { echo "Run as root."; exit 1; }
APP=/opt/dfl
BRANCH="${DFL_BRANCH:-step6-rebuild}"
if [ "${1:-}" != "--no-pull" ]; then
  git -C "$APP" fetch origin "$BRANCH"
  git -C "$APP" reset --hard "origin/$BRANCH"
fi
OUT="$(mktemp)"
python3 -I "$APP/engine/build_site.py" "$OUT"
install -m 644 -o caddy -g caddy "$OUT" /var/www/dfl/index.html
rm -f "$OUT"
echo "Page rebuilt from $(git -C "$APP" rev-parse --short HEAD)."
