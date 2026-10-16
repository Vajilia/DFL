#!/usr/bin/env bash
# Turn on the website's Pause / Resume button. Run as root:  bash /opt/dfl/deploy/enable-controls.sh
# It starts the small pause service (dfl-control) and adds one route to the existing website configuration (the login is left exactly as it is; with the current template the route is already there and behind the login). Safe to run again.
set -euo pipefail
main() {
  [ "$(id -u)" -eq 0 ] || { echo "Run as root."; exit 1; }
  local APP=/opt/dfl CF=/etc/caddy/Caddyfile
  [ -f "$CF" ] || { echo "No website configuration found ($CF): run the setup first."; exit 1; }

  echo "== 1/3 Pause service"
  install -m 644 "$APP/deploy/dfl-control.service" /etc/systemd/system/dfl-control.service
  systemctl daemon-reload
  systemctl enable dfl-control >/dev/null 2>&1
  systemctl restart dfl-control
  sleep 2
  systemctl is-active dfl-control

  echo "== 2/3 Website route"
  if grep -q "reverse_proxy 127.0.0.1:8081" "$CF"; then
    echo "The route is already there."
  else
    cp "$CF" "$CF.before-controls"
    python3 - "$CF" <<'PY'
import re, sys
p = sys.argv[1]
s = open(p).read()
old = re.search(r"\n(\s*)root \* /var/www/dfl\n\s*file_server\n", s)
if not old:
    sys.exit("The website configuration is not in the expected shape; nothing was changed.")
ind = old.group(1)
new = f"\n{ind}handle /api/* {{\n{ind}\treverse_proxy 127.0.0.1:8081\n{ind}}}\n{ind}handle {{\n{ind}\troot * /var/www/dfl\n{ind}\tfile_server\n{ind}}}\n"
open(p, "w").write(s[:old.start()] + new + s[old.end():])
PY
    if ! caddy validate --config "$CF" --adapter caddyfile >/dev/null 2>&1; then
      cp "$CF.before-controls" "$CF"
      echo "The new configuration did not validate, so the old one was put back. Nothing changed."
      exit 1
    fi
  fi

  echo "== 3/3 Reload the website and rebuild the page"
  systemctl reload caddy || systemctl restart caddy
  # The pause switch must sit behind the website login: asking for it without a password has to be refused.
  local CODE
  CODE="$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 "https://$(cat /etc/dfl/host)/api/state" || true)"
  if [ "$CODE" != "401" ]; then
    if [ -f "$CF.before-controls" ]; then cp "$CF.before-controls" "$CF"; systemctl reload caddy || systemctl restart caddy; fi
    systemctl stop dfl-control || true
    echo "Without a password the pause switch answered $CODE instead of 401 (login required), so it was switched off again and the old configuration put back."
    exit 1
  fi
  echo "Checked: the pause switch is behind the website login."
  bash "$APP/deploy/update.sh" --no-pull --no-restart
  echo
  echo "Done. Open the Live tab: a league made with block pacing now has a Pause button."
}
main "$@"
exit
