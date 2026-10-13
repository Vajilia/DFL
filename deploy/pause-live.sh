#!/usr/bin/env bash
# Pause or resume the live league. Run as root:  bash /opt/dfl/deploy/pause-live.sh pause | resume | status
# While paused the league stands still: no play is revealed and the clock does not run. On resume it picks up exactly where it stopped, and every time on the page
# moves later by the length of the pause. (The runner looks at the switch every few seconds, so a pause can take up to about three seconds to show.)
set -euo pipefail
main() {
  [ "$(id -u)" -eq 0 ] || { echo "Run as root."; exit 1; }
  local LIVE=/var/www/dfl/live
  [ -s "$LIVE/meta.json" ] || { echo "No live league is set up."; exit 1; }
  case "${1:-status}" in
    pause)  printf '{"paused":true}\n'  > "$LIVE/control.json"; chown dfl:dfl "$LIVE/control.json"; chmod 644 "$LIVE/control.json"; echo "Pausing the league." ;;
    resume) printf '{"paused":false}\n' > "$LIVE/control.json"; chown dfl:dfl "$LIVE/control.json"; chmod 644 "$LIVE/control.json"; echo "Resuming the league." ;;
    status) grep -q '"paused": *true' "$LIVE/control.json" 2>/dev/null && echo "The league is paused." || echo "The league is running." ;;
    *) echo "Use: pause-live.sh pause | resume | status"; exit 1 ;;
  esac
}
main "$@"
exit
