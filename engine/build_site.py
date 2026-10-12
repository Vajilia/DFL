"""Build the read-only website: export the founding league's data (site_export.py) and pour it into site/template.html. One self-contained page.

    python engine/build_site.py [out.html] [seed]
    python engine/build_site.py --live [out.html] [seed]     the live page: no results of the autopilot season, only the founding rosters

The live page learns everything that happens from the feed the live runner writes (engine/live.py), so the data poured into it holds no game, standing, seed or champion.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import site_export

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def spoiler_free(d: dict) -> dict:
    """Remove every result of the autopilot season from the exported data."""
    d["live"] = True
    d["box"] = {}
    d["games"], d["ambassador"], d["playoffs"] = [], [], []
    d["seeds"], d["division_ranks"], d["champion"] = {}, {}, None
    for c in d["clubs"]:
        c["record"] = dict(w=0, l=0, t=0, pf=0, pa=0, exit="", div_rank=0)
        c.pop("ambassador", None)
    return d


def build(out: str, seed: int = 7, live: bool = False) -> int:
    d = site_export.export(seed)
    data = json.dumps(spoiler_free(d) if live else d, separators=(",", ":")).replace("</", "<\\/")      # safe inside a script tag
    html = open(os.path.join(ROOT, "site", "template.html"), encoding="utf-8").read().replace("__DATA__", data)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    return len(html)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--live"]
    out = args[0] if args else os.path.join(ROOT, "site", "index.html")
    print(out, build(out, int(args[1]) if len(args) > 1 else 7, "--live" in sys.argv), "bytes")
