"""Edition 8.15 isolated read-only founding website preview.

Consumes the six-tab public contract and canonical founding tables. No server,
controls, secrets, live output, state mutations or gameplay decisions.
"""
from __future__ import annotations

import argparse
import csv
from html import escape
from io import StringIO
from pathlib import Path
import re

import ed815_public_view as PUBLIC
import ed815_public_results as RESULTS

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "DFL_Design_Document_Ed8.15.md"

def founding_tables(document: str):
    blocks = re.findall(r"```\s*\n(.*?)```", document, flags=re.S)
    def extract(header):
        matches = [b for b in blocks if b.startswith(header + ",") or b.splitlines()[0] == header]
        if len(matches) != 1:
            raise ValueError("missing or ambiguous founding table " + header)
        return list(csv.DictReader(StringIO(matches[0].strip())))
    teams = extract("team_id,abbr,team_city,team_name")
    games = extract("week,game,date,kickoff,away,home")
    if len(teams) != 48 or len(games) != 360:
        raise ValueError("founding table counts differ from Edition 8.15")
    if len({int(t["team_id"]) for t in teams}) != 48:
        raise ValueError("duplicate founding club identity")
    if sum(t["is_active"] == "true" for t in teams) != 40:
        raise ValueError("founding active club count differs")
    if sum(t["club_status"] == "ambassador" for t in teams) != 8:
        raise ValueError("founding Ambassador club count differs")
    names = {t["team_city"] for t in teams}
    if any(g["away"] not in names or g["home"] not in names for g in games):
        raise ValueError("game references unknown club")
    if len({(g["week"], g["game"]) for g in games}) != 360:
        raise ValueError("duplicate numbered fixture")
    return teams, games

def render_html(document: str, *, cards=(), events=(), season_year=2000,
                since_sequence=0, revealed_through_sequence=0):
    teams, games = founding_tables(document)
    finals, records = RESULTS.revealed_finals(
        teams, games, events, through_sequence=revealed_through_sequence
    )
    revealed_events = [event for event in events
                       if event["sequence"] <= revealed_through_sequence]
    packet = PUBLIC.public_packet(cards=cards, events=revealed_events,
                                  season_year=season_year,
                                  since_sequence=since_sequence)
    def e(value):
        return escape(str(value), quote=True)
    rows = []
    for t in teams:
        primary = t["primary_hex"]
        if not re.fullmatch(r"#[0-9A-Fa-f]{6}", primary):
            raise ValueError("invalid canonical team palette")
        name = e(t["team_city"] + " " + t["team_name"])
        rows.append(
            f'<tr><td><span class="swatch" style="background:{primary}"></span>{name}</td>'
            f'<td>{e(t["conference"])}</td><td>{e(t["division"])}</td>'
            f'<td>{e(t["club_status"].title())}</td></tr>'
        )
    fixtures = []
    for g in games:
        final = finals.get((int(g["week"]), int(g["game"])))
        score = (f'{final["away_score"]}–{final["home_score"]}'
                 if final is not None else "—")
        fixtures.append(
            f'<tr><td>{e(g["week"])}</td><td>{e(g["date"])}</td>'
            f'<td>{e(g["kickoff"])} UTC</td><td>{e(g["away"])}</td>'
            f'<td>{e(g["home"])}</td><td>{e(score)}</td></tr>'
        )
    players = [
        '<article class="person"><strong>' + e(p["name"]) + '</strong>'
        + '<span>' + e(p["role"]) + ' · ' + e(p["position"]) + ' · age '
        + e(p["age"]) + '</span></article>'
        for p in packet["characters"]
    ]
    digest = [
        '<li><time>' + e(v["simulated_time"]) + '</time> '
        + e(v["public_summary"]) + '</li>'
        for v in packet["event_digest"]
    ]
    if not players:
        players = ['<p>No public player cards have been imported yet.</p>']
    if not digest:
        digest = ['<li>No new public events in this preview.</li>']
    if finals:
        standing_rows = []
        for t in sorted((t for t in teams if t["is_active"] == "true"),
                        key=lambda t: (t["conference"], t["division"], t["team_city"])):
            rec = records[t["team_city"]]
            standing_rows.append(
                f'<tr><td>{e(t["team_city"] + " " + t["team_name"])}</td>'
                f'<td>{e(rec.games_played)}</td><td>{e(rec.wins)}</td>'
                f'<td>{e(rec.losses)}</td><td>{e(rec.points_for)}</td>'
                f'<td>{e(rec.points_against)}</td></tr>'
            )
        standings_html = (
            '<p>Public completed games only; ties do not count as wins or losses. '
            'Playoff seeds are not declared in this provisional table.</p>'
            '<table><thead><tr><th>Club</th><th>GP</th><th>W</th>'
            '<th>L</th><th>PF</th><th>PA</th></tr></thead><tbody>'
            + "".join(standing_rows) + '</tbody></table>'
        )
        totals = RESULTS.public_totals(finals)
        stats_html = (
            '<p>Revealed final games: ' + e(totals["final_games"]) + '</p>'
            '<p>Tied games: ' + e(totals["ties"]) + '</p>'
            '<p>Points scored: ' + e(totals["total_points"]) + '</p>'
            '<p>Player performance statistics await a verified event feed.</p>'
        )
    else:
        standings_html = ('<p>No publicly revealed game finals yet. '
                          'Standings will use Edition 8.15 tiebreaks.</p>')
        stats_html = ('<p>No publicly revealed game finals yet. '
                      'No projected results or hidden ability ratings are displayed.</p>')
    sections = (
        ('Home', '<div class="numbers"><div><b>48</b> franchises</div>'
         '<div><b>40</b> active</div><div><b>8</b> Ambassadors</div>'
         '<div><b>360</b> numbered games</div></div>'
         '<h3>Public-event digest</h3><ul>' + "".join(digest) + '</ul>'),
        ('Teams', '<table><thead><tr><th>Club</th><th>Conference</th>'
         '<th>Division</th><th>Status</th></tr></thead><tbody>'
         + "".join(rows) + '</tbody></table>'),
        ('Players', '<div class="people">' + "".join(players) + '</div>'),
        ('Schedule', '<table><thead><tr><th>Week</th><th>Date</th>'
         '<th>Kickoff</th><th>Away</th><th>Home</th><th>Final</th></tr></thead><tbody>'
         + "".join(fixtures) + '</tbody></table>'),
        ('Standings', standings_html),
        ('Statistics', stats_html),
    )
    if tuple(s[0] for s in sections) != PUBLIC.TABS:
        raise AssertionError("navigation differs from Edition 8.15 §16")
    nav = "".join(f'<a href="#{title.lower()}">{title}</a>' for title, _ in sections)
    body = "".join(
        f'<section id="{title.lower()}"><h2>{title}</h2>{content}</section>'
        for title, content in sections
    )
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'">
<title>DFL — Edition 8.15 founding preview</title>
<style>
:root{color-scheme:dark}*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:#101623;color:#e6ebf2;font:16px/1.5 system-ui,sans-serif}
header{padding:2rem max(1rem,calc((100vw - 1100px)/2));background:linear-gradient(120deg,#162f4f,#331c39)}
h1{margin:.1rem 0;font-size:2.4rem}header p{margin:.3rem 0;color:#d5dce6}
nav{display:flex;flex-wrap:wrap;gap:.7rem;margin-top:1.3rem}
nav a{color:#edf5ff;text-decoration:none;border:1px solid #9da9bf;padding:.45rem .7rem;border-radius:.6rem}
main{max-width:1100px;margin:auto;padding:1.2rem}section{padding:1.5rem 0;border-bottom:1px solid #344158}
h2{color:#b9f2ff}h3{font-size:1.1rem}.numbers{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:.6rem}
.numbers>div,.person{padding:1rem;background:#1b2638;border-radius:.7rem}
.numbers b{font-size:2rem;display:block;color:#b9f2ff}
table{border-collapse:collapse;width:100%;font-size:.9rem}
th,td{padding:.55rem;text-align:left;border-bottom:1px solid #354155}
th{color:#b9f2ff}.swatch{display:inline-block;width:.7rem;height:.7rem;margin-right:.5rem;border-radius:50%}
.people{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:.6rem}.person span{display:block}
time{color:#b9f2ff}footer{max-width:1100px;margin:auto;padding:1.4rem;color:#a9b9ce}
@media(max-width:700px){main{padding:.8rem}table{display:block;overflow-x:auto;white-space:nowrap}}
</style></head><body>
<header><h1>Diamond Football League</h1>
<p>Edition 8.15 · Founding-season data preview · Read only</p>
<nav aria-label="Primary navigation">""" + nav + """</nav></header>
<main>""" + body + """</main>
<footer>Reference preview only. No simulated scores, commissioner actions or live season state.</footer>
</body></html>
"""

def main():
    ap = argparse.ArgumentParser(description="Build a separate, read-only founding preview")
    ap.add_argument("--out", type=Path, required=True, help="explicit preview HTML output path")
    args = ap.parse_args()
    html = render_html(SOURCE.read_text(encoding="utf-8"))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(html, encoding="utf-8")
    print("Wrote isolated Edition 8.15 preview:", args.out)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
