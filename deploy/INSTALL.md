# Putting the DFL website on its own server

This puts the read-only league window on a small always-on server, behind a login, with a secure (https) address. About 15 minutes, about
$12 a month. You do the account and the server; the password is typed only on the server, never to Claude or into the repository.

## 1. Make the server (DigitalOcean)

1. Sign up at digitalocean.com (card and email: yours to enter).
2. **Create → Droplets**, then choose:
   - Region: New York or San Francisco (whichever is closer to you and your peers)
   - Image: **Ubuntu 24.04 (LTS) x64**
   - Size: **Basic, Regular SSD, 2 GB / 1 CPU** (about $12/month)
   - Authentication: **Password** (pick a long one for the *server's* root account; keep it in your password manager; it is not the website login)
   - Tick **Enable backups** (weekly, about 20% extra). Name it `dfl`.
3. Click **Create Droplet** and wait about a minute.

## 2. Install

1. Open the droplet and click **Console** (top right). A black terminal opens in the browser and logs you in as root. If it asks for the
   login, user `root` and the server password from step 1.
2. Paste this single line and press Enter:

       curl -fsSL https://raw.githubusercontent.com/Vajilia/dfl/step6-rebuild/deploy/setup.sh | bash

3. It takes a few minutes. Near the end it asks for a **website login name** (press Enter to accept `dfl`) and a **password**
   (at least 10 characters, typed twice; nothing shows as you type). This is what you and your peers will use.
4. It ends with the address, for example `https://203-0-113-5.sslip.io`. Open it; the first visit can take up to a minute while the security
   certificate is issued. Give peers the address and the login.

The address is built from the server's number using the free sslip.io service, so no domain purchase is needed. If you later buy a domain,
point it at the server and tell Claude; it is one line to change.

## 3. Later

- **New version of the league window:** open the Console and run `bash /opt/dfl/deploy/update.sh`
- **Change the website login:** `bash /opt/dfl/deploy/render.sh`
- **If something goes wrong:** copy whatever the Console printed and paste it to Claude.

## What this does and does not do

It serves a snapshot of the founding league (the seed-7 export that the page is built from). It is not yet the always-running league: that
is the later step (Director, scheduled seasons, agents), and it will run on this same server. Nothing on the page can change anything.

## What the script does (for the curious or the cautious)

Installs Caddy (web server, automatic https), Python 3 and git; opens ports 22, 80, 443 only; clones https://github.com/Vajilia/dfl (public)
to `/opt/dfl`; builds the page to `/var/www/dfl/index.html`; writes `/etc/caddy/Caddyfile` with the login stored as a bcrypt hash. Pages
are marked do-not-index so search engines skip them. The script file is in this folder if you want to read it first.

## Honest caveat

These scripts were checked for syntax and the page build was tested on the same Python version Ubuntu 24.04 ships (it builds byte-identical),
but they have not yet been run on a real droplet. If any step prints an error, paste it back and it will be fixed.
