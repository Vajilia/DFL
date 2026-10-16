#!/usr/bin/env bash
# Make the website public (no password to view it) WITHOUT touching the league's code. Run as root on the server:
#   bash /opt/dfl/deploy/make-public.sh           do it
#   bash /opt/dfl/deploy/make-public.sh --undo    put the login back exactly as it was
# It only edits the web server's configuration (/etc/caddy/Caddyfile). It does not pull code, rebuild the page or restart the league
# (a restart replays the league from its seed, so new engine code could change results already played).
# If the pause switch is on (the /api route), that route keeps the login; the pages become open.
set -euo pipefail
main() {
  [ "$(id -u)" -eq 0 ] || { echo "Run as root."; exit 1; }
  local CF=/etc/caddy/Caddyfile BK=/etc/caddy/Caddyfile.before-public
  [ -f "$CF" ] || { echo "No website configuration found ($CF). Nothing changed."; exit 1; }
  if [ "${1:-}" = "--undo" ]; then
    [ -f "$BK" ] || { echo "No backup ($BK) to go back to. Nothing changed."; exit 1; }
    cp "$CF" "$CF.public-version"; cp "$BK" "$CF"
    caddy validate --config "$CF" --adapter caddyfile >/dev/null 2>&1 || { cp "$CF.public-version" "$CF"; echo "The backup did not validate; the public version was put back. Nothing changed."; exit 1; }
    systemctl reload caddy || systemctl restart caddy
    echo "Done: the website is behind its login again, as it was before."; exit 0
  fi
  [ -f "$BK" ] || cp -p "$CF" "$BK"            # the first backup is kept; running this twice never overwrites it
  cp -p "$CF" "$CF.pre-run"
  local out
  out="$(python3 - "$CF" <<'PY'
import re, sys
p = sys.argv[1]
s = open(p).read()
m = re.search(r"\n([ \t]*)basic_auth \{\n[ \t]*(\S+) (\S+)\n[ \t]*\}\n", s)
if not m:
    print("NOCHANGE"); sys.exit(0)
ind, user, h = m.group(1), m.group(2), m.group(3)
s = s[:m.start()] + "\n" + s[m.end():]
r = re.search(r"\n([ \t]*)handle /api/\* \{\n", s)
if r:
    i2 = r.group(1) + "\t"
    block = f"{i2}basic_auth {{\n{i2}\t{user} {h}\n{i2}}}\n"
    s = s[:r.end()] + block + s[r.end():]
    print("API")
else:
    print("OPEN")
open(p, "w").write(s)
PY
)"
  if [ "$out" = "NOCHANGE" ]; then echo "No site-wide login found in the configuration: it may already be public. Nothing changed."; exit 0; fi
  if ! caddy validate --config "$CF" --adapter caddyfile >/dev/null 2>&1; then
    cp -p "$CF.pre-run" "$CF"; echo "The new configuration did not validate, so the old one was put back. Nothing changed."; exit 1
  fi
  systemctl reload caddy || systemctl restart caddy
  sleep 2
  local HOST A B
  HOST="$(cat /etc/dfl/host)"
  A="$(curl -s -o /dev/null -w '%{http_code}' --max-time 20 "https://$HOST/" || true)"
  B="$(curl -s -o /dev/null -w '%{http_code}' --max-time 20 "https://$HOST/api/state" || true)"
  if [ "$A" != "200" ] || { [ "$out" = "API" ] && [ "$B" != "401" ]; }; then
    cp -p "$CF.pre-run" "$CF"; systemctl reload caddy || systemctl restart caddy
    echo "Checks failed (home page answered $A without a password; pause switch answered $B). The old configuration was put back."; exit 1
  fi
  echo "Done: the website answers $A without a password."
  if [ "$out" = "API" ]; then
    echo "The pause switch still needs the login (answered $B without it)."
    echo "Note: until the page itself is updated, a visitor on the Live tab may see a password box (the page asks for the pause switch). Cancel closes it."
  else
    echo "(The pause switch is not turned on on this server, so there is no login left at all.)"
  fi
  echo "To go back: bash /opt/dfl/deploy/make-public.sh --undo"
}
main "$@"
exit
