# Runbook: make the live website public (no password to view it)

Status: **proposed**. Nothing here has been run on the server. The owner approves each step; Claude cannot reach the server.
Written 2026-10-16. Applies to the DigitalOcean server that serves the live league.

## Read this first: do NOT run `update.sh` for this

The live league is replayed from its seed every time the runner restarts, and `update.sh` pulls the newest code and restarts the runner.
Since the server was last updated, the code has changed in ways that move results (for example the tiebreak order, PR #14, and several rule versions).
`engine/live.py` warns about exactly this ("any change to how games are played can change what they were"). So **updating the server's code is a
separate decision** (it can rewrite results already played, which the project rules forbid without approval). Making the site public needs only a change
to the web server's configuration, which is what `deploy/make-public.sh` does. It does not pull, rebuild or restart anything.

## 0. Look first (changes nothing)

In the DigitalOcean Console (as root), and paste the output to Claude if anything looks odd:

```
git -C /opt/dfl rev-parse --short HEAD                      # the code the server is on
grep engine_commit /var/www/dfl/live/meta.json              # the code the league was made with
systemctl is-active dfl-live dfl-control caddy              # which services are running (dfl-control may say inactive: fine)
grep -c "reverse_proxy 127.0.0.1:8081" /etc/caddy/Caddyfile # 1 = the Pause button's route is on, 0 = it is not
```

## 1. Back up (about 5 minutes)

1. **DigitalOcean snapshot** (the real safety net): in the DigitalOcean dashboard open the server (Droplet) > Snapshots > Take snapshot. It costs a few cents a month; delete it when you are happy. You can take it with the server running.
2. **File copies** on the server:
```
mkdir -p /root/dfl-backup-2026-10-16
cp -p /etc/caddy/Caddyfile /root/dfl-backup-2026-10-16/
tar czf /root/dfl-backup-2026-10-16/live-state.tgz /var/www/dfl/live /etc/dfl
ls -l /root/dfl-backup-2026-10-16/
```
The league's own state is the feed in `/var/www/dfl/live`; the script does not touch it. The copy is for peace of mind.

## 2. Do it (about 1 minute)

Get the script without moving the server's code (this fetches one file, nothing else):

```
git -C /opt/dfl fetch origin main
git -C /opt/dfl show origin/main:deploy/make-public.sh > /root/make-public.sh
less /root/make-public.sh        # read it if you like; q to quit
bash /root/make-public.sh
```

The script keeps a copy of the configuration (`/etc/caddy/Caddyfile.before-public`), changes it, checks it is valid, reloads the web server, then
checks that the home page opens **without** a password (and, if the Pause button is on, that its route still demands the login). If any check fails it puts
the old configuration back by itself and says so.

## 3. Verify (from any browser or phone, not logged in)

- Open `https://<the address>`: it loads with no password box. A private/incognito window is the cleanest test.
- Click through Live, Standings, Schedule.
- If the Pause button is on: a visitor on the Live tab may briefly see a password box (the older page asks for the switch). Cancel closes it and everything else works. This goes away when the page is updated (see "Later").
- Only if you want to be sure the pause switch is still locked: `curl -s -o /dev/null -w '%{http_code}\n' https://<the address>/api/state` should print `401`.

## Rollback (about 1 minute)

```
bash /root/make-public.sh --undo
```
That restores the saved configuration and reloads the web server (the site is behind its login again). If the script itself is unavailable:
```
cp /etc/caddy/Caddyfile.before-public /etc/caddy/Caddyfile && systemctl reload caddy
```
Last resort: restore the DigitalOcean snapshot. Nothing in this plan changes league state, so there is nothing to roll back there.

## Later (not part of this, needs its own approval)

- **Updating the server's code** (so the page gets the Standings tab and the quiet Pause-button check, plus every engine change since): first compare `git -C /opt/dfl diff --stat HEAD origin/step6-rebuild -- engine | tail -1`. If the engine differs, the choice is to start a new league (`deploy/reset-live.sh` archives the old feed) or to hold the league on its current code. Decide that deliberately, with a snapshot.
- After such an update, `deploy/render.sh` writes the new configuration shape (login on `/api/*` only), and the Pause button appears in a browser opened once as `https://<the address>/?admin=1`.
- The "do not index" header stays on, so search engines still skip the site; remove it only if you want the site findable.
