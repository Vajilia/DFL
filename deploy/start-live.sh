#!/usr/bin/env bash
# Start (or restart) the live league on this server. Run as root. It can be typed as one line:
#   curl -fsSL https://raw.githubusercontent.com/Vajilia/dfl/step6-rebuild/deploy/start-live.sh | bash
# or, once the code is on the server:  bash /opt/dfl/deploy/start-live.sh
# The first time it asks when the first kickoff should happen (Pacific time). After that it only brings the code up to date and restarts the runner;
# the league carries on from the clock. Everything is inside main() so the whole script is read before anything runs.
set -euo pipefail

main() {
  [ "$(id -u)" -eq 0 ] || { echo "Run as root."; exit 1; }
  local APP=/opt/dfl LIVE=/var/www/dfl/live BRANCH="${DFL_BRANCH:-step6-rebuild}"
  [ -d "$APP/.git" ] || { echo "The league code is not on this server yet: run the setup first (deploy/INSTALL.md)."; exit 1; }

  echo "== 1/4 Latest league code"
  git -C "$APP" fetch origin "$BRANCH"
  git -C "$APP" reset --hard "origin/$BRANCH"

  echo "== 2/4 Runner account and folders"
  id dfl >/dev/null 2>&1 || useradd --system --no-create-home --shell /usr/sbin/nologin dfl
  mkdir -p "$LIVE/g"
  chown -R dfl:dfl "$LIVE"
  chmod 755 "$LIVE" "$LIVE/g"
  install -m 644 "$APP/deploy/dfl-live.service" /etc/systemd/system/dfl-live.service
  systemctl daemon-reload

  if [ ! -s "$LIVE/meta.json" ]; then
    echo
    echo "The live league has not been started yet."
    echo "When should the very first kickoff be? Type it in Pacific time as year-month-day hour:minute, for example  2026-10-17 09:00"
    local WHEN=""
    read -r -p "First kickoff: " WHEN < /dev/tty
    WHEN="${WHEN/ /T}"
    # The first kickoff is a real moment; the league's own opening (Founding Day) falls about three and a half real days before it.
    su -s /bin/bash dfl -c "TZ=America/Los_Angeles python3 -I $APP/engine/live.py --out $LIVE --opener-at '$WHEN' --init"
  fi

  echo "== 3/4 Pages"
  bash "$APP/deploy/update.sh" --no-pull --no-restart

  echo "== 4/4 Start the runner"
  systemctl enable dfl-live >/dev/null 2>&1
  systemctl restart dfl-live
  sleep 4
  systemctl is-active dfl-live
  echo
  echo "The live league is running. Open https://$(cat /etc/dfl/host) and look at the Live tab."
}
main "$@"
exit
