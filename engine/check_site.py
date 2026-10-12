"""The website's data (site_export.py) agrees with the engine: every game has its date, the standings add up, the page builds."""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import site_export, build_site

failures = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok:
        failures.append(name)


d = site_export.export(7)
cl = {c["id"]: c for c in d["clubs"]}
act = [c for c in d["clubs"] if not c["exiled"]]
check("48 clubs, 8 in exile, 40 playing, 53 players each", len(d["clubs"]) == 48 and len(act) == 40 and all(len(c["roster"]) == 53 for c in d["clubs"]))
check("360 regular-season games, each with a date and a kickoff", len(d["games"]) == 360 and all(g["date"] and g["time"] for g in d["games"]))
check("every playing club has 18 results and its record matches its games", all(
    c["record"]["w"] + c["record"]["l"] + c["record"]["t"] == 18 and c["record"]["w"] == sum(1 for g in d["games"] if (g["home"] == c["id"] and g["hp"] > g["ap"]) or (g["away"] == c["id"] and g["ap"] > g["hp"])) for c in act))
check("wins equal losses across the league (ties count once each side)", sum(c["record"]["w"] for c in act) == sum(c["record"]["l"] for c in act))
check("the eight clubs in exile each played seven Ambassador games", all(sum(c["ambassador"][k] for k in "wlt") == 7 for c in d["clubs"] if c["exiled"]) and len(d["ambassador"]) == 28)
check("thirteen playoff games and a champion among the 14 playoff clubs", len(d["playoffs"]) == 13 and d["champion"] in {t for s in d["seeds"].values() for t in s} and sum(len(s) for s in d["seeds"].values()) == 14)
check("the same seed gives the same site data", site_export.export(7)["games"] == d["games"] and site_export.export(7)["champion"] == d["champion"])
ev = d["evolution"]
check("forty seasons of the schedule (2000 to 2039), year 1 in order, the pattern repeating every eight years, every season a permutation of the eight divisions",
      len(ev) == 40 and ev[0]["slots"] == list(range(1, 9)) and all(ev[i]["slots"] == ev[i + 8]["slots"] for i in range(32)) and all(sorted(e["slots"]) == list(range(1, 9)) for e in ev)
      and ev[1]["slots"][:4] == [4, 1, 2, 3] and ev[4]["slots"] == [5, 6, 7, 8, 1, 2, 3, 4])
out = os.path.join(tempfile.mkdtemp(), "i.html")
n = build_site.build(out, 7)
html = open(out, encoding="utf-8").read()
check("the page builds as one file with the data in it and no placeholder left", n > 1_000_000 and "__DATA__" not in html and "Diamond Football League" in html)
print("\n" + ("ALL PASS" if not failures else f"{len(failures)} FAILED: {failures}"))
sys.exit(1 if failures else 0)
