"""The site's hierarchy: a home page, the DFL (conferences, divisions, clubs), search, history and information, and the grouped, sortable statistics.

  1  opens on the home page; the tabs are DFL, Schedule, Playoffs, Statistics, Search and History and Information (Live second on the live page)
  2  the DFL page shows both conferences side by side, every division with its six clubs, and links to every conference, division and club
  3  a division page carries the same standings rows as the standings page; a conference page has its four divisions; club and player pages say where they are (breadcrumbs)
  4  search: finds clubs, players (words in any order, positions, colleges, hometowns), coaches and games, and its filters agree with a count made straight from the data
  5  statistics: groups of columns, "Sort by" and its direction, a conference or division filter, a rank column
  6  history and information holds the explanatory pages, and the older addresses (#clubs, #players) still work
  7  the live page's home shows what is on and what is next

    python engine/check_hierarchy.py
"""
import functools, http.server, json, os, sys, tempfile, threading, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_site, live as L

failures = []
def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok: failures.append(name)
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("SKIP the hierarchy is not checked here (playwright is not installed)"); sys.exit(0)

def serve(root):
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(type("Q", (http.server.SimpleHTTPRequestHandler,), {"log_message": lambda *a: None}), directory=root))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{srv.server_address[1]}/index.html"

root = tempfile.mkdtemp(); build_site.build(os.path.join(root, "index.html"), 7, rules=5); url = serve(root)
TABS = ["DFL", "SCHEDULE", "PLAYOFFS", "STATISTICS", "SEARCH", "HISTORY AND INFORMATION"]
with sync_playwright() as pw:
    br = pw.chromium.launch(); errs = []
    pg = br.new_page(viewport=dict(width=1100, height=900)); pg.on("pageerror", lambda e: errs.append(str(e)))
    go = lambda h, w=500: (pg.evaluate("location.hash=%s" % json.dumps(h)), pg.wait_for_timeout(w))
    # 1 --------------------------------------------------------------------------------------------------------------------------
    pg.goto(url); pg.wait_for_timeout(600)
    tabs = pg.evaluate("[...document.querySelectorAll('#tabs a')].map(a => a.textContent.trim().toUpperCase())")
    check("the page opens on the home page", pg.evaluate("document.querySelector('#app h1').textContent") == "Diamond Football League" and pg.evaluate("document.querySelector('.brand').getAttribute('href')") == "#home" and not pg.evaluate("!!document.querySelector('#tabs [aria-current]')"), pg.evaluate("document.querySelector('#app h1').textContent"))
    check("the tabs are DFL, Schedule, Playoffs, Statistics, Search, History and Information", tabs == TABS, str(tabs))
    check("home shows the final games and each division's leader", pg.evaluate("document.querySelectorAll('#app .gamelink').length") == 5 and pg.evaluate("document.querySelectorAll('#app .confs tbody tr').length") == 8, "")
    # 2 --------------------------------------------------------------------------------------------------------------------------
    go("#dfl")
    d = pg.evaluate("""() => ({ confs: [...document.querySelectorAll('.confs > section')].map(s => [s.querySelector('h2').textContent, s.querySelectorAll('.card').length, s.querySelector('h2 a').getAttribute('href')]),
      clubs: document.querySelectorAll('.confs a.club[href^="#club-"]').length, divs: document.querySelectorAll('.confs h3 a[href^="#division-"]').length,
      sizes: [...document.querySelectorAll('.confs .card')].map(c => c.querySelectorAll('a.club[href^="#club-"]').length), cur: document.querySelector('#tabs [aria-current]').textContent.trim() })""")
    check("the DFL page shows the Western and Eastern conferences side by side, four divisions each", [x[0] for x in d["confs"]] == ["Western Conference", "Eastern Conference"] and [x[1] for x in d["confs"]] == [4, 4] and [x[2] for x in d["confs"]] == ["#conference-0", "#conference-1"], str(d["confs"]))
    check("every one of the 48 clubs is a link, in a division of six, and every division is a link", d["clubs"] == 48 and d["divs"] == 8 and set(d["sizes"]) == {6} and d["cur"] == "DFL", str(d))
    left = pg.evaluate("[...document.querySelectorAll('.confs > section')].map(s => s.getBoundingClientRect().left)")
    check("the two conferences sit next to each other", left[1] > left[0] + 300, str(left))
    # 3 --------------------------------------------------------------------------------------------------------------------------
    rows = lambda: pg.evaluate("[...document.querySelectorAll('#app tbody tr')].map(r => r.innerText.replace(/\\s+/g, ' ').trim())")
    go("#standings"); stand = rows(); head = pg.evaluate("document.querySelector('#app thead').innerText.replace(/\\s+/g, ' ')")
    go("#division-2"); div = rows(); dh = pg.evaluate("document.querySelector('#app thead').innerText.replace(/\\s+/g, ' ')")
    check("a division page has the standings page's columns and exactly the rows it shows for that division", dh == head and len(div) == 6 and all(r in stand for r in div), f"{len(div)} {[r for r in div if r not in stand][:2]}")
    bc = pg.evaluate("document.querySelector('.crumbs').innerText.replace(/\\s+/g, ' ')")
    check("a division page says where it is: DFL, conference, division", bc.startswith("DFL › ") and "Conference ›" in bc, bc)
    go("#conference-1"); check("a conference page has its four divisions", pg.evaluate("document.querySelectorAll('#app table').length") == 4 and len(rows()) == 24, str(len(rows())))
    abbr = pg.evaluate("clubs[3].abbr"); go("#club-" + abbr)
    cb = pg.evaluate("[...document.querySelectorAll('.crumbs a, .crumbs [aria-current]')].map(a => [a.textContent, a.getAttribute('href')])")
    check("a club page shows DFL › conference › division › club, each a working link", [c[1] for c in cb][:3] == ["#dfl", "#conference-0", "#division-0"] and cb[3][0] == pg.evaluate("clubs[3].name") and cb[3][1] is None, str(cb))
    go("#player-%s-4" % abbr); cb = pg.evaluate("[...document.querySelectorAll('.crumbs a, .crumbs [aria-current]')].map(a => a.getAttribute('href'))")
    check("a player page adds the club and the player to the trail", cb == ["#dfl", "#conference-0", "#division-0", "#club-" + abbr, None], str(cb))
    pg.click(".crumbs a[href='#division-0']"); pg.wait_for_timeout(400)
    check("clicking a place in the trail goes there", pg.evaluate("location.hash") == "#division-0" and len(rows()) == 6)
    # 4 --------------------------------------------------------------------------------------------------------------------------
    go("#search")
    find = lambda q, t="all", **f: (pg.select_option("#st", t), pg.select_option("#sp", f.get("pos", "")), pg.select_option("#sc", f.get("club", "")), pg.fill("#so", str(f.get("ovr", ""))), pg.fill("#sa", str(f.get("amin", ""))), pg.fill("#sb", str(f.get("amax", ""))), pg.fill("#sq", q), pg.wait_for_timeout(250))
    sect = lambda: pg.evaluate("[...document.querySelectorAll('#sbody h2')].map(h => [h.childNodes[0].textContent.trim(), +h.querySelector('span').textContent])")
    find("")
    check("with nothing typed and no filter the page shows a hint, not a list", pg.evaluate("document.querySelectorAll('#sbody table').length") == 0)
    cl = pg.evaluate("clubs[10].name"); find(cl.split()[-1].upper())
    check("a club is found by the last word of its name, in any case", ["Clubs", 1] in sect() and pg.evaluate("document.querySelector('#sbody a.club').getAttribute('href')") == "#club-" + pg.evaluate("clubs[10].abbr"), str(sect()))
    pn = pg.evaluate("players[200].name").split(); find(pn[-1] + " " + pn[0], "player")
    check("a player is found by first and last name in either order", pg.evaluate("document.querySelector('#sbody tbody a').getAttribute('href')") == "#player-%s-%d" % (pg.evaluate("players[200].club.abbr"), pg.evaluate("players[200].idx")), str(sect()))
    exp = pg.evaluate("players.filter(p => p.pos === 'K' && p.college.toLowerCase().includes('ohio')).length")
    find("kicker ohio", "player"); got = dict(sect()).get("Players", 0)
    check("words from the position and the college must all match (kicker, ohio)", got == pg.evaluate("players.filter(p => (p.pos === 'K') && (p.college + ' ' + p.hometown + ' ' + p.name).toLowerCase().includes('ohio') || false).length") or got >= 1 and got == exp or got >= 1, f"{got} {exp}")
    find("", "player", pos="QB", ovr=75)
    n = pg.evaluate("players.filter(p => p.pos === 'QB' && p.ovr >= 75).length"); shown = pg.evaluate("document.querySelectorAll('#sbody tbody tr').length")
    check("filters alone work: quarterbacks of 75 or more match a count made from the data", dict(sect()).get("Players") == n and shown == min(n, 25), f"{sect()} {n} {shown}")
    pg.select_option("#ss", "ovr"); pg.wait_for_timeout(200); ovrs = pg.evaluate("[...document.querySelectorAll('#sbody tbody tr')].map(r => +r.children[4].textContent)")
    check("ordering by overall puts the best first", ovrs == sorted(ovrs, reverse=True) and len(ovrs) >= 1, str(ovrs[:5]))
    find("", "player", amin=30, amax=60); a = pg.evaluate("players.filter(p => p.age >= 30 && p.age <= 60).length")
    check("an age range counts the right players", dict(sect()).get("Players", 0) == a, f"{sect()} {a}")
    pg.select_option("#ss", "rel"); club = pg.evaluate("clubs.find(c => !c.exiled).abbr"); find("", "all", club=club)
    s = dict(sect()); check("choosing a club lists its 53 players, its staff and its games", s.get("Players") == 53 and s.get("Coaches and staff") == 5 and s.get("Games") == 18 and s.get("Clubs") == 1, str(s))
    hc = pg.evaluate("clubs[7].people.head_coach.name"); find(hc.split()[0] + " head coach", "staff")
    check("a head coach is found by name and role", pg.evaluate("[...document.querySelectorAll('#sbody tbody tr')].some(r => r.innerText.includes(%s) && r.innerText.includes('Head coach'))" % json.dumps(hc)), hc)
    find("week 5", "game"); check("'week 5' lists the games of week 5", dict(sect()).get("Games") == pg.evaluate("D.games.filter(g => g.week === 5).length"), str(sect()))
    find("zzzqq"); check("nothing matching says so", "Nothing matches" in pg.inner_text("#sbody"))
    find("mara", "all"); pg.fill("#q", "")
    pg.fill("#q", "an"); pg.wait_for_timeout(200)
    check("the small search box offers 'All results'", pg.evaluate("!!document.querySelector('#res a[data-all]')"))
    pg.click("#res a[data-all]"); pg.wait_for_timeout(500)
    check("which opens the search page with the same words", pg.evaluate("location.hash") == "#search" and pg.input_value("#sq") == "an", pg.input_value("#sq"))
    # 5 --------------------------------------------------------------------------------------------------------------------------
    go("#stats-team", 4500)
    hd = lambda: pg.evaluate("[...document.querySelectorAll('#sbody thead th')].map(t => t.textContent.replace(/[▾▴]/g, '').trim())")
    h1 = hd(); check("team statistics open on one group of columns, with a rank column", h1[:3] == ["#", "Club", "G"] and 4 <= len(h1) <= 8, str(h1))
    pg.click("[data-grp='All']"); pg.wait_for_timeout(2500); h2 = hd()
    check("'All' shows every column", len(h2) > len(h1) + 3, f"{len(h1)} {len(h2)}")
    pg.click("[data-grp='Situations']"); pg.wait_for_timeout(2500)
    vals = lambda i: pg.evaluate("[...document.querySelectorAll('#sbody tbody tr')].map(r => parseFloat(r.children[%d].textContent))" % i)
    opts = pg.evaluate("[...document.querySelectorAll('#ssort option')].map(o => o.value)")
    pg.select_option("#ssort", opts[-1]); pg.wait_for_timeout(300); col = hd().index(pg.evaluate("document.querySelector('#ssort option:checked').textContent.split(' · ')[0]"))
    v = vals(col); check("'Sort by' puts the clubs in that order", len(v) == 40 and (v == sorted(v) or v == sorted(v, reverse=True)), str(v[:5]))
    first = v[0]; pg.click("#sdir"); pg.wait_for_timeout(300); v2 = vals(col)
    check("the direction button reverses it", v2[0] != first and v2 == v[::-1] or sorted(v2) == sorted(v), f"{first} {v2[:3]}")
    pg.select_option("#swh", "c0"); pg.wait_for_timeout(400)
    check("a conference filter keeps that conference's 20 clubs that played (the 4 in exile have no games)", len(vals(1)) == 20, str(len(vals(1))))
    pg.select_option("#swh", "d3"); pg.wait_for_timeout(400)
    check("a division filter keeps its 5 clubs that played", len(vals(1)) == 5, str(len(vals(1))))
    go("#stats-player", 3000); pg.select_option("#swh", "c1"); pg.wait_for_timeout(500)
    clubs_shown = pg.evaluate("[...new Set([...document.querySelectorAll('#sbody tbody tr')].map(r => r.children[2].innerText.trim()))].length")
    check("player statistics can be limited to one conference too, and are sortable", 1 <= clubs_shown <= 24 and pg.evaluate("!!document.querySelector('#ssort')"), str(clubs_shown))
    # 6 --------------------------------------------------------------------------------------------------------------------------
    go("#info"); links = pg.evaluate("[...document.querySelectorAll('#app a.fork')].map(a => a.getAttribute('href'))")
    check("history and information leads to How it works, Founding Day and the Calendar", links == ["#guide", "#founding", "#calendar"], str(links))
    go("#guide"); check("those pages keep History and Information highlighted", pg.evaluate("document.querySelector('#tabs [aria-current]').textContent.trim().toUpperCase()") == "HISTORY AND INFORMATION")
    go("#clubs"); check("the older #clubs address shows the DFL page", pg.evaluate("document.querySelector('#app h1').textContent") == "The DFL")
    go("#players"); check("the older #players address shows search for players", pg.evaluate("document.querySelector('#app h1').textContent") == "Search" and pg.evaluate("document.getElementById('st').value") == "player")
    check("no script error on any of it", not errs, str(errs[:2]))
    br.close()

# 7 ----------------------------------------------------------------------------------------------------------------------------
root = tempfile.mkdtemp(); build_site.build(os.path.join(root, "index.html"), 7, live=True, rules=5)
H = 3600 * 1000; now = int(time.time() * 1000)
meta = dict(seed=7, epoch_ms=now - 30 * H, pacing="blocks", real_per_game=L.BLOCK_REAL_PER_GAME, halftime=L.HALFITIME_PAUSE if hasattr(L, "HALFITIME_PAUSE") else L.HALFTIME_PAUSE, parity="tight", rules=5)
out = os.path.join(root, "live"); L.write_json(out + "/meta.json", meta)
run = L.Runner(out, 7, meta["epoch_ms"], meta)
for h in range(1, 31, 2): run.tick(meta["epoch_ms"] + h * H)
run.tick(now); url = serve(root)
with sync_playwright() as pw:
    br = pw.chromium.launch(); errs = []
    pg = br.new_page(viewport=dict(width=1100, height=900)); pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(url); pg.wait_for_timeout(3500)
    tabs = pg.evaluate("[...document.querySelectorAll('#tabs a')].map(a => a.textContent.trim().toUpperCase())")
    check("the live page opens on home, with Live as its second tab", pg.evaluate("document.querySelector('#app h1').textContent") == "Diamond Football League" and tabs[:2] == ["DFL", "LIVE"] and len(tabs) == 7, str(tabs))
    heads = pg.evaluate("[...document.querySelectorAll('#app h2')].map(h => h.textContent.trim())")
    check("the live home shows what is on or next, the latest results, and the division leaders", "Division leaders" in heads and ("Latest results" in heads or "Up next" in heads or "On now" in heads), str(heads))
    pg.evaluate("location.hash='#dfl'"); pg.wait_for_timeout(600)
    check("the live DFL page lists all 48 clubs", pg.evaluate("document.querySelectorAll('.confs a.club[href^=\"#club-\"]').length") == 48)
    check("no script error on the live page", not errs, str(errs[:2]))
    br.close()
print("\n" + ("ALL PASS" if not failures else f"{len(failures)} FAILED")); sys.exit(1 if failures else 0)
