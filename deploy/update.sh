#!/usr/bin/env bash
# Pull the latest league code and rebuild the pages. Run as root:  bash /opt/dfl/deploy/update.sh
#   --no-pull     rebuild from the code already on the server
#   --no-restart  do not restart the live runner (start-live.sh does that itself)
# With a live league running, index.html is the spoiler-free live page (it learns everything from the feed); before that it is the founding snapshot.
set -euo pipefail
main() {
  [ "$(id -u)" -eq 0 ] || { echo "Run as root."; exit 1; }
  local APP=/opt/dfl
  local BRANCH="${DFL_BRANCH:-step6-rebuild}"
  PULL=1; RESTART=1
  for a in "$@"; do case "$a" in --no-pull) PULL=0;; --no-restart) RESTART=0;; esac; done
  if [ "$PULL" = 1 ]; then
    git -C "$APP" fetch origin "$BRANCH"
    git -C "$APP" reset --hard "origin/$BRANCH"
  fi
  TMP="$(mktemp)"
  if [ -s /var/www/dfl/live/meta.json ]; then
    python3 -I "$APP/engine/build_site.py" --live "$TMP"      # a league is running: the page watches the feed, no results are baked in
    install -m 644 -o caddy -g caddy "$TMP" /var/www/dfl/index.html
    rm -f /var/www/dfl/snapshot.html      # (the founding snapshot would show the live league's year-1 results ahead of time)
  else
    python3 -I "$APP/engine/build_site.py" "$TMP"            # before the live league is started: the founding snapshot
    install -m 644 -o caddy -g caddy "$TMP" /var/www/dfl/index.html
  fi
  rm -f "$TMP"
  echo "Pages rebuilt from $(git -C "$APP" rev-parse --short HEAD)."
  if [ "$RESTART" = 1 ] && systemctl is-enabled dfl-live >/dev/null 2>&1; then
    systemctl restart dfl-live
    echo "Live runner restarted (the league carries on from the clock)."
  fi
}
main "$@"
exit
