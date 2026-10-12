#!/usr/bin/env bash
# One-time setup of the DFL website on a fresh Ubuntu 24.04 server. Run as root (the DigitalOcean web Console is root).
#   curl -fsSL https://raw.githubusercontent.com/Vajilia/dfl/step6-rebuild/deploy/setup.sh | bash
# Safe to run again: it updates what is there. It installs Caddy (web server with automatic HTTPS), Python and git, opens ports 22/80/443,
# fetches the league code, builds the page, and asks you for a website login (typed on this machine only).
set -euo pipefail
[ "$(id -u)" -eq 0 ] || { echo "Run as root."; exit 1; }
BRANCH="${DFL_BRANCH:-step6-rebuild}"
REPO="https://github.com/Vajilia/dfl.git"
APP=/opt/dfl

export DEBIAN_FRONTEND=noninteractive
echo "== 1/6 Packages"
apt-get update -y
apt-get install -y debian-keyring debian-archive-keyring apt-transport-https curl gpg git python3 ufw
if ! command -v caddy >/dev/null; then
  curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor --yes -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
  curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' > /etc/apt/sources.list.d/caddy-stable.list
  apt-get update -y
  apt-get install -y caddy
fi

echo "== 2/6 Firewall (SSH, web)"
ufw allow 22/tcp >/dev/null
ufw allow 80/tcp >/dev/null
ufw allow 443/tcp >/dev/null
ufw --force enable >/dev/null

echo "== 3/6 League code"
if [ -d "$APP/.git" ]; then
  git -C "$APP" fetch origin "$BRANCH"
  git -C "$APP" checkout "$BRANCH"
  git -C "$APP" reset --hard "origin/$BRANCH"
else
  git clone --branch "$BRANCH" "$REPO" "$APP"
fi

echo "== 4/6 Address"
mkdir -p /etc/dfl /var/www/dfl
if [ ! -s /etc/dfl/host ]; then
  IP="$(curl -4 -fsS https://ifconfig.me || curl -4 -fsS https://api.ipify.org)"
  # sslip.io turns an address like 203-0-113-5.sslip.io into that IP, so HTTPS works without owning a domain.
  echo "${IP//./-}.sslip.io" > /etc/dfl/host
fi
echo "   address: https://$(cat /etc/dfl/host)"

echo "== 5/6 Build the page"
bash "$APP/deploy/update.sh" --no-pull

echo "== 6/6 Website login"
bash "$APP/deploy/render.sh"

echo
echo "Done. Open:  https://$(cat /etc/dfl/host)"
echo "(The first visit can take up to a minute while the security certificate is issued.)"
