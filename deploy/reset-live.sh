#!/usr/bin/env bash
# Erase the live league and start a fresh one from the beginning. Run as root:  bash /opt/dfl/deploy/reset-live.sh
# The old league is not deleted: its feed is moved to /var/lib/dfl-archive/live-<date> (only root can see it there) and can be put back by hand.
# The new league runs with the code now on the server (blocks pacing: continuous, about 30-minute games, pausable). It asks for the first kickoff and a seed.
set -euo pipefail

main() {
  [ "$(id -u)" -eq 0 ] || { echo "Run as root."; exit 1; }
  local APP=/opt/dfl LIVE=/var/www/dfl/live ARCH=/var/lib/dfl-archive
  [ -d "$APP/.git" ] || { echo "The league code is not on this server yet: run the setup first (deploy/INSTALL.md)."; exit 1; }

  echo "This ERASES the live league (every game played so far) and starts a new one from the beginning."
  echo "The old feed is kept in $ARCH."
  local SURE=""
  read -r -p "Type  reset  to go on: " SURE < /dev/tty
  [ "$SURE" = "reset" ] || { echo "Nothing was changed."; exit 1; }

  echo "When should the very first kickoff be? Pacific time as year-month-day hour:minute, for example  2026-10-17 19:00  (Saturday night is when block 1 would be)"
  local WHEN="" SEED="" PARITY=""
  read -r -p "First kickoff: " WHEN < /dev/tty
  read -r -p "Seed (Enter for 7; the same seed always makes the same league): " SEED < /dev/tty
  SEED="${SEED:-7}"
  read -r -p "Parity (Enter for tight = the rules as written; none = no cap, floor, exile help or lottery): " PARITY < /dev/tty
  PARITY="${PARITY:-tight}"
  case "$PARITY" in tight|none) ;; *) echo "Parity must be  tight  or  none. Nothing was changed."; exit 1;; esac
  case "$SEED" in ''|*[!0-9]*) echo "The seed must be a whole number. Nothing was changed."; exit 1;; esac
  WHEN="${WHEN/ /T}"

  # Check the new league can be made before the old one is touched.
  local CHECK; CHECK="$(mktemp -d)"
  chown dfl:dfl "$CHECK"
  su -s /bin/bash dfl -c "TZ=America/Los_Angeles python3 -I $APP/engine/live.py --out $CHECK --opener-at '$WHEN' --seed $SEED --pacing blocks --parity $PARITY --init" \
    || { rm -rf "$CHECK"; echo "That first kickoff was not understood. Nothing was changed."; exit 1; }

  echo "== 1/4 Stop the runner"
  systemctl stop dfl-live 2>/dev/null || true

  echo "== 2/4 Keep the old league"
  if [ -e "$LIVE/meta.json" ]; then
    mkdir -p "$ARCH"; chmod 700 "$ARCH"
    mv "$LIVE" "$ARCH/live-$(date +%Y%m%d-%H%M%S)"
  fi
  mkdir -p "$LIVE/g"
  cp "$CHECK/meta.json" "$LIVE/meta.json"
  rm -rf "$CHECK"
  chown -R dfl:dfl "$LIVE"
  chmod 755 "$LIVE" "$LIVE/g"

  echo "== 3/4 Pages"
  bash "$APP/deploy/update.sh" --no-pull --no-restart

  echo "== 4/4 Start the new league"
  systemctl enable dfl-live >/dev/null 2>&1
  systemctl restart dfl-live
  sleep 4
  systemctl is-active dfl-live
  echo
  echo "The new league is running; its first kickoff is $WHEN Pacific, parity $PARITY. Open https://$(cat /etc/dfl/host) and look at the Live tab."
}
main "$@"
exit
