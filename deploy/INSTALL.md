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
2. Type this single line (the Console's paste can add hidden characters that break the command, so typing it is safer) and press Enter:

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

## 3b. The live league

Setup gives you a snapshot of the founding season. To run the league live on the server (it plays each game at its kickoff and the page follows):

1. Open the Console and type this one line, then Enter:

       curl -fsSL https://raw.githubusercontent.com/Vajilia/dfl/step6-rebuild/deploy/start-live.sh | bash

2. The first time it asks **"First kickoff:"**. Type the date and time in Pacific time, like `2026-10-17 09:00`, and press Enter. It then starts the runner
   (a systemd service named `dfl-live`, so it keeps running when you close the Console and starts again if the server restarts).
3. Open the website and look at the **Live** tab. Until the first kickoff it counts down; then games appear as they are played.

A new league runs block after block (a game about 30 minutes, 2 minutes between blocks, 5 between weeks; a league year about 56 hours). A league made before 2026-10-13 keeps its old pace (one league year per real week, a game about 36 minutes). Typing the line again later just updates the code and restarts the runner; the league carries on from the clock,
nothing is lost. To see how it is doing: `systemctl status dfl-live`, or `journalctl -u dfl-live -n 20`.

- **Pause / resume** (new leagues only): `bash /opt/dfl/deploy/pause-live.sh pause`, `... resume`, `... status`. A paused league stands still and picks up where it stopped.
- **Start over** (erase the league and begin again; the old feed is kept in `/var/lib/dfl-archive`): `bash /opt/dfl/deploy/reset-live.sh`. It asks for the first kickoff and a seed.

## What this does and does not do

The page is a read-only window; nothing on it can change anything. The live league is the engine on autopilot (no agents yet: the Director, the Commissioner page and the
agents come later and will run on this same server).

## What the script does (for the curious or the cautious)

Installs Caddy (web server, automatic https), Python 3 and git; opens ports 22, 80, 443 only; clones https://github.com/Vajilia/dfl (public)
to `/opt/dfl`; builds the page to `/var/www/dfl/index.html`; writes `/etc/caddy/Caddyfile` with the login stored as a bcrypt hash. Pages
are marked do-not-index so search engines skip them. The script file is in this folder if you want to read it first.

## Honest caveat

These scripts were checked for syntax and the page build was tested on the same Python version Ubuntu 24.04 ships (it builds byte-identical),
but they have not yet been run on a real droplet. If any step prints an error, paste it back and it will be fixed.
