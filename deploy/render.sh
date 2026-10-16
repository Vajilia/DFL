#!/usr/bin/env bash
# Writes /etc/caddy/Caddyfile from the template, the host name, a user name and a password typed here on the server. Run as root.
# The password is asked for on this machine only; the repository never sees it.
set -euo pipefail
[ "$(id -u)" -eq 0 ] || { echo "Run as root."; exit 1; }
# When started through a pipe (curl | bash) the keyboard is not stdin; read the answers from the terminal instead.
[ -t 0 ] || exec < /dev/tty
HERE="$(cd "$(dirname "$0")" && pwd)"
HOST="$(cat /etc/dfl/host)"
CUR_USER="$(cat /etc/dfl/user 2>/dev/null || echo dfl)"
read -r -p "Login name for the Pause button (the website itself is public) [$CUR_USER]: " U || true
U="${U:-$CUR_USER}"
case "$U" in *[!A-Za-z0-9_.-]*|"") echo "Use letters, digits, dot, dash or underscore only."; exit 1;; esac
while true; do
  read -r -s -p "Password for the Pause button (min 10 characters): " P1; echo
  read -r -s -p "Again: " P2; echo
  [ "$P1" = "$P2" ] && [ "${#P1}" -ge 10 ] && break
  echo "They did not match, or were shorter than 10 characters. Try again."
done
HASH="$(caddy hash-password --plaintext "$P1")"
unset P1 P2
TMP="$(mktemp)"
sed -e "s|__HOST__|$HOST|" -e "s|__USER__|$U|" -e "s|__HASH__|$HASH|" "$HERE/Caddyfile.template" > "$TMP"
install -m 640 -o root -g caddy "$TMP" /etc/caddy/Caddyfile
rm -f "$TMP"
echo "$U" > /etc/dfl/user
caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile >/dev/null
systemctl reload caddy || systemctl restart caddy
echo "The login for the Pause button is now: $U (password as you typed it)."
