#!/usr/bin/env bash
# Start the Chronicle (the weekly story). Run as root:  bash /opt/dfl/deploy/enable-chronicle.sh
# It only reads the live feed and writes /var/www/dfl/live/chronicle; it never restarts the league runner. Safe to run again.
# Without /etc/dfl/chronicle.env it uses the free template writer. To use an AI writer, create that file yourself on the server (mode 600, owner root) with
#   ANTHROPIC_API_KEY=...   DFL_CHRONICLE_MODEL=...   DFL_PRICE_IN=...   DFL_PRICE_OUT=...   (one per line; prices are dollars per million tokens)
# and then:  systemctl restart dfl-chronicle
set -euo pipefail
main() {
  [ "$(id -u)" -eq 0 ] || { echo "Run as root."; exit 1; }
  local APP=/opt/dfl OUT=/var/www/dfl/live/chronicle
  mkdir -p "$OUT"
  chown dfl:dfl "$OUT"
  install -m 644 "$APP/deploy/dfl-chronicle.service" /etc/systemd/system/dfl-chronicle.service
  systemctl daemon-reload
  systemctl enable dfl-chronicle >/dev/null 2>&1
  systemctl restart dfl-chronicle
  sleep 3
  systemctl is-active dfl-chronicle
  echo "Chronicle files so far: $(ls "$OUT" 2>/dev/null | grep -c '^[0-9]' || true)"
}
main "$@"
exit
